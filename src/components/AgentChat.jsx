import { useState } from 'react'
import { Bot, ChevronDown, Loader2, Send } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { agentChat } from '../services/api'
import './AgentChat.css'

const EXAMPLE_QUERIES = [
  'Python stajı ara',
  'ASELSAN hakkında bilgi ver',
  '1 numaralı ilan için başvuru hazırlığı yap',
  'Mülakat sorusu sor, yazılım mühendisliği',
]

/* ── Lightweight markdown renderer ─────────────────────────────── */
function processInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i}>{part.slice(2, -2)}</strong>
    if (part.startsWith('*') && part.endsWith('*'))
      return <em key={i}>{part.slice(1, -1)}</em>
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} className="agent__inline-code">{part.slice(1, -1)}</code>
    return part
  })
}

function MarkdownContent({ text }) {
  const lines = (text || '').split('\n')
  const elements = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    if (line.startsWith('### ')) {
      elements.push(<h4 key={i} className="agent__md-h4">{processInline(line.slice(4))}</h4>)
    } else if (line.startsWith('## ')) {
      elements.push(<h3 key={i} className="agent__md-h3">{processInline(line.slice(3))}</h3>)
    } else if (line.startsWith('# ')) {
      elements.push(<h2 key={i} className="agent__md-h2">{processInline(line.slice(2))}</h2>)
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      const items = []
      while (i < lines.length && (lines[i].startsWith('- ') || lines[i].startsWith('* '))) {
        items.push(lines[i].slice(2))
        i++
      }
      elements.push(
        <ul key={`ul-${i}`} className="agent__md-ul">
          {items.map((item, j) => <li key={j}>{processInline(item)}</li>)}
        </ul>
      )
      continue
    } else if (/^\d+\. /.test(line)) {
      const items = []
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ''))
        i++
      }
      elements.push(
        <ol key={`ol-${i}`} className="agent__md-ol">
          {items.map((item, j) => <li key={j}>{processInline(item)}</li>)}
        </ol>
      )
      continue
    } else if (line.trim() === '') {
      if (elements.length > 0) elements.push(<div key={i} className="agent__md-gap" />)
    } else {
      elements.push(<p key={i} className="agent__md-p">{processInline(line)}</p>)
    }
    i++
  }

  return <div className="agent__markdown">{elements}</div>
}

/* ── Tool call row ──────────────────────────────────────────────── */
function ToolRow({ call, index }) {
  const [open, setOpen] = useState(false)
  const argsStr = Object.entries(call.args || {})
    .map(([k, v]) => `${k}: ${typeof v === 'string' ? `"${v.slice(0, 40)}${v.length > 40 ? '…' : ''}"` : v}`)
    .join('  ')

  return (
    <div className="agent__tool-row">
      <div className="agent__tool-row-main">
        <span className="agent__tool-idx">{String(index + 1).padStart(2, '0')}</span>
        <span className="agent__tool-fn">{call.tool}</span>
        {argsStr && <span className="agent__tool-params">{argsStr}</span>}
        <button className="agent__tool-toggle" onClick={() => setOpen(!open)} aria-label="Sonucu göster">
          <ChevronDown size={13} className={open ? 'agent__chevron--open' : ''} />
        </button>
      </div>
      {open && (
        <pre className="agent__tool-json">
          {JSON.stringify(call.result, null, 2).slice(0, 600)}
          {JSON.stringify(call.result).length > 600 ? '\n…' : ''}
        </pre>
      )}
    </div>
  )
}

/* ── Main component ─────────────────────────────────────────────── */
export default function AgentChat() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [currentQuery, setCurrentQuery] = useState('')

  const reset = () => { setResult(null); setError(null); setMessage('') }

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
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() }
  }

  return (
    <div className="agent">

      {/* Header */}
      <div className="agent__header">
        <h1 className="agent__title">MCP AI Ajan</h1>
        <p className="agent__subtitle">
          Kullanıcı&nbsp;→&nbsp;<span className="agent__subtitle-hl">LLM (MCP Host)</span>&nbsp;→&nbsp;MCP Server&nbsp;→&nbsp;Yanıt
        </p>
      </div>

      {/* Input */}
      <div className="agent__input-wrap">
        <textarea
          className="agent__textarea input"
          placeholder="Bir şey sor — 'ASELSAN hakkında bilgi ver', 'Python stajı ara'..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          disabled={loading}
        />
        <div className="agent__input-footer">
          <div className="agent__hint">Enter ile gönder · Shift+Enter yeni satır</div>
          <button
            className="btn btn-primary agent__send"
            onClick={() => handleSubmit()}
            disabled={loading || !message.trim()}
          >
            {loading
              ? <><Loader2 size={14} className="agent__spin" /> Çalışıyor</>
              : <><Send size={14} /> Gönder</>
            }
          </button>
        </div>
      </div>

      {/* Example chips */}
      {!result && !loading && !error && (
        <div className="agent__examples">
          <span className="agent__examples-label">Dene</span>
          <div className="agent__chips">
            {EXAMPLE_QUERIES.map((q) => (
              <button key={q} className="agent__chip" onClick={() => handleSubmit(q)}>{q}</button>
            ))}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <motion.div className="agent__loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Loader2 size={16} className="agent__spin" />
          <span>LLM MCP araçlarını keşfediyor&hellip;</span>
          <span className="agent__loading-query">&ldquo;{currentQuery}&rdquo;</span>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <motion.div className="agent__error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          {error}
        </motion.div>
      )}

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            className="agent__result"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            {/* User query bubble */}
            <div className="agent__user-row">
              <div className="agent__user-bubble">{currentQuery}</div>
            </div>

            {/* Tool trace */}
            {result.tool_calls?.length > 0 && (
              <div className="agent__trace">
                <div className="agent__trace-header">
                  <span className="agent__trace-label">MCP araç çağrıları</span>
                  <span className="agent__trace-count">{result.tool_calls.length} araç</span>
                </div>
                <div className="agent__trace-body">
                  {result.tool_calls.map((call, i) => (
                    <ToolRow key={i} call={call} index={i} />
                  ))}
                </div>
              </div>
            )}

            {/* Agent answer */}
            <div className="agent__answer">
              <div className="agent__answer-header">
                <Bot size={14} />
                <span>Ajan yanıtı</span>
              </div>
              <div className="agent__answer-body">
                <MarkdownContent text={result.answer} />
              </div>
            </div>

            <button className="agent__reset" onClick={reset}>
              ← Yeni soru sor
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
