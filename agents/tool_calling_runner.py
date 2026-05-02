"""Helpers for running structured tool-calling agents."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agent.schemas import PlannerOutput
from config.llm import get_agent_llm


def _compact_planner_json(planner_output: PlannerOutput) -> str:
    return planner_output.model_dump_json(exclude_none=True)


def _invoke_tool(tool_map: dict[str, BaseTool], tool_call: dict[str, Any]) -> ToolMessage:
    tool_name = tool_call["name"]
    selected_tool = tool_map.get(tool_name)
    if selected_tool is None:
        return ToolMessage(
            content=json.dumps({"error": f"unknown tool {tool_name}"}),
            tool_call_id=tool_call["id"],
        )
    result = selected_tool.invoke(tool_call.get("args", {}))
    return ToolMessage(
        content=json.dumps(result, ensure_ascii=False),
        tool_call_id=tool_call["id"],
    )


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
    llm = get_agent_llm()
    llm_with_tools = llm.bind_tools(tool_list)

    planner_json = _compact_planner_json(planner_output)
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
                f"Planner output JSON:\n{planner_json}"
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

    tool_calls = list(ai_response.tool_calls or [])
    tool_messages: list[ToolMessage] = []
    if len(tool_calls) <= 1:
        for tc in tool_calls:
            tool_messages.append(_invoke_tool(tool_map, tc))
    else:
        with ThreadPoolExecutor(max_workers=min(8, len(tool_calls))) as pool:
            future_to_pos = {
                pool.submit(_invoke_tool, tool_map, tc): i for i, tc in enumerate(tool_calls)
            }
            indexed: list[tuple[int, ToolMessage]] = []
            for fut in as_completed(future_to_pos):
                pos = future_to_pos[fut]
                indexed.append((pos, fut.result()))
            indexed.sort(key=lambda x: x[0])
            tool_messages = [tm for _, tm in indexed]

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
