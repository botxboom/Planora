"""Activity agent node using tool-calling."""

from __future__ import annotations

from agents.tool_calling_runner import run_structured_tool_calling_agent
from agent.schemas import ActivityAgentOutput, TravelGraphState
from tools.travel_tools import get_distance, search_places, web_search_travel


def activity_agent_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    if planner_output is None:
        raise ValueError("planner_output missing in activity_agent_node")

    hints = state.get("judge_feedback_hints", [])
    planner_with_hints = planner_output.model_copy(
        update={
            "preferences": planner_output.preferences + [f"judge_hint={hint}" for hint in hints[:3]]
        }
    )
    output = run_structured_tool_calling_agent(
        agent_name="ActivityAgent",
        planner_output=planner_with_hints,
        instruction=(
            "Suggest activities and food options clustered by area to reduce travel time "
            "between points in each day. "
            "Call web_search_travel with queries like '<destination> local transport scooter rental app cabs' "
            "when you need grounded, practical intra-city mobility (not flights from home). "
            "Always set first_day_local_mobility to 2–4 short sentences focused on arrival day only: "
            "airport/station to hotel transfers and immediate local options for first stops — not a full city guide. "
            "Always set local_mobility_guide to 2–5 sentences on realistic on-the-ground transport "
            "(rented two-wheeler, app taxis, buses between zones, self-drive) for moving between "
            "the areas you recommend on middle/explore days — never describe the inter-city flight/train "
            "from the user's home here. "
            "If judge feedback exists, improve completeness and feasibility."
        ),
        tools=[search_places, get_distance, web_search_travel],
        output_model=ActivityAgentOutput,
    )

    return {"activity_output": output}
