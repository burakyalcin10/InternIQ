import { useRef, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { FileText, FolderKanban, Loader2, LogOut, Upload, UserRound } from 'lucide-react'
import { useAuth } from '../context/useAuth'
import './AccountPage.css'

export default function AccountPage() {
  const { user, profile, authLoading, isAuthenticated, logout, saveProfileCv } = useAuth()
  const [cvText, setCvText] = useState('')
  const [cvFile, setCvFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/giris" replace />
  }

  const formattedUploadDate = profile?.cv_uploaded_at
    ? new Date(profile.cv_uploaded_at).toLocaleString('tr-TR')
    : ''

  const handleCvUpload = async (event) => {
    event.preventDefault()
    if (!cvFile && !cvText.trim()) {
      setError('Bir PDF yükleyin veya CV metni girin.')
      return
    }

    setUploading(true)
    setMessage('')
    setError('')

    try {
      const data = await saveProfileCv({ cvFile, cvText })
      setMessage(data.message)
      setCvFile(null)
      setCvText('')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const handleLogout = async () => {
    setMessage('')
    setError('')
    try {
      await logout()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <span className="section-tag">Hesabım</span>
          <h1 className="section-title">
            CV’nizi bir kez yükleyin,
            <br />
            <span className="text-gradient">tüm AI akışları sizinle çalışsın.</span>
          </h1>
          <p className="section-desc">
            Kayıtlı CV profili sayesinde Başvuru Asistanı, CV analizi ve proje özetleri aynı profil bağlamında çalışır.
          </p>
        </div>
      </div>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="wrap">
          {authLoading ? (
            <div className="account-card glass-card account-card--center">
              <Loader2 size={28} className="spin" />
              <p>Oturum bilgileri yükleniyor...</p>
            </div>
          ) : (
            <div className="account-layout">
              <div className="account-card glass-card">
                <div className="account-card__head">
                  <UserRound size={18} />
                  <div>
                    <h2>{user?.name || 'InternIQ Kullanıcısı'}</h2>
                    <p>{user?.email}</p>
                  </div>
                </div>

                <div className="account-status">
                  <span className={`tag ${profile?.has_cv ? 'tag-emerald' : 'tag-amber'}`}>
                    {profile?.has_cv ? 'CV kayıtlı' : 'CV bekleniyor'}
                  </span>
                  {formattedUploadDate && (
                    <span className="account-status__date">Son güncelleme: {formattedUploadDate}</span>
                  )}
                </div>

                <div className="account-summary">
                  <h3>Profil özeti</h3>
                  <p>{profile?.summary || 'Henüz bir CV özeti oluşturulmadı.'}</p>
                </div>

                <div className="account-meta">
                  <div className="account-meta__item">
                    <strong>Deneyim düzeyi</strong>
                    <span>{profile?.experience_level || 'Belirlenmedi'}</span>
                  </div>
                  <div className="account-meta__item">
                    <strong>Eğitim</strong>
                    <span>{profile?.education_summary || 'CV yüklendiğinde çıkarılacak'}</span>
                  </div>
                </div>

                {profile?.skills?.length > 0 && (
                  <div className="account-tags">
                    {profile.skills.map((skill) => (
                      <span key={skill} className="tag tag-accent">{skill}</span>
                    ))}
                  </div>
                )}

                {profile?.projects?.length > 0 && (
                  <div className="account-projects">
                    <div className="account-projects__head">
                      <FolderKanban size={16} />
                      <strong>Çıkarılan projeler</strong>
                    </div>
                    <div className="account-projects__list">
                      {profile.projects.map((project, index) => (
                        <div key={`${project.title}-${index}`} className="account-project">
                          <strong>{project.title}</strong>
                          {project.description && <p>{project.description}</p>}
                          {project.skills?.length > 0 && (
                            <div className="account-project__tags">
                              {project.skills.map((skill) => (
                                <span key={skill} className="tag">{skill}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="account-actions">
                  <Link className="btn btn-primary" to="/features#workflow-section">
                    Başvuru Asistanı’na git
                  </Link>
                  <button type="button" className="btn btn-ghost" onClick={handleLogout}>
                    <LogOut size={16} /> Çıkış yap
                  </button>
                </div>
              </div>

              <form className="account-card glass-card" onSubmit={handleCvUpload}>
                <div className="account-card__head">
                  <FileText size={18} />
                  <div>
                    <h2>CV profilini güncelle</h2>
                    <p>PDF yükleyin veya CV metnini yapıştırın. Sistem bunu tüm AI akışlarında kullanır.</p>
                  </div>
                </div>

                <div className="account-upload">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt"
                    className="account-upload__input"
                    onChange={(event) => setCvFile(event.target.files?.[0] || null)}
                  />
                  <button
                    type="button"
                    className="account-upload__button"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload size={16} /> PDF veya metin dosyası seç
                  </button>
                  <span className="account-upload__hint">
                    {cvFile ? `${cvFile.name} seçildi` : 'Dosya seçmezseniz aşağıdaki metin alanı kullanılır.'}
                  </span>
                </div>

                <label className="account-field">
                  <span>CV metni</span>
                  <textarea
                    className="input account-textarea"
                    value={cvText}
                    onChange={(event) => setCvText(event.target.value)}
                    placeholder="CV’nizin düz metnini buraya yapıştırabilirsiniz."
                  />
                </label>

                {profile?.has_cv && (
                  <div className="account-preview">
                    <strong>Mevcut CV özeti</strong>
                    <p>{profile.summary}</p>
                  </div>
                )}

                <button className="btn btn-primary account-btn" disabled={uploading}>
                  {uploading ? <Loader2 size={16} className="spin" /> : <Upload size={16} />}
                  CV’yi kaydet
                </button>
              </form>
            </div>
          )}

          {(message || error) && (
            <div className={`account-feedback glass-card ${error ? 'account-feedback--error' : 'account-feedback--success'}`}>
              {error || message}
            </div>
          )}
        </div>
      </section>
    </>
  )
}
