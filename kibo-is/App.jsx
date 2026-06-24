import React, { useState, useEffect, useRef } from 'react'
import { 
  FileText, Shield, AlertTriangle, Clock, Ban, Check, Undo2, 
  ChevronDown, ChevronUp, Terminal, ShieldAlert, UserCheck, Search 
} from 'lucide-react'

// Mock initial data if backend API is not yet active or unreachable
const INITIAL_TRANSACTIONS = [
  {
    id: "thread-101",
    type: "DSAR",
    client: "TechCorp Inc.",
    jurisdiction: "US",
    priority: "critical",
    deadline: "48 hours",
    description: "Verify identity and process CCPA deletion request.",
    agent: "US DSAR Rights Agent",
    summary: "User authenticated. 3 systems matched. No legal hold.",
    raw: '{"systems": ["crm", "billing"], "confidence": 0.99}'
  },
  {
    id: "thread-102",
    type: "Vendor",
    client: "CloudScale Inc.",
    jurisdiction: "EU",
    priority: "high",
    deadline: "12 hours",
    description: "Evaluate vendor GDPR DPA adequacy for analytics integration.",
    agent: "EU Data Transfer Auditor",
    summary: "Standard contractual clauses present. Sub-processors listed.",
    raw: '{"risk_level": "medium", "data_location": "Frankfurt"}'
  },
  {
    id: "thread-103",
    type: "Breach",
    client: "HealthFirst Corp",
    jurisdiction: "Canada",
    priority: "critical",
    deadline: "24 hours",
    description: "Perform HIPAA compliance review on misconfigured S3 bucket.",
    agent: "Canada PHIPA Security Agent",
    summary: "Exposed files: 120 health charts. Exposure time: 14 hours.",
    raw: '{"affected_records": 120, "pii_exposed": true}'
  }
]

export const App = () => {
  const [transactions, setTransactions] = useState(INITIAL_TRANSACTIONS)
  const [history, setHistory] = useState([])
  const [selectedId, setSelectedId] = useState("thread-101")
  const [activeTab, setActiveTab] = useState('summary') // 'summary' | 'raw'
  const [reasoning, setReasoning] = useState('')
  const [toast, setToast] = useState(null) // { timerId, tx, action, originalIndex }
  const [undoCountdown, setUndoCountdown] = useState(5)
  const [showHistory, setShowHistory] = useState(false)
  const [rules, setRules] = useState([])
  const countdownIntervalRef = useRef(null)

  // API base URL configuration
  const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') 
    ? "http://127.0.0.1:8000/api" 
    : "/api"

  // Sync state with API backend on mount
  useEffect(() => {
    fetchTransactions()
    fetchRules()
  }, [])

  const fetchTransactions = async () => {
    try {
      const res = await fetch(`${API_BASE}/transactions`)
      if (res.ok) {
        const data = await res.json()
        const pending = data.filter(t => t.status === 'pending')
        if (pending.length > 0) {
          setTransactions(pending)
          setSelectedId(pending[0].id)
        } else {
          setTransactions([])
        }
        // Save completed to history
        const resolved = data.filter(t => t.status !== 'pending')
        setHistory(resolved)
      }
    } catch (e) {
      console.warn("FastAPI backend offline; running in mock browser state.")
    }
  }

  const fetchRules = async () => {
    try {
      const res = await fetch(`${API_BASE}/rules`)
      if (res.ok) {
        const data = await res.json()
        setRules(data)
      }
    } catch (e) {
      console.warn("Could not load rules from backend.")
    }
  }

  const selectedTx = transactions.find(t => t.id === selectedId) || transactions[0]

  // Keyboard Navigation & Actions
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore key events if user is typing in the reasoning text area
      if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') {
        return
      }

      if (e.key === 'j') {
        // Go Down
        const idx = transactions.findIndex(t => t.id === selectedId)
        if (idx < transactions.length - 1) {
          setSelectedId(transactions[idx + 1].id)
        }
      } else if (e.key === 'k') {
        // Go Up
        const idx = transactions.findIndex(t => t.id === selectedId)
        if (idx > 0) {
          setSelectedId(transactions[idx - 1].id)
        }
      } else if (e.key === '1') {
        triggerAction('approve_now')
      } else if (e.key === '2') {
        triggerAction('approve_always')
      } else if (e.key === '3') {
        triggerAction('flag_legal')
      } else if (e.key === '4') {
        triggerAction('review_later')
      } else if (e.key === '5') {
        triggerAction('reject')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedId, transactions])

  // Countdown timer for Undo
  useEffect(() => {
    if (toast) {
      setUndoCountdown(5)
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)
      countdownIntervalRef.current = setInterval(() => {
        setUndoCountdown(prev => {
          if (prev <= 1) {
            clearInterval(countdownIntervalRef.current)
            commitActionBackend(toast.tx, toast.action, toast.reasoning)
            setToast(null)
            return 5
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)
    }
  }, [toast])

  const triggerAction = (action) => {
    if (!selectedTx) return

    // Save previous state for Undo
    const originalIndex = transactions.findIndex(t => t.id === selectedTx.id)
    
    // Remove immediately from active stream UI
    const updated = transactions.filter(t => t.id !== selectedTx.id)
    setTransactions(updated)
    
    // Auto-select next item
    if (updated.length > 0) {
      setSelectedId(updated[Math.min(originalIndex, updated.length - 1)].id)
    } else {
      setSelectedId(null)
    }

    // Set Undo Toast state
    setToast({
      tx: selectedTx,
      action,
      reasoning,
      originalIndex
    })

    // Reset reasoning box
    setReasoning('')
  }

  const handleUndo = () => {
    if (!toast) return
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current)

    // Reinsert transaction back to list
    const restored = [...transactions]
    restored.splice(toast.originalIndex, 0, toast.tx)
    setTransactions(restored)
    setSelectedId(toast.tx.id)
    setReasoning(toast.reasoning)
    setToast(null)
  }

  const commitActionBackend = async (tx, action, actionReasoning) => {
    // Add to local history list immediately
    const actionLabelMap = {
      approve_now: "APPROVED",
      approve_always: "AUTO-APPROVED RULE",
      flag_legal: "FLAGGED LEGAL",
      review_later: "DEFERRED",
      reject: "REJECTED RULE"
    }

    const historyItem = {
      ...tx,
      status: actionLabelMap[action],
      human_decision: actionLabelMap[action],
      human_reasoning: actionReasoning || "No reasoning specified."
    }
    
    setHistory(prev => [historyItem, ...prev])

    // Push to FastAPI backend
    try {
      const res = await fetch(`${API_BASE}/transactions/${tx.id}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, reasoning: actionReasoning || "Dashboard signed-off." })
      })
      if (res.ok) {
        fetchTransactions()
        fetchRules()
      }
    } catch (e) {
      console.warn("Backend offline; transaction finalized locally.", historyItem)
    }
  }

  const getPriorityColor = (p) => {
    if (p === 'critical') return 'border-l-4 border-l-red-600'
    if (p === 'high') return 'border-l-4 border-l-amber-500'
    return 'border-l-4 border-l-slate-400'
  }

  const getTxIcon = (type) => {
    if (type === 'DSAR') return <UserCheck size={14} className="text-emerald-600" />
    if (type === 'Breach') return <ShieldAlert size={14} className="text-rose-600" />
    return <Shield size={14} className="text-blue-600" />
  }

  return (
    <div className="min-h-screen bg-[#F5F2EB] text-[#111111] flex flex-col font-mono text-xs select-none">
      {/* Top Header */}
      <header className="border-b border-[#D1CDBF] bg-white py-4 px-6 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-3.5 h-3.5 bg-[#B87B31]" />
          <h1 className="text-base font-bold uppercase tracking-widest">KIBO.IS // PRIVACY OVERLORD</h1>
        </div>
        <div className="flex items-center space-x-6">
          <div className="text-[10px] text-[#706E64] uppercase font-bold">
            Role: Chief Privacy Officer (CPO)
          </div>
          <div className="bg-[#B87B31] text-white px-2 py-0.5 font-bold uppercase text-[9px] border border-[#B87B31]">
            Active Session
          </div>
        </div>
      </header>

      {/* Main Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Live Transaction Stream */}
        <aside className="w-1/3 border-r border-[#D1CDBF] flex flex-col justify-between bg-[#EDE9DF]/40">
          <div className="p-4 border-b border-[#D1CDBF] flex justify-between items-center bg-white">
            <span className="font-bold uppercase tracking-wider text-[10px] text-[#706E64]">Live Operations Queue ({transactions.length})</span>
            <span className="text-[9px] bg-black text-[#F5F2EB] px-1.5 py-0.5 font-bold">HITL BOUNDARY</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-[#D1CDBF]">
            {transactions.map((tx) => {
              const isSelected = tx.id === selectedId
              return (
                <div
                  key={tx.id}
                  onClick={() => setSelectedId(tx.id)}
                  className={`p-4 cursor-pointer transition-all hover:bg-white flex flex-col gap-2 ${getPriorityColor(tx.priority)} ${
                    isSelected ? 'bg-white shadow-[inset_3px_0_0_0_#B87B31]' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-center space-x-2">
                      {getTxIcon(tx.type)}
                      <span className="font-bold uppercase text-[10px] tracking-tight">{tx.type}</span>
                    </div>
                    <span className="text-[8px] bg-black text-white px-1 font-bold uppercase">{tx.jurisdiction}</span>
                  </div>

                  <p className="text-[11px] leading-snug font-bold">{tx.description}</p>

                  <div className="flex justify-between text-[9px] text-[#706E64] font-bold">
                    <span>{tx.client}</span>
                    <span className="text-red-700 uppercase">{tx.deadline}</span>
                  </div>
                </div>
              )
            })}

            {transactions.length === 0 && (
              <div className="p-8 text-center text-[#706E64] italic">
                All privacy agent actions authorized. Operations on track.
              </div>
            )}
          </div>
        </aside>

        {/* Right Pane: Decision Panel */}
        <main className="w-2/3 flex flex-col bg-white">
          {selectedTx ? (
            <div className="flex-1 flex flex-col justify-between">
              {/* Decision Panel Header */}
              <div className="p-6 border-b border-[#D1CDBF] flex justify-between items-start bg-[#F5F2EB]/30">
                <div className="space-y-1.5">
                  <div className="text-[9px] text-[#706E64] uppercase font-bold tracking-wider">
                    Client: {selectedTx.client} · Jurisdiction: {selectedTx.jurisdiction}
                  </div>
                  <h2 className="text-lg font-extrabold uppercase tracking-tight">
                    {selectedTx.description}
                  </h2>
                </div>
                <div className="text-right font-bold text-[9px] text-[#B87B31] border border-[#B87B31] px-2.5 py-1">
                  Routed to: {selectedTx.agent}
                </div>
              </div>

              {/* Tabbed Info View */}
              <div className="flex-1 flex flex-col overflow-hidden">
                <div className="flex border-b border-[#D1CDBF] bg-white">
                  <button
                    onClick={() => setActiveTab('summary')}
                    className={`px-6 py-2.5 font-bold uppercase text-[10px] tracking-wider border-r border-[#D1CDBF] ${
                      activeTab === 'summary' ? 'bg-[#F5F2EB]' : 'bg-transparent text-[#706E64]'
                    }`}
                  >
                    AI Summary
                  </button>
                  <button
                    onClick={() => setActiveTab('raw')}
                    className={`px-6 py-2.5 font-bold uppercase text-[10px] tracking-wider border-r border-[#D1CDBF] ${
                      activeTab === 'raw' ? 'bg-[#F5F2EB]' : 'bg-transparent text-[#706E64]'
                    }`}
                  >
                    Raw Context (JSON)
                  </button>
                </div>

                <div className="flex-1 p-6 overflow-y-auto bg-[#F5F2EB]/10">
                  {activeTab === 'summary' ? (
                    <div className="space-y-4">
                      <div className="text-[10px] text-[#B87B31] uppercase tracking-wider font-extrabold flex items-center gap-1.5">
                        <Terminal size={12} />
                        <span>Swarm Audit Synthesis</span>
                      </div>
                      <p className="text-xs leading-relaxed text-[#111111] font-bold bg-white border border-[#D1CDBF] p-4">
                        {selectedTx.summary}
                      </p>
                      <div className="text-[9px] text-[#706E64] space-y-1">
                        <div>· Checkpoints parsed: 3 (Data Redaction, SCC Check, Consent Check)</div>
                        <div>· LangGraph Execution Thread: {selectedTx.id}</div>
                      </div>
                    </div>
                  ) : (
                    <pre className="p-4 border border-[#D1CDBF] bg-white text-[10px] overflow-x-auto leading-relaxed">
                      {JSON.stringify(JSON.parse(selectedTx.raw), null, 2)}
                    </pre>
                  )}
                </div>
              </div>

              {/* Reasoning & Actions Block */}
              <div className="p-6 border-t border-[#D1CDBF] bg-[#EDE9DF]/20 space-y-4">
                <div>
                  <label className="block text-[9px] text-[#706E64] uppercase font-bold mb-1.5">
                    Audit Logging Reason (Optional for auto-learning)
                  </label>
                  <textarea
                    value={reasoning}
                    onChange={(e) => setReasoning(e.target.value)}
                    placeholder="Provide justification rules or compliance citations for this decision..."
                    className="w-full h-16 bg-white border border-[#D1CDBF] p-3 text-xs focus:outline-none focus:border-[#B87B31] font-mono"
                  />
                </div>

                {/* 5 Semantic Action Buttons */}
                <div className="grid grid-cols-5 gap-2">
                  <button
                    onClick={() => triggerAction('approve_now')}
                    className="bg-[#16a34a] hover:bg-green-700 text-white font-bold uppercase tracking-wider py-3 flex flex-col items-center justify-center gap-1"
                    title="Approve immediately. Shortcut: 1"
                  >
                    <Check size={14} />
                    <span>Approve [1]</span>
                  </button>

                  <button
                    onClick={() => triggerAction('approve_always')}
                    className="bg-[#2563eb] hover:bg-blue-700 text-white font-bold uppercase tracking-wider py-3 flex flex-col items-center justify-center gap-1"
                    title="Approve matching future cases autonomously. Shortcut: 2"
                  >
                    <Shield size={14} />
                    <span>Always [2]</span>
                  </button>

                  <button
                    onClick={() => triggerAction('flag_legal')}
                    className="bg-[#9333ea] hover:bg-purple-700 text-white font-bold uppercase tracking-wider py-3 flex flex-col items-center justify-center gap-1"
                    title="Escalate review to outside legal. Shortcut: 3"
                  >
                    <AlertTriangle size={14} />
                    <span>Flag [3]</span>
                  </button>

                  <button
                    onClick={() => triggerAction('review_later')}
                    className="bg-[#475569] hover:bg-slate-700 text-white font-bold uppercase tracking-wider py-3 flex flex-col items-center justify-center gap-1"
                    title="Defer action and keep in queue. Shortcut: 4"
                  >
                    <Clock size={14} />
                    <span>Later [4]</span>
                  </button>

                  <button
                    onClick={() => triggerAction('reject')}
                    className="bg-[#dc2626] hover:bg-red-700 text-white font-bold uppercase tracking-wider py-3 flex flex-col items-center justify-center gap-1"
                    title="Reject and block current execution. Shortcut: 5"
                  >
                    <Ban size={14} />
                    <span>Reject [5]</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-3 bg-[#F5F2EB]/20">
              <Shield size={32} className="text-[#D1CDBF]" />
              <div className="text-[10px] text-[#706E64] uppercase font-bold tracking-wider">
                Select a transaction to inspect and authorize.
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Bottom Expandable Decision History Drawer */}
      <footer className="border-t border-[#D1CDBF] bg-white">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="w-full flex justify-between items-center py-2.5 px-6 font-bold uppercase text-[9px] tracking-widest text-[#706E64] hover:bg-[#F5F2EB]/30 transition-colors"
        >
          <span>Operations Audit Changelog ({history.length} resolved)</span>
          {showHistory ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </button>

        {showHistory && (
          <div className="max-h-48 overflow-y-auto border-t border-[#D1CDBF] p-4 bg-[#F5F2EB]/10 divide-y divide-[#D1CDBF]">
            {history.map((h, idx) => (
              <div key={idx} className="py-2.5 flex justify-between items-start text-[10px]">
                <div className="space-y-1">
                  <div className="font-bold flex items-center gap-2">
                    <span className="text-[#B87B31]">{h.id}</span>
                    <span>·</span>
                    <span className="uppercase">{h.client}</span>
                    <span>·</span>
                    <span className="text-[#706E64]">{h.description}</span>
                  </div>
                  <div className="text-[#706E64] italic">
                    Reasoning logged: "{h.human_reasoning}"
                  </div>
                </div>
                <div className="font-extrabold border px-2 py-0.5 border-[#D1CDBF] text-[9px] uppercase">
                  {h.status}
                </div>
              </div>
            ))}
            {history.length === 0 && (
              <div className="text-center italic py-4 text-[#706E64]">
                No actions recorded in active session.
              </div>
            )}
          </div>
        )}
      </footer>

      {/* Undo Grace period floating Toast */}
      {toast && (
        <div className="fixed bottom-12 left-1/2 -translate-x-1/2 bg-black text-white px-6 py-3 shadow-lg flex items-center space-x-6 z-50 border border-white">
          <div className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 bg-[#B87B31] animate-ping" />
            <span className="font-bold uppercase tracking-wider text-[10px]">
              Decision logged. Dispatching in {undoCountdown}s
            </span>
          </div>
          <button
            onClick={handleUndo}
            className="flex items-center space-x-1 border border-white/40 px-2 py-1 text-[9px] font-extrabold uppercase hover:bg-white hover:text-black transition-colors"
          >
            <Undo2 size={10} />
            <span>Undo</span>
          </button>
        </div>
      )}
    </div>
  )
}
export default App
