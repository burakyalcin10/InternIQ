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
- **Google Gemini** — CV analysis and ATS scoring
- **OpenAI GPT-4o-mini** — LLM backbone for CrewAI agents

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
| `OPENAI_API_KEY` | For real CrewAI | Company research AI agents |
| `GEMINI_API_KEY` | For real CV analysis | CV Tailorer Gemini AI mode |
| `CORS_ORIGINS` | Yes | Allowed frontend domains |

## 🌐 Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Frontend | Vercel | [intern-iq-iota.vercel.app](https://intern-iq-iota.vercel.app) |
| Backend | Render | [interniq-api.onrender.com](https://interniq-api.onrender.com) |

## 📁 Project Structure

```
InternIQ/
├── src/                        # React Frontend
│   ├── components/             # UI Components (ListingList, CVTailorer, CompanyCards, MockInterview, etc.)
│   ├── pages/                  # Page components (Home, Features, CompanyResearch, ListingDetail, About)
│   ├── services/api.js         # API service layer
│   ├── hooks/                  # Custom React hooks
│   └── index.css               # Design system
├── backend/                    # FastAPI Backend
│   ├── main.py                 # FastAPI app entry point
│   ├── routers/                # API endpoints (listings, companies, cv, interview, crew)
│   ├── crew/                   # CrewAI Module
│   │   ├── company_crew.py     # Agent creation, task assignment & crew kickoff
│   │   └── config/
│   │       ├── agents.yaml     # Agent role, goal & backstory definitions
│   │       └── tasks.yaml      # Task descriptions & expected outputs
│   ├── data/                   # JSON data files (listings, companies)
│   └── requirements.txt        # Python dependencies
└── docs/
    └── AI_Agent_Planning.md    # Comprehensive AI agent planning document
```

## 📝 License

© 2026 InternIQ. All rights reserved.
