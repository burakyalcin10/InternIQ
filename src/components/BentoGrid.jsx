import { Radar, FileText, Building2, MessageSquare } from 'lucide-react'
import { motion } from 'framer-motion'
import './BentoGrid.css'

const features = [
  {
    num: '01',
    title: 'Staj Radar',
    desc: 'LinkedIn, Kariyer.net, Indeed ve şirket sitelerinden ilanları otomatik tarar, sana özel filtreler.',
    tag: 'Akıllı Arama',
    icon: Radar,
    gradient: 'bento__item--violet',
  },
  {
    num: '02',
    title: 'CV Tailorer',
    desc: 'İlan açıklamasını yapıştır, CV\'ni o pozisyona göre yeniden düzenlesin. ATS skorunu anında gör.',
    tag: 'AI Optimizasyon',
    icon: FileText,
    gradient: 'bento__item--cyan',
  },
  {
    num: '03',
    title: 'Company Intel',
    desc: 'Başvurmadan önce şirket kültürünü, tech stack\'ini, mülakat tarzını ve güncel haberlerini öğren.',
    tag: 'Derin Araştırma',
    icon: Building2,
    gradient: 'bento__item--emerald',
  },
  {
    num: '04',
    title: 'Mock Interview',
    desc: 'Pozisyona ve şirkete özel mülakat soruları ile pratik yap, anında değerlendirme al.',
    tag: 'Mülakat Koçu',
    icon: MessageSquare,
    gradient: 'bento__item--amber',
  },
]

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1 }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
}

export default function BentoGrid() {
  return (
    <motion.div
      className="bento"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-60px' }}
    >
      {features.map((f) => {
        const Icon = f.icon
        return (
          <motion.div
            key={f.num}
            className={`bento__item ${f.gradient}`}
            variants={itemVariants}
          >
            <div className="bento__icon-wrap">
              <Icon size={20} />
            </div>
            <span className="bento__num">{f.num}</span>
            <h3 className="bento__title">{f.title}</h3>
            <p className="bento__desc">{f.desc}</p>
            <span className="bento__tag">{f.tag}</span>
            <div className="bento__glow" />
          </motion.div>
        )
      })}
    </motion.div>
  )
}
