# InternIQ — AI-Powered Internship Platform

AI destekli staj arama platformu. Doğru stajı bul, hazırlığını AI'a bırak.

## 🚀 Proje Hakkında

InternIQ, üniversite öğrencilerinin staj arama sürecini uçtan uca otomatize eden bir AI platformudur. Dört temel modül ile çalışır:

1. **🔍 Staj Radar** — Birden fazla platformdan ilanları toplar ve filtreler
2. **📄 CV Tailorer** — İlan bazlı CV optimizasyonu ve ATS skor analizi
3. **🏢 Company Intel** — Şirket kültürü, tech stack ve mülakat bilgileri
4. **🎤 Mock Interview** — Pozisyona özel mülakat simülasyonu

## 🛠️ Tech Stack

### Frontend
- **React 18** + **Vite** — SPA, client-side routing
- **Framer Motion** — Animasyonlar
- **Lucide React** — İkon seti
- **CSS Design System** — Custom dark theme

### Backend
- **FastAPI** (Python) — REST API
- **Supabase** (PostgreSQL) — Veritabanı
- **Uvicorn** — ASGI server

### AI (Planlanan)
- **OpenAI SDK** — CV analizi (Hafta 2)
- **CrewAI** — Multi-agent araştırma (Hafta 3)
- **LangGraph** — Stateful interview (Hafta 4)
- **AutoGen** — Otonom ilan tarama (Hafta 5)
- **MCP** — Platform entegrasyonları (Hafta 6)

## 📦 Kurulum

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python -m uvicorn main:app --reload
```

## 📁 Proje Yapısı

```
InternIQ/
├── src/                    # React Frontend
│   ├── components/         # UI Componentleri
│   ├── pages/              # Sayfa componentleri
│   ├── services/           # API service layer
│   ├── hooks/              # Custom React hooks
│   └── index.css           # Design system
├── backend/                # FastAPI Backend
│   ├── routers/            # API endpoint'leri
│   ├── services/           # Business logic
│   ├── data/               # JSON veri dosyaları
│   └── main.py             # FastAPI app
├── docs/                   # Dokümantasyon
└── package.json
```

## 📝 Lisans

© 2026 InternIQ. Tüm hakları saklıdır.
