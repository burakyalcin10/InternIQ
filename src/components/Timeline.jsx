import { motion } from 'framer-motion'
import './Timeline.css'

const roadmap = [
  {
    week: 'Hafta 2', title: 'OpenAI SDK — CV Tailoring Assistant',
    description: 'OpenAI API ile ilanları analiz eden ve CV\'yi optimize eden akıllı asistan.',
    tech: 'OpenAI SDK, GPT-4', status: 'completed',
  },
  {
    week: 'Hafta 3', title: 'CrewAI — Multi-Agent Araştırma Ekibi',
    description: 'Araştırmacı, CV uzmanı ve mülakat koçu agentlardan oluşan bir ekip.',
    tech: 'CrewAI, LLM Agents', status: 'completed',
  },
  {
    week: 'Hafta 4', title: 'LangGraph — Başvuru Workflow & AI Mülakat',
    description: 'Multi-step başvuru hazırlık workflow\'u ve AI-destekli stateful mülakat simülasyonu.',
    tech: 'LangGraph, StateGraph, LangSmith', status: 'active',
  },
  {
    week: 'Hafta 5', title: 'AutoGen — Otonom İlan Tarama',
    description: 'Otomatik ilan tarayıcı ve bildirim sistemi.',
    tech: 'AutoGen, Web Scraping', status: 'upcoming',
  },
  {
    week: 'Hafta 6', title: 'MCP — Platform Entegrasyonları',
    description: 'LinkedIn, Kariyer.net ve Gmail ile entegrasyon.',
    tech: 'MCP Protocol', status: 'upcoming',
  },
]

export default function Timeline() {
  return (
    <div className="timeline">
      {roadmap.map((item, i) => (
        <motion.div
          key={item.week}
          className={`tl-item tl-item--${item.status}`}
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: i * 0.1 }}
        >
          <div className="tl-item__dot" />
          <div className="tl-item__content">
            <div className="tl-item__header">
              <span className="tl-item__week">{item.week}</span>
              {item.status === 'completed' && <span className="tag tag-emerald">Tamamlandı</span>}
              {item.status === 'active' && <span className="tag tag-accent">Aktif</span>}
              {item.status === 'upcoming' && <span className="tag">Yakında</span>}
            </div>
            <h3 className="tl-item__title">{item.title}</h3>
            <p className="tl-item__desc">{item.description}</p>
            <span className="tl-item__tech">{item.tech}</span>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
