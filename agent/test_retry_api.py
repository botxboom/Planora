"""Tests for explicit retry endpoint behavior."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from feedback.store import save_planning_run


def test_retry_endpoint_uses_strategy_and_parent_context(
    monkeypatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "retry.db"
    monkeypatch.setenv("PLANORA_DB_PATH", str(db_path))

    import config.settings as settings_module

    settings_module.get_settings.cache_clear()
    import backend.main as backend_main

    importlib.reload(backend_main)

    save_planning_run(
        run_id="seed-run",
        user_id="user-1",
        query="Plan Goa trip under 25000",
        plan_payload={
            "judge_output": {
                "score": 5,
                "issues": ["Budget too high"],
                "improved_suggestions": ["Reduce hotel costs"],
            }
        },
        judge_score=5,
    )

    captured = {"state": None}

    def fake_invoke(initial_state):
        captured["state"] = initial_state
        return {
            "planner_output": {
                "destination": "Goa",
                "budget_inr": 24000,
                "duration_days": 4,
                "preferences": [],
            },
            "final_itinerary": {
                "destination": "Goa",
                "duration_days": 4,
                "daily_plan": {},
                "budget_summary": {"target_budget_inr": 24000},
                "optimization_notes": [],
            },
            "judge_output": {
                "score": 8,
                "issues": [],
                "improved_suggestions": [],
                "evaluation_summary": "Improved",
            },
        }

    monkeypatch.setattr(backend_main.graph, "invoke", fake_invoke)

    client = TestClient(backend_main.app)
    response = client.post(
        "/plan/retry",
        json={"run_id": "seed-run", "strategy": "optimizer_agent"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["parent_run_id"] == "seed-run"
    assert payload["metadata"]["retry_strategy"] == "optimizer_agent"
    assert captured["state"]["retry_target"] == "optimizer_agent"
    assert "Budget too high" in captured["state"]["judge_feedback_hints"]
