"""Standalone LangGraph workflow runner — spawned as a subprocess from the
MCP server so the openai SDK's sync httpx pipeline doesn't hang inside the
MCP stdio child on Windows.

Usage:
    python -m langgraph_workflow._run_workflow_subprocess <listing_id> [cv_text_b64]

Reads OPENAI_API_KEY from backend/.env, runs workflow_graph.invoke, then
prints the JSON result to stdout. Anything written to stderr is discarded
by the parent.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

# Force UTF-8 on stdout/stderr so the parent can decode Turkish characters
# regardless of the Windows console code page (cp1254/cp1252).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env", override=False)
sys.path.insert(0, str(BACKEND_DIR))

from langgraph_workflow.graph import workflow_graph
from services.profile_store import summarize_cv_profile


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "listing_id argument required"}), flush=True)
        sys.exit(2)

    try:
        listing_id = int(sys.argv[1])
    except ValueError:
        print(json.dumps({"status": "error", "error": "listing_id must be int"}), flush=True)
        sys.exit(2)

    cv_text = ""
    if len(sys.argv) >= 3 and sys.argv[2]:
        try:
            cv_text = base64.b64decode(sys.argv[2]).decode("utf-8", errors="replace")
        except Exception:
            cv_text = sys.argv[2]

    candidate_profile = summarize_cv_profile(cv_text or "")
    initial_state = {
        "listing_id": listing_id,
        "cv_text": cv_text or "",
        "candidate_profile": candidate_profile,
        "mcp_context": {},
        "listing_data": {},
        "job_requirements": [],
        "job_description": "",
        "cv_score": 0,
        "cv_analysis": {},
        "needs_improvement": False,
        "cv_suggestions": [],
        "company_name": "",
        "company_info": {},
        "interview_questions": [],
        "interview_sections": {},
        "action_plan": {},
        "status": "fallback",
        "llm_provider": "fallback",
    }

    result = workflow_graph.invoke(initial_state)
    payload = {
        "listing_data": result.get("listing_data", {}),
        "company_name": result.get("company_name", ""),
        "cv_score": result.get("cv_score", 0),
        "cv_analysis": result.get("cv_analysis", {}),
        "cv_suggestions": result.get("cv_suggestions", []),
        "company_info": result.get("company_info", {}),
        "interview_questions": result.get("interview_questions", []),
        "interview_sections": result.get("interview_sections", {}),
        "action_plan": result.get("action_plan", {}),
        "status": result.get("status", "fallback"),
        "llm_provider": result.get("llm_provider", "fallback"),
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
