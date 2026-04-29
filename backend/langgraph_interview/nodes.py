"""
LangGraph Interview — Node Functions

Five graph nodes for the stateful mock interview:
  1. generate_question  — AI-powered question generation
  2. evaluate_answer    — AI-powered answer evaluation
  3. adjust_difficulty  — Dynamic difficulty adjustment
  4. check_progress     — Router: continue or finish
  5. generate_summary   — Comprehensive performance summary
"""

import json
import hashlib
import os
import re

# ── LLM helper ──────────────────────────────────────────────

def get_llm():
    """Return a ChatOpenAI instance, or None if no API key."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_key_here":
        return None
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7, max_tokens=1024)


# ── Fallback data ───────────────────────────────────────────

FALLBACK_QUESTIONS = {
    "technical": {
        "easy": [
            "Git'te branch nedir ve neden kullanılır?",
            "HTTP GET ve POST arasındaki fark nedir?",
            "Array ve LinkedList arasındaki temel farklar nelerdir?",
        ],
        "medium": [
            "REST API tasarlarken dikkat etmeniz gereken temel prensipler nelerdir?",
            "React'te state management yaklaşımlarını karşılaştırın.",
            "SQL ve NoSQL veritabanları arasındaki farkları açıklayın.",
        ],
        "hard": [
            "Microservice mimarisinde servisler arası iletişim stratejilerini açıklayın.",
            "Bir e-ticaret platformunun ölçeklenebilirlik stratejisini tasarlayın.",
            "Distributed systems'da CAP teoremini açıklayın ve pratik örnekler verin.",
        ],
    },
    "behavioral": {
        "easy": [
            "Bir takım projesinde yaşadığınız bir zorluğu anlatın.",
            "Yeni bir teknoloji öğrenmeniz gereken bir durumu anlatın.",
            "Staj deneyiminizden ne bekliyorsunuz?",
        ],
        "medium": [
            "Deadline baskısı altında kalite ve hız arasında nasıl denge kurarsınız?",
            "Bir projede teknik bir hata yaptığınızda nasıl çözdünüz?",
            "Geri bildirim aldığınızda nasıl tepki verirsiniz?",
        ],
        "hard": [
            "Takım liderliği yaptığınız ve kritik bir karar vermeniz gereken bir durumu anlatın.",
            "Birbiriyle çelişen öncelikleri nasıl yönetirsiniz?",
            "Başarısızlıkla sonuçlanan bir projenizden ne öğrendiniz?",
        ],
    },
}

EXTRA_FALLBACK_QUESTIONS = {
    "technical": {
        "easy": [
            "Bir API'den gelen hatayı frontend'de kullanıcıya nasıl gösterirsiniz?",
            "Local storage ve session storage arasındaki fark nedir?",
            "Python'da list comprehension ne işe yarar?",
        ],
        "medium": [
            "Bir sayfanın yavaş açılmasını nasıl analiz edip iyileştirirsiniz?",
            "JWT tabanlı auth akışında token yenileme nasıl yönetilir?",
            "Bir backend endpoint'i için hangi testleri yazardınız?",
        ],
        "hard": [
            "Yüksek trafikli bir bildirim sistemini nasıl tasarlardınız?",
            "Cache invalidation problemini örnek bir sistem üzerinde nasıl çözersiniz?",
            "Veri tutarlılığı ile performans arasında nasıl trade-off yaparsınız?",
        ],
    },
    "behavioral": {
        "easy": [
            "Geri bildirim aldığınızda bunu nasıl uyguladığınızı anlatın.",
            "Bir görevi yetiştiremediğinizde nasıl iletişim kurarsınız?",
            "Takımda size verilen sorumluluğu nasıl takip edersiniz?",
        ],
        "medium": [
            "Takım arkadaşınızla fikir ayrılığı yaşadığınızda nasıl ilerlersiniz?",
            "Belirsiz bir görev aldığınızda netleştirmek için hangi adımları atarsınız?",
            "Bir projede öncelikler değiştiğinde planınızı nasıl güncellersiniz?",
        ],
        "hard": [
            "Eksik bilgiyle karar vermeniz gereken bir durumda nasıl risk yönetimi yaparsınız?",
            "Bir ekip üyesinin performansı projeyi etkilediğinde nasıl yaklaşırsınız?",
            "Kendi hatanızı geç fark ettiğiniz bir durumda paydaşları nasıl yönetirsiniz?",
        ],
    },
}

LOW_QUALITY_ANSWERS = {
    "",
    "bilmiyorum",
    "bilmiyom",
    "bilmem",
    "yok",
    "hayir",
    "hayır",
    "ss",
    "ne oldu",
    "soylemeyecegim",
    "söylemeyeceğim",
    "cevap yok",
    "fikrim yok",
}

EVASIVE_MARKERS = (
    "bilmiyorum",
    "bilmem",
    "yok",
    "soylemeyecegim",
    "söylemeyeceğim",
    "cevap vermek istemiyorum",
)


def _normalized_answer(answer: str) -> str:
    return " ".join((answer or "").strip().lower().split())


def _is_low_quality_answer(answer: str) -> bool:
    normalized = _normalized_answer(answer)
    word_count = len(normalized.split())
    return (
        normalized in LOW_QUALITY_ANSWERS
        or word_count < 4
        or any(marker in normalized for marker in EVASIVE_MARKERS)
    )


def _low_quality_answer_result(answer: str) -> dict:
    normalized = _normalized_answer(answer)
    score = 0 if normalized in {"", "yok", "ss", "bilmiyorum", "bilmem"} else 10
    feedback = (
        "Cevap, soruyu değerlendirebilmek için yeterli bilgi içermiyor. "
        "Somut bir durum, kendi rolünüz, attığınız adımlar ve sonuç paylaşılmadığı için "
        "mülakat açısından güçlü bir kanıt oluşmuyor.\n\n"
        "💪 Güçlü: Bu cevapta belirgin bir güçlü yan gözlenmedi.\n\n"
        "📈 Geliştir: STAR yapısını kullanın: Durum, Görev, Aksiyon ve Sonuç. "
        "Kısa da olsa gerçek veya makul bir örnek vererek cevabı 4-6 cümleye çıkarın."
    )
    return {
        "feedback": feedback,
        "scores": [score],
        "messages": [{"role": "user", "content": answer}],
    }


def _stable_index(seed: str, category: str, difficulty: str, question_count: int, total: int) -> int:
    raw = f"{seed}:{category}:{difficulty}:{question_count}".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest(), 16) % max(total, 1)


def _profile_context(profile: dict) -> str:
    if not profile:
        return ""

    parts = []
    summary = profile.get("summary") or profile.get("experience_level")
    if summary:
        parts.append(f"Profil özeti: {str(summary)[:500]}")

    skills = profile.get("skills") or []
    if skills:
        parts.append(f"Beceriler: {', '.join(map(str, skills[:12]))}")

    education = profile.get("education_summary")
    if education:
        parts.append(f"Eğitim: {str(education)[:180]}")

    projects = profile.get("projects") or []
    project_titles = [
        str(project.get("title", "")).strip()
        for project in projects
        if isinstance(project, dict) and project.get("title")
    ]
    if project_titles:
        parts.append(f"Projeler: {', '.join(project_titles[:4])}")

    return "\n".join(parts)


def _clean_question_text(question: str) -> str:
    return re.sub(r"^\s*soru\s*\d+\s*[:.)-]\s*", "", question.strip(), flags=re.IGNORECASE)


# ════════════════════════════════════════════════════════════
#  NODE 1 — Generate Question
# ════════════════════════════════════════════════════════════

def generate_question(state: dict) -> dict:
    """Generate an interview question using LLM or fallback."""
    llm = get_llm()
    company = state.get("company", "Genel")
    position = state.get("position", "Yazılım Mühendisi Stajyeri")
    category = state.get("category", "technical")
    difficulty = state.get("difficulty", "medium")
    question_count = state.get("question_count", 0)
    messages = state.get("messages", [])
    asked_questions = state.get("asked_questions", [])
    candidate_profile = state.get("candidate_profile", {})
    session_seed = state.get("session_seed", "default")

    if not llm:
        return _fallback_question(category, question_count, difficulty, asked_questions, session_seed)

    prev_context = ""
    if messages:
        recent = messages[-4:]
        prev_context = "\n".join(
            [f"{'Soru' if m['role']=='assistant' else 'Cevap'}: {m['content'][:200]}" for m in recent]
        )

    cat_label = "Teknik" if category == "technical" else "Davranışsal"
    prompt = (
        f"Sen bir kıdemli mülakat koçusun. {company} şirketinde {position} pozisyonu için "
        f"bir {cat_label.lower()} mülakat sorusu oluştur.\n\n"
        f"Zorluk seviyesi: {difficulty}\n"
        f"Soru numarası: {question_count + 1}\n"
    )
    if prev_context:
        prompt += f"\nÖnceki konuşma:\n{prev_context}\n\nDaha önce sorulmamış farklı bir soru sor.\n"
    else:
        prompt += "\nBu ilk soru.\n"
    profile_context = _profile_context(candidate_profile)
    if profile_context:
        prompt += (
            "\nAday profili / CV özeti:\n"
            f"{profile_context}\n"
            "Soruyu mümkünse adayın becerileri, projeleri veya deneyim seviyesine bağla.\n"
        )

    if asked_questions:
        previous_questions = "\n".join(f"- {question[:220]}" for question in asked_questions[-8:])
        prompt += (
            "\nBu oturumda daha önce sorulan sorular:\n"
            f"{previous_questions}\n"
            "Bu soruların konusunu, örneğini veya cümle yapısını tekrar etme.\n"
        )

    if state.get("scores") and state["scores"][-1] < 50:
        prompt += (
            "\nSon cevap zayıftı. Adaya toparlanma şansı veren, ama aynı soruyu tekrar etmeyen "
            "daha spesifik bir takip sorusu sor.\n"
        )

    prompt += (
        f"\nOturum varyasyon anahtarı: {session_seed}.\n"
        "Her oturumda farklı açıdan sor. Sadece tek bir soru yaz, açıklama ekleme. Türkçe yaz."
    )

    response = llm.invoke(prompt)
    question = _clean_question_text(response.content)

    return {
        "current_question": question,
        "question_count": question_count + 1,
        "messages": [{"role": "assistant", "content": question}],
        "asked_questions": [question],
        "phase": "questioning",
    }


# ════════════════════════════════════════════════════════════
#  NODE 2 — Evaluate Answer
# ════════════════════════════════════════════════════════════

def evaluate_answer(state: dict) -> dict:
    """Evaluate user's answer with AI scoring and feedback."""
    llm = get_llm()
    question = state.get("current_question", "")
    answer = state.get("user_answer", "")
    company = state.get("company", "Genel")

    if _is_low_quality_answer(answer):
        return _low_quality_answer_result(answer)

    if not llm:
        return _fallback_evaluate(answer)

    prompt = (
        f"Sen bir mülakat değerlendiricisisin. Aşağıdaki mülakat sorusuna verilen cevabı değerlendir.\n\n"
        f"Şirket: {company}\nSoru: {question}\nCevap: {answer}\n\n"
        f"Aşağıdaki JSON formatında yanıt ver (sadece JSON, başka bir şey yazma):\n"
        f'{{\n'
        f'  "score": <0-100 arası puan>,\n'
        f'  "feedback": "<2-3 cümle Türkçe geri bildirim>",\n'
        f'  "strengths": "<güçlü yanlar, kısa>",\n'
        f'  "improvements": "<geliştirilmesi gerekenler, kısa>"\n'
        f'}}'
    )

    response = llm.invoke(prompt)
    text = response.content.strip()

    # Clean markdown code blocks
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        result = json.loads(text)
        score = result.get("score", 60)
        if score < 20:
            result["strengths"] = "Bu cevapta belirgin bir güçlü yan gözlenmedi."
        feedback = result.get("feedback", "Değerlendirme tamamlandı.")
        if result.get("strengths"):
            feedback += f"\n\n💪 Güçlü: {result['strengths']}"
        if result.get("improvements"):
            feedback += f"\n\n📈 Geliştir: {result['improvements']}"
    except json.JSONDecodeError:
        score = 60
        feedback = text

    return {
        "feedback": feedback,
        "scores": [score],
        "messages": [{"role": "user", "content": answer}],
    }


# ════════════════════════════════════════════════════════════
#  NODE 3 — Adjust Difficulty
# ════════════════════════════════════════════════════════════

def adjust_difficulty(state: dict) -> dict:
    """Dynamically adjust difficulty based on recent performance."""
    scores = state.get("scores", [])
    current = state.get("difficulty", "medium")
    max_questions = state.get("max_questions", 5)
    question_limit = state.get("question_limit", max_questions)

    updates = {}
    if scores and scores[-1] < 50 and max_questions < question_limit:
        updates["max_questions"] = max_questions + 1

    if len(scores) < 2:
        return {"difficulty": current, **updates}

    avg_recent = sum(scores[-2:]) / 2

    if avg_recent >= 80:
        new_diff = "hard"
    elif avg_recent >= 50:
        new_diff = "medium"
    else:
        new_diff = "easy"

    return {"difficulty": new_diff, **updates}


# ════════════════════════════════════════════════════════════
#  NODE 4 — Check Progress (Router)
# ════════════════════════════════════════════════════════════

def check_progress(state: dict) -> str:
    """Router function: decide whether to continue or end."""
    question_count = state.get("question_count", 0)
    max_questions = state.get("max_questions", 5)

    if question_count >= max_questions:
        return "done"
    return "continue"


# ════════════════════════════════════════════════════════════
#  NODE 5 — Generate Summary
# ════════════════════════════════════════════════════════════

def generate_summary(state: dict) -> dict:
    """Generate comprehensive interview performance summary."""
    llm = get_llm()
    scores = state.get("scores", [])
    messages = state.get("messages", [])
    company = state.get("company", "Genel")
    avg_score = sum(scores) / len(scores) if scores else 0

    if avg_score < 20:
        return _low_score_summary(scores, avg_score)

    if not llm:
        return _fallback_summary(scores, avg_score)

    conversation = "\n".join(
        [f"{'Soru' if m['role']=='assistant' else 'Cevap'}: {m['content'][:200]}" for m in messages[-10:]]
    )

    prompt = (
        f"Sen bir mülakat koçusun. Aşağıdaki mülakat performansını özetle.\n\n"
        f"Şirket: {company}\n"
        f"Toplam soru: {len(scores)}\n"
        f"Puanlar: {scores}\n"
        f"Ortalama: {avg_score:.0f}/100\n\n"
        f"Konuşma:\n{conversation[:2000]}\n\n"
        f"3-4 cümlelik Türkçe bir özet yaz. Güçlü yanları, gelişim alanlarını ve genel tavsiyeni belirt."
    )

    response = llm.invoke(prompt)

    return {
        "summary": response.content.strip(),
        "phase": "completed",
    }


# ── Fallback helpers ────────────────────────────────────────

def _fallback_question(category, question_count, difficulty, asked_questions=None, session_seed="default"):
    asked_questions = asked_questions or []
    questions = FALLBACK_QUESTIONS.get(category, FALLBACK_QUESTIONS["technical"])
    extras = EXTRA_FALLBACK_QUESTIONS.get(category, {}).get(difficulty, [])
    diff_qs = [*questions.get(difficulty, questions["medium"]), *extras]
    available = [question for question in diff_qs if question not in asked_questions]
    if not available:
        available = diff_qs
    idx = _stable_index(session_seed, category, difficulty, question_count, len(available))
    if len(available) > 1 and asked_questions and available[idx] == asked_questions[-1]:
        idx = (idx + 1) % len(available)
    question = available[idx]
    return {
        "current_question": question,
        "question_count": question_count + 1,
        "messages": [{"role": "assistant", "content": question}],
        "asked_questions": [question],
        "phase": "questioning",
    }


def _fallback_evaluate(answer):
    if _is_low_quality_answer(answer):
        return _low_quality_answer_result(answer)

    length = len(answer)
    if length < 20:
        score, fb = 30, "Cevabınız çok kısa. Daha detaylı yanıt vermeniz bekleniyor."
    elif length < 100:
        score, fb = 60, "İyi bir başlangıç. Somut bir proje deneyimiyle desteklerseniz daha güçlü olur."
    else:
        score, fb = 85, "Kapsamlı ve detaylı bir cevap. Mülakatta bu şekilde ifade ederseniz güçlü izlenim bırakırsınız."
    return {
        "feedback": fb,
        "scores": [score],
        "messages": [{"role": "user", "content": answer}],
    }


def _fallback_summary(scores, avg_score):
    n = len(scores)
    if avg_score >= 75:
        s = f"Mülakat performansınız güçlü! {n} sorudan ortalama {avg_score:.0f} puan aldınız. Teknik bilginiz sağlam, gerçek mülakata hazırsınız."
    elif avg_score >= 50:
        s = f"Ortalama performans ({avg_score:.0f}/100). Bazı alanlarda güçlüsünüz ancak teknik derinliği artırmanız gerekiyor."
    else:
        s = f"Gelişime açık alanlarınız var ({avg_score:.0f}/100). Temel kavramları gözden geçirin ve daha detaylı cevaplar verin."
    return {"summary": s, "phase": "completed"}


def _low_score_summary(scores, avg_score):
    n = len(scores)
    return {
        "summary": (
            f"Mülakat performansı zayıf kaldı: {n} soruda ortalama {avg_score:.0f}/100 puan alındı. "
            "Cevaplarda somut örnek, adayın kendi rolü, izlediği adımlar ve sonuç bilgisi bulunmadığı için "
            "net bir güçlü yan tespit edilemedi. Gelişim için her soruya STAR yapısıyla 4-6 cümlelik, "
            "ölçülebilir sonuç içeren cevaplar hazırlanmalı."
        ),
        "phase": "completed",
    }
