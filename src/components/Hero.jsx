import { Link } from 'react-router-dom'
import { ArrowRight, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import './Hero.css'

export default function Hero() {
  return (
    <section className="hero">
      {/* Animated background orbs */}
      <div className="hero__orbs">
        <div className="hero__orb hero__orb--1" />
        <div className="hero__orb hero__orb--2" />
        <div className="hero__orb hero__orb--3" />
      </div>

      {/* Grid pattern overlay */}
      <div className="hero__grid-pattern" />

      <div className="wrap">
        <div className="hero__inner">
          <motion.div
            className="hero__badge"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Zap size={12} />
            <span>AI destekli staj platformu</span>
          </motion.div>

          <motion.h1
            className="hero__title"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            Doğru stajı bul,
            <br />
            <span className="text-gradient">hazırlığını AI'a bırak.</span>
          </motion.h1>

          <motion.p
            className="hero__desc"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            İlanları tek yerde topla, CV'ni her pozisyona göre optimize et,
            şirketi tanı, mülakata hazırlan — hepsi bir platformda.
          </motion.p>

          <motion.div
            className="hero__btns"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.45 }}
          >
            <Link to="/features" className="btn btn-primary">
              Keşfet <ArrowRight size={16} />
            </Link>
            <Link to="/about" className="btn btn-secondary">
              Nasıl çalışır?
            </Link>
          </motion.div>

          <motion.div
            className="hero__stats"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <div className="hero__stat">
              <span className="hero__stat-val">4</span>
              <span className="hero__stat-label">AI Agent</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-val">500+</span>
              <span className="hero__stat-label">Staj İlanı</span>
            </div>
            <div className="hero__stat-divider" />
            <div className="hero__stat">
              <span className="hero__stat-val">%95</span>
              <span className="hero__stat-label">ATS Uyum</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
