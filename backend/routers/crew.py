"""Crew Router — AI-Powered Company Research via CrewAI"""

from fastapi import APIRouter
from pydantic import BaseModel

# CrewAI requires Python < 3.14 — graceful fallback for local dev
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

    Falls back to pre-built reports when OPENAI_API_KEY is not set.
    """
    if not CREWAI_AVAILABLE:
        return {
            "status": "fallback",
            "message": "CrewAI is not available in this environment (requires Python < 3.14). Works on Render deployment.",
            "company_summary": f"{req.company_name} hakkında araştırma",
            "culture": "CrewAI bu Python sürümünde kullanılamıyor. Render deployment'ta çalışır.",
            "tech_stack": [],
            "interview_tips": "Lütfen deploy edilmiş versiyonu kullanın.",
            "pros": [],
            "cons": [],
            "overall_rating": "N/A",
            "recommendation": "Deploy edilen versiyonda CrewAI tam olarak çalışmaktadır."
        }
    result = run_crew(req.company_name)
    return result
