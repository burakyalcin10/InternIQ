import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { CheckCircle2, Loader2, LogIn, Sparkles } from 'lucide-react'
import { useAuth } from '../context/useAuth'
import './AuthPage.css'

const initialForm = {
  email: '',
  password: '',
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isAuthenticated, authLoading } = useAuth()
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!authLoading && isAuthenticated) {
    return <Navigate to="/hesabim" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await login(form)
      navigate('/hesabim')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <span className="section-tag">Giriş Yap</span>
          <h1 className="section-title">
            Kaldığınız yerden devam edin,
            <br />
            <span className="text-gradient">CV profiliniz hep hazır olsun.</span>
          </h1>
        </div>
      </div>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <div className="auth-layout">
            <form className="auth-card glass-card" onSubmit={handleSubmit}>
              <div className="auth-card__header">
                <div className="auth-card__eyebrow">
                  <LogIn size={14} />
                  Supabase Auth
                </div>
                <h2 className="auth-card__title">Giriş yap</h2>
                <p className="auth-card__desc">
                  Kayıtlı CV’nizle analizlere ve başvuru akışlarına anında dönün.
                </p>
              </div>

              <label className="auth-field">
                <span>E-posta</span>
                <input
                  type="email"
                  className="input"
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  placeholder="ornek@mail.com"
                  required
                />
              </label>

              <label className="auth-field">
                <span>Şifre</span>
                <input
                  type="password"
                  className="input"
                  value={form.password}
                  onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                  placeholder="Şifrenizi girin"
                  required
                />
              </label>

              <button className="btn btn-primary auth-btn" disabled={submitting}>
                {submitting ? <Loader2 size={16} className="spin" /> : <LogIn size={16} />}
                Giriş yap
              </button>

              {error && <div className="auth-feedback auth-feedback--error">{error}</div>}
            </form>

            <div className="auth-side glass-card">
              <h2 className="auth-side__title">InternIQ hesabınız neler sağlar?</h2>
              <p className="auth-side__desc">
                Tek seferlik CV yükleme ile tüm AI modülleri aynı profil bağlamı üzerinden çalışır.
              </p>

              <div className="auth-side__list">
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>CV analizi kayıtlı profilinizden otomatik beslenir.</span>
                </div>
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>Başvuru Asistanı ilan bazlı planı CV’nize göre kişiselleştirir.</span>
                </div>
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>Supabase oturumu ile daha profesyonel ve gerçekçi bir akış sunulur.</span>
                </div>
              </div>

              <p className="auth-side__footer">
                Henüz hesabınız yok mu? <Link to="/kayit">Kayıt olun</Link>
              </p>
              <p className="auth-side__footer" style={{ marginTop: 10 }}>
                <Sparkles size={14} style={{ verticalAlign: 'text-bottom', marginRight: 6 }} />
                Giriş yaptıktan sonra üst menüde <strong>Hesabım</strong> görünür.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
