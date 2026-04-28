"""Optimizer agent node using tool-calling."""

from __future__ import annotations

from agents.tool_calling_runner import run_structured_tool_calling_agent
from agent.schemas import OptimizerAgentOutput, PlannerOutput, TravelGraphState
from tools.travel_tools import estimate_costs


def optimizer_agent_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    transport_output = state.get("transport_output")
    stay_output = state.get("stay_output")
    activity_output = state.get("activity_output")

    if planner_output is None:
        raise ValueError("planner_output missing in optimizer_agent_node")
    if transport_output is None or stay_output is None or activity_output is None:
        return {}

    activity_cost = sum(item.estimated_cost_inr for item in activity_output.activities)
    hints = state.get("judge_feedback_hints", [])
    budget_context = {
        "transport_inr": transport_output.options[0].estimated_cost_inr
        if transport_output.options
        else 0,
        "stay_inr": stay_output.estimated_total_stay_cost_inr,
        "activities_inr": activity_cost,
    }

    planner_with_hint = PlannerOutput(
        destination=planner_output.destination,
        budget_inr=planner_output.budget_inr,
        duration_days=planner_output.duration_days,
        preferences=planner_output.preferences
        + [f"cost_inputs={budget_context}"]
        + [f"judge_hint={hint}" for hint in hints[:3]],
    )

    output = run_structured_tool_calling_agent(
        agent_name="OptimizerAgent",
        planner_output=planner_with_hint,
        instruction=(
            "Optimize the combined plan for budget adherence and realistic allocation "
            "across transport, stay, and activities. If judge feedback exists, directly resolve those issues."
        ),
        tools=[estimate_costs],
        output_model=OptimizerAgentOutput,
    )

    return {"optimizer_output": output}
