"""Planner node for extracting structured constraints from user query."""

from __future__ import annotations

import re

from agent.schemas import PlannerOutput, TravelGraphState, UserPreferenceProfile
from memory.store import get_user_preferences

DEFAULT_BUDGET_INR = 20000
DEFAULT_DURATION_DAYS = 3


def _extract_duration_days(query: str) -> int:
    day_match = re.search(r"(\d+)\s*[- ]?\s*day", query, re.IGNORECASE)
    if day_match:
        return max(1, int(day_match.group(1)))
    return DEFAULT_DURATION_DAYS


def _extract_budget_inr(query: str) -> int:
    budget_patterns = [
        r"(?:under|within|budget(?:\s*of)?)\s*[₹rsinr\s,]*?(\d[\d,]*)",
        r"₹\s*(\d[\d,]*)",
        r"(\d[\d,]*)\s*(?:inr|rs)",
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if not match:
            continue
        value = int(match.group(1).replace(",", ""))
        if value > 0:
            return value
    return DEFAULT_BUDGET_INR


def _title_city(raw: str) -> str:
    return " ".join(part.capitalize() for part in raw.strip().split())


def _extract_route(query: str) -> tuple[str, str | None]:
    """Return (destination, origin_city_or_none) from explicit route phrases."""

    # "from Delhi to Goa under ..." / "from Bangalore to Goa"
    from_to = re.search(
        r"(?i)\bfrom\s+([A-Za-z][A-Za-z\s]*?)\s+to\s+([A-Za-z][A-Za-z\s]*?)(?:\s+under|\s+within|\s+with|\s+[,]|\s+\d|\s*$)",
        query,
    )
    if from_to:
        origin = _title_city(from_to.group(1))
        dest = _title_city(from_to.group(2))
        return dest, origin

    # "to Goa from Delhi under ..." / "trip to Goa from Bangalore"
    to_from = re.search(
        r"(?i)\bto\s+([A-Za-z][A-Za-z\s]*?)\s+from\s+([A-Za-z][A-Za-z\s]*?)(?:\s+under|\s+within|\s+with|\s+[,]|\s+\d|\s*$)",
        query,
    )
    if to_from:
        dest = _title_city(to_from.group(1))
        origin = _title_city(to_from.group(2))
        return dest, origin

    return _extract_destination_fallback(query), None


def _extract_destination_fallback(query: str) -> str:
    """Destination only when no explicit origin+destination pair was found."""

    to_match = re.search(
        r"(?i)\bto\s+([A-Za-z][A-Za-z\s]*?)(?:\s+from\s+[A-Za-z]|\s+under|\s+within|\s+with|\s+[,]|\s+\d|\s*$)",
        query,
    )
    if to_match:
        dest = to_match.group(1).strip()
        dest = re.sub(r"(?i)\s+from\s+.*$", "", dest).strip()
        return _title_city(dest) if dest else "Unknown"

    fallback_words = re.findall(r"\b[A-Z][a-zA-Z]+\b", query)
    if fallback_words:
        return fallback_words[-1]
    return "Unknown"


def _extract_preferences(query: str) -> list[str]:
    preference_candidates = {
        "good food": ["food", "good food", "local cuisine"],
        "minimal travel time": ["minimal travel time", "less travel", "short commute"],
        "budget": ["budget", "affordable", "cheap"],
        "chill": ["chill", "relaxed", "slow paced"],
    }

    lowered = query.lower()
    preferences: list[str] = []
    for normalized, aliases in preference_candidates.items():
        if any(alias in lowered for alias in aliases):
            preferences.append(normalized)

    with_clause = re.search(r"\bwith\s+(.+)$", query, re.IGNORECASE)
    if with_clause:
        free_text = with_clause.group(1).strip()
        if free_text and free_text not in preferences:
            preferences.append(free_text)
    return preferences


def planner_node(state: TravelGraphState) -> TravelGraphState:
    """Parse user request into structured planner output."""

    query = state["query"]
    preferences = _extract_preferences(query)

    memory_profile: UserPreferenceProfile | None = None
    user_id = state.get("user_id")
    if user_id:
        memory_profile = get_user_preferences(user_id)
        if memory_profile:
            if memory_profile.budget_style:
                preferences.append(f"memory_budget_style={memory_profile.budget_style}")
            if memory_profile.travel_style:
                preferences.append(f"memory_travel_style={memory_profile.travel_style}")

    destination, origin_city = _extract_route(query)
    planner_output = PlannerOutput(
        destination=destination,
        origin_city=origin_city,
        budget_inr=_extract_budget_inr(query),
        duration_days=_extract_duration_days(query),
        preferences=preferences,
    )
    result: TravelGraphState = {"planner_output": planner_output}
    if memory_profile:
        result["memory_profile"] = memory_profile
    return result
