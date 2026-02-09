from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.ai.dog_matcher import GeoLocation, MatchNotifier, StrayDogReport
from app.ai.photo_analyzer import PetAIRepository
from app.ai.video_analyzer import PetDynamicInfoRepository
from app.db.sqlite import SQLiteDatabase


class SQLitePetRepository(PetAIRepository):
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def update_pet_ai_tags(self, pet_id: str, ai_tags: dict[str, Any]) -> None:
        payload = json.dumps(ai_tags, ensure_ascii=True)
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO pets (id, aitags, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    aitags = excluded.aitags,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (pet_id, payload),
            )


class SQLitePetDynamicInfoRepository(PetDynamicInfoRepository):
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def create_pet_dynamic_info(self, pet_id: str, dynamic_info: dict[str, Any]) -> None:
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO pet_dynamic_info (
                    pet_id,
                    activity_level,
                    approach_speed,
                    emotional_stability,
                    play_preference,
                    body_language_score
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    pet_id,
                    float(dynamic_info["activity_level"]),
                    float(dynamic_info["approach_speed"]),
                    float(dynamic_info["emotional_stability"]),
                    str(dynamic_info["play_preference"]),
                    float(dynamic_info["body_language_score"]),
                ),
            )


class SQLiteStrayReportRepository:
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def upsert_report(self, report: StrayDogReport) -> None:
        latitude = report.location.latitude if report.location else None
        longitude = report.location.longitude if report.location else None
        reported_at = report.reported_at.isoformat() if report.reported_at else None
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO stray_dog_reports (
                    report_id,
                    image_path,
                    image_base64,
                    latitude,
                    longitude,
                    reported_at,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(report_id) DO UPDATE SET
                    image_path = excluded.image_path,
                    image_base64 = excluded.image_base64,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    reported_at = excluded.reported_at,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    report.report_id,
                    report.image_path,
                    report.image_base64,
                    latitude,
                    longitude,
                    reported_at,
                ),
            )

    def list_reports(self) -> list[StrayDogReport]:
        with self.db.connection() as conn:
            rows = conn.execute(
                """
                SELECT report_id, image_path, image_base64, latitude, longitude, reported_at
                FROM stray_dog_reports
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [self._to_report(row) for row in rows]

    @staticmethod
    def _to_report(row: Any) -> StrayDogReport:
        reported_at = None
        if row["reported_at"]:
            reported_at = datetime.fromisoformat(row["reported_at"])
        location = None
        if row["latitude"] is not None and row["longitude"] is not None:
            location = GeoLocation(latitude=float(row["latitude"]), longitude=float(row["longitude"]))
        return StrayDogReport(
            report_id=str(row["report_id"]),
            image_path=row["image_path"],
            image_base64=row["image_base64"],
            reported_at=reported_at,
            location=location,
        )


class SQLiteMatchNotifier(MatchNotifier):
    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def notify_possible_match(
        self,
        owner_id: str,
        matched_report_ids: list[str],
        similarity_score: float,
    ) -> None:
        payload = json.dumps(matched_report_ids, ensure_ascii=True)
        with self.db.connection() as conn:
            conn.execute(
                """
                INSERT INTO match_notifications (owner_id, matched_report_ids, similarity_score)
                VALUES (?, ?, ?)
                """,
                (owner_id, payload, float(similarity_score)),
            )

    def list_notifications(self) -> list[dict[str, Any]]:
        with self.db.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, owner_id, matched_report_ids, similarity_score, created_at
                FROM match_notifications
                ORDER BY id DESC
                """
            ).fetchall()

        result: list[dict[str, Any]] = []
        for row in rows:
            result.append(
                {
                    "id": int(row["id"]),
                    "owner_id": str(row["owner_id"]),
                    "matched_report_ids": json.loads(row["matched_report_ids"]),
                    "similarity_score": float(row["similarity_score"]),
                    "created_at": row["created_at"],
                }
            )
        return result
