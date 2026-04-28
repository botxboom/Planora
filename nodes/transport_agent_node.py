"""Transport agent node using tool-calling."""

from __future__ import annotations

from agents.tool_calling_runner import run_structured_tool_calling_agent
from agent.schemas import TransportAgentOutput, TravelGraphState
from tools.travel_tools import estimate_costs, get_distance, web_search_travel


def transport_agent_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    if planner_output is None:
        raise ValueError("planner_output missing in transport_agent_node")

    hints = state.get("judge_feedback_hints", [])
    planner_with_hints = planner_output.model_copy(
        update={
            "preferences": planner_output.preferences + [f"judge_hint={hint}" for hint in hints[:3]]
        }
    )
    output = run_structured_tool_calling_agent(
        agent_name="TransportAgent",
        planner_output=planner_with_hints,
        instruction=(
            "Propose practical transport options prioritizing minimal travel time and "
            "budget fit. Include multiple transport modes and one recommendation. "
            "When calling get_distance, use origin_city from the planner JSON as the "
            "source city if it is set; otherwise infer the departure city only from the "
            "user query text (do not assume Mumbai). Use destination from planner JSON. "
            "You may call web_search_travel once for realistic inter-city routes, terminals, "
            "or typical fares when unsure. "
            "Always set arrival_leg_summary to 1–3 clear sentences describing ONLY how the "
            "traveler gets from their origin city to the destination (e.g. flight/train/bus, "
            "approx duration and cost). Do not put intra-city scooter/cab advice in arrival_leg_summary. "
            "When duration_days in the planner JSON is 2 or more, always set return_leg_summary to "
            "1–3 sentences on returning from destination back to origin_city (or inferred origin): "
            "recommended modes, time vs money tradeoff, rough cost — not local sightseeing transport. "
            "For duration_days==1, return_leg_summary may briefly note same-day return options or be empty. "
            "You may call web_search_travel for return routes or fares when unsure. "
            "If judge feedback exists, prioritize fixing those realism concerns."
        ),
        tools=[get_distance, estimate_costs, web_search_travel],
        output_model=TransportAgentOutput,
    )

    return {"transport_output": output}
