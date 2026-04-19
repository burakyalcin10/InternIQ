import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Zap, Gauge, Trophy } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  getInterviewQuestion, evaluateAnswer,
  lgStartInterview, lgAnswerQuestion
} from '../services/api'
import './MockInterview.css'

export default function MockInterview() {
  const [category, setCategory] = useState('technical')
  const [mode, setMode] = useState('ai') // 'ai' (LangGraph) or 'basic'
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Mock Interview\'a hoş geldiniz! AI modunda LangGraph destekli akıllı mülakat deneyimi yaşayın. "Başla" yazarak mülakata başlayın.' }
  ])
  const [input, setInput] = useState('')
  const [questionIndex, setQuestionIndex] = useState(0)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [started, setStarted] = useState(false)
  const [waiting, setWaiting] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [difficulty, setDifficulty] = useState('medium')
  const [lastScore, setLastScore] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, text) => {
    setMessages(prev => [...prev, { role, text }])
  }

  // ── AI Mode (LangGraph) ──

  const handleAIStart = async () => {
    try {
      const data = await lgStartInterview('Genel', 'Yazılım Mühendisi Stajyeri', category, 5)
      setSessionId(data.session_id)
      setStarted(true)
      setDifficulty(data.difficulty || 'medium')
      addMessage('bot', `📝 Soru ${data.question_number}/${data.total_questions} [${data.difficulty}]\n\n${data.question}`)
      setCurrentQuestion(data.question)
    } catch (err) {
      console.error('LG start error:', err)
      addMessage('bot', '⚠️ LangGraph mülakatı başlatılamadı. Backend bağlantısını kontrol edin.')
    }
  }

  const handleAIAnswer = async (text) => {
    try {
      const data = await lgAnswerQuestion(sessionId, text)
      setDifficulty(data.difficulty || 'medium')
      setLastScore(data.score)

      if (data.phase === 'completed') {
        addMessage('bot', `📊 Değerlendirme: ${data.feedback}\n\n📊 Puan: ${data.score}/100`)
        addMessage('bot', `🏆 Mülakat Tamamlandı!\n\n${data.summary}\n\n📈 Ortalama Puan: ${data.average_score?.toFixed(0)}/100\n📊 Toplam Soru: ${data.total_questions}`)
        setStarted(false)
        setSessionId(null)
      } else {
        addMessage('bot', `📊 Değerlendirme: ${data.feedback}\n\n📊 Puan: ${data.score}/100`)
        setTimeout(() => {
          addMessage('bot', `📝 Soru ${data.question_number}/${data.total_questions} [${data.difficulty}]\n\n${data.question}`)
          setCurrentQuestion(data.question)
          setWaiting(false)
        }, 800)
        return
      }
    } catch (err) {
      console.error('LG answer error:', err)
      addMessage('bot', '⚠️ Değerlendirme sırasında bir hata oluştu.')
    }
    setWaiting(false)
  }

  // ── Basic Mode ──

  const fetchQuestion = async (cat, index) => {
    try {
      const data = await getInterviewQuestion(cat, index)
      if (data.done) {
        addMessage('bot', '✅ Tüm soruları tamamladınız! "Başla" yazarak yeni bir mülakat başlatabilirsiniz.')
        setStarted(false)
        return
      }
      setCurrentQuestion(data.question)
      addMessage('bot', `Soru ${data.current}/${data.total} [${data.category} · ${data.difficulty}]\n\n${data.question}`)
    } catch (err) {
      addMessage('bot', '⚠️ Soru yüklenirken bir hata oluştu.')
    }
  }

  // ── Send Handler ──

  const handleSend = async () => {
    const text = input.trim()
    if (!text || waiting) return
    setInput('')
    addMessage('user', text)
    setWaiting(true)

    if (text.toLowerCase() === 'başla' || text.toLowerCase() === 'basla') {
      setQuestionIndex(0)
      if (mode === 'ai') {
        await handleAIStart()
      } else {
        setStarted(true)
        await fetchQuestion(category, 0)
      }
      setWaiting(false)
      return
    }

    if (!started) {
      addMessage('bot', '"Başla" yazarak yeni bir mülakat başlatabilirsiniz.')
      setWaiting(false)
      return
    }

    if (mode === 'ai' && sessionId) {
      await handleAIAnswer(text)
    } else {
      // Basic mode
      try {
        const evalData = await evaluateAnswer(currentQuestion, text)
        setLastScore(evalData.score)
        addMessage('bot', `${evalData.feedback}\n\n📊 Puan: ${evalData.score}/100`)
        const nextIndex = questionIndex + 1
        setQuestionIndex(nextIndex)
        setTimeout(async () => {
          await fetchQuestion(category, nextIndex)
          setWaiting(false)
        }, 1000)
        return
      } catch (err) {
        addMessage('bot', '⚠️ Değerlendirme sırasında bir hata oluştu.')
      }
      setWaiting(false)
    }
  }

  const handleCategoryChange = (cat) => {
    setCategory(cat)
    setStarted(false)
    setQuestionIndex(0)
    setCurrentQuestion(null)
    setSessionId(null)
    setLastScore(null)
    setMessages([
      { role: 'bot', text: `${cat === 'technical' ? 'Teknik' : 'Davranışsal'} mülakat modunu seçtiniz. "Başla" yazarak başlayın.` }
    ])
  }

  const handleModeChange = (newMode) => {
    setMode(newMode)
    setStarted(false)
    setQuestionIndex(0)
    setCurrentQuestion(null)
    setSessionId(null)
    setLastScore(null)
    setMessages([
      { role: 'bot', text: newMode === 'ai'
        ? '🤖 AI Mülakat modu — LangGraph ile akıllı soru üretimi, AI değerlendirme ve dinamik zorluk ayarı. "Başla" yazarak başlayın.'
        : '📋 Basit Mülakat modu — Hazır soru havuzundan sorular. "Başla" yazarak başlayın.'
      }
    ])
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend()
  }

  const getDifficultyColor = () => {
    if (difficulty === 'hard') return 'var(--rose)'
    if (difficulty === 'easy') return 'var(--emerald)'
    return 'var(--amber)'
  }

  return (
    <div className="chat glass-card">
      <div className="chat__header">
        <div className="chat__header-left">
          <Bot size={18} style={{ color: 'var(--accent-light)' }} />
          <span>Mock Interview</span>
          {mode === 'ai' && (
            <span className="chat__lg-badge">
              <Zap size={10} /> LangGraph
            </span>
          )}
        </div>
        <div className="chat__header-controls">
          <div className="chat__mode-toggle">
            <button
              className={`chat__mode-btn ${mode === 'ai' ? 'chat__mode-btn--active' : ''}`}
              onClick={() => handleModeChange('ai')}
            >
              <Zap size={12} /> AI
            </button>
            <button
              className={`chat__mode-btn ${mode === 'basic' ? 'chat__mode-btn--active' : ''}`}
              onClick={() => handleModeChange('basic')}
            >
              Basic
            </button>
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
      </div>

      {/* Status Bar */}
      {started && mode === 'ai' && (
        <div className="chat__status-bar">
          <div className="chat__status-item">
            <Gauge size={13} />
            <span>Zorluk:</span>
            <span className="chat__difficulty" style={{ color: getDifficultyColor() }}>
              {difficulty === 'easy' ? 'Kolay' : difficulty === 'hard' ? 'Zor' : 'Orta'}
            </span>
          </div>
          {lastScore !== null && (
            <div className="chat__status-item">
              <Trophy size={13} />
              <span>Son Puan:</span>
              <span style={{ color: lastScore >= 70 ? 'var(--emerald)' : 'var(--amber)' }}>
                {lastScore}/100
              </span>
            </div>
          )}
        </div>
      )}

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
