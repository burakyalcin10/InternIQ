"""
Interview Router — Mock Interview

Two modes:
  1. Basic endpoints (/interview/ask, /interview/evaluate) — original rule-based
  2. LangGraph endpoints (/interview/lg/*) — AI-powered stateful interview
"""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.langsmith_tracing import get_langsmith_project, runnable_config, tracing_context

router = APIRouter()

# ════════════════════════════════════════════════════════════
#  BASIC MODE — Original rule-based (kept for backward compat)
# ════════════════════════════════════════════════════════════

QUESTIONS = {
    "technical": [
        {"question": "REST API ile GraphQL arasındaki temel farklar nelerdir?", "category": "Backend", "difficulty": "Medium"},
        {"question": "Big-O notation nedir? Binary search'ün time complexity'sini açıklayın.", "category": "Algorithms", "difficulty": "Easy"},
        {"question": "React'te Virtual DOM nasıl çalışır?", "category": "Frontend", "difficulty": "Medium"},
        {"question": "Bir e-ticaret sitesinin veritabanı şemasını nasıl tasarlarsınız?", "category": "Database", "difficulty": "Hard"},
        {"question": "CI/CD pipeline nedir? Nasıl kurarsınız?", "category": "DevOps", "difficulty": "Medium"},
    ],
    "behavioral": [
        {"question": "Bir takım projesinde anlaşmazlık yaşadığınız bir durumu anlatın.", "category": "Teamwork", "difficulty": "Easy"},
        {"question": "Deadline baskısı altında kalite ve hız arasında nasıl denge kurarsınız?", "category": "Time Mgmt", "difficulty": "Medium"},
        {"question": "Başarısızlıkla sonuçlanan bir projenizden ne öğrendiniz?", "category": "Reflection", "difficulty": "Easy"},
    ],
}


class AskRequest(BaseModel):
    category: str = "technical"
    question_index: int = 0


class EvaluateRequest(BaseModel):
    question: str
    answer: str


@router.post("/interview/ask")
async def ask_question(request: AskRequest):
    """Mülakat sorusu getir."""
    category = request.category if request.category in QUESTIONS else "technical"
    questions = QUESTIONS[category]

    if request.question_index >= len(questions):
        return {"done": True, "message": "Tüm soruları tamamladınız!"}

    q = questions[request.question_index]
    return {
        "done": False,
        "question": q["question"],
        "category": q["category"],
        "difficulty": q["difficulty"],
        "current": request.question_index + 1,
        "total": len(questions),
    }


@router.post("/interview/evaluate")
async def evaluate_answer(request: EvaluateRequest):
    """
    Cevabı değerlendir — simüle, sonra AI ile yapılacak.
    """
    answer_len = len(request.answer)

    if answer_len < 20:
        feedback = "Cevabınız çok kısa. Daha detaylı yanıt bekleniyor."
        score = 30
    elif answer_len < 80:
        feedback = "İyi bir başlangıç. Somut bir proje deneyimiyle desteklerseniz daha güçlü olur."
        score = 60
    else:
        feedback = "Kapsamlı ve detaylı bir cevap. Mülakatta da bu netlikte ifade ederseniz güçlü bir izlenim bırakırsınız."
        score = 85

    return {"feedback": feedback, "score": score}


# ════════════════════════════════════════════════════════════
#  LANGGRAPH MODE — AI-powered stateful interview
# ════════════════════════════════════════════════════════════

from langgraph_interview.graph import question_graph, answer_graph

# In-memory session store (production would use Redis)
_sessions: dict = {}


class LGStartRequest(BaseModel):
    company: str = "Genel"
    position: str = "Yazılım Mühendisi Stajyeri"
    category: str = "technical"
    max_questions: int = 5
    candidate_profile: dict = Field(default_factory=dict)


class LGAnswerRequest(BaseModel):
    session_id: str
    answer: str


@router.post("/interview/lg/start")
async def lg_start_interview(req: LGStartRequest):
    """
    Start a LangGraph-powered interview session.

    Creates a session, runs the question_graph to generate
    the first question, and returns the session_id + question.

    Graph: START → generate_question → END
    """
    session_id = str(uuid.uuid4())
    target_questions = max(3, min(req.max_questions, 8))

    initial_state = {
        "company": req.company,
        "position": req.position,
        "category": req.category,
        "candidate_profile": req.candidate_profile,
        "session_seed": session_id[:8],
        "messages": [],
        "asked_questions": [],
        "current_question": "",
        "user_answer": "",
        "question_count": 0,
        "target_questions": target_questions,
        "max_questions": target_questions,
        "question_limit": min(target_questions + 2, 8),
        "scores": [],
        "difficulty": "medium",
        "feedback": "",
        "phase": "start",
        "summary": "",
    }

    trace_tags = ["langgraph", "interview", "start"]
    trace_metadata = {
        "company": req.company,
        "position": req.position,
        "category": req.category,
        "max_questions": target_questions,
        "has_candidate_profile": bool(req.candidate_profile),
    }

    with tracing_context(
        project_name=get_langsmith_project("InternIQ-Interview"),
        tags=trace_tags,
        metadata=trace_metadata,
    ):
        result = question_graph.invoke(
            initial_state,
            config=runnable_config(tags=trace_tags, metadata=trace_metadata),
        )

    # Save session
    _sessions[session_id] = result

    return {
        "session_id": session_id,
        "question": result["current_question"],
        "question_number": result["question_count"],
        "total_questions": result["max_questions"],
        "difficulty": result["difficulty"],
        "phase": result["phase"],
        "mode": "langgraph",
    }


@router.post("/interview/lg/answer")
async def lg_answer_question(req: LGAnswerRequest):
    """
    Submit an answer to the current interview question.

    Runs the answer_graph which:
      1. evaluate_answer   — AI scores the answer
      2. adjust_difficulty  — Raises/lowers difficulty
      3. check_progress     — ROUTER: continue or done?
      4a. generate_question — Next question (if continuing)
      4b. generate_summary  — Final report (if done)

    Returns feedback + next question (or summary).
    """
    session = _sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found. Start a new interview."}

    # Update state with user's answer
    session["user_answer"] = req.answer

    trace_tags = ["langgraph", "interview", "answer"]
    trace_metadata = {
        "session_id": req.session_id,
        "question_count": session.get("question_count", 0),
        "difficulty": session.get("difficulty", "medium"),
        "phase": session.get("phase", "questioning"),
    }

    with tracing_context(
        project_name=get_langsmith_project("InternIQ-Interview"),
        tags=trace_tags,
        metadata=trace_metadata,
    ):
        result = answer_graph.invoke(
            session,
            config=runnable_config(tags=trace_tags, metadata=trace_metadata),
        )

    # Save updated session
    _sessions[req.session_id] = result

    response = {
        "session_id": req.session_id,
        "feedback": result.get("feedback", ""),
        "score": result["scores"][-1] if result.get("scores") else 0,
        "difficulty": result.get("difficulty", "medium"),
        "phase": result.get("phase", "questioning"),
        "mode": "langgraph",
    }

    if result.get("phase") == "completed":
        # Interview finished
        response["summary"] = result.get("summary", "")
        response["scores"] = result.get("scores", [])
        response["average_score"] = (
            sum(result["scores"]) / len(result["scores"])
            if result.get("scores")
            else 0
        )
        response["total_questions"] = len(result.get("scores", []))
        # Clean up session
        del _sessions[req.session_id]
    else:
        # Next question
        response["question"] = result.get("current_question", "")
        response["question_number"] = result.get("question_count", 0)
        response["total_questions"] = result.get("max_questions", 5)

    return response
