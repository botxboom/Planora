"""Shared schemas for the travel planning graph."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict


class UserRequest(BaseModel):
    """Input payload for planning requests."""

    query: str = Field(..., min_length=3, description="Natural language travel request")
    user_id: str | None = Field(
        default=None, description="Optional user identifier for memory and feedback"
    )


class FeedbackRequest(BaseModel):
    run_id: str = Field(..., min_length=4)
    user_feedback: str = Field(..., pattern="^(up|down)$")
    user_id: str | None = None
    comment: str | None = None


class RetryRequest(BaseModel):
    run_id: str = Field(..., min_length=4)
    strategy: str = Field(
        default="auto",
        pattern="^(auto|transport_agent|stay_agent|activity_agent|optimizer_agent)$",
    )
    user_id: str | None = None
    query_override: str | None = None


class UserPreferenceProfile(BaseModel):
    user_id: str
    budget_style: str | None = None
    travel_style: str | None = None


class PlannerOutput(BaseModel):
    """Structured output produced by planner node."""

    destination: str = Field(..., description="Primary destination city/region")
    origin_city: str | None = Field(
        default=None,
        description="Departure city when stated in the query (e.g. from Delhi to Goa)",
    )
    budget_inr: int = Field(..., ge=0, description="Estimated user budget in INR")
    duration_days: int = Field(..., ge=1, description="Trip duration in days")
    preferences: list[str] = Field(
        default_factory=list, description="Extracted user preferences"
    )


class TransportOption(BaseModel):
    mode: str
    route: str
    travel_time_hours: float = Field(..., ge=0)
    estimated_cost_inr: int = Field(..., ge=0)


class TransportAgentOutput(BaseModel):
    options: list[TransportOption] = Field(default_factory=list)
    recommended_mode: str
    rationale: str
    arrival_leg_summary: str = Field(
        default="",
        description=(
            "How the traveler reaches the destination from their home/origin city only "
            "(e.g. direct flight, train). Rough time and cost. No intra-city transport."
        ),
    )
    return_leg_summary: str = Field(
        default="",
        description=(
            "When trip is 2+ days: how they return destination to origin (modes, time vs money, "
            "rough cost). Not intra-city transport."
        ),
    )


class StayOption(BaseModel):
    name: str
    area: str
    nightly_cost_inr: int = Field(..., ge=0)


class StayAgentOutput(BaseModel):
    options: list[StayOption] = Field(default_factory=list)
    selected_stay: StayOption
    estimated_total_stay_cost_inr: int = Field(..., ge=0)
    stay_pricing_note: str = Field(
        default="",
        description="Web-grounded typical nightly rate or range for the selected stay/area (INR).",
    )
    return_day_stay_note: str = Field(
        default="",
        description=(
            "When duration is 2+ days: last-night / layover / night-journey guidance "
            "(e.g. near airport for early flight, or not needed)."
        ),
    )


class ActivityItem(BaseModel):
    name: str
    area: str
    category: str
    estimated_cost_inr: int = Field(..., ge=0)


class ActivityAgentOutput(BaseModel):
    activities: list[ActivityItem] = Field(default_factory=list)
    food_recommendations: list[str] = Field(default_factory=list)
    daily_clustering_note: str
    first_day_local_mobility: str = Field(
        default="",
        description=(
            "Short: airport/station to hotel and first local hops only (not a full city guide)."
        ),
    )
    local_mobility_guide: str = Field(
        default="",
        description=(
            "Realistic ways to move within the destination (scooter/bike rental, app cabs, "
            "buses, self-drive). Must not repeat the inter-city flight/train from home."
        ),
    )


class OptimizerAgentOutput(BaseModel):
    fits_budget: bool
    optimized_total_cost_inr: int = Field(..., ge=0)
    category_split: dict[str, int] = Field(default_factory=dict)
    optimization_notes: list[str] = Field(default_factory=list)


class TripDayPhase(StrEnum):
    reaching = "reaching"
    explore = "explore"
    return_home = "return_home"


class DailyItinerary(BaseModel):
    phase: TripDayPhase = Field(
        ...,
        description="reaching=day1 inbound, explore=middle days, return_home=last day when N>=2.",
    )
    headline: str = Field(..., description="Card title, e.g. Reaching Goa / Explore Goa / Return to Delhi.")
    primary_transport_summary: str = Field(
        default="",
        description="Inter-city to destination (day 1), local mobility (explore), return leg (last day).",
    )
    getting_around: str = Field(
        default="",
        description="First-day local hops after arrival, or local guide on explore days; often empty on return.",
    )
    stay_summary: str = Field(
        default="",
        description="Stay with ₹/night and pricing context; return-day layover note when relevant.",
    )
    theme: str = Field(
        default="",
        description="Legacy: duplicate of headline for older clients.",
    )
    stay: str = Field(
        default="",
        description="Legacy: duplicate of stay_summary for older clients.",
    )
    activities: list[str] = Field(default_factory=list)
    food: list[str] = Field(default_factory=list)


class FinalItinerary(BaseModel):
    """Structured itinerary produced by aggregator node."""

    destination: str
    duration_days: int = Field(..., ge=1)
    arrival_summary: str = Field(
        default="",
        description="Single clear summary: origin city to destination (inter-city leg only).",
    )
    daily_plan: dict[str, DailyItinerary] = Field(default_factory=dict)
    budget_summary: dict[str, Any] = Field(default_factory=dict)
    optimization_notes: list[str] = Field(default_factory=list)


class JudgeOutput(BaseModel):
    score: int = Field(..., ge=1, le=10)
    issues: list[str] = Field(default_factory=list)
    improved_suggestions: list[str] = Field(default_factory=list)
    evaluation_summary: str


class TravelGraphState(TypedDict):
    """LangGraph state shared across nodes."""

    query: str
    user_id: NotRequired[str | None]
    planner_output: NotRequired[PlannerOutput]
    transport_output: NotRequired[TransportAgentOutput]
    stay_output: NotRequired[StayAgentOutput]
    activity_output: NotRequired[ActivityAgentOutput]
    optimizer_output: NotRequired[OptimizerAgentOutput]
    final_itinerary: NotRequired[FinalItinerary]
    judge_output: NotRequired[JudgeOutput]
    refinement_count: NotRequired[int]
    retry_target: NotRequired[str]
    judge_feedback_hints: NotRequired[list[str]]
    memory_profile: NotRequired[UserPreferenceProfile]
    metadata: NotRequired[dict[str, Any]]
