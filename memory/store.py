"""Persistent user memory storage."""

from __future__ import annotations

from agent.schemas import UserPreferenceProfile
from config.db import get_connection


def _ensure_table() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                budget_style TEXT,
                travel_style TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def get_user_preferences(user_id: str) -> UserPreferenceProfile | None:
    _ensure_table()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT user_id, budget_style, travel_style FROM user_preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return UserPreferenceProfile(
        user_id=row["user_id"],
        budget_style=row["budget_style"],
        travel_style=row["travel_style"],
    )


def upsert_user_preferences(
    *, user_id: str, budget_style: str | None = None, travel_style: str | None = None
) -> UserPreferenceProfile:
    _ensure_table()
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT budget_style, travel_style FROM user_preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        merged_budget = budget_style if budget_style is not None else (
            existing["budget_style"] if existing else None
        )
        merged_travel = travel_style if travel_style is not None else (
            existing["travel_style"] if existing else None
        )

        connection.execute(
            """
            INSERT INTO user_preferences (user_id, budget_style, travel_style, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                budget_style = excluded.budget_style,
                travel_style = excluded.travel_style,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, merged_budget, merged_travel),
        )
        connection.commit()

    return UserPreferenceProfile(
        user_id=user_id, budget_style=merged_budget, travel_style=merged_travel
    )
