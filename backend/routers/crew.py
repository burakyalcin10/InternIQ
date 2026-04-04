"""Crew Router — AI-Powered Company Research via CrewAI"""

from fastapi import APIRouter
from pydantic import BaseModel

from crew.company_crew import run_crew

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
    result = run_crew(req.company_name)
    return result
