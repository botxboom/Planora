"""CLI runner for the compiled travel graph (invoke once, print JSON state)."""

from __future__ import annotations

import argparse
import json
from typing import Any

from graph.travel_graph import build_travel_graph

DEFAULT_QUERY = "Plan a 4-day trip to Goa under ₹25,000 with good food and minimal travel time"


def _serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    serialized: dict[str, Any] = {}
    for key, value in state.items():
        if hasattr(value, "model_dump"):
            serialized[key] = value.model_dump()
        else:
            serialized[key] = value
    return serialized


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Planora travel graph and print final state as JSON.")
    parser.add_argument("--query", type=str, default=DEFAULT_QUERY)
    parser.add_argument("--user-id", type=str, default=None)
    args = parser.parse_args()

    graph = build_travel_graph()
    initial_state = {"query": args.query, "user_id": args.user_id, "metadata": {}}
    result = graph.invoke(initial_state)

    print(json.dumps(_serialize_state(result), indent=2))


if __name__ == "__main__":
    main()
