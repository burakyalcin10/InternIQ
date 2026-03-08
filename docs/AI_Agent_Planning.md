# InternIQ — AI Agent Integration Planning Document

---

## 1. Project Overview

### 1.1 Website Topic and Purpose

**InternIQ** is an AI-powered platform that aims to automate the end-to-end internship application process for university students in Turkey. The name "InternIQ" reflects the project's core philosophy: bringing intelligence (IQ) to every step of the internship journey — from discovery to preparation to follow-up.

The platform was born from a real, personal pain point: as a computer engineering student, finding relevant internship opportunities is a fragmented, time-consuming, and often overwhelming experience. Job listings are spread across multiple platforms (LinkedIn, Kariyer.net, Indeed, individual company career pages), each with different interfaces and search mechanisms. Once a relevant position is found, tailoring a CV to match the job description requires significant manual effort. Researching the company's culture, technical stack, and interview process adds additional hours. Finally, preparing for technical and behavioral interviews without company-specific guidance leads to generic, unfocused preparation.

InternIQ addresses all four of these pain points through a unified platform powered by specialized AI agents.

### 1.2 Target Users

The platform serves three distinct user segments, each with different needs:

| User Segment | Profile | Primary Need |
|---|---|---|
| **Primary** | Computer Science / Engineering students (3rd–4th year) actively seeking internship positions in the Turkish tech market | End-to-end application support: finding listings, tailoring CVs, company research, and interview prep |
| **Secondary** | Recent graduates (0–1 year experience) looking for entry-level positions | Similar workflow but with more emphasis on portfolio presentation and salary negotiation guidance |
| **Tertiary** | University career center counselors and academic advisors | Dashboard view to track student applications, aggregate analytics, and provide guided support |

### 1.3 Core Features of the Website

The website (draft version) implements four core modules, each corresponding to a specific stage of the internship application lifecycle:

**1. Staj Radar (Internship Radar)**
- Aggregates internship listings from multiple sources into a single, unified view
- Provides filtering by position type (Remote, On-site, Hybrid), technology stack, and company
- Displays a "match score" indicating how well each listing aligns with the user's profile
- Current implementation: Static data rendered dynamically via JavaScript with real-time search filtering

**2. CV Tailorer**
- Allows users to paste a job description and receive AI-powered CV optimization recommendations
- Calculates an ATS (Applicant Tracking System) compatibility score
- Provides specific, actionable suggestions for improving CV content
- Current implementation: Simulated analysis with pre-configured suggestions; will be replaced with OpenAI SDK integration in Week 2

**3. Company Intel**
- Provides comprehensive company profiles including culture, tech stack, Glassdoor ratings, interview style, and recent news
- Enables students to research companies before applying, leading to more informed applications
- Current implementation: Static company data rendered as interactive cards

**4. Mock Interview**
- Interactive chat-based interview simulation with category selection (Technical vs. Behavioral)
- Generates position-specific questions and provides feedback on user answers
- Evaluates response depth and provides improvement suggestions
- Current implementation: Rule-based feedback system; will be replaced with LangGraph-powered conversational AI in Week 4

---

## 2. AI Agent Concept

### 2.1 Problem Definition

University students in Turkey spend an estimated 15–20 hours per week on internship-related activities. This time breaks down approximately as follows:

| Activity | Time (hrs/week) | Pain Level |
|---|---|---|
| Searching for listings across platforms | 4–6 | High — repetitive, scattered |
| Tailoring CV for each application | 3–5 | High — tedious, uncertain quality |
| Researching companies | 2–3 | Medium — information overload |
| Preparing for interviews | 3–4 | High — lacks personalization |
| Tracking applications and follow-ups | 1–2 | Medium — easily forgotten |

The fundamental problem is not the lack of information, but its fragmentation and the manual effort required to synthesize it into actionable steps. An AI agent system can automate the repetitive aspects while providing personalized, context-aware assistance at each stage.

### 2.2 AI Agent Descriptions

InternIQ will integrate four specialized AI agents, each designed to solve a specific problem:

#### Agent 1: Scout Agent — Autonomous Listing Aggregator

| Attribute | Description |
|---|---|
| **Type** | Autonomous background agent |
| **Problem Solved** | Eliminates the need to manually check multiple job platforms daily |
| **Core Capability** | Continuously scans LinkedIn, Kariyer.net, Indeed, and company career pages for new internship listings matching the user's profile |
| **Behavior** | Runs on a scheduled basis (e.g., every 6 hours). Extracts listing details, deduplicates across platforms, calculates a match score based on the user's skills and preferences, and sends push notifications for high-match opportunities (>80%) |
| **Technology** | AutoGen framework for autonomous multi-step execution; BeautifulSoup/Playwright for web scraping |
| **Input** | User profile (skills, interests, location preference, experience level) |
| **Output** | Ranked list of new internship opportunities with match scores and direct application links |

#### Agent 2: CV Specialist Agent — Interactive CV Optimizer

| Attribute | Description |
|---|---|
| **Type** | Interactive advisor agent (on-demand) |
| **Problem Solved** | Automates CV customization for each job application |
| **Core Capability** | Analyzes the job description, compares it against the user's master CV, and generates a tailored version with optimized keywords, restructured bullet points, and ATS-friendly formatting |
| **Behavior** | User pastes a job description → Agent extracts key requirements → Identifies gaps between requirements and CV → Suggests specific modifications → Calculates ATS compatibility score |
| **Technology** | OpenAI SDK (GPT-4 Turbo) for natural language understanding and generation |
| **Input** | Job description text + user's master CV |
| **Output** | Tailored CV content, ATS score (0–100), specific improvement suggestions with before/after examples |

#### Agent 3: Research Agent — Company Intelligence Gatherer

| Attribute | Description |
|---|---|
| **Type** | On-demand research agent (multi-agent collaboration) |
| **Problem Solved** | Consolidates scattered company information into a single actionable report |
| **Core Capability** | Gathers and synthesizes information from Glassdoor, LinkedIn, tech blogs, news sites, and GitHub to create a comprehensive company profile |
| **Behavior** | Triggered when user clicks on a company or explicitly requests research. Three sub-agents collaborate: (1) Culture Agent reads Glassdoor reviews and employee feedback, (2) Tech Agent analyzes GitHub repos and job postings to identify the tech stack, (3) News Agent searches for recent company news and press releases. Results are synthesized into a unified report |
| **Technology** | CrewAI framework for orchestrating multiple collaborative agents with defined roles and goals |
| **Input** | Company name |
| **Output** | Structured company intelligence report (culture, tech stack, interview format, pros/cons, recent developments) |

#### Agent 4: Interview Coach Agent — Conversational Mock Interviewer

| Attribute | Description |
|---|---|
| **Type** | Interactive coach/evaluator agent (stateful conversation) |
| **Problem Solved** | Provides personalized, company-specific interview preparation instead of generic practice |
| **Core Capability** | Generates interview questions tailored to the specific position and company, conducts a simulated interview via chat, and provides structured feedback on each answer |
| **Behavior** | User selects a company and position → Agent generates relevant technical and behavioral questions → User answers in natural language → Agent evaluates based on relevance, depth, specificity, and communication clarity → Provides score and improvement suggestions |
| **Technology** | LangGraph for managing stateful multi-turn conversation with branching logic (follow-up questions, difficulty adjustment) |
| **Input** | Company name, position title, user's experience level |
| **Output** | Series of interview questions, per-answer feedback, overall readiness score, areas for improvement |

### 2.3 User Interaction Model

Each agent has a distinct interaction pattern designed around natural user workflows:

```
         ┌──────────────────────────────────────────────┐
         │              USER JOURNEY                     │
         │                                              │
         │   ┌─────────┐    ┌─────────┐    ┌─────────┐ │
         │   │ DISCOVER │───▶│ PREPARE │───▶│  APPLY  │ │
         │   └────┬────┘    └────┬────┘    └────┬────┘ │
         │        │              │              │       │
         │   Scout Agent    CV Specialist   (Combined)  │
         │   Company Intel  Coach Agent                 │
         │                                              │
         │   Background     Interactive     Automated   │
         │   Notifications  Chat & Forms    Follow-up   │
         └──────────────────────────────────────────────┘
```

| Agent | Trigger | Interaction | Response |
|---|---|---|---|
| Scout Agent | Automatic (scheduled) | Dashboard + push notifications | Listing cards with match scores |
| CV Specialist | User-initiated | Paste job description → Get analysis | ATS score + improvement list |
| Research Agent | User-initiated (click company) | One-click → Wait → Read report | Structured company profile |
| Interview Coach | User-initiated | Interactive chat conversation | Questions → Feedback → Score |

---

## 3. System Architecture (High-Level)

### 3.1 Architecture Diagram

The system follows a modular three-tier architecture with an AI orchestration layer:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│                      React + Vite (SPA)                         │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Radar View │  │ CV Editor  │  │ Intel View │  │ Interview │ │
│  │            │  │            │  │            │  │ Chat UI   │ │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  └─────┬─────┘ │
│         │               │               │              │        │
└─────────┼───────────────┼───────────────┼──────────────┼────────┘
          │               │               │              │
          │         REST API / WebSocket (JSON)          │
          │               │               │              │
┌─────────┼───────────────┼───────────────┼──────────────┼────────┐
│         ▼               ▼               ▼              ▼        │
│                    API LAYER (FastAPI)                           │
│                                                                 │
│   /api/v1/listings     → Scout Controller                       │
│   /api/v1/cv/analyze   → CV Controller                          │
│   /api/v1/company/{id} → Intel Controller                       │
│   /api/v1/interview/*  → Interview Controller (WebSocket)       │
│   /api/v1/auth/*       → Auth Controller (JWT)                  │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  AI ORCHESTRATION│ │   DATABASE   │ │ EXTERNAL SERVICES│
│  LAYER           │ │              │ │                  │
│                  │ │  Supabase    │ │  LinkedIn API    │
│  ┌────────────┐  │ │ (PostgreSQL) │ │  Kariyer.net     │
│  │  OpenAI    │  │ │              │ │  Indeed           │
│  │  SDK       │  │ │  Tables:     │ │  Glassdoor       │
│  ├────────────┤  │ │  ─ users     │ │  OpenAI API      │
│  │  CrewAI    │  │ │  ─ profiles  │ │  GitHub API      │
│  │            │  │ │  ─ listings  │ │  Gmail API       │
│  ├────────────┤  │ │  ─ cvs       │ │  News APIs       │
│  │  LangGraph │  │ │  ─ companies │ │                  │
│  │            │  │ │  ─ sessions  │ │                  │
│  ├────────────┤  │ │  ─ history   │ │                  │
│  │  AutoGen   │  │ │              │ │                  │
│  │            │  │ │              │ │                  │
│  ├────────────┤  │ │              │ │                  │
│  │  MCP       │  │ │              │ │                  │
│  │  Protocol  │  │ │              │ │                  │
│  └────────────┘  │ │              │ │                  │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

### 3.2 Data Flow Diagram

The following illustrates how a typical CV analysis request flows through the system:

```
User pastes job description in CV Tailorer
        │
        ▼
Frontend sends POST /api/v1/cv/analyze
  { jobDescription: "...", userId: "..." }
        │
        ▼
FastAPI validates request, retrieves user's CV from Supabase
        │
        ▼
CV Controller calls OpenAI SDK:
  System prompt + Job description + User CV
        │
        ▼
OpenAI GPT-4 returns structured analysis:
  { score: 87, keywords: [...], suggestions: [...] }
        │
        ▼
FastAPI saves analysis to history table
        │
        ▼
Response sent back to frontend
        │
        ▼
UI updates with ATS score + suggestions
```

### 3.3 AI Agent ↔ System Interaction Details

**Frontend ↔ Backend Communication:**
- CV Tailorer: Standard REST API (POST request → JSON response)
- Mock Interview: WebSocket connection for real-time bidirectional chat
- Company Intel: REST API with caching (GET request → cached or fresh JSON)
- Staj Radar: Polling endpoint + optional Server-Sent Events for new listing notifications

**Backend ↔ AI Layer:**
- Each agent controller instantiates the appropriate AI framework
- OpenAI SDK calls are direct API calls with structured prompts
- CrewAI spawns a crew of sub-agents that collaborate and return a merged result
- LangGraph maintains conversation state in a graph structure, enabling branching dialogue
- AutoGen operates as a background task with scheduled execution

**MCP (Model Context Protocol) Integration (Week 6):**
- MCP will standardize the interface between AI agents and external services
- LinkedIn MCP Server: Read job listings, company profiles
- Gmail MCP Server: Send follow-up emails, track application status
- Kariyer.net MCP Server: Access local Turkish job market data
- This abstraction allows agents to interact with external services without platform-specific code

### 3.4 Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| **Frontend (current)** | HTML5 + CSS3 + Vanilla JS | Rapid prototype for draft submission; zero build step, instant GitHub Pages deployment |
| **Frontend (planned)** | React 18 + Vite 5 | Component-based architecture for complex UI interactions; fast HMR development |
| **Styling** | Custom CSS Design System | Full control over aesthetics; dark theme with Space Grotesk typography |
| **Backend** | FastAPI (Python 3.11+) | Async-native, automatic OpenAPI docs, excellent Python AI library ecosystem |
| **Database** | Supabase (PostgreSQL) | Free tier, built-in auth, real-time subscriptions, Row Level Security |
| **AI – Week 2** | OpenAI SDK (Python) | GPT-4 Turbo for CV analysis and text generation |
| **AI – Week 3** | CrewAI | Multi-agent collaboration for company research pipeline |
| **AI – Week 4** | LangGraph | Stateful conversation graphs for mock interview flow |
| **AI – Week 5** | AutoGen | Autonomous agent loops for background listing scanning |
| **AI – Week 6** | MCP (Model Context Protocol) | Standardized external service integration layer |
| **Deployment (FE)** | Vercel / GitHub Pages | Free, automatic deployments from Git pushes |
| **Deployment (BE)** | Railway / Render | Free tier Python hosting with environment variable support |
| **Version Control** | Git + GitHub | Standard collaboration and assignment submission |

### 3.5 Development Roadmap

| Week | Course Topic | InternIQ Integration | Deliverable |
|---|---|---|---|
| **Week 2** | OpenAI SDK | CV Tailoring assistant: Replace simulated analysis with GPT-4 powered CV comparison, keyword extraction, and ATS scoring | Working `/api/v1/cv/analyze` endpoint |
| **Week 3** | CrewAI | Multi-agent company research: Build a crew of 3 sub-agents (Culture, Tech, News) that collaboratively generate company intelligence reports | Working `/api/v1/company/{id}` endpoint |
| **Week 4** | LangGraph | Stateful interview workflow: Design a conversation graph with adaptive difficulty, follow-up questions, and evaluation rubrics | Working WebSocket interview endpoint |
| **Week 5** | AutoGen | Autonomous listing scanner: Build an agent loop that scrapes job platforms, deduplicates, scores, and sends notifications | Background worker + notification system |
| **Week 6** | MCP | Platform integrations: Create MCP servers for LinkedIn, Kariyer.net, and Gmail, enabling agents to read/write external data through a unified protocol | MCP server implementations |

---

## 4. Feasibility and Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| API rate limits on job platforms | High | Medium | Implement caching, respect robots.txt, use official APIs where available |
| OpenAI API costs | Medium | Low | Use GPT-4 Turbo Mini for routine tasks, implement response caching |
| Complex LangGraph state management | Medium | Medium | Start with simple linear flow, add branching incrementally |
| Data freshness of listings | High | Medium | Implement TTL-based cache invalidation, scheduled re-scraping |
| User data privacy | Low | High | Use Supabase RLS, encrypt sensitive data, comply with KVKK |

---

## 5. Conclusion

InternIQ's architecture is designed for incremental AI integration. Each weekly course module maps directly to a specific platform feature, ensuring that learning is applied in a practical context. The modular agent architecture means each component can be developed, tested, and deployed independently.

The key differentiator is the **end-to-end approach**: rather than solving one aspect of the internship search, InternIQ provides a unified platform that supports students from opportunity discovery through preparation to application tracking. Each AI agent specializes in its domain while sharing context through the central database, creating a cohesive and intelligent user experience.

The draft website establishes the user interface patterns and interaction flows that will be enhanced with real AI capabilities as the course progresses.
