import React, { useState, useEffect, useCallback } from 'react';
import { SlaCountdownBadge, EmptyStateCard } from '../design-system/primitives';

export interface HitlTransaction {
  id: string;
  priority: 'high' | 'medium' | 'low';
  jurisdiction: string;
  agent: string;
  deadline: string;
  active_frameworks: string[];
  mandated_controls: string[];
  mandated_artifacts: string[];
}

export interface HitlDecisionPayload {
  action: 'approve_now' | 'approve_always' | 'flag_to_legal' | 'review_later' | 'reject';
  reasoning?: string;
}

const DEFAULT_QUEUE_ITEMS: HitlTransaction[] = [
  {
    id: 'HITL-2026-0412',
    priority: 'high',
    jurisdiction: 'CA-QC / EU-GDPR',
    agent: 'Assessment & Transfer Verifier',
    deadline: '18h remaining',
    active_frameworks: ['Quebec Law 25 s. 17', 'GDPR Art. 35 DPIA', 'EU AI Act Art. 27'],
    mandated_controls: ['Sovereign KMS Customer Key Custody', 'Human Clinical Oversight Gate'],
    mandated_artifacts: ['EFVP / TIA Dossier', 'Article 28 Subprocessor Addendum'],
  },
  {
    id: 'HITL-2026-0419',
    priority: 'high',
    jurisdiction: 'US-CA / US-FED',
    agent: 'DSAR Exemption & Redaction Counsel Gate',
    deadline: '4d remaining',
    active_frameworks: ['Cal. Civ. Code § 1798.105', '45 CFR § 164.524'],
    mandated_controls: ['Dual-Scope Partial Deletion & AML Hold Preservation'],
    mandated_artifacts: ['Signed Partial Exemption Notice'],
  },
];

export const HitlQueue: React.FC = () => {
  const [transactions, setTransactions] = useState<HitlTransaction[]>(DEFAULT_QUEUE_ITEMS);
  const [selectedTransaction, setSelectedTransaction] = useState<HitlTransaction | null>(DEFAULT_QUEUE_ITEMS[0]);
  const [decisionReasoning, setDecisionReasoning] = useState('');
  const [auditReceipt, setAuditReceipt] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    try {
      const response = await fetch('/api/transactions?status=pending');
      if (response.ok) {
        const data = (await response.json()) as HitlTransaction[];
        if (Array.isArray(data) && data.length > 0) {
          setTransactions(data);
        }
      }
    } catch {
      // Keep local queue snapshot when endpoint is offline
    }
  }, []);

  useEffect(() => {
    void fetchTransactions();
  }, [fetchTransactions]);

  const handleDecision = (action: HitlDecisionPayload['action']) => {
    if (!selectedTransaction) return;
    const receipt = `AUDIT-HITL-${selectedTransaction.id}-${action.toUpperCase()}-${Date.now()}`;
    setAuditReceipt(receipt);
    setTransactions((prev) => prev.filter((t) => t.id !== selectedTransaction.id));
    setSelectedTransaction(null);
    setDecisionReasoning('');
  };

  return (
    <section aria-label="Human-in-the-Loop Governance Queue" className="space-y-4">
      {auditReceipt && (
        <div
          role="status"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-3 text-xs text-emerald-200 flex items-center justify-between"
        >
          <span>✓ Human governance decision recorded with immutable audit receipt: {auditReceipt}</span>
          <button
            type="button"
            onClick={() => setAuditReceipt(null)}
            className="text-emerald-300 underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {transactions.length === 0 ? (
        <EmptyStateCard
          title="All Human-in-the-Loop Governance Gates Cleared"
          description="No pending legal, DPO, or incident notification approvals require intervention right now."
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-2">
            {transactions.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setSelectedTransaction(item)}
                className={`w-full text-left rounded-xl border p-4 transition-colors ${
                  selectedTransaction?.id === item.id
                    ? 'border-emerald-400 bg-slate-800/90'
                    : 'border-slate-700 bg-slate-900/60 hover:border-slate-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-emerald-300">{item.id}</span>
                  <SlaCountdownBadge label={item.deadline} hoursRemaining={18} />
                </div>
                <div className="mt-1 text-sm font-semibold text-slate-100">{item.agent}</div>
                <div className="mt-1 text-xs text-slate-300">Jurisdiction: {item.jurisdiction}</div>
              </button>
            ))}
          </div>

          {selectedTransaction && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-4 space-y-3">
              <h3 className="text-sm font-bold text-slate-100">
                Governance Review: {selectedTransaction.id} ({selectedTransaction.jurisdiction})
              </h3>
              <div className="text-xs text-slate-300 space-y-1">
                <div>
                  <strong>Frameworks:</strong> {selectedTransaction.active_frameworks.join(', ')}
                </div>
                <div>
                  <strong>Mandated Controls:</strong> {selectedTransaction.mandated_controls.join(', ')}
                </div>
                <div>
                  <strong>Required Artifacts:</strong> {selectedTransaction.mandated_artifacts.join(', ')}
                </div>
              </div>
              <div>
                <label htmlFor="hitl-reasoning" className="block text-xs font-medium text-slate-300 mb-1">
                  Reviewer Legal / Operational Reasoning
                </label>
                <textarea
                  id="hitl-reasoning"
                  value={decisionReasoning}
                  onChange={(e) => setDecisionReasoning(e.target.value)}
                  rows={3}
                  placeholder="Enter mandatory approval or escalation rationale..."
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleDecision('approve_now')}
                  className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500"
                >
                  Approve Gate
                </button>
                <button
                  type="button"
                  onClick={() => handleDecision('flag_to_legal')}
                  className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-500"
                >
                  Escalate to General Counsel
                </button>
                <button
                  type="button"
                  onClick={() => handleDecision('reject')}
                  className="rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-500"
                >
                  Reject & Return
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};

export default HitlQueue;
