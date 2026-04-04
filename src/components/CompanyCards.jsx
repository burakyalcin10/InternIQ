import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Star, Users, Code2, Loader2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { getCompanies } from '../services/api'
import './CompanyCards.css'

export default function CompanyCards() {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getCompanies()
      setCompanies(data.companies || [])
    } catch (err) {
      console.error('Companies fetch error:', err)
      setError('Şirket bilgileri yüklenirken bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '48px' }}>
        <Loader2 size={24} className="spin" style={{ color: 'var(--accent-light)' }} />
        <p style={{ marginTop: '12px', color: 'var(--text-tertiary)' }}>Şirketler yükleniyor...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '48px' }}>
        <p style={{ color: 'var(--rose)' }}>{error}</p>
        <button className="btn btn-ghost" onClick={fetchCompanies} style={{ marginTop: '8px' }}>
          Tekrar Dene
        </button>
      </div>
    )
  }

  return (
    <div className="companies">
      {companies.map((c, i) => (
        <motion.div
          key={c.id || c.name}
          className="company-card glass-card"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: i * 0.1 }}
        >
          <div className="company-card__header">
            <div className="company-card__avatar">{c.logo}</div>
            <div>
              <div className="company-card__name">{c.name}</div>
              <div className="company-card__industry">{c.industry} · {c.employees}</div>
            </div>
          </div>

          <div className="company-card__stats">
            <div className="company-card__stat">
              <Star size={14} className="company-card__stat-icon" />
              <span className="company-card__stat-val">{c.rating}</span>
              <span className="company-card__stat-label">Rating</span>
            </div>
            <div className="company-card__stat">
              <Users size={14} className="company-card__stat-icon" />
              <span className="company-card__stat-val">{c.employees}</span>
              <span className="company-card__stat-label">Çalışan</span>
            </div>
            <div className="company-card__stat">
              <Code2 size={14} className="company-card__stat-icon" />
              <span className="company-card__stat-val">{c.tech_stack.length}+</span>
              <span className="company-card__stat-label">Stack</span>
            </div>
          </div>

          <div className="company-card__details">
            <div className="company-card__detail">
              <strong>Kültür:</strong> {c.culture}
            </div>
            <div className="company-card__detail">
              <strong>Mülakat:</strong> {c.interview_style}
            </div>
            <div className="company-card__news">{c.recent_news}</div>
          </div>

          <div className="company-card__tech">
            {c.tech_stack.map((t) => (
              <span key={t} className="tag">{t}</span>
            ))}
          </div>

          <Link
            to={`/company-research/${encodeURIComponent(c.name)}`}
            className="btn btn-primary company-card__ai-btn"
          >
            <Sparkles size={14} />
            AI Analizi Başlat
          </Link>
        </motion.div>
      ))}
    </div>
  )
}
