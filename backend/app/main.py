from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.database import Base, engine
from .routes import user_router, pet_router, matching_router, analyze, pets, lost, stray, map as map_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main API routers
app.include_router(user_router, prefix=settings.API_V1_STR)
app.include_router(pet_router, prefix=settings.API_V1_STR)
app.include_router(matching_router)

# Stray / lost / map / adoption / analyze (Jiawen)
app.include_router(analyze.router, prefix="/api")
app.include_router(pets.router, prefix="/api")
app.include_router(lost.router, prefix="/api")
app.include_router(stray.router, prefix="/api")
app.include_router(map_routes.router, prefix="/api")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
def root():
    return {
        "message": "Welcome to Goodle API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
