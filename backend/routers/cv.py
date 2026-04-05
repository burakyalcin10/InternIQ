"""CV Router — CV Tailorer with PDF Upload + Gemini AI Analysis"""

import os
import json
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from PyPDF2 import PdfReader
import io

router = APIRouter()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def analyze_with_gemini(cv_text: str, job_description: str) -> dict:
    """Use Google Gemini to analyze CV against job description."""
    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key or api_key == "your_gemini_key_here":
        return get_fallback_analysis(cv_text, job_description)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""Sen bir kariyer danışmanı ve CV uzmanısın. Aşağıdaki CV'yi ve iş ilanı açıklamasını analiz et.

CV İÇERİĞİ:
{cv_text[:3000]}

İLAN AÇIKLAMASI:
{job_description[:2000]}

Lütfen aşağıdaki JSON formatında yanıt ver (sadece JSON, başka bir şey yazma):
{{
    "score": <0-100 arası ATS uyumluluk skoru>,
    "matched_keywords": ["eşleşen anahtar kelime 1", "eşleşen anahtar kelime 2", ...],
    "missing_keywords": ["eksik anahtar kelime 1", "eksik anahtar kelime 2", ...],
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

        # Clean markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        result = json.loads(response_text)
        result["status"] = "ai"
        return result

    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return get_fallback_analysis(cv_text, job_description)


def get_fallback_analysis(cv_text: str, job_description: str) -> dict:
    """Fallback analysis when no API key is available."""
    # Simple keyword matching
    jd_lower = job_description.lower()
    cv_lower = cv_text.lower() if cv_text else ""

    common_skills = [
        "python", "java", "javascript", "react", "node.js", "sql", "docker",
        "kubernetes", "git", "c++", "c#", "html", "css", "typescript",
        "aws", "azure", "linux", "mongodb", "postgresql", "rest api",
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "agile", "scrum", "ci/cd", "microservices"
    ]

    matched = [s for s in common_skills if s in jd_lower and s in cv_lower]
    missing = [s for s in common_skills if s in jd_lower and s not in cv_lower]

    total_relevant = len(matched) + len(missing)
    score = int((len(matched) / max(total_relevant, 1)) * 100) if total_relevant > 0 else 65

    # Ensure score is reasonable
    score = max(40, min(95, score))

    suggestions = []
    if matched:
        suggestions.append({
            "icon": "✅",
            "text": f"Eşleşen teknik beceriler: {', '.join(matched[:5])}",
            "type": "success"
        })

    if missing:
        suggestions.append({
            "icon": "⚠️",
            "text": f"İlanda aranan ama CV'de eksik: {', '.join(missing[:4])}",
            "type": "warning"
        })

    suggestions.extend([
        {
            "icon": "💡",
            "text": "Proje açıklamalarında somut metrikler belirtin (ör: '%30 performans artışı')",
            "type": "info"
        },
        {
            "icon": "📝",
            "text": "Summary bölümünü her iş ilanına özel yeniden yazın",
            "type": "info"
        },
        {
            "icon": "🎯",
            "text": "ATS uyumluluğu için standart bölüm başlıkları kullanın (Education, Experience, Skills)",
            "type": "info"
        },
    ])

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "summary": f"CV'niz ilana %{score} oranında uyumludur. {len(matched)} anahtar beceri eşleşti, {len(missing)} beceri eksik.",
        "status": "fallback"
    }


@router.post("/cv/analyze")
async def analyze_cv(
    job_description: str = Form(...),
    cv_file: UploadFile = File(None),
    cv_text: str = Form(""),
):
    """
    CV analizi — PDF upload veya metin olarak CV kabul eder.
    Gemini API varsa AI analizi, yoksa keyword-based fallback.
    """
    # Extract CV text from PDF or use provided text
    extracted_cv_text = cv_text

    if cv_file and cv_file.filename:
        file_bytes = await cv_file.read()
        if cv_file.filename.lower().endswith(".pdf"):
            extracted_cv_text = extract_text_from_pdf(file_bytes)
        else:
            extracted_cv_text = file_bytes.decode("utf-8", errors="ignore")

    if not extracted_cv_text.strip():
        extracted_cv_text = "(CV metni sağlanmadı)"

    result = analyze_with_gemini(extracted_cv_text, job_description)

    return result
