"""
LangGraph Interview — Graph Definition

Two compiled graphs:
  question_graph — Generates the first/next interview question
  answer_graph   — Evaluates answer → adjusts difficulty → continues or summarizes

Graph topology (answer_graph):

  START → evaluate_answer → adjust_difficulty ─┬─ "continue" → generate_question → END
                                                └─ "done"     → generate_summary  → END
"""

from langgraph.graph import StateGraph, START, END

from .state import InterviewState
from .nodes import (
    generate_question,
    evaluate_answer,
    adjust_difficulty,
    check_progress,
    generate_summary,
)


def build_question_graph():
    """Single-node graph: generates a question and returns."""
    builder = StateGraph(InterviewState)
    builder.add_node("generate_question", generate_question)
    builder.add_edge(START, "generate_question")
    builder.add_edge("generate_question", END)
    return builder.compile()


def build_answer_graph():
    """
    Multi-step graph with conditional branching.

    Steps:
      1. evaluate_answer   — Score the user's answer
      2. adjust_difficulty  — Raise/lower difficulty based on performance
      3. check_progress     — ROUTER: continue asking or finish?
      4a. generate_question — Next question (if continuing)
      4b. generate_summary  — Final report (if done)
    """
    builder = StateGraph(InterviewState)

    # ── Add nodes ──
    builder.add_node("evaluate_answer", evaluate_answer)
    builder.add_node("adjust_difficulty", adjust_difficulty)
    builder.add_node("generate_question", generate_question)
    builder.add_node("generate_summary", generate_summary)

    # ── Linear edges ──
    builder.add_edge(START, "evaluate_answer")
    builder.add_edge("evaluate_answer", "adjust_difficulty")

    # ── Conditional edge: continue or done ──
    builder.add_conditional_edges(
        "adjust_difficulty",
        check_progress,
        {
            "continue": "generate_question",
            "done": "generate_summary",
        },
    )

    # ── Terminal edges ──
    builder.add_edge("generate_question", END)
    builder.add_edge("generate_summary", END)

    return builder.compile()


# ── Pre-compiled graphs (import-ready) ──
question_graph = build_question_graph()
answer_graph = build_answer_graph()
