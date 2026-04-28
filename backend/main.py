"""FastAPI layer for planning, feedback, and memory APIs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent.schemas import FeedbackRequest, RetryRequest, UserRequest
from config.settings import get_settings
from feedback.service import record_feedback_and_update_memory
from feedback.store import get_feedback_events, get_planning_run, save_planning_run
from graph.travel_graph import build_travel_graph
from memory.store import get_user_preferences

app = FastAPI(title="Planora API", version="0.1.0")
settings = get_settings()
graph = build_travel_graph()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RETRY_STRATEGIES = {
    "auto",
    "transport_agent",
    "stay_agent",
    "activity_agent",
    "optimizer_agent",
}


def _serialize_payload(payload: dict) -> dict:
    serialized: dict = {}
    for key, value in payload.items():
        if hasattr(value, "model_dump"):
            serialized[key] = value.model_dump()
        else:
            serialized[key] = value
    return serialized


def _current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_judge_score(serialized_payload: dict[str, Any]) -> int | None:
    judge_output = serialized_payload.get("judge_output")
    if isinstance(judge_output, dict):
        score = judge_output.get("score")
        if isinstance(score, int):
            return score
    return None


def _persist_plan_run(
    *,
    run_id: str,
    user_id: str | None,
    query: str,
    serialized_payload: dict[str, Any],
) -> None:
    save_planning_run(
        run_id=run_id,
        user_id=user_id,
        query=query,
        plan_payload=serialized_payload,
        judge_score=_extract_judge_score(serialized_payload),
    )


def _invoke_plan(
    *,
    query: str,
    user_id: str | None,
    run_id: str,
    metadata: dict[str, Any] | None = None,
    extra_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    initial_state: dict[str, Any] = {
        "query": query,
        "user_id": user_id,
        "metadata": {
            "source": "api",
            "run_id": run_id,
            **(metadata or {}),
        },
    }
    if extra_state:
        initial_state.update(extra_state)

    result = graph.invoke(initial_state)
    serialized = _serialize_payload(result)
    serialized.setdefault("metadata", {})
    serialized["metadata"]["run_id"] = run_id
    if metadata:
        serialized["metadata"].update(metadata)

    _persist_plan_run(
        run_id=run_id,
        user_id=user_id,
        query=query,
        serialized_payload=serialized,
    )
    return serialized


def _sse_frame(event: str, payload: dict[str, Any]) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    )


def _map_node_to_event(node_name: str) -> str:
    mapping = {
        "planner": "planner_completed",
        "transport_agent": "agent_completed",
        "stay_agent": "agent_completed",
        "activity_agent": "agent_completed",
        "optimizer_agent": "agent_completed",
        "judge": "judge_completed",
        "feedback": "retry_triggered",
        "aggregator": "aggregator_completed",
    }
    return mapping.get(node_name, "node_completed")


def _plan_stream_generator(
    *,
    query: str,
    user_id: str | None,
    run_id: str,
    metadata: dict[str, Any] | None = None,
    extra_state: dict[str, Any] | None = None,
) -> Iterable[str]:
    accumulated_state: dict[str, Any] = {
        "query": query,
        "user_id": user_id,
        "metadata": {"source": "api-stream", "run_id": run_id, **(metadata or {})},
    }
    if extra_state:
        accumulated_state.update(extra_state)

    yield _sse_frame(
        "run_started",
        {"run_id": run_id, "timestamp": _current_iso_timestamp()},
    )
    try:
        for chunk in graph.stream(accumulated_state, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                if isinstance(node_output, dict):
                    accumulated_state.update(node_output)
                    serialized_node_output = _serialize_payload(node_output)
                else:
                    serialized_node_output = {"value": node_output}

                yield _sse_frame(
                    _map_node_to_event(node_name),
                    {
                        "run_id": run_id,
                        "timestamp": _current_iso_timestamp(),
                        "node": node_name,
                        "payload": serialized_node_output,
                    },
                )

        serialized_final = _serialize_payload(accumulated_state)
        serialized_final.setdefault("metadata", {})
        serialized_final["metadata"]["run_id"] = run_id
        if metadata:
            serialized_final["metadata"].update(metadata)
        _persist_plan_run(
            run_id=run_id,
            user_id=user_id,
            query=query,
            serialized_payload=serialized_final,
        )

        yield _sse_frame(
            "final_result",
            {
                "run_id": run_id,
                "timestamp": _current_iso_timestamp(),
                "result": serialized_final,
            },
        )
    except Exception as exc:  # pragma: no cover - defensive stream fallback
        yield _sse_frame(
            "error",
            {
                "run_id": run_id,
                "timestamp": _current_iso_timestamp(),
                "message": str(exc),
            },
        )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.post("/plan")
def create_plan(request: UserRequest) -> dict:
    run_id = str(uuid4())
    return _invoke_plan(
        query=request.query,
        user_id=request.user_id,
        run_id=run_id,
    )


@app.post("/plan/stream")
def create_plan_stream(request: UserRequest) -> StreamingResponse:
    run_id = str(uuid4())
    generator = _plan_stream_generator(
        query=request.query,
        user_id=request.user_id,
        run_id=run_id,
    )
    return StreamingResponse(generator, media_type="text/event-stream")


@app.post("/plan/retry")
def retry_plan(request: RetryRequest) -> dict:
    if request.strategy not in RETRY_STRATEGIES:
        raise HTTPException(status_code=400, detail="Invalid retry strategy")

    previous_run = get_planning_run(request.run_id)
    if previous_run is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    strategy = request.strategy
    run_id = str(uuid4())
    query = request.query_override or previous_run["query"]
    user_id = request.user_id or previous_run.get("user_id")

    previous_plan = previous_run.get("plan", {})
    judge_output = previous_plan.get("judge_output", {})
    hints: list[str] = []
    if isinstance(judge_output, dict):
        hints.extend(judge_output.get("issues", [])[:3])
        hints.extend(judge_output.get("improved_suggestions", [])[:3])

    extra_state: dict[str, Any] = {
        "judge_feedback_hints": hints,
    }
    if strategy != "auto":
        extra_state["retry_target"] = strategy

    return _invoke_plan(
        query=query,
        user_id=user_id,
        run_id=run_id,
        metadata={
            "source": "api-retry",
            "parent_run_id": request.run_id,
            "retry_strategy": strategy,
        },
        extra_state=extra_state,
    )


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest) -> dict:
    run = get_planning_run(request.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    result = record_feedback_and_update_memory(
        run_id=request.run_id,
        user_feedback=request.user_feedback,
        comment=request.comment,
        user_id=request.user_id,
    )
    return {"status": "recorded", **result}


@app.get("/feedback/{run_id}")
def get_feedback_for_run(run_id: str) -> dict:
    run = get_planning_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_id not found")
    events = get_feedback_events(run_id)
    return {"run": run, "feedback_events": events}


@app.get("/memory/{user_id}")
def get_memory(user_id: str) -> dict:
    profile = get_user_preferences(user_id)
    return {"user_id": user_id, "profile": profile.model_dump() if profile else None}
