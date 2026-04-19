"""CV router for PDF upload and CV analysis."""

import io
import json
import os

from fastapi import APIRouter, File, Form, Header, UploadFile
from PyPDF2 import PdfReader

from services.profile_store import clean_extracted_cv_text, get_profile
from services.supabase_auth import get_authenticated_user

router = APIRouter()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file and clean common encoding noise."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return clean_extracted_cv_text(text)


def analyze_with_gemini(cv_text: str, job_description: str) -> dict:
    """Use Google Gemini to analyze CV against job description."""
    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key or api_key == "your_gemini_key_here":
        return get_fallback_analysis(cv_text, job_description)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""Sen bir kariyer danışmanı ve CV uzmanısın. Aşağıdaki CV'yi ve iş ilanı açıklamasını analiz et.

CV İÇERİĞİ:
{cv_text[:3000]}

İLAN AÇIKLAMASI:
{job_description[:2000]}

Lütfen aşağıdaki JSON formatında yanıt ver (sadece JSON, başka bir şey yazma):
{{
    "score": <0-100 arası ATS uyumluluk skoru>,
    "matched_keywords": ["eşleşen anahtar kelime 1", "eşleşen anahtar kelime 2"],
    "missing_keywords": ["eksik anahtar kelime 1", "eksik anahtar kelime 2"],
    "suggestions": [
        {{"icon": "✅", "text": "<olumlu yorum>", "type": "success"}},
        {{"icon": "⚠️", "text": "<uyarı/eksik>", "type": "warning"}},
        {{"icon": "💡", "text": "<öneri>", "type": "info"}}
    ],
    "summary": "<CV'nin ilana ne kadar uygun olduğuna dair 2-3 cümlelik Türkçe özet>"
}}

En az 5 suggestion ver. Türkçe yaz."""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        result = json.loads(response_text)
        result["status"] = "ai"
        return result

    except Exception as exc:
        print(f"[Gemini] Error: {exc}")
        return get_fallback_analysis(cv_text, job_description)


def get_fallback_analysis(cv_text: str, job_description: str) -> dict:
    """Fallback analysis when no API key is available."""
    jd_lower = job_description.lower()
    cv_lower = cv_text.lower() if cv_text else ""

    common_skills = [
        "python",
        "java",
        "javascript",
        "react",
        "node.js",
        "sql",
        "docker",
        "kubernetes",
        "git",
        "c++",
        "c#",
        "html",
        "css",
        "typescript",
        "aws",
        "azure",
        "linux",
        "mongodb",
        "postgresql",
        "rest api",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "agile",
        "scrum",
        "ci/cd",
        "microservices",
    ]

    matched = [skill for skill in common_skills if skill in jd_lower and skill in cv_lower]
    missing = [skill for skill in common_skills if skill in jd_lower and skill not in cv_lower]

    total_relevant = len(matched) + len(missing)
    score = int((len(matched) / max(total_relevant, 1)) * 100) if total_relevant > 0 else 65
    score = max(40, min(95, score))

    suggestions = []
    if matched:
        suggestions.append(
            {
                "icon": "✅",
                "text": f"Eşleşen teknik beceriler: {', '.join(matched[:5])}",
                "type": "success",
            }
        )

    if missing:
        suggestions.append(
            {
                "icon": "⚠️",
                "text": f"İlanda aranan ama CV'de eksik: {', '.join(missing[:4])}",
                "type": "warning",
            }
        )

    suggestions.extend(
        [
            {
                "icon": "💡",
                "text": "Proje açıklamalarında somut metrikler belirtin (ör: '%30 performans artışı').",
                "type": "info",
            },
            {
                "icon": "📝",
                "text": "Özet bölümünü her iş ilanına özel yeniden yazın.",
                "type": "info",
            },
            {
                "icon": "🎯",
                "text": "ATS uyumluluğu için standart bölüm başlıkları kullanın (Education, Experience, Skills).",
                "type": "info",
            },
        ]
    )

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "summary": f"CV'niz ilana %{score} oranında uyumludur. {len(matched)} anahtar beceri eşleşti, {len(missing)} beceri eksik.",
        "status": "fallback",
    }


@router.post("/cv/analyze")
async def analyze_cv(
    job_description: str = Form(...),
    cv_file: UploadFile | None = File(default=None),
    cv_text: str = Form(default=""),
    authorization: str | None = Header(default=None),
):
    """
    CV analizi — PDF upload veya metin olarak CV kabul eder.
    Kullanıcı giriş yaptıysa ve yeni CV göndermediyse kayıtlı CV'yi kullanır.
    """
    extracted_cv_text = cv_text
    cv_source = "manual"

    if cv_file and cv_file.filename:
        file_bytes = await cv_file.read()
        if cv_file.filename.lower().endswith(".pdf"):
            extracted_cv_text = extract_text_from_pdf(file_bytes)
        else:
            extracted_cv_text = clean_extracted_cv_text(file_bytes.decode("utf-8", errors="ignore"))
    elif not extracted_cv_text.strip():
        user = get_authenticated_user(authorization)
        profile = get_profile(str(user.id)) if user else None
        saved_cv = profile.get("cv_text", "") if profile else ""
        if saved_cv.strip():
            extracted_cv_text = saved_cv
            cv_source = "profile"

    if not extracted_cv_text.strip():
        extracted_cv_text = "(CV metni sağlanmadı)"
        cv_source = "empty"

    result = analyze_with_gemini(clean_extracted_cv_text(extracted_cv_text), job_description)
    result["cv_source"] = cv_source
    return result
