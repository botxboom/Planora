"""Tests for LangGraph travel pipeline (planner, agents, aggregator, judge)."""

from __future__ import annotations

import pytest

from agent.schemas import (
    ActivityAgentOutput,
    ActivityItem,
    JudgeOutput,
    OptimizerAgentOutput,
    StayAgentOutput,
    StayOption,
    TransportAgentOutput,
    TransportOption,
    TripDayPhase,
)
from graph.travel_graph import build_travel_graph
from nodes.planner_node import planner_node


SAMPLE_QUERY = "Plan a 4-day trip to Goa under ₹25,000 with good food and minimal travel time"


def test_planner_extracts_expected_fields() -> None:
    initial_state = {"query": SAMPLE_QUERY, "metadata": {}}
    updated_state = planner_node(initial_state)
    planner_output = updated_state["planner_output"]

    assert planner_output.destination == "Goa"
    assert planner_output.origin_city is None
    assert planner_output.duration_days == 4
    assert planner_output.budget_inr == 25000
    assert any("food" in preference for preference in planner_output.preferences)


def test_planner_extracts_from_city_to_city() -> None:
    q = "Plan a trip from Delhi to Goa under 25000"
    out = planner_node({"query": q, "metadata": {}})["planner_output"]
    assert out.destination == "Goa"
    assert out.origin_city == "Delhi"


def test_planner_extracts_to_city_from_city() -> None:
    q = "Plan a trip to Goa from Bangalore under 20000"
    out = planner_node({"query": q, "metadata": {}})["planner_output"]
    assert out.destination == "Goa"
    assert out.origin_city == "Bangalore"


def test_planner_injects_memory_preferences(monkeypatch: pytest.MonkeyPatch) -> None:
    from agent.schemas import UserPreferenceProfile

    monkeypatch.setattr(
        "nodes.planner_node.get_user_preferences",
        lambda user_id: UserPreferenceProfile(
            user_id=user_id, budget_style="budget", travel_style="chill"
        ),
    )
    state = planner_node({"query": SAMPLE_QUERY, "user_id": "u-1", "metadata": {}})
    preferences = state["planner_output"].preferences
    assert "memory_budget_style=budget" in preferences
    assert "memory_travel_style=chill" in preferences
    assert "memory_profile" in state


@pytest.fixture
def mock_structured_agent_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_runner(*, output_model, **kwargs):
        if output_model is TransportAgentOutput:
            return TransportAgentOutput(
                options=[
                    TransportOption(
                        mode="flight",
                        route="Mumbai to Goa direct",
                        travel_time_hours=1.3,
                        estimated_cost_inr=4500,
                    )
                ],
                recommended_mode="flight",
                rationale="Fastest option with acceptable cost.",
                arrival_leg_summary="",
                return_leg_summary="",
            )
        if output_model is StayAgentOutput:
            chosen = StayOption(name="Zostel Goa", area="Anjuna", nightly_cost_inr=1200)
            return StayAgentOutput(
                options=[chosen],
                selected_stay=chosen,
                estimated_total_stay_cost_inr=4800,
                stay_pricing_note="Typical hostel bunks in Anjuna run about ₹900–1,500/night in season.",
                return_day_stay_note="Late flight: consider a few hours rest near GOI or flexible checkout.",
            )
        if output_model is ActivityAgentOutput:
            return ActivityAgentOutput(
                activities=[
                    ActivityItem(
                        name="Baga Beach",
                        area="North Goa",
                        category="beach",
                        estimated_cost_inr=400,
                    ),
                    ActivityItem(
                        name="Fontainhas Walk",
                        area="Panjim",
                        category="heritage",
                        estimated_cost_inr=300,
                    ),
                ],
                food_recommendations=["Mum's Kitchen", "Gunpowder"],
                daily_clustering_note="Grouped by nearby zones for low commute.",
                first_day_local_mobility=(
                    "From Goa airport or Thivim station, prepaid taxis or app cabs to Anjuna; "
                    "rent a scooter for short hops on day one."
                ),
                local_mobility_guide=(
                    "Within Goa, rent a scooter or bike for short hops between beaches; "
                    "use app cabs (GoaMiles, Uber) for longer north–south runs or late nights."
                ),
            )
        if output_model is OptimizerAgentOutput:
            return OptimizerAgentOutput(
                fits_budget=True,
                optimized_total_cost_inr=22000,
                category_split={
                    "transport_inr": 4500,
                    "stay_inr": 4800,
                    "activities_inr": 2000,
                    "food_inr": 3500,
                    "buffer_inr": 7200,
                },
                optimization_notes=["Kept transport minimal and clustered activities by area."],
            )
        raise AssertionError("Unknown output model in fake runner.")

    monkeypatch.setattr("nodes.transport_agent_node.run_structured_tool_calling_agent", fake_runner)
    monkeypatch.setattr("nodes.stay_agent_node.run_structured_tool_calling_agent", fake_runner)
    monkeypatch.setattr("nodes.activity_agent_node.run_structured_tool_calling_agent", fake_runner)
    monkeypatch.setattr("nodes.optimizer_agent_node.run_structured_tool_calling_agent", fake_runner)


@pytest.fixture
def mock_judge_high_score(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_evaluate_itinerary(**kwargs):
        return JudgeOutput(
            score=8,
            issues=["Minor optimization possible."],
            improved_suggestions=["Tighten activity sequencing by area."],
            evaluation_summary="Plan is realistic and complete.",
        )

    monkeypatch.setattr("nodes.judge_node.evaluate_itinerary", fake_evaluate_itinerary)


@pytest.fixture
def mock_judge_low_score(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_evaluate_itinerary(**kwargs):
        return JudgeOutput(
            score=5,
            issues=["Budget split is too loose.", "Day sequencing may increase travel time."],
            improved_suggestions=[
                "Reduce long hops between zones.",
                "Reallocate more budget buffer to activities.",
            ],
            evaluation_summary="Needs revision for stronger feasibility.",
        )

    monkeypatch.setattr("nodes.judge_node.evaluate_itinerary", fake_evaluate_itinerary)


def test_graph_executes_and_returns_structured_output(
    mock_structured_agent_runner: None, mock_judge_high_score: None
) -> None:
    graph = build_travel_graph()
    result = graph.invoke({"query": SAMPLE_QUERY, "metadata": {}})

    assert "planner_output" in result
    assert "transport_output" in result
    assert "stay_output" in result
    assert "activity_output" in result
    assert "optimizer_output" in result
    assert "final_itinerary" in result
    assert "judge_output" in result
    assert result["planner_output"].destination == "Goa"
    assert result["final_itinerary"].budget_summary["target_budget_inr"] == 25000
    assert "flight" in result["final_itinerary"].arrival_summary.lower()
    assert "goa" in result["final_itinerary"].arrival_summary.lower()
    daily = result["final_itinerary"].daily_plan
    assert daily["day_1"].phase == TripDayPhase.reaching
    assert daily["day_2"].phase == TripDayPhase.explore
    assert daily["day_3"].phase == TripDayPhase.explore
    assert daily["day_4"].phase == TripDayPhase.return_home
    assert "Reaching Goa" in daily["day_1"].headline
    assert "Explore Goa" in daily["day_2"].headline
    assert "Return to" in daily["day_4"].headline
    assert "flight" in daily["day_1"].primary_transport_summary.lower()
    assert daily["day_1"].getting_around
    assert "scooter" in daily["day_1"].getting_around.lower()
    assert "scooter" in daily["day_2"].primary_transport_summary.lower()
    assert daily["day_1"].stay_summary
    assert "1,200" in daily["day_1"].stay_summary or "1200" in daily["day_1"].stay_summary
    assert daily["day_4"].stay_summary
    assert result["judge_output"].score == 8
    assert "refinement_count" not in result or result["refinement_count"] == 0


def test_low_judge_score_triggers_bounded_refinements(
    mock_structured_agent_runner: None, mock_judge_low_score: None
) -> None:
    graph = build_travel_graph()
    result = graph.invoke({"query": SAMPLE_QUERY, "metadata": {}})

    assert result["judge_output"].score == 5
    assert result["refinement_count"] == 2
    assert result["retry_target"] == "optimizer_agent"
    assert result["final_itinerary"].budget_summary["refinement_applied"] is True
    assert any(
        "Refinement loops executed" in note
        for note in result["final_itinerary"].optimization_notes
    )


def test_judge_retry_stops_when_score_recovers(
    mock_structured_agent_runner: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    scores = [5, 8]

    def fake_evaluate_itinerary(**kwargs):
        score = scores.pop(0) if scores else 8
        return JudgeOutput(
            score=score,
            issues=["Travel time realism issue"] if score < 7 else [],
            improved_suggestions=["Reduce zone hopping"] if score < 7 else [],
            evaluation_summary="Auto-test judge response",
        )

    monkeypatch.setattr("nodes.judge_node.evaluate_itinerary", fake_evaluate_itinerary)

    graph = build_travel_graph()
    result = graph.invoke({"query": SAMPLE_QUERY, "metadata": {}})

    assert result["judge_output"].score == 8
    assert result["refinement_count"] == 1
    assert result["retry_target"] == "transport_agent"
