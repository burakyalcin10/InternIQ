"""Crew Router - AI-powered company research via CrewAI."""

from fastapi import APIRouter
from pydantic import BaseModel

# CrewAI requires Python < 3.14 - graceful fallback for local dev
try:
    from crew.company_crew import run_crew

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    run_crew = None

router = APIRouter()


class CompanyResearchRequest(BaseModel):
    company_name: str


@router.post("/crew/research")
async def research_company(req: CompanyResearchRequest):
    """
    Kick off the CrewAI company research crew.

    3 agents (Culture Researcher, Tech Analyst, Report Writer) collaborate
    sequentially to produce a comprehensive company intelligence report.

    Falls back to a UI-compatible report shape when CrewAI is unavailable.
    """
    if not CREWAI_AVAILABLE:
        fallback_report = {
            "company_summary": f"{req.company_name} hakkinda arastirma",
            "culture": "CrewAI bu Python surumunde kullanilamiyor. Render deployment'ta calisir.",
            "tech_stack": [],
            "interview_tips": ["Lutfen deploy edilmis versiyonu kullanin."],
            "pros": [],
            "cons": [],
            "overall_rating": "N/A",
            "recommendation": "Deploy edilen versiyonda CrewAI tam olarak calismaktadir.",
        }
        return {
            "status": "fallback",
            "company": req.company_name,
            "report": fallback_report,
            "message": "CrewAI is not available in this environment (requires Python < 3.14). Works on Render deployment.",
        }

    result = run_crew(req.company_name)
    return result
