from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any, Optional, Sequence

try:
    import cv2
except ImportError:  # pragma: no cover - optional dependency
    cv2 = None


class _GenAIV2Backend:
    """Backend for google.genai package."""

    def __init__(self, module: Any, types_module: Any, api_key: str) -> None:
        self._module = module
        self._types = types_module
        self._client = module.Client(api_key=api_key)

    def generation_config(self, *, temperature: float, max_output_tokens: int) -> Any:
        try:
            return self._types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
                max_output_tokens=max_output_tokens,
            )
        except Exception:
            return {
                "temperature": temperature,
                "response_mime_type": "application/json",
                "max_output_tokens": max_output_tokens,
            }

    def build_inline_part(self, *, mime_type: str, data: bytes) -> Any:
        try:
            return self._types.Part.from_bytes(data=data, mime_type=mime_type)
        except Exception:
            return {"mime_type": mime_type, "data": data}

    def generate_content(self, *, model_name: str, contents: Sequence[Any], generation_config: Any) -> Any:
        # google.genai uses `config`; keep fallback for potential sdk signature drift.
        try:
            return self._client.models.generate_content(
                model=model_name,
                contents=list(contents),
                config=generation_config,
            )
        except TypeError:
            return self._client.models.generate_content(
                model=model_name,
                contents=list(contents),
                generation_config=generation_config,
            )

    def upload_file(self, *, path: str, mime_type: str) -> Any:
        # Support different google.genai file upload signatures.
        methods = [
            lambda: self._client.files.upload(file=path, mime_type=mime_type),
            lambda: self._client.files.upload(file=path),
            lambda: self._client.files.upload(path=path, mime_type=mime_type),
            lambda: self._client.files.upload(path=path),
        ]
        last_error: Exception | None = None
        for method in methods:
            try:
                return method()
            except Exception as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise RuntimeError("Failed to upload file with google.genai.")

    def get_file(self, *, name: str) -> Any:
        return self._client.files.get(name=name)

    def delete_file(self, *, name: str) -> None:
        self._client.files.delete(name=name)

    @staticmethod
    def file_state_name(file_obj: Any) -> str:
        state = getattr(file_obj, "state", None)
        if state is None:
            return "ACTIVE"
        name = getattr(state, "name", None)
        if name:
            return str(name).upper()
        state_text = str(state).upper()
        if "." in state_text:
            state_text = state_text.split(".")[-1]
        return state_text


class GeminiClient:
    """Wrapper around Gemini SDK with JSON-safe output parsing."""

    _JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)

    def __init__(
        self,
        api_key: Optional[str] = None,
        image_model: Optional[str] = None,
        video_model: Optional[str] = None,
        default_temperature: float = 0.3,
        upload_timeout_seconds: int = 180,
        upload_poll_interval_seconds: float = 2.0,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Missing Gemini API key. Set GEMINI_API_KEY or pass api_key.")

        self._backend = self._init_backend(key)
        self.image_model = image_model or os.getenv("GEMINI_IMAGE_MODEL", "gemini-flash-latest")
        self.video_model = video_model or os.getenv("GEMINI_VIDEO_MODEL", "gemini-flash-latest")
        self.default_temperature = default_temperature
        self.upload_timeout_seconds = upload_timeout_seconds
        self.upload_poll_interval_seconds = upload_poll_interval_seconds

    @staticmethod
    def _init_backend(api_key: str) -> Any:
        try:
            from google import genai as genai_v2
            from google.genai import types as genai_types

            return _GenAIV2Backend(genai_v2, genai_types, api_key)
        except Exception as exc:
            raise RuntimeError("No Gemini SDK available. Install `google-genai`.") from exc

    def generate_json(
        self,
        prompt: str,
        *,
        parts: Optional[Sequence[Any]] = None,
        model: str = "image",
        temperature: Optional[float] = None,
        max_output_tokens: int = 2048,
    ) -> dict[str, Any]:
        model_name = self._resolve_model_name(model)
        generation_config = self._backend.generation_config(
            temperature=self.default_temperature if temperature is None else temperature,
            max_output_tokens=max_output_tokens,
        )

        contents: list[Any] = [prompt]
        if parts:
            contents.extend(parts)

        response = self._backend.generate_content(
            model_name=model_name,
            contents=contents,
            generation_config=generation_config,
        )
        response_text = self._extract_response_text(response)
        return self._parse_json(response_text)

    def build_image_part(
        self,
        *,
        image_base64: Optional[str] = None,
        image_path: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Any:
        if bool(image_base64) == bool(image_path):
            raise ValueError("Provide exactly one of image_base64 or image_path.")

        if image_path:
            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            data = path.read_bytes()
            guessed = mimetypes.guess_type(path.name)[0]
            mime = mime_type or guessed or "image/jpeg"
            return self._backend.build_inline_part(mime_type=mime, data=data)

        assert image_base64 is not None
        decoded = self._decode_base64(image_base64)
        return self._backend.build_inline_part(mime_type=mime_type or "image/jpeg", data=decoded)

    def upload_video(self, video_path: str, *, preprocess_seconds: Optional[int] = 10) -> Any:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        upload_path = path
        temporary_clip: Optional[Path] = None
        if preprocess_seconds:
            temporary_clip = self._trim_video(path, preprocess_seconds)
            upload_path = temporary_clip

        try:
            uploaded = self._backend.upload_file(path=str(upload_path), mime_type="video/mp4")
            file_name = getattr(uploaded, "name", "")
            if not file_name:
                # If sdk already returns an active handle without a file name.
                return uploaded
            return self._wait_for_uploaded_file(file_name)
        finally:
            if temporary_clip and temporary_clip.exists():
                temporary_clip.unlink(missing_ok=True)

    def delete_uploaded_file(self, uploaded_file_or_name: Any) -> None:
        name = uploaded_file_or_name
        if not isinstance(name, str):
            name = getattr(uploaded_file_or_name, "name", "")
        if not name:
            return
        try:
            self._backend.delete_file(name=name)
        except Exception:
            return

    def _resolve_model_name(self, model: str) -> str:
        if model == "video":
            return self.video_model
        return self.image_model

    def _wait_for_uploaded_file(self, file_name: str) -> Any:
        deadline = time.time() + self.upload_timeout_seconds
        while time.time() < deadline:
            file_obj = self._backend.get_file(name=file_name)
            state = self._backend.file_state_name(file_obj)
            if state == "ACTIVE":
                return file_obj
            if state == "FAILED":
                raise RuntimeError(f"Gemini file processing failed for {file_name}.")
            time.sleep(self.upload_poll_interval_seconds)

        raise TimeoutError(f"Timed out waiting for Gemini to process file {file_name}.")

    @staticmethod
    def _decode_base64(payload: str) -> bytes:
        cleaned = payload.strip()
        if cleaned.startswith("data:") and "," in cleaned:
            cleaned = cleaned.split(",", 1)[1]
        cleaned = "".join(cleaned.split())
        try:
            return base64.b64decode(cleaned, validate=True)
        except Exception as exc:
            raise ValueError("Invalid base64 image payload.") from exc

    @staticmethod
    def _extract_response_text(response: Any) -> str:
        try:
            text = getattr(response, "text", "")
            if text:
                return text.strip()
        except Exception:
            pass

        chunks: list[str] = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", "")
                if part_text:
                    chunks.append(part_text)
        return "\n".join(chunks).strip()

    def _parse_json(self, raw_text: str) -> dict[str, Any]:
        if not raw_text:
            raise ValueError("Gemini response is empty; cannot parse JSON.")

        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        fenced_match = self._JSON_BLOCK_RE.search(raw_text)
        if fenced_match:
            parsed = json.loads(fenced_match.group(1))
            if isinstance(parsed, dict):
                return parsed

        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(raw_text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed

        preview = raw_text[:300]
        raise ValueError(f"Could not parse model response as JSON object: {preview}")

    def _trim_video(self, source_path: Path, seconds: int) -> Path:
        if seconds <= 0:
            return source_path
        if cv2 is None:
            raise RuntimeError("opencv-python is required for video preprocessing.")

        capture = cv2.VideoCapture(str(source_path))
        if not capture.isOpened():
            raise ValueError(f"Cannot open video file: {source_path}")

        writer = None
        out_path: Optional[Path] = None
        try:
            fps = capture.get(cv2.CAP_PROP_FPS)
            if not fps or fps <= 0:
                fps = 30.0

            max_frames = max(1, int(fps * seconds))
            ret, first_frame = capture.read()
            if not ret:
                raise ValueError(f"Unable to read first frame from video: {source_path}")

            height, width = first_frame.shape[:2]
            fd, temp_name = tempfile.mkstemp(suffix=".mp4")
            os.close(fd)
            out_path = Path(temp_name)

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))
            if not writer.isOpened():
                raise ValueError("Failed to open temporary video writer.")

            frames_written = 0
            writer.write(first_frame)
            frames_written += 1

            while frames_written < max_frames:
                ret, frame = capture.read()
                if not ret:
                    break
                writer.write(frame)
                frames_written += 1

            if frames_written == 0:
                raise ValueError(f"No frames written for video clip: {source_path}")
            return out_path
        finally:
            capture.release()
            if writer is not None:
                writer.release()
