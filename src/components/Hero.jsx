import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import './Hero.css'

const FEATURES = [
  { num: '01', name: 'Staj Radar', desc: 'İlan toplama & filtreleme' },
  { num: '02', name: 'CV Tailorer', desc: 'ATS optimizasyonu' },
  { num: '03', name: 'Company Intel', desc: 'Şirket araştırması' },
  { num: '04', name: 'Mock Interview', desc: 'AI mülakat koçu' },
]

export default function Hero() {
  return (
    <section className="hero">
      <div className="wrap">
        <div className="hero__inner">

          <motion.div
            className="hero__top-bar"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <span className="hero__label">InternIQ — AI Staj Platformu</span>
            <span className="hero__label hero__label--right">v2.0 · 2025</span>
          </motion.div>

          <div className="hero__rule" />

          <div className="hero__content">
            <div className="hero__left">
              <motion.h1
                className="hero__title"
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.55, delay: 0.1 }}
              >
                Doğru stajı<br />
                bul, hazırlığını<br />
                <span className="hero__title--accent">AI'a bırak.</span>
              </motion.h1>

              <motion.p
                className="hero__desc"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, delay: 0.25 }}
              >
                İlanları tek yerde topla, CV'ni her pozisyona göre optimize et,
                şirketi tanı, mülakata hazırlan.
              </motion.p>

              <motion.div
                className="hero__btns"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.38 }}
              >
                <Link to="/features" className="btn btn-primary">
                  Keşfet <ArrowRight size={15} />
                </Link>
                <Link to="/about" className="btn btn-secondary">
                  Nasıl çalışır?
                </Link>
              </motion.div>
            </div>

            <motion.div
              className="hero__right"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              {FEATURES.map((f, i) => (
                <motion.div
                  key={f.num}
                  className="hero__feature"
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.35, delay: 0.3 + i * 0.07 }}
                >
                  <span className="hero__feature-num">{f.num}</span>
                  <div className="hero__feature-text">
                    <span className="hero__feature-name">{f.name}</span>
                    <span className="hero__feature-desc">{f.desc}</span>
                  </div>
                  <ArrowRight size={13} className="hero__feature-arrow" />
                </motion.div>
              ))}
            </motion.div>
          </div>

          <div className="hero__rule" />

          <motion.div
            className="hero__stats"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.5 }}
          >
            <span>4 AI Agent</span>
            <span className="hero__stat-sep" />
            <span>500+ İlan</span>
            <span className="hero__stat-sep" />
            <span>%95 ATS Uyum</span>
            <span className="hero__stat-sep" />
            <span>MCP + LangGraph</span>
          </motion.div>

        </div>
      </div>
    </section>
  )
}
