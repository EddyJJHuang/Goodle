from __future__ import annotations

import base64
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Optional, Sequence


class MockGeminiClient:
    """Offline fake client for local API testing without Gemini credentials."""

    def __init__(self, *_: Any, **__: Any) -> None:
        pass

    def generate_json(
        self,
        prompt: str,
        *,
        parts: Optional[Sequence[Any]] = None,
        model: str = "image",
        temperature: Optional[float] = None,
        max_output_tokens: int = 2048,
    ) -> dict[str, Any]:
        del model, temperature, max_output_tokens
        lower_prompt = prompt.lower()

        if '"activity_level"' in lower_prompt and '"approach_speed"' in lower_prompt:
            return {
                "activity_level": 7.2,
                "approach_speed": 6.8,
                "emotional_stability": 7.9,
                "play_preference": "chase",
                "body_language_score": 7.1,
            }

        if '"similarity_score"' in lower_prompt and '"is_match"' in lower_prompt:
            score = self._mock_similarity(parts or [])
            return {
                "breed_match": score >= 60,
                "coat_pattern_similarity": max(0.0, min(100.0, score - 5)),
                "body_size_similarity": max(0.0, min(100.0, score - 8)),
                "face_feature_similarity": max(0.0, min(100.0, score - 3)),
                "special_mark_similarity": max(0.0, min(100.0, score - 10)),
                "similarity_score": score,
                "is_match": score >= 70,
                "reason": "Mock comparison based on deterministic byte fingerprint.",
            }

        return {
            "breed": "mixed (labrador + border collie)",
            "size": "medium",
            "age_group": "adult",
            "appearance_tags": ["short_coat", "semi_floppy_ears", "black_white"],
            "personality_guess": "friendly, energetic, and people-oriented",
        }

    def build_image_part(
        self,
        *,
        image_base64: Optional[str] = None,
        image_path: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> dict[str, Any]:
        if bool(image_base64) == bool(image_path):
            raise ValueError("Provide exactly one of image_base64 or image_path.")

        if image_path:
            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            guessed = mimetypes.guess_type(path.name)[0]
            return {"mime_type": mime_type or guessed or "image/jpeg", "data": path.read_bytes()}

        assert image_base64 is not None
        return {"mime_type": mime_type or "image/jpeg", "data": self._decode_base64(image_base64)}

    def upload_video(self, video_path: str, *, preprocess_seconds: Optional[int] = 10) -> Any:
        del preprocess_seconds
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        return {"name": "mock-video", "path": str(path)}

    def delete_uploaded_file(self, uploaded_file_or_name: Any) -> None:
        del uploaded_file_or_name
        return

    @staticmethod
    def _decode_base64(payload: str) -> bytes:
        cleaned = payload.strip()
        if cleaned.startswith("data:") and "," in cleaned:
            cleaned = cleaned.split(",", 1)[1]
        cleaned = "".join(cleaned.split())
        return base64.b64decode(cleaned, validate=False)

    def _mock_similarity(self, parts: Sequence[Any]) -> float:
        if len(parts) < 2:
            return 55.0
        left = self._extract_bytes(parts[0])
        right = self._extract_bytes(parts[1])
        if not left or not right:
            return 55.0
        if left == right:
            return 95.0

        digest = hashlib.sha256(left[:1024] + right[:1024]).hexdigest()
        bucket = int(digest[:8], 16) % 100
        # Keep score in a realistic range around threshold.
        return float(max(40, min(92, bucket)))

    @staticmethod
    def _extract_bytes(part: Any) -> bytes:
        if isinstance(part, dict):
            data = part.get("data")
            if isinstance(data, bytes):
                return data
        return b""
