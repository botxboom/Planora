"""Feedback/refinement node triggered for low judge score."""

from __future__ import annotations

from agent.schemas import FinalItinerary, TravelGraphState


def _select_retry_target(issues: list[str]) -> str:
    text = " ".join(issue.lower() for issue in issues)
    if any(keyword in text for keyword in ["budget", "cost", "expensive", "price"]):
        return "optimizer_agent"
    if any(keyword in text for keyword in ["travel time", "realism", "commute", "transit"]):
        return "transport_agent"
    if any(keyword in text for keyword in ["complete", "missing day", "coverage"]):
        return "activity_agent"
    if any(keyword in text for keyword in ["stay", "hotel", "accommodation"]):
        return "stay_agent"
    return "optimizer_agent"


def feedback_node(state: TravelGraphState) -> TravelGraphState:
    final_itinerary = state.get("final_itinerary")
    judge_output = state.get("judge_output")
    if final_itinerary is None or judge_output is None:
        raise ValueError("final_itinerary or judge_output missing in feedback_node")

    current_count = int(state.get("refinement_count", 0))
    retry_target = _select_retry_target(judge_output.issues)
    budget_summary = dict(final_itinerary.budget_summary)
    budget_summary["refinement_applied"] = True
    budget_summary["last_judge_score"] = judge_output.score

    hints = [*judge_output.issues, *judge_output.improved_suggestions]
    notes = list(final_itinerary.optimization_notes)
    notes.append("Refined after judge review due to low score.")
    notes.append(f"Retry target selected: {retry_target}.")
    notes.extend([f"Judge issue: {issue}" for issue in judge_output.issues[:3]])
    notes.extend(
        [f"Improvement: {suggestion}" for suggestion in judge_output.improved_suggestions[:3]]
    )

    refined_itinerary = FinalItinerary(
        destination=final_itinerary.destination,
        duration_days=final_itinerary.duration_days,
        arrival_summary=final_itinerary.arrival_summary,
        daily_plan=final_itinerary.daily_plan,
        budget_summary=budget_summary,
        optimization_notes=notes,
    )

    return {
        "final_itinerary": refined_itinerary,
        "refinement_count": current_count + 1,
        "retry_target": retry_target,
        "judge_feedback_hints": hints,
    }
