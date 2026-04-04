import { motion } from 'framer-motion'
import { Cpu, Search, FileText, MessageSquare } from 'lucide-react'
import Timeline from '../components/Timeline'
import './AboutPage.css'

const markers = [
  { color: 'var(--accent)', label: 'Problem', desc: 'İlanlar dağınık, CV düzenleme zahmetli, hazırlık stresli' },
  { color: 'var(--emerald)', label: 'Çözüm', desc: 'Her acı noktası için uzman bir AI agent' },
  { color: 'var(--amber)', label: 'Yaklaşım', desc: 'Multi-agent mimari, her aşamada otomatik destek' },
  { color: 'var(--rose)', label: 'Vizyon', desc: 'Her öğrencinin doğru staja ulaşabilmesi' },
]

const agents = [
  { id: 'Scout', title: 'Keşif Agentı', desc: "Web'i tarayarak yeni ilanları bulan, filtreleyen ve sınıflandıran otonom araştırmacı.", tech: 'AutoGen · Web Scraping', icon: Search, color: 'var(--accent)' },
  { id: 'Writer', title: 'CV Uzmanı', desc: "İlan gereksinimlerini analiz edip CV'yi optimize eden, ATS uyumluluğunu artıran agent.", tech: 'OpenAI SDK · NLP', icon: FileText, color: 'var(--sky)' },
  { id: 'Intel', title: 'Araştırmacı', desc: 'Şirket kültürü, tech stack, mülakat tarzı, güncel haberleri derleyen agent.', tech: 'CrewAI · RAG', icon: Cpu, color: 'var(--emerald)' },
  { id: 'Coach', title: 'Mülakat Koçu', desc: 'Pozisyona özel sorular üreten, cevapları değerlendiren, geri bildirim veren agent.', tech: 'LangGraph · GPT-4', icon: MessageSquare, color: 'var(--amber)' },
]

const techStack = ['React', 'Vite', 'FastAPI', 'Python', 'OpenAI SDK', 'CrewAI', 'LangGraph', 'AutoGen', 'MCP', 'Supabase']

export default function AboutPage() {
  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <span className="section-tag">Hakkında</span>
          <h1 className="section-title">
            Staj arama sürecini
            <br />
            <span className="text-gradient">AI ile yeniden tanımlıyoruz.</span>
          </h1>
        </div>
      </div>

      {/* About Split */}
      <section className="section">
        <div className="wrap">
          <div className="about-grid">
            <div className="about-markers">
              {markers.map((m, i) => (
                <motion.div
                  key={m.label}
                  className="about-marker glass-card"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                >
                  <div className="about-marker__dot" style={{ background: m.color }} />
                  <div>
                    <strong>{m.label}</strong>
                    <span>{m.desc}</span>
                  </div>
                </motion.div>
              ))}
            </div>

            <motion.div
              className="about-copy"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <h3>Neden InternIQ?</h3>
              <p>
                Staj aramanın ne kadar zor olduğunu biliyoruz. İlanlar onlarca platformda dağınık,
                her başvuru için CV düzenlemek saatler alıyor, şirketler hakkında bilgi bulmak güç
                ve mülakat hazırlığı stresli.
              </p>
              <p>
                InternIQ, bu sorunları multi-agent AI mimarisi ile çözüyor. Her modül, sürecin
                farklı bir aşamasında uzmanlaşmış bir AI asistanla destekleniyor.
              </p>
              <h3 style={{ marginTop: '28px' }}>Tech Stack</h3>
              <div className="about-tech-row">
                {techStack.map((t) => (
                  <span key={t} className="tag">{t}</span>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Architecture */}
      <section className="section" id="architecture">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">Mimari</span>
            <h2 className="section-title">Sistem mimarisi</h2>
            <p className="section-desc">AI agent katmanı ve bileşen yapısı.</p>
          </div>
          <motion.div
            className="arch-box glass-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <pre>{`┌─────────────────────────────────────────────────────────┐
│                   FRONTEND  (React + Vite)              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Radar   │ │ Tailorer │ │  Intel   │ │Interview │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
└───────┼─────────────┼────────────┼────────────┼─────────┘
        │             │            │            │
        ▼             ▼            ▼            ▼
┌─────────────────────────────────────────────────────────┐
│              API GATEWAY  (FastAPI · Python)             │
│         REST  ·  WebSocket  ·  JWT Auth                 │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌───────────────┐
│   AI LAYER   │ │   DATABASE   │ │   EXTERNAL    │
│              │ │              │ │   SERVICES    │
│ · OpenAI SDK │ │  Supabase    │ │               │
│ · CrewAI     │ │ (PostgreSQL) │ │ · LinkedIn    │
│ · LangGraph  │ │              │ │ · Kariyer.net │
│ · AutoGen    │ │ · users      │ │ · Indeed      │
│ · MCP        │ │ · listings   │ │ · Glassdoor   │
│              │ │ · cvs        │ │ · Gmail       │
│              │ │ · history    │ │ · OpenAI API  │
└──────────────┘ └──────────────┘ └───────────────┘`}</pre>
          </motion.div>
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Roadmap */}
      <section className="section" id="roadmap">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">Yol Haritası</span>
            <h2 className="section-title">Hafta hafta gelişim planı</h2>
            <p className="section-desc">Her hafta yeni bir AI framework entegre ediliyor.</p>
          </div>
          <Timeline />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Agents */}
      <section className="section" id="agents">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">AI Agentlar</span>
            <h2 className="section-title">Uzman agent ekibi</h2>
            <p className="section-desc">Her görev için uzmanlaşmış bir AI agent.</p>
          </div>
          <div className="agents-grid">
            {agents.map((agent, i) => {
              const Icon = agent.icon
              return (
                <motion.div
                  key={agent.id}
                  className="agent-card glass-card"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                >
                  <div className="agent-card__icon" style={{ background: `${agent.color}18`, borderColor: `${agent.color}33`, color: agent.color }}>
                    <Icon size={20} />
                  </div>
                  <span className="agent-card__id">{agent.id}</span>
                  <h3 className="agent-card__title">{agent.title}</h3>
                  <p className="agent-card__desc">{agent.desc}</p>
                  <span className="tag tag-accent" style={{ marginTop: 'auto' }}>{agent.tech}</span>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>
    </>
  )
}
