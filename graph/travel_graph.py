"""LangGraph assembly for Phase 5 workflow with targeted retries."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agent.schemas import TravelGraphState
from config.settings import get_settings
from nodes.activity_agent_node import activity_agent_node
from nodes.aggregator_node import aggregator_node
from nodes.feedback_node import feedback_node
from nodes.judge_node import judge_node
from nodes.optimizer_agent_node import optimizer_agent_node
from nodes.planner_node import planner_node
from nodes.stay_agent_node import stay_agent_node
from nodes.transport_agent_node import transport_agent_node

def _route_after_judge(state: TravelGraphState) -> str:
    settings = get_settings()
    judge_output = state.get("judge_output")
    if judge_output is None:
        return END

    refinement_count = int(state.get("refinement_count", 0))
    if (
        judge_output.score < settings.judge_threshold
        and refinement_count < settings.max_refinement_loops
    ):
        return "feedback"
    return END


def _route_after_feedback(state: TravelGraphState) -> str:
    target = state.get("retry_target", "optimizer_agent")
    if target in {"transport_agent", "stay_agent", "activity_agent", "optimizer_agent"}:
        return target
    return "optimizer_agent"


def build_travel_graph():
    """Build and compile the phase-5 graph."""

    graph_builder = StateGraph(TravelGraphState)
    graph_builder.add_node("planner", planner_node)
    graph_builder.add_node("transport_agent", transport_agent_node)
    graph_builder.add_node("stay_agent", stay_agent_node)
    graph_builder.add_node("activity_agent", activity_agent_node)
    graph_builder.add_node("optimizer_agent", optimizer_agent_node)
    graph_builder.add_node("aggregator", aggregator_node)
    graph_builder.add_node("judge", judge_node)
    graph_builder.add_node("feedback", feedback_node)

    graph_builder.add_edge(START, "planner")
    graph_builder.add_edge("planner", "transport_agent")
    graph_builder.add_edge("planner", "stay_agent")
    graph_builder.add_edge("planner", "activity_agent")

    graph_builder.add_edge("transport_agent", "optimizer_agent")
    graph_builder.add_edge("stay_agent", "optimizer_agent")
    graph_builder.add_edge("activity_agent", "optimizer_agent")
    graph_builder.add_edge("optimizer_agent", "aggregator")
    graph_builder.add_edge("aggregator", "judge")
    graph_builder.add_conditional_edges("judge", _route_after_judge, ["feedback", END])
    graph_builder.add_conditional_edges(
        "feedback",
        _route_after_feedback,
        ["transport_agent", "stay_agent", "activity_agent", "optimizer_agent"],
    )

    return graph_builder.compile()
