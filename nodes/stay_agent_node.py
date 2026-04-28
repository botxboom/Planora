"""Stay agent node using tool-calling."""

from __future__ import annotations

from agents.tool_calling_runner import run_structured_tool_calling_agent
from agent.schemas import StayAgentOutput, TravelGraphState
from tools.travel_tools import estimate_costs, get_hotels, web_search_travel


def stay_agent_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    if planner_output is None:
        raise ValueError("planner_output missing in stay_agent_node")

    nightly_budget = max(1000, int((planner_output.budget_inr * 0.4) / planner_output.duration_days))
    hints = state.get("judge_feedback_hints", [])
    planner_with_hint = planner_output.model_copy(
        update={
            "preferences": planner_output.preferences
            + [f"nightly_stay_budget_hint_inr={nightly_budget}"]
            + [f"judge_hint={hint}" for hint in hints[:3]]
        }
    )

    output = run_structured_tool_calling_agent(
        agent_name="StayAgent",
        planner_output=planner_with_hint,
        instruction=(
            "Find stay options within budget and select one stay recommendation "
            "that minimizes extra commute. "
            "Use web_search_travel to check typical nightly rates or recent price ranges for the "
            "selected property or neighborhood (INR); summarize in stay_pricing_note (1–3 sentences, "
            "grounded in snippets when available). "
            "When duration_days is 2 or more, fill return_day_stay_note: practical guidance for the "
            "LAST travel day (checkout timing, airport/station-near sleep for early/late departures, "
            "night trains, or 'not needed' if a simple checkout suffices). "
            "If judge feedback exists, correct stay-related gaps."
        ),
        tools=[get_hotels, estimate_costs, web_search_travel],
        output_model=StayAgentOutput,
    )

    return {"stay_output": output}
