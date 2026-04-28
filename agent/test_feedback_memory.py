"""Tests for feedback persistence and memory updates."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def test_feedback_updates_user_memory(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "planora_test.db"
    monkeypatch.setenv("PLANORA_DB_PATH", str(db_path))

    import config.settings as settings_module

    settings_module.get_settings.cache_clear()

    import backend.main as backend_main

    importlib.reload(backend_main)

    def fake_invoke(initial_state):
        return {
            "planner_output": {
                "destination": "Goa",
                "budget_inr": 25000,
                "duration_days": 4,
                "preferences": ["good food", "minimal travel time"],
            },
            "final_itinerary": {
                "destination": "Goa",
                "duration_days": 4,
                "daily_plan": {},
                "budget_summary": {"target_budget_inr": 25000},
                "optimization_notes": [],
            },
            "judge_output": {"score": 8, "issues": [], "improved_suggestions": [], "evaluation_summary": "Good"},
        }

    monkeypatch.setattr(backend_main.graph, "invoke", fake_invoke)
    client = TestClient(backend_main.app)

    plan_response = client.post(
        "/plan",
        json={
            "query": "Plan a 4-day trip to Goa under ₹25,000 with good food and minimal travel time",
            "user_id": "user-123",
        },
    )
    assert plan_response.status_code == 200
    run_id = plan_response.json()["metadata"]["run_id"]

    feedback_response = client.post(
        "/feedback",
        json={
            "run_id": run_id,
            "user_feedback": "up",
            "user_id": "user-123",
            "comment": "Nice plan",
        },
    )
    assert feedback_response.status_code == 200
    payload = feedback_response.json()
    assert payload["status"] == "recorded"
    assert payload["memory_updated"] is True

    memory_response = client.get("/memory/user-123")
    assert memory_response.status_code == 200
    profile = memory_response.json()["profile"]
    assert profile["budget_style"] == "budget"
    assert profile["travel_style"] == "efficient"


def test_feedback_endpoint_404_for_unknown_run(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "planora_test_404.db"
    monkeypatch.setenv("PLANORA_DB_PATH", str(db_path))

    import config.settings as settings_module

    settings_module.get_settings.cache_clear()

    import backend.main as backend_main

    importlib.reload(backend_main)
    client = TestClient(backend_main.app)

    response = client.post(
        "/feedback",
        json={"run_id": "unknown", "user_feedback": "up"},
    )
    assert response.status_code == 404
