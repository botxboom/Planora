"""LLM-as-judge evaluator for generated itineraries."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from agent.schemas import FinalItinerary, JudgeOutput, PlannerOutput
from config.llm import get_anthropic_llm


def evaluate_itinerary(*, planner_output: PlannerOutput, itinerary: FinalItinerary) -> JudgeOutput:
    """Evaluate itinerary quality using Anthropic structured output."""

    llm = get_anthropic_llm(temperature=0)
    structured_llm = llm.with_structured_output(JudgeOutput)

    messages = [
        SystemMessage(
            content=(
                "You are a strict travel-plan judge. Evaluate itinerary quality on three criteria:\n"
                "1) budget adherence\n"
                "2) realism and travel-time feasibility\n"
                "3) completeness across days\n"
                "Return a score from 1 to 10, clear issues, and actionable improved suggestions."
            )
        ),
        HumanMessage(
            content=(
                "Planner constraints:\n"
                f"{planner_output.model_dump_json(indent=2)}\n\n"
                "Generated itinerary:\n"
                f"{itinerary.model_dump_json(indent=2)}\n\n"
                "Penalize missing daily coverage, unrealistic costs, and excessive transit."
            )
        ),
    ]

    return structured_llm.invoke(messages)
