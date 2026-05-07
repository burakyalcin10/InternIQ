"""InternIQ MCP Server.

This server exposes InternIQ internship and company context through the
Model Context Protocol. It is intentionally read-only for the classroom demo.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=False)

from langgraph_interview.graph import answer_graph, question_graph
from langgraph_workflow.graph import workflow_graph
from routers.cv import get_fallback_analysis
from services.profile_store import get_profile, serialize_profile, summarize_cv_profile
from services.supabase_auth import SUPABASE_CLIENT

logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp.server").setLevel(logging.WARNING)


def _warmup_openai() -> None:
    """Prime httpx/openai inside the stdio subprocess.

    On Windows, the FIRST sync OpenAI request from a freshly-spawned MCP
    subprocess can stall ~3 minutes (httpx + asyncio + piped stdio interaction).
    Subsequent requests through ANY client (langchain_openai, litellm, raw
    openai SDK) are then instant.

    Empirically a raw httpx GET is NOT sufficient to prime the openai SDK's
    own httpx instance — we need to exercise the exact code path the LangGraph
    nodes use. A single tiny ChatOpenAI.invoke() warms langchain_openai →
    openai SDK → httpx all at once.
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_key_here":
        return
    # Step 1 — raw httpx GET to prime DNS/TLS at the OS level.
    try:
        import httpx
        with httpx.Client(timeout=30.0) as client:
            client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
    except Exception:
        pass


import threading as _threading
_threading.Thread(target=_warmup_openai, daemon=True, name="openai-warmup").start()

DATA_DIR = BASE_DIR / "data"
LISTINGS_PATH = DATA_DIR / "listings.json"
COMPANIES_PATH = DATA_DIR / "companies.json"
_INTERVIEW_SESSIONS: dict[str, dict[str, Any]] = {}
_AUTH_SESSIONS: dict[str, dict[str, Any]] = {}

mcp = FastMCP(
    "InternIQ MCP Server",
    instructions=(
        "Provides read-only internship listings, company intelligence, and "
        "application preparation context for InternIQ agents."
    ),
)


def _load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, list) else []


def _load_listings() -> list[dict[str, Any]]:
    return _load_json(LISTINGS_PATH)


def _load_companies() -> list[dict[str, Any]]:
    return _load_json(COMPANIES_PATH)


def _normalize_company_name(value: str) -> str:
    cleaned = (value or "").strip().lower()
    if "(" in cleaned:
        cleaned = cleaned.split("(", 1)[0].strip()
    return " ".join(cleaned.replace("-", " ").split())


def _find_listing(listing_id: int) -> dict[str, Any] | None:
    return next(
        (listing for listing in _load_listings() if listing.get("id") == listing_id),
        None,
    )


def _find_company(company_name: str) -> dict[str, Any] | None:
    normalized_name = _normalize_company_name(company_name)
    return next(
        (
            company
            for company in _load_companies()
            if _normalize_company_name(company.get("name", "")) == normalized_name
        ),
        None,
    )


def _compact_listing(listing: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": listing.get("id"),
        "company": listing.get("company"),
        "position": listing.get("position"),
        "location": listing.get("location"),
        "type": listing.get("type"),
        "tags": listing.get("tags", []),
        "deadline": listing.get("deadline"),
        "match_score": listing.get("match_score"),
        "program_name": listing.get("program_name"),
        "duration": listing.get("duration"),
        "department": listing.get("department"),
        "description": listing.get("description", ""),
        "requirements": listing.get("requirements", []),
        "benefits": listing.get("benefits", []),
        "apply_url": listing.get("apply_url", ""),
        "source": listing.get("source", ""),
    }


def _compact_company(company: dict[str, Any] | None, company_name: str) -> dict[str, Any]:
    if not company:
        return {
            "name": company_name,
            "industry": "Unknown",
            "rating": "N/A",
            "tech_stack": [],
            "culture": "No local company profile was found.",
            "interview_style": "Standard technical and HR interview.",
            "recent_news": "",
        }

    return {
        "id": company.get("id"),
        "name": company.get("name"),
        "industry": company.get("industry"),
        "employees": company.get("employees"),
        "rating": company.get("rating"),
        "tech_stack": company.get("tech_stack", []),
        "culture": company.get("culture", ""),
        "interview_style": company.get("interview_style", ""),
        "recent_news": company.get("recent_news", ""),
    }


@mcp.tool()
def login_user(email: str, password: str) -> dict[str, Any]:
    """Sign in to InternIQ with Supabase email/password for this local MCP session."""
    if SUPABASE_CLIENT is None:
        return {
            "authenticated": False,
            "error": "Supabase is not configured in backend/.env.",
        }

    try:
        response = SUPABASE_CLIENT.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as exc:
        return {
            "authenticated": False,
            "error": str(exc),
        }

    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if not user or not session:
        return {
            "authenticated": False,
            "error": "Login failed.",
        }

    auth_session_id = str(uuid.uuid4())
    user_id = str(getattr(user, "id", ""))
    profile = get_profile(user_id) or {}
    _AUTH_SESSIONS[auth_session_id] = {
        "user_id": user_id,
        "email": getattr(user, "email", email),
        "access_token": getattr(session, "access_token", ""),
        "profile": profile,
    }

    return {
        "authenticated": True,
        "auth_session_id": auth_session_id,
        "user": {
            "id": user_id,
            "email": getattr(user, "email", email),
        },
        "profile": serialize_profile(profile) if profile else {},
        "has_profile_cv": bool(profile.get("cv_text", "").strip()),
        "tools_used": ["login_user"],
    }


@mcp.tool()
def logout_user(auth_session_id: str) -> dict[str, Any]:
    """Clear an InternIQ MCP auth session from memory."""
    existed = auth_session_id in _AUTH_SESSIONS
    _AUTH_SESSIONS.pop(auth_session_id, None)
    return {
        "logged_out": existed,
        "auth_session_id": auth_session_id,
        "tools_used": ["logout_user"],
    }


@mcp.tool()
def get_current_account(auth_session_id: str) -> dict[str, Any]:
    """Return the currently authenticated InternIQ user/profile for an MCP auth session."""
    auth_session = _AUTH_SESSIONS.get(auth_session_id)
    if not auth_session:
        return {
            "authenticated": False,
            "error": "Auth session not found. Run login first.",
        }

    profile = get_profile(auth_session["user_id"]) or auth_session.get("profile", {})
    auth_session["profile"] = profile
    return {
        "authenticated": True,
        "user": {
            "id": auth_session["user_id"],
            "email": auth_session["email"],
        },
        "profile": serialize_profile(profile) if profile else {},
        "has_profile_cv": bool(profile.get("cv_text", "").strip()),
        "tools_used": ["get_current_account"],
    }


def _profile_cv_for_auth(auth_session_id: str) -> tuple[str, dict[str, Any] | None]:
    auth_session = _AUTH_SESSIONS.get(auth_session_id)
    if not auth_session:
        return "", None

    profile = get_profile(auth_session["user_id"]) or auth_session.get("profile", {})
    auth_session["profile"] = profile
    return profile.get("cv_text", ""), profile


@mcp.tool()
def list_interniq_features() -> dict[str, Any]:
    """List InternIQ app features exposed through this MCP server."""
    return {
        "features": [
            {
                "name": "Account",
                "tools": ["login_user", "get_current_account", "logout_user"],
                "description": "Sign in and use the saved profile CV during this local MCP session.",
            },
            {
                "name": "Staj Radar",
                "tools": ["search_internships", "get_listing_context"],
                "description": "Search and inspect internship listings.",
            },
            {
                "name": "Company Intel",
                "tools": ["get_company_context", "run_company_research"],
                "description": "Read company profile, tech stack, culture, and interview style.",
            },
            {
                "name": "CV Tailorer",
                "tools": ["analyze_cv_for_listing", "summarize_cv_profile_tool"],
                "description": "Analyze a CV against a selected internship listing.",
            },
            {
                "name": "Application Workflow",
                "tools": ["build_application_context", "run_application_workflow"],
                "description": "Run the LangGraph preparation flow from the terminal.",
            },
            {
                "name": "Mock Interview",
                "tools": ["start_mock_interview", "answer_mock_interview"],
                "description": "Run a stateful mock interview inside one MCP server session.",
            },
        ],
        "note": "Authentication-only account operations are intentionally not exposed through the public terminal demo.",
    }


@mcp.tool()
def search_internships(query: str = "", limit: int = 5) -> dict[str, Any]:
    """Search InternIQ internship listings by company, position, tags, or location."""
    listings = _load_listings()
    normalized_query = query.strip().lower()

    if normalized_query:
        listings = [
            listing
            for listing in listings
            if normalized_query in str(listing.get("company", "")).lower()
            or normalized_query in str(listing.get("position", "")).lower()
            or normalized_query in str(listing.get("location", "")).lower()
            or any(normalized_query in str(tag).lower() for tag in listing.get("tags", []))
        ]

    capped_limit = max(1, min(limit, 20))
    results = [_compact_listing(listing) for listing in listings[:capped_limit]]
    return {
        "query": query,
        "total": len(listings),
        "returned": len(results),
        "listings": results,
    }


@mcp.tool()
def get_listing_context(listing_id: int) -> dict[str, Any]:
    """Return detailed context for a single InternIQ internship listing."""
    listing = _find_listing(listing_id)
    if not listing:
        return {"found": False, "listing_id": listing_id, "listing": None}

    return {
        "found": True,
        "listing_id": listing_id,
        "listing": _compact_listing(listing),
    }


@mcp.tool()
def get_company_context(company_name: str) -> dict[str, Any]:
    """Return read-only company intelligence for an InternIQ company profile."""
    company = _find_company(company_name)
    return {
        "found": company is not None,
        "company_name": company_name,
        "company": _compact_company(company, company_name),
    }


@mcp.tool()
def run_company_research(company_name: str) -> dict[str, Any]:
    """Return a structured company intelligence report from local InternIQ data."""
    # Local data only in the agent loop — CrewAI is available via the terminal `research` command
    company_result = get_company_context(company_name)
    company = company_result.get("company", {})
    tech_stack = company.get("tech_stack", [])
    return {
        "status": "ok" if company_result.get("found") else "fallback",
        "company": company.get("name", company_name),
        "report": {
            "company_summary": (
                f"{company.get('name', company_name)} operates in {company.get('industry', 'technology')} "
                f"and is relevant for internship preparation."
            ),
            "culture": company.get("culture", ""),
            "tech_stack": tech_stack,
            "interview_tips": [
                f"Review {tech} fundamentals and prepare a project example."
                for tech in tech_stack[:4]
            ] or ["Prepare examples about your projects, teamwork, and learning process."],
            "recent_news": company.get("recent_news", ""),
            "overall_rating": company.get("rating", "N/A"),
            "recommendation": "Use this context before running the application workflow or mock interview.",
        },
    }


def _run_crewai_research_sync(company_name: str) -> dict[str, Any]:
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key or openai_key == "your_openai_key_here":
        return {"status": "error", "error": "OPENAI_API_KEY not set.", "company": company_name}

    # CrewAI is invoked as a subprocess: its verbose/emoji output, alt-process
    # spawning, and litellm/httpx state all interact badly with the MCP stdio
    # transport when run in-process. The subprocess wraps run_crew and prints a
    # single JSON line to stdout. stderr is captured but not parsed.
    import subprocess as _subprocess
    import sys as _sys

    try:
        completed = _subprocess.run(
            [_sys.executable, "-m", "crew._run_crew_subprocess", company_name],
            stdin=_subprocess.DEVNULL,
            stdout=_subprocess.PIPE,
            # stderr discarded: CrewAI emits non-UTF-8 console bytes on Windows
            # which crash text-mode decoding. We only need stdout (the JSON).
            stderr=_subprocess.DEVNULL,
            cwd=str(BASE_DIR),
            timeout=240,
        )
    except _subprocess.TimeoutExpired:
        return {"status": "error", "error": "CrewAI subprocess timed out after 240s.", "company": company_name}
    except Exception as exc:
        return {"status": "error", "error": f"CrewAI subprocess failed: {exc!r}", "company": company_name}

    raw_bytes = completed.stdout or b""
    raw = raw_bytes.decode("utf-8", errors="replace").strip()
    if not raw:
        return {
            "status": "error",
            "error": "CrewAI subprocess produced no output.",
            "company": company_name,
        }
    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "CrewAI subprocess output was not JSON.",
            "raw_tail": raw[-500:],
            "company": company_name,
        }
    return {
        "status": "crewai",
        "company": company_name,
        "report": report,
    }


@mcp.tool()
async def run_crewai_research(company_name: str) -> dict[str, Any]:
    """Run multi-agent CrewAI company research (Culture Researcher → Tech Analyst → Report Writer).
    Takes 1-3 minutes. Use only when a deep, narrative company report is explicitly requested."""
    import anyio.to_thread as _to_thread
    return await _to_thread.run_sync(_run_crewai_research_sync, company_name)


@mcp.tool()
def analyze_cv_for_listing(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Analyze CV text against a selected internship listing from the terminal."""
    listing = _find_listing(listing_id)
    if not listing:
        return {"found": False, "error": "Listing not found", "listing_id": listing_id}

    job_description = "\n".join(
        [
            str(listing.get("position", "")),
            str(listing.get("description", "")),
            "\n".join(str(item) for item in listing.get("requirements", [])),
            " ".join(str(tag) for tag in listing.get("tags", [])),
        ]
    )
    analysis = get_fallback_analysis(cv_text or "", job_description)
    return {
        "found": True,
        "listing": _compact_listing(listing),
        "analysis": analysis,
        "tools_used": ["analyze_cv_for_listing"],
    }


@mcp.tool()
def analyze_profile_cv_for_listing(auth_session_id: str, listing_id: int) -> dict[str, Any]:
    """Analyze the logged-in user's saved CV against a selected listing."""
    cv_text, profile = _profile_cv_for_auth(auth_session_id)
    if profile is None:
        return {"authenticated": False, "error": "Auth session not found. Run login first."}
    if not cv_text.strip():
        return {"authenticated": True, "error": "This account has no saved CV text."}

    result = analyze_cv_for_listing(listing_id, cv_text)
    result["authenticated"] = True
    result["profile_email"] = _AUTH_SESSIONS[auth_session_id]["email"]
    result["tools_used"] = ["analyze_profile_cv_for_listing", "analyze_cv_for_listing"]
    return result


@mcp.tool()
def summarize_cv_profile_tool(cv_text: str) -> dict[str, Any]:
    """Summarize CV text into the profile shape used by InternIQ workflows."""
    return {
        "summary": summarize_cv_profile(cv_text or ""),
        "tools_used": ["summarize_cv_profile_tool"],
    }


@mcp.tool()
def build_application_context(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Build the listing, company, and CV context used before LangGraph preparation."""
    listing = _find_listing(listing_id)
    if not listing:
        return {
            "found": False,
            "listing_id": listing_id,
            "error": "Listing not found",
            "tools_used": ["build_application_context"],
        }

    compact_listing = _compact_listing(listing)
    company = _compact_company(_find_company(str(listing.get("company", ""))), str(listing.get("company", "")))
    requirements = compact_listing.get("requirements", []) + compact_listing.get("tags", [])
    cv_words = [word.strip(".,;:()[]{}").lower() for word in cv_text.split()]
    cv_word_set = {word for word in cv_words if len(word) > 1}
    matched_requirements = [
        requirement
        for requirement in requirements
        if any(part.lower() in cv_word_set for part in str(requirement).replace("/", " ").split())
    ]

    return {
        "found": True,
        "listing": compact_listing,
        "company": company,
        "cv_context": {
            "source": "manual" if cv_text.strip() else "empty",
            "character_count": len(cv_text),
            "word_count": len(cv_words),
            "matched_requirements": matched_requirements[:8],
        },
        "application_context": {
            "position": compact_listing.get("position"),
            "company": compact_listing.get("company"),
            "core_requirements": requirements[:10],
            "company_tech_stack": company.get("tech_stack", []),
            "interview_style": company.get("interview_style"),
            "prompt_hint": (
                "Use this context to evaluate candidate fit, prepare interview questions, "
                "and create an action plan."
            ),
        },
        "tools_used": ["build_application_context"],
        "resources_available": ["interniq://listings", "interniq://companies"],
        "prompt_name": "application-prep-prompt",
    }


@mcp.tool()
async def run_application_workflow(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Run InternIQ's LangGraph application preparation workflow from the terminal."""
    import anyio.to_thread as _to_thread
    return await _to_thread.run_sync(_run_application_workflow_sync, listing_id, cv_text)


def _run_application_workflow_sync(listing_id: int, cv_text: str = "") -> dict[str, Any]:
    """Sync implementation of the LangGraph workflow run.

    The graph is executed in a fresh subprocess. Inside the MCP stdio child
    on Windows, the openai SDK's first sync httpx request stalls indefinitely
    (asyncio + piped stdio interaction). Spawning a clean subprocess avoids
    the issue — same fix as CrewAI uses.
    """
    mcp_context = build_application_context(listing_id, cv_text)
    if not mcp_context.get("found"):
        return mcp_context

    import base64 as _b64
    import subprocess as _subprocess
    import sys as _sys

    cv_arg = _b64.b64encode((cv_text or "").encode("utf-8")).decode("ascii")
    try:
        completed = _subprocess.run(
            [_sys.executable, "-m", "langgraph_workflow._run_workflow_subprocess",
             str(listing_id), cv_arg],
            stdin=_subprocess.DEVNULL,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.DEVNULL,
            cwd=str(BASE_DIR),
            timeout=180,
        )
    except _subprocess.TimeoutExpired:
        return {
            "found": True,
            "status": "error",
            "error": "LangGraph workflow subprocess timed out after 180s.",
            "mcp_context": mcp_context,
        }
    except Exception as exc:
        return {
            "found": True,
            "status": "error",
            "error": f"LangGraph workflow subprocess failed: {exc!r}",
            "mcp_context": mcp_context,
        }

    raw = (completed.stdout or b"").decode("utf-8", errors="replace").strip()
    if not raw:
        return {
            "found": True,
            "status": "error",
            "error": "LangGraph workflow subprocess produced no output.",
            "mcp_context": mcp_context,
        }
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "found": True,
            "status": "error",
            "error": "LangGraph workflow subprocess output was not JSON.",
            "raw_tail": raw[-500:],
            "mcp_context": mcp_context,
        }

    return {
        "found": True,
        "listing": {
            "id": result.get("listing_data", {}).get("id"),
            "position": result.get("listing_data", {}).get("position"),
            "company": result.get("company_name"),
        },
        "cv_score": result.get("cv_score", 0),
        "cv_analysis": result.get("cv_analysis", {}),
        "cv_suggestions": result.get("cv_suggestions", []),
        "company_info": result.get("company_info", {}),
        "interview_questions": result.get("interview_questions", []),
        "interview_sections": result.get("interview_sections", {}),
        "action_plan": result.get("action_plan", {}),
        "status": result.get("status", "fallback"),
        "llm_provider": result.get("llm_provider", "fallback"),
        "mcp_context": mcp_context,
        "tools_used": ["build_application_context", "run_application_workflow"],
    }


@mcp.tool()
async def run_profile_application_workflow(auth_session_id: str, listing_id: int) -> dict[str, Any]:
    """Run the application workflow using the logged-in user's saved CV."""
    import anyio.to_thread as _to_thread
    cv_text, profile = _profile_cv_for_auth(auth_session_id)
    if profile is None:
        return {"authenticated": False, "error": "Auth session not found. Run login first."}
    if not cv_text.strip():
        return {"authenticated": True, "error": "This account has no saved CV text."}

    result = await _to_thread.run_sync(_run_application_workflow_sync, listing_id, cv_text)
    result["authenticated"] = True
    result["profile_email"] = _AUTH_SESSIONS[auth_session_id]["email"]
    result["tools_used"] = ["run_profile_application_workflow", *result.get("tools_used", [])]
    return result


def _start_mock_interview_sync(
    company: str,
    position: str,
    category: str,
    max_questions: int,
    cv_text: str,
) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    target_questions = max(3, min(max_questions, 8))
    candidate_profile = summarize_cv_profile(cv_text or "") if cv_text.strip() else {}

    initial_state = {
        "company": company,
        "position": position,
        "category": category,
        "candidate_profile": candidate_profile,
        "session_seed": session_id[:8],
        "messages": [],
        "asked_questions": [],
        "current_question": "",
        "user_answer": "",
        "question_count": 0,
        "target_questions": target_questions,
        "max_questions": target_questions,
        "question_limit": min(target_questions + 2, 8),
        "scores": [],
        "difficulty": "medium",
        "feedback": "",
        "phase": "start",
        "summary": "",
    }

    result = question_graph.invoke(initial_state)
    _INTERVIEW_SESSIONS[session_id] = result
    return {
        "session_id": session_id,
        "question": result.get("current_question", ""),
        "question_number": result.get("question_count", 1),
        "total_questions": result.get("max_questions", target_questions),
        "difficulty": result.get("difficulty", "medium"),
        "phase": result.get("phase", "questioning"),
        "mode": "langgraph",
        "tools_used": ["start_mock_interview"],
    }


@mcp.tool()
async def start_mock_interview(
    company: str = "Genel",
    position: str = "Yazılım Mühendisi Stajyeri",
    category: str = "technical",
    max_questions: int = 5,
    cv_text: str = "",
) -> dict[str, Any]:
    """Start a stateful LangGraph mock interview session inside the MCP server."""
    import anyio.to_thread as _to_thread
    return await _to_thread.run_sync(
        _start_mock_interview_sync, company, position, category, max_questions, cv_text
    )


@mcp.tool()
async def start_profile_mock_interview(
    auth_session_id: str,
    company: str = "Genel",
    position: str = "Yazılım Mühendisi Stajyeri",
    category: str = "technical",
    max_questions: int = 5,
) -> dict[str, Any]:
    """Start a mock interview using the logged-in user's saved CV profile."""
    import anyio.to_thread as _to_thread
    cv_text, profile = _profile_cv_for_auth(auth_session_id)
    if profile is None:
        return {"authenticated": False, "error": "Auth session not found. Run login first."}

    result = await _to_thread.run_sync(
        _start_mock_interview_sync, company, position, category, max_questions, cv_text or ""
    )
    result["authenticated"] = True
    result["profile_email"] = _AUTH_SESSIONS[auth_session_id]["email"]
    result["tools_used"] = ["start_profile_mock_interview", *result.get("tools_used", [])]
    return result


def _answer_mock_interview_sync(session_id: str, answer: str) -> dict[str, Any]:
    session = _INTERVIEW_SESSIONS.get(session_id)
    if not session:
        return {"error": "Session not found. Start a new interview.", "session_id": session_id}

    session["user_answer"] = answer
    result = answer_graph.invoke(session)
    _INTERVIEW_SESSIONS[session_id] = result

    response = {
        "session_id": session_id,
        "feedback": result.get("feedback", ""),
        "score": result["scores"][-1] if result.get("scores") else 0,
        "difficulty": result.get("difficulty", "medium"),
        "phase": result.get("phase", "questioning"),
        "mode": "langgraph",
        "tools_used": ["answer_mock_interview"],
    }

    if result.get("phase") == "completed":
        response["summary"] = result.get("summary", "")
        response["scores"] = result.get("scores", [])
        response["average_score"] = (
            sum(result["scores"]) / len(result["scores"])
            if result.get("scores")
            else 0
        )
        response["total_questions"] = len(result.get("scores", []))
        del _INTERVIEW_SESSIONS[session_id]
    else:
        response["question"] = result.get("current_question", "")
        response["question_number"] = result.get("question_count", 0)
        response["total_questions"] = result.get("max_questions", 5)

    return response


@mcp.tool()
async def answer_mock_interview(session_id: str, answer: str) -> dict[str, Any]:
    """Submit an answer to a terminal MCP mock interview session."""
    import anyio.to_thread as _to_thread
    return await _to_thread.run_sync(_answer_mock_interview_sync, session_id, answer)


@mcp.resource(
    "interniq://listings",
    name="InternIQ Listings",
    description="Read-only JSON snapshot of InternIQ internship listings.",
    mime_type="application/json",
)
def listings_resource() -> str:
    """Return all internship listings as JSON."""
    return json.dumps(_load_listings(), ensure_ascii=False, indent=2)


@mcp.resource(
    "interniq://companies",
    name="InternIQ Companies",
    description="Read-only JSON snapshot of InternIQ company intelligence.",
    mime_type="application/json",
)
def companies_resource() -> str:
    """Return all company profiles as JSON."""
    return json.dumps(_load_companies(), ensure_ascii=False, indent=2)


@mcp.prompt(
    name="application-prep-prompt",
    description="Prompt template for preparing an internship application with InternIQ context.",
)
def application_prep_prompt(position: str = "Software Engineering Intern", company: str = "Selected company") -> str:
    """Return a reusable prompt template for application preparation."""
    return (
        "You are InternIQ's application preparation assistant.\n"
        f"Prepare the candidate for the {position} role at {company}.\n"
        "Use MCP-provided listing context, company context, and CV context.\n"
        "Explain fit, missing skills, interview preparation, and concrete next steps."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
