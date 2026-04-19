import { useState, useRef } from 'react'
import {
  Sparkles, Loader2, FileText, Upload, X, CheckCircle2,
  Building2, MessageSquare, Target, ArrowRight, Zap, AlertCircle
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { startWorkflow } from '../services/api'
import './ApplicationWorkflow.css'

export default function ApplicationWorkflow({ listingId, listingTitle, companyName }) {
  const [cvText, setCvText] = useState('')
  const [cvFile, setCvFile] = useState(null)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) setCvFile(file)
  }

  const handleRun = async () => {
    setRunning(true)
    setResult(null)
    setError(null)

    try {
      // If a file is uploaded, read it as text (simplified; backend handles PDF)
      let finalCvText = cvText
      if (cvFile && !cvText.trim()) {
        finalCvText = `(Dosya yüklendi: ${cvFile.name})`
      }

      const data = await startWorkflow(listingId || 1, finalCvText)
      setResult(data)
    } catch (err) {
      console.error('Workflow error:', err)
      setError('Workflow çalıştırılamadı. Backend bağlantısını kontrol edin.')
    } finally {
      setRunning(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--emerald)'
    if (score >= 60) return 'var(--amber)'
    return 'var(--rose)'
  }

  return (
    <div className="workflow">
      {!result && !running && (
        <motion.div
          className="workflow__input glass-card"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="workflow__input-header">
            <Zap size={18} style={{ color: 'var(--accent-light)' }} />
            <div>
              <h3>AI Başvuru Hazırlık Asistanı</h3>
              <p className="workflow__input-sub">
                LangGraph ile 6 adımlı akıllı hazırlık planı
                {listingTitle && <> — <strong>{listingTitle}</strong></>}
                {companyName && <> @ {companyName}</>}
              </p>
            </div>
          </div>

          <div className="workflow__cv-input">
            <label>CV Metniniz (opsiyonel)</label>
            <textarea
              className="input workflow__textarea"
              placeholder="CV'nizin metnini buraya yapıştırın. Boş bırakırsanız genel analiz yapılır..."
              value={cvText}
              onChange={(e) => setCvText(e.target.value)}
              rows={4}
            />
          </div>

          <button
            className="btn btn-primary workflow__run-btn"
            onClick={handleRun}
            disabled={running}
          >
            <Sparkles size={16} /> Hazırlık Planı Oluştur
          </button>

          <div className="workflow__steps-preview">
            <span className="workflow__step-label">Adımlar:</span>
            {['İlan Analizi', 'CV Değerlendirme', 'CV Önerileri', 'Şirket Araştırma', 'Mülakat Hazırlık', 'Aksiyon Planı'].map((s, i) => (
              <span key={i} className="workflow__step-chip">{i + 1}. {s}</span>
            ))}
          </div>
        </motion.div>
      )}

      <AnimatePresence mode="wait">
        {running && (
          <motion.div
            key="loading"
            className="workflow__loading glass-card"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="workflow__loading-animation">
              <Loader2 size={32} className="spin" style={{ color: 'var(--accent-light)' }} />
            </div>
            <h3>LangGraph Workflow Çalışıyor...</h3>
            <p>6 adımlı hazırlık planı oluşturuluyor</p>
            <div className="workflow__loading-steps">
              <div className="workflow__loading-step workflow__loading-step--active">
                <Sparkles size={13} /> İlan analiz ediliyor...
              </div>
              <div className="workflow__loading-step">
                <FileText size={13} /> CV değerlendiriliyor...
              </div>
              <div className="workflow__loading-step">
                <Building2 size={13} /> Şirket araştırılıyor...
              </div>
              <div className="workflow__loading-step">
                <MessageSquare size={13} /> Mülakat soruları hazırlanıyor...
              </div>
            </div>
          </motion.div>
        )}

        {error && !running && (
          <motion.div
            key="error"
            className="workflow__error glass-card"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <AlertCircle size={32} style={{ color: 'var(--rose)' }} />
            <p>{error}</p>
            <button className="btn btn-ghost" onClick={() => { setError(null) }}>
              Tekrar Dene
            </button>
          </motion.div>
        )}

        {result && !running && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Header */}
            <div className="workflow__result-header glass-card">
              <div className="workflow__result-title-row">
                <div>
                  <div className="workflow__result-badge">
                    <Zap size={13} /> LangGraph Analiz
                    <span className="workflow__result-mode">
                      {result.status === 'ai' ? '· AI' : '· Demo'}
                    </span>
                  </div>
                  <h2>{result.action_plan?.company || companyName}</h2>
                  <p className="workflow__result-pos">{result.action_plan?.position || listingTitle}</p>
                </div>
                <div
                  className="workflow__score-ring"
                  style={{ borderColor: getScoreColor(result.cv_score), color: getScoreColor(result.cv_score) }}
                >
                  <span className="workflow__score-val">{result.cv_score}</span>
                  <span className="workflow__score-label">CV Skoru</span>
                </div>
              </div>
            </div>

            <div className="workflow__result-grid">
              {/* CV Analysis */}
              <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
                <h3><FileText size={16} /> CV Analizi</h3>
                <p>{result.cv_analysis?.summary || 'CV analizi tamamlandı.'}</p>
                {result.cv_analysis?.matched_skills?.length > 0 && (
                  <div className="workflow__tags">
                    <span className="workflow__tag-label">Eşleşen:</span>
                    {result.cv_analysis.matched_skills.map((s, i) => (
                      <span key={i} className="tag tag--match">{s}</span>
                    ))}
                  </div>
                )}
                {result.cv_analysis?.missing_skills?.length > 0 && (
                  <div className="workflow__tags">
                    <span className="workflow__tag-label">Eksik:</span>
                    {result.cv_analysis.missing_skills.map((s, i) => (
                      <span key={i} className="tag tag--miss">{s}</span>
                    ))}
                  </div>
                )}
              </motion.div>

              {/* CV Suggestions */}
              {result.cv_suggestions?.length > 0 && (
                <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                  <h3><Target size={16} /> CV İyileştirme Önerileri</h3>
                  <ul className="workflow__list">
                    {result.cv_suggestions.map((s, i) => (
                      <li key={i}><CheckCircle2 size={14} /> {s}</li>
                    ))}
                  </ul>
                </motion.div>
              )}

              {/* Company Info */}
              <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <h3><Building2 size={16} /> Şirket Bilgisi</h3>
                <p><strong>Sektör:</strong> {result.company_info?.industry}</p>
                <p><strong>Kültür:</strong> {result.company_info?.culture}</p>
                <p><strong>Mülakat Tarzı:</strong> {result.company_info?.interview_style}</p>
                {result.company_info?.tech_stack?.length > 0 && (
                  <div className="workflow__tags" style={{ marginTop: 8 }}>
                    {result.company_info.tech_stack.map((t, i) => (
                      <span key={i} className="tag">{t}</span>
                    ))}
                  </div>
                )}
              </motion.div>

              {/* Interview Questions */}
              {result.interview_questions?.length > 0 && (
                <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                  <h3><MessageSquare size={16} /> Hazırlık Soruları</h3>
                  <ol className="workflow__list workflow__list--numbered">
                    {result.interview_questions.map((q, i) => (
                      <li key={i}>{q}</li>
                    ))}
                  </ol>
                </motion.div>
              )}

              {/* Action Plan */}
              {result.action_plan?.steps && (
                <motion.div className="workflow__result-card workflow__result-card--wide workflow__result-card--highlight glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                  <h3><Sparkles size={16} /> Kişiselleştirilmiş Aksiyon Planı</h3>
                  {result.action_plan.summary && (
                    <p className="workflow__plan-summary">{result.action_plan.summary}</p>
                  )}
                  <div className="workflow__action-steps">
                    {result.action_plan.steps.map((step, i) => (
                      <div key={i} className="workflow__action-step">
                        <div className="workflow__action-num">{step.step || i + 1}</div>
                        <div>
                          <strong>{step.title}</strong>
                          <p>{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>

            <button className="btn btn-ghost workflow__reset-btn" onClick={() => { setResult(null); setError(null) }}>
              ← Yeni Analiz
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
