"""Standalone CrewAI runner — invoked as a subprocess so its rich/verbose
output and subprocess machinery cannot interfere with the MCP stdio transport.

Usage:
    python -m crew._run_crew_subprocess <company_name>

Reads OPENAI_API_KEY from backend/.env, runs the crew, prints the JSON result
to stdout, and exits. Anything CrewAI logs to stderr is harmless.
"""

from __future__ import annotations

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

from crew.company_crew import run_crew


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "company_name argument required"}), flush=True)
        sys.exit(2)
    company_name = sys.argv[1]
    result = run_crew(company_name)
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
