import ListingList from '../components/ListingList'
import CVTailorer from '../components/CVTailorer'
import CompanyCards from '../components/CompanyCards'
import MockInterview from '../components/MockInterview'
import ApplicationWorkflow from '../components/ApplicationWorkflow'

export default function FeaturesPage() {
  return (
    <>
      <div className="page-top">
        <div className="wrap">
          <span className="section-tag">Tüm Özellikler</span>
          <h1 className="section-title">
            Staj sürecini dönüştüren
            <br />
            <span className="text-gradient">dört temel modül.</span>
          </h1>
          <p className="section-desc">
            Her modül, başvuru sürecinin farklı bir aşamasını otomatize eder.
          </p>
        </div>
      </div>

      {/* Staj Radar */}
      <section className="section" id="radar-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">01 · Staj Radar</span>
            <h2 className="section-title">Tüm ilanlar, tek yerde.</h2>
            <p className="section-desc">
              LinkedIn, Kariyer.net, Indeed ve şirket sitelerinden toplanan staj ilanları.
            </p>
          </div>
          <ListingList />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* CV Tailorer */}
      <section className="section" id="cv-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">02 · CV Tailorer</span>
            <h2 className="section-title">Her ilana özel, akıllı CV.</h2>
            <p className="section-desc">
              İlan açıklamasını yapıştır, AI CV'ni analiz etsin.
            </p>
          </div>
          <CVTailorer />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Company Intel */}
      <section className="section" id="company-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">03 · Company Intel</span>
            <h2 className="section-title">Şirketi başvurmadan önce tanı.</h2>
            <p className="section-desc">
              Kültür, tech stack, mülakat tarzı ve güncel haberler.
            </p>
          </div>
          <CompanyCards />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Mock Interview */}
      <section className="section" id="interview-section">
        <div className="wrap">
          <div className="section-head text-center">
            <span className="section-tag">04 · Mock Interview</span>
            <h2 className="section-title">Mülakata güvenle hazırlan.</h2>
            <p className="section-desc">
              Pozisyona özel sorularla pratik yap, anında geri bildirim al.
            </p>
          </div>
          <MockInterview />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      {/* Application Workflow (LangGraph) */}
      <section className="section" id="workflow-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">05 · Başvuru Asistanı</span>
            <h2 className="section-title">AI ile başvuru hazırlığı.</h2>
            <p className="section-desc">
              LangGraph ile 6 adımlı akıllı workflow: ilan analizi → CV değerlendirme → şirket araştırma → mülakat hazırlık → aksiyon planı.
            </p>
          </div>
          <ApplicationWorkflow />
        </div>
      </section>
    </>
  )
}
