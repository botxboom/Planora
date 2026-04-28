"""Persistence for planning runs and user feedback."""

from __future__ import annotations

import json
from typing import Any

from config.db import get_connection


def _ensure_tables() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS planning_runs (
                run_id TEXT PRIMARY KEY,
                user_id TEXT,
                query TEXT NOT NULL,
                plan_json TEXT NOT NULL,
                judge_score INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                user_feedback TEXT NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(run_id) REFERENCES planning_runs(run_id)
            )
            """
        )
        connection.commit()


def save_planning_run(
    *,
    run_id: str,
    user_id: str | None,
    query: str,
    plan_payload: dict[str, Any],
    judge_score: int | None,
) -> None:
    _ensure_tables()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO planning_runs (run_id, user_id, query, plan_json, judge_score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, user_id, query, json.dumps(plan_payload), judge_score),
        )
        connection.commit()


def get_planning_run(run_id: str) -> dict[str, Any] | None:
    _ensure_tables()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT run_id, user_id, query, plan_json, judge_score, created_at
            FROM planning_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "run_id": row["run_id"],
        "user_id": row["user_id"],
        "query": row["query"],
        "plan": json.loads(row["plan_json"]),
        "judge_score": row["judge_score"],
        "created_at": row["created_at"],
    }


def save_feedback_event(*, run_id: str, user_feedback: str, comment: str | None) -> int:
    _ensure_tables()
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO feedback_events (run_id, user_feedback, comment)
            VALUES (?, ?, ?)
            """,
            (run_id, user_feedback, comment),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_feedback_events(run_id: str) -> list[dict[str, Any]]:
    _ensure_tables()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, run_id, user_feedback, comment, created_at
            FROM feedback_events
            WHERE run_id = ?
            ORDER BY id ASC
            """,
            (run_id,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "run_id": row["run_id"],
            "user_feedback": row["user_feedback"],
            "comment": row["comment"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
