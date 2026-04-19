"""Workflow Router — LangGraph Application Preparation Workflow"""

from fastapi import APIRouter
from pydantic import BaseModel

from langgraph_workflow.graph import workflow_graph

router = APIRouter()


class PrepareRequest(BaseModel):
    listing_id: int
    cv_text: str = ""


@router.post("/workflow/prepare")
async def prepare_application(req: PrepareRequest):
    """
    Run the LangGraph Application Preparation Workflow.

    This orchestrates 7 steps through a stateful graph:
      1. analyze_listing → Parse listing requirements
      2. evaluate_cv → Score CV against listing
      3. [conditional] suggest_improvements → CV tips (if score < 70)
      4. research_company → Company intelligence
      5. generate_interview_prep → Company-specific questions
      6. create_action_plan → Personalized action plan

    Returns a comprehensive preparation report.
    """
    initial_state = {
        "listing_id": req.listing_id,
        "cv_text": req.cv_text,
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
        "action_plan": {},
        "status": "fallback",
    }

    result = workflow_graph.invoke(initial_state)

    return {
        "listing": {
            "id": result.get("listing_data", {}).get("id"),
            "position": result.get("listing_data", {}).get("position"),
            "company": result.get("company_name"),
        },
        "cv_analysis": result.get("cv_analysis", {}),
        "cv_score": result.get("cv_score", 0),
        "cv_suggestions": result.get("cv_suggestions", []),
        "company_info": result.get("company_info", {}),
        "interview_questions": result.get("interview_questions", []),
        "action_plan": result.get("action_plan", {}),
        "status": result.get("status", "fallback"),
    }
