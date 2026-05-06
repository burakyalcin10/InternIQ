"""MCP client bridge for the InternIQ classroom demo."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKEND_DIR = Path(__file__).resolve().parents[1]
MCP_MODULE = "mcp_server.interniq_mcp"
LISTINGS_RESOURCE = "interniq://listings"
COMPANIES_RESOURCE = "interniq://companies"
APPLICATION_PROMPT = "application-prep-prompt"


def _trace(step: str, label: str, detail: Any = "", status: str = "ok") -> dict[str, Any]:
    return {
        "step": step,
        "label": label,
        "detail": detail,
        "status": status,
    }


def _model_to_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True)
    if isinstance(value, dict):
        return value
    return {"value": str(value)}


def _content_to_text(content: Any) -> str:
    if hasattr(content, "text"):
        return str(content.text)
    if isinstance(content, dict) and "text" in content:
        return str(content["text"])
    return str(content)


def _extract_json_from_tool(result: Any) -> dict[str, Any]:
    structured = getattr(result, "structuredContent", None)
    if structured is None:
        structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured

    content_items = getattr(result, "content", []) or []
    text = "\n".join(_content_to_text(item) for item in content_items).strip()
    if not text:
        return {}

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"text": text}


def _resource_text(result: Any) -> str:
    contents = getattr(result, "contents", []) or []
    return "\n".join(_content_to_text(item) for item in contents).strip()


def _prompt_text(result: Any) -> str:
    messages = getattr(result, "messages", []) or []
    parts: list[str] = []
    for message in messages:
        content = getattr(message, "content", None)
        if content is not None:
            parts.append(_content_to_text(content))
    return "\n".join(parts).strip()


def _tool_summary(tool: Any) -> dict[str, Any]:
    data = _model_to_dict(tool)
    return {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "input_schema": data.get("inputSchema") or data.get("input_schema") or {},
    }


def _resource_summary(resource: Any) -> dict[str, Any]:
    data = _model_to_dict(resource)
    return {
        "uri": str(data.get("uri", "")),
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "mime_type": data.get("mimeType") or data.get("mime_type", ""),
    }


def _prompt_summary(prompt: Any) -> dict[str, Any]:
    data = _model_to_dict(prompt)
    return {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "arguments": data.get("arguments", []),
    }


def _server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", MCP_MODULE],
        cwd=str(BACKEND_DIR),
    )


async def run_interniq_mcp_demo(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Run the full MCP demo flow and return traceable UI-friendly data."""
    trace: list[dict[str, Any]] = []
    capabilities: dict[str, Any] = {
        "tools": [],
        "resources": [],
        "prompts": [],
    }
    resource_reads: dict[str, Any] = {}
    prompt_payload: dict[str, Any] = {}
    context: dict[str, Any] = {}

    try:
        params = _server_parameters()
        trace.append(
            _trace(
                "connect",
                "Connect over stdio",
                {
                    "command": params.command,
                    "args": params.args,
                    "cwd": str(params.cwd),
                    "transport": "stdio",
                },
            )
        )

        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                initialize_result = await session.initialize()
                trace.append(
                    _trace(
                        "initialize",
                        "Initialize MCP session",
                        {
                            "server": _model_to_dict(getattr(initialize_result, "serverInfo", {})),
                            "protocol_version": getattr(initialize_result, "protocolVersion", ""),
                        },
                    )
                )

                tools_result = await session.list_tools()
                tools = [_tool_summary(tool) for tool in tools_result.tools]
                capabilities["tools"] = tools
                trace.append(
                    _trace(
                        "discover_tools",
                        "Discover Tools",
                        [{"name": tool["name"], "description": tool["description"]} for tool in tools],
                    )
                )

                resources_result = await session.list_resources()
                resources = [_resource_summary(resource) for resource in resources_result.resources]
                capabilities["resources"] = resources
                trace.append(
                    _trace(
                        "discover_resources",
                        "Discover Resources",
                        [{"uri": resource["uri"], "name": resource["name"]} for resource in resources],
                    )
                )

                for resource_uri in (LISTINGS_RESOURCE, COMPANIES_RESOURCE):
                    read_result = await session.read_resource(resource_uri)
                    text = _resource_text(read_result)
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError:
                        parsed = text
                    resource_reads[resource_uri] = {
                        "items": len(parsed) if isinstance(parsed, list) else None,
                        "preview": parsed[:2] if isinstance(parsed, list) else str(parsed)[:500],
                    }

                trace.append(
                    _trace(
                        "read_resources",
                        "Read Resources",
                        resource_reads,
                    )
                )

                prompts_result = await session.list_prompts()
                prompts = [_prompt_summary(prompt) for prompt in prompts_result.prompts]
                capabilities["prompts"] = prompts
                trace.append(
                    _trace(
                        "discover_prompts",
                        "Discover Prompts",
                        [{"name": prompt["name"], "description": prompt["description"]} for prompt in prompts],
                    )
                )

                prompt_result = await session.get_prompt(APPLICATION_PROMPT)
                prompt_payload = {
                    "name": APPLICATION_PROMPT,
                    "text": _prompt_text(prompt_result),
                }
                trace.append(_trace("get_prompt", "Get Prompt", prompt_payload))

                tool_result = await session.call_tool(
                    "build_application_context",
                    {"listing_id": listing_id, "cv_text": cv_text},
                )
                context = _extract_json_from_tool(tool_result)
                trace.append(
                    _trace(
                        "call_tool",
                        "Call Tool: build_application_context",
                        {
                            "listing_id": listing_id,
                            "found": context.get("found"),
                            "company": context.get("company", {}).get("name"),
                            "position": context.get("listing", {}).get("position"),
                        },
                    )
                )

        trace.append(
            _trace(
                "return_context",
                "Return MCP Context",
                {
                    "tools_used": context.get("tools_used", []),
                    "resources_available": context.get("resources_available", []),
                    "prompt_name": context.get("prompt_name", APPLICATION_PROMPT),
                },
            )
        )

        return {
            "mcp_status": "ok" if context.get("found", True) else "fallback",
            "mcp_trace": trace,
            "mcp_context": context,
            "mcp_capabilities": capabilities,
            "mcp_resources": resource_reads,
            "mcp_prompt": prompt_payload,
        }
    except Exception as exc:
        trace.append(_trace("error", "MCP Error", str(exc), "error"))
        return {
            "mcp_status": "error",
            "mcp_trace": trace,
            "mcp_context": context,
            "mcp_capabilities": capabilities,
            "mcp_resources": resource_reads,
            "mcp_prompt": prompt_payload,
            "mcp_error": str(exc),
        }


def run_interniq_mcp_demo_sync(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Synchronous wrapper for terminal demos and non-async callers."""
    return asyncio.run(run_interniq_mcp_demo(listing_id=listing_id, cv_text=cv_text))


def _print_cli_result(result: dict[str, Any]) -> None:
    print("InternIQ MCP Demo")
    print("=================")
    print(f"Status: {result.get('mcp_status')}")
    print()

    for item in result.get("mcp_trace", []):
        print(f"[{item.get('status', 'ok').upper()}] {item.get('label')}")
        detail = item.get("detail")
        if detail:
            print(json.dumps(detail, ensure_ascii=True, indent=2))
        print()

    context = result.get("mcp_context", {})
    if context:
        print("MCP Context")
        print("-----------")
        print(json.dumps(context, ensure_ascii=True, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the InternIQ MCP stdio demo.")
    parser.add_argument("--listing-id", type=int, default=1)
    parser.add_argument("--cv-text", default="")
    args = parser.parse_args()
    _print_cli_result(run_interniq_mcp_demo_sync(args.listing_id, args.cv_text))


if __name__ == "__main__":
    main()
