import json

from app.database import get_db

from app.ai.gemini_service import (
    GeminiRecommendationService
)


class RecommendationService:

    def __init__(self):

        self.ai = (
            GeminiRecommendationService()
        )

    def create(
        self,
        user_id: int,
        planner: str,
        payload: dict,
        image_bytes=None,
        image_mime=None
    ):

        result = self.ai.generate(
            planner=planner,
            data=payload,
            image_bytes=image_bytes,
            image_mime=image_mime
        )

        with get_db() as db:

            cursor = db.execute(
                """
                INSERT INTO recommendations
                (
                    user_id,
                    planner_type,
                    request_json,
                    result_json
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    planner,
                    json.dumps(payload),
                    result.model_dump_json()
                )
            )

            recommendation_id = (
                cursor.lastrowid
            )

        return (
            recommendation_id,
            result
        )

    def history(
        self,
        user_id: int,
        limit: int = 50
    ):

        with get_db() as db:

            rows = db.execute(
                """
                SELECT
                    id,
                    planner_type,
                    request_json,
                    result_json,
                    created_at
                FROM recommendations
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    user_id,
                    limit
                )
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


service = RecommendationService()
