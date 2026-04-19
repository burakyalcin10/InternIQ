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
          <span className="section-tag">Tum Ozellikler</span>
          <h1 className="section-title">
            Staj surecini donusturen
            <br />
            <span className="text-gradient">bes temel modul.</span>
          </h1>
          <p className="section-desc">
            Her modul, basvuru surecinin farkli bir asamasini otomatize eder.
          </p>
        </div>
      </div>

      <section className="section" id="radar-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">01 · Staj Radar</span>
            <h2 className="section-title">Tum ilanlar, tek yerde.</h2>
            <p className="section-desc">
              LinkedIn, Kariyer.net, Indeed ve sirket sitelerinden toplanan staj ilanlari.
            </p>
          </div>
          <ListingList />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      <section className="section" id="cv-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">02 · CV Tailorer</span>
            <h2 className="section-title">Her ilana ozel, akilli CV.</h2>
            <p className="section-desc">
              Ilan aciklamasini yapistir, AI CV'ni analiz etsin.
            </p>
          </div>
          <CVTailorer />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      <section className="section" id="company-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">03 · Company Intel</span>
            <h2 className="section-title">Sirketi basvurmadan once tani.</h2>
            <p className="section-desc">
              Kultur, tech stack, mulakat tarzi ve guncel haberler.
            </p>
          </div>
          <CompanyCards />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      <section className="section" id="interview-section">
        <div className="wrap">
          <div className="section-head text-center">
            <span className="section-tag">04 · Mock Interview</span>
            <h2 className="section-title">Mulakata guvenle hazirlan.</h2>
            <p className="section-desc">
              Pozisyona ozel sorularla pratik yap, aninda geri bildirim al.
            </p>
          </div>
          <MockInterview />
        </div>
      </section>

      <div className="wrap"><div className="gradient-divider" /></div>

      <section className="section" id="workflow-section">
        <div className="wrap">
          <div className="section-head">
            <span className="section-tag">05 · Basvuru Asistani</span>
            <h2 className="section-title">AI ile basvuru hazirligi.</h2>
            <p className="section-desc">
              LangGraph ile 7 adimli workflow: ilan analizi → CV degerlendirme → skor kontrolu → sirket arastirma → mulakat hazirlik → aksiyon plani.
            </p>
          </div>
          <ApplicationWorkflow />
        </div>
      </section>
    </>
  )
}
