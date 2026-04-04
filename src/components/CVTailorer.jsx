import { useState } from 'react'
import { Send, Loader2, FileCheck, AlertCircle, Lightbulb, Target, FileText } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { analyzeCv } from '../services/api'
import './CVTailorer.css'

const iconMap = {
  '✅': FileCheck,
  '⚠️': AlertCircle,
  '💡': Lightbulb,
  '📝': FileText,
  '🎯': Target,
}

export default function CVTailorer() {
  const [jobDesc, setJobDesc] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!jobDesc.trim()) return
    setAnalyzing(true)
    setResult(null)
    setError(null)

    try {
      const data = await analyzeCv(jobDesc)
      // Map API response to component format
      const suggestions = data.suggestions.map((s) => ({
        icon: iconMap[s.icon] || Lightbulb,
        text: s.text,
        type: s.type,
      }))
      setResult({ score: data.score, suggestions })
    } catch (err) {
      console.error('CV analysis error:', err)
      setError('CV analizi sırasında bir hata oluştu. Backend çalışıyor mu kontrol edin.')
    } finally {
      setAnalyzing(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--emerald)'
    if (score >= 70) return 'var(--amber)'
    return 'var(--rose)'
  }

  return (
    <div className="cv-grid">
      <div className="cv-panel glass-card">
        <h3 className="cv-panel__title">İlan Açıklaması</h3>
        <textarea
          className="input cv-panel__textarea"
          placeholder={"Staj ilanının açıklamasını buraya yapıştırın...\n\nÖrnek: 'We are looking for a Software Engineering Intern with experience in React, Node.js, and cloud technologies...'"}
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
        <button
          className="btn btn-primary cv-panel__btn"
          onClick={handleAnalyze}
          disabled={analyzing || !jobDesc.trim()}
        >
          {analyzing ? (
            <>
              <Loader2 size={16} className="spin" /> Analiz ediliyor...
            </>
          ) : (
            <>
              <Send size={16} /> CV'yi Analiz Et
            </>
          )}
        </button>
      </div>

      <div className="cv-panel glass-card">
        <h3 className="cv-panel__title">Analiz Sonuçları</h3>
        <AnimatePresence mode="wait">
          {analyzing && (
            <motion.div
              key="loading"
              className="cv-loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Loader2 size={32} className="spin" style={{ color: 'var(--accent-light)' }} />
              <p>AI analiz ediyor...</p>
            </motion.div>
          )}

          {!analyzing && error && (
            <motion.div
              key="error"
              className="cv-empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <AlertCircle size={40} style={{ color: 'var(--rose)' }} />
              <p style={{ color: 'var(--rose)' }}>{error}</p>
              <button className="btn btn-ghost" onClick={handleAnalyze} style={{ marginTop: '8px' }}>
                Tekrar Dene
              </button>
            </motion.div>
          )}

          {!analyzing && !error && result && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <div className="cv-score-box">
                <div
                  className="cv-score-ring"
                  style={{
                    borderColor: getScoreColor(result.score),
                    color: getScoreColor(result.score),
                  }}
                >
                  {result.score}
                </div>
                <div>
                  <div className="cv-score-label">ATS Uyumluluk Skoru</div>
                  <div className="cv-score-sub">
                    CV'niz bu ilan ile {result.score}% eşleşiyor
                  </div>
                </div>
              </div>

              <div className="cv-suggestions-title">Öneriler</div>
              <div className="cv-suggestions">
                {result.suggestions.map((s, i) => {
                  const Icon = s.icon
                  return (
                    <motion.div
                      key={i}
                      className={`cv-suggestion cv-suggestion--${s.type}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.1 }}
                    >
                      <Icon size={16} className="cv-suggestion__icon" />
                      <span>{s.text}</span>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {!analyzing && !error && !result && (
            <motion.div
              key="empty"
              className="cv-empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <FileText size={40} style={{ color: 'var(--text-muted)' }} />
              <p>İlan açıklamasını yapıştırıp butona tıklayın.</p>
              <p className="cv-empty__sub">
                AI, CV'nizi ilanla karşılaştırarak ATS skoru ve öneriler sunacak.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
