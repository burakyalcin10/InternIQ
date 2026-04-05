import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, MapPin, Clock, Calendar, Building2, ExternalLink,
  CheckCircle2, Gift, Loader2, Briefcase, Timer, Users, Sparkles
} from 'lucide-react'
import { motion } from 'framer-motion'
import { getListing } from '../services/api'
import './ListingDetail.css'

export default function ListingDetail() {
  const { id } = useParams()
  const [listing, setListing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchListing()
  }, [id])

  const fetchListing = async () => {
    try {
      setLoading(true)
      const data = await getListing(id)
      setListing(data)
    } catch (err) {
      setError('Staj ilanı bulunamadı.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="detail-loading">
        <Loader2 size={32} className="spin" style={{ color: 'var(--accent-light)' }} />
        <p>Yükleniyor...</p>
      </div>
    )
  }

  if (error || !listing) {
    return (
      <div className="detail-loading">
        <p style={{ color: 'var(--rose)' }}>{error || 'İlan bulunamadı.'}</p>
        <Link to="/features" className="btn btn-ghost" style={{ marginTop: '12px' }}>
          <ArrowLeft size={16} /> İlanlara dön
        </Link>
      </div>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--emerald)'
    if (score >= 70) return 'var(--amber)'
    return 'var(--rose)'
  }

  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <Link to="/features" className="detail__back">
            <ArrowLeft size={16} /> Tüm Stajlara Dön
          </Link>
        </div>
      </div>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <motion.div
            className="detail"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {/* Header */}
            <div className="detail__header glass-card">
              <div className="detail__header-top">
                <div className="detail__logo">{listing.logo}</div>
                <div className="detail__header-info">
                  <h1 className="detail__title">{listing.position}</h1>
                  <div className="detail__company">{listing.company}</div>
                  {listing.program_name && (
                    <span className="tag tag-accent">{listing.program_name}</span>
                  )}
                </div>
                <div
                  className="detail__score"
                  style={{ borderColor: getScoreColor(listing.match_score), color: getScoreColor(listing.match_score) }}
                >
                  <span className="detail__score-val">{listing.match_score}</span>
                  <span className="detail__score-label">Eşleşme</span>
                </div>
              </div>

              <div className="detail__meta-row">
                <div className="detail__meta-item">
                  <MapPin size={14} />
                  <span>{listing.location}</span>
                </div>
                <div className="detail__meta-item">
                  <Briefcase size={14} />
                  <span>{listing.type}</span>
                </div>
                {listing.duration && (
                  <div className="detail__meta-item">
                    <Timer size={14} />
                    <span>{listing.duration}</span>
                  </div>
                )}
                {listing.deadline && (
                  <div className="detail__meta-item">
                    <Calendar size={14} />
                    <span>Son başvuru: {new Date(listing.deadline).toLocaleDateString('tr-TR')}</span>
                  </div>
                )}
                {listing.department && (
                  <div className="detail__meta-item">
                    <Building2 size={14} />
                    <span>{listing.department}</span>
                  </div>
                )}
              </div>

              <div className="detail__tags">
                {listing.tags.map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            </div>

            {/* Body Grid */}
            <div className="detail__grid">
              {/* Left Column */}
              <div className="detail__main-col">
                {/* Description */}
                <div className="detail__section glass-card">
                  <h2 className="detail__section-title">Staj Hakkında</h2>
                  <p className="detail__desc">{listing.description}</p>
                </div>

                {/* Requirements */}
                {listing.requirements && listing.requirements.length > 0 && (
                  <div className="detail__section glass-card">
                    <h2 className="detail__section-title">Aranan Nitelikler</h2>
                    <ul className="detail__list">
                      {listing.requirements.map((req, i) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.05 }}
                        >
                          <CheckCircle2 size={16} className="detail__list-icon detail__list-icon--req" />
                          <span>{req}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Benefits */}
                {listing.benefits && listing.benefits.length > 0 && (
                  <div className="detail__section glass-card">
                    <h2 className="detail__section-title">Staj Avantajları</h2>
                    <ul className="detail__list">
                      {listing.benefits.map((b, i) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.05 }}
                        >
                          <Gift size={16} className="detail__list-icon detail__list-icon--benefit" />
                          <span>{b}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Right Column - Sidebar */}
              <div className="detail__sidebar">
                <div className="detail__apply-card glass-card">
                  <h3>Başvuru Yap</h3>
                  <p className="detail__apply-note">
                    Bu staja başvurmak için aşağıdaki butona tıklayarak şirketin resmi kariyer sayfasına yönlendirileceksiniz.
                  </p>
                  <a
                    href={listing.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary detail__apply-btn"
                  >
                    Başvur <ExternalLink size={16} />
                  </a>
                  {listing.source && (
                    <div className="detail__source">
                      Kaynak: <strong>{listing.source}</strong>
                    </div>
                  )}
                </div>

                <div className="detail__info-card glass-card">
                  <h3>Hızlı Bilgi</h3>
                  <div className="detail__info-rows">
                    <div className="detail__info-row">
                      <span className="detail__info-label">Şirket</span>
                      <span className="detail__info-val">{listing.company}</span>
                    </div>
                    <div className="detail__info-row">
                      <span className="detail__info-label">Konum</span>
                      <span className="detail__info-val">{listing.location}</span>
                    </div>
                    <div className="detail__info-row">
                      <span className="detail__info-label">Çalışma Tipi</span>
                      <span className="detail__info-val">{listing.type}</span>
                    </div>
                    {listing.duration && (
                      <div className="detail__info-row">
                        <span className="detail__info-label">Süre</span>
                        <span className="detail__info-val">{listing.duration}</span>
                      </div>
                    )}
                    {listing.deadline && (
                      <div className="detail__info-row">
                        <span className="detail__info-label">Son Başvuru</span>
                        <span className="detail__info-val">{new Date(listing.deadline).toLocaleDateString('tr-TR')}</span>
                      </div>
                    )}
                  </div>
                </div>

                <Link
                  to={`/company-research/${encodeURIComponent(listing.company)}`}
                  className="btn btn-primary detail__ai-btn"
                >
                  <Sparkles size={16} />
                  AI Şirket Analizi
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  )
}
