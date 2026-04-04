import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { MapPin, Clock, TrendingUp, Search, Filter, Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { getListings } from '../services/api'
import './ListingList.css'

export default function ListingList({ limit }) {
  const [listings, setListings] = useState([])
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchListings()
  }, [])

  const fetchListings = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getListings()
      setListings(data.listings || [])
    } catch (err) {
      console.error('Listings fetch error:', err)
      setError('İlanlar yüklenirken bir hata oluştu.')
    } finally {
      setLoading(false)
    }
  }

  const filteredListings = listings.filter((l) => {
    const matchSearch = !search
      || l.position.toLowerCase().includes(search.toLowerCase())
      || l.company.toLowerCase().includes(search.toLowerCase())
      || l.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
    const matchType = typeFilter === 'all' || l.type === typeFilter
    return matchSearch && matchType
  })

  const displayListings = limit ? filteredListings.slice(0, limit) : filteredListings

  const getScoreClass = (score) => {
    if (score >= 85) return 'listing__score--high'
    if (score >= 70) return 'listing__score--mid'
    return 'listing__score--low'
  }

  if (loading) {
    return (
      <div className="listings__empty">
        <Loader2 size={24} className="spin" style={{ color: 'var(--accent-light)' }} />
        <p style={{ marginTop: '12px' }}>İlanlar yükleniyor...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="listings__empty">
        <p style={{ color: 'var(--rose)' }}>{error}</p>
        <button className="btn btn-ghost" onClick={fetchListings} style={{ marginTop: '8px' }}>
          Tekrar Dene
        </button>
      </div>
    )
  }

  return (
    <div className="listings">
      {!limit && (
        <div className="listings__filters">
          <div className="listings__search-wrap">
            <Search size={16} className="listings__search-icon" />
            <input
              type="text"
              className="input listings__search"
              placeholder="Pozisyon, şirket veya teknoloji ara..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="listings__filter-wrap">
            <Filter size={16} className="listings__filter-icon" />
            <select
              className="input listings__type-select"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="all">Tüm Tipler</option>
              <option value="Remote">Remote</option>
              <option value="On-site">On-site</option>
              <option value="Hybrid">Hybrid</option>
            </select>
          </div>
        </div>
      )}

      <div className="listings__list">
        {displayListings.map((listing, i) => (
          <motion.div
            key={listing.id}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
          >
            <Link to={`/staj/${listing.id}`} className="listing">
              <div className="listing__main">
                <div className="listing__icon">{listing.logo}</div>
                <div className="listing__info">
                  <div className="listing__title">{listing.position}</div>
                  <div className="listing__company">
                    {listing.company}
                    {listing.source && (
                      <span className="listing__source">· {listing.source}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="listing__meta">
                <span className="listing__loc">
                  <MapPin size={12} /> {listing.location}
                </span>
                <span className="listing__type">
                  <Clock size={12} /> {listing.type}
                </span>
              </div>
              <div className="listing__tags">
                {listing.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
              <div className={`listing__score ${getScoreClass(listing.match_score)}`}>
                <TrendingUp size={12} />
                {listing.match_score}%
              </div>
            </Link>
          </motion.div>
        ))}

        {displayListings.length === 0 && (
          <div className="listings__empty">
            <p>Aramanızla eşleşen ilan bulunamadı.</p>
          </div>
        )}
      </div>
    </div>
  )
}
