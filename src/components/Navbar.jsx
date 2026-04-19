import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Sparkles } from 'lucide-react'
import './Navbar.css'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 30)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { to: '/', label: 'Ana Sayfa' },
    { to: '/features', label: 'Ozellikler' },
    { to: '/about', label: 'Hakkinda' },
  ]

  return (
    <nav className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
      <div className="navbar__inner">
        <Link to="/" className="navbar__brand" onClick={() => setIsOpen(false)}>
          <div className="navbar__logo">
            <Sparkles size={18} />
          </div>
          <span>InternIQ</span>
        </Link>

        <div className={`navbar__links ${isOpen ? 'navbar__links--open' : ''}`}>
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`navbar__link ${location.pathname === link.to ? 'navbar__link--active' : ''}`}
              onClick={() => setIsOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <Link to="/features" className="navbar__cta" onClick={() => setIsOpen(false)}>
            Basla
          </Link>
        </div>

        <button
          className="navbar__toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
    </nav>
  )
}
