"""Anthropic-only LLM configuration."""

from __future__ import annotations

import os

from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv


def get_anthropic_llm(*, temperature: float = 0.1) -> ChatAnthropic:
    """Return the shared Anthropic chat model for agent nodes."""

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file."
        )

    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")

    return ChatAnthropic(
        model=model_name,
        temperature=temperature,
        anthropic_api_key=api_key,
    )
