"""CV Router — CV Tailorer"""

import random
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CVAnalyzeRequest(BaseModel):
    job_description: str
    cv_text: str = ""


class Suggestion(BaseModel):
    icon: str
    text: str
    type: str  # success, warning, info


class CVAnalyzeResponse(BaseModel):
    score: int
    suggestions: list[Suggestion]


@router.post("/cv/analyze", response_model=CVAnalyzeResponse)
async def analyze_cv(request: CVAnalyzeRequest):
    """
    CV analizi yap — şu an simüle, CrewAI entegrasyonu sonra eklenecek.
    OpenAI API key geldiğinde gerçek analiz yapılacak.
    """
    # Simulated analysis — will be replaced with OpenAI/CrewAI
    score = random.randint(70, 95)

    suggestions = [
        Suggestion(
            icon="✅",
            text=f"Teknik becerilerin ilanla %{score} oranında eşleşiyor",
            type="success",
        ),
        Suggestion(
            icon="⚠️",
            text='"Docker" ve "Kubernetes" deneyimini eklemeyi düşün — ilanlarda sıkça aranıyor',
            type="warning",
        ),
        Suggestion(
            icon="💡",
            text="Proje açıklamalarında impact metriklerini belirt (ör: %30 performans artışı)",
            type="info",
        ),
        Suggestion(
            icon="📝",
            text="Summary bölümünü pozisyona özel yeniden yaz",
            type="info",
        ),
        Suggestion(
            icon="🎯",
            text="ATS uyumluluğu için standart bölüm başlıkları kullan",
            type="info",
        ),
    ]

    return CVAnalyzeResponse(score=score, suggestions=suggestions)
