from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai import DogMatcher, GeminiClient, MockGeminiClient, PhotoAnalyzer, VideoAnalyzer
from app.api.ai_routes import router as ai_router
from app.core.response import api_error, api_success
from app.core.settings import Settings, get_settings
from app.db.sqlite import SQLiteDatabase
from app.repositories.ai_repositories import (
    SQLiteMatchNotifier,
    SQLitePetDynamicInfoRepository,
    SQLitePetRepository,
    SQLiteStrayReportRepository,
)


def _create_ai_client(settings: Settings) -> GeminiClient | MockGeminiClient:
    if settings.mock_mode:
        return MockGeminiClient()
    if not settings.gemini_api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Set it or enable AI_MOCK_MODE=1.")
    return GeminiClient(
        api_key=settings.gemini_api_key,
        image_model=settings.gemini_image_model,
        video_model=settings.gemini_video_model,
    )


def _initialize_runtime(app: FastAPI, settings: Settings) -> None:
    db = SQLiteDatabase(settings.sqlite_path)
    db.initialize()

    ai_client = _create_ai_client(settings)
    app.state.settings = settings
    app.state.db = db
    app.state.ai_client = ai_client
    app.state.pet_repository = SQLitePetRepository(db)
    app.state.dynamic_info_repository = SQLitePetDynamicInfoRepository(db)
    app.state.stray_report_repository = SQLiteStrayReportRepository(db)
    app.state.match_notifier = SQLiteMatchNotifier(db)
    app.state.photo_analyzer = PhotoAnalyzer(
        ai_client,
        temperature=settings.photo_temperature,
    )
    app.state.video_analyzer = VideoAnalyzer(
        ai_client,
        temperature=settings.video_temperature,
    )
    app.state.matcher = DogMatcher(
        client=ai_client,
        similarity_threshold=settings.similarity_threshold,
        max_distance_km=settings.max_distance_km,
        max_time_gap_hours=settings.max_time_gap_hours,
        temperature=settings.match_temperature,
    )


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _initialize_runtime(app, settings)
        yield

    app = FastAPI(
        title="Goodle Backend API",
        version="1.0.0",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=api_error(message=str(exc.detail), code=exc.status_code),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        message = "Validation error"
        if exc.errors():
            first_error = exc.errors()[0]
            message = str(first_error.get("msg", message))
        return JSONResponse(status_code=422, content=api_error(message=message, code=422, data=exc.errors()))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=api_error(message=str(exc), code=500))

    @app.get(f"{settings.api_prefix}/health")
    def health() -> dict[str, Any]:
        return api_success({"status": "ok", "mock_mode": settings.mock_mode})

    app.include_router(ai_router, prefix=settings.api_prefix)
    return app


app = create_app()
