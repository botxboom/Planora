"""Tests for SSE planning stream endpoint."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi.testclient import TestClient


def test_plan_stream_emits_events_and_final_result(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "streaming.db"
    monkeypatch.setenv("PLANORA_DB_PATH", str(db_path))

    import config.settings as settings_module

    settings_module.get_settings.cache_clear()
    import backend.main as backend_main

    importlib.reload(backend_main)

    def fake_stream(state, stream_mode="updates"):
        assert stream_mode == "updates"
        yield {
            "planner": {
                "planner_output": {
                    "destination": "Goa",
                    "budget_inr": 25000,
                    "duration_days": 4,
                    "preferences": ["good food"],
                }
            }
        }
        yield {
            "aggregator": {
                "final_itinerary": {
                    "destination": "Goa",
                    "duration_days": 4,
                    "daily_plan": {},
                    "budget_summary": {"target_budget_inr": 25000},
                    "optimization_notes": [],
                }
            }
        }
        yield {
            "judge": {
                "judge_output": {
                    "score": 8,
                    "issues": [],
                    "improved_suggestions": [],
                    "evaluation_summary": "Good",
                }
            }
        }

    monkeypatch.setattr(backend_main.graph, "stream", fake_stream)

    client = TestClient(backend_main.app)
    response = client.post(
        "/plan/stream",
        json={"query": "Plan Goa trip", "user_id": "u-1"},
    )
    assert response.status_code == 200
    assert "event: run_started" in response.text
    assert "event: planner_completed" in response.text
    assert "event: final_result" in response.text
