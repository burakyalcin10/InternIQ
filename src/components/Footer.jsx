import { Link } from 'react-router-dom'
import { ExternalLink, Globe, Mail } from 'lucide-react'
import Logo from './Logo'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer__grid">
          <div className="footer__brand-col">
            <Link to="/" className="footer__brand">
              <Logo size={28} standalone />
              <span>InternIQ</span>
            </Link>
            <p className="footer__tagline">
              AI destekli staj arama platformu. Doğru stajı bul, hazırlığını AI'a bırak.
            </p>
          </div>

          <div className="footer__col">
            <h4>Platform</h4>
            <Link to="/features">Staj Radar</Link>
            <Link to="/features">CV Tailorer</Link>
            <Link to="/features">Company Intel</Link>
            <Link to="/features">Mock Interview</Link>
          </div>

          <div className="footer__col">
            <h4>Hakkında</h4>
            <Link to="/about">Proje</Link>
            <Link to="/about">Mimari</Link>
            <Link to="/about">Yol Haritası</Link>
            <Link to="/about">AI Agentlar</Link>
          </div>

          <div className="footer__col">
            <h4>İletişim</h4>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              <ExternalLink size={14} /> GitHub
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">
              <Globe size={14} /> LinkedIn
            </a>
            <a href="mailto:info@interniq.com">
              <Mail size={14} /> E-posta
            </a>
          </div>
        </div>

        <div className="footer__bottom">
          <span>© 2026 InternIQ. Tüm hakları saklıdır.</span>
          <div className="footer__tech">
            <span className="tag">React</span>
            <span className="tag">FastAPI</span>
            <span className="tag">CrewAI</span>
            <span className="tag">Supabase</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
