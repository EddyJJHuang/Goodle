from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pytest

from app.ai import DogMatcher, GeminiClient, LostDogNotice, PhotoAnalyzer, StrayDogReport, VideoAnalyzer


ROOT_DIR = Path(__file__).resolve().parents[1]
EVAL_DATA_PATH = ROOT_DIR / "tests" / "fixtures" / "ai_eval_dataset.json"
TAG_ALIAS_MAP = {
    "short_hair": "short_coat",
    "short_haired": "short_coat",
    "short_fur": "short_coat",
    "smooth_coat": "short_coat",
    "long_hair": "long_coat",
    "long_haired": "long_coat",
    "long_fur": "long_coat",
    "black_and_white": "black_white",
    "white_coat": "white",
    "pure_white_coat": "white",
    "off_white": "white",
}


def _enabled() -> bool:
    return os.getenv("AI_LIVE_EVAL", "").strip().lower() in {"1", "true", "yes", "on"}


def _show_output() -> bool:
    return os.getenv("AI_EVAL_SHOW_OUTPUT", "").strip().lower() in {"1", "true", "yes", "on"}


def _load_dataset() -> dict[str, Any]:
    if not EVAL_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing eval dataset: {EVAL_DATA_PATH}. "
            "Create it with photos/videos and expected labels."
        )
    return json.loads(EVAL_DATA_PATH.read_text(encoding="utf-8"))


def _resolve_path(raw: str) -> str:
    path = Path(raw)
    if path.is_absolute():
        return str(path)
    return str((ROOT_DIR / path).resolve())


def _soft_accuracy(pairs: list[tuple[str, str]]) -> float:
    if not pairs:
        return 1.0
    hits = sum(1 for expected, actual in pairs if expected == actual)
    return hits / len(pairs)


def _mae(pairs: list[tuple[float, float]]) -> float:
    if not pairs:
        return 0.0
    return sum(abs(expected - actual) for expected, actual in pairs) / len(pairs)


def _normalize_tag(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    if not normalized:
        return ""
    return TAG_ALIAS_MAP.get(normalized, normalized)


def _normalize_tag_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {tag for raw in values if (tag := _normalize_tag(str(raw)))}


@pytest.mark.live_ai
@pytest.mark.skipif(not _enabled(), reason="Set AI_LIVE_EVAL=1 to run live Gemini quality evals.")
def test_photo_quality_eval() -> None:
    dataset = _load_dataset()
    rows = dataset.get("photo_eval", [])
    assert rows, "photo_eval dataset is empty."

    client = GeminiClient()
    analyzer = PhotoAnalyzer(client)
    prompt = analyzer._load_prompt()

    size_pairs: list[tuple[str, str]] = []
    age_pairs: list[tuple[str, str]] = []

    for row in rows:
        image_path = _resolve_path(row["image_path"])
        expected_size = str(row.get("expected_size", "")).strip().lower()
        expected_age = str(row.get("expected_age_group", "")).strip().lower()
        required_breed_keywords = [
            str(keyword).strip().lower()
            for keyword in row.get("required_breed_keywords", [])
            if str(keyword).strip()
        ]
        required_tags = {_normalize_tag(tag) for tag in row.get("required_tags", []) if _normalize_tag(tag)}
        required_tag_groups = [
            {_normalize_tag(option) for option in group if _normalize_tag(option)}
            for group in row.get("required_tag_groups", [])
            if isinstance(group, list)
        ]

        image_part = client.build_image_part(image_path=image_path)
        raw_result = client.generate_json(
            prompt,
            parts=[image_part],
            model="image",
            temperature=analyzer.temperature,
        )
        result = analyzer._normalize_result(raw_result).to_dict()

        if _show_output():
            print(f"\n[photo_eval] image_path={image_path}")
            print(f"raw_model_json={json.dumps(raw_result, ensure_ascii=False)}")
            print(f"normalized_result={json.dumps(result, ensure_ascii=False)}")

        actual_size = str(result.get("size", "")).strip().lower()
        actual_age = str(result.get("age_group", "")).strip().lower()
        actual_breed = str(result.get("breed", "")).strip().lower()

        if expected_size:
            size_pairs.append((expected_size, actual_size))
        if expected_age:
            age_pairs.append((expected_age, actual_age))
        if required_breed_keywords:
            assert any(keyword in actual_breed for keyword in required_breed_keywords), (
                f"{image_path}: breed mismatch; expected one of keywords={required_breed_keywords}, "
                f"got={result.get('breed', '')}"
            )

        got_tags = _normalize_tag_set(result.get("appearance_tags", []))
        missing = required_tags - got_tags
        assert not missing, (
            f"{image_path}: missing required tags {sorted(missing)}; "
            f"got={sorted(got_tags)} raw={result.get('appearance_tags', [])}"
        )
        for group in required_tag_groups:
            if not group:
                continue
            assert group & got_tags, (
                f"{image_path}: none of required tag options matched {sorted(group)}; "
                f"got={sorted(got_tags)} raw={result.get('appearance_tags', [])}"
            )

    if size_pairs:
        if len(size_pairs) < 5:
            mismatches = [(expected, actual) for expected, actual in size_pairs if expected != actual]
            assert not mismatches, f"size mismatches: {mismatches}"
        else:
            assert _soft_accuracy(size_pairs) >= 0.70
    if age_pairs:
        if len(age_pairs) < 5:
            mismatches = [(expected, actual) for expected, actual in age_pairs if expected != actual]
            assert not mismatches, f"age_group mismatches: {mismatches}"
        else:
            assert _soft_accuracy(age_pairs) >= 0.70


@pytest.mark.live_ai
@pytest.mark.skipif(not _enabled(), reason="Set AI_LIVE_EVAL=1 to run live Gemini quality evals.")
def test_video_quality_eval() -> None:
    dataset = _load_dataset()
    rows = dataset.get("video_eval", [])
    assert rows, "video_eval dataset is empty."

    client = GeminiClient()
    analyzer = VideoAnalyzer(client)

    activity_pairs: list[tuple[float, float]] = []
    approach_pairs: list[tuple[float, float]] = []

    for row in rows:
        video_path = _resolve_path(row["video_path"])
        preprocess_seconds = int(row.get("preprocess_seconds", 10))
        expected_activity = float(row["expected_activity_level"])
        expected_approach = float(row["expected_approach_speed"])

        result = analyzer.analyze_video(video_path=video_path, preprocess_seconds=preprocess_seconds)
        activity_pairs.append((expected_activity, float(result["activity_level"])))
        approach_pairs.append((expected_approach, float(result["approach_speed"])))

    assert _mae(activity_pairs) <= 2.0
    assert _mae(approach_pairs) <= 2.0


@pytest.mark.live_ai
@pytest.mark.skipif(not _enabled(), reason="Set AI_LIVE_EVAL=1 to run live Gemini quality evals.")
def test_dog_match_quality_eval() -> None:
    dataset = _load_dataset()
    rows = dataset.get("match_eval", [])
    assert rows, "match_eval dataset is empty."

    client = GeminiClient()
    matcher = DogMatcher(client)

    tp = fp = fn = 0
    for row in rows:
        notice_image_path = _resolve_path(row["notice_image_path"])
        candidate_image_path = _resolve_path(row["candidate_image_path"])
        expected_match = bool(row["expected_is_match"])

        result = matcher.match_lost_dog(
            notice=LostDogNotice(image_path=notice_image_path),
            candidate_reports=[StrayDogReport(report_id="candidate", image_path=candidate_image_path)],
        )
        predicted = bool(result["is_match"])

        if predicted and expected_match:
            tp += 1
        elif predicted and not expected_match:
            fp += 1
        elif (not predicted) and expected_match:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0

    assert precision >= 0.75
    assert recall >= 0.75
