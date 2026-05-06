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


def normalize_company_name(value: str) -> str:
    """Normalize company names for fuzzy equality across local datasets."""
    cleaned = (value or "").strip().lower()
    if "(" in cleaned:
        cleaned = cleaned.split("(", 1)[0].strip()
    return " ".join(cleaned.replace("-", " ").split())


def get_llm():
    """Return Gemini client config, or None if no API key."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_key_here":
        return None
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    preferred_model = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")
    timeout = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "12"))
    fallback_models = [
        "models/gemini-flash-lite-latest",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash",
    ]
    ordered_models = [preferred_model] + [name for name in fallback_models if name != preferred_model]
    return {"genai": genai, "models": ordered_models, "timeout": timeout}


def _invoke_model_text(model, prompt: str) -> str:
    last_error = None

    for model_name in model["models"]:
        try:
            response = model["genai"].GenerativeModel(model_name).generate_content(
                prompt,
                request_options={"timeout": model.get("timeout", 12)},
            )
            text = getattr(response, "text", "").strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error

    return ""


def _extract_json_payload(text: str):
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(cleaned[start:end + 1])
    raise json.JSONDecodeError("No JSON object found", cleaned, 0)


def _format_candidate_profile(profile: dict) -> str:
    summary = profile.get("summary", "") or "Yok"
    experience_level = profile.get("experience_level", "") or "Belirtilmedi"
    education = profile.get("education_summary", "") or "Belirtilmedi"
    skills = ", ".join(profile.get("skills", [])) or "Belirtilmedi"

    project_lines = []
    for project in profile.get("projects", [])[:5]:
        title = project.get("title", "").strip()
        description = project.get("description", "").strip()
        project_skills = ", ".join(project.get("skills", []))
        fragments = [title]
        if description:
            fragments.append(description)
        if project_skills:
            fragments.append(f"Kullanilan teknolojiler: {project_skills}")
        if title:
            project_lines.append("- " + " | ".join(fragments))

    projects = "\n".join(project_lines) if project_lines else "- Proje bilgisi bulunmuyor"

    return (
        f"Ozet: {summary}\n"
        f"Deneyim duzeyi: {experience_level}\n"
        f"Egitim: {education}\n"
        f"Beceriler: {skills}\n"
        f"Projeler:\n{projects}"
    )


# ════════════════════════════════════════════════════════════
#  NODE 1 — Analyze Listing
# ════════════════════════════════════════════════════════════

def analyze_listing(state: dict) -> dict:
    """Load listing data and extract key requirements."""
    listing_id = state.get("listing_id", 1)
    mcp_listing = state.get("mcp_context", {}).get("listing", {})

    if mcp_listing:
        listing = mcp_listing
    else:
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
    candidate_profile = state.get("candidate_profile", {})
    job_desc = state.get("job_description", "")
    requirements = state.get("job_requirements", [])
    company = state.get("company_name", "")

    if not cv_text.strip():
        cv_text = "(CV metni sağlanmadı)"

    if not llm:
        return _fallback_cv_eval(cv_text, requirements)

    profile_context = _format_candidate_profile(candidate_profile)
    prompt = (
        "Sen deneyimli bir teknik kariyer danismanisin. Bir stajyer adayin uygunlugunu yalnizca birebir anahtar kelime eslesmesine gore degil,\n"
        "teknoloji benzerligi, proje deneyimi, aktarilabilir beceri ve egitim baglamina gore degerlendir.\n"
        "Ornek: PostgreSQL -> SQL icin guclu eslesme, Next.js -> React icin aktarilabilir frontend deneyimi, FastAPI -> backend/API deneyimi olarak sayilabilir.\n"
        "Skoru gercekci ver ama gereksiz sert olma.\n\n"
        f"Şirket: {company}\n"
        f"İlan Gereksinimleri: {', '.join(requirements[:10])}\n"
        f"İlan Açıklaması: {job_desc[:1000]}\n\n"
        f"Aday Profil Ozetı:\n{profile_context}\n\n"
        f"Ham CV Metni:\n{cv_text[:2500]}\n\n"
        f"JSON formatında yanıt ver (sadece JSON):\n"
        f'{{\n'
        f'  "score": <0-100>,\n'
        f'  "matched_skills": ["dogrudan eslesen beceri"],\n'
        f'  "transferable_skills": ["dolayli ama ilgili beceri"],\n'
        f'  "missing_skills": ["eksik veya daha az gorunen beceri"],\n'
        f'  "strengths": ["adayin guclu yonu"],\n'
        f'  "risks": ["basvuruda risk yaratabilecek konu"],\n'
        f'  "summary": "<2-3 cumle Turkce ozet>"\n'
        f'}}'
    )

    try:
        result = _extract_json_payload(_invoke_model_text(llm, prompt))
    except Exception:
        return _fallback_cv_eval(cv_text, requirements)

    score = int(result.get("score", 65))
    score = max(40, min(95, score))

    return {
        "cv_score": score,
        "cv_analysis": result,
        "needs_improvement": score < 70,
        "status": "ai",
        "llm_provider": "gemini",
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
    candidate_profile = state.get("candidate_profile", {})
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
            ],
            "llm_provider": "fallback",
        }

    missing = cv_analysis.get("missing_skills", [])
    transferable = cv_analysis.get("transferable_skills", [])
    prompt = (
        f"Sen bir CV uzmanısın. {company} şirketine başvuru için CV'yi daha güçlü hale getireceksin.\n"
        f"Aday özeti: {candidate_profile.get('summary', '')}\n"
        f"Aday becerileri: {', '.join(candidate_profile.get('skills', []))}\n"
        f"Eksik beceriler: {', '.join(missing)}\n"
        f"Aktarılabilir beceriler: {', '.join(transferable)}\n"
        f"İlan gereksinimleri: {', '.join(requirements[:8])}\n\n"
        "5 adet spesifik, uygulanabilir Turkce CV iyilestirme onerisi ver.\n"
        "Oneriler genel tavsiye olmasin; adayin projelerini ve becerilerini HAVELSAN baglaminda nasil konumlayacagini anlatsin.\n"
        "Her oneriyi yeni satirda, madde isaretiyle yaz."
    )

    try:
        response_text = _invoke_model_text(llm, prompt)
        suggestions = [
            line.strip().lstrip("•-123456789. ")
            for line in response_text.split("\n")
            if line.strip() and len(line.strip()) > 5
        ]
        return {"cv_suggestions": suggestions[:6], "llm_provider": "gemini"}
    except Exception:
        fallback_suggestions = [
            f"{company} için özet kısmınızı ve proje deneyimlerinizi ilana göre yeniden konumlandırın.",
            "Proje açıklamalarında ölçülebilir sonuçlar ve teknik sahiplik vurgusu ekleyin.",
            f"Şu başlıklarda görünürlüğü artırın: {', '.join(missing[:3])}" if missing else "İlanda öne çıkan teknik başlıkları CV içinde daha görünür hale getirin.",
            "Başvurduğunuz rol için kullandığınız benzer teknolojileri birebir isimleriyle yazın.",
        ]
        return {"cv_suggestions": fallback_suggestions, "llm_provider": "fallback"}


# ════════════════════════════════════════════════════════════
#  NODE 5 — Research Company
# ════════════════════════════════════════════════════════════

def research_company(state: dict) -> dict:
    """Load company info from existing data."""
    company_name = state.get("company_name", "")
    mcp_company = state.get("mcp_context", {}).get("company", {})
    if mcp_company:
        return {
            "company_info": {
                "name": mcp_company.get("name", company_name),
                "industry": mcp_company.get("industry", "Teknoloji"),
                "rating": mcp_company.get("rating", "N/A"),
                "tech_stack": mcp_company.get("tech_stack", []),
                "culture": mcp_company.get("culture", ""),
                "interview_style": mcp_company.get("interview_style", ""),
                "recent_news": mcp_company.get("recent_news", ""),
            }
        }

    normalized_name = normalize_company_name(company_name)

    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    company = next(
        (
            c
            for c in companies
            if normalize_company_name(c["name"]) == normalized_name
        ),
        None,
    )

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
    candidate_profile = state.get("candidate_profile", {})
    company_name = company_info.get("name", "Genel")
    tech_stack = company_info.get("tech_stack", [])
    interview_style = company_info.get("interview_style", "")

    if not llm:
        cv_specific = [
            "CV'nizde öne çıkan projelerden birini seçin ve mimari kararlarınızı anlatın.",
            "Takım çalışması gerektiren bir projede sorumluluk aldığınız bir anı paylaşın.",
            "Projelerinizden birinde yaşadığınız teknik bir problemi nasıl çözdünüz?",
        ]
        company_specific = [
            f"{company_name} tarafında Java ve React kullanılan bir projede nasıl katkı verirsiniz?",
            f"{company_name} gibi kurumsal bir ekipte kod kalitesi ve test süreçlerini nasıl ele alırsınız?",
            f"{company_name} mülakatında size mikroservisler veya container yönetimi sorulursa nasıl cevap verirsiniz?",
        ]
        return {
            "interview_questions": cv_specific + company_specific,
            "interview_sections": {
                "cv_specific": cv_specific,
                "company_specific": company_specific,
            },
            "llm_provider": "fallback",
        }

    project_titles = ", ".join(project.get("title", "") for project in candidate_profile.get("projects", [])[:4])
    prompt = (
        f"Sen bir mülakat koçusun. {company_name} şirketi için staj mülakatına hazırlık soruları oluştur.\n\n"
        f"Şirket bilgileri:\n"
        f"- Sektör: {company_info.get('industry', 'Teknoloji')}\n"
        f"- Tech stack: {', '.join(tech_stack)}\n"
        f"- Mülakat tarzı: {interview_style}\n\n"
        f"Adayın öne çıkan becerileri: {', '.join(candidate_profile.get('skills', []))}\n"
        f"Adayın projeleri: {project_titles}\n\n"
        "Iki kategori halinde toplam 6 soru uret:\n"
        "1. cv_specific: Adayin CV'sindeki projelere ve deneyimlerine dayali 3 soru.\n"
        "2. company_specific: Bu role basvuran adaylara sirketin sorma ihtimali yuksek 3 teknik veya davranissal soru.\n"
        "company_specific sorularinda adayin projesine bagimli kalma; rol, tech stack ve sirket ortamina odaklan.\n"
        "Yanit formatin sadece JSON olsun:\n"
        "{\n"
        '  "cv_specific": ["..."],\n'
        '  "company_specific": ["..."]\n'
        "}"
    )

    try:
        payload = _extract_json_payload(_invoke_model_text(llm, prompt))
        cv_specific = [question.strip() for question in payload.get("cv_specific", []) if question.strip()]
        company_specific = [question.strip() for question in payload.get("company_specific", []) if question.strip()]
    except Exception:
        cv_specific = []
        company_specific = []

    if not cv_specific and not company_specific:
        company_specific = [
            f"{company_name} tarafında Java ve React ile geliştirilen bir modülde nasıl ilerlersiniz?",
            f"{company_name} gibi savunma/kurumsal projelerde test, güvenlik ve kod kalite beklentileri neler olur?",
            f"{company_name} mülakatında Docker, Kubernetes veya SQL ile ilgili nasıl bir teknik soru bekliyorsunuz?",
        ]
        cv_specific = [
            f"{project_titles.split(',')[0] if project_titles else 'Öne çıkan projeniz'} üzerinden mimari tercihlerinizi anlatın.",
            "CV'nizdeki projelerden birinde aldığınız teknik riski ve bunu nasıl yönettiğinizi açıklayın.",
            "Takım içinde sahiplik aldığınız bir geliştirmeyi ve ölçülebilir etkisini paylaşın.",
        ]

    return {
        "interview_questions": (cv_specific + company_specific)[:6],
        "interview_sections": {
            "cv_specific": cv_specific[:3],
            "company_specific": company_specific[:3],
        },
        "llm_provider": "gemini",
    }


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
    candidate_profile = state.get("candidate_profile", {})
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
            },
            "llm_provider": "fallback",
        }

    prompt = (
        f"Sen bir kariyer danışmanısın. Aşağıdaki bilgilere dayanarak kişiselleştirilmiş bir başvuru aksiyon planı oluştur.\n\n"
        f"Pozisyon: {listing.get('position', 'Stajyer')} @ {company_name}\n"
        f"CV Skoru: {cv_score}/100\n"
        f"Eksikler: {', '.join(cv_analysis.get('missing_skills', []))}\n"
        f"Aktarılabilir beceriler: {', '.join(cv_analysis.get('transferable_skills', []))}\n"
        f"Şirket Tech Stack: {', '.join(company_info.get('tech_stack', []))}\n\n"
        f"Adayın mevcut güçlü projeleri: {', '.join(project.get('title', '') for project in candidate_profile.get('projects', [])[:4])}\n"
        f"Adayın güçlü becerileri: {', '.join(candidate_profile.get('skills', []))}\n"
        f"CV önerileri: {'; '.join(cv_suggestions[:4])}\n\n"
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

    try:
        plan = _extract_json_payload(_invoke_model_text(llm, prompt))
    except Exception:
        plan = {
            "readiness_score": cv_score,
            "steps": [{"step": 1, "title": "Genel Hazırlık", "description": "Detaylı aksiyon planı üretilemedi, temel hazırlık adımlarına odaklanın."}],
            "summary": f"CV skoru: %{cv_score}. Detaylı plan oluşturuldu.",
        }

    plan["position"] = listing.get("position", "Stajyer")
    plan["company"] = company_name

    return {"action_plan": plan, "llm_provider": "gemini"}


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
            "transferable_skills": [],
            "missing_skills": missing,
            "summary": f"CV'niz ilana %{score} oranında uyumlu. {len(matched)} beceri eşleşti.",
        },
        "needs_improvement": score < 70,
        "status": "fallback",
        "llm_provider": "fallback",
    }
