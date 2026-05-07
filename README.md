# InternIQ — AI-Powered Internship Platform

AI-powered internship search and preparation platform. Built incrementally over four assignments — each layered a new AI capability (OpenAI SDK, CrewAI, LangGraph, MCP) onto the same product.

## ⚡ Quick Start

> Prerequisites: **Node.js 18+**, **Python 3.11** (CrewAI does not work on 3.14+), Git.

### 1. Clone the repo
```bash
git clone https://github.com/burakyalcin10/InternIQ.git
cd InternIQ
```

### 2. Backend (terminal 1)
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

# Open .env and fill in at least OPENAI_API_KEY (others optional — see below)

uvicorn main:app --reload       # http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### 3. Frontend (terminal 2 — keep terminal 1 running)
```bash
# from the repo root
npm install
npm run dev                     # http://localhost:5173
```

> Frontend config: copy `.env.example` to `.env` at the repo root and set `VITE_API_URL=http://localhost:8000/api/v1` (default already correct), plus optional Supabase keys for auth.
>
> ⚠️ If a `.env.local` exists at the repo root, Vite loads it **after** `.env` and its values win. If listings fail to load with a network error, the most common cause is a stale `VITE_API_URL` in `.env.local` pointing to a different port than the one uvicorn is bound to.

### 4. (Optional) MCP Terminal Client
After step 2, the `interniqmcp` console script becomes available inside the backend venv:
```bash
# in backend/ with .venv active
interniqmcp
InternIQ> tools                  # list 17 tools
InternIQ> login user@example.com
InternIQ> prepare 1              # uses saved CV when logged in
```

The MCP terminal spawns the MCP server itself over stdio — it does **not** need the FastAPI server (uvicorn) to be running.

### Minimum keys needed for full functionality

| Feature | Key | What breaks without it |
|---|---|---|
| Workflow / Interview / MCP Agent | `OPENAI_API_KEY` | Falls back to canned demo responses |
| CV Tailorer (Gemini) | `GEMINI_API_KEY` | Falls back to keyword-based analysis |
| Auth + saved CV | `SUPABASE_URL` + `SUPABASE_KEY` | Auth endpoints disabled — anonymous demo only |
| LangSmith tracing | `LANGSMITH_*` (3 vars) | Tracing silently disabled |

Without any keys the app still runs end-to-end on fallback data — useful for quick UI demos.

---

## 🚀 About the Project

InternIQ automates the end-to-end internship application process for university students. It exposes its features both as a regular web app and as an **MCP server**, so any LLM can drive the platform autonomously.

| Module | Powered by | What it does |
|---|---|---|
| **🔍 Staj Radar** | Static aggregation + filters | Surfaces internship listings from multiple sources |
| **📄 CV Tailorer** | Google Gemini | PDF CV analysis with ATS-style scoring & suggestions |
| **🏢 Company Intel** | CrewAI (3 sequential agents) | Culture + tech stack + interview report |
| **🎤 Mock Interview** | LangGraph (2 graphs) | Stateful, adaptive-difficulty interview simulation |
| **🛠️ Application Workflow** | LangGraph (7-node graph) | End-to-end preparation pipeline for a chosen listing |
| **🤖 MCP Server + AI Agent** | MCP / FastMCP | 17 tools exposed over stdio + LLM-as-MCP-host chat |

## 🛠️ Tech Stack

### Frontend
- **React 18** + **Vite** + **React Router v7** — SPA with client-side routing
- **Framer Motion** — Animations and micro-interactions
- **Lucide React** — Icon set
- **Custom CSS Design System** — Brutalist-modern dark theme (amber accent, solid cards, no glassmorphism)
- **Custom SVG logomark** — `src/components/Logo.jsx` (5-square matrix mark)

### Backend
- **FastAPI** (Python 3.11) — REST API with automatic OpenAPI docs
- **Uvicorn** — ASGI server
- **FastMCP** — MCP server runtime (stdio transport)
- **Supabase** — Auth + PostgreSQL database

### AI Integrations
- **OpenAI GPT-4o-mini** — LLM backbone for CrewAI agents, LangGraph nodes, MCP host agent
- **Google Gemini** — PDF CV analysis and ATS scoring
- **CrewAI** — Multi-agent company research (Culture Researcher → Tech Analyst → Report Writer)
- **LangGraph** — Stateful workflow orchestration (Application Workflow + Mock Interview)
- **MCP (Model Context Protocol)** — Standard protocol layer over the platform's features
- **LangSmith** — Tracing and observability for LangGraph runs

## 🤖 CrewAI Architecture (Company Intel)

3-agent crew with sequential processing:

```
User selects company → POST /api/v1/crew/research
                              │
                              ▼
                  ┌─────────────────────┐
                  │  Culture Researcher │  → work culture, intern experiences
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │   Tech Analyst      │  → tech stack, interview process
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │   Report Writer     │  → structured JSON report
                  └──────────┬──────────┘
                             ▼
                    Final Intelligence Report
```

- **Config files**: `backend/crew/config/agents.yaml` & `tasks.yaml`
- **Kickoff code**: `backend/crew/company_crew.py` → `run_crew()`
- **Fallback**: Pre-built reports for ASELSAN, BAYKAR when API keys are unavailable
- **Subprocess isolation**: When invoked via MCP, the crew runs in a clean Python subprocess (`backend/crew/_run_crew_subprocess.py`) so its verbose output cannot corrupt MCP JSON-RPC frames

## 🔀 LangGraph Architecture

### 1. Application Preparation Workflow (`POST /api/v1/workflow/prepare`)

A 7-node StateGraph that orchestrates the entire application preparation process:

```
START → analyze_listing → evaluate_cv → [check_cv_score]
                                          ├── score < 70 → suggest_improvements ─┐
                                          └── score ≥ 70 ──────────────────────────┤
                                                                                    ▼
                                                                          research_company
                                                                                    │
                                                                                    ▼
                                                                      generate_interview_prep
                                                                                    │
                                                                                    ▼
                                                                          create_action_plan
                                                                                    │
                                                                                    ▼
                                                                                   END
```

- **Conditional Edge**: If CV score < 70, routes through `suggest_improvements` first — token savings on strong CVs
- **Action plan prompt**: 5 fixed categories (Technical Gap / Portfolio / Company Prep / Interview Practice / Application Strategy), no duplicate steps, company name required in at least 2 steps
- **Subprocess isolation**: When invoked via MCP, runs in `backend/langgraph_workflow/_run_workflow_subprocess.py`

### 2. AI Mock Interview (`POST /api/v1/interview/lg/*`)

Two compiled StateGraphs for stateful interview sessions:

**Question Graph** (start):
```
START → generate_question → END
```

**Answer Graph** (per-answer):
```
START → evaluate_answer → adjust_difficulty → [check_progress]
                                                ├── continue → generate_question → END
                                                └── done     → generate_summary  → END
```

- **Adaptive Difficulty**: Adjusts based on rolling score average
- **In-memory session store**: `_sessions[session_id]` in `routers/interview.py`
- **5 nodes**: `generate_question`, `evaluate_answer`, `adjust_difficulty`, `check_progress` (router), `generate_summary`

## 🔌 MCP Architecture

InternIQ exposes its features as a Model Context Protocol server — any LLM (Claude, GPT, etc.) can drive the platform via tool calling.

```
┌──────────────────────────────────────────────────────────┐
│  Frontend /ajan      Terminal: interniqmcp                │
│         ↓                       ↓                         │
│  POST /agent/chat      direct stdio spawn                 │
│         ↓                                                 │
│  mcp_agent.py  (LLM-as-MCP-host — GPT-4o-mini)            │
│      • discover tools via MCP protocol                    │
│      • loop: LLM picks tool → call → feed result back     │
│      • max 6 iterations                                   │
│         ↓ stdio                                           │
│  interniq_mcp.py  (FastMCP server)                        │
│      • 17 tools / 2 resources / 1 prompt                  │
│      • heavy tools (CrewAI, LangGraph) → subprocess       │
└──────────────────────────────────────────────────────────┘
```

### What's exposed (17 tools)

| Category | Tools |
|---|---|
| Discovery | `list_interniq_features`, `search_internships`, `get_listing_context`, `get_company_context` |
| Auth | `register_user`, `login_user`, `logout_user`, `get_current_account` |
| CV | `analyze_cv_for_listing`, `analyze_profile_cv_for_listing` |
| Workflow | `run_application_workflow`, `run_profile_application_workflow` |
| Interview | `start_mock_interview`, `start_profile_mock_interview`, `answer_mock_interview` |
| Research | `run_company_research` (local), `run_crewai_research` (CrewAI subprocess) |

### Three ways to use it

```bash
# 1. Browser — /ajan page
open http://localhost:5173/ajan

# 2. Terminal client (no FastAPI required)
interniqmcp
InternIQ> tools                  # list 17 tools
InternIQ> login user@example.com
InternIQ> prepare 1              # auto-uses saved CV when logged in

# 3. Programmatic — POST /api/v1/agent/chat
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Python remote stajı bul"}'
```

### Why subprocess isolation?

Inside the FastMCP stdio child on Windows, the openai SDK's first sync httpx request hangs indefinitely (asyncio + piped stdio interaction). CrewAI and LangGraph workflow are therefore spawned as clean subprocesses (`_run_crew_subprocess.py`, `_run_workflow_subprocess.py`) — JSON-only output, UTF-8 stdout, stderr discarded. Same fix also prevents CrewAI's verbose output from corrupting MCP JSON-RPC frames.

## 📦 Setup

### Frontend
```bash
npm install
npm run dev               # http://localhost:5173
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env    # fill in API keys
.venv\Scripts\python -m uvicorn main:app --reload   # http://localhost:8000
```

### Environment Variables

| Variable | Required | Used For |
|---|---|---|
| `OPENAI_API_KEY` | for real AI | CrewAI, LangGraph, MCP host agent |
| `GEMINI_API_KEY` | for real CV analysis | CV Tailorer Gemini mode |
| `SUPABASE_URL` / `SUPABASE_KEY` | for auth | User registration, login, CV profile storage |
| `LANGSMITH_TRACING` | optional | Set to `true` to enable LangSmith tracing |
| `LANGSMITH_API_KEY` | optional | LangSmith API key |
| `LANGSMITH_PROJECT` | optional | LangSmith project name (default: `InternIQ`) |
| `CORS_ORIGINS` | yes | Allowed frontend origins |

### LangSmith Tracing

When `LANGSMITH_TRACING=true`, every LangGraph invocation is traced with tags + metadata (workflow vs interview, listing id, CV source, session id, difficulty, question count). View runs at [smith.langchain.com](https://smith.langchain.com) under the configured project.

### MCP Terminal

Once `pip install -e .` is run inside `backend/`, the `interniqmcp` console script becomes available:

```bash
interniqmcp
```

Spawns the MCP server over stdio and gives an interactive REPL with 20+ commands (`tools`, `search`, `prepare`, `crewai`, `interview`, `ask`, etc.). The FastAPI server does **not** need to be running.

## 🌐 Deployment

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | [intern-iq-iota.vercel.app](https://intern-iq-iota.vercel.app) |
| Backend | Render | [interniq-api.onrender.com](https://interniq-api.onrender.com) |

## 📁 Project Structure

```
InternIQ/
├── src/                                # React Frontend
│   ├── components/
│   │   ├── AgentChat.jsx               # MCP Agent chat UI (/ajan)
│   │   ├── ApplicationWorkflow.jsx     # LangGraph workflow UI
│   │   ├── MockInterview.jsx           # AI Interview (LangGraph)
│   │   ├── CVTailorer.jsx              # CV analysis (Gemini)
│   │   ├── CompanyCards.jsx            # Company Intel
│   │   ├── Timeline.jsx                # Assignment-week timeline
│   │   ├── Logo.jsx                    # 5-square matrix logomark
│   │   └── ...                         # Hero, BentoGrid, ListingList…
│   ├── pages/                          # Page components (HomePage, AgentPage…)
│   ├── context/AuthContext.jsx         # Supabase auth state
│   ├── services/api.js                 # Centralized API client
│   └── index.css                       # Brutalist-modern design system
│
├── backend/                            # FastAPI Backend
│   ├── main.py                         # FastAPI entry, CORS, routers
│   ├── routers/
│   │   ├── auth.py                     # /auth/{register,login,me}
│   │   ├── listings.py                 # /listings
│   │   ├── companies.py                # /companies
│   │   ├── cv.py                       # /cv/analyze (Gemini)
│   │   ├── interview.py                # /interview (basic + LangGraph)
│   │   ├── workflow.py                 # /workflow/prepare
│   │   ├── crew.py                     # /crew/research (CrewAI)
│   │   ├── mcp.py                      # /mcp/demo
│   │   └── agent.py                    # /agent/chat (LLM-as-MCP-host)
│   │
│   ├── langgraph_workflow/             # 7-node Application Workflow
│   │   ├── state.py                    # WorkflowState (TypedDict)
│   │   ├── nodes.py                    # 7 node functions
│   │   ├── graph.py                    # StateGraph build & compile
│   │   └── _run_workflow_subprocess.py # MCP subprocess runner
│   │
│   ├── langgraph_interview/            # Mock Interview (2 graphs)
│   │   ├── state.py
│   │   ├── nodes.py                    # 5 nodes
│   │   └── graph.py                    # question_graph, answer_graph
│   │
│   ├── crew/                           # CrewAI module
│   │   ├── company_crew.py             # Agent + crew + run_crew()
│   │   ├── config/{agents,tasks}.yaml  # Crew definitions
│   │   └── _run_crew_subprocess.py     # MCP subprocess runner
│   │
│   ├── mcp_server/
│   │   └── interniq_mcp.py             # MCP server (17 tools)
│   │
│   ├── services/
│   │   ├── mcp_bridge.py               # MCP demo client
│   │   ├── mcp_agent.py                # LLM-as-MCP-host loop
│   │   ├── interniq_terminal.py        # interniqmcp REPL
│   │   ├── langsmith_tracing.py        # Tracing context manager
│   │   ├── profile_store.py            # User CV profiles
│   │   └── supabase_auth.py            # Auth validation
│   │
│   ├── data/                           # Static JSON (listings, companies)
│   └── requirements.txt
│
└── (assignment reports and study notes are kept locally, outside the repo)
```

## 🏛️ Architecture Notes

These are the design decisions that come up most often when this project is reviewed.

### 1. Shared Core — MCP and FastAPI Do Not Duplicate Code

The most common question: *"Are the MCP server and the FastAPI routers two parallel implementations of the same logic?"*

**No.** Both are thin transport adapters over the same business logic modules:

```
┌──────────────────────────────────────────────────────────────┐
│                  BUSINESS LOGIC (single source)              │
│                                                              │
│  langgraph_workflow/    langgraph_interview/                 │
│  crew/                  services/profile_store               │
│  services/supabase_auth services/langsmith_tracing           │
└──────────────────────────────────────────────────────────────┘
                ▲                              ▲
                │ import                       │ import
                │                              │
       ┌────────┴─────────┐          ┌─────────┴──────────┐
       │  FastAPI Routers │          │   MCP Server       │
       │  (HTTP/JSON)     │          │   (stdio JSON-RPC) │
       │                  │          │                    │
       │  Pydantic models │          │  @mcp.tool() decor │
       │  /workflow/...   │          │  17 tools          │
       │  /interview/...  │          │  2 resources       │
       │  /crew/...       │          │  1 prompt          │
       └──────────────────┘          └────────────────────┘
```

| Module | FastAPI imports it | MCP server imports it |
|---|---|---|
| `langgraph_workflow.graph.workflow_graph` | ✅ `routers/workflow.py:6` | ✅ `mcp_server/interniq_mcp.py:23` |
| `langgraph_interview.graph.{question_graph, answer_graph}` | ✅ `routers/interview.py:91` | ✅ `mcp_server/interniq_mcp.py:22` |
| `crew.company_crew.run_crew` | ✅ `routers/crew.py` | ✅ via `_run_crew_subprocess.py` |
| `services.profile_store` | ✅ `routers/workflow.py:9` | ✅ `mcp_server/interniq_mcp.py:25` |
| `services.supabase_auth` | ✅ `routers/workflow.py:10` | ✅ `mcp_server/interniq_mcp.py:26` |
| `routers.cv.get_fallback_analysis` | ✅ inside the router | ✅ `mcp_server/interniq_mcp.py:24` (from the router!) |

The only differences are the per-transport adapter concerns (request validation style, auth header vs `auth_session_id` argument, error frame format). A bug fix in the workflow graph propagates to both surfaces automatically.

### 2. Database Touch Points

MCP itself is a protocol — it has no built-in persistence. The DB layer lives behind specific tools.

| MCP Tool | Data source |
|---|---|
| `search_internships`, `get_listing_context` | Static JSON — `backend/data/listings.json` |
| `get_company_context` | Static JSON — `backend/data/companies.json` |
| `register_user`, `login_user`, `logout_user`, `get_current_account` | **Supabase Auth** via `services/supabase_auth.py` |
| `analyze_profile_cv_for_listing`, `run_profile_application_workflow`, `start_profile_mock_interview` | Supabase user metadata + `services/profile_store.py` (local cache) |
| `run_application_workflow`, `analyze_cv_for_listing` (anonymous) | Argument-only — no DB |
| `run_company_research`, `run_crewai_research` | LLM + static fallback — no DB |

So 8 of 17 tools touch Supabase. The framing is: MCP is the **capability-scoped, type-safe API surface** in front of the database. The LLM never writes SQL — it calls a named tool whose implementation owns the DB query.

### 3. MCP Resources (read-only, no tool call needed)

Two resources are exposed for hosts (e.g. Claude Desktop) that want to attach context without invoking a tool:

| URI | What it returns | Code |
|---|---|---|
| `interniq://listings` | All internship listings as JSON | `mcp_server/interniq_mcp.py:772` |
| `interniq://companies` | All company intelligence profiles as JSON | `mcp_server/interniq_mcp.py:783` |

```python
@mcp.resource(
    "interniq://listings",
    name="InternIQ Listings",
    description="Read-only JSON snapshot of InternIQ internship listings.",
    mime_type="application/json",
)
def listings_resource() -> str:
    return json.dumps(_load_listings(), ensure_ascii=False, indent=2)
```

Tool vs resource distinction: tools are **actions** (parameterised, may have side effects), resources are **data** (idempotent reads). Both back the same JSON files; the resource form is convenient for hosts that pre-load context.

### 4. Memory and State

InternIQ does **not** use any formal LLM memory primitive — no LangChain `ConversationBufferMemory`, no LangGraph `MemorySaver` / SQLite checkpointer, no vector store. There are four in-memory `dict` stores instead, all wiped on backend restart:

| Store | Location | Holds |
|---|---|---|
| `_sessions` | `backend/routers/interview.py:94` | Web-side mock interview sessions |
| `_INTERVIEW_SESSIONS` | `backend/mcp_server/interniq_mcp.py:66` | MCP-side mock interview sessions |
| `_AUTH_SESSIONS` | `backend/mcp_server/interniq_mcp.py:67` | MCP `login_user` → `{email, profile}` |
| Frontend Supabase session | `src/context/AuthContext.jsx` | JWT in `localStorage` |

LangGraph workflow runs are single-shot — state lives inside one `workflow_graph.invoke()` call and is gone afterwards. Mock interview is the only multi-turn surface, and it threads its `TypedDict` state through `_sessions[session_id]` between turns. Production would swap the `dict` for Redis and add a `SqliteSaver` / `RedisCheckpointer` to LangGraph.

The MCP host agent (`backend/services/mcp_agent.py`) is also stateless — every `/agent/chat` request starts a fresh conversation, with no recollection of prior queries.

## 📝 License

© 2026 InternIQ. All rights reserved.
