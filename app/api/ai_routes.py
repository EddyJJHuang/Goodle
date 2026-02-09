from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field, model_validator

from app.ai import DogMatcher, GeoLocation, LostDogNotice, StrayDogReport
from app.core.response import api_success


router = APIRouter(prefix="/ai", tags=["AI"])


class LocationInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AnalyzePhotoRequest(BaseModel):
    pet_id: str = Field(min_length=1)
    image_base64: Optional[str] = None
    image_path: Optional[str] = None

    @model_validator(mode="after")
    def _validate_source(self) -> "AnalyzePhotoRequest":
        if bool(self.image_base64) == bool(self.image_path):
            raise ValueError("Provide exactly one of image_base64 or image_path.")
        return self


class AnalyzeVideoRequest(BaseModel):
    pet_id: str = Field(min_length=1)
    video_path: str = Field(min_length=1)
    preprocess_seconds: int = Field(default=10, ge=0, le=120)


class StrayReportCreateRequest(BaseModel):
    report_id: str = Field(min_length=1)
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    reported_at: Optional[datetime] = None
    location: Optional[LocationInput] = None

    @model_validator(mode="after")
    def _validate_source(self) -> "StrayReportCreateRequest":
        if bool(self.image_base64) == bool(self.image_path):
            raise ValueError("Provide exactly one of image_base64 or image_path.")
        return self


class CandidateReportInput(BaseModel):
    report_id: str = Field(min_length=1)
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    reported_at: Optional[datetime] = None
    location: Optional[LocationInput] = None

    @model_validator(mode="after")
    def _validate_source(self) -> "CandidateReportInput":
        if bool(self.image_base64) == bool(self.image_path):
            raise ValueError("Provide exactly one of image_base64 or image_path.")
        return self


class MatchLostDogRequest(BaseModel):
    owner_id: Optional[str] = None
    notice_image_base64: Optional[str] = None
    notice_image_path: Optional[str] = None
    lost_at: Optional[datetime] = None
    location: Optional[LocationInput] = None
    use_db_reports: bool = True
    candidate_reports: list[CandidateReportInput] = Field(default_factory=list)
    similarity_threshold: Optional[float] = Field(default=None, ge=0, le=100)
    max_distance_km: Optional[float] = Field(default=None, ge=0)
    max_time_gap_hours: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_source(self) -> "MatchLostDogRequest":
        if bool(self.notice_image_base64) == bool(self.notice_image_path):
            raise ValueError("Provide exactly one of notice_image_base64 or notice_image_path.")
        return self


def _location(value: Optional[LocationInput]) -> Optional[GeoLocation]:
    if value is None:
        return None
    return GeoLocation(latitude=value.latitude, longitude=value.longitude)


def _tmp_suffix(filename: Optional[str], fallback: str) -> str:
    if filename:
        ext = Path(filename).suffix
        if ext:
            return ext
    return fallback


async def _save_upload_to_temp(upload: UploadFile, fallback_suffix: str) -> Path:
    suffix = _tmp_suffix(upload.filename, fallback_suffix)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        content = await upload.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        temp_file.write(content)
        return Path(temp_file.name)
    finally:
        temp_file.close()
        await upload.close()


@router.post("/analyze-photo")
def analyze_photo(payload: AnalyzePhotoRequest, request: Request) -> dict[str, Any]:
    analyzer = request.app.state.photo_analyzer
    repository = request.app.state.pet_repository
    try:
        result = analyzer.analyze_and_persist(
            pet_id=payload.pet_id,
            repository=repository,
            image_base64=payload.image_base64,
            image_path=payload.image_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_success(result)


@router.post("/analyze-photo/upload")
async def analyze_photo_upload(
    request: Request,
    pet_id: str = Form(...),
    photo: UploadFile = File(...),
) -> dict[str, Any]:
    analyzer = request.app.state.photo_analyzer
    repository = request.app.state.pet_repository
    temp_path = await _save_upload_to_temp(photo, ".jpg")
    try:
        result = analyzer.analyze_and_persist(
            pet_id=pet_id,
            repository=repository,
            image_path=str(temp_path),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)
    return api_success(result)


@router.post("/analyze-video")
def analyze_video(payload: AnalyzeVideoRequest, request: Request) -> dict[str, Any]:
    analyzer = request.app.state.video_analyzer
    repository = request.app.state.dynamic_info_repository
    try:
        result = analyzer.analyze_and_persist(
            pet_id=payload.pet_id,
            video_path=payload.video_path,
            repository=repository,
            preprocess_seconds=payload.preprocess_seconds,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return api_success(result)


@router.post("/analyze-video/upload")
async def analyze_video_upload(
    request: Request,
    pet_id: str = Form(...),
    preprocess_seconds: int = Form(10),
    video: UploadFile = File(...),
) -> dict[str, Any]:
    analyzer = request.app.state.video_analyzer
    repository = request.app.state.dynamic_info_repository
    if preprocess_seconds < 0 or preprocess_seconds > 120:
        raise HTTPException(status_code=400, detail="preprocess_seconds must be between 0 and 120.")

    temp_path = await _save_upload_to_temp(video, ".mp4")
    try:
        result = analyzer.analyze_and_persist(
            pet_id=pet_id,
            video_path=str(temp_path),
            repository=repository,
            preprocess_seconds=preprocess_seconds,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        temp_path.unlink(missing_ok=True)
    return api_success(result)


@router.post("/stray-reports")
def upsert_stray_report(payload: StrayReportCreateRequest, request: Request) -> dict[str, Any]:
    repository = request.app.state.stray_report_repository
    report = StrayDogReport(
        report_id=payload.report_id,
        image_base64=payload.image_base64,
        image_path=payload.image_path,
        reported_at=payload.reported_at,
        location=_location(payload.location),
    )
    repository.upsert_report(report)
    return api_success({"report_id": payload.report_id}, message="report upserted")


@router.get("/stray-reports")
def list_stray_reports(request: Request) -> dict[str, Any]:
    repository = request.app.state.stray_report_repository
    reports = repository.list_reports()
    data: list[dict[str, Any]] = []
    for report in reports:
        data.append(
            {
                "report_id": report.report_id,
                "image_path": report.image_path,
                "has_image_base64": bool(report.image_base64),
                "reported_at": report.reported_at.isoformat() if report.reported_at else None,
                "location": (
                    {"latitude": report.location.latitude, "longitude": report.location.longitude}
                    if report.location
                    else None
                ),
            }
        )
    return api_success(data)


@router.post("/match-lost-dog")
def match_lost_dog(payload: MatchLostDogRequest, request: Request) -> dict[str, Any]:
    settings = request.app.state.settings
    client = request.app.state.ai_client
    notifier = request.app.state.match_notifier
    repository = request.app.state.stray_report_repository

    reports_by_id: dict[str, StrayDogReport] = {}
    if payload.use_db_reports:
        for report in repository.list_reports():
            reports_by_id[report.report_id] = report
    for report in payload.candidate_reports:
        reports_by_id[report.report_id] = StrayDogReport(
            report_id=report.report_id,
            image_base64=report.image_base64,
            image_path=report.image_path,
            reported_at=report.reported_at,
            location=_location(report.location),
        )

    matcher = DogMatcher(
        client=client,
        similarity_threshold=payload.similarity_threshold or settings.similarity_threshold,
        max_distance_km=payload.max_distance_km or settings.max_distance_km,
        max_time_gap_hours=payload.max_time_gap_hours or settings.max_time_gap_hours,
        temperature=settings.match_temperature,
    )
    notice = LostDogNotice(
        image_base64=payload.notice_image_base64,
        image_path=payload.notice_image_path,
        lost_at=payload.lost_at,
        location=_location(payload.location),
    )

    try:
        result = matcher.match_lost_dog(
            notice=notice,
            candidate_reports=list(reports_by_id.values()),
            owner_id=payload.owner_id,
            notifier=notifier,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result["candidate_count"] = len(reports_by_id)
    return api_success(result)


@router.get("/notifications")
def list_notifications(request: Request) -> dict[str, Any]:
    notifier = request.app.state.match_notifier
    return api_success(notifier.list_notifications())
