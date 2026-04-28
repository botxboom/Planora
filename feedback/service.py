"""Feedback processing and memory update service."""

from __future__ import annotations

from agent.schemas import UserPreferenceProfile
from feedback.store import get_planning_run, save_feedback_event
from memory.store import upsert_user_preferences


def _infer_budget_style(target_budget_inr: int | None) -> str | None:
    if target_budget_inr is None:
        return None
    if target_budget_inr <= 30000:
        return "budget"
    if target_budget_inr >= 100000:
        return "luxury"
    return "midrange"


def _infer_travel_style(query: str) -> str:
    lowered = query.lower()
    if "minimal travel time" in lowered or "fast" in lowered:
        return "efficient"
    if "chill" in lowered or "relaxed" in lowered:
        return "chill"
    return "balanced"


def record_feedback_and_update_memory(
    *,
    run_id: str,
    user_feedback: str,
    comment: str | None,
    user_id: str | None,
) -> dict:
    feedback_id = save_feedback_event(
        run_id=run_id,
        user_feedback=user_feedback,
        comment=comment,
    )
    run = get_planning_run(run_id)
    if run is None:
        return {"feedback_id": feedback_id, "memory_updated": False, "profile": None}

    effective_user_id = user_id or run.get("user_id")
    if not effective_user_id:
        return {"feedback_id": feedback_id, "memory_updated": False, "profile": None}

    if user_feedback != "up":
        return {"feedback_id": feedback_id, "memory_updated": False, "profile": None}

    plan = run.get("plan", {})
    final_itinerary = plan.get("final_itinerary", {})
    budget_summary = final_itinerary.get("budget_summary", {})
    target_budget = budget_summary.get("target_budget_inr")

    profile: UserPreferenceProfile = upsert_user_preferences(
        user_id=effective_user_id,
        budget_style=_infer_budget_style(target_budget),
        travel_style=_infer_travel_style(run.get("query", "")),
    )

    return {
        "feedback_id": feedback_id,
        "memory_updated": True,
        "profile": profile.model_dump(),
    }
