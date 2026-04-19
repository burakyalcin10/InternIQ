"""
LangGraph Workflow — State Definition

State schema for the Application Preparation Workflow.
Tracks listing analysis, CV evaluation, company research,
interview prep, and final action plan across graph nodes.
"""

from typing_extensions import TypedDict


class WorkflowState(TypedDict):
    """Application preparation workflow state."""

    # ── Input ──
    listing_id: int
    cv_text: str

    # ── Listing Analysis ──
    listing_data: dict
    job_requirements: list
    job_description: str

    # ── CV Evaluation ──
    cv_score: int
    cv_analysis: dict
    needs_improvement: bool
    cv_suggestions: list

    # ── Company Research ──
    company_name: str
    company_info: dict

    # ── Interview Prep ──
    interview_questions: list

    # ── Final Output ──
    action_plan: dict
    status: str  # "ai" | "fallback"
