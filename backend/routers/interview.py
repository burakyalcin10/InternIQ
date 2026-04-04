"""Interview Router — Mock Interview"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

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
