"""MCP AI Agent — LLM as MCP host.

The LLM (GPT-4o-mini) connects to the InternIQ MCP server, discovers available
tools, and decides autonomously which tools to call based on the user's query.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

BACKEND_DIR = Path(__file__).resolve().parents[1]
MCP_MODULE = "mcp_server.interniq_mcp"

# Auth-only tools that require an active auth_session_id — not useful for the public agent
_SKIP_TOOLS = {
    "login_user",
    "logout_user",
    "get_current_account",
    "analyze_profile_cv_for_listing",
    "run_profile_application_workflow",
    "start_profile_mock_interview",
}

_SYSTEM_PROMPT = (
    "Sen InternIQ'nun AI asistanısın. "
    "Kullanıcının sorularını yanıtlamak için sana sağlanan MCP araçlarını kullanırsın. "
    "Her zaman Türkçe yanıt ver. "
    "Araç sonuçlarını kullanıcıya açık ve kısa şekilde özetle — ham JSON döndürme. "
    "Birden fazla araç gerekiyorsa sırayla kullan."
)


def _server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", MCP_MODULE],
        cwd=str(BACKEND_DIR),
    )


def _mcp_tool_to_openai(tool: Any) -> dict[str, Any]:
    data = tool.model_dump(mode="json", by_alias=True) if hasattr(tool, "model_dump") else dict(tool)
    return {
        "type": "function",
        "function": {
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "parameters": data.get("inputSchema") or data.get("input_schema") or {
                "type": "object",
                "properties": {},
            },
        },
    }


def _extract_tool_result(result: Any) -> Any:
    structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured

    content_items = getattr(result, "content", []) or []
    text = "\n".join(
        (item.text if hasattr(item, "text") else str(item)) for item in content_items
    ).strip()

    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}


async def run_agent(user_message: str) -> dict[str, Any]:
    """Agentic loop: LLM decides which MCP tools to call, executes them via the
    MCP server over stdio, and synthesizes a final natural-language answer."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        return {
            "status": "error",
            "answer": "OPENAI_API_KEY backend/.env dosyasında tanımlı değil.",
            "tool_calls": [],
            "tools_available": [],
        }

    client = AsyncOpenAI(api_key=openai_key)
    tool_calls_log: list[dict[str, Any]] = []

    async with stdio_client(_server_parameters()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            mcp_tools = [t for t in tools_result.tools if getattr(t, "name", "") not in _SKIP_TOOLS]
            openai_tools = [_mcp_tool_to_openai(t) for t in mcp_tools]
            tools_available = [t["function"]["name"] for t in openai_tools]

            messages: list[dict[str, Any]] = [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]

            for _ in range(6):
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )

                choice = response.choices[0]
                assistant = choice.message

                # Append assistant turn to message history
                assistant_dict: dict[str, Any] = {"role": "assistant", "content": assistant.content}
                if assistant.tool_calls:
                    assistant_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in assistant.tool_calls
                    ]
                messages.append(assistant_dict)

                if choice.finish_reason == "stop" or not assistant.tool_calls:
                    return {
                        "status": "ok",
                        "answer": assistant.content or "",
                        "tool_calls": tool_calls_log,
                        "tools_available": tools_available,
                    }

                # Execute each tool call via MCP server
                tool_result_messages: list[dict[str, Any]] = []
                for tc in assistant.tool_calls:
                    tool_name = tc.function.name
                    try:
                        tool_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    try:
                        mcp_result = await session.call_tool(tool_name, tool_args)
                        result_data = _extract_tool_result(mcp_result)
                    except Exception as exc:
                        result_data = {"error": str(exc)}

                    tool_calls_log.append({"tool": tool_name, "args": tool_args, "result": result_data})
                    tool_result_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result_data, ensure_ascii=False),
                    })

                messages.extend(tool_result_messages)

    return {
        "status": "ok",
        "answer": "Yanıt oluşturulurken çok fazla adım gerekti. Lütfen soruyu daha kısa tutun.",
        "tool_calls": tool_calls_log,
        "tools_available": tools_available,
    }
