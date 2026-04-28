"""Judge node that scores final itinerary quality."""

from __future__ import annotations

from agent.schemas import TravelGraphState
from judge.evaluator import evaluate_itinerary


def judge_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    final_itinerary = state.get("final_itinerary")
    if planner_output is None or final_itinerary is None:
        raise ValueError("planner_output or final_itinerary missing in judge_node")

    judge_output = evaluate_itinerary(
        planner_output=planner_output,
        itinerary=final_itinerary,
    )
    return {"judge_output": judge_output}
