"""Reusable LangChain tools for travel planning."""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from langchain_core.tools import tool

from config.settings import get_settings

_web_search_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_web_search_lock = threading.Lock()

_PLACE_DB: dict[str, list[dict[str, Any]]] = {
    "goa food": [
        {"name": "Mum's Kitchen", "category": "food", "area": "Panjim"},
        {"name": "Gunpowder", "category": "food", "area": "Assagao"},
        {"name": "Vinayak Family Restaurant", "category": "food", "area": "Assagao"},
    ],
    "goa activities": [
        {"name": "Baga Beach", "category": "beach", "area": "North Goa"},
        {"name": "Dudhsagar Falls", "category": "nature", "area": "Sanguem"},
        {"name": "Fontainhas Walk", "category": "heritage", "area": "Panjim"},
    ],
}

_HOTEL_DB: dict[str, list[dict[str, Any]]] = {
    "goa": [
        {"name": "Zostel Goa", "area": "Anjuna", "price_per_night_inr": 1200},
        {"name": "Treebo Trend Green Park", "area": "Mapusa", "price_per_night_inr": 2200},
        {"name": "FabHotel Prime", "area": "Calangute", "price_per_night_inr": 2800},
        {"name": "BloomSuites", "area": "Calangute", "price_per_night_inr": 4200},
    ]
}

_DISTANCE_DB: dict[tuple[str, str], dict[str, float]] = {
    ("mumbai", "goa"): {"distance_km": 590, "hours_by_train": 10, "hours_by_flight": 1.3},
    ("delhi", "goa"): {"distance_km": 1870, "hours_by_train": 28, "hours_by_flight": 2.7},
    ("bangalore", "goa"): {"distance_km": 560, "hours_by_train": 12, "hours_by_flight": 1.2},
}


def _normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


@tool
def search_places(query: str) -> list[dict[str, Any]]:
    """Search attractions or food options by free-text query."""

    normalized = _normalize(query)
    if "food" in normalized:
        return _PLACE_DB.get("goa food", [])
    if "activity" in normalized or "things to do" in normalized:
        return _PLACE_DB.get("goa activities", [])

    combined = _PLACE_DB.get("goa food", []) + _PLACE_DB.get("goa activities", [])
    return combined[:4]


@tool
def get_distance(source: str, destination: str) -> dict[str, float]:
    """Return rough distance and travel duration estimates between two cities."""

    key = (_normalize(source), _normalize(destination))
    reverse_key = (_normalize(destination), _normalize(source))

    if key in _DISTANCE_DB:
        return _DISTANCE_DB[key]
    if reverse_key in _DISTANCE_DB:
        return _DISTANCE_DB[reverse_key]

    return {"distance_km": 750.0, "hours_by_train": 14.0, "hours_by_flight": 1.8}


@tool
def estimate_costs(data: dict[str, Any]) -> dict[str, Any]:
    """Estimate cost totals from partial numeric travel cost data."""

    numeric_values: dict[str, float] = {}
    for key, value in data.items():
        if isinstance(value, (int, float)):
            numeric_values[key] = float(value)
    total = int(sum(numeric_values.values()))

    return {
        "line_items": numeric_values,
        "estimated_total_inr": total,
    }


def _web_search_cache_key(query: str) -> str:
    return query.strip().lower()[:512]


@tool
def web_search_travel(query: str) -> dict[str, Any]:
    """Search the web for travel facts (local transport, routes, realistic tips).

    Prefer this when the destination's on-the-ground transport or venue details are uncertain.
    Returns short snippets with URLs when `TAVILY_API_KEY` is set; otherwise a clear disabled notice.
    """

    settings = get_settings()
    if settings.skip_web_search:
        return {
            "ok": False,
            "query": query,
            "skipped": True,
            "message": (
                "Web search disabled via PLANORA_SKIP_WEB_SEARCH. "
                "Use search_places, get_distance, and conservative estimates."
            ),
        }

    ttl = int(settings.web_search_cache_ttl_seconds)
    cache_key = _web_search_cache_key(query)
    if ttl > 0:
        now = time.monotonic()
        with _web_search_lock:
            hit = _web_search_cache.get(cache_key)
        if hit is not None:
            ts, payload = hit
            if now - ts < ttl:
                merged = dict(payload)
                merged["cached"] = True
                return merged

    api_key = os.environ.get("TAVILY_API_KEY", "").strip()
    if not api_key:
        return {
            "ok": False,
            "query": query,
            "message": (
                "Web search is not configured. Set TAVILY_API_KEY in the server environment "
                "for grounded snippets; until then use search_places/get_distance and conservative estimates."
            ),
        }

    payload = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 5,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "query": query, "error": f"HTTP {exc.code}: {exc.reason}"}
    except OSError as exc:
        return {"ok": False, "query": query, "error": str(exc)}

    snippets: list[dict[str, str]] = []
    for row in data.get("results", [])[:5]:
        snippets.append(
            {
                "title": str(row.get("title") or ""),
                "url": str(row.get("url") or ""),
                "content": str(row.get("content") or "")[:700],
            }
        )
    out: dict[str, Any] = {"ok": True, "query": query, "answer": data.get("answer"), "results": snippets}
    if ttl > 0:
        with _web_search_lock:
            _web_search_cache[cache_key] = (time.monotonic(), dict(out))
    return out


@tool
def get_hotels(location: str, nightly_budget_inr: int) -> list[dict[str, Any]]:
    """Return accommodation options filtered by nightly budget."""

    hotels = _HOTEL_DB.get(_normalize(location), [])
    filtered = [
        hotel for hotel in hotels if hotel["price_per_night_inr"] <= nightly_budget_inr
    ]
    return filtered[:5] if filtered else hotels[:3]
