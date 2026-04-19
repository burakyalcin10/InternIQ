import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { CheckCircle2, Loader2, Sparkles, UserPlus } from 'lucide-react'
import { useAuth } from '../context/useAuth'
import './AuthPage.css'

const initialForm = {
  name: '',
  email: '',
  password: '',
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, isAuthenticated, authLoading } = useAuth()
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  if (!authLoading && isAuthenticated) {
    return <Navigate to="/hesabim" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setMessage('')

    try {
      const result = await register(form)
      if (result.requiresEmailConfirmation) {
        setMessage(result.message)
      } else {
        navigate('/hesabim')
      }
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
          <span className="section-tag">Kayıt Ol</span>
          <h1 className="section-title">
            CV profilinizi oluşturun,
            <br />
            <span className="text-gradient">InternIQ sizin için çalışmaya başlasın.</span>
          </h1>
        </div>
      </div>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <div className="auth-layout">
            <form className="auth-card glass-card" onSubmit={handleSubmit}>
              <div className="auth-card__header">
                <div className="auth-card__eyebrow">
                  <UserPlus size={14} />
                  Supabase Auth
                </div>
                <h2 className="auth-card__title">Yeni hesap oluştur</h2>
                <p className="auth-card__desc">
                  Hesabınızı oluşturun, ardından CV’nizi ekleyip tüm AI modüllerini ortak profil üzerinden kullanın.
                </p>
              </div>

              <label className="auth-field">
                <span>Ad Soyad</span>
                <input
                  className="input"
                  value={form.name}
                  onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                  placeholder="Örn. Burak Yalçın"
                  required
                />
              </label>

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
                  placeholder="En az 6 karakter"
                  required
                />
              </label>

              <button className="btn btn-primary auth-btn" disabled={submitting}>
                {submitting ? <Loader2 size={16} className="spin" /> : <UserPlus size={16} />}
                Kayıt ol
              </button>

              {error && <div className="auth-feedback auth-feedback--error">{error}</div>}
              {message && <div className="auth-feedback auth-feedback--success">{message}</div>}
            </form>

            <div className="auth-side glass-card">
              <h2 className="auth-side__title">Kayıt olduktan sonra neler değişir?</h2>
              <p className="auth-side__desc">
                Sisteme giriş yaptıktan sonra üst menüde <strong>Hesabım</strong> sekmesi açılır ve profiliniz kalıcı hale gelir.
              </p>

              <div className="auth-side__list">
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>PDF CV yükleyip tek merkezden profil yönetebilirsiniz.</span>
                </div>
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>CV Tailorer ve Başvuru Asistanı kayıtlı CV’yi otomatik kullanır.</span>
                </div>
                <div className="auth-side__item">
                  <CheckCircle2 size={16} />
                  <span>Supabase oturum yapısı sayesinde demo değil ürün hissi veren bir giriş deneyimi oluşur.</span>
                </div>
              </div>

              <p className="auth-side__footer">
                Zaten hesabınız var mı? <Link to="/giris">Giriş yapın</Link>
              </p>
              <p className="auth-side__footer" style={{ marginTop: 10 }}>
                <Sparkles size={14} style={{ verticalAlign: 'text-bottom', marginRight: 6 }} />
                E-posta doğrulaması açıksa kayıt sonrası doğrulama bağlantısını da kontrol edin.
              </p>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
