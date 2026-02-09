from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Protocol, Sequence

from .gemini_client import GeminiClient


DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "lost_dog_match_prompt.txt"


class MatchNotifier(Protocol):
    """Callback contract for notifying owner when potential matches are found."""

    def notify_possible_match(
        self,
        owner_id: str,
        matched_report_ids: list[str],
        similarity_score: float,
    ) -> None:
        ...


@dataclass(frozen=True)
class GeoLocation:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class LostDogNotice:
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    lost_at: Optional[datetime] = None
    location: Optional[GeoLocation] = None


@dataclass(frozen=True)
class StrayDogReport:
    report_id: str
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    reported_at: Optional[datetime] = None
    location: Optional[GeoLocation] = None


class DogMatcher:
    def __init__(
        self,
        client: GeminiClient,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
        similarity_threshold: float = 70.0,
        max_distance_km: float = 5.0,
        max_time_gap_hours: int = 72,
        temperature: float = 0.2,
    ) -> None:
        self.client = client
        self.prompt_path = prompt_path
        self.similarity_threshold = similarity_threshold
        self.max_distance_km = max_distance_km
        self.max_time_gap_hours = max_time_gap_hours
        self.temperature = temperature

    def match_lost_dog(
        self,
        *,
        notice: LostDogNotice,
        candidate_reports: Sequence[StrayDogReport],
        owner_id: Optional[str] = None,
        notifier: Optional[MatchNotifier] = None,
    ) -> dict[str, Any]:
        if not candidate_reports:
            return {"is_match": False, "similarity_score": 0.0, "matched_report_ids": []}

        prompt = self._load_prompt()
        notice_part = self.client.build_image_part(
            image_base64=notice.image_base64,
            image_path=notice.image_path,
        )

        matched_report_ids: list[str] = []
        highest_similarity = 0.0

        for report in candidate_reports:
            if not self._passes_spatiotemporal_filter(notice, report):
                continue

            report_part = self.client.build_image_part(
                image_base64=report.image_base64,
                image_path=report.image_path,
            )
            raw = self.client.generate_json(
                prompt,
                parts=[notice_part, report_part],
                model="image",
                temperature=self.temperature,
            )

            similarity = self._normalize_similarity(raw.get("similarity_score"))
            highest_similarity = max(highest_similarity, similarity)

            model_is_match = bool(raw.get("is_match", False))
            if model_is_match or similarity >= self.similarity_threshold:
                matched_report_ids.append(report.report_id)

        is_match = len(matched_report_ids) > 0
        if is_match and owner_id and notifier:
            notifier.notify_possible_match(
                owner_id=owner_id,
                matched_report_ids=matched_report_ids,
                similarity_score=highest_similarity,
            )

        return {
            "is_match": is_match,
            "similarity_score": round(highest_similarity, 2),
            "matched_report_ids": matched_report_ids,
        }

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")
        return self.prompt_path.read_text(encoding="utf-8")

    def _passes_spatiotemporal_filter(self, notice: LostDogNotice, report: StrayDogReport) -> bool:
        if notice.lost_at and report.reported_at:
            hours = abs((report.reported_at - notice.lost_at).total_seconds()) / 3600
            if hours > self.max_time_gap_hours:
                return False

        if notice.location and report.location:
            distance_km = self._haversine_km(
                notice.location.latitude,
                notice.location.longitude,
                report.location.latitude,
                report.location.longitude,
            )
            if distance_km > self.max_distance_km:
                return False

        return True

    @staticmethod
    def _normalize_similarity(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            score = 0.0
        return max(0.0, min(100.0, score))

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius_km = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_km * c
