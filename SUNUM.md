# InternIQ — Sunum Script'i

> Üniversite öğrencileri için AI destekli staj başvuru platformu.
> Süre hedefi: 12-15 dakika.
> Yapı: dersin **4 ödevi boyunca** ne eklendiğini sırayla göstereceğim — her bölümde
> *hangi teknoloji geldi*, *projeye hangi feature olarak işlendi*, *kodda nerede*.

---

## 0) Açılış (45 sn)

> "Merhaba, ben Burak. Bugün **InternIQ**'yu anlatacağım — staj arayan
> üniversite öğrencileri için AI platformu. Projeyi tek seferde değil,
> dersin **4 ödevi boyunca katmanlı** geliştirdim. Her ödevde dersin
> o haftaki konusunu (OpenAI SDK, CrewAI, LangGraph, MCP) gerçek bir
> kullanım senaryosuna oturttum. Bugün bu yolculuğu göstereceğim."

**Soru-tetik:** "Kaçınız staj başvururken her ilana göre CV'nizi tek tek
ayarlamak zorunda kaldı?" → InternIQ bu döngüyü otomatize ediyor.

**Açılış demosu (15 sn):** `/` anasayfayı aç, brutalist-modern tema
göster, **Timeline** bölümüne kaydır → dersin haftalarını/ödevlerini
ekranda göster. *"Bugün bu timeline'i takip edeceğiz."*

> Kod referansı: `src/components/Timeline.jsx:4-30`

---

## 1) Ödev 1 — Planlama + Frontend Draft (1.5 dk)

### Konu
Proje fikri, hedef kullanıcı, mimari plan, draft UI.

### Ne yapıldı
- 4 modül olarak InternIQ tasarlandı: **Staj Radar**, **CV Tailorer**, **Company Intel**, **Mock Interview**
- Tam frontend (React + Vite + React Router) — auth dahil
- Backend iskeleti (FastAPI) — tüm endpoint'ler stub
- Static JSON data: `backend/data/listings.json`, `companies.json`

### Kodda nerede
| Bölüm | Dosya |
|---|---|
| Planlama dökümanı | `docs/AI_Agent_Planning.md` |
| Frontend giriş noktası | `src/main.jsx`, `src/App.jsx` |
| Sayfa rotaları | `src/pages/*.jsx` (HomePage, ListingDetail, CompanyResearch, AccountPage…) |
| Bileşenler | `src/components/*.jsx` (Hero, BentoGrid, Timeline, ListingList…) |
| Logo | `src/components/Logo.jsx` (custom SVG, 5-square matrix) |
| Tasarım sistemi | `src/index.css` (brutalist-modern dark, amber accent) |
| Backend giriş | `backend/main.py` |
| Auth + profil | `src/context/AuthContext.jsx`, `backend/services/profile_store.py` |

### Demo (30 sn)
- Anasayfayı göster — Hero, BentoGrid, Timeline
- `/ilanlar` → ListingList (filtre + arama)
- Kayıtlı kullanıcı ile `Hesabım` sayfasına gir → CV özeti, skills, projects

> *"Burası 'kabuk' — AI gelmeden önce ürünün şeklini oturttuk. Sonraki
> 3 ödevde içine sırayla zekâ ekleyeceğiz."*

---

## 2) Ödev 2 — CrewAI Multi-Agent Company Intel (2.5 dk)

### Konu
**CrewAI** ile çoklu-ajan iş birliği.

### Ne yapıldı
3 ajanlı sequential bir crew kuruldu, **Company Intel** modülünü gerçekten
AI'lı yapan kısım bu:
1. **Culture Researcher** — şirket kültürü, çalışma ortamı
2. **Tech Analyst** — teknoloji yığını, mühendislik pratiği
3. **Report Writer** — diğer iki ajanın çıktısını yapılandırılmış JSON rapora sentezler

### Kodda nerede
| Bölüm | Dosya | Açıklama |
|---|---|---|
| Crew tanımı + run_crew() | `backend/crew/company_crew.py` | Ana entry point, fallback dahil |
| Ajan tanımları | `backend/crew/config/agents.yaml` | role / goal / backstory |
| Görev tanımları | `backend/crew/config/tasks.yaml` | description + expected_output |
| API endpoint | `backend/routers/crew.py` | `POST /api/v1/crew/research` |
| Frontend | `src/components/CompanyCards.jsx`, `src/pages/CompanyResearch.jsx` | Şirket kartı + rapor görünümü |
| LLM | `LLM(model="gpt-4o-mini")` — `company_crew.py:148` |

### Process
```
Culture Researcher  →  Tech Analyst  →  Report Writer
    (kültür)            (tech stack)      (sentez)
```
> "Process.sequential — her ajan bir öncekinin çıktısı üzerine inşa ediyor."

### Demo (45 sn)
- **UI yolu:** `/sirket-arastir` → "ASELSAN" yaz → araştır → 3 ajanın ürettiği rapor (kültür, tech stack, mülakat ipuçları, artılar/eksiler)
- *"Bu raporun arkasında 3 LLM çağrısı var, sırayla. Her ajanın `agents.yaml`'da rolü, hedefi, geçmiş hikâyesi tanımlı."*

### Fallback
> "API key olmadığında `FALLBACK_REPORTS` devreye giriyor (ASELSAN, BAYKAR önceden hazır).
> Bu sayede demo asla kırılmıyor."
- Kod: `company_crew.py:21-101` (FALLBACK_REPORTS sözlüğü)

---

## 3) Ödev 3 — LangGraph Stateful Workflows (3.5 dk)

### Konu
**LangGraph** ile durumlu (stateful) çok-adımlı iş akışları.

### Ne yapıldı
**İki ayrı StateGraph** kuruldu — projeye iki yeni feature olarak girdi:

#### A) Application Preparation Workflow (7 düğüm)
İlana ve CV'ye özel **kişiselleştirilmiş başvuru paketi** üretiyor.

```
START
  → analyze_listing       (ilanı parse, requirement çıkar)
  → evaluate_cv           (CV-ilan uyumu skor 0-100)
  → [check_cv_score]      ← CONDITIONAL EDGE
       ├─ skor < 70 → suggest_improvements → research_company
       └─ skor ≥ 70 ────────────────────────→ research_company
  → research_company      (yerel data + opsiyonel CrewAI)
  → generate_interview_prep (pozisyona özel sorular)
  → create_action_plan    (5 adımlı kişisel yol haritası)
  → END
```

#### B) Mock Interview — 2 ayrı graph
- **`question_graph`** — soru üretimi
- **`answer_graph`** — cevap değerlendirme + zorluk ayarı + sonraki soruya yönlendirme
- *"Cevap iyiyse zorluk artar, kötüyse azalır — adaptive interview."*

#### Bonus: Auth + CV profil katmanı
LangGraph workflow'larını anlamlı kılmak için kullanıcı CV'sini kalıcı sakla:
- `register` / `login` / `profile`
- Kullanıcı CV'sini bir kez yükler → her workflow'da kullanılır

### Kodda nerede
| Bölüm | Dosya |
|---|---|
| **Workflow graph** | `backend/langgraph_workflow/graph.py` |
| Workflow düğümleri | `backend/langgraph_workflow/nodes.py` (7 fonksiyon) |
| Workflow state | `backend/langgraph_workflow/state.py` (TypedDict) |
| **Interview graphs** | `backend/langgraph_interview/graph.py` (`question_graph`, `answer_graph`) |
| Interview düğümleri | `backend/langgraph_interview/nodes.py` (5 fonksiyon) |
| API — workflow | `backend/routers/workflow.py` → `POST /workflow/prepare` |
| API — interview | `backend/routers/interview.py` → `POST /interview/lg/start`, `/lg/answer` |
| Frontend — workflow | `src/components/ApplicationWorkflow.jsx` (Hazırla butonu) |
| Frontend — interview | `src/components/MockInterview.jsx` |
| **LangSmith tracing** | `backend/services/langsmith_tracing.py` |
| LLM | `ChatOpenAI(model="gpt-4o-mini", max_tokens=1200)` — `nodes.py:36` |

### Demo (1.5 dk)

#### Workflow demo
- `/ilanlar/1` (ASELSAN) → **"Hazırla"** butonu
- *"Bu butona basınca arka planda 7 düğümlü LangGraph çalışıyor. Conditional edge sayesinde CV skoru iyiyse improvement node'una gitmiyor — token tasarrufu."*
- Sonuç ekranı: skor, eksik beceriler, CV önerileri, mülakat soruları, action plan
- (Opsiyonel) **LangSmith** dashboard aç → her node'un timing'i görünür: *"Observability free."*

#### Interview demo
- `/mulakat` → AI mod
- "Başla" → ilk soru
- Cevap yaz → değerlendirme + sonraki soru (zorluk değişiyor)

### Conditional edge — neden önemli?
> "Klasik linear LLM chain'lerde her adım hep koşar. LangGraph'ın asıl gücü
> *graph yapısı*: koşullu dallanma, döngü, state birikimi. Workflow'umda
> CV skoru >= 70 ise improvement node'unu **atlıyoruz** — `nodes.py:check_cv_score`
> bunu yapan router."

---

## 4) Ödev 4 — MCP — *Final Ödev* (4-5 dk)

> Bu projenin entelektüel olarak en ilginç kısmı.

### Konu
**Model Context Protocol** — Anthropic'in açtığı standart. LLM'lerin
dış sistemlere erişmesi için *USB-C portu* gibi düşün. Tools, resources,
prompts olarak üç şey sunuyor.

### Ne yapıldı

InternIQ'nun **17 yeteneğini** MCP tool olarak expose ettim, ayrıca
**LLM-as-MCP-host** ajanlı bir chat ekledim. Üç ayrı kullanım yolu var:

1. **Frontend `/ajan` sayfası** — tarayıcıdan doğal dil
2. **`interniqmcp` terminal client** — komut satırından
3. **(Tasarımsal)** Claude Desktop'a register edilebilir

### Mimari

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend (/ajan)                                            │
│      ↓ POST /api/v1/agent/chat                                │
│  FastAPI router (backend/routers/agent.py)                    │
│      ↓                                                        │
│  mcp_agent.py  (LLM-as-MCP-host — GPT-4o-mini)               │
│      • LLM'e tool listesini ver (MCP'den keşfet)             │
│      • Loop: LLM tool seç → çağır → sonucu LLM'e ver         │
│      • Max 6 iterasyon, sonra cevap yaz                      │
│      ↓ stdio                                                  │
│  interniq_mcp.py  (FastMCP server)                            │
│      • 17 tools / 2 resources / 1 prompt                     │
│      • Heavy iş yükü → subprocess izolasyonu                 │
└──────────────────────────────────────────────────────────────┘
```

### MCP Server'da neler var? (17 tool)

| Kategori | Tool'lar |
|---|---|
| Discovery | `list_interniq_features`, `search_internships`, `get_listing_context`, `get_company_context` |
| Auth | `register_user`, `login_user`, `logout_user`, `get_current_account` |
| CV | `analyze_cv_for_listing`, `analyze_profile_cv_for_listing` |
| Workflow | `run_application_workflow`, `run_profile_application_workflow` |
| Interview | `start_mock_interview`, `start_profile_mock_interview`, `answer_mock_interview` |
| Research | `run_company_research` (lokal), `run_crewai_research` (CrewAI) |

### Kodda nerede
| Bölüm | Dosya |
|---|---|
| **MCP Server** | `backend/mcp_server/interniq_mcp.py` |
| MCP Client bridge | `backend/services/mcp_bridge.py` |
| **LLM-as-MCP-host ajan** | `backend/services/mcp_agent.py` |
| Terminal client | `backend/services/interniq_terminal.py` (`interniqmcp` komutu) |
| Demo endpoint | `backend/routers/mcp.py` → `POST /mcp/demo` |
| Ajan endpoint | `backend/routers/agent.py` → `POST /agent/chat` |
| Frontend ajan UI | `src/components/AgentChat.jsx`, `AgentChat.css` |
| **Subprocess wrappers** | `backend/crew/_run_crew_subprocess.py`, `backend/langgraph_workflow/_run_workflow_subprocess.py` |

### Önemli design kararı: MCP transport stdio
> "MCP server bir **subprocess** olarak doğuyor (FastMCP, stdin/stdout
> üzerinden JSON-RPC). Yani FastAPI'nin çalışmasına bile gerek yok —
> terminal client direkt MCP server'ı spawn edebiliyor."

### Demo 1 — `/ajan` sayfası (1 dk)

UI'a git: `http://localhost:5173/ajan`

Yaz:
> *"BAYKAR'a backend developer staji icin basvuracagim, hazirlanmama yardim et"*

> "İzleyin: LLM önce `search_internships`'i çağırıyor → BAYKAR'da uygun
> ilan buluyor → `run_application_workflow`'u çağırıyor → tüm sonucu
> Türkçe sentezleyip cevap veriyor. Hepsi otonom, ben tool çağırmıyorum."

Sağ panelde **tool call log'u** görünür — her adım görünür.

### Demo 2 — Terminal client (1 dk)

```powershell
interniqmcp
```

```
InternIQ> tools                        # 17 tool listele
InternIQ> search python remote         # search_internships
InternIQ> login deneme@gmail.com       # login_user
Password: ******
Logged in as deneme@gmail.com
Saved CV: yes
InternIQ> prepare 1                    # ← AKILLI YÖNLENDİRME
Using saved CV for deneme@gmail.com...
=== Yazılım Mühendisliği Stajyeri @ ASELSAN ===
CV Score: 65
[CV Analysis] ...
[CV Suggestions] ...
[Company: ASELSAN] ...
[Interview Questions] ...
[Action Plan] ...
```

> "**`prepare`** komutu giriş yapmışsa otomatik kayıtlı CV'yi kullanıyor —
> bu da bir LangGraph workflow çağrısı, ama MCP üzerinden, ama subprocess
> izolasyonuyla."

### Demo 3 — `crewai` komutu (opsiyonel — zaman varsa)
```
InternIQ> crewai BAYKAR
Running CrewAI agents (1-3 min)...
```
> "MCP üzerinden CrewAI tetikleniyor. ~60 saniyede 3 ajanlı rapor."

---

## 5) Teknik Zorluklar (1.5 dk)

> "Buraya gelmek kolay olmadı. Üç büyük problem yaşadım."

### Problem 1: Windows + asyncio + stdio + httpx hangi
- **Belirti:** MCP üzerinden CrewAI veya LangGraph çağırınca 3+ dakika takılıyor (UI'dan direkt çağırınca çalışıyor!)
- **Sebep:** FastMCP child process'inde, openai SDK'nin **ilk** sync httpx
  request'i Windows'ta asyncio event loop ile çakışıp donuyor
- **Denedik:** httpx warmup, ChatOpenAI warmup → yetmedi
- **Çözüm:** Heavy LLM iş yüklerini **subprocess izolasyonu** ile çalıştır.
  Her CrewAI/LangGraph çağrısı temiz bir Python subprocess'e gönderilir,
  JSON çıktı parse edilir.
  - Kod: `backend/crew/_run_crew_subprocess.py`, `backend/langgraph_workflow/_run_workflow_subprocess.py`
  - Bu pattern aynı zamanda CrewAI'ın verbose rich/emoji output'unun
    MCP JSON-RPC frame'lerini bozmasını da engelliyor.

### Problem 2: Türkçe karakterlerin Windows console'da bozulması
- **Belirti:** Subprocess çıktısında `�` replacement char'lar
- **Sebep:** Windows default code page **cp1254** (Türkçe), UTF-8 değil
- **Çözüm:** Subprocess başlangıcında `sys.stdout.reconfigure(encoding="utf-8")`,
  parent tarafında ham bytes alıp `decode("utf-8", errors="replace")`

### Problem 3: Action plan tekrar ediyordu (prompt engineering)
- **Belirti:** 5 adımdan 3'ü "projeyi vurgula" diyordu
- **Çözüm:** Prompt'ta 5 sabit kategori (Teknik Eksiklik / Portföy /
  Şirket / Mülakat / Başvuru), tekrar yasak, şirket adı en az 2 adımda zorunlu.
  - Kod: `backend/langgraph_workflow/nodes.py` → `create_action_plan` (line 402+)

---

## 6) Kapanış (45 sn)

### Ödev → Feature haritası (özet)
| Ödev | Konu | Projeye katkısı | Asıl dosya |
|---|---|---|---|
| **Ödev 1** | Planlama + Frontend draft | UI iskeleti, auth, data layer | `src/`, `backend/main.py` |
| **Ödev 2** | CrewAI | Company Intel — 3 ajanlı şirket araştırması | `backend/crew/company_crew.py` |
| **Ödev 3** | LangGraph | Application Workflow + Mock Interview (2 graph) | `backend/langgraph_workflow/`, `langgraph_interview/` |
| **Ödev 4** | MCP | 17 tool, LLM-as-MCP-host ajan, terminal client | `backend/mcp_server/interniq_mcp.py`, `services/mcp_agent.py` |

### Ne öğrendim?
- AI framework seçimi: *"Hammer için her şey çivi gibi görünür."* Her
  framework'ü doğru problemde kullandım — CrewAI multi-agent için,
  LangGraph stateful workflow için, MCP standart protokol için.
- MCP: standartlar ürün geliştirmeyi hızlandırıyor. 17 tool yazdım,
  herhangi bir LLM kullanabiliyor.
- Production realities: Windows quirks, Turkish encoding, async/sync
  interaction — kitaba sığmayan şeyler.

### Sonraki adımlar
- Ödev 5'te planlanan **AutoGen** (otonom ilan tarama) eklenebilir
- Vector DB ile semantic CV-ilan eşleştirme
- WhatsApp bot (MCP transport ekle, mevcut tool'ları yeniden kullan)

### Linkler
- **GitHub:** github.com/burakyalcin10/InternIQ
- **Live:** intern-iq-iota.vercel.app
- **API docs:** interniq-api.onrender.com/docs

> "Sorular?"

---

## Demo Hazırlık Checklist (sunum öncesi)

- [ ] `npm run dev` çalışıyor (port 5173)
- [ ] `uvicorn main:app --reload` çalışıyor (port 8000)
- [ ] `backend/.env` içinde `OPENAI_API_KEY` ve `GEMINI_API_KEY` doluk
- [ ] Tarayıcı sekmeleri: `/`, `/ilanlar/1`, `/ajan`, `/sirket-arastir`
- [ ] PowerShell penceresinde `interniqmcp` hazır beklesin (yedek terminal)
- [ ] LangSmith dashboard açık (smith.langchain.com → InternIQ projesi)
- [ ] Test login: `deneme@gmail.com` (kayıtlı CV ile)

## Yedek Sorular (jüri sorabilir)

**S: Neden 3 farklı AI framework? Karmaşıklık değil mi?**
> Her biri farklı bir problem için. LangGraph stateful state machine için,
> CrewAI multi-agent role-based abstraction için, direct OpenAI tek-shot için.
> Hepsini LangGraph ile yapmak mümkün ama CrewAI'ın role+goal+backstory
> abstraction'ı şirket araştırması için doğal bir fit.

**S: MCP yerine REST API yetmez miydi?**
> REST API zaten var (FastAPI). MCP onun ÜSTÜNE bir abstraction.
> Avantaj: herhangi bir LLM (Claude, GPT, Gemini) tool calling ile
> doğrudan kullanabiliyor. REST API kullanmak isteyen LLM'in custom
> integration kodu yazması gerekir.

**S: Subprocess izolasyonu neden gerekli?**
> Windows + asyncio + stdio + httpx. FastMCP child'ında openai SDK'nin
> ilk sync request'i takılıyor. Subprocess izolasyonu temiz bir Python
> process veriyor — CrewAI verbose output'u da MCP JSON-RPC frame'lerine
> sızmıyor.

**S: AutoGen ne oldu (Ödev 5)?**
> Yol haritasında vardı, otonom ilan tarayıcı planlandı. MCP ödevini
> derinleştirmek için zaman ayırdım — 17 tool yazmak ve LLM-as-MCP-host
> ajan kurmak öncelikliydi. AutoGen sonraki iterasyon için açık.

**S: AI maliyeti?**
> Bir tam workflow ~$0.01-0.02 (gpt-4o-mini, max_tokens=1200).
> CrewAI report ~$0.03. Mock interview ~$0.005/turn.

**S: Production'da kaç kullanıcı kaldırır?**
> Şu an in-memory session'lar (`_sessions` dict), production'da Redis
> gerekir. CrewAI çağrısı ~60s sürdüğü için queue (Celery) lazım.
> Şu haliyle ~10 concurrent demo için yeterli.

**S: LangGraph vs CrewAI farkı?**
> LangGraph = düşük seviye state machine, conditional edges + state
> birikimi yazabilirsin.
> CrewAI = yüksek seviye agent abstraction, role + goal + backstory
> verirsin gerisi yapılır.
> LangGraph daha esnek, CrewAI daha hızlı yazılır.
