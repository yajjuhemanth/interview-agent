import React from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

const api = {
  agent: async (job_title: string, job_description: string) => {
    const r = await fetch('/agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_title, job_description })
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data?.error || `Request failed (${r.status})`)
    return data
  },
  history: async () => {
    const r = await fetch('/get?limit=50')
    const data = await r.json()
    if (!r.ok) throw new Error(`Failed to load history (${r.status})`)
    return data as Array<any>
  }
}

type LevelKey = 'basic' | 'intermediate' | 'expert'

function QACard({ qa, level }: { qa: any, level: LevelKey }) {
  const pairs: Array<{question: string, answer: string}> = Array.isArray(qa?.[level]) ? qa[level] : []
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-3">Q&A</h2>
      {pairs.length ? (
        <ul className="space-y-2 list-none pl-0">
          {pairs.map((p, idx) => (
            <li key={idx} className="qa-item">
              <details>
                <summary><strong>Q{idx + 1}.</strong> {p.question}</summary>
                <div className="answer muted small">{p.answer || 'No answer (AI unavailable?).'}</div>
              </details>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No questions returned.</p>
      )}
    </div>
  )
}

function History({ level }: { level: LevelKey }) {
  const [items, setItems] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(false)
  const load = async () => {
    setLoading(true)
    try { setItems(await api.history()) } finally { setLoading(false) }
  }
  React.useEffect(() => { load() }, [])
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">History</h2>
        <button className="btn btn-ghost" onClick={load} disabled={loading}>{loading ? 'Loading…' : 'Reload'}</button>
      </div>
      {!items.length ? (
        <p className="muted">No records yet.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((rec) => (
            <li key={rec.id}>
              <details>
                <summary className="cursor-pointer">
                  <strong>#{rec.id}</strong> • {rec.job_title} • {rec.created_at}
                </summary>
                <div className="muted small mt-1">{rec.job_description}</div>
                <div className="mt-2">
                  <QACard qa={rec.qa} level={level} />
                </div>
              </details>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function App() {
  const [jobTitle, setJobTitle] = React.useState('')
  const [jobDesc, setJobDesc] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string|null>(null)
  const [result, setResult] = React.useState<any|null>(null)
  const [showHistory, setShowHistory] = React.useState(false)
  const [level, setLevel] = React.useState<LevelKey>('basic')

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!jobTitle.trim() || !jobDesc.trim()) {
      setError('Please fill in both Job Title and Job Description.')
      return
    }
    setLoading(true)
    try {
      const data = await api.agent(jobTitle.trim(), jobDesc.trim())
      setResult(data)
    } catch (err: any) {
      setError(err.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <section className="hero mb-5">
        <h1>Interview Agent</h1>
        <p className="small">Generate role-specific interview Q&A. Click a question to reveal its answer.</p>
      </section>

      <form onSubmit={onSubmit} className="card space-y-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">Job Title</label>
            <input className="input" value={jobTitle} onChange={e => setJobTitle(e.target.value)} placeholder="Frontend Developer" />
          </div>
          <div>
            <label className="label">Job Description</label>
            <textarea className="input" rows={3} value={jobDesc} onChange={e => setJobDesc(e.target.value)} placeholder="ReactJS, JS, testing" />
          </div>
        </div>
        <div>
          <label className="label">Difficulty</label>
          <div className="flex gap-2">
            {(['basic','intermediate','expert'] as LevelKey[]).map(l => (
              <button
                key={l}
                type="button"
                className={`btn ${level===l? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => setLevel(l)}
              >{l.charAt(0).toUpperCase()+l.slice(1)}</button>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn btn-primary" type="submit" disabled={loading}>{loading ? 'Generating…' : 'Generate & Save'}</button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => setShowHistory(prev => !prev)}
          >
            {showHistory ? 'Hide History' : 'View History'}
          </button>
        </div>
        {error && <div className="text-red-600 font-semibold">{error}</div>}
      </form>

      {result && (
        <section className="mb-4">
          <QACard qa={result.qa} level={level} />
        </section>
      )}

      {showHistory && (
        <section id="history">
          <History level={level} />
        </section>
      )}
    </div>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
