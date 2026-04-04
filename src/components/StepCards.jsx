import { UserPlus, Search, Rocket } from 'lucide-react'
import { motion } from 'framer-motion'
import './StepCards.css'

const steps = [
  {
    num: '01',
    title: 'Profil oluştur',
    desc: "CV'ni yükle, ilgi alanlarını belirle. AI profilini analiz etsin.",
    icon: UserPlus,
  },
  {
    num: '02',
    title: 'İlanları keşfet',
    desc: 'Sana özel filtrelenmiş ilanları gör, eşleşme skorlarını incele.',
    icon: Search,
  },
  {
    num: '03',
    title: 'Hazırlan & başvur',
    desc: "CV'ni optimize et, şirketi araştır, mülakata hazırlan.",
    icon: Rocket,
  },
]

export default function StepCards() {
  return (
    <div className="steps">
      {steps.map((step, i) => {
        const Icon = step.icon
        return (
          <motion.div
            key={step.num}
            className="step-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <div className="step-card__line" />
            <div className="step-card__num">{step.num}</div>
            <div className="step-card__icon">
              <Icon size={20} />
            </div>
            <h3 className="step-card__title">{step.title}</h3>
            <p className="step-card__desc">{step.desc}</p>
          </motion.div>
        )
      })}
    </div>
  )
}
