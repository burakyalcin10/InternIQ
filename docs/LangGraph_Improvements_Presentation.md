# InternIQ — LangGraph İyileştirmeleri (19 Nisan Sonrası)

Bu döküman, hocamın "Bu nasıl çalışıyor?" ve "Neden böyle yaptın?" sorularını yanıtlamak üzere, ilgili kod parçacıkları ve dosya yollarıyla birlikte hazırlanmıştır.

---

## Genel Bakış: Ne Değişti?

19 Nisan öncesinde InternIQ'nun AI katmanı **CrewAI** üzerine kuruluydu — şirket araştırması için birden fazla ajanın sıralı çalıştığı bir yapı. LangGraph entegrasyonu ile iki yeni özellik eklendi:

| Özellik | Teknoloji | Açıklama |
|---|---|---|
| Başvuru Hazırlık Akışı | LangGraph (7 düğüm) | Kullanıcının CV'sini bir ilana karşı analiz eder, şirket araştırır, mülakat soruları ve aksiyon planı üretir |
| AI Mülakat Simülasyonu | LangGraph (2 graf, 5 düğüm) | Kullanıcıyla soru-cevap döngüsü kurar, her cevabı puanlar, zorluğu dinamik olarak ayarlar |

Ardından gelen commit'lerde bu iki özellik şu iyileştirmelerle pekiştirildi:

1. **Gemini ile kişiselleştirilmiş analiz** — Düğümler artık kullanıcının profilinden (projeler, beceriler) haberdar
2. **Kayıtlı profil entegrasyonu** — Kullanıcı bir kez CV yüklediğinde, workflow otomatik olarak bunu kullanır
3. **Güçlü fallback katmanı** — API anahtarı olmasa bile sistem çalışmaya devam eder
4. **LangSmith gözlemlenebilirliği** — Her graf çalışması izlenip debug edilebilir
5. **Ortam değişkeni düzeltmesi** — `python-dotenv`'in `.env`'yi kaçırdığı durum manuel yüklemeyle çözüldü

---

## 1. LangGraph Nedir ve Neden Kullandık?

### Nasıl çalışır?

LangGraph, **durum makinesi (state machine)** mantığıyla AI iş akışları kurmanı sağlayan bir kütüphane. Temel yapı:

- **State (Durum):** `TypedDict` ile tanımlanmış, tüm düğümler arasında paylaşılan bir sözlük
- **Node (Düğüm):** State'i alıp değiştirerek geri dönen Python fonksiyonu
- **Edge (Kenar):** Düğümler arası geçişi tanımlar — sabit veya koşullu olabilir
- **Conditional Edge:** Bir "router" fonksiyonu çalıştırır ve dönen string'e göre farklı düğüme yönlendirir

Veri akışı şu şekilde ilerler: her düğüm yalnızca kendi ürettiği alanları döndürür, LangGraph bunları mevcut state ile birleştirerek sonraki düğüme iletir.

```
STATE = { listing_id, cv_text, cv_score, company_info, action_plan, ... }

START → [node_1: STATE'i okur, kendi alanlarını günceller]
      → [node_2: güncel STATE'i alır, kendi alanlarını günceller]
      → ...
      → END
```

### Neden CrewAI yerine / yanında LangGraph?

**CrewAI** ajan odaklıdır — ajan özerk davranır, kendi kararlarını verir, iç döngüleri kontrolü zordur. Şirket araştırması gibi "araştır ve raporla" görevleri için idealdir.

**LangGraph** ise belirleyici (deterministic) akışlar için tercih edildi. Startup'tan aksiyon planına uzanan 7 adımlı bir süreçte her adımın ne yapacağı önceden biliniyor. Koşullu yönlendirme (CV skoru 70 altındaysa farklı yol), durum birikimi ve belirli sıralama için LangGraph çok daha uygun.

---

## 2. State Tanımları

State, tüm düğümlerin okuyup yazabildiği paylaşılan sözlüktür. Her özellik için ayrı bir `TypedDict` sınıfı tanımlandı.

### Workflow State

**`backend/langgraph_workflow/state.py`**

```python
from typing_extensions import TypedDict

class WorkflowState(TypedDict):
    # ── Input ──
    listing_id: int
    cv_text: str
    candidate_profile: dict        # Kayıtlı profilden gelen yapılandırılmış veri

    # ── Listing Analysis ──
    listing_data: dict
    job_requirements: list
    job_description: str

    # ── CV Evaluation ──
    cv_score: int
    cv_analysis: dict
    needs_improvement: bool        # Koşullu kenarın okuyacağı bayrak
    cv_suggestions: list

    # ── Company Research ──
    company_name: str
    company_info: dict

    # ── Interview Prep ──
    interview_questions: list
    interview_sections: dict

    # ── Final Output ──
    action_plan: dict
    status: str                    # "ai" | "fallback"
    llm_provider: str              # "gemini" | "fallback"
```

### Interview State

**`backend/langgraph_interview/state.py`**

```python
from typing import Annotated
from typing_extensions import TypedDict
import operator

class InterviewState(TypedDict):
    # ── Context ──
    company: str
    position: str
    category: str                  # "technical" | "behavioral"

    # ── Conversation ──
    messages: Annotated[list, operator.add]   # Birikmeli: her düğüm listeye ekler
    current_question: str
    user_answer: str

    # ── Progress ──
    question_count: int
    max_questions: int
    scores: Annotated[list, operator.add]     # Birikmeli: her cevabın puanı eklenir
    difficulty: str                # "easy" | "medium" | "hard"

    # ── Output ──
    feedback: str
    phase: str                     # "start" | "questioning" | "completed"
    summary: str
```

**Neden `Annotated[list, operator.add]`?**

Normalde bir düğüm `{"messages": [new_item]}` döndürdüğünde LangGraph bu alanı **üzerine yazar**. `operator.add` reducer'ı tanımlandığında LangGraph bunun yerine **mevcut listeye ekler**. Bu sayede tüm mülakat geçmişi ve puan serisi korunur — her düğüm sadece kendi katkısını döndürür, tüm geçmişi taşımak zorunda kalmaz.

---

## 3. Graf Tanımları ve START Noktaları

### Workflow Graf

**`backend/langgraph_workflow/graph.py`**

```python
from langgraph.graph import StateGraph, START, END

from .state import WorkflowState
from .nodes import (
    analyze_listing,
    evaluate_cv,
    check_cv_score,        # Router fonksiyonu — node değil
    suggest_improvements,
    research_company,
    generate_interview_prep,
    create_action_plan,
)

def build_workflow_graph():
    builder = StateGraph(WorkflowState)

    # ── Düğümleri kaydet ──
    builder.add_node("analyze_listing", analyze_listing)
    builder.add_node("evaluate_cv", evaluate_cv)
    builder.add_node("suggest_improvements", suggest_improvements)
    builder.add_node("research_company", research_company)
    builder.add_node("generate_interview_prep", generate_interview_prep)
    builder.add_node("create_action_plan", create_action_plan)

    # ── Sabit kenarlar ──
    builder.add_edge(START, "analyze_listing")      # ← START noktası
    builder.add_edge("analyze_listing", "evaluate_cv")

    # ── Koşullu kenar: CV skoru 70'in altındaysa farklı yol ──
    builder.add_conditional_edges(
        "evaluate_cv",         # Bu düğümden çık
        check_cv_score,        # Bu router'ı çalıştır
        {
            "needs_improvement": "suggest_improvements",   # Dönen "needs_improvement" → bu düğüme
            "good_fit": "research_company",                # Dönen "good_fit" → bu düğüme
        },
    )

    # ── İki yol birleşiyor ──
    builder.add_edge("suggest_improvements", "research_company")
    builder.add_edge("research_company", "generate_interview_prep")
    builder.add_edge("generate_interview_prep", "create_action_plan")
    builder.add_edge("create_action_plan", END)

    return builder.compile()

# İmport edilmeye hazır, önceden derlenmiş graf
workflow_graph = build_workflow_graph()
```

**Graf topolojisi:**

```
START
  │
  ▼
analyze_listing          → İlandan gereksinimler çıkarılır (JSON dosyasından)
  │
  ▼
evaluate_cv              → CV, ilana karşı Gemini ile değerlendirilir (0-100 puan)
  │
  ▼
[check_cv_score]         ← ROUTER düğümü (koşullu kenar)
  │              │
  │ skor<70      │ skor≥70
  ▼              │
suggest_improvements     → Şirkete özgü CV iyileştirme önerileri üretilir
  │              │
  └──────┬───────┘
         ▼
  research_company        → Şirket bilgisi veri tabanından alınır
         │
         ▼
  generate_interview_prep → Şirkete ve CV'ye özel mülakat soruları üretilir
         │
         ▼
  create_action_plan      → 5 adımlı kişiselleştirilmiş eylem planı sentezlenir
         │
         ▼
        END
```

---

### Interview Grafları

**`backend/langgraph_interview/graph.py`**

```python
from langgraph.graph import StateGraph, START, END

from .state import InterviewState
from .nodes import (
    generate_question,
    evaluate_answer,
    adjust_difficulty,
    check_progress,        # Router fonksiyonu
    generate_summary,
)

def build_question_graph():
    """Tek düğümlü graf — sadece ilk soruyu üretir."""
    builder = StateGraph(InterviewState)
    builder.add_node("generate_question", generate_question)
    builder.add_edge(START, "generate_question")    # ← START noktası
    builder.add_edge("generate_question", END)
    return builder.compile()


def build_answer_graph():
    """Çok adımlı graf — cevabı değerlendirir, zorluğu ayarlar, devam veya bitir."""
    builder = StateGraph(InterviewState)

    builder.add_node("evaluate_answer", evaluate_answer)
    builder.add_node("adjust_difficulty", adjust_difficulty)
    builder.add_node("generate_question", generate_question)
    builder.add_node("generate_summary", generate_summary)

    builder.add_edge(START, "evaluate_answer")          # ← START noktası
    builder.add_edge("evaluate_answer", "adjust_difficulty")

    # ── Koşullu kenar: devam mı, bitir mi? ──
    builder.add_conditional_edges(
        "adjust_difficulty",
        check_progress,        # "continue" veya "done" döndürür
        {
            "continue": "generate_question",
            "done": "generate_summary",
        },
    )

    builder.add_edge("generate_question", END)
    builder.add_edge("generate_summary", END)

    return builder.compile()


# Her ikisi de import anında derlenir
question_graph = build_question_graph()
answer_graph   = build_answer_graph()
```

**Neden iki ayrı graf?** İlk soru için cevap değerlendirme, zorluk ayarı gibi adımlara gerek yok. Tek düğümlü `question_graph` sadece ilk soruyu üretir. Her cevap geldiğinde 4 adımlı `answer_graph` devreye girer. Sorumluluklar bu şekilde net olarak ayrılıyor.

**`answer_graph` topolojisi:**

```
START
  │
  ▼
evaluate_answer          → Cevabı AI ile puanlar (0-100), geri bildirim üretir
  │
  ▼
adjust_difficulty        → Son 2 puanın ortalamasına göre zorluğu günceller
  │
  ▼
[check_progress]         ← ROUTER
  │              │
  │ "continue"   │ "done"
  ▼              ▼
generate_question     generate_summary   → Tüm mülakat özetini AI ile yazar
  │                       │
  ▼                       ▼
 END                     END
```

---

## 4. Router Fonksiyonları (Koşullu Kenarlar)

Router fonksiyonları bir `str` döndürür — LangGraph bu string'i `add_conditional_edges`'deki map ile düğüm adına çevirir. Node değil, saf Python fonksiyonudur.

### CV Skoru Router'ı

**`backend/langgraph_workflow/nodes.py`** — satır 209

```python
def check_cv_score(state: dict) -> str:
    """Router: CV skoru 70'in altındaysa önce iyileştirme öner."""
    if state.get("needs_improvement", False):
        return "needs_improvement"
    return "good_fit"
```

`needs_improvement` bayrağı bir önceki düğüm olan `evaluate_cv` tarafından state'e yazılır:

```python
# evaluate_cv düğümünün döndürdüğü değer — nodes.py satır 196
return {
    "cv_score": score,
    "cv_analysis": result,
    "needs_improvement": score < 70,   # ← Router bunu okuyacak
    "status": "ai",
    "llm_provider": "gemini",
}
```

### Mülakat İlerleme Router'ı

**`backend/langgraph_interview/nodes.py`** — satır 197

```python
def check_progress(state: dict) -> str:
    """Router: soru limitine ulaşıldıysa bitir, yoksa devam et."""
    question_count = state.get("question_count", 0)
    max_questions  = state.get("max_questions", 5)

    if question_count >= max_questions:
        return "done"
    return "continue"
```

---

## 5. Düğüm Fonksiyonları

### Düğüm 1 — `generate_question` (Interview)

**`backend/langgraph_interview/nodes.py`** — satır 70

```python
def generate_question(state: dict) -> dict:
    """Şirket, pozisyon ve mevcut zorluğa göre AI ile soru üret."""
    llm           = get_llm()
    company       = state.get("company", "Genel")
    position      = state.get("position", "Yazılım Mühendisi Stajyeri")
    category      = state.get("category", "technical")
    difficulty    = state.get("difficulty", "medium")
    question_count = state.get("question_count", 0)
    messages      = state.get("messages", [])

    if not llm:
        return _fallback_question(category, question_count, difficulty)

    # Son 4 mesajı context olarak ver — tekrar eden soru üretimini önler
    prev_context = ""
    if messages:
        recent = messages[-4:]
        prev_context = "\n".join(
            [f"{'Soru' if m['role']=='assistant' else 'Cevap'}: {m['content'][:200]}"
             for m in recent]
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
    prompt += "\nSadece soruyu yaz, başka açıklama ekleme. Türkçe yaz."

    response = llm.invoke(prompt)
    question  = response.content.strip()

    return {
        "current_question": question,
        "question_count":   question_count + 1,
        "messages":         [{"role": "assistant", "content": question}],  # Birikmeli listeye eklenir
        "phase":            "questioning",
    }
```

### Düğüm 2 — `evaluate_answer` (Interview)

**`backend/langgraph_interview/nodes.py`** — satır 118

```python
def evaluate_answer(state: dict) -> dict:
    """Kullanıcının cevabını AI ile puanla ve geri bildirim üret."""
    llm      = get_llm()
    question = state.get("current_question", "")
    answer   = state.get("user_answer", "")
    company  = state.get("company", "Genel")

    if not llm:
        return _fallback_evaluate(answer)

    prompt = (
        f"Sen bir mülakat değerlendiricisisin. Aşağıdaki soruya verilen cevabı değerlendir.\n\n"
        f"Şirket: {company}\nSoru: {question}\nCevap: {answer}\n\n"
        f"Aşağıdaki JSON formatında yanıt ver (sadece JSON):\n"
        '{{\n'
        '  "score": <0-100 arası puan>,\n'
        '  "feedback": "<2-3 cümle Türkçe geri bildirim>",\n'
        '  "strengths": "<güçlü yanlar, kısa>",\n'
        '  "improvements": "<geliştirilmesi gerekenler, kısa>"\n'
        '}}'
    )

    response = llm.invoke(prompt)
    text     = response.content.strip()

    # Gemini bazen markdown kod bloğu içine sarıyor — temizle
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    try:
        result   = json.loads(text.strip())
        score    = result.get("score", 60)
        feedback = result.get("feedback", "Değerlendirme tamamlandı.")
        if result.get("strengths"):
            feedback += f"\n\n💪 Güçlü: {result['strengths']}"
        if result.get("improvements"):
            feedback += f"\n\n📈 Geliştir: {result['improvements']}"
    except json.JSONDecodeError:
        score, feedback = 60, text

    return {
        "feedback": feedback,
        "scores":   [score],                                           # Birikmeli listeye eklenir
        "messages": [{"role": "user", "content": answer}],            # Birikmeli listeye eklenir
    }
```

### Düğüm 3 — `analyze_listing` (Workflow)

**`backend/langgraph_workflow/nodes.py`** — satır 121

```python
def analyze_listing(state: dict) -> dict:
    """İlan verilerini JSON'dan yükle, gereksinimler çıkar."""
    listing_id = state.get("listing_id", 1)

    with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
        listings = json.load(f)

    listing = next((l for l in listings if l["id"] == listing_id), None)
    if not listing:
        listing = listings[0] if listings else {}

    requirements = listing.get("requirements", [])
    tags         = listing.get("tags", [])
    description  = listing.get("description", "")

    # Sadece kendi alanlarını döndürür — geri kalan state değişmez
    return {
        "listing_data":    listing,
        "job_requirements": requirements + tags,
        "job_description": description,
        "company_name":    listing.get("company", "Bilinmeyen"),
    }
```

### Düğüm 2 — `evaluate_cv` (Workflow, Gemini ile)

**`backend/langgraph_workflow/nodes.py`** — satır 150

```python
def evaluate_cv(state: dict) -> dict:
    """CV'yi ilana karşı Gemini ile değerlendir."""
    llm               = get_llm()        # Gemini istemcisi veya None
    cv_text           = state.get("cv_text", "")
    candidate_profile = state.get("candidate_profile", {})   # Kayıtlı profil
    job_desc          = state.get("job_description", "")
    requirements      = state.get("job_requirements", [])
    company           = state.get("company_name", "")

    if not llm:
        return _fallback_cv_eval(cv_text, requirements)   # API yoksa keyword matching

    profile_context = _format_candidate_profile(candidate_profile)

    prompt = (
        "Sen deneyimli bir teknik kariyer danismanisin. Bir stajyer adayin uygunlugunu "
        "yalnizca birebir anahtar kelime eslesmesine gore degil, teknoloji benzerligi, "
        "proje deneyimi, aktarilabilir beceri ve egitim baglamina gore degerlendir.\n"
        "Ornek: PostgreSQL -> SQL icin guclu eslesme, "
        "Next.js -> React icin aktarilabilir frontend deneyimi.\n\n"
        f"Şirket: {company}\n"
        f"İlan Gereksinimleri: {', '.join(requirements[:10])}\n"
        f"İlan Açıklaması: {job_desc[:1000]}\n\n"
        f"Aday Profil Ozeti:\n{profile_context}\n\n"    # Ham metin + yapılandırılmış profil
        f"Ham CV Metni:\n{cv_text[:2500]}\n\n"
        f"JSON formatında yanıt ver:\n"
        '{"score": <0-100>, "matched_skills": [...], '
        '"transferable_skills": [...], "missing_skills": [...], '
        '"strengths": [...], "risks": [...], "summary": "..."}'
    )

    try:
        result = _extract_json_payload(_invoke_model_text(llm, prompt))
    except Exception:
        return _fallback_cv_eval(cv_text, requirements)

    score = max(40, min(95, int(result.get("score", 65))))   # 40-95 aralığına sıkıştır

    return {
        "cv_score":        score,
        "cv_analysis":     result,
        "needs_improvement": score < 70,    # Router bunu okuyacak
        "status":          "ai",
        "llm_provider":    "gemini",
    }
```

**Neden `max(40, min(95, score))`?** Gemini bazen 10 veya 98 gibi uç değerler veriyordu. Gerçekçi bir staj başvurusu için 40 altı veya 95 üstü skorlar anlamsız — sıkıştırma ile kullanıcı deneyimi daha tutarlı hale geliyor.

### Düğüm 5 — `suggest_improvements` (Workflow)

**`backend/langgraph_workflow/nodes.py`** — satır 220

```python
def suggest_improvements(state: dict) -> dict:
    """Düşük CV skoru için şirkete özgü iyileştirme önerileri üret."""
    llm               = get_llm()
    cv_analysis       = state.get("cv_analysis", {})
    candidate_profile = state.get("candidate_profile", {})
    company           = state.get("company_name", "")
    requirements      = state.get("job_requirements", [])

    if not llm:
        missing = cv_analysis.get("missing_skills", requirements[:3])
        return {
            "cv_suggestions": [
                f"Şu becerileri CV'nize ekleyin: {', '.join(missing[:4])}",
                "Proje açıklamalarınıza somut metrikler ekleyin (ör: '%30 performans artışı')",
                f"{company} için özelleştirilmiş bir summary bölümü yazın",
            ],
            "llm_provider": "fallback",
        }

    missing      = cv_analysis.get("missing_skills", [])
    transferable = cv_analysis.get("transferable_skills", [])

    prompt = (
        f"Sen bir CV uzmanısın. {company} şirketine başvuru için CV'yi daha güçlü hale getireceksin.\n"
        f"Aday becerileri: {', '.join(candidate_profile.get('skills', []))}\n"
        f"Eksik beceriler: {', '.join(missing)}\n"
        f"Aktarılabilir beceriler: {', '.join(transferable)}\n"
        f"İlan gereksinimleri: {', '.join(requirements[:8])}\n\n"
        "5 adet spesifik, uygulanabilir Türkçe CV iyileştirme önerisi ver.\n"
        "Öneriler genel tavsiye olmasın; adayın projelerini ve becerilerini "
        f"{company} bağlamında nasıl konumlayacağını anlatsın.\n"
        "Her öneriyi yeni satırda, madde işaretiyle yaz."
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
        return {"cv_suggestions": [...], "llm_provider": "fallback"}
```

Bu düğüm sadece `check_cv_score` router'ı `"needs_improvement"` döndürdüğünde çalışır — skor ≥ 70 ise tamamen atlanır.

### Düğüm 6 — `research_company` (Workflow)

**`backend/langgraph_workflow/nodes.py`** — satır 276

```python
def research_company(state: dict) -> dict:
    """Şirket bilgisini companies.json'dan yükle."""
    company_name    = state.get("company_name", "")
    normalized_name = normalize_company_name(company_name)

    with open(COMPANIES_PATH, "r", encoding="utf-8") as f:
        companies = json.load(f)

    company = next(
        (c for c in companies if normalize_company_name(c["name"]) == normalized_name),
        None,
    )

    if company:
        return {
            "company_info": {
                "name":           company["name"],
                "industry":       company["industry"],
                "rating":         company["rating"],
                "tech_stack":     company["tech_stack"],
                "culture":        company["culture"],
                "interview_style": company["interview_style"],
            }
        }

    # Şirket bulunamazsa genel fallback
    return {
        "company_info": {
            "name":           company_name,
            "culture":        "Bilgi mevcut değil — şirketin kariyer sayfasını inceleyin.",
            "interview_style": "Standart teknik mülakat + HR görüşmesi beklenir.",
            ...
        }
    }
```

Şirket ismi normalizasyonu ayrı bir yardımcı fonksiyon ile yapılır:

```python
# nodes.py — satır 22
def normalize_company_name(value: str) -> str:
    """Büyük-küçük harf, kısa çizgi, parantez içi ekler gibi farklılıkları temizle."""
    cleaned = (value or "").strip().lower()
    if "(" in cleaned:
        cleaned = cleaned.split("(", 1)[0].strip()   # "HAVELSAN (Ankara)" → "havelsan"
    return " ".join(cleaned.replace("-", " ").split())
```

**Neden normalizasyon?** Veri setindeki şirket adı `"HAVELSAN A.Ş."` iken kullanıcı `"Havelsan"` yazabilir. Normalizasyon olmadan `next(...)` her zaman `None` döner ve genel fallback devreye girer. Fuzzy matching yerine bu basit kurala dayalı temizleme, veri setimiz için yeterli.

### Düğüm 7 — `generate_interview_prep` (Workflow)

**`backend/langgraph_workflow/nodes.py`** — satır 324

```python
def generate_interview_prep(state: dict) -> dict:
    """Şirkete ve adayın profillerine göre iki kategoride mülakat soruları üret."""
    llm               = get_llm()
    company_info      = state.get("company_info", {})
    candidate_profile = state.get("candidate_profile", {})
    company_name      = company_info.get("name", "Genel")
    tech_stack        = company_info.get("tech_stack", [])
    interview_style   = company_info.get("interview_style", "")

    project_titles = ", ".join(
        project.get("title", "") for project in candidate_profile.get("projects", [])[:4]
    )

    prompt = (
        f"Sen bir mülakat koçusun. {company_name} şirketi için staj mülakatına hazırlık soruları oluştur.\n\n"
        f"Tech stack: {', '.join(tech_stack)}\n"
        f"Mülakat tarzı: {interview_style}\n"
        f"Adayın becerileri: {', '.join(candidate_profile.get('skills', []))}\n"
        f"Adayın projeleri: {project_titles}\n\n"
        "İki kategori halinde toplam 6 soru üret:\n"
        "1. cv_specific: Adayın CV'sindeki projelere dayalı 3 soru.\n"
        "2. company_specific: Bu role başvuran adaylara şirketin sorma ihtimali yüksek 3 soru.\n"
        "Yanıt formatın sadece JSON olsun:\n"
        '{"cv_specific": ["..."], "company_specific": ["..."]}'
    )

    try:
        payload        = _extract_json_payload(_invoke_model_text(llm, prompt))
        cv_specific    = payload.get("cv_specific", [])
        company_specific = payload.get("company_specific", [])
    except Exception:
        cv_specific, company_specific = [], []

    return {
        "interview_questions": (cv_specific + company_specific)[:6],
        "interview_sections":  {
            "cv_specific":      cv_specific[:3],
            "company_specific": company_specific[:3],
        },
        "llm_provider": "gemini",
    }
```

**Neden iki kategori?** CV'ye dayalı sorular adayı kendi deneyimini anlatmaya yönlendirirken, şirket odaklı sorular gerçek mülakata özgü beklentileri yansıtır. Birini diğerinin yerine koymak, hazırlığı eksik bırakırdı.

### Düğüm 8 — `create_action_plan` (Workflow)

**`backend/langgraph_workflow/nodes.py`** — satır 407

```python
def create_action_plan(state: dict) -> dict:
    """Tüm düğümlerin çıktısını okuyarak 5 adımlı kişiselleştirilmiş aksiyon planı sentezle."""
    llm               = get_llm()
    listing           = state.get("listing_data", {})
    cv_score          = state.get("cv_score", 0)
    cv_analysis       = state.get("cv_analysis", {})
    cv_suggestions    = state.get("cv_suggestions", [])
    company_info      = state.get("company_info", {})
    candidate_profile = state.get("candidate_profile", {})
    company_name      = company_info.get("name", "")

    prompt = (
        f"Sen bir kariyer danışmanısın. Kişiselleştirilmiş bir başvuru aksiyon planı oluştur.\n\n"
        f"Pozisyon: {listing.get('position')} @ {company_name}\n"
        f"CV Skoru: {cv_score}/100\n"
        f"Eksikler: {', '.join(cv_analysis.get('missing_skills', []))}\n"
        f"Aktarılabilir beceriler: {', '.join(cv_analysis.get('transferable_skills', []))}\n"
        f"Şirket Tech Stack: {', '.join(company_info.get('tech_stack', []))}\n"
        f"Adayın projeleri: {', '.join(p.get('title','') for p in candidate_profile.get('projects',[])[:4])}\n"
        f"CV önerileri: {'; '.join(cv_suggestions[:4])}\n\n"
        "JSON formatında 5 adımlı aksiyon planı oluştur:\n"
        '{"readiness_score": ..., "steps": [{"step": 1, "title": "...", "description": "..."},...], "summary": "..."}'
    )

    try:
        plan = _extract_json_payload(_invoke_model_text(llm, prompt))
    except Exception:
        plan = {"readiness_score": cv_score, "steps": [...], "summary": "..."}

    plan["position"] = listing.get("position", "Stajyer")
    plan["company"]  = company_name

    return {"action_plan": plan, "llm_provider": "gemini"}
```

Bu düğüm workflow'un **son düğümü** — önceki tüm düğümlerin state'e yazdığı verileri (`cv_score`, `cv_analysis`, `cv_suggestions`, `company_info`, `candidate_profile`) okuyarak sentezler. LangGraph'ın state biriktirme mekanizması sayesinde bu düğüm hiçbir ayrı parametre almadan tüm bağlama erişebilir.

### Düğüm 9 — `adjust_difficulty` (Interview)

**`backend/langgraph_interview/nodes.py`** — satır 173

```python
def adjust_difficulty(state: dict) -> dict:
    """Son 2 cevabın ortalamasına göre zorluğu dinamik ayarla."""
    scores  = state.get("scores", [])
    current = state.get("difficulty", "medium")

    if len(scores) < 2:          # Henüz yeterli veri yok
        return {"difficulty": current}

    avg_recent = sum(scores[-2:]) / 2    # Sliding window — son 2 puan

    if avg_recent >= 80:
        new_diff = "hard"
    elif avg_recent >= 50:
        new_diff = "medium"
    else:
        new_diff = "easy"

    return {"difficulty": new_diff}
```

**Neden son 2 puanın ortalaması?** Tek puana göre zorluk değiştirmek çok hassas olurdu — bir soruyu yanlış anlayan kullanıcı haksız yere "easy"'e düşerdi. İki puanın sliding window'u hem anlık başarısızlığa hem anlık şansa karşı daha kararlı. Daha uzun bir pencere (5 puan) ise geç tepki verirdi.

### Düğüm 4 — `generate_summary` (Interview)

**`backend/langgraph_interview/nodes.py`** — satır 211

```python
def generate_summary(state: dict) -> dict:
    """Tüm mülakat performansını özetle."""
    llm        = get_llm()
    scores     = state.get("scores", [])
    messages   = state.get("messages", [])    # Tüm birikmiş konuşma geçmişi
    company    = state.get("company", "Genel")
    avg_score  = sum(scores) / len(scores) if scores else 0

    if not llm:
        return _fallback_summary(scores, avg_score)

    # Tüm konuşmadan son 10 mesajı al (token limiti)
    conversation = "\n".join(
        [f"{'Soru' if m['role']=='assistant' else 'Cevap'}: {m['content'][:200]}"
         for m in messages[-10:]]
    )

    prompt = (
        f"Sen bir mülakat koçusun. Aşağıdaki mülakat performansını özetle.\n\n"
        f"Şirket: {company}\n"
        f"Toplam soru: {len(scores)}\n"
        f"Puanlar: {scores}\n"
        f"Ortalama: {avg_score:.0f}/100\n\n"
        f"Konuşma:\n{conversation[:2000]}\n\n"
        "3-4 cümlelik Türkçe bir özet yaz. Güçlü yanları, gelişim alanlarını "
        "ve genel tavsiyeni belirt."
    )

    response = llm.invoke(prompt)
    return {
        "summary": response.content.strip(),
        "phase":   "completed",
    }
```

---

## 6. Grafların API Endpoint'lerinden Çağrılması

### Workflow Endpoint'i

**`backend/routers/workflow.py`** — satır 29

```python
from langgraph_workflow.graph import workflow_graph

@router.post("/workflow/prepare")
async def prepare_application(req: PrepareRequest, authorization: str | None = Header(default=None)):
    # --- CV kaynağını belirle ---
    cv_text = req.cv_text.strip()
    cv_source = "manual"

    if not cv_text:
        user    = get_authenticated_user(authorization)     # Supabase JWT doğrulama
        profile = get_profile(str(user.id)) if user else None
        saved_cv = profile.get("cv_text", "") if profile else ""
        if saved_cv.strip():
            cv_text   = saved_cv
            cv_source = "profile"    # Kayıtlı profil kullanıldı

    # --- Initial state oluştur ---
    initial_state = {
        "listing_id":        req.listing_id,
        "cv_text":           cv_text,
        "candidate_profile": candidate_profile,   # Yapılandırılmış profil verisi
        "listing_data":      {},
        "cv_score":          0,
        "needs_improvement": False,
        "status":            "fallback",
        "llm_provider":      "fallback",
        # ... diğer alanlar başlangıç değerleriyle
    }

    # --- Grafı çalıştır (LangSmith tracing ile) ---
    with tracing_context(project_name="InternIQ-Workflow", tags=["langgraph", "workflow"]):
        result = workflow_graph.invoke(
            initial_state,
            config=runnable_config(tags=["langgraph", "workflow"])
        )

    return {
        "cv_score":           result.get("cv_score", 0),
        "cv_analysis":        result.get("cv_analysis", {}),
        "cv_suggestions":     result.get("cv_suggestions", []),
        "interview_sections": result.get("interview_sections", {}),
        "action_plan":        result.get("action_plan", {}),
        "status":             result.get("status", "fallback"),
        "llm_provider":       result.get("llm_provider", "fallback"),
        "cv_source":          cv_source,
    }
```

### Interview Endpoint'leri

**`backend/routers/interview.py`** — satır 109

```python
from langgraph_interview.graph import question_graph, answer_graph

_sessions: dict = {}    # session_id → InterviewState (production'da Redis)

@router.post("/interview/lg/start")
async def lg_start_interview(req: LGStartRequest):
    session_id = str(uuid.uuid4())

    initial_state = {
        "company":        req.company,
        "position":       req.position,
        "category":       req.category,
        "messages":       [],        # Birikmeli — başlangıçta boş
        "scores":         [],        # Birikmeli — başlangıçta boş
        "question_count": 0,
        "max_questions":  req.max_questions,
        "difficulty":     "medium",
        "phase":          "start",
        # ... diğer alanlar
    }

    # Sadece ilk soruyu üretecek tek düğümlü graf
    result = question_graph.invoke(initial_state)
    _sessions[session_id] = result   # State'i sakla

    return {
        "session_id":      session_id,
        "question":        result["current_question"],
        "question_number": result["question_count"],
        "difficulty":      result["difficulty"],
    }


@router.post("/interview/lg/answer")
async def lg_answer_question(req: LGAnswerRequest):
    session = _sessions.get(req.session_id)
    if not session:
        return {"error": "Session not found. Start a new interview."}

    session["user_answer"] = req.answer    # Cevabı state'e yaz

    # 4 adımlı graf: değerlendir → zorluğu ayarla → [router] → soru/özet
    result = answer_graph.invoke(session)
    _sessions[req.session_id] = result     # Güncel state'i kaydet

    if result.get("phase") == "completed":
        del _sessions[req.session_id]      # Mülakat bitti, oturumu temizle
        return {
            "phase":          "completed",
            "summary":        result.get("summary", ""),
            "scores":         result.get("scores", []),
            "average_score":  sum(result["scores"]) / len(result["scores"]),
        }
    else:
        return {
            "phase":           "questioning",
            "feedback":        result.get("feedback", ""),
            "score":           result["scores"][-1],
            "question":        result.get("current_question", ""),
            "question_number": result.get("question_count", 0),
            "difficulty":      result.get("difficulty", "medium"),
        }
```

---

## 7. Profil Entegrasyonu — Kişiselleştirilmiş Analiz

Kullanıcı CV yüklediğinde `profile_store.py` bunu yapılandırılmış veriye dönüştürür. Bu veri `candidate_profile` alanıyla workflow state'ine girer.

### CV Kaynağı Belirleme Mantığı

**`backend/routers/workflow.py`** — satır 46

```python
cv_text   = req.cv_text.strip()
cv_source = "manual"

if not cv_text:
    user    = get_authenticated_user(authorization)
    profile = get_profile(str(user.id)) if user else None
    saved_cv = profile.get("cv_text", "") if profile else ""

    if saved_cv.strip():
        cv_text   = saved_cv
        cv_source = "profile"    # Kayıtlı profil kullanıldı
    else:
        cv_source = "empty"

# Kaynağa göre candidate_profile oluştur
if profile and cv_source == "profile":
    candidate_profile = {
        "summary":          profile.get("summary", ""),
        "skills":           profile.get("skills", []),
        "education_summary": profile.get("education_summary", ""),
        "experience_level": profile.get("experience_level", ""),
        "projects":         profile.get("projects", []),
    }
elif cv_text.strip():
    candidate_profile = summarize_cv_profile(cv_text)   # Anlık çıkarım
else:
    candidate_profile = {"summary": "", "skills": [], ...}
```

### Profil State'e Yansıması

**`backend/langgraph_workflow/state.py`**

```python
class WorkflowState(TypedDict):
    cv_text:           str     # Ham metin
    candidate_profile: dict   # ← Yapılandırılmış profil buradan gelir
    # ...
```

`evaluate_cv` ve `generate_interview_prep` düğümleri bu iki alanı birlikte kullanır. Ham CV metni Gemini'nin tokenlarını tüketirken, yapılandırılmış profil ("Projeler: InternIQ, Beceriler: Python, React") çok daha az token ile çok daha anlamlı context sağlar.

### `evaluate_cv` Prompt'unun Tasarımı

**`backend/langgraph_workflow/nodes.py`** — satır 167

```python
prompt = (
    "Sen deneyimli bir teknik kariyer danismanisin. Bir stajyer adayin uygunlugunu "
    "yalnizca birebir anahtar kelime eslesmesine gore degil, teknoloji benzerligi, "
    "proje deneyimi, aktarilabilir beceri ve egitim baglamina gore degerlendir.\n"
    "Ornek: PostgreSQL -> SQL icin guclu eslesme, "       # ← Transfer beceri örnekleri
    "Next.js -> React icin aktarilabilir frontend deneyimi.\n"
    "Skoru gercekci ver ama gereksiz sert olma.\n\n"      # ← Uç değerleri önlemek için
    ...
)
```

**Neden bu satırlar prompt'a eklendi?** İlk versiyonda Gemini birebir keyword eşleşmesi yapıyordu — PostgreSQL bilen bir aday SQL arayan bir ilana çok düşük skor alıyordu. Prompt'a transfer beceri örnekleri eklenince değerlendirme çok daha gerçekçi ve kullanışlı hale geldi. "Gereksiz sert olma" yönlendirmesi ise Gemini'nin stajyer adaylarını fazla düşük puanlamasını engelledi.

---

## 8. Fallback Mimarisi

### LLM Yükleme Fonksiyonu

**`backend/langgraph_workflow/nodes.py`** — satır 31

```python
def get_llm():
    """Gemini istemcisini döndür, API anahtarı yoksa None."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_key_here":
        return None

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Model öncelik listesi — birincil başarısız olursa sıradakini dener
    preferred_model  = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fallback_models  = [
        "models/gemini-flash-lite-latest",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash",
    ]
    ordered_models = [preferred_model] + [m for m in fallback_models if m != preferred_model]
    return {"genai": genai, "models": ordered_models}
```

**`backend/langgraph_workflow/nodes.py`** — `_invoke_model_text` — satır 48

```python
def _invoke_model_text(model, prompt: str) -> str:
    """Model listesini sırayla dene — bir başarısız olursa sonrakine geç."""
    last_error = None

    for model_name in model["models"]:
        try:
            response = model["genai"].GenerativeModel(model_name).generate_content(prompt)
            text = getattr(response, "text", "").strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc
            continue    # Bu model başarısız, sıradakini dene

    if last_error:
        raise last_error
    return ""
```

### Her Düğümde Fallback Deseni

**`backend/langgraph_workflow/nodes.py`** — `evaluate_cv`

```python
def evaluate_cv(state: dict) -> dict:
    llm = get_llm()
    if not llm:
        return _fallback_cv_eval(cv_text, requirements)   # ← Keyword matching
    # ... Gemini ile gerçek analiz
```

**`backend/langgraph_workflow/nodes.py`** — `_fallback_cv_eval`

```python
def _fallback_cv_eval(cv_text, requirements):
    """API yoksa basit keyword eşleştirmesi yap."""
    cv_lower = cv_text.lower()
    matched  = [r for r in requirements if r.lower() in cv_lower]
    missing  = [r for r in requirements if r.lower() not in cv_lower]
    total    = len(matched) + len(missing)
    score    = int((len(matched) / max(total, 1)) * 100) if total > 0 else 55
    score    = max(40, min(95, score))

    return {
        "cv_score":        score,
        "cv_analysis":     {"matched_skills": matched, "missing_skills": missing, ...},
        "needs_improvement": score < 70,
        "status":          "fallback",
        "llm_provider":    "fallback",
    }
```

**Neden bu yaklaşım?** Hem geliştirme ortamında (API anahtarı olmadan test) hem de production'da API limiti veya kesinti durumunda kullanıcı hata görmez — düşük kalitede ama tutarlı bir çıktı alır.

### Provider Takibi

Her düğüm, çıktısında hangi yolu izlediğini state'e yazar:

```python
# Gerçek AI kullanıldığında — evaluate_cv, nodes.py
return {
    "cv_score":     score,
    "status":       "ai",
    "llm_provider": "gemini",   # ← Hangi model kullanıldı
}

# Fallback kullanıldığında — _fallback_cv_eval, nodes.py
return {
    "cv_score":     score,
    "status":       "fallback",
    "llm_provider": "fallback",
}
```

Router, graf çalıştıktan sonra son state'i okuyarak tutarlı bir `llm_provider` değeri normalize eder:

**`backend/routers/workflow.py`** — satır 122

```python
final_status   = result.get("status", "fallback")
final_provider = result.get("llm_provider", "fallback") if final_status == "ai" else "fallback"

return {
    ...
    "status":       final_status,    # "ai" veya "fallback"
    "llm_provider": final_provider,  # "gemini" veya "fallback"
}
```

**Neden bu ayrım?** Frontend bu bilgiyi kullanarak kullanıcıya "AI ile analiz edildi" veya "Demo mod" gösterebilir. Ayrıca hangi düğümün fallback'e düştüğü LangSmith trace'inde görülebildiğinden, hangi API çağrısının başarısız olduğu kolayca tespit edilebilir.

---

## 9. LangSmith Gözlemlenebilirliği

### Servis Katmanı

**`backend/services/langsmith_tracing.py`**

```python
from contextlib import nullcontext
import langsmith as ls

def is_langsmith_enabled() -> bool:
    """Hem LANGSMITH_TRACING=true hem de API anahtarı varsa True döner."""
    tracing_enabled = (
        _is_truthy(os.getenv("LANGSMITH_TRACING"))
        or _is_truthy(os.getenv("LANGCHAIN_TRACING_V2"))   # Geriye uyumluluk
    )
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    return tracing_enabled and bool(api_key)


def tracing_context(project_name, tags=None, metadata=None):
    """LangSmith context manager döndür — anahtar yoksa no-op (nullcontext)."""
    if not is_langsmith_enabled():
        return nullcontext()    # ← Anahtar yoksa hiçbir şey yapmaz, sistem çalışır

    return ls.tracing_context(
        enabled=True,
        project_name=project_name,
        tags=tags or [],
        metadata=metadata or {},
    )


def runnable_config(tags=None, metadata=None) -> dict:
    """LangGraph'ın invoke() çağrısına geçirilecek config sözlüğü."""
    config = {}
    if tags:     config["tags"]     = tags
    if metadata: config["metadata"] = metadata
    return config
```

### Endpoint'lerde Kullanım

**`backend/routers/workflow.py`** — satır 113

```python
from services.langsmith_tracing import get_langsmith_project, runnable_config, tracing_context

trace_tags     = ["langgraph", "workflow", "application-prep"]
trace_metadata = {"listing_id": req.listing_id, "cv_source": cv_source}

with tracing_context(
    project_name=get_langsmith_project("InternIQ-Workflow"),
    tags=trace_tags,
    metadata=trace_metadata,
):
    result = workflow_graph.invoke(
        initial_state,
        config=runnable_config(tags=trace_tags, metadata=trace_metadata),
    )
```

**`backend/routers/interview.py`** — satır 145 (start endpoint'i)

```python
with tracing_context(
    project_name=get_langsmith_project("InternIQ-Interview"),
    tags=["langgraph", "interview", "start"],
    metadata={"company": req.company, "max_questions": req.max_questions},
):
    result = question_graph.invoke(initial_state, config=runnable_config(...))
```

**Neden `nullcontext` fallback?** Tracing servisini koşullu bir `if` ile sarmak yerine `nullcontext` kullanmak, tracing olmayan ortamlarda da aynı `with` bloğunun sorunsuz çalışmasını sağlar. Tek satır değişiklik ile tüm endpoint'lerde opsiyonel tracing elde ediliyor.

---

## 10. Ortam Değişkeni Yükleme Düzeltmesi

**`backend/main.py`** — satır 11

```python
from pathlib import Path
from dotenv import load_dotenv

def load_local_env() -> None:
    """
    backend/.env dosyasını kesin yoldan yükle.
    python-dotenv, uvicorn çalışma dizinine göre yolu hesaplar
    ve bazen .env'yi atlayabiliyor.
    """
    env_path = Path(__file__).resolve().parent / ".env"   # main.py'ye göreli, her zaman doğru
    if not env_path.exists():
        return

    load_dotenv(env_path, override=False)

    if os.getenv("GEMINI_API_KEY"):    # Başarıyla yüklendiyse dur
        return

    # python-dotenv'in kaçırdığı kenar durum için manuel parse
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())   # override=False ile aynı davranış


load_local_env()    # ← Tüm router importlarından ÖNCE çalışır
```

**Neden `__file__` kullanıldı?** `os.getcwd()` veya göreceli yol, `uvicorn`'un nereden çalıştırıldığına bağlıdır. `Path(__file__).resolve().parent` her zaman `main.py`'nin bulunduğu klasörü — yani `backend/` — gösterir. **Neden `setdefault`?** Render gibi deploy platformları env var'ları zaten sistem ortamına yükler; `setdefault` bu değerlerin üzerine yazmaz.

---

## Özet: Mimari Kararlar

| Karar | İlgili Dosya | Neden |
|---|---|---|
| LangGraph + CrewAI birlikte | `routers/workflow.py`, `routers/crew.py` | Deterministik akış için LangGraph, özerk araştırma için CrewAI |
| 2 ayrı graf (question + answer) | `langgraph_interview/graph.py` | İlk soru için değerlendirme adımları gereksiz — sorumluluklar ayrı |
| `TypedDict` state | `langgraph_*/state.py` | Tür güvencesi, IDE desteği, state şeması dokümantasyon görevi görüyor |
| `Annotated[list, operator.add]` | `langgraph_interview/state.py` | Mesajlar ve puanlar üzerine yazılmadan birikir |
| CV skoru için conditional edge | `langgraph_workflow/graph.py:53` | Graf topolojisi kararı koddan ayırır; router saf fonksiyon olarak test edilebilir |
| Her düğümde fallback | `langgraph_*/nodes.py` | API yoksa sistem çökmez, düşük kaliteli ama tutarlı çıktı döner |
| Model öncelik listesi | `langgraph_workflow/nodes.py:38` | Birincil Gemini modeli başarısız olursa sıradaki denenir |
| LangSmith `nullcontext` | `services/langsmith_tracing.py:45` | Tracing opsiyonel — anahtar olmadan da sistem bozulmuyor |
| `Path(__file__)` ile env yükleme | `backend/main.py:14` | Çalışma dizininden bağımsız, her ortamda doğru `.env` bulunur |
| Yapılandırılmış `candidate_profile` | `langgraph_workflow/state.py`, `routers/workflow.py` | Ham metin yerine çıkarılmış beceri/proje verisi Gemini'ye daha az tokenla daha anlamlı context sağlar |
