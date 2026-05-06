# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# InternIQ — AI-Powered Internship Platform

## Project Overview

**InternIQ** is an AI-powered internship search and application platform for university students. It automates the entire internship preparation pipeline with four core modules:

1. **Staj Radar** — Internship listing aggregation with search & filtering
2. **CV Tailorer** — AI-powered CV optimization with ATS scoring (Google Gemini)
3. **Company Intel** — Company research & interview insights via CrewAI multi-agent system
4. **Mock Interview** — Position-specific interview simulation with LangGraph + AI feedback
5. **MCP Server** — InternIQ features exposed as MCP tools/resources/prompts over stdio transport
6. **MCP AI Agent** — LLM-as-MCP-host: GPT-4o-mini autonomously selects and calls MCP tools

---

## Tech Stack

### Frontend
- **React 18** + **Vite** — Single Page Application with client-side routing
- **React Router v7** — Page routing (BrowserRouter)
- **Framer Motion** — Smooth animations and transitions
- **Lucide React** — Modern icon library
- **Supabase JS Client** — Auth & real-time DB integration (planned)
- **Custom CSS** — Brutalist-modern dark design system (amber accent, solid cards, no glassmorphism)
- **SVG Logo** — `src/components/Logo.jsx` — 5-square matrix mark, standalone + mark variants

**Frontend Build:**
```bash
npm install
npm run dev          # Vite dev server (default port 5173)
npm run build        # Optimized production build
npm run lint         # ESLint checks
npm run preview      # Local production build preview
```

### Backend
- **FastAPI** (Python 3.11) — REST API with automatic OpenAPI docs
- **Uvicorn** — ASGI web server
- **Pydantic** — Data validation
- **Python-dotenv** — Environment configuration

**Backend Setup:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Unix
pip install -r requirements.txt
cp .env.example .env       # Configure API keys
uvicorn main:app --reload  # Dev server (port 8000)
```

### AI/ML Integrations

#### 1. **MCP** (Model Context Protocol)
- **Purpose:** Expose InternIQ features as a standard protocol layer (tools, resources, prompts)
- **Server:** `backend/mcp_server/interniq_mcp.py` — 17 tools, 2 resources, 1 prompt, stdio transport
- **Client Bridge:** `backend/services/mcp_bridge.py` — async client that runs the demo flow (connect → initialize → discover → call tool → return context)
- **AI Agent:** `backend/services/mcp_agent.py` — GPT-4o-mini as MCP host; agentic loop that discovers tools and calls them autonomously
- **Terminal:** `backend/services/interniq_terminal.py` — interactive CLI (`interniqmcp` command)
- **API Endpoint:** `POST /api/v1/mcp/demo` — runs MCP demo flow, returns `mcp_trace`
- **Agent Endpoint:** `POST /api/v1/agent/chat` — LLM-driven MCP agent, returns `tool_calls` + `answer`
- **Frontend:** `/ajan` page with `AgentChat` component showing tool call log + LLM answer

#### 2. **LangGraph** (Stateful Workflows)
- **Purpose:** Orchestrate multi-step AI workflows with stateful graphs
- **Used for:**
  - Application Preparation Workflow (7-node graph)
  - Mock Interview System (2 compiled graphs)
- **Features:** Conditional routing, message accumulation, fallback responses
- **LangSmith Tracing:** All executions traced for observability

#### 2. **CrewAI** (Multi-Agent System)
- **Purpose:** Company intelligence research via agent collaboration
- **Agents:** Culture Researcher → Tech Analyst → Report Writer (sequential)
- **Output:** Structured company intelligence JSON report
- **Config files:** `backend/crew/config/agents.yaml` & `tasks.yaml`

#### 3. **OpenAI** (LLM Backbone)
- **Model:** GPT-4o-mini (for CrewAI agents and LangGraph nodes)
- **Purpose:** Generate questions, evaluate answers, analyze content
- **Fallback:** Pre-built demo responses when API key unavailable

#### 4. **Google Gemini** (CV Analysis)
- **Purpose:** PDF CV analysis and ATS score calculation
- **Used in:** CV Tailorer module
- **Fallback:** Keyword-based analysis when API key unavailable

---

## Architecture

### Frontend Structure

```
src/
├── components/              # Reusable UI components
│   ├── MockInterview.jsx   # LangGraph interview UI + basic mode
│   ├── ApplicationWorkflow.jsx  # 7-step workflow orchestration UI
│   ├── CVTailorer.jsx      # CV analysis interface
│   ├── CompanyCards.jsx    # Company intelligence display
│   ├── ListingList.jsx     # Internship listings
│   ├── Navbar.jsx          # Navigation
│   ├── Hero.jsx            # Landing page hero
│   ├── BentoGrid.jsx       # Feature showcase
│   ├── Timeline.jsx        # Process timeline
│   └── ...                 # Other UI components
│
├── pages/                   # Page-level components
│   ├── HomePage.jsx        # Landing
│   ├── ListingDetail.jsx   # Listing details + ApplicationWorkflow
│   ├── CompanyResearch.jsx # Company intelligence page
│   ├── LoginPage.jsx       # Auth
│   ├── RegisterPage.jsx    # Auth
│   ├── AccountPage.jsx     # User profile
│   └── FeaturesPage.jsx    # Features overview
│
├── context/                 # State management
│   ├── AuthContext.jsx     # Auth state + Supabase integration
│   └── useAuth.js          # Auth hook
│
├── services/
│   └── api.js              # API client with auth headers
│
├── lib/
│   ├── supabase.js         # Supabase client initialization
│   └── auth-errors.js      # Error handling
│
├── hooks/
│   └── useAnimations.js    # Framer Motion helpers
│
└── index.css               # Global styles + design system
```

**Entry Point:** `src/main.jsx` → `src/App.jsx` → Routes

**API Communication:**
- All frontend API calls go through `services/api.js`
- Base URL: `VITE_API_URL` (default: `http://localhost:8000/api/v1`)
- Auth: Supabase JWT token in `Authorization: Bearer <token>` header

### Backend Structure

```
backend/
├── main.py                 # FastAPI app entry point
│                          # CORS config, router registration
│
├── routers/               # API endpoint modules
│   ├── auth.py           # User authentication (login/register/me)
│   ├── listings.py       # GET /listings, /listings/{id}
│   ├── companies.py      # GET /companies, /companies/{id}
│   ├── cv.py             # POST /cv/analyze (Gemini + PDF upload)
│   ├── interview.py      # Interview endpoints (basic + LangGraph)
│   ├── crew.py           # POST /crew/research (CrewAI company research)
│   └── workflow.py       # POST /workflow/prepare (LangGraph application prep)
│
├── langgraph_interview/   # Mock Interview State Graphs
│   ├── state.py          # InterviewState TypedDict
│   ├── nodes.py          # 5 graph nodes
│   └── graph.py          # StateGraph definition + compiled graphs
│
├── langgraph_workflow/    # Application Preparation State Graph
│   ├── state.py          # WorkflowState TypedDict
│   ├── nodes.py          # 7 graph nodes
│   └── graph.py          # StateGraph definition + compiled graph
│
├── crew/                  # CrewAI Company Research
│   ├── company_crew.py   # Agent creation, task definition, run_crew()
│   ├── config/
│   │   ├── agents.yaml   # 3 agents: Culture Researcher, Tech Analyst, Report Writer
│   │   └── tasks.yaml    # Task definitions for each agent
│   └── fallback data     # Pre-built reports for major Turkish companies
│
├── services/              # Utility services
│   ├── langsmith_tracing.py    # LangSmith context manager + config
│   ├── profile_store.py        # User profile & CV storage
│   └── supabase_auth.py        # Supabase auth validation
│
├── data/                  # Static JSON data
│   └── [internship listings, company data]
│
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .env                  # (gitignored) Active configuration
├── Procfile              # Render deployment config
├── build.sh              # Build script
├── runtime.txt           # Python 3.11.11 version
└── .python-version       # Version pin for local dev
```

**Entry Point:** `backend/main.py`

---

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` — Register new user
- `POST /auth/login` — User login
- `GET /auth/me` — Get current user

### Listings (`/listings`)
- `GET /listings` — List all internship listings
- `GET /listings/{id}` — Get listing details

### Companies (`/companies`)
- `GET /companies` — List companies
- `GET /companies/{id}` — Get company details

### CV Analysis (`/cv`)
- `POST /cv/analyze` — Analyze CV against job description (Gemini API)
  - Input: `job_description`, `cv_file` (PDF) or `cv_text`
  - Output: `score`, `analysis`, `suggestions`

### Interview (`/interview`)

**Basic Mode (Rule-based):**
- `POST /interview/ask` — Get question by category
  - Input: `category` ("technical" | "behavioral"), `question_index`
  - Output: Question object with difficulty
- `POST /interview/evaluate` — Evaluate answer (rule-based)
  - Input: `question`, `answer`
  - Output: `feedback`, `score`

**LangGraph Mode (AI-powered):**
- `POST /interview/lg/start` — Start LangGraph interview session
  - Input: `company`, `position`, `category`, `max_questions`
  - Output: `session_id`, `question`, `question_number`, `difficulty`
  
- `POST /interview/lg/answer` — Submit answer (stateful)
  - Input: `session_id`, `answer`
  - Output: `feedback`, `score`, `difficulty`, `phase`
  - Returns: Next question or final summary with average score

### CrewAI Company Research (`/crew`)
- `POST /crew/research` — Research company via CrewAI agents
  - Input: `company_name`
  - Output: Structured intelligence report

### LangGraph Workflow (`/workflow`)
- `POST /workflow/prepare` — Run application preparation workflow
  - Input: `listing_id`, `cv_text` (optional)
  - Output: 7-step workflow results + `mcp_trace` (MCP protocol trace)

### MCP Demo (`/mcp`)
- `POST /mcp/demo` — Run MCP stdio demo flow, returns full protocol trace

### MCP AI Agent (`/agent`)
- `POST /agent/chat` — LLM-as-MCP-host: natural language → autonomous tool calls → answer
  - Input: `message` (string)
  - Output: `status`, `answer`, `tool_calls[]` (tool + args + result), `tools_available[]`

---

## Key Data Flows

### Mock Interview (LangGraph)
```
User: "Başla" (Start in AI mode)
  → Frontend: POST /interview/lg/start
  → Backend: question_graph.invoke(initial_state)
  → Generate first question
  → Frontend: Display question
  → User: Types answer
  → Frontend: POST /interview/lg/answer
  → Backend: answer_graph.invoke(session_state)
    - evaluate_answer: AI scores (0-100)
    - adjust_difficulty: Raises/lowers difficulty
    - check_progress (ROUTER): continue or done?
      - continue → generate_question
      - done → generate_summary
  → Frontend: Display feedback, score, next question (or summary)
  → Repeat until max_questions reached or done
```

**Session Management:** In-memory dict `_sessions[session_id]`

### Application Preparation Workflow (LangGraph)
```
User: Clicks "Hazırla" on listing
  → Frontend: POST /workflow/prepare
  → Backend: workflow_graph.invoke(initial_state)
    1. analyze_listing: Extract job requirements
    2. evaluate_cv: Score CV match (0-100)
    3. [Conditional] suggest_improvements: Tips if score < 70
    4. research_company: CrewAI integration
    5. generate_interview_prep: Position-specific questions
    6. create_action_plan: Personalized roadmap
  → Frontend: Display multi-step results
```

**Conditional Edge:** Routes through improvements only if CV score < 70

### CrewAI Company Research
```
User: Clicks company card
  → Frontend: POST /crew/research
  → Backend: run_crew() with 3 sequential agents
    1. Culture Researcher: company culture
    2. Tech Analyst: tech stack
    3. Report Writer: synthesize findings
  → Backend: Return structured JSON report
  → Frontend: Display company intelligence
```

**Fallback:** Pre-built reports when OpenAI key unavailable

---

## Environment Variables

### Frontend (`.env`)
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend (`backend/.env`)
```env
# Supabase (database — planning migration)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# OpenAI (CrewAI + LangGraph)
OPENAI_API_KEY=your_openai_key_here

# Google Gemini (CV analysis)
GEMINI_API_KEY=your_gemini_key_here

# LangSmith (tracing)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=InternIQ

# App Config
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Development Workflow

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11 (backend)
- Git

### Local Setup

1. **Frontend**
   ```bash
   npm install
   npm run dev
   # http://localhost:5173
   ```

2. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   # Edit .env with API keys
   uvicorn main:app --reload
   # http://localhost:8000
   # Docs: http://localhost:8000/docs
   ```

### Testing

- **Frontend Linting:** `npm run lint`
- **Backend Docs:** http://localhost:8000/docs (auto OpenAPI)
- **LangSmith Tracing:** smith.langchain.com (if enabled)

### Code Organization

**Frontend:**
- Components in `src/components/` (reusable)
- Pages in `src/pages/` (routes)
- API calls in `src/services/api.js` (centralized)
- Context in `src/context/` (global state)

**Backend:**
- Endpoints in `routers/` (module per feature)
- LangGraph graphs in `langgraph_*` folders
- Utilities in `services/`
- Pydantic models for validation

---

## Deployment

### Frontend
- **Platform:** Vercel
- **URL:** https://intern-iq-iota.vercel.app
- **Build:** `npm run build` → `dist/`

### Backend
- **Platform:** Render
- **URL:** https://interniq-api.onrender.com
- **Build:** `build.sh` → pip install requirements
- **Runtime:** Python 3.11.11
- **Proc:** Uvicorn via Procfile

---

## Common Tasks

### Add a New API Endpoint

1. Create router file (e.g., `backend/routers/newfeature.py`)
2. Define Pydantic models for request/response
3. Implement endpoint function (async def)
4. Register in `backend/main.py`:
   ```python
   from routers import newfeature
   app.include_router(newfeature.router, prefix="/api/v1", tags=["NewFeature"])
   ```
5. Add frontend API call in `src/services/api.js`
6. Use in component

### Add LangGraph Node

1. Define node function in `backend/langgraph_*/nodes.py`
2. Add state fields if needed in `state.py`
3. Register in `backend/langgraph_*/graph.py`:
   ```python
   graph.add_node("node_name", node_function)
   graph.add_edge(source_node, "node_name")
   ```

### Debug LangGraph Flow

1. Enable `LANGSMITH_TRACING=true`
2. Run endpoint
3. Check smith.langchain.com
4. View full trace with timing per node

### Add React Component

1. Create file in `src/components/MyComponent.jsx`
2. Import hooks/styles
3. Export default function component
4. Import and use in page

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Check CORS_ORIGINS in backend/.env |
| API 404 | Ensure router registered in backend/main.py |
| LangGraph fallback | Set OPENAI_API_KEY in backend/.env |
| CrewAI fallback | Set OPENAI_API_KEY for real agents |
| CV analysis fails | Set GEMINI_API_KEY or use keyword fallback |
| Session not found | Use /interview/lg/start first |
| Vite port taken | Kill process or npm run dev -- --port 5174 |
| Python venv issue | Use absolute path or check Windows exec policy |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| backend/main.py | FastAPI entry point, CORS, routers |
| backend/langgraph_interview/graph.py | Interview graphs |
| backend/langgraph_workflow/graph.py | Application workflow graph |
| backend/crew/company_crew.py | CrewAI agents + fallback |
| backend/routers/interview.py | Interview endpoints |
| backend/routers/workflow.py | Workflow endpoint |
| backend/mcp_server/interniq_mcp.py | MCP server (17 tools, 2 resources, 1 prompt) |
| backend/services/mcp_bridge.py | MCP client bridge — runs demo flow, returns trace |
| backend/services/mcp_agent.py | LLM-as-MCP-host agentic loop (GPT-4o-mini) |
| backend/services/interniq_terminal.py | Interactive MCP terminal client (`interniqmcp`) |
| backend/routers/mcp.py | POST /mcp/demo endpoint |
| backend/routers/agent.py | POST /agent/chat endpoint |
| src/services/api.js | Frontend API client |
| src/App.jsx | Routes |
| src/components/Logo.jsx | SVG logomark — standalone + mark variants |
| src/components/AgentChat.jsx | MCP Agent chat UI |
| src/components/MockInterview.jsx | Interview UI |
| src/components/ApplicationWorkflow.jsx | Workflow UI |
| src/index.css | Design system — amber accent, brutalist-modern tokens |
| public/favicon.svg | Favicon — 5-square matrix mark |
| .env.example | Environment template |
| package.json | Frontend dependencies |
| backend/requirements.txt | Python dependencies |

---

## Key Patterns

- LangGraph states are `TypedDict`-based (`state.py`) — not Redux or React context
- All AI features have fallback responses when API keys are missing — check for `status: "fallback"` in responses
- Interview sessions are in-memory (`_sessions` dict in `routers/interview.py`) — restart backend clears them; production would need Redis
- Backend loads `.env` with a custom `load_local_env()` in `main.py` due to dotenv path resolution issues on this setup
- Frontend API calls always go through `src/services/api.js` — add new API functions there, not inline in components
- LangSmith tracing: wrap `workflow_graph.invoke()` / `answer_graph.invoke()` in `tracing_context()` from `services/langsmith_tracing.py` when adding new graph invocations
- CrewAI requires Python < 3.14 — the import is guarded with try/except in `routers/crew.py`
- MCP server runs as a subprocess over stdio — `mcp_bridge.py` and `mcp_agent.py` both use `StdioServerParameters` to spawn it; the FastAPI server does NOT need to be running for the terminal client to work
- MCP agent loop: max 6 iterations, skips auth-only tools (`_SKIP_TOOLS` set in `mcp_agent.py`), converts MCP `inputSchema` → OpenAI function format
- Design system: `--accent` is amber `#f59e0b`; `.glass-card` is now a solid card (no `backdrop-filter`); do not re-introduce blur/glassmorphism
- Logo: use `<Logo />` (mark-only, currentColor) inside already-colored containers; use `<Logo standalone />` for self-contained amber+dark mark
