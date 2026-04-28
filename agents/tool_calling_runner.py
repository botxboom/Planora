"""Helpers for running structured tool-calling agents."""

from __future__ import annotations

import json
from typing import Any, Iterable

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agent.schemas import PlannerOutput
from config.llm import get_anthropic_llm


def run_structured_tool_calling_agent(
    *,
    agent_name: str,
    planner_output: PlannerOutput,
    instruction: str,
    tools: Iterable[BaseTool],
    output_model: type[BaseModel],
) -> BaseModel:
    """Run a tool-calling flow and return validated structured output."""

    tool_list = list(tools)
    tool_map = {tool.name: tool for tool in tool_list}
    llm = get_anthropic_llm()
    llm_with_tools = llm.bind_tools(tool_list)

    messages: list[Any] = [
        SystemMessage(
            content=(
                f"You are {agent_name} for a travel planning system.\n"
                "You must call at least one tool before finalizing your answer.\n"
                "Focus on constraints from planner output and keep estimates realistic."
            )
        ),
        HumanMessage(
            content=(
                f"{instruction}\n\n"
                f"Planner output JSON:\n{planner_output.model_dump_json(indent=2)}"
            )
        ),
    ]

    ai_response = llm_with_tools.invoke(messages)
    if not ai_response.tool_calls:
        ai_response = llm_with_tools.invoke(
            messages
            + [
                ai_response,
                HumanMessage(content="Call at least one tool before continuing."),
            ]
        )

    tool_messages: list[ToolMessage] = []
    for tool_call in ai_response.tool_calls:
        tool_name = tool_call["name"]
        selected_tool = tool_map.get(tool_name)
        if selected_tool is None:
            continue
        result = selected_tool.invoke(tool_call.get("args", {}))
        tool_messages.append(
            ToolMessage(
                content=json.dumps(result, ensure_ascii=False),
                tool_call_id=tool_call["id"],
            )
        )

    structured_llm = llm.with_structured_output(output_model)
    return structured_llm.invoke(
        messages
        + [
            ai_response,
            *tool_messages,
            HumanMessage(
                content=(
                    "Use the tool outputs and return the final structured response. "
                    "Do not include extra text."
                )
            ),
        ]
    )
