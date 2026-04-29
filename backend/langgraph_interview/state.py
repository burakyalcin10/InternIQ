"""
LangGraph Interview — State Definition

TypedDict-based state schema for the Mock Interview workflow.
Uses Annotated reducers so messages and scores accumulate across nodes.
"""

from typing import Annotated
from typing_extensions import TypedDict
import operator


class InterviewState(TypedDict):
    """Stateful mock interview workflow state."""

    # ── Context ──
    company: str
    position: str
    category: str  # "technical" | "behavioral"
    candidate_profile: dict
    session_seed: str

    # ── Conversation ──
    messages: Annotated[list, operator.add]  # [{role, content}, ...]
    asked_questions: Annotated[list, operator.add]
    current_question: str
    user_answer: str

    # ── Progress ──
    question_count: int
    target_questions: int
    max_questions: int
    question_limit: int
    scores: Annotated[list, operator.add]  # [int, ...]
    difficulty: str  # "easy" | "medium" | "hard"

    # ── Output ──
    feedback: str
    phase: str  # "start" | "questioning" | "completed"
    summary: str
