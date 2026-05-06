import { useState } from 'react'
import {
  Bot,
  ChevronRight,
  Loader2,
  MessageSquare,
  Send,
  Terminal,
  Wrench,
} from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { agentChat } from '../services/api'
import './AgentChat.css'

const EXAMPLE_QUERIES = [
  'Python stajı ara',
  'ASELSAN hakkında bilgi ver',
  '1 numaralı ilan için başvuru hazırlığı yap',
  'Mülakat sorusu sor, yazılım mühendisliği',
  'InternIQ özelliklerini listele',
]

function ToolCallItem({ call, index }) {
  const [expanded, setExpanded] = useState(false)
  const resultStr = JSON.stringify(call.result, null, 2)
  const preview = resultStr.length > 300 ? resultStr.slice(0, 300) + '\n...' : resultStr

  return (
    <motion.div
      className="agent__tool-call"
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
    >
      <button className="agent__tool-header" onClick={() => setExpanded(!expanded)}>
        <ChevronRight size={12} className={`agent__tool-chevron ${expanded ? 'agent__tool-chevron--open' : ''}`} />
        <span className="agent__tool-name">{call.tool}</span>
        <span className="agent__tool-args">
          {JSON.stringify(call.args)}
        </span>
      </button>
      {expanded && (
        <pre className="agent__tool-result">{preview}</pre>
      )}
    </motion.div>
  )
}

export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentQuery, setCurrentQuery] = useState('')

  const handleSubmit = async (query) => {
    const q = (query ?? message).trim()
    if (!q || loading) return

    setLoading(true)
    setResult(null)
    setError(null)
    setCurrentQuery(q)
    if (!query) setMessage('')

    try {
      const data = await agentChat(q)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Ajan yanıt veremedi. Backend bağlantısını kontrol edin.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="agent">
      <div className="agent__header">
        <div className="agent__header-icon">
          <Bot size={22} />
        </div>
        <div>
          <h2>MCP AI Ajan</h2>
          <p className="agent__header-sub">
            LLM, MCP sunucusunu keşfeder ve hangi araçları çağıracağına kendisi karar verir
          </p>
        </div>
      </div>

      <div className="agent__arch glass-card">
        <div className="agent__arch-step">
          <span className="agent__arch-label">Kullanıcı</span>
          <span className="agent__arch-desc">Doğal dil sorgu</span>
        </div>
        <ChevronRight size={14} className="agent__arch-arrow" />
        <div className="agent__arch-step agent__arch-step--highlight">
          <span className="agent__arch-label">LLM (GPT-4o-mini)</span>
          <span className="agent__arch-desc">MCP Host — araç seçimi</span>
        </div>
        <ChevronRight size={14} className="agent__arch-arrow" />
        <div className="agent__arch-step">
          <span className="agent__arch-label">MCP Server</span>
          <span className="agent__arch-desc">stdio transport</span>
        </div>
        <ChevronRight size={14} className="agent__arch-arrow" />
        <div className="agent__arch-step">
          <span className="agent__arch-label">Yanıt</span>
          <span className="agent__arch-desc">Sentezlenmiş cevap</span>
        </div>
      </div>

      <div className="agent__input-area glass-card">
        <textarea
          className="agent__textarea input"
          placeholder="Bir şey sor: 'ASELSAN hakkında bilgi ver' veya 'Python stajı ara'..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          disabled={loading}
        />
        <button
          className="btn btn-primary agent__send"
          onClick={() => handleSubmit()}
          disabled={loading || !message.trim()}
        >
          {loading ? <Loader2 size={15} className="agent__spin" /> : <Send size={15} />}
          {loading ? 'Çalışıyor...' : 'Gönder'}
        </button>
      </div>

      {!result && !loading && (
        <div className="agent__examples">
          <span className="agent__examples-label">Örnek sorular</span>
          <div className="agent__example-chips">
            {EXAMPLE_QUERIES.map((q) => (
              <button
                key={q}
                className="agent__example-chip"
                onClick={() => handleSubmit(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading && (
        <motion.div
          className="agent__loading glass-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <Loader2 size={18} className="agent__spin" />
          <div>
            <div className="agent__loading-title">LLM MCP araçlarını keşfediyor ve çalıştırıyor</div>
            <div className="agent__loading-query">&ldquo;{currentQuery}&rdquo;</div>
          </div>
        </motion.div>
      )}

      {error && (
        <motion.div
          className="agent__error glass-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {error}
        </motion.div>
      )}

      <AnimatePresence>
        {result && (
          <motion.div
            className="agent__result"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="agent__query-echo">
              <MessageSquare size={13} />
              <span>{currentQuery}</span>
            </div>

            {result.tool_calls?.length > 0 && (
              <div className="agent__section glass-card">
                <div className="agent__section-label">
                  <Terminal size={13} />
                  MCP Araç Çağrıları — {result.tool_calls.length} araç çalıştı
                </div>
                <div className="agent__tool-calls">
                  {result.tool_calls.map((call, i) => (
                    <ToolCallItem key={i} call={call} index={i} />
                  ))}
                </div>
              </div>
            )}

            {result.tool_calls?.length === 0 && (
              <div className="agent__section glass-card">
                <div className="agent__section-label">
                  <Wrench size={13} />
                  LLM araç çağırmadan yanıt üretti
                </div>
              </div>
            )}

            <motion.div
              className="agent__answer glass-card"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <div className="agent__section-label">
                <Bot size={13} />
                LLM Yanıtı
              </div>
              <div className="agent__answer-text">{result.answer}</div>
            </motion.div>

            <button
              className="agent__new-query"
              onClick={() => { setResult(null); setError(null); setMessage('') }}
            >
              Yeni soru sor
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
