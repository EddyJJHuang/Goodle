from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from .gemini_client import GeminiClient


DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "video_behavior_prompt.txt"


class PetDynamicInfoRepository(Protocol):
    """Repository contract for persisting AI output into pet_dynamic_info."""

    def create_pet_dynamic_info(self, pet_id: str, dynamic_info: dict[str, Any]) -> None:
        ...


@dataclass(frozen=True)
class VideoAnalysisResult:
    activity_level: float
    approach_speed: float
    emotional_stability: float
    play_preference: str
    body_language_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VideoAnalyzer:
    def __init__(
        self,
        client: GeminiClient,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
        temperature: float = 0.3,
    ) -> None:
        self.client = client
        self.prompt_path = prompt_path
        self.temperature = temperature

    def analyze_video(self, video_path: str, *, preprocess_seconds: int = 10) -> dict[str, Any]:
        prompt = self._load_prompt()
        uploaded_video = self.client.upload_video(video_path, preprocess_seconds=preprocess_seconds)

        try:
            raw = self.client.generate_json(
                prompt,
                parts=[uploaded_video],
                model="video",
                temperature=self.temperature,
            )
        finally:
            self.client.delete_uploaded_file(uploaded_video)

        return self._normalize_result(raw).to_dict()

    def analyze_and_persist(
        self,
        *,
        pet_id: str,
        video_path: str,
        repository: PetDynamicInfoRepository,
        preprocess_seconds: int = 10,
    ) -> dict[str, Any]:
        result = self.analyze_video(video_path, preprocess_seconds=preprocess_seconds)
        repository.create_pet_dynamic_info(pet_id, result)
        return result

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")
        return self.prompt_path.read_text(encoding="utf-8")

    def _normalize_result(self, payload: dict[str, Any]) -> VideoAnalysisResult:
        return VideoAnalysisResult(
            activity_level=self._clamp_score(payload.get("activity_level")),
            approach_speed=self._clamp_score(payload.get("approach_speed")),
            emotional_stability=self._clamp_score(payload.get("emotional_stability")),
            play_preference=self._normalize_play_preference(payload.get("play_preference")),
            body_language_score=self._clamp_score(payload.get("body_language_score")),
        )

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            score = 0.0
        return round(max(0.0, min(10.0, score)), 2)

    @staticmethod
    def _normalize_play_preference(value: Any) -> str:
        mapping = {
            "chase": "chase",
            "wrestle": "wrestle",
            "chasing": "chase",
            "wrestling": "wrestle",
        }
        normalized = str(value or "").strip().lower()
        return mapping.get(normalized, normalized or "mixed")
