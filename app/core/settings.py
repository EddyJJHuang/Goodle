from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.env_loader import load_env_files


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    api_prefix: str
    sqlite_path: str
    gemini_api_key: str | None
    gemini_image_model: str
    gemini_video_model: str
    photo_temperature: float
    video_temperature: float
    match_temperature: float
    similarity_threshold: float
    max_distance_km: float
    max_time_gap_hours: int
    mock_mode: bool
    cors_origins: list[str]

    @property
    def sqlite_file(self) -> Path:
        return Path(self.sqlite_path)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_env_files()
    cors_value = os.getenv("CORS_ORIGINS", "*")
    cors_origins = [item.strip() for item in cors_value.split(",") if item.strip()]
    if not cors_origins:
        cors_origins = ["*"]

    return Settings(
        api_prefix=os.getenv("API_PREFIX", "/api"),
        sqlite_path=os.getenv("SQLITE_PATH", "data/goodle.db"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_image_model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.0-flash"),
        gemini_video_model=os.getenv("GEMINI_VIDEO_MODEL", "gemini-3.0-pro"),
        photo_temperature=_to_float(os.getenv("PHOTO_AI_TEMPERATURE"), 0.3),
        video_temperature=_to_float(os.getenv("VIDEO_AI_TEMPERATURE"), 0.3),
        match_temperature=_to_float(os.getenv("MATCH_AI_TEMPERATURE"), 0.2),
        similarity_threshold=_to_float(os.getenv("MATCH_SIMILARITY_THRESHOLD"), 70.0),
        max_distance_km=_to_float(os.getenv("MATCH_MAX_DISTANCE_KM"), 5.0),
        max_time_gap_hours=_to_int(os.getenv("MATCH_MAX_TIME_GAP_HOURS"), 72),
        mock_mode=_to_bool(os.getenv("AI_MOCK_MODE"), default=False),
        cors_origins=cors_origins,
    )
