# InternIQ - LangGraph Implementation Report

**Student:** Burak Yalcin 20220808069  
**Project:** InternIQ - AI-Powered Internship Platform  
**Assignment:** LangGraph Integration Assignment  
**GitHub URL:** https://github.com/burakyalcin10/InternIQ  
**GitHub Account:** https://github.com/burakyalcin10  
**Live Demo:** https://intern-iq-iota.vercel.app  
**Backend API / Swagger:** https://interniq-api.onrender.com/docs  

---

## 1. Project Overview

InternIQ is an AI-powered internship platform developed for university students in Turkey. The goal of the project is to make the internship application process more efficient by combining internship discovery, CV analysis, company research, and interview preparation inside a single platform.

The project currently includes four major modules:

1. **Staj Radar** - Aggregates internship listings from different companies and platforms
2. **CV Tailorer** - Analyzes CV content and provides optimization suggestions
3. **Company Intel** - Performs AI-powered company research using CrewAI
4. **Mock Interview / Application Workflow** - Uses LangGraph to orchestrate stateful interview and application preparation flows

For this assignment, LangGraph was integrated into the existing InternIQ project without creating a new project. The purpose of this integration is not only to "include LangGraph", but to use it in meaningful, step-based, stateful AI workflows that solve real problems for internship applicants.

Before explaining the LangGraph-specific features, one important improvement should be mentioned: authentication and CV profile management were added so that users can save their CVs once and reuse them across AI modules. This makes the LangGraph workflows more realistic and personalized.

### Figure 1 - Authentication and profile entry point
> Insert a screenshot of the login/register/account access flow here. This figure should show that users can enter the system and that the project now supports account-based usage instead of only anonymous demo interactions.

---

## 2. Authentication and CV Profile Layer

To make the LangGraph features more useful, a lightweight authentication and user profile layer was implemented before finalizing the workflow. This addition allows students to create an account, sign in, upload their CV once, and reuse their saved CV profile in multiple AI flows.

This design is important because a LangGraph-based preparation flow becomes much more meaningful when it works on persistent user data rather than on temporary pasted text only.

The authentication/profile layer provides the following:

- User registration and sign-in
- Session-based access to personal features
- CV upload and storage inside the user profile
- Extraction of profile summary, skills, education, and project information from the uploaded CV
- Reuse of the saved CV inside the application workflow

In other words, the platform now supports a more product-like scenario:

1. A student creates an account
2. The student uploads a CV
3. The system analyzes and stores the CV profile
4. LangGraph workflow uses that profile during internship preparation

This makes the LangGraph integration significantly stronger because the graph now operates on user-specific context rather than on generic demo text.

### Figure 2 - Account page with embedded CV profile
> Insert a screenshot of the "Hesabım" page here. The screenshot should ideally show the saved CV summary, extracted skills, education section, and project information. This proves that CV data is embedded into the system and can later be consumed by LangGraph.

---

## 3. Why LangGraph Was Used

The assignment specifically requires LangGraph to be added into the existing project and implemented effectively. In this project, LangGraph was chosen for tasks that require:

- clearly defined steps,
- shared state across steps,
- conditional branching,
- and multi-stage AI orchestration.

This is different from CrewAI.

The project now uses both frameworks for different purposes:

| Component | Purpose |
|-----------|---------|
| **CrewAI** | Multi-agent company research in the Company Intel module |
| **LangGraph** | Stateful, step-by-step orchestration for application preparation and interview simulation |

This separation is intentional and technically meaningful:

- CrewAI is better suited for collaborative multi-agent research tasks
- LangGraph is better suited for deterministic flows with well-defined nodes and transitions

Therefore, LangGraph was integrated into two parts of the project:

1. **Application Preparation Workflow**
2. **AI Mock Interview**

Both are stateful, multi-step, and suitable for graph-based execution.

### Figure 3 - Features page showing LangGraph-based modules
> Insert a screenshot of the Features page here. It should show the LangGraph-related modules, especially the Application Workflow and the Mock Interview sections, so the reader can see that LangGraph was added into the existing platform.

---

## 4. LangGraph Application Preparation Workflow

The first and most important LangGraph integration in this assignment is the **Application Preparation Workflow**.

This flow is exposed from:

- `POST /api/v1/workflow/prepare`

and compiled in:

- `backend/langgraph_workflow/graph.py`

The graph orchestrates the internship preparation process from beginning to end. It takes the selected internship listing and the candidate's CV/profile data, then generates a structured preparation output.

### 4.1 Purpose of the Workflow

The goal of this workflow is to answer the following question:

> "Given this internship posting and this student's CV, how should the student prepare?"

Instead of generating one single AI answer, the workflow separates the problem into smaller and better-defined stages. This improves explainability and makes the implementation easier to discuss in class.

### 4.2 Workflow Steps

The graph contains the following steps:

1. **analyze_listing** - Parses the internship listing and extracts requirements
2. **evaluate_cv** - Evaluates the CV against the listing
3. **check_cv_score** - Determines whether the candidate needs improvement before continuing
4. **suggest_improvements** - Generates targeted CV suggestions if the score is low
5. **research_company** - Retrieves company information and context
6. **generate_interview_prep** - Produces interview preparation questions
7. **create_action_plan** - Synthesizes the full preparation plan

These steps are not only visible in code; they are also surfaced in the frontend so the workflow can be demonstrated clearly during class discussion.

### 4.3 Graph Topology

The graph structure is:

```text
START -> analyze_listing -> evaluate_cv -> [check_cv_score]
                                          |-- needs_improvement -> suggest_improvements -> research_company
                                          |-- good_fit ---------------------------------> research_company
research_company -> generate_interview_prep -> create_action_plan -> END
```

This conditional routing is one of the key reasons LangGraph is appropriate here. If the CV score is low, the graph routes through a CV improvement stage first. If the score is already acceptable, it skips that extra correction step and continues directly to company research.

This shows that the graph is not a static chain; it contains branching logic and stateful decision-making.

### 4.4 Workflow Graph Definition

The core graph is defined in `backend/langgraph_workflow/graph.py`. The following snippet shows how nodes and the conditional edge are registered:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(WorkflowState)

builder.add_node("analyze_listing", analyze_listing)
builder.add_node("evaluate_cv", evaluate_cv)
builder.add_node("suggest_improvements", suggest_improvements)
builder.add_node("research_company", research_company)
builder.add_node("generate_interview_prep", generate_interview_prep)
builder.add_node("create_action_plan", create_action_plan)

builder.add_edge(START, "analyze_listing")
builder.add_edge("analyze_listing", "evaluate_cv")

builder.add_conditional_edges(
    "evaluate_cv",
    check_cv_score,
    {
        "needs_improvement": "suggest_improvements",
        "good_fit": "research_company",
    },
)

builder.add_edge("suggest_improvements", "research_company")
builder.add_edge("research_company", "generate_interview_prep")
builder.add_edge("generate_interview_prep", "create_action_plan")
builder.add_edge("create_action_plan", END)

workflow_graph = builder.compile()
```

This snippet is important because it directly demonstrates that LangGraph is not only mentioned in the report; it is truly used to define a multi-step stateful execution graph.

### 4.5 Workflow Execution Through the FastAPI Router

The graph is executed from the backend router after the initial state is prepared from the internship listing and the user's CV/profile data:

```python
initial_state = {
    "listing_id": req.listing_id,
    "cv_text": cv_text,
    "candidate_profile": candidate_profile,
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
```

This part matters because it is the LangGraph equivalent of a "kickoff" step: the system gathers all necessary context, creates the initial graph state, and then invokes the graph to produce the final output.

### 4.6 Node Example: Conditional Routing

One of the simplest but most important nodes is the routing logic that decides whether the workflow should go through CV improvement first:

```python
def check_cv_score(state: dict) -> str:
    """Router: if CV score < 70, suggest improvements first."""
    if state.get("needs_improvement", False):
        return "needs_improvement"
    return "good_fit"
```

Although this function is short, it is critical for the effectiveness of the graph. It shows that the workflow is not just a linear sequence; the path changes according to the analysis result stored in the shared state.

### Figure 4 - Application workflow input screen
> Insert a screenshot of the Application Workflow input screen here. It should show internship selection, CV usage, and the "Hazırlık Planı Oluştur" button. If possible, capture the saved CV note that indicates the user's embedded profile is being used.

### Figure 5 - LangGraph steps visible in the UI
> Insert a screenshot showing the workflow steps (LangGraph nodes) here. This figure is especially important because it directly supports the assignment requirement that the steps must be well defined.

---

## 5. Application Workflow Output

The output of the LangGraph workflow is intentionally structured into multiple sections instead of a single paragraph. This makes the result more useful for students and also demonstrates that the graph is coordinating several AI operations together.

The result includes:

- CV analysis summary
- matched / missing skills
- CV improvement suggestions
- company information
- company-specific and CV-specific interview questions
- personalized action plan

### 5.1 CV-Aware Analysis

Because the user profile stores CV data, the workflow can operate on the student's actual background. The system does not only look at internship tags; it also uses the extracted summary, skills, education, and project information.

This improves personalization. For example, project experience can influence:

- the fit analysis,
- the generated interview questions,
- and the action plan.

### 5.2 Interview Preparation Split

One useful improvement made during development was splitting interview preparation into two categories:

1. **CV-specific questions**
2. **Company / role-specific questions**

This matters because a realistic internship preparation session should not only ask about the student's own projects. It should also prepare the student for generic technical or behavioral questions that the company may ask every candidate.

### 5.3 Personalized Action Plan

The final node synthesizes all previous outputs into a preparation plan. This gives the student a practical result instead of only diagnostic feedback.

The action plan typically includes:

- what to improve in the CV,
- what to study before the interview,
- what to expect from the company,
- and what to focus on during application preparation.

### Figure 6 - Workflow result (top section)
> Insert a screenshot of the workflow result page here. The top of the result should show the company name, position, CV score, and LangGraph execution badge.

### Figure 7 - Workflow result (questions + action plan)
> Insert a screenshot of the lower result area here. This should ideally show the split interview questions (CV-specific and company-specific) together with the personalized action plan.

---

## 6. LangGraph Mock Interview

The second LangGraph integration in the project is the **AI Mock Interview** module.

This module exists because internship candidates often need not only preparation advice, but also repeated question-answer practice. That type of interaction is stateful and sequential, which makes it a strong candidate for LangGraph.

The LangGraph interview mode is exposed via:

- `POST /api/v1/interview/lg/start`
- `POST /api/v1/interview/lg/answer`

### 6.1 Why LangGraph Fits the Interview Problem

An interview session naturally contains state:

- the current question,
- the candidate's answer,
- previous scores,
- difficulty level,
- how many questions have been asked,
- whether the interview should continue or stop.

LangGraph is ideal here because this state needs to be updated after every turn.

### 6.2 Interview Graph Structure

There are actually two compiled graphs used in this module:

#### Question Graph

```text
START -> generate_question -> END
```

#### Answer Graph

```text
START -> evaluate_answer -> adjust_difficulty -> [check_progress]
                                               |-- continue -> generate_question -> END
                                               |-- done     -> generate_summary  -> END
```

### 6.3 What the Interview Graph Demonstrates

This part of the system demonstrates that LangGraph is not only used for one workflow endpoint. It is also reused in a second, clearly different stateful interaction:

- dynamic question generation,
- answer evaluation,
- difficulty adaptation,
- progress control,
- summary generation at the end.

This strengthens the assignment significantly because LangGraph is not used in a superficial way; it is used as a reusable orchestration layer in multiple product features.

### 6.4 Interview Graph Definition

The mock interview uses two separate compiled LangGraph structures. The question graph is minimal, but the answer graph contains the real orchestration logic:

```python
builder = StateGraph(InterviewState)

builder.add_node("evaluate_answer", evaluate_answer)
builder.add_node("adjust_difficulty", adjust_difficulty)
builder.add_node("generate_question", generate_question)
builder.add_node("generate_summary", generate_summary)

builder.add_edge(START, "evaluate_answer")
builder.add_edge("evaluate_answer", "adjust_difficulty")

builder.add_conditional_edges(
    "adjust_difficulty",
    check_progress,
    {
        "continue": "generate_question",
        "done": "generate_summary",
    },
)

builder.add_edge("generate_question", END)
builder.add_edge("generate_summary", END)

answer_graph = builder.compile()
```

This second graph proves that LangGraph was not added for only one endpoint. Instead, it was reused in another stateful AI feature where multi-turn logic and branching are necessary.

### Figure 8 - Mock interview question screen
> Insert a screenshot of the LangGraph mock interview question screen here. It should show the current question, category, difficulty, and the active interview state.

### Figure 9 - Mock interview feedback / summary screen
> Insert a screenshot of the completed interview or feedback stage here. This figure should prove that the graph tracks answers and eventually produces a summary.

---

## 7. LangSmith Integration

The assignment notes that LangSmith integration is helpful. To strengthen the implementation and make it easier to discuss in class, LangSmith tracing was added to the project.

LangSmith is now wired into the LangGraph-based flows so that executions can be observed and inspected.

### 7.1 Traced Flows

Tracing was added to:

- `POST /api/v1/workflow/prepare`
- `POST /api/v1/interview/lg/start`
- `POST /api/v1/interview/lg/answer`

### 7.2 Why LangSmith Was Added

LangSmith helps in three ways:

1. It makes graph execution observable
2. It makes debugging easier
3. It improves explainability during demos and class discussion

For example, a traced run can show:

- which flow was triggered,
- which listing was analyzed,
- whether the CV came from manual input or saved profile,
- which interview session was active,
- how the graph progressed.

This is especially useful for demonstrating that the LangGraph integration is real and operational rather than only described conceptually.

### 7.3 Configuration

The following environment variables are used for tracing:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=InternIQ
```

The integration is optional. If these variables are not set, the system still runs normally; tracing is simply disabled.

### 7.4 LangSmith Tracing Code

Tracing is wrapped around the LangGraph invocation so that workflow executions can be inspected in LangSmith without changing the user-facing API:

```python
trace_tags = ["langgraph", "workflow", "application-prep"]
trace_metadata = {
    "listing_id": req.listing_id,
    "cv_source": cv_source,
    "has_manual_cv": bool(req.cv_text.strip()),
    "has_profile_cv": cv_source == "profile",
}

with tracing_context(
    project_name=get_langsmith_project("InternIQ-Workflow"),
    tags=trace_tags,
    metadata=trace_metadata,
):
    result = workflow_graph.invoke(
        initial_state,
        config=runnable_config(tags=trace_tags, metadata=trace_metadata),
    )
```

This snippet demonstrates that tracing is not only enabled by environment variables; it is also integrated into the execution path of the LangGraph workflow with meaningful tags and metadata.

### Figure 10 - LangSmith trace view
> Insert a screenshot from LangSmith here. Ideally the screenshot should show one workflow trace or interview trace, including run name, graph execution, or metadata/tags.

---

## 8. LangGraph and CrewAI Working Together

One of the assignment requirements is that LangGraph must be added to the existing project **alongside CrewAI**, and that both should work together without creating a new project.

This requirement is satisfied in InternIQ.

The architecture now contains:

- **CrewAI** for company research
- **LangGraph** for workflow orchestration and interview orchestration

This coexistence is meaningful, because both frameworks solve different problems:

| Framework | Role in InternIQ |
|-----------|------------------|
| **CrewAI** | Multi-agent company intelligence generation |
| **LangGraph** | Step-based, stateful application and interview flows |

This means the project demonstrates not just one AI integration, but a more realistic multi-framework architecture where each tool is used according to its strengths.

### Figure 11 - CrewAI company analysis still working
> Insert a screenshot of the Company Intel / CrewAI analysis screen here. This figure is important because it proves that LangGraph was added into the existing project without breaking the earlier CrewAI integration.

---

## 9. API Endpoints and Technical Structure

The LangGraph implementation is fully integrated into the backend API and exposed through documented FastAPI endpoints.

Main LangGraph-related endpoints:

- `POST /api/v1/workflow/prepare`
- `POST /api/v1/interview/lg/start`
- `POST /api/v1/interview/lg/answer`

These endpoints are accessible through FastAPI's automatically generated Swagger documentation, which helps both in development and presentation.

The key implementation files are:

### Application Workflow

- `backend/langgraph_workflow/state.py`
- `backend/langgraph_workflow/nodes.py`
- `backend/langgraph_workflow/graph.py`
- `backend/routers/workflow.py`
- `src/components/ApplicationWorkflow.jsx`

### Mock Interview

- `backend/langgraph_interview/state.py`
- `backend/langgraph_interview/nodes.py`
- `backend/langgraph_interview/graph.py`
- `backend/routers/interview.py`
- `src/components/MockInterview.jsx`

### LangSmith Tracing

- `backend/services/langsmith_tracing.py`

### Authentication / Profile Support

- `backend/routers/auth.py`
- `backend/services/profile_store.py`
- `src/pages/AccountPage.jsx`
- `src/context/AuthContext.jsx`

This structure makes the system easy to explain:

- router layer handles API requests,
- graph modules define the flow,
- node modules define the actual logic,
- frontend components render the results to the user.

### Figure 12 - FastAPI Swagger UI
> Insert a screenshot of the Swagger UI here. It should ideally show the LangGraph endpoints under the Interview and Workflow sections so that the backend integration is visible.

---

## 10. File Structure

```text
InternIQ/
├── backend/
│   ├── routers/
│   │   ├── workflow.py                # LangGraph application workflow endpoint
│   │   ├── interview.py               # LangGraph interview endpoints
│   │   ├── crew.py                    # CrewAI company research endpoint
│   │   └── auth.py                    # Authentication endpoints
│   ├── langgraph_workflow/
│   │   ├── state.py                   # WorkflowState definition
│   │   ├── nodes.py                   # Workflow nodes
│   │   └── graph.py                   # Workflow graph compile
│   ├── langgraph_interview/
│   │   ├── state.py                   # InterviewState definition
│   │   ├── nodes.py                   # Interview nodes
│   │   └── graph.py                   # Interview graphs compile
│   ├── services/
│   │   ├── profile_store.py           # CV profile extraction and storage
│   │   └── langsmith_tracing.py       # LangSmith tracing helper
│   ├── main.py                        # FastAPI app entry point
│   └── requirements.txt               # Includes langgraph, langsmith, crewai
├── src/
│   ├── components/
│   │   ├── ApplicationWorkflow.jsx    # Workflow UI
│   │   ├── MockInterview.jsx          # Interview UI
│   │   ├── CompanyCards.jsx           # CrewAI company cards
│   │   └── CVTailorer.jsx             # CV analysis UI
│   ├── pages/
│   │   ├── AccountPage.jsx            # Saved CV profile page
│   │   └── CompanyResearch.jsx        # CrewAI analysis result page
│   └── services/
│       └── api.js                     # Frontend API service layer
└── docs/
    └── LangGraph_Implementation_Report.md
```

---

## 11. Requirement-by-Requirement Checklist

To make the assignment coverage explicit:

### Requirement 1 - Include a LangGraph in your project
**Satisfied.** Two LangGraph implementations exist:

- Application Preparation Workflow
- AI Mock Interview

### Requirement 2 - Understand its purpose and implement it effectively
**Satisfied.** LangGraph is used in places where:

- state must be preserved,
- steps are clearly defined,
- conditional routing is needed,
- and multi-stage execution adds value.

### Requirement 3 - Commit your work to Git and share your Git account link
**Satisfied.**

- GitHub account: https://github.com/burakyalcin10
- Repository: https://github.com/burakyalcin10/InternIQ

### Requirement 4 - Be prepared to discuss implementation details in class
**Satisfied.** The implementation contains clearly explainable graphs, nodes, conditional edges, and tracing support.

### Requirement 5 - Make sure to have steps well defined
**Satisfied.** Both the workflow and interview graphs contain explicit, named steps.

### Requirement 6 - LangSmith integration is helpful
**Satisfied.** LangSmith tracing support has been added.

### Requirement 7 - Do not create a new project; add it into existing project alongside CrewAI and both should work
**Satisfied.** LangGraph and CrewAI coexist in the same InternIQ codebase and serve different modules.

### Requirement 8 - Submit a PDF report with screenshots and implemented features
**Satisfied after export.** This markdown report is prepared to be converted into PDF after inserting screenshots.

---

## 12. Conclusion

This assignment extends InternIQ with a meaningful LangGraph integration rather than a minimal demo. LangGraph is used in two different and realistic AI-driven modules: application preparation and mock interview. Both modules rely on clearly defined graph steps, shared state, and conditional transitions.

The project also strengthens the LangGraph integration with:

- account-based CV persistence,
- saved profile embedding,
- CrewAI coexistence,
- and LangSmith observability.

As a result, the implementation does not only fulfill the technical requirements of the assignment, but also improves the overall product quality of InternIQ by making the AI features more structured, personalized, and explainable.
