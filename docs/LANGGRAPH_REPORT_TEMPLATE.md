# InternIQ LangGraph Assignment Report

## 1. Project Summary

InternIQ is an AI-powered internship preparation platform. The project already included CrewAI for company research, and this assignment extends the same project with LangGraph-based workflows without creating a new project.

## 2. Assignment Goals

- Add LangGraph into the existing project
- Define workflow steps clearly
- Keep CrewAI and LangGraph working side by side
- Make the implementation discussable in class
- Optionally support LangSmith tracing

## 3. LangGraph Purpose In This Project

LangGraph is used for stateful, step-based orchestration.

### 3.1 Mock Interview Graph

Purpose:
To manage a multi-turn interview session where the system remembers previous answers, adjusts difficulty, and generates either a next question or a final summary.

Main nodes:

1. `generate_question`
2. `evaluate_answer`
3. `adjust_difficulty`
4. `check_progress`
5. `generate_summary`

### 3.2 Application Preparation Workflow

Purpose:
To create a structured internship preparation pipeline for a selected job listing.

Main nodes:

1. `analyze_listing`
2. `evaluate_cv`
3. `check_cv_score`
4. `suggest_improvements`
5. `research_company`
6. `generate_interview_prep`
7. `create_action_plan`

## 4. CrewAI And LangGraph Together

This project contains both frameworks in the same codebase:

- CrewAI is used for company intelligence research
- LangGraph is used for stateful interview and preparation workflows

Why both are used:

- CrewAI is better for multi-agent collaboration
- LangGraph is better for explicit step orchestration and state transitions

## 5. Implemented Features

### 5.1 LangGraph Mock Interview

- AI interview start endpoint
- Session-based answer evaluation
- Dynamic difficulty update
- Final summary generation

### 5.2 LangGraph Application Workflow

- Internship listing selection
- CV analysis against selected listing
- Conditional improvement suggestions
- Company info aggregation
- Interview preparation questions
- Personalized action plan
- Visible workflow steps in the UI

### 5.3 Stability Improvements

- Fixed API error handling for missing listings/companies
- Fixed CrewAI fallback response shape for frontend compatibility
- Improved company name matching in workflow research
- Added workflow step metadata to API responses

## 6. LangSmith Note

LangSmith tracing can be enabled with environment variables such as:

- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_API_KEY=...`
- `LANGCHAIN_PROJECT=InternIQ`

This helps observe LangGraph execution and debug node transitions.

## 7. Screenshots

Add screenshots here:

1. Features page showing LangGraph workflow section
2. Workflow input screen with listing selection
3. Workflow result screen showing graph steps and action plan
4. Mock Interview LangGraph mode
5. CrewAI company analysis screen

## 8. Technical Files

Relevant files:

- `backend/langgraph_interview/graph.py`
- `backend/langgraph_interview/nodes.py`
- `backend/langgraph_workflow/graph.py`
- `backend/langgraph_workflow/nodes.py`
- `backend/routers/interview.py`
- `backend/routers/workflow.py`
- `backend/routers/crew.py`
- `src/components/MockInterview.jsx`
- `src/components/ApplicationWorkflow.jsx`

## 9. Verification

Completed checks:

- `npm run build`
- `npm run lint`
- Python syntax validation for LangGraph and router modules

## 10. Conclusion

LangGraph was integrated into the existing InternIQ project successfully. The project now demonstrates both CrewAI and LangGraph in different but complementary roles, with clearly defined steps and user-facing workflow outputs.
