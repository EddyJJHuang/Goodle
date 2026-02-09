from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient


def _b64(payload: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(payload).decode("utf-8")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_MOCK_MODE", "1")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "goodle-test.db"))

    from app.core.settings import get_settings

    get_settings.cache_clear()

    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    get_settings.cache_clear()


def test_analyze_photo_json(client: TestClient) -> None:
    response = client.post(
        "/api/ai/analyze-photo",
        json={
            "pet_id": "pet_001",
            "image_base64": _b64(b"same-dog"),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"code", "message", "data"}
    assert payload["code"] == 200
    assert set(payload["data"].keys()) == {
        "breed",
        "size",
        "age_group",
        "appearance_tags",
        "personality_guess",
    }
    assert payload["data"]["breed"]
    assert payload["data"]["size"] in {"small", "medium", "large"}


def test_analyze_video_upload(client: TestClient) -> None:
    response = client.post(
        "/api/ai/analyze-video/upload",
        data={"pet_id": "pet_002", "preprocess_seconds": "10"},
        files={"video": ("sample.mp4", b"fake-mp4-bytes", "video/mp4")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == {"code", "message", "data"}
    assert payload["code"] == 200
    assert set(payload["data"].keys()) == {
        "activity_level",
        "approach_speed",
        "emotional_stability",
        "play_preference",
        "body_language_score",
    }
    assert 0 <= payload["data"]["activity_level"] <= 10


def test_match_and_notification_chain(client: TestClient) -> None:
    same = _b64(b"same-dog")
    diff = _b64(b"other-dog")

    report_1 = client.post(
        "/api/ai/stray-reports",
        json={"report_id": "rep_001", "image_base64": same},
    )
    report_2 = client.post(
        "/api/ai/stray-reports",
        json={"report_id": "rep_002", "image_base64": diff},
    )
    assert report_1.status_code == 200
    assert report_2.status_code == 200

    match = client.post(
        "/api/ai/match-lost-dog",
        json={
            "owner_id": "owner_001",
            "notice_image_base64": same,
            "use_db_reports": True,
        },
    )
    assert match.status_code == 200
    match_body = match.json()
    assert set(match_body.keys()) == {"code", "message", "data"}
    match_payload = match_body["data"]
    assert set(match_payload.keys()) == {
        "is_match",
        "similarity_score",
        "matched_report_ids",
        "candidate_count",
    }
    assert match_payload["candidate_count"] >= 2
    assert "rep_001" in match_payload["matched_report_ids"]

    notifications = client.get("/api/ai/notifications")
    assert notifications.status_code == 200
    notifications_body = notifications.json()
    assert set(notifications_body.keys()) == {"code", "message", "data"}
    rows = notifications_body["data"]
    assert rows
    assert set(rows[0].keys()) == {"id", "owner_id", "matched_report_ids", "similarity_score", "created_at"}
    assert rows[0]["owner_id"] == "owner_001"
