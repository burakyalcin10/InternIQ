# InternIQ — AI Agent Planning Document

## 1. Project Overview

### 1.1 Website Topic and Purpose

**InternIQ** is an AI-powered internship platform designed to automate and streamline the entire internship application process for university students. The platform addresses four critical pain points that students face:

1. **Finding internships is time-consuming** — listings are scattered across LinkedIn, Kariyer.net, Indeed, and individual company websites
2. **Customizing CVs for each application is tedious** — each position requires different emphasis on skills and experiences
3. **Researching companies before interviews is difficult** — relevant information is spread across multiple sources
4. **Interview preparation lacks personalization** — generic preparation doesn't address company-specific expectations

### 1.2 Target Users

| User Segment | Description |
|--------------|-------------|
| **Primary** | University students (3rd-4th year) actively seeking internship positions |
| **Secondary** | Recent graduates looking for entry-level positions |
| **Tertiary** | Career counselors and university career centers |

### 1.3 Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🔍 **Staj Radar** | Aggregates internship listings from multiple platforms with smart filtering | Draft UI ✅ |
| 📄 **CV Tailorer** | AI-powered CV optimization with ATS compatibility scoring | Draft UI ✅ |
| 🏢 **Company Intel** | Company research dashboard (culture, tech stack, reviews, news) | Draft UI ✅ |
| 🎤 **Mock Interview** | AI-generated interview questions with real-time feedback | Draft UI ✅ |

---

## 2. AI Agent Concept

### 2.1 Problem Statement

University students spend an average of **15-20 hours per week** on internship-related activities: searching for listings, tailoring CVs, researching companies, and preparing for interviews. This process is:

- **Repetitive** — the same steps are performed for every application
- **Inefficient** — manual research and CV editing is slow
- **Incomplete** — students often miss relevant opportunities or preparation areas
- **Stressful** — the uncertainty of the process increases anxiety

### 2.2 AI Agent Types

InternIQ will integrate a **multi-agent system** where each agent specializes in a specific domain:

#### Agent 1: Scout Agent (Autonomous Researcher)
- **Type:** Autonomous background agent
- **Problem Solved:** Finding and filtering relevant internship listings
- **Technology:** AutoGen + Web Scraping
- **Behavior:** Continuously scans job platforms, filters based on user profile, sends notifications for high-match opportunities

#### Agent 2: CV Specialist Agent (Advisor)
- **Type:** Interactive advisor agent
- **Problem Solved:** CV optimization for specific positions
- **Technology:** OpenAI SDK (GPT-4)
- **Behavior:** Analyzes job description, compares with user's CV, suggests modifications, calculates ATS score

#### Agent 3: Research Agent (Investigator)
- **Type:** On-demand research agent
- **Problem Solved:** Comprehensive company intelligence gathering
- **Technology:** CrewAI (multi-agent collaboration)
- **Behavior:** Gathers data from Glassdoor, LinkedIn, news sites, tech blogs; synthesizes into actionable report

#### Agent 4: Interview Coach Agent (Evaluator)
- **Type:** Interactive coach/evaluator agent
- **Problem Solved:** Personalized interview preparation
- **Technology:** LangGraph (stateful conversation)
- **Behavior:** Generates company/position-specific questions, evaluates answers, provides improvement feedback

### 2.3 User Interaction Methods

| Agent | Interaction Type | Interface |
|-------|-----------------|-----------|
| Scout Agent | Background automation | Dashboard notifications, email alerts |
| CV Specialist | Interactive chat + form | Upload CV → Paste job description → Get recommendations |
| Research Agent | On-demand request | Click company → View auto-generated intelligence report |
| Interview Coach | Chat-based simulation | Real-time Q&A chat with feedback after each answer |

---

## 3. System Architecture (High-Level)

### 3.1 Architecture Overview

The system follows a **three-tier architecture** with an AI orchestration layer:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│                    React + Vite (SPA)                           │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │ Staj      │ │ CV        │ │ Company   │ │ Mock      │      │
│  │ Radar     │ │ Tailorer  │ │ Intel     │ │ Interview │      │
│  │ Dashboard │ │ Interface │ │ Dashboard │ │ Chat UI   │      │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘      │
└────────┼──────────────┼─────────────┼─────────────┼─────────────┘
         │              │             │             │
         ▼              ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                        │
│         REST Endpoints · WebSocket · JWT Authentication         │
│                                                                 │
│   /api/listings    /api/cv     /api/company    /api/interview   │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  AI ORCHESTRATION│ │   DATABASE   │ │ EXTERNAL APIs   │
│                  │ │              │ │                  │
│ ┌──────────────┐ │ │  Supabase    │ │ · LinkedIn API  │
│ │ Scout Agent  │ │ │ (PostgreSQL) │ │ · Kariyer.net   │
│ │ (AutoGen)    │ │ │              │ │ · Indeed API    │
│ ├──────────────┤ │ │ Tables:      │ │ · Glassdoor     │
│ │ CV Specialist│ │ │ · users      │ │ · OpenAI API    │
│ │ (OpenAI SDK) │ │ │ · profiles   │ │ · Gmail API     │
│ ├──────────────┤ │ │ · listings   │ │ · News APIs     │
│ │ Research     │ │ │ · cvs        │ │                  │
│ │ Agent(CrewAI)│ │ │ · companies  │ │                  │
│ ├──────────────┤ │ │ · interviews │ │                  │
│ │ Coach Agent  │ │ │ · history    │ │                  │
│ │ (LangGraph)  │ │ │              │ │                  │
│ ├──────────────┤ │ │              │ │                  │
│ │ MCP Protocol │ │ │              │ │                  │
│ │ Integration  │ │ │              │ │                  │
│ └──────────────┘ │ │              │ │                  │
└──────────────────┘ └──────────────┘ └─────────────────┘
```

### 3.2 Data Flow

```
User Action → Frontend Component → API Request → FastAPI Router
    → Agent Orchestrator → Specific AI Agent(s)
    → External API Calls (if needed)
    → Response Processing
    → Database Update
    → API Response → Frontend Update → User Sees Result
```

### 3.3 AI Agent Interaction Details

#### Frontend ↔ AI Agent Communication
- **CV Tailorer:** HTTP POST request with job description → Backend processes with OpenAI SDK → Returns analysis JSON
- **Mock Interview:** WebSocket connection for real-time chat → LangGraph manages conversation state → Streaming responses
- **Company Intel:** HTTP GET request → CrewAI agent team executes research → Returns compiled report
- **Staj Radar:** Background cron job (AutoGen) → Updates database → Frontend polls or receives push notifications

#### External API Integration via MCP
The **Model Context Protocol (MCP)** will be used to standardize communication with external services:
- LinkedIn MCP Server → Job listings, company profiles
- Gmail MCP Server → Application tracking, follow-up reminders
- Kariyer.net MCP Server → Local job market data

### 3.4 Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Vite | Single Page Application |
| Styling | CSS3 (custom design system) | Premium dark theme UI |
| Backend | FastAPI (Python) | REST API + WebSocket |
| Database | Supabase (PostgreSQL) | Data persistence, auth |
| AI - Week 2 | OpenAI SDK | CV analysis, text generation |
| AI - Week 3 | CrewAI | Multi-agent research team |
| AI - Week 4 | LangGraph | Stateful interview workflow |
| AI - Week 5 | AutoGen | Autonomous listing scanner |
| AI - Week 6 | MCP | External service integration |
| Deployment (FE) | Vercel / GitHub Pages | Frontend hosting |
| Deployment (BE) | Railway | Backend hosting |

### 3.5 Weekly Development Roadmap

| Week | Framework | InternIQ Integration |
|------|-----------|---------------------|
| Week 2 | OpenAI SDK | CV Tailoring assistant — analyze job descriptions, optimize CV content |
| Week 3 | CrewAI | Multi-agent research team — Researcher + CV Expert + Interview Coach |
| Week 4 | LangGraph | Application workflow engine — Apply → Prepare → Track stateful flow |
| Week 5 | AutoGen | Autonomous listing scanner — automated search and notification system |
| Week 6 | MCP | Platform integrations — LinkedIn, Kariyer.net, Gmail connectors |

---

## 4. Conclusion

InternIQ is designed as a modular, extensible platform where each weekly AI framework naturally maps to a specific feature area. The draft website establishes the UI/UX foundation, while the multi-agent architecture ensures that each aspect of the internship process is handled by a specialized AI agent. This approach allows incremental integration of AI capabilities without requiring a complete system redesign at each stage.

The key differentiator of InternIQ is its **end-to-end approach**: rather than solving one aspect of internship search, it provides a unified platform that accompanies students from discovery through preparation to application tracking.
