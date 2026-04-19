"""Workflow Router - LangGraph application preparation workflow."""

from fastapi import APIRouter, Header
from pydantic import BaseModel

from langgraph_workflow.graph import workflow_graph
from services.profile_store import get_profile, summarize_cv_profile
from services.supabase_auth import get_authenticated_user

router = APIRouter()

WORKFLOW_STEPS = [
    {"id": "analyze_listing", "title": "İlan Analizi"},
    {"id": "evaluate_cv", "title": "CV Değerlendirme"},
    {"id": "check_cv_score", "title": "CV Skor Kontrolü"},
    {"id": "suggest_improvements", "title": "CV İyileştirme Önerileri"},
    {"id": "research_company", "title": "Şirket Araştırması"},
    {"id": "generate_interview_prep", "title": "Mülakat Hazırlığı"},
    {"id": "create_action_plan", "title": "Aksiyon Planı"},
]


class PrepareRequest(BaseModel):
    listing_id: int
    cv_text: str = ""


@router.post("/workflow/prepare")
async def prepare_application(
    req: PrepareRequest,
    authorization: str | None = Header(default=None),
):
    """
    Run the LangGraph application preparation workflow.

    This orchestrates 7 steps through a stateful graph:
      1. analyze_listing -> Parse listing requirements
      2. evaluate_cv -> Score CV against listing
      3. [conditional] suggest_improvements -> CV tips (if score < 70)
      4. research_company -> Company intelligence
      5. generate_interview_prep -> Company-specific questions
      6. create_action_plan -> Personalized action plan
    """
    cv_text = req.cv_text.strip()
    cv_source = "manual"
    profile = None

    if not cv_text:
        user = get_authenticated_user(authorization)
        profile = get_profile(str(user.id)) if user else None
        saved_cv = profile.get("cv_text", "") if profile else ""
        if saved_cv.strip():
            cv_text = saved_cv
            cv_source = "profile"
        else:
            cv_source = "empty"

    if profile and cv_source == "profile":
        candidate_profile = {
            "summary": profile.get("summary", ""),
            "skills": profile.get("skills", []),
            "education_summary": profile.get("education_summary", ""),
            "experience_level": profile.get("experience_level", ""),
            "projects": profile.get("projects", []),
        }
    elif cv_text.strip():
        derived = summarize_cv_profile(cv_text)
        candidate_profile = {
            "summary": derived.get("summary", ""),
            "skills": derived.get("skills", []),
            "education_summary": derived.get("education_summary", ""),
            "experience_level": derived.get("experience_level", ""),
            "projects": derived.get("projects", []),
        }
    else:
        candidate_profile = {
            "summary": "",
            "skills": [],
            "education_summary": "",
            "experience_level": "",
            "projects": [],
        }

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
    final_status = result.get("status", "fallback")
    final_provider = result.get("llm_provider", "fallback") if final_status == "ai" else "fallback"

    return {
        "listing": {
            "id": result.get("listing_data", {}).get("id"),
            "position": result.get("listing_data", {}).get("position"),
            "company": result.get("company_name"),
        },
        "workflow_steps": WORKFLOW_STEPS,
        "cv_analysis": result.get("cv_analysis", {}),
        "cv_score": result.get("cv_score", 0),
        "cv_suggestions": result.get("cv_suggestions", []),
        "company_info": result.get("company_info", {}),
        "interview_questions": result.get("interview_questions", []),
        "interview_sections": result.get("interview_sections", {}),
        "action_plan": result.get("action_plan", {}),
        "status": final_status,
        "llm_provider": final_provider,
        "cv_source": cv_source,
    }
