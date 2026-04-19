import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useLocation, useSearchParams } from 'react-router-dom'
import {
  AlertCircle,
  Briefcase,
  Building2,
  CheckCircle2,
  FileText,
  Loader2,
  MessageSquare,
  Sparkles,
  Target,
  Zap,
} from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { useAuth } from '../context/useAuth'
import { getListings, startWorkflow } from '../services/api'
import './ApplicationWorkflow.css'

const FALLBACK_STEPS = [
  { id: 'analyze_listing', title: 'İlan Analizi' },
  { id: 'evaluate_cv', title: 'CV Değerlendirme' },
  { id: 'check_cv_score', title: 'CV Skor Kontrolü' },
  { id: 'suggest_improvements', title: 'CV İyileştirme Önerileri' },
  { id: 'research_company', title: 'Şirket Araştırması' },
  { id: 'generate_interview_prep', title: 'Mülakat Hazırlığı' },
  { id: 'create_action_plan', title: 'Aksiyon Planı' },
]

export default function ApplicationWorkflow({ listingId, listingTitle, companyName }) {
  const { isAuthenticated, profile, authLoading } = useAuth()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const queryListingId = searchParams.get('listing')
  const shouldAutoRun = searchParams.get('autorun') === '1'
  const autoRunTriggeredRef = useRef(false)
  const [cvText, setCvText] = useState('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [listings, setListings] = useState([])
  const [selectedListingId, setSelectedListingId] = useState(listingId || queryListingId || '')
  const [loadingListings, setLoadingListings] = useState(!listingId)

  useEffect(() => {
    if (!listingId && queryListingId) {
      setSelectedListingId(queryListingId)
    }
  }, [listingId, queryListingId])

  useEffect(() => {
    if (listingId) {
      setSelectedListingId(listingId)
      setLoadingListings(false)
      return
    }

    let active = true

    const loadListings = async () => {
      try {
        setLoadingListings(true)
        const data = await getListings({ limit: 12 })
        if (!active) return

        const nextListings = data.listings || []
        setListings(nextListings)
        if (nextListings.length > 0) {
          setSelectedListingId((currentId) => currentId || nextListings[0].id)
        }
      } catch (err) {
        console.error('Workflow listings error:', err)
        if (active) {
          setError('İlanlar yüklenemedi. Workflow için bir ilan seçimi gerekli.')
        }
      } finally {
        if (active) {
          setLoadingListings(false)
        }
      }
    }

    loadListings()

    return () => {
      active = false
    }
  }, [listingId, queryListingId])

  const workflowSteps = result?.workflow_steps || FALLBACK_STEPS
  const interviewSections = result?.interview_sections || {}
  const cvSpecificQuestions = interviewSections.cv_specific || []
  const companySpecificQuestions = interviewSections.company_specific || []
  const selectedListing = listingId
    ? { id: listingId, position: listingTitle, company: companyName }
    : listings.find((listing) => listing.id === Number(selectedListingId))

  const usingSavedCv = !cvText.trim() && isAuthenticated && profile?.has_cv

  const handleRun = async () => {
    if (!selectedListingId) {
      setError('Lütfen önce bir ilan seçin.')
      return
    }

    setRunning(true)
    setResult(null)
    setError(null)

    try {
      const data = await startWorkflow(Number(selectedListingId), cvText)
      setResult(data)
    } catch (err) {
      console.error('Workflow error:', err)
      setError(err.message || 'Workflow çalıştırılamadı. Backend bağlantısını kontrol edin.')
    } finally {
      setRunning(false)
    }
  }

  useEffect(() => {
    if (!shouldAutoRun || autoRunTriggeredRef.current) {
      return
    }

    if (authLoading || loadingListings || running || !selectedListingId) {
      return
    }

    if (!isAuthenticated || !profile?.has_cv) {
      autoRunTriggeredRef.current = true
      setError('Otomatik başlatma için önce giriş yapıp güncel CV profilinizi yüklemelisiniz.')
      return
    }

    autoRunTriggeredRef.current = true
    handleRun()
  }, [
    shouldAutoRun,
    authLoading,
    loadingListings,
    running,
    selectedListingId,
    isAuthenticated,
    profile?.has_cv,
  ])

  useLayoutEffect(() => {
    if (!shouldAutoRun) {
      return
    }

    const scrollToWorkflow = () => {
      const section = document.getElementById('workflow-section')
      section?.scrollIntoView({ behavior: 'auto', block: 'start' })
    }

    const frameId = window.requestAnimationFrame(scrollToWorkflow)
    return () => window.cancelAnimationFrame(frameId)
  }, [shouldAutoRun, location.key])

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
                LangGraph ile durum tutan, adım adım ilerleyen başvuru hazırlık akışı
              </p>
            </div>
          </div>

          <div className="workflow__selector-row">
            <label className="workflow__field">
              <span>Seçilen İlan</span>
              {listingId ? (
                <div className="workflow__listing-pill">
                  <Briefcase size={14} />
                  <span>{listingTitle} {companyName ? `@ ${companyName}` : ''}</span>
                </div>
              ) : (
                <select
                  className="input workflow__select"
                  value={selectedListingId}
                  onChange={(event) => setSelectedListingId(event.target.value)}
                  disabled={loadingListings}
                >
                  <option value="">
                    {loadingListings ? 'İlanlar yükleniyor...' : 'Bir ilan seçin'}
                  </option>
                  {listings.map((listing) => (
                    <option key={listing.id} value={listing.id}>
                      {listing.position} - {listing.company}
                    </option>
                  ))}
                </select>
              )}
            </label>
          </div>

          {selectedListing && (
            <div className="workflow__listing-summary">
              <div className="workflow__listing-heading">
                <Briefcase size={14} />
                <strong>{selectedListing.position}</strong>
              </div>
              <p>
                {selectedListing.company || 'Şirket seçimi bekleniyor'} için CV analizi, şirket araştırması,
                mülakat hazırlığı ve aksiyon planı tek bir graph üzerinden üretilir.
              </p>
            </div>
          )}

          <div className="workflow__cv-input">
            <label htmlFor="workflow-cv-text">CV Metniniz</label>
            <textarea
              id="workflow-cv-text"
              className="input workflow__textarea"
              placeholder="CV’nizin metnini buraya yapıştırın. Boş bırakırsanız sistem kayıtlı CV’nizi veya genel uygunluk analizini kullanır."
              value={cvText}
              onChange={(event) => setCvText(event.target.value)}
              rows={4}
            />
          </div>

          {usingSavedCv && (
            <div className="workflow__saved-cv-note">
              Kayıtlı CV profiliniz kullanılacak. İsterseniz bu alanı doldurarak anlık farklı bir CV ile test yapabilirsiniz.
            </div>
          )}

          <button
            className="btn btn-primary workflow__run-btn"
            onClick={handleRun}
            disabled={running || loadingListings || !selectedListingId}
          >
            <Sparkles size={16} /> Hazırlık Planı Oluştur
          </button>

          <div className="workflow__steps-panel">
            <div className="workflow__step-label">LangGraph düğümleri</div>
            <div className="workflow__steps-preview">
              {workflowSteps.map((step, index) => (
                <span key={step.id} className="workflow__step-chip">
                  {index + 1}. {step.title}
                </span>
              ))}
            </div>
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
            <h3>LangGraph workflow çalışıyor...</h3>
            <p>Seçilen ilan için graph düğümleri sırayla işleniyor.</p>
            <div className="workflow__loading-steps">
              {workflowSteps.map((step, index) => (
                <div
                  key={step.id}
                  className={`workflow__loading-step ${index === 0 ? 'workflow__loading-step--active' : ''}`}
                >
                  <Sparkles size={13} /> {step.title}
                </div>
              ))}
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
            <button className="btn btn-ghost" onClick={() => setError(null)}>
              Tekrar dene
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
            <div className="workflow__result-header glass-card">
              <div className="workflow__result-title-row">
                <div>
                  <div className="workflow__result-badge">
                    <Zap size={13} /> LangGraph Analiz
                    <span className="workflow__result-mode">
                      {result.llm_provider === 'gemini'
                        ? '· Gemini'
                        : result.status === 'ai'
                          ? '· AI'
                          : '· Demo'}
                    </span>
                  </div>
                  <h2>{result.action_plan?.company || result.listing?.company || companyName}</h2>
                  <p className="workflow__result-pos">
                    {result.action_plan?.position || result.listing?.position || listingTitle}
                  </p>
                </div>
                <div
                  className="workflow__score-ring"
                  style={{ borderColor: getScoreColor(result.cv_score), color: getScoreColor(result.cv_score) }}
                >
                  <span className="workflow__score-val">{result.cv_score}</span>
                  <span className="workflow__score-label">CV Skoru</span>
                </div>
              </div>

              <div className="workflow__result-meta">
                <span className={`tag ${result.cv_source === 'profile' ? 'tag-emerald' : 'tag-accent'}`}>
                  {result.cv_source === 'profile'
                    ? 'Kayıtlı CV kullanıldı'
                    : result.cv_source === 'manual'
                      ? 'Elle girilen CV kullanıldı'
                      : 'Genel değerlendirme'}
                </span>
              </div>
            </div>

            <div className="workflow__graph-summary glass-card">
              <div className="workflow__graph-summary-head">
                <Sparkles size={16} />
                <strong>Çalıştırılan LangGraph adımları</strong>
              </div>
              <div className="workflow__graph-summary-steps">
                {(result.workflow_steps || workflowSteps).map((step, index) => (
                  <div key={step.id} className="workflow__graph-step">
                    <span className="workflow__graph-step-num">{index + 1}</span>
                    <span>{step.title}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="workflow__result-grid">
              <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
                <h3><FileText size={16} /> CV Analizi</h3>
                <p>{result.cv_analysis?.summary || 'CV analizi tamamlandı.'}</p>
                {result.cv_analysis?.matched_skills?.length > 0 && (
                  <div className="workflow__tags">
                    <span className="workflow__tag-label">Eşleşen:</span>
                    {result.cv_analysis.matched_skills.map((skill, index) => (
                      <span key={index} className="tag tag--match">{skill}</span>
                    ))}
                  </div>
                )}
                {result.cv_analysis?.transferable_skills?.length > 0 && (
                  <div className="workflow__tags">
                    <span className="workflow__tag-label">Aktarılabilir:</span>
                    {result.cv_analysis.transferable_skills.map((skill, index) => (
                      <span key={index} className="tag">{skill}</span>
                    ))}
                  </div>
                )}
                {result.cv_analysis?.missing_skills?.length > 0 && (
                  <div className="workflow__tags">
                    <span className="workflow__tag-label">Eksik:</span>
                    {result.cv_analysis.missing_skills.map((skill, index) => (
                      <span key={index} className="tag tag--miss">{skill}</span>
                    ))}
                  </div>
                )}
              </motion.div>

              {result.cv_suggestions?.length > 0 && (
                <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                  <h3><Target size={16} /> CV İyileştirme Önerileri</h3>
                  <ul className="workflow__list">
                    {result.cv_suggestions.map((suggestion, index) => (
                      <li key={index}><CheckCircle2 size={14} /> {suggestion}</li>
                    ))}
                  </ul>
                </motion.div>
              )}

              <motion.div className="workflow__result-card glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <h3><Building2 size={16} /> Şirket Bilgisi</h3>
                <p><strong>Sektör:</strong> {result.company_info?.industry}</p>
                <p><strong>Kültür:</strong> {result.company_info?.culture}</p>
                <p><strong>Mülakat tarzı:</strong> {result.company_info?.interview_style}</p>
                {result.company_info?.tech_stack?.length > 0 && (
                  <div className="workflow__tags" style={{ marginTop: 8 }}>
                    {result.company_info.tech_stack.map((tech, index) => (
                      <span key={index} className="tag">{tech}</span>
                    ))}
                  </div>
                )}
              </motion.div>

              {result.interview_questions?.length > 0 && (
                <motion.div className="workflow__result-card workflow__result-card--wide glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                  <h3><MessageSquare size={16} /> Hazırlık Soruları</h3>
                  <div className="workflow__interview-grid">
                    <div className="workflow__interview-column">
                      <strong className="workflow__interview-title">CV’ye Özel Sorular</strong>
                      <ol className="workflow__list workflow__list--numbered">
                        {(cvSpecificQuestions.length > 0 ? cvSpecificQuestions : result.interview_questions.slice(0, 3)).map((question, index) => (
                          <li key={`cv-${index}`}>{question}</li>
                        ))}
                      </ol>
                    </div>
                    <div className="workflow__interview-column">
                      <strong className="workflow__interview-title">Şirketin Sorabileceği Genel Sorular</strong>
                      <ol className="workflow__list workflow__list--numbered">
                        {(companySpecificQuestions.length > 0 ? companySpecificQuestions : result.interview_questions.slice(3)).map((question, index) => (
                          <li key={`company-${index}`}>{question}</li>
                        ))}
                      </ol>
                    </div>
                  </div>
                </motion.div>
              )}

              {result.action_plan?.steps && (
                <motion.div className="workflow__result-card workflow__result-card--wide workflow__result-card--highlight glass-card" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                  <h3><Sparkles size={16} /> Kişiselleştirilmiş Aksiyon Planı</h3>
                  {result.action_plan.summary && (
                    <p className="workflow__plan-summary">{result.action_plan.summary}</p>
                  )}
                  <div className="workflow__action-steps">
                    {result.action_plan.steps.map((step, index) => (
                      <div key={index} className="workflow__action-step">
                        <div className="workflow__action-num">{step.step || index + 1}</div>
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
              ← Yeni analiz
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
