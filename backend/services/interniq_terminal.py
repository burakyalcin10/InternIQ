"""Interactive terminal client for using InternIQ through MCP."""

from __future__ import annotations

import asyncio
import getpass
import json
import shlex
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from services.mcp_bridge import _extract_json_from_tool, _server_parameters, _tool_summary

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _read_text_arg(parts: list[str], start_index: int) -> str:
    if len(parts) <= start_index:
        return ""

    first = Path(parts[start_index])
    if first.exists() and first.is_file():
        return first.read_text(encoding="utf-8", errors="ignore")

    return " ".join(parts[start_index:])


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _print_help() -> None:
    print(
        """
InternIQ MCP Terminal
=====================
Commands:
  help
  tools
  login <email>
  profile
  logout
  features
  search <query>
  listing <listing_id>
  company <company_name>
  research <company_name>
  cv <listing_id> <cv_file_path | cv_text>
  cv-profile <listing_id>
  workflow <listing_id> <cv_file_path | cv_text>
  workflow-profile <listing_id>
  interview start <company> <position> [max_questions]
  interview-profile start <company> <position> [max_questions]
  interview answer <session_id> <answer_text>
  call <tool_name> <json_args>
  quit

Examples:
  search python remote
  login deneme@gmail.com
  profile
  listing 1
  cv 1 C:\\Users\\burak\\Desktop\\cv.txt
  cv-profile 1
  workflow 1 "Python C++ embedded systems project"
  workflow-profile 1
  interview start ASELSAN "Software Engineering Intern" 3
  interview-profile start ASELSAN "Software Engineering Intern" 3
  interview answer <session_id> "I built an embedded systems project with C++..."
  call search_internships {"query":"react","limit":3}
""".strip()
    )


def _short_print(tool_name: str, result: dict[str, Any]) -> None:
    if tool_name == "search_internships":
        print(f"Found {result.get('total', 0)} listing(s), showing {result.get('returned', 0)}:")
        for listing in result.get("listings", []):
            print(f"  #{listing.get('id')} {listing.get('position')} @ {listing.get('company')} [{listing.get('type')}]")
        return

    if tool_name == "get_listing_context":
        listing = result.get("listing") or {}
        print(f"#{listing.get('id')} {listing.get('position')} @ {listing.get('company')}")
        print(f"Location: {listing.get('location')} | Type: {listing.get('type')}")
        print(f"Tags: {', '.join(listing.get('tags', []))}")
        print("Requirements:")
        for item in listing.get("requirements", []):
            print(f"  - {item}")
        return

    if tool_name in {"get_company_context", "run_company_research"}:
        company = result.get("company") if tool_name == "get_company_context" else result.get("report", {})
        _print_json(company)
        return

    if tool_name == "analyze_cv_for_listing":
        analysis = result.get("analysis", {})
        print(f"Score: {analysis.get('score')}")
        print(analysis.get("summary", ""))
        if analysis.get("matched_keywords"):
            print(f"Matched: {', '.join(analysis.get('matched_keywords', []))}")
        if analysis.get("missing_keywords"):
            print(f"Missing: {', '.join(analysis.get('missing_keywords', []))}")
        return

    if tool_name == "run_application_workflow":
        print(f"CV Score: {result.get('cv_score')}")
        action_plan = result.get("action_plan", {})
        print(action_plan.get("summary", ""))
        for step in action_plan.get("steps", []):
            print(f"  {step.get('step')}. {step.get('title')}: {step.get('description')}")
        return

    if tool_name == "start_mock_interview":
        print(f"Session: {result.get('session_id')}")
        print(f"Question {result.get('question_number')}/{result.get('total_questions')}: {result.get('question')}")
        return

    if tool_name == "login_user":
        if result.get("authenticated"):
            print(f"Logged in as {result.get('user', {}).get('email')}")
            print(f"Saved CV: {'yes' if result.get('has_profile_cv') else 'no'}")
        else:
            print(f"Login failed: {result.get('error')}")
        return

    if tool_name == "get_current_account":
        if not result.get("authenticated"):
            print(result.get("error", "Not authenticated."))
            return
        profile = result.get("profile", {})
        print(f"Account: {result.get('user', {}).get('email')}")
        print(f"Saved CV: {'yes' if result.get('has_profile_cv') else 'no'}")
        if profile.get("summary"):
            print(f"Summary: {profile.get('summary')}")
        if profile.get("skills"):
            print(f"Skills: {', '.join(profile.get('skills', [])[:10])}")
        return

    if tool_name == "logout_user":
        print("Logged out." if result.get("logged_out") else "No active auth session was found.")
        return

    if tool_name == "answer_mock_interview":
        print(f"Score: {result.get('score')} | Difficulty: {result.get('difficulty')}")
        print(f"Feedback: {result.get('feedback')}")
        if result.get("phase") == "completed":
            print("Interview completed.")
            print(result.get("summary", ""))
        else:
            print(f"Next question {result.get('question_number')}/{result.get('total_questions')}: {result.get('question')}")
        return

    _print_json(result)


async def _call_tool(session: ClientSession, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = await session.call_tool(tool_name, arguments)
    return _extract_json_from_tool(result)


async def _handle_command(session: ClientSession, line: str, state: dict[str, Any]) -> bool:
    try:
        parts = shlex.split(line)
    except ValueError as exc:
        print(f"Parse error: {exc}")
        return True

    if not parts:
        return True

    command = parts[0].lower()
    if command in {"quit", "exit", "q"}:
        return False

    if command == "help":
        _print_help()
        return True

    if command == "tools":
        tools_result = await session.list_tools()
        for tool in tools_result.tools:
            summary = _tool_summary(tool)
            print(f"- {summary['name']}: {summary['description']}")
        return True

    if command == "login" and len(parts) >= 2:
        password = await asyncio.to_thread(getpass.getpass, "Password: ")
        result = await _call_tool(
            session,
            "login_user",
            {"email": parts[1], "password": password},
        )
        if result.get("authenticated"):
            state["auth_session_id"] = result.get("auth_session_id")
        _short_print("login_user", result)
        return True

    if command == "logout":
        auth_session_id = state.get("auth_session_id")
        if not auth_session_id:
            print("No active auth session.")
            return True
        result = await _call_tool(session, "logout_user", {"auth_session_id": auth_session_id})
        state.pop("auth_session_id", None)
        _short_print("logout_user", result)
        return True

    if command == "profile":
        auth_session_id = state.get("auth_session_id")
        if not auth_session_id:
            print("Run login <email> first.")
            return True
        result = await _call_tool(session, "get_current_account", {"auth_session_id": auth_session_id})
        _short_print("get_current_account", result)
        return True

    tool_names = {
        _tool_summary(tool)["name"]
        for tool in (await session.list_tools()).tools
    }

    if command in tool_names:
        raw_arguments = line[len(parts[0]):].strip()
        try:
            arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as exc:
            print(f"JSON argument error: {exc}")
            print(f"Use: {command} {{\"arg_name\":\"value\"}}")
            return True

        result = await _call_tool(session, command, arguments)
        _short_print(command, result)
        return True

    if command == "features":
        result = await _call_tool(session, "list_interniq_features", {})
        _short_print("list_interniq_features", result)
        return True

    if command == "search":
        result = await _call_tool(session, "search_internships", {"query": " ".join(parts[1:]), "limit": 10})
        _short_print("search_internships", result)
        return True

    if command == "listing" and len(parts) >= 2:
        result = await _call_tool(session, "get_listing_context", {"listing_id": int(parts[1])})
        _short_print("get_listing_context", result)
        return True

    if command == "company" and len(parts) >= 2:
        result = await _call_tool(session, "get_company_context", {"company_name": " ".join(parts[1:])})
        _short_print("get_company_context", result)
        return True

    if command == "research" and len(parts) >= 2:
        result = await _call_tool(session, "run_company_research", {"company_name": " ".join(parts[1:])})
        _short_print("run_company_research", result)
        return True

    if command == "cv" and len(parts) >= 3:
        result = await _call_tool(
            session,
            "analyze_cv_for_listing",
            {"listing_id": int(parts[1]), "cv_text": _read_text_arg(parts, 2)},
        )
        _short_print("analyze_cv_for_listing", result)
        return True

    if command == "cv-profile" and len(parts) >= 2:
        auth_session_id = state.get("auth_session_id")
        if not auth_session_id:
            print("Run login <email> first.")
            return True
        result = await _call_tool(
            session,
            "analyze_profile_cv_for_listing",
            {"auth_session_id": auth_session_id, "listing_id": int(parts[1])},
        )
        _short_print("analyze_cv_for_listing", result)
        return True

    if command == "workflow" and len(parts) >= 2:
        result = await _call_tool(
            session,
            "run_application_workflow",
            {"listing_id": int(parts[1]), "cv_text": _read_text_arg(parts, 2)},
        )
        _short_print("run_application_workflow", result)
        return True

    if command == "workflow-profile" and len(parts) >= 2:
        auth_session_id = state.get("auth_session_id")
        if not auth_session_id:
            print("Run login <email> first.")
            return True
        result = await _call_tool(
            session,
            "run_profile_application_workflow",
            {"auth_session_id": auth_session_id, "listing_id": int(parts[1])},
        )
        _short_print("run_application_workflow", result)
        return True

    if command == "interview" and len(parts) >= 2:
        subcommand = parts[1].lower()
        if subcommand == "start" and len(parts) >= 4:
            max_questions = int(parts[4]) if len(parts) >= 5 and parts[4].isdigit() else 3
            result = await _call_tool(
                session,
                "start_mock_interview",
                {
                    "company": parts[2],
                    "position": parts[3],
                    "category": "technical",
                    "max_questions": max_questions,
                },
            )
            _short_print("start_mock_interview", result)
            return True

    if command == "interview-profile" and len(parts) >= 2:
        auth_session_id = state.get("auth_session_id")
        if not auth_session_id:
            print("Run login <email> first.")
            return True

        subcommand = parts[1].lower()
        if subcommand == "start" and len(parts) >= 4:
            max_questions = int(parts[4]) if len(parts) >= 5 and parts[4].isdigit() else 3
            result = await _call_tool(
                session,
                "start_profile_mock_interview",
                {
                    "auth_session_id": auth_session_id,
                    "company": parts[2],
                    "position": parts[3],
                    "category": "technical",
                    "max_questions": max_questions,
                },
            )
            _short_print("start_mock_interview", result)
            return True

        if subcommand == "answer" and len(parts) >= 4:
            result = await _call_tool(
                session,
                "answer_mock_interview",
                {"session_id": parts[2], "answer": " ".join(parts[3:])},
            )
            _short_print("answer_mock_interview", result)
            return True

    if command == "call" and len(parts) >= 2:
        tool_name = parts[1]
        raw_arguments = line.split(parts[1], 1)[1].strip()
        arguments = json.loads(raw_arguments or "{}")
        result = await _call_tool(session, tool_name, arguments)
        _short_print(tool_name, result)
        return True

    print("Unknown or incomplete command. Type 'help' for examples.")
    return True


async def run_terminal() -> None:
    print("Starting InternIQ MCP server over stdio...")
    params = _server_parameters()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            state: dict[str, Any] = {}
            print("Connected. Type 'help' for commands.")
            while True:
                try:
                    line = await asyncio.to_thread(input, "InternIQ> ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                keep_running = await _handle_command(session, line, state)
                if not keep_running:
                    break


def main() -> None:
    asyncio.run(run_terminal())


if __name__ == "__main__":
    main()
