# InternIQ — AI-Powered Internship Platform

AI-powered internship search platform. Find the right internship, let AI handle the preparation.

## 🚀 About the Project

InternIQ is an AI platform that automates the end-to-end internship application process for university students. It operates through four core modules:

1. **🔍 Staj Radar** — Aggregates internship listings from multiple platforms with search & filtering
2. **📄 CV Tailorer** — AI-powered CV optimization with ATS score analysis (Gemini AI)
3. **🏢 Company Intel** — Company culture, tech stack & interview insights via CrewAI multi-agent research
4. **🎤 Mock Interview** — Position-specific interview simulation with instant feedback

## 🛠️ Tech Stack

### Frontend
- **React 18** + **Vite** — Single Page Application with client-side routing
- **Framer Motion** — Smooth animations and micro-interactions
- **Lucide React** — Modern icon set
- **Custom CSS Design System** — Dark theme with glassmorphism

### Backend
- **FastAPI** (Python 3.11) — REST API with automatic OpenAPI docs
- **Uvicorn** — ASGI server
- **Supabase** — PostgreSQL database (planned migration)

### AI Integrations
- **CrewAI** — Multi-agent company research (3 agents: Culture Researcher, Tech Analyst, Report Writer)
- **LangGraph** — Stateful workflow orchestration (Application Workflow + AI Interview)
- **Google Gemini** — CV analysis and ATS scoring
- **OpenAI GPT-4o-mini** — LLM backbone for CrewAI agents and LangGraph nodes
- **LangSmith** — Tracing and observability for LangGraph workflows

## 🤖 CrewAI Architecture

The Company Intel module uses a 3-agent crew with sequential processing:

```
User selects company → POST /api/v1/crew/research
                            │
                            ▼
                ┌─────────────────────┐
                │  Culture Researcher │  → Analyzes work culture, intern experiences
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Tech Analyst      │  → Researches tech stack, interview process
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Report Writer     │  → Synthesizes into structured JSON report
                └──────────┬──────────┘
                           │
                           ▼
                  Final Intelligence Report
                  (displayed in React UI)
```

- **Config files**: `backend/crew/config/agents.yaml` & `tasks.yaml`
- **Kickoff code**: `backend/crew/company_crew.py` → `run_crew()`
- **Fallback**: Pre-built reports when API keys are unavailable

## 🔀 LangGraph Architecture

### 1. Application Preparation Workflow (`/api/v1/workflow/prepare`)

A 7-node StateGraph that orchestrates the entire application preparation process:

```
START → analyze_listing → evaluate_cv → [check_cv_score]
                                          ├── "needs_improvement" → suggest_improvements ─┐
                                          └── "good_fit" ────────────────────────────────────┤
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

- **Conditional Edge**: If CV score < 70, routes through `suggest_improvements` before company research
- **7 Nodes**: Each performs a specific analysis step with LLM + fallback
- **Output**: Comprehensive action plan with CV analysis, company info, interview questions

### 2. AI Mock Interview (`/api/v1/interview/lg/*`)

Two compiled StateGraphs for stateful interview sessions:

**Question Graph** (start):
```
START → generate_question → END
```

**Answer Graph** (per-answer):
```
START → evaluate_answer → adjust_difficulty → [check_progress]
                                                ├── "continue" → generate_question → END
                                                └── "done"     → generate_summary  → END
```

- **Dynamic Difficulty**: Adjusts question difficulty based on rolling score average
- **Session Management**: In-memory session store for stateful multi-turn conversations
- **5 Nodes**: generate_question, evaluate_answer, adjust_difficulty, check_progress (router), generate_summary
- **LangSmith Integration**: All graph executions are traced for observability

## 📦 Setup

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Fill in API keys in .env
.venv\Scripts\python -m uvicorn main:app --reload
```

### Environment Variables
| Variable | Required | Used For |
|----------|----------|----------|
| `OPENAI_API_KEY` | For real AI | CrewAI agents + LangGraph interview & workflow |
| `GEMINI_API_KEY` | For real CV analysis | CV Tailorer Gemini AI mode |
| `LANGSMITH_TRACING` | Optional | Enable LangSmith tracing (`true`) |
| `LANGSMITH_API_KEY` | Optional | LangSmith API key for observability |
| `LANGSMITH_PROJECT` | Optional | LangSmith project name |
| `CORS_ORIGINS` | Yes | Allowed frontend domains |

### LangSmith Tracing

LangSmith tracing is now wired into both LangGraph flows:

- `POST /api/v1/workflow/prepare`
- `POST /api/v1/interview/lg/start`
- `POST /api/v1/interview/lg/answer`

To enable it locally, add these values to `backend/.env`:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=InternIQ
```

When enabled, each run is sent to LangSmith with tags and metadata such as:

- workflow vs interview flow
- listing id
- CV source
- interview session id
- difficulty / question count

## 🌐 Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | [intern-iq-iota.vercel.app](https://intern-iq-iota.vercel.app) |
| Backend | Render | [interniq-api.onrender.com](https://interniq-api.onrender.com) |

## 📁 Project Structure

```
InternIQ/
├── src/                          # React Frontend
│   ├── components/               # UI Components
│   │   ├── MockInterview.jsx     # AI Interview (LangGraph) + Basic mode
│   │   ├── ApplicationWorkflow.jsx # LangGraph Workflow UI
│   │   ├── CVTailorer.jsx        # CV Analysis (Gemini)
│   │   ├── CompanyCards.jsx      # Company Intel
│   │   └── ...                   # Hero, BentoGrid, Timeline, etc.
│   ├── pages/                    # Page components
│   ├── services/api.js           # API service layer
│   ├── hooks/                    # Custom React hooks
│   └── index.css                 # Design system
├── backend/                      # FastAPI Backend
│   ├── main.py                   # FastAPI app entry point
│   ├── routers/                  # API endpoints
│   │   ├── interview.py          # Interview (Basic + LangGraph)
│   │   ├── workflow.py           # LangGraph Application Workflow
│   │   ├── crew.py               # CrewAI Company Research
│   │   ├── cv.py                 # CV Analysis (Gemini)
│   │   ├── listings.py           # Staj Radar
│   │   └── companies.py          # Company Data
│   ├── langgraph_interview/      # LangGraph Interview Module
│   │   ├── state.py              # InterviewState (TypedDict)
│   │   ├── nodes.py              # 5 graph nodes
│   │   └── graph.py              # StateGraph definition & compile
│   ├── langgraph_workflow/       # LangGraph Workflow Module
│   │   ├── state.py              # WorkflowState (TypedDict)
│   │   ├── nodes.py              # 7 graph nodes
│   │   └── graph.py              # StateGraph definition & compile
│   ├── crew/                     # CrewAI Module
│   │   ├── company_crew.py       # Agent creation & crew kickoff
│   │   └── config/               # YAML agent/task configs
│   ├── data/                     # JSON data files
│   └── requirements.txt          # Python dependencies
└── docs/
    └── AI_Agent_Planning.md      # AI agent planning document
```

## 📝 License

© 2026 InternIQ. All rights reserved.
