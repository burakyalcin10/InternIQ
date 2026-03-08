# 🎯 InternIQ — AI-Powered Internship Platform

> Staj başvurusunu baştan sona otomatize eden AI platformu.

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## 📖 Proje Açıklaması

InternIQ, üniversite öğrencilerinin staj arama, başvuru ve mülakat hazırlık süreçlerini AI teknolojileri ile otomatize eden bir platformdur.

### 🔑 Temel Özellikler

| Modül | Açıklama |
|-------|----------|
| 🔍 **Staj Radar** | LinkedIn, Kariyer.net, Indeed ve şirket sitelerinden ilanları toplar, filtreler |
| 📄 **CV Tailorer** | İlana özel CV optimizasyonu yapar, ATS uyumluluk skoru hesaplar |
| 🏢 **Company Intel** | Şirket kültürü, tech stack, Glassdoor yorumları, güncel haberleri derler |
| 🎤 **Mock Interview** | Pozisyona özel mülakat soruları üretir, cevapları değerlendirir |

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Modern bir web tarayıcısı (Chrome, Firefox, Safari, Edge)
- (Opsiyonel) VS Code + Live Server eklentisi

### Yerel Çalıştırma

```bash
# 1. Repo'yu klonlayın
git clone https://github.com/burakyalcin10/InternIQ.git

# 2. Proje dizinine gidin
cd InternIQ

# 3. Tarayıcıda açın (herhangi biri):

# Seçenek A: Doğrudan dosyayı açın
start index.html          # Windows
open index.html           # macOS

# Seçenek B: VS Code Live Server ile
# VS Code'da projeyi açın → index.html → sağ tık → "Open with Live Server"

# Seçenek C: Python HTTP server
python -m http.server 8000
# Tarayıcıda http://localhost:8000 adresine gidin
```

## 🏗️ Proje Yapısı

```
InternIQ/
├── index.html              # Ana sayfa
├── features.html           # Özellikler sayfası (Radar, CV, Chat)
├── about.html              # Hakkımızda, mimari, yol haritası
├── css/
│   └── style.css           # Tüm stiller (dark theme, glassmorphism)
├── js/
│   ├── data.js             # Dinamik içerik verileri
│   └── main.js             # Uygulama mantığı ve etkileşimler
├── docs/
│   └── AI_Agent_Planning.md  # AI Agent Planlama Dokümanı
└── README.md               # Bu dosya
```

## 🛠️ Kullanılan Teknolojiler

### Mevcut (Draft v1)
- **HTML5** — Semantik yapı
- **CSS3** — Custom properties, glassmorphism, grid layout, animasyonlar
- **Vanilla JavaScript** — DOM manipülasyonu, dinamik render, event handling

### Planlanan (Gelecek Sürümler)
- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **AI:** OpenAI SDK, CrewAI, LangGraph, AutoGen, MCP
- **Database:** Supabase (PostgreSQL)
- **Deploy:** Vercel (FE) + Railway (BE)

## 📄 AI Agent Planlama Dokümanı

Detaylı AI agent entegrasyon planı için: [📑 AI_Agent_Planning.md](docs/AI_Agent_Planning.md)

## 🌐 Canlı Demo

🔗 [InternIQ Live Demo](https://burakyalcin10.github.io/InternIQ/)

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

*Built with 🤖 & ❤️ for AI Agents course — 2026*
