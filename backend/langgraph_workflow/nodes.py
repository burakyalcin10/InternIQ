"""
LangGraph Workflow — Node Functions

Six nodes for the Application Preparation Workflow:
  1. analyze_listing        — Parse listing, extract requirements
  2. evaluate_cv            — Score CV against the listing
  3. check_cv_score         — Router: needs improvement or good fit
  4. suggest_improvements   — Generate CV improvement suggestions
  5. research_company       — Gather company intelligence
  6. generate_interview_prep — Create company-specific interview questions
  7. create_action_plan     — Synthesize everything into final plan
"""

import os
import json
from pathlib import Path

LISTINGS_PATH = Path(__file__).parent.parent / "data" / "listings.json"
COMPANIES_PATH = Path(__file__).parent.parent / "data" / "companies.json"


def get_llm():
    """Return a ChatOpenAI instance, or None if no API key."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_key_here":
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=1024)


# ════════════════════════════════════════════════════════════
#  NODE 1 — Analyze Listing
# ════════════════════════════════════════════════════════════

def analyze_listing(state: dict) -> dict:
    """Load listing data and extract key requirements."""
    listing_id = state.get("listing_id", 1)

    # Load listing from JSON
    with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
        listings = json.load(f)

    listing = next((l for l in listings if l["id"] == listing_id), None)
    if not listing:
        listing = listings[0] if listings else {}

    # Extract requirements
    requirements = listing.get("requirements", [])
    tags = listing.get("tags", [])
    description = listing.get("description", "")

    return {
        "listing_data": listing,
        "job_requirements": requirements + tags,
        "job_description": description,
        "company_name": listing.get("company", "Bilinmeyen"),
    }


# ════════════════════════════════════════════════════════════
#  NODE 2 — Evaluate CV
# ════════════════════════════════════════════════════════════

def evaluate_cv(state: dict) -> dict:
    """Evaluate CV against job listing using LLM or keyword matching."""
    llm = get_llm()
    cv_text = state.get("cv_text", "")
    job_desc = state.get("job_description", "")
    requirements = state.get("job_requirements", [])
    company = state.get("company_name", "")

    if not cv_text.strip():
        cv_text = "(CV metni sağlanmadı)"

    if not llm:
        return _fallback_cv_eval(cv_text, requirements)

    prompt = (
        f"Sen bir kariyer danışmanısın. Aşağıdaki CV'yi iş ilanıyla karşılaştır.\n\n"
        f"Şirket: {company}\n"
        f"İlan Gereksinimleri: {', '.join(requirements[:10])}\n"
        f"İlan Açıklaması: {job_desc[:1000]}\n\n"
        f"CV: {cv_text[:2000]}\n\n"
        f"JSON formatında yanıt ver (sadece JSON):\n"
        f'{{\n'
        f'  "score": <0-100>,\n'
        f'  "matched_skills": ["eşleşen1", "eşleşen2"],\n'
        f'  "missing_skills": ["eksik1", "eksik2"],\n'
        f'  "summary": "<2 cümle Türkçe özet>"\n'
        f'}}'
    )

    response = llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    try:
        result = json.loads(text.strip())
    except json.JSONDecodeError:
        return _fallback_cv_eval(cv_text, requirements)

    score = result.get("score", 65)

    return {
        "cv_score": score,
        "cv_analysis": result,
        "needs_improvement": score < 70,
        "status": "ai",
    }


# ════════════════════════════════════════════════════════════
#  NODE 3 — Check CV Score (Router)
# ════════════════════════════════════════════════════════════

def check_cv_score(state: dict) -> str:
    """Router: if CV score < 70, suggest improvements first."""
    if state.get("needs_improvement", False):
        return "needs_improvement"
    return "good_fit"


# ════════════════════════════════════════════════════════════
#  NODE 4 — Suggest Improvements
# ════════════════════════════════════════════════════════════

def suggest_improvements(state: dict) -> dict:
    """Generate CV improvement suggestions."""
    llm = get_llm()
    cv_analysis = state.get("cv_analysis", {})
    company = state.get("company_name", "")
    requirements = state.get("job_requirements", [])

    if not llm:
        missing = cv_analysis.get("missing_skills", requirements[:3])
        return {
            "cv_suggestions": [
                f"Şu becerileri CV'nize ekleyin: {', '.join(missing[:4])}",
                "Proje açıklamalarınıza somut metrikler ekleyin (ör: '%30 performans artışı')",
                f"{company} için özelleştirilmiş bir summary bölümü yazın",
                "ATS uyumlu standart bölüm başlıkları kullanın (Education, Experience, Skills)",
            ]
        }

    missing = cv_analysis.get("missing_skills", [])
    prompt = (
        f"Sen bir CV uzmanısın. {company} şirketine başvuru için CV'de şu eksikler var:\n"
        f"Eksik beceriler: {', '.join(missing)}\n"
        f"İlan gereksinimleri: {', '.join(requirements[:8])}\n\n"
        f"5 adet spesifik, uygulanabilir Türkçe CV iyileştirme önerisi ver.\n"
        f"Her öneriyi yeni satırda, madde işaretiyle yaz."
    )

    response = llm.invoke(prompt)
    suggestions = [
        line.strip().lstrip("•-123456789. ")
        for line in response.content.strip().split("\n")
        if line.strip() and len(line.strip()) > 5
    ]

    return {"cv_suggestions": suggestions[:6]}


# ════════════════════════════════════════════════════════════
#  NODE 5 — Research Company
# ════════════════════════════════════════════════════════════

def research_company(state: dict) -> dict:
    """Load company info from existing data."""
    company_name = state.get("company_name", "")

    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    company = next((c for c in companies if c["name"].lower() == company_name.lower()), None)

    if company:
        return {
            "company_info": {
                "name": company["name"],
                "industry": company["industry"],
                "rating": company["rating"],
                "tech_stack": company["tech_stack"],
                "culture": company["culture"],
                "interview_style": company["interview_style"],
                "recent_news": company.get("recent_news", ""),
            }
        }

    # Generic fallback
    return {
        "company_info": {
            "name": company_name,
            "industry": "Teknoloji",
            "rating": "N/A",
            "tech_stack": [],
            "culture": "Bilgi mevcut değil — şirketin kariyer sayfasını inceleyin.",
            "interview_style": "Standart teknik mülakat + HR görüşmesi beklenir.",
            "recent_news": "",
        }
    }


# ════════════════════════════════════════════════════════════
#  NODE 6 — Generate Interview Prep
# ════════════════════════════════════════════════════════════

def generate_interview_prep(state: dict) -> dict:
    """Generate company-specific interview questions."""
    llm = get_llm()
    company_info = state.get("company_info", {})
    company_name = company_info.get("name", "Genel")
    tech_stack = company_info.get("tech_stack", [])
    interview_style = company_info.get("interview_style", "")

    if not llm:
        base_qs = [
            f"{company_name} için neden çalışmak istiyorsunuz?",
            f"{'Bu teknolojilerden hangilerini biliyorsunuz: ' + ', '.join(tech_stack[:3]) if tech_stack else 'Hangi teknolojilerde deneyimlisiniz?'}",
            "Bir takım projesinde yaşadığınız en büyük zorluğu anlatın.",
            f"{company_name}'ın sektöründeki güncel trendler hakkında ne biliyorsunuz?",
            "5 yıl sonra kendinizi nerede görüyorsunuz?",
        ]
        return {"interview_questions": base_qs}

    prompt = (
        f"Sen bir mülakat koçusun. {company_name} şirketi için staj mülakatına hazırlık soruları oluştur.\n\n"
        f"Şirket bilgileri:\n"
        f"- Sektör: {company_info.get('industry', 'Teknoloji')}\n"
        f"- Tech stack: {', '.join(tech_stack)}\n"
        f"- Mülakat tarzı: {interview_style}\n\n"
        f"5 adet mülakat sorusu oluştur (3 teknik + 2 davranışsal). Her soruyu yeni satırda yaz. Türkçe yaz."
    )

    response = llm.invoke(prompt)
    questions = [
        line.strip().lstrip("•-123456789. ")
        for line in response.content.strip().split("\n")
        if line.strip() and len(line.strip()) > 10
    ]

    return {"interview_questions": questions[:6]}


# ════════════════════════════════════════════════════════════
#  NODE 7 — Create Action Plan
# ════════════════════════════════════════════════════════════

def create_action_plan(state: dict) -> dict:
    """Synthesize all findings into a personalized action plan."""
    llm = get_llm()
    listing = state.get("listing_data", {})
    cv_score = state.get("cv_score", 0)
    cv_analysis = state.get("cv_analysis", {})
    cv_suggestions = state.get("cv_suggestions", [])
    company_info = state.get("company_info", {})
    interview_questions = state.get("interview_questions", [])
    company_name = company_info.get("name", "")

    if not llm:
        return {
            "action_plan": {
                "readiness_score": cv_score,
                "position": listing.get("position", "Stajyer"),
                "company": company_name,
                "steps": [
                    {"step": 1, "title": "CV Güncellemesi", "description": "; ".join(cv_suggestions[:2]) if cv_suggestions else "CV'nizi ilana göre güncelleyin"},
                    {"step": 2, "title": "Şirket Araştırması", "description": f"{company_name} hakkında detaylı araştırma yapın. Kültür: {company_info.get('culture', 'N/A')[:100]}"},
                    {"step": 3, "title": "Teknik Hazırlık", "description": f"Şu teknolojileri çalışın: {', '.join(company_info.get('tech_stack', ['Genel programlama'])[:4])}"},
                    {"step": 4, "title": "Mülakat Pratiği", "description": "Hazırlanan mülakat sorularını cevaplayarak pratik yapın"},
                    {"step": 5, "title": "Başvuru", "description": f"Başvuru linki: {listing.get('apply_url', '#')}"},
                ],
                "summary": f"{company_name} - {listing.get('position', 'Stajyer')} pozisyonu için hazırlık planınız oluşturuldu. CV uyumluluk skoru: %{cv_score}.",
            }
        }

    prompt = (
        f"Sen bir kariyer danışmanısın. Aşağıdaki bilgilere dayanarak kişiselleştirilmiş bir başvuru aksiyon planı oluştur.\n\n"
        f"Pozisyon: {listing.get('position', 'Stajyer')} @ {company_name}\n"
        f"CV Skoru: {cv_score}/100\n"
        f"Eksikler: {', '.join(cv_analysis.get('missing_skills', []))}\n"
        f"Şirket Tech Stack: {', '.join(company_info.get('tech_stack', []))}\n\n"
        f"JSON formatında 5 adımlı bir aksiyon planı oluştur (sadece JSON):\n"
        f'{{\n'
        f'  "readiness_score": {cv_score},\n'
        f'  "steps": [\n'
        f'    {{"step": 1, "title": "...", "description": "..."}},\n'
        f'    ...\n'
        f'  ],\n'
        f'  "summary": "2 cümle Türkçe özet"\n'
        f'}}'
    )

    response = llm.invoke(prompt)
    text = response.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    try:
        plan = json.loads(text.strip())
    except json.JSONDecodeError:
        plan = {
            "readiness_score": cv_score,
            "steps": [{"step": 1, "title": "Genel Hazırlık", "description": text[:500]}],
            "summary": f"CV skoru: %{cv_score}. Detaylı plan oluşturuldu.",
        }

    plan["position"] = listing.get("position", "Stajyer")
    plan["company"] = company_name

    return {"action_plan": plan}


# ── Fallback helper ─────────────────────────────────────────

def _fallback_cv_eval(cv_text, requirements):
    """Simple keyword-based CV evaluation."""
    cv_lower = cv_text.lower()
    matched = [r for r in requirements if r.lower() in cv_lower]
    missing = [r for r in requirements if r.lower() not in cv_lower]
    total = len(matched) + len(missing)
    score = int((len(matched) / max(total, 1)) * 100) if total > 0 else 55
    score = max(40, min(95, score))

    return {
        "cv_score": score,
        "cv_analysis": {
            "score": score,
            "matched_skills": matched,
            "missing_skills": missing,
            "summary": f"CV'niz ilana %{score} oranında uyumlu. {len(matched)} beceri eşleşti.",
        },
        "needs_improvement": score < 70,
        "status": "fallback",
    }
