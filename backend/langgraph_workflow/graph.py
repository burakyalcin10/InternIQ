"""
LangGraph Workflow — Graph Definition

Application Preparation Workflow: a multi-step graph that orchestrates
listing analysis, CV evaluation, company research, and interview prep
into a personalized action plan.

Graph topology:

  START → analyze_listing → evaluate_cv → [check_cv_score]
                                            ├─ "needs_improvement" → suggest_improvements → research_company
                                            └─ "good_fit" ─────────────────────────────────→ research_company
          research_company → generate_interview_prep → create_action_plan → END
"""

from langgraph.graph import StateGraph, START, END

from .state import WorkflowState
from .nodes import (
    analyze_listing,
    evaluate_cv,
    check_cv_score,
    suggest_improvements,
    research_company,
    generate_interview_prep,
    create_action_plan,
)


def build_workflow_graph():
    """
    Build the Application Preparation Workflow graph.

    7 nodes, 1 conditional edge (CV score check).
    Demonstrates LangGraph orchestrating multiple AI services
    into a unified preparation pipeline.
    """
    builder = StateGraph(WorkflowState)

    # ── Add all nodes ──
    builder.add_node("analyze_listing", analyze_listing)
    builder.add_node("evaluate_cv", evaluate_cv)
    builder.add_node("suggest_improvements", suggest_improvements)
    builder.add_node("research_company", research_company)
    builder.add_node("generate_interview_prep", generate_interview_prep)
    builder.add_node("create_action_plan", create_action_plan)

    # ── Linear edges ──
    builder.add_edge(START, "analyze_listing")
    builder.add_edge("analyze_listing", "evaluate_cv")

    # ── Conditional edge: CV score routing ──
    builder.add_conditional_edges(
        "evaluate_cv",
        check_cv_score,
        {
            "needs_improvement": "suggest_improvements",
            "good_fit": "research_company",
        },
    )

    # ── Converge paths ──
    builder.add_edge("suggest_improvements", "research_company")
    builder.add_edge("research_company", "generate_interview_prep")
    builder.add_edge("generate_interview_prep", "create_action_plan")
    builder.add_edge("create_action_plan", END)

    return builder.compile()


# ── Pre-compiled graph ──
workflow_graph = build_workflow_graph()
