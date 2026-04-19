import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Star, Users, Code2, Loader2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { getCompanies, getListings } from '../services/api'
import './CompanyCards.css'

const normalizeCompanyName = (value) => (
  (value || '')
    .toLocaleLowerCase('tr-TR')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\(.*?\)/g, ' ')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
)

export default function CompanyCards() {
  const navigate = useNavigate()
  const [companies, setCompanies] = useState([])
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      setLoading(true)
      setError(null)

      const [companiesData, listingsData] = await Promise.all([
        getCompanies(),
        getListings({ limit: 50 }),
      ])

      setCompanies(companiesData.companies || [])
      setListings(listingsData.listings || [])
    } catch (err) {
      console.error('Companies fetch error:', err)
      setError('Şirket bilgileri yüklenirken bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  const getMatchingListing = (companyName) => {
    const normalizedCompany = normalizeCompanyName(companyName)
    return listings.find((listing) => normalizeCompanyName(listing.company) === normalizedCompany)
  }

  const handleCardNavigation = (listingId) => {
    if (!listingId) return
    navigate(`/staj/${listingId}`)
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
      {companies.map((company, index) => {
        const matchingListing = getMatchingListing(company.name)
        const listingId = matchingListing?.id

        return (
          <motion.div
            key={company.id || company.name}
            className={`company-card glass-card ${listingId ? 'company-card--clickable' : ''}`}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            onClick={() => handleCardNavigation(listingId)}
            onKeyDown={(event) => {
              if ((event.key === 'Enter' || event.key === ' ') && listingId) {
                event.preventDefault()
                handleCardNavigation(listingId)
              }
            }}
            role={listingId ? 'link' : undefined}
            tabIndex={listingId ? 0 : undefined}
          >
            <div className="company-card__header">
              <div className="company-card__avatar">{company.logo}</div>
              <div>
                <div className="company-card__name">{company.name}</div>
                <div className="company-card__industry">{company.industry} · {company.employees}</div>
              </div>
            </div>

            <div className="company-card__stats">
              <div className="company-card__stat">
                <Star size={14} className="company-card__stat-icon" />
                <span className="company-card__stat-val">{company.rating}</span>
                <span className="company-card__stat-label">Rating</span>
              </div>
              <div className="company-card__stat">
                <Users size={14} className="company-card__stat-icon" />
                <span className="company-card__stat-val">{company.employees}</span>
                <span className="company-card__stat-label">Çalışan</span>
              </div>
              <div className="company-card__stat">
                <Code2 size={14} className="company-card__stat-icon" />
                <span className="company-card__stat-val">{company.tech_stack.length}+</span>
                <span className="company-card__stat-label">Stack</span>
              </div>
            </div>

            <div className="company-card__details">
              <div className="company-card__detail">
                <strong>Kültür:</strong> {company.culture}
              </div>
              <div className="company-card__detail">
                <strong>Mülakat:</strong> {company.interview_style}
              </div>
              <div className="company-card__news">{company.recent_news}</div>
            </div>

            <div className="company-card__tech">
              {company.tech_stack.map((tech) => (
                <span key={tech} className="tag">{tech}</span>
              ))}
            </div>

            {listingId && (
              <div className="company-card__listing-hint">
                İlan detay sayfasına gitmek için karta tıkla
              </div>
            )}

            <Link
              to={`/company-research/${encodeURIComponent(company.name)}`}
              className="btn btn-primary company-card__ai-btn"
              onClick={(event) => event.stopPropagation()}
            >
              <Sparkles size={14} />
              AI Analizi Başlat
            </Link>
          </motion.div>
        )
      })}
    </div>
  )
}
