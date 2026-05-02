"""Anthropic-only LLM configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Default when only ANTHROPIC_MODEL is set: specialists use the same model.
# When nothing is set, prefer a small fast default for agents (override via env).
_DEFAULT_FAST = "claude-3-5-haiku-20241022"


def _strip_model(name: str | None) -> str | None:
    if name is None:
        return None
    s = name.strip()
    return s or None


def get_anthropic_llm(*, temperature: float = 0.1) -> ChatAnthropic:
    """Primary chat model (legacy entrypoint; same as agents if AGENTS env unset)."""

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )

    model_name = os.getenv("ANTHROPIC_MODEL", _DEFAULT_FAST)

    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        anthropic_api_key=api_key,
    )


def get_agent_llm(*, temperature: float = 0.1) -> ChatAnthropic:
    """Model for specialist tool-calling agents (transport, stay, activity, optimizer).

    Set ANTHROPIC_MODEL_AGENTS to a faster model (e.g. Haiku) while keeping
    ANTHROPIC_MODEL for other uses. Falls back to ANTHROPIC_MODEL, then Haiku.
    """

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )

    model_name = (
        _strip_model(os.getenv("ANTHROPIC_MODEL_AGENTS"))
        or _strip_model(os.getenv("ANTHROPIC_MODEL"))
        or _DEFAULT_FAST
    )

    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        anthropic_api_key=api_key,
    )


def get_judge_llm(*, temperature: float = 0.0) -> ChatAnthropic:
    """Model for judge structured scoring (often same tier as agents)."""

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )

    model_name = (
        _strip_model(os.getenv("ANTHROPIC_MODEL_JUDGE"))
        or _strip_model(os.getenv("ANTHROPIC_MODEL_AGENTS"))
        or _strip_model(os.getenv("ANTHROPIC_MODEL"))
        or _DEFAULT_FAST
    )

    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        anthropic_api_key=api_key,
    )
