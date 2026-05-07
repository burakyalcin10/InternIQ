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
    "Birden fazla araç gerekiyorsa sırayla kullan.\n\n"
    "Araç seçim rehberi:\n"
    "- 'mülakata hazırla', 'başvuru hazırla', 'hazırlık yap' → run_application_workflow kullan (CV analizi + şirket araştırması + aksiyon planı, 30-60 sn)\n"
    "- 'mülakat sorusu sor', 'simüle et', 'soru sor' → start_mock_interview kullan (interaktif soru-cevap)\n"
    "- Şirket hakkında hızlı bilgi → get_company_context veya run_company_research\n"
    "- 'detaylı şirket raporu', 'derinlemesine araştır', 'CrewAI çalıştır' → run_crewai_research (1-3 dakika sürer, sadece açıkça istenirse)\n"
    "- run_application_workflow için listing_id gerekir; önce search_internships ile ilgili ilanı bul."
)


def _build_system_prompt(user_profile: dict | None) -> str:
    if not user_profile:
        return _SYSTEM_PROMPT

    cv_text = (user_profile.get("cv_text") or "")[:4000]
    skills = ", ".join(user_profile.get("skills") or [])
    lines = [
        _SYSTEM_PROMPT,
        "",
        "KULLANICI PROFİLİ MEVCUT:",
        f"E-posta: {user_profile.get('email', '')}",
        f"Özet: {user_profile.get('summary', '')}",
        f"Beceriler: {skills}",
        f"Deneyim: {user_profile.get('experience_level', '')}",
    ]
    if cv_text:
        lines += [
            "",
            "CV metni (run_application_workflow veya analyze_cv_for_listing çağırırken "
            "cv_text parametresine aşağıdaki metni ver):",
            cv_text,
        ]
    return "\n".join(lines)


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


_HEAVY_DROP_FIELDS = {"mcp_context", "cv_analysis", "interview_sections", "tools_used", "llm_provider"}
_MAX_CONTENT_CHARS = 2500


def _trim_tool_result(tool_name: str, result_data: Any) -> str:
    """Trim large tool results before adding to LLM message history."""
    if isinstance(result_data, dict):
        trimmed = {k: v for k, v in result_data.items() if k not in _HEAVY_DROP_FIELDS}
        # Further truncate cv_suggestions list
        if "cv_suggestions" in trimmed and isinstance(trimmed["cv_suggestions"], list):
            trimmed["cv_suggestions"] = trimmed["cv_suggestions"][:3]
        if "interview_questions" in trimmed and isinstance(trimmed["interview_questions"], list):
            trimmed["interview_questions"] = trimmed["interview_questions"][:4]
        content = json.dumps(trimmed, ensure_ascii=False)
    else:
        content = json.dumps(result_data, ensure_ascii=False)
    return content[:_MAX_CONTENT_CHARS]


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


async def run_agent(user_message: str, user_profile: dict | None = None) -> dict[str, Any]:
    """Agentic loop with 90-second timeout."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        return {
            "status": "error",
            "answer": "OPENAI_API_KEY is not set in backend/.env.",
            "tool_calls": [],
            "tools_available": [],
        }
    try:
        return await asyncio.wait_for(
            _agent_loop(user_message, user_profile, openai_key),
            timeout=180.0,
        )
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "answer": "Request timed out after 180s. The workflow may be under heavy load — try again.",
            "tool_calls": [],
            "tools_available": [],
        }


async def run_llm_loop(
    user_message: str,
    user_profile: dict | None,
    openai_key: str,
    session: ClientSession,
) -> dict[str, Any]:
    """LLM decision loop over an existing MCP ClientSession (no subprocess spawn)."""
    client = AsyncOpenAI(api_key=openai_key)
    tool_calls_log: list[dict[str, Any]] = []

    tools_result = await session.list_tools()
    mcp_tools = [t for t in tools_result.tools if getattr(t, "name", "") not in _SKIP_TOOLS]
    openai_tools = [_mcp_tool_to_openai(t) for t in mcp_tools]
    tools_available = [t["function"]["name"] for t in openai_tools]

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _build_system_prompt(user_profile)},
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
                "content": _trim_tool_result(tool_name, result_data),
            })

        messages.extend(tool_result_messages)

    return {
        "status": "ok",
        "answer": "Too many steps required to generate a response. Please simplify your query.",
        "tool_calls": tool_calls_log,
        "tools_available": tools_available,
    }


async def _agent_loop(
    user_message: str, user_profile: dict | None, openai_key: str
) -> dict[str, Any]:
    """Spawns its own MCP subprocess — used by the HTTP API endpoint."""
    async with stdio_client(_server_parameters()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await run_llm_loop(user_message, user_profile, openai_key, session)
