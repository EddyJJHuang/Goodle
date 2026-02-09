from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional, Protocol

from .gemini_client import GeminiClient


DEFAULT_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "photo_analysis_prompt.txt"


class PetAIRepository(Protocol):
    """Repository contract for persisting photo analysis into pets.aitags."""

    def update_pet_ai_tags(self, pet_id: str, ai_tags: dict[str, Any]) -> None:
        ...


@dataclass(frozen=True)
class PhotoAnalysisResult:
    breed: str
    size: str
    age_group: str
    appearance_tags: list[str]
    personality_guess: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PhotoAnalyzer:
    def __init__(
        self,
        client: GeminiClient,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
        temperature: float = 0.3,
    ) -> None:
        self.client = client
        self.prompt_path = prompt_path
        self.temperature = temperature

    def analyze_photo(
        self,
        *,
        image_base64: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict[str, Any]:
        prompt = self._load_prompt()
        image_part = self.client.build_image_part(image_base64=image_base64, image_path=image_path)
        raw = self.client.generate_json(
            prompt,
            parts=[image_part],
            model="image",
            temperature=self.temperature,
        )
        return self._normalize_result(raw).to_dict()

    def analyze_and_persist(
        self,
        *,
        pet_id: str,
        repository: PetAIRepository,
        image_base64: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> dict[str, Any]:
        result = self.analyze_photo(image_base64=image_base64, image_path=image_path)
        repository.update_pet_ai_tags(pet_id, result)
        return result

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")
        return self.prompt_path.read_text(encoding="utf-8")

    def _normalize_result(self, payload: dict[str, Any]) -> PhotoAnalysisResult:
        breed = str(payload.get("breed", "unknown")).strip() or "unknown"
        size = self._normalize_size(payload.get("size"))
        age_group = self._normalize_age_group(payload.get("age_group"))
        appearance_tags = self._normalize_tags(payload.get("appearance_tags"))
        personality_guess = str(payload.get("personality_guess", "unknown")).strip() or "unknown"

        return PhotoAnalysisResult(
            breed=breed,
            size=size,
            age_group=age_group,
            appearance_tags=appearance_tags,
            personality_guess=personality_guess,
        )

    @staticmethod
    def _normalize_size(value: Any) -> str:
        mapping = {
            "small": "small",
            "medium": "medium",
            "large": "large",
            "toy": "small",
            "mini": "small",
            "giant": "large",
        }
        normalized = str(value or "").strip().lower()
        return mapping.get(normalized, "medium")

    @staticmethod
    def _normalize_age_group(value: Any) -> str:
        mapping = {
            "puppy": "puppy",
            "adult": "adult",
            "senior": "senior",
            "young": "puppy",
            "old": "senior",
        }
        normalized = str(value or "").strip().lower()
        return mapping.get(normalized, "adult")

    @staticmethod
    def _normalize_tags(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            pieces = [part.strip() for part in value.split(",")]
            return [part for part in pieces if part]
        return []
