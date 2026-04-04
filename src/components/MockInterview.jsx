import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { getInterviewQuestion, evaluateAnswer } from '../services/api'
import './MockInterview.css'

export default function MockInterview() {
  const [category, setCategory] = useState('technical')
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Mock Interview\'a hoş geldiniz! Bir kategori seçin ve "Başla" yazarak mülakata başlayın.' }
  ])
  const [input, setInput] = useState('')
  const [questionIndex, setQuestionIndex] = useState(0)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [started, setStarted] = useState(false)
  const [waiting, setWaiting] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, text) => {
    setMessages(prev => [...prev, { role, text }])
  }

  const fetchQuestion = async (cat, index) => {
    try {
      const data = await getInterviewQuestion(cat, index)
      if (data.done) {
        addMessage('bot', '✅ Tüm soruları tamamladınız! Tekrar "Başla" yazarak yeni bir mülakat başlatabilirsiniz.')
        setStarted(false)
        return
      }
      setCurrentQuestion(data.question)
      addMessage('bot', `Soru ${data.current}/${data.total} [${data.category} · ${data.difficulty}]\n\n${data.question}`)
    } catch (err) {
      console.error('Interview question error:', err)
      addMessage('bot', '⚠️ Soru yüklenirken bir hata oluştu. Backend bağlantısını kontrol edin.')
    }
  }

  const handleSend = async () => {
    const text = input.trim()
    if (!text || waiting) return
    setInput('')

    addMessage('user', text)
    setWaiting(true)

    if (text.toLowerCase() === 'başla' || text.toLowerCase() === 'basla') {
      setStarted(true)
      setQuestionIndex(0)
      await fetchQuestion(category, 0)
      setWaiting(false)
      return
    }

    if (started && currentQuestion) {
      try {
        // Evaluate the answer via backend
        const evalData = await evaluateAnswer(currentQuestion, text)
        addMessage('bot', `${evalData.feedback}\n\n📊 Puan: ${evalData.score}/100`)

        const nextIndex = questionIndex + 1
        setQuestionIndex(nextIndex)

        // Fetch next question after a short delay
        setTimeout(async () => {
          await fetchQuestion(category, nextIndex)
          setWaiting(false)
        }, 1000)
        return
      } catch (err) {
        console.error('Evaluate error:', err)
        addMessage('bot', '⚠️ Değerlendirme sırasında bir hata oluştu.')
      }
    } else {
      addMessage('bot', '"Başla" yazarak yeni bir mülakat başlatabilirsiniz.')
    }

    setWaiting(false)
  }

  const handleCategoryChange = (cat) => {
    setCategory(cat)
    setStarted(false)
    setQuestionIndex(0)
    setCurrentQuestion(null)
    setMessages([
      { role: 'bot', text: `${cat === 'technical' ? 'Teknik' : 'Davranışsal'} mülakat modunu seçtiniz. "Başla" yazarak başlayın.` }
    ])
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend()
  }

  return (
    <div className="chat glass-card">
      <div className="chat__header">
        <div className="chat__header-left">
          <Bot size={18} style={{ color: 'var(--accent-light)' }} />
          <span>Mock Interview</span>
        </div>
        <div className="chat__categories">
          <button
            className={`chat__cat-btn ${category === 'technical' ? 'chat__cat-btn--active' : ''}`}
            onClick={() => handleCategoryChange('technical')}
          >
            Teknik
          </button>
          <button
            className={`chat__cat-btn ${category === 'behavioral' ? 'chat__cat-btn--active' : ''}`}
            onClick={() => handleCategoryChange('behavioral')}
          >
            Davranışsal
          </button>
        </div>
      </div>

      <div className="chat__messages">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              className={`chat__msg chat__msg--${msg.role}`}
              initial={{ opacity: 0, y: 10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.25 }}
            >
              <div className="chat__msg-avatar">
                {msg.role === 'bot' ? <Bot size={14} /> : <User size={14} />}
              </div>
              <div className="chat__msg-text">{msg.text}</div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="chat__input-row">
        <input
          type="text"
          className="chat__input"
          placeholder="Cevabınızı yazın veya 'Başla' diyerek başlayın..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={waiting}
        />
        <button className="chat__send-btn" onClick={handleSend} disabled={!input.trim() || waiting}>
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
