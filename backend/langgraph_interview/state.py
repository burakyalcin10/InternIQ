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

    # ── Conversation ──
    messages: Annotated[list, operator.add]  # [{role, content}, ...]
    current_question: str
    user_answer: str

    # ── Progress ──
    question_count: int
    max_questions: int
    scores: Annotated[list, operator.add]  # [int, ...]
    difficulty: str  # "easy" | "medium" | "hard"

    # ── Output ──
    feedback: str
    phase: str  # "start" | "questioning" | "completed"
    summary: str
