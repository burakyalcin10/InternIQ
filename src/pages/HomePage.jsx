import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import Hero from '../components/Hero'
import BentoGrid from '../components/BentoGrid'
import StepCards from '../components/StepCards'
import ListingList from '../components/ListingList'
import { motion } from 'framer-motion'

export default function HomePage() {
  return (
    <>
      <Hero />

      {/* Features Bento */}
      <section className="section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">Özellikler</span>
            <h2 className="section-title">Dört modül, dört gerçek sorun.</h2>
            <p className="section-desc">
              Her biri staj sürecinin farklı bir acısını çözmek için tasarlandı.
            </p>
          </div>
          <BentoGrid />
        </div>
      </section>

      {/* Metrics */}
      <section className="section">
        <div className="wrap">
          <motion.div
            className="metrics-row"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="metric-card glass-card">
              <span className="metric-card__val">500<span className="metric-card__plus">+</span></span>
              <span className="metric-card__label">Aktif Staj İlanı</span>
            </div>
            <div className="metric-card glass-card">
              <span className="metric-card__val">50<span className="metric-card__plus">+</span></span>
              <span className="metric-card__label">Şirket Profili</span>
            </div>
            <div className="metric-card glass-card">
              <span className="metric-card__val">1.2k<span className="metric-card__plus">+</span></span>
              <span className="metric-card__label">Mülakat Sorusu</span>
            </div>
            <div className="metric-card glass-card">
              <span className="metric-card__val">%95</span>
              <span className="metric-card__label">ATS Uyumluluk</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section className="section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">Nasıl Çalışır</span>
            <h2 className="section-title">Üç adımda staj başvurusu.</h2>
            <p className="section-desc">
              Profil oluştur, ilanları keşfet, hazırlan ve başvur.
            </p>
          </div>
          <StepCards />
        </div>
      </section>

      {/* Featured Listings */}
      <section className="section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">Güncel İlanlar</span>
            <h2 className="section-title">Öne çıkan staj fırsatları</h2>
            <p className="section-desc">Türkiye'nin önde gelen teknoloji şirketlerinden.</p>
          </div>
          <ListingList limit={4} />
          <div className="section-cta">
            <Link to="/features" className="btn btn-secondary">
              Tüm ilanları gör <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="section">
        <div className="wrap">
          <motion.div
            className="cta-banner"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="cta-banner__glow" />
            <div className="cta-banner__content">
              <Sparkles size={20} className="cta-banner__icon" />
              <h3 className="cta-banner__title">Staj arama sürecini dönüştürmeye hazır mısın?</h3>
              <p className="cta-banner__desc">
                4 AI agent, seni doğru staja bir adım daha yaklaştırsın.
              </p>
              <div className="cta-banner__btns">
                <Link to="/features" className="btn btn-primary">
                  Hemen Başla <ArrowRight size={16} />
                </Link>
                <Link to="/about" className="btn btn-ghost">
                  Daha fazla bilgi
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </>
  )
}
