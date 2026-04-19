import { useRef, useState } from 'react'
import {
  AlertCircle,
  FileCheck,
  FileText,
  Lightbulb,
  Loader2,
  Sparkles,
  Target,
  Upload,
  X,
} from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { useAuth } from '../context/useAuth'
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
  const { profile } = useAuth()
  const [jobDesc, setJobDesc] = useState('')
  const [cvFile, setCvFile] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file && file.type === 'application/pdf') {
      setCvFile(file)
    } else if (file) {
      alert('Lütfen PDF formatında bir dosya yükleyin.')
    }
  }

  const removeFile = () => {
    setCvFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleAnalyze = async () => {
    if (!jobDesc.trim()) return
    setAnalyzing(true)
    setResult(null)
    setError(null)

    try {
      const data = await analyzeCv(jobDesc, cvFile)
      const suggestions = (data.suggestions || []).map((suggestion) => ({
        icon: iconMap[suggestion.icon] || Lightbulb,
        text: suggestion.text,
        type: suggestion.type,
      }))

      setResult({
        score: data.score,
        suggestions,
        matched_keywords: data.matched_keywords || [],
        missing_keywords: data.missing_keywords || [],
        summary: data.summary || '',
        status: data.status || 'fallback',
        cv_source: data.cv_source || 'manual',
      })
    } catch (err) {
      console.error('CV analysis error:', err)
      setError(err.message || 'CV analizi sırasında bir hata oluştu. Backend çalışıyor mu kontrol edin.')
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
          placeholder={"Staj ilanının açıklamasını buraya yapıştırın...\n\nÖrnek: 'ASELSAN Yazılım Mühendisliği Stajyeri — C/C++ ve gömülü sistem bilgisi aranan, 3-4. sınıf öğrencileri...'"}
          value={jobDesc}
          onChange={(event) => setJobDesc(event.target.value)}
        />

        <div className="cv-upload">
          <div className="cv-upload__label">CV Yükle (PDF)</div>
          {!cvFile ? (
            <div
              className="cv-upload__dropzone"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={20} />
              <span>PDF dosyası seçmek için tıklayın</span>
              <span className="cv-upload__hint">veya sürükleyip bırakın</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="cv-upload__input"
              />
            </div>
          ) : (
            <div className="cv-upload__file">
              <FileText size={18} />
              <span className="cv-upload__filename">{cvFile.name}</span>
              <span className="cv-upload__size">
                ({(cvFile.size / 1024).toFixed(0)} KB)
              </span>
              <button className="cv-upload__remove" onClick={removeFile}>
                <X size={14} />
              </button>
            </div>
          )}
        </div>

        {profile?.has_cv && !cvFile && (
          <div className="cv-upload__profile-note">
            PDF yüklemezseniz kayıtlı CV profiliniz kullanılacaktır.
          </div>
        )}

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
              <Sparkles size={16} /> CV’yi analiz et
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
              {cvFile && <p className="cv-loading__sub">PDF okunuyor ve değerlendiriliyor...</p>}
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
                Tekrar dene
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
                    CV’niz bu ilan ile %{result.score} eşleşiyor
                    {result.status === 'ai' && (
                      <span className="cv-badge cv-badge--ai">Gemini AI</span>
                    )}
                    {result.status === 'fallback' && (
                      <span className="cv-badge cv-badge--fallback">Demo</span>
                    )}
                  </div>
                  <div className="cv-score-sub">
                    {result.cv_source === 'profile'
                      ? 'Kayıtlı CV profiliniz kullanıldı.'
                      : result.cv_source === 'empty'
                        ? 'CV olmadan genel uygunluk analizi yapıldı.'
                        : 'Gönderdiğiniz CV kullanıldı.'}
                  </div>
                </div>
              </div>

              {result.summary && (
                <div className="cv-summary">
                  <p>{result.summary}</p>
                </div>
              )}

              {(result.matched_keywords.length > 0 || result.missing_keywords.length > 0) && (
                <div className="cv-keywords">
                  {result.matched_keywords.length > 0 && (
                    <div className="cv-keywords__group">
                      <div className="cv-keywords__label cv-keywords__label--match">Eşleşen</div>
                      <div className="cv-keywords__tags">
                        {result.matched_keywords.map((keyword, index) => (
                          <span key={index} className="tag tag--match">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.missing_keywords.length > 0 && (
                    <div className="cv-keywords__group">
                      <div className="cv-keywords__label cv-keywords__label--miss">Eksik</div>
                      <div className="cv-keywords__tags">
                        {result.missing_keywords.map((keyword, index) => (
                          <span key={index} className="tag tag--miss">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="cv-suggestions-title">Öneriler</div>
              <div className="cv-suggestions">
                {result.suggestions.map((suggestion, index) => {
                  const Icon = suggestion.icon
                  return (
                    <motion.div
                      key={index}
                      className={`cv-suggestion cv-suggestion--${suggestion.type}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Icon size={16} className="cv-suggestion__icon" />
                      <span>{suggestion.text}</span>
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
              <Upload size={40} style={{ color: 'var(--text-muted)' }} />
              <p>CV’nizi PDF olarak yükleyin ve ilan açıklamasını yapıştırın.</p>
              <p className="cv-empty__sub">
                AI, CV’nizi ilanla karşılaştırarak ATS skoru, eşleşen veya eksik beceriler ve öneriler sunacak.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
