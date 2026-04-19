import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, Sparkles, UserRound, X } from 'lucide-react'
import { useAuth } from '../context/useAuth'
import './Navbar.css'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 30)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { to: '/', label: 'Ana Sayfa' },
    { to: '/features', label: 'Özellikler' },
    { to: '/about', label: 'Hakkında' },
    ...(isAuthenticated ? [{ to: '/hesabim', label: 'Hesabım' }] : []),
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
          <Link
            to={isAuthenticated ? '/hesabim' : '/giris'}
            className="navbar__cta"
            onClick={() => setIsOpen(false)}
          >
            <UserRound size={15} />
            {isAuthenticated ? 'Hesabım' : 'Giriş Yap'}
          </Link>
        </div>

        <button
          className="navbar__toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Menüyü aç veya kapat"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
    </nav>
  )
}
