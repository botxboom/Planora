"""Aggregator node to compose final itinerary from agent outputs."""

from __future__ import annotations

from agent.schemas import (
    ActivityAgentOutput,
    DailyItinerary,
    FinalItinerary,
    StayAgentOutput,
    TravelGraphState,
    TripDayPhase,
)


def _arrival_summary(state: TravelGraphState) -> str:
    """Inter-city leg only (home/origin → destination)."""

    planner_output = state["planner_output"]
    transport_output = state["transport_output"]
    custom = (transport_output.arrival_leg_summary or "").strip()
    if custom:
        return custom

    origin = planner_output.origin_city or "your departure city"
    dest = planner_output.destination
    options = transport_output.options
    mode_key = (transport_output.recommended_mode or "").strip().lower()
    pick = None
    for opt in options:
        if opt.mode.lower() == mode_key:
            pick = opt
            break
    if pick is None and options:
        pick = options[0]
    if pick is not None:
        return (
            f"{pick.mode.title()} from {origin} to {dest}: {pick.route}. "
            f"About {pick.travel_time_hours:.1f} h, roughly ₹{pick.estimated_cost_inr:,} (estimate)."
        )
    return (
        f"Plan inter-city travel from {origin} to {dest} using the options and rationale "
        f"from the transport agent ({transport_output.recommended_mode})."
    )


def _return_leg_summary(state: TravelGraphState) -> str:
    """Inter-city leg destination → origin (last day)."""

    planner_output = state["planner_output"]
    transport_output = state["transport_output"]
    custom = (transport_output.return_leg_summary or "").strip()
    if custom:
        return custom

    origin = planner_output.origin_city or "your departure city"
    dest = planner_output.destination
    options = transport_output.options
    mode_key = (transport_output.recommended_mode or "").strip().lower()
    pick = None
    for opt in options:
        if opt.mode.lower() == mode_key:
            pick = opt
            break
    if pick is None and options:
        pick = options[0]
    if pick is not None:
        return (
            f"{pick.mode.title()} from {dest} back to {origin}: {pick.route}. "
            f"About {pick.travel_time_hours:.1f} h, roughly ₹{pick.estimated_cost_inr:,} (estimate). "
            f"Weigh time vs money against your overall budget (₹{planner_output.budget_inr:,})."
        )
    return (
        f"Plan return from {dest} to {origin}; compare modes for time and cost within your "
        f"budget (₹{planner_output.budget_inr:,}). See transport rationale for tradeoffs."
    )


def _local_getting_around(activity_output: ActivityAgentOutput) -> str:
    guide = (activity_output.local_mobility_guide or "").strip()
    if guide:
        return guide
    return (
        "Within the destination, use app cabs or short-term scooter/bike rentals where common; "
        "cluster stops by neighborhood to limit long cross-town hops."
    )


def _first_day_local_mobility(activity_output: ActivityAgentOutput) -> str:
    text = (activity_output.first_day_local_mobility or "").strip()
    if text:
        return text
    return (
        "From the airport or railway station, use prepaid taxis or app cabs to your hotel; "
        "then use local options (autos, cabs, or rentals) for today's nearby stops."
    )


def _stay_summary_line(stay_output: StayAgentOutput, *, is_return_day: bool) -> str:
    sel = stay_output.selected_stay
    line = f"{sel.name} ({sel.area}) — about ₹{sel.nightly_cost_inr:,}/night"
    pricing = (stay_output.stay_pricing_note or "").strip()
    if pricing:
        line += f". {pricing}"
    if is_return_day:
        ret = (stay_output.return_day_stay_note or "").strip()
        if ret:
            return f"{ret}\n\nMain booking: {line}"
        return (
            f"{line}\n\nIf you depart late or overnight, consider a short stay or lounge near "
            "your station or airport; otherwise align checkout with your return journey."
        )
    return line


def _build_daily_plan(state: TravelGraphState) -> dict[str, DailyItinerary]:
    planner_output = state["planner_output"]
    stay_output = state["stay_output"]
    activity_output = state["activity_output"]

    activity_names = [activity.name for activity in activity_output.activities]
    food_names = activity_output.food_recommendations
    local_mobility = _local_getting_around(activity_output)
    first_day_local = _first_day_local_mobility(activity_output)
    arrival_text = _arrival_summary(state)
    return_text = _return_leg_summary(state)
    n = planner_output.duration_days
    dest = planner_output.destination
    origin_label = planner_output.origin_city or "home"

    daily_plan: dict[str, DailyItinerary] = {}
    for day_index in range(1, n + 1):
        day_key = f"day_{day_index}"
        activity_slice = activity_names[(day_index - 1) :: n] or activity_names[:2]
        food_slice = food_names[(day_index - 1) :: n] or food_names[:2]

        if n == 1:
            phase = TripDayPhase.reaching
            headline = f"Reaching {dest}"
            primary = arrival_text
            ret_snip = (state["transport_output"].return_leg_summary or "").strip()
            if ret_snip:
                primary = f"{primary}\n\nSame-day return / onward: {ret_snip}"
            getting = first_day_local
            stay_s = _stay_summary_line(stay_output, is_return_day=False)
            rd = (stay_output.return_day_stay_note or "").strip()
            if rd:
                stay_s = f"{stay_s}\n{rd}"
        elif day_index == 1:
            phase = TripDayPhase.reaching
            headline = f"Reaching {dest}"
            primary = arrival_text
            getting = first_day_local
            stay_s = _stay_summary_line(stay_output, is_return_day=False)
        elif day_index == n:
            phase = TripDayPhase.return_home
            headline = f"Return to {origin_label}"
            primary = return_text
            getting = ""
            stay_s = _stay_summary_line(stay_output, is_return_day=True)
        else:
            phase = TripDayPhase.explore
            headline = f"Explore {dest}"
            primary = local_mobility
            getting = local_mobility
            stay_s = _stay_summary_line(stay_output, is_return_day=False)

        daily_plan[day_key] = DailyItinerary(
            phase=phase,
            headline=headline,
            primary_transport_summary=primary,
            getting_around=getting,
            stay_summary=stay_s,
            theme=headline,
            stay=stay_s,
            activities=activity_slice,
            food=food_slice,
        )
    return daily_plan


def aggregator_node(state: TravelGraphState) -> TravelGraphState:
    planner_output = state.get("planner_output")
    optimizer_output = state.get("optimizer_output")
    if planner_output is None or optimizer_output is None:
        return {}

    refinement_count = int(state.get("refinement_count", 0))
    retry_target = state.get("retry_target")
    judge_feedback_hints = state.get("judge_feedback_hints", [])
    optimization_notes = list(optimizer_output.optimization_notes)
    if refinement_count > 0:
        optimization_notes.append(f"Refinement loops executed: {refinement_count}.")
    if retry_target:
        optimization_notes.append(f"Last retry target: {retry_target}.")
    optimization_notes.extend(
        [f"Judge feedback hint: {hint}" for hint in judge_feedback_hints[:3]]
    )

    final_itinerary = FinalItinerary(
        destination=planner_output.destination,
        duration_days=planner_output.duration_days,
        arrival_summary=_arrival_summary(state),
        daily_plan=_build_daily_plan(state),
        budget_summary={
            "target_budget_inr": planner_output.budget_inr,
            "optimized_total_cost_inr": optimizer_output.optimized_total_cost_inr,
            "fits_budget": optimizer_output.fits_budget,
            "category_split": optimizer_output.category_split,
            "refinement_applied": refinement_count > 0,
            "refinement_count": refinement_count,
            "last_retry_target": retry_target,
        },
        optimization_notes=optimization_notes,
    )

    return {"final_itinerary": final_itinerary}
