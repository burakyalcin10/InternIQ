import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Building2, Code2, MessageSquare, ThumbsUp,
  ThumbsDown, Star, Loader2, Sparkles, Bot
} from 'lucide-react'
import { motion } from 'framer-motion'
import { startCrewResearch } from '../services/api'
import './CompanyResearch.css'

export default function CompanyResearch() {
  const { name } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    runResearch()
  }, [name])

  const runResearch = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await startCrewResearch(decodeURIComponent(name))
      setData(result)
    } catch (err) {
      setError('Araştırma sırasında bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="crew-loading">
        <div className="crew-loading__animation">
          <div className="crew-loading__orb crew-loading__orb--1">
            <Bot size={24} />
          </div>
          <div className="crew-loading__orb crew-loading__orb--2">
            <Code2 size={24} />
          </div>
          <div className="crew-loading__orb crew-loading__orb--3">
            <MessageSquare size={24} />
          </div>
        </div>
        <h2 className="crew-loading__title">CrewAI Analiz Ediyor...</h2>
        <p className="crew-loading__sub">3 AI ajan {decodeURIComponent(name)} hakkında araştırma yapıyor</p>
        <div className="crew-loading__steps">
          <div className="crew-loading__step crew-loading__step--active">
            <Sparkles size={14} /> Kültür Araştırmacısı çalışıyor...
          </div>
          <div className="crew-loading__step">
            <Code2 size={14} /> Teknoloji Analisti bekliyor...
          </div>
          <div className="crew-loading__step">
            <MessageSquare size={14} /> Rapor Yazarı bekliyor...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="crew-loading">
        <p style={{ color: 'var(--rose)' }}>{error}</p>
        <Link to="/features" className="btn btn-ghost" style={{ marginTop: '12px' }}>
          <ArrowLeft size={16} /> Geri dön
        </Link>
      </div>
    )
  }

  const report = data?.report || {}

  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <Link to="/features" className="detail__back">
            <ArrowLeft size={16} /> Özellikler Sayfasına Dön
          </Link>
        </div>
      </div>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Header */}
            <div className="crew-header glass-card">
              <div className="crew-header__top">
                <div>
                  <div className="crew-header__badge">
                    <Sparkles size={14} />
                    CrewAI Analizi
                    {data?.status === 'fallback' && <span className="crew-header__mode">· Demo Mod</span>}
                  </div>
                  <h1 className="crew-header__title">{decodeURIComponent(name)}</h1>
                  <p className="crew-header__summary">{report.company_summary}</p>
                </div>
                {report.overall_rating && (
                  <div className="crew-header__rating">
                    <Star size={20} />
                    <span>{report.overall_rating}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Content Grid */}
            <div className="crew-grid">
              {/* Culture */}
              <motion.div
                className="crew-section glass-card"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <h2 className="crew-section__title">
                  <Building2 size={18} /> Kültür & Çalışma Ortamı
                </h2>
                <p className="crew-section__text">{report.culture}</p>
              </motion.div>

              {/* Tech Stack */}
              <motion.div
                className="crew-section glass-card"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
              >
                <h2 className="crew-section__title">
                  <Code2 size={18} /> Teknoloji Stack
                </h2>
                {report.tech_stack && (
                  <div className="crew-tags">
                    {report.tech_stack.map((tech, i) => (
                      <span key={i} className="tag">{tech}</span>
                    ))}
                  </div>
                )}
              </motion.div>

              {/* Interview Tips */}
              <motion.div
                className="crew-section glass-card crew-section--wide"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h2 className="crew-section__title">
                  <MessageSquare size={18} /> Mülakat Hazırlık Rehberi
                </h2>
                {report.interview_tips && (
                  <ul className="crew-list">
                    {report.interview_tips.map((tip, i) => (
                      <li key={i}>{tip}</li>
                    ))}
                  </ul>
                )}
              </motion.div>

              {/* Pros */}
              <motion.div
                className="crew-section glass-card"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
              >
                <h2 className="crew-section__title crew-section__title--pro">
                  <ThumbsUp size={18} /> Artılar
                </h2>
                {report.pros && (
                  <ul className="crew-list crew-list--pro">
                    {report.pros.map((pro, i) => (
                      <li key={i}>{pro}</li>
                    ))}
                  </ul>
                )}
              </motion.div>

              {/* Cons */}
              <motion.div
                className="crew-section glass-card"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h2 className="crew-section__title crew-section__title--con">
                  <ThumbsDown size={18} /> Eksiler
                </h2>
                {report.cons && (
                  <ul className="crew-list crew-list--con">
                    {report.cons.map((con, i) => (
                      <li key={i}>{con}</li>
                    ))}
                  </ul>
                )}
              </motion.div>

              {/* Recommendation */}
              {report.recommendation && (
                <motion.div
                  className="crew-section glass-card crew-section--wide crew-section--highlight"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35 }}
                >
                  <h2 className="crew-section__title">
                    <Sparkles size={18} /> Genel Tavsiye
                  </h2>
                  <p className="crew-section__text">{report.recommendation}</p>
                </motion.div>
              )}
            </div>

            {/* Agents Info Footer */}
            <div className="crew-agents glass-card">
              <h3>Bu rapor 3 AI ajan tarafından oluşturuldu</h3>
              <div className="crew-agents__list">
                <div className="crew-agent-badge">
                  <Bot size={16} />
                  <span>Kültür Araştırmacısı</span>
                </div>
                <div className="crew-agent-badge">
                  <Code2 size={16} />
                  <span>Teknoloji Analisti</span>
                </div>
                <div className="crew-agent-badge">
                  <MessageSquare size={16} />
                  <span>Rapor Yazarı</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  )
}
