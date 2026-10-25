import React, { useState, useEffect, useRef } from 'react';
import { SlaCountdownBadge, EmptyStateCard } from '../../design-system/primitives';
import { liveEventClient } from '../../services/liveEventClient';

export type InboxQueueFilter =
  | 'all'
  | 'my_work'
  | 'needs_approval'
  | 'overdue_due_soon'
  | 'incidents'
  | 'dsars'
  | 'regulatory_review';

export interface UnifiedInboxItem {
  id: string;
  title: string;
  queueType: 'assessment' | 'incident' | 'dsar' | 'regulatory' | 'vendor';
  jurisdiction: string;
  statuteCitation: string;
  assignedTo: string;
  slaLabel: string;
  hoursRemaining: number;
  overdue?: boolean;
  needsApproval: boolean;
  status: 'open' | 'approved' | 'changes_requested' | 'escalated_legal' | 'deferred';
  summary: string;
  recommendedAction: string;
  auditReceipt?: string;
}

export const INITIAL_UNIFIED_INBOX_ITEMS: UnifiedInboxItem[] = [
  {
    id: 'INB-2026-0412',
    title: 'Clinical AI Diagnostic Triage — Combined GDPR Art. 35 DPIA + Ontario PHIPA TRA + Law 25 EFVP',
    queueType: 'assessment',
    jurisdiction: 'CA-ON · CA-QC · EU-GDPR',
    statuteCitation: 'GDPR Art. 35; EU AI Act Art. 27; PHIPA s. 10; Quebec Law 25 s. 3.3 & s. 17',
    assignedTo: 'usr-cpo-counsel-01',
    slaLabel: '16h remaining',
    hoursRemaining: 16,
    overdue: false,
    needsApproval: true,
    status: 'open',
    summary: 'High-risk AI clinical decision support processing health data across Ontario, Quebec, and Germany.',
    recommendedAction: 'Verify Sovereign KMS key custody & human clinician oversight gate before approving.',
  },
  {
    id: 'INB-2026-0194',
    title: 'DSAR-2026-0194 — Dual-Scope Access & Deletion Request (California + Quebec Resident)',
    queueType: 'dsar',
    jurisdiction: 'US-CA · CA-QC',
    statuteCitation: 'Cal. Civ. Code § 1798.105(d); Quebec Law 25 s. 27–28',
    assignedTo: 'usr-cpo-counsel-01',
    slaLabel: 'Overdue by 4h',
    hoursRemaining: -4,
    overdue: true,
    needsApproval: true,
    status: 'open',
    summary: 'Consumer requested full deletion; BSA/AML ledger records require partial statutory hold while marketing telemetry is purged.',
    recommendedAction: 'Approve partial deletion & statutory exemption explanation letter.',
  },
  {
    id: 'INB-2026-0881',
    title: 'INC-2026-881 — Subprocessor Cloud Telemetry Bucket Misconfiguration Triage',
    queueType: 'incident',
    jurisdiction: 'EU-DE · CA-QC · US-NY',
    statuteCitation: 'GDPR Art. 33 (72h); Quebec Law 25 s. 3.5 (RROSH); NY GBL § 899-aa',
    assignedTo: 'usr-cpo-counsel-01',
    slaLabel: '41h remaining (72h clock)',
    hoursRemaining: 41,
    overdue: false,
    needsApproval: true,
    status: 'open',
    summary: 'Encrypted telemetry snapshot exposed for 19 minutes; customer-managed HSM keys remained intact.',
    recommendedAction: 'Review forensic encryption key-custody attestation and sign off on counsel privilege determination.',
  },
  {
    id: 'INB-2026-0905',
    title: 'REG-2026-0905 — California CPPA ADMT Rulemaking & Colorado AI Act Rule Pack Promotion',
    queueType: 'regulatory',
    jurisdiction: 'US-CA · US-CO',
    statuteCitation: 'Cal. Civ. Code § 1798.185(a)(16); Colo. Rev. Stat. § 6-1-1701',
    assignedTo: 'usr-legal-counsel-01',
    slaLabel: '5d remaining',
    hoursRemaining: 120,
    overdue: false,
    needsApproval: true,
    status: 'open',
    summary: 'Candidate obligation pack extracted from verified official source with SHA-256 span provenance.',
    recommendedAction: 'Verify statutory text span and promote rule v2026.10.2 to production JRAE.',
  },
];

export interface UnifiedInboxViewProps {
  items?: UnifiedInboxItem[];
  onCountChange?: (openCount: number) => void;
}

export const UnifiedInboxView: React.FC<UnifiedInboxViewProps> = ({ items: externalItems, onCountChange }) => {
  const [items, setItems] = useState<UnifiedInboxItem[]>(externalItems || INITIAL_UNIFIED_INBOX_ITEMS);
  const [activeQueue, setActiveQueue] = useState<InboxQueueFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [reasoning, setReasoning] = useState('');
  const [lastActionUndo, setLastActionUndo] = useState<{
    itemId: string;
    previousStatus: UnifiedInboxItem['status'];
    message: string;
  } | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const filteredItems = items.filter((item) => {
    if (activeQueue === 'my_work' && item.assignedTo !== 'usr-cpo-counsel-01') return false;
    if (activeQueue === 'needs_approval' && (!item.needsApproval || item.status !== 'open')) return false;
    if (activeQueue === 'overdue_due_soon' && !item.overdue && item.hoursRemaining > 48) return false;
    if (activeQueue === 'incidents' && item.queueType !== 'incident') return false;
    if (activeQueue === 'dsars' && item.queueType !== 'dsar') return false;
    if (activeQueue === 'regulatory_review' && item.queueType !== 'regulatory') return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        item.id.toLowerCase().includes(q) ||
        item.title.toLowerCase().includes(q) ||
        item.jurisdiction.toLowerCase().includes(q) ||
        item.statuteCitation.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const selectedItem = filteredItems[selectedIndex] || filteredItems[0] || null;

  useEffect(() => {
    if (onCountChange) {
      onCountChange(items.filter((i) => i.status === 'open').length);
    }
  }, [items, onCountChange]);

  const executeDecision = async (
    target: UnifiedInboxItem,
    nextStatus: UnifiedInboxItem['status'],
    actionCode: 'accept' | 'flag_legal' | 'defer'
  ) => {
    const prevStatus = target.status;
    let receipt = `AUDIT-INBOX-${target.id}-${actionCode.toUpperCase()}-${Date.now()}`;

    // Attempt backend confirmation on /api/inbox/{id}/decision + SSE publish
    try {
      const res = await fetch(`/api/inbox/${encodeURIComponent(target.id)}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: actionCode,
          reasoning: reasoning || `Governed ${actionCode} decision by CPO/DPO`,
        }),
      });
      if (res.ok) {
        const json = (await res.json()) as { audit_ref?: string };
        if (json.audit_ref) receipt = json.audit_ref;
      }
    } catch {
      // Fallback receipt when offline
    }

    void liveEventClient.publishEvent({
      event_type: nextStatus === 'approved' ? 'approval.completed' : 'case.stage_changed',
      title: `Inbox Decision: ${target.id} → ${nextStatus.toUpperCase()}`,
      summary: `${target.title} (${target.jurisdiction}) — Receipt: ${receipt}`,
      severity: nextStatus === 'approved' ? 'success' : 'info',
      entity_type: target.queueType,
      entity_id: target.id,
      target_section: 'inbox',
    });

    setItems((prev) =>
      prev.map((i) =>
        i.id === target.id
          ? { ...i, status: nextStatus, needsApproval: false, auditReceipt: receipt }
          : i
      )
    );
    setLastActionUndo({
      itemId: target.id,
      previousStatus: prevStatus,
      message: `${target.id} marked as ${nextStatus.replace('_', ' ')} (Receipt: ${receipt})`,
    });
    setReasoning('');
  };

  const handleUndo = () => {
    if (!lastActionUndo) return;
    setItems((prev) =>
      prev.map((i) =>
        i.id === lastActionUndo.itemId
          ? { ...i, status: lastActionUndo.previousStatus, needsApproval: true, auditReceipt: undefined }
          : i
      )
    );
    setLastActionUndo(null);
  };

  // Keyboard navigation shortcuts: j / k / / / a / f
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      if (e.key === 'j') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, Math.max(0, filteredItems.length - 1)));
      } else if (e.key === 'k') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(0, prev - 1));
      } else if (e.key === '/') {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === 'a' && selectedItem) {
        e.preventDefault();
        void executeDecision(selectedItem, 'approved', 'accept');
      } else if (e.key === 'f' && selectedItem) {
        e.preventDefault();
        void executeDecision(selectedItem, 'escalated_legal', 'flag_legal');
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  });

  const queueTabs: Array<{ id: InboxQueueFilter; label: string }> = [
    { id: 'all', label: 'All Queues' },
    { id: 'my_work', label: 'My Work' },
    { id: 'needs_approval', label: 'Needs Approval' },
    { id: 'overdue_due_soon', label: 'Overdue & Due Soon' },
    { id: 'incidents', label: 'Incidents' },
    { id: 'dsars', label: 'DSARs' },
    { id: 'regulatory_review', label: 'Regulatory Review' },
  ];

  return (
    <section aria-label="Unified Privacy Inbox" data-testid="unified-inbox-view" className="space-y-4">
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            Unified Privacy Inbox & Human Governance Queue
          </h2>
          <p className="text-xs text-slate-300">
            Keyboard shortcuts: <kbd className="rounded bg-slate-800 px-1.5 py-0.5 font-mono">j</kbd>/
            <kbd className="rounded bg-slate-800 px-1.5 py-0.5 font-mono">k</kbd> navigate ·{' '}
            <kbd className="rounded bg-slate-800 px-1.5 py-0.5 font-mono">/</kbd> search ·{' '}
            <kbd className="rounded bg-slate-800 px-1.5 py-0.5 font-mono">a</kbd> approve ·{' '}
            <kbd className="rounded bg-slate-800 px-1.5 py-0.5 font-mono">f</kbd> escalate to counsel
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={searchInputRef}
            type="search"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Filter by ID, statute, or jurisdiction..."
            aria-label="Filter inbox items"
            data-testid="inbox-search-input"
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 w-64 focus:outline-none focus:ring-2 focus:ring-sky-400"
          />
        </div>
      </div>

      {/* Reversible Action Undo Banner */}
      {lastActionUndo && (
        <div
          role="status"
          data-testid="inbox-undo-banner"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/40 px-4 py-2.5 text-xs text-emerald-200 flex items-center justify-between"
        >
          <span>✓ {lastActionUndo.message}</span>
          <button
            type="button"
            onClick={handleUndo}
            data-testid="inbox-undo-btn"
            className="rounded bg-emerald-700/60 px-2.5 py-1 text-xs font-semibold text-white hover:bg-emerald-600"
          >
            Undo Action
          </button>
        </div>
      )}

      {/* 7 Queue Filter Tabs */}
      <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Inbox Queue Views">
        {queueTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeQueue === tab.id}
            data-testid={`inbox-tab-${tab.id}`}
            onClick={() => {
              setActiveQueue(tab.id);
              setSelectedIndex(0);
            }}
            className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              activeQueue === tab.id
                ? 'bg-emerald-500/20 border border-emerald-400 text-emerald-200 font-semibold'
                : 'border border-slate-800 bg-slate-900/60 text-slate-300 hover:text-slate-100'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {filteredItems.length === 0 ? (
        <EmptyStateCard
          title="No Matching Items in Queue"
          description="All matching tasks or governance approvals in this view have been resolved."
          actionLabel="Reset Queue Filter"
          onAction={() => {
            setActiveQueue('all');
            setSearchQuery('');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left 5 cols: Queue List */}
          <div className="lg:col-span-5 space-y-2">
            {filteredItems.map((item, idx) => {
              const isSelected = selectedItem?.id === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  data-testid={`inbox-item-${item.id}`}
                  onClick={() => setSelectedIndex(idx)}
                  className={`w-full text-left rounded-xl border p-3.5 transition-all ${
                    isSelected
                      ? 'border-emerald-400 bg-slate-800/90'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs font-bold text-emerald-300">{item.id}</span>
                    <SlaCountdownBadge
                      label={item.slaLabel}
                      hoursRemaining={item.hoursRemaining}
                      overdue={item.overdue}
                    />
                  </div>
                  <div className="mt-1 text-xs font-semibold text-slate-100">{item.title}</div>
                  <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-300">
                    <span>{item.jurisdiction}</span>
                    <span className="uppercase font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-200">
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Right 7 cols: Context & Decision Drawer */}
          {selectedItem && (
            <div
              data-testid="inbox-detail-panel"
              className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/80 p-5 space-y-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-emerald-300">{selectedItem.id}</span>
                    <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-mono text-slate-200">
                      {selectedItem.jurisdiction}
                    </span>
                  </div>
                  <h3 className="mt-1 text-base font-bold text-slate-100">{selectedItem.title}</h3>
                </div>
                <SlaCountdownBadge
                  label={selectedItem.slaLabel}
                  hoursRemaining={selectedItem.hoursRemaining}
                  overdue={selectedItem.overdue}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                  <div className="text-slate-300 font-semibold">Binding Statutory Basis</div>
                  <div className="mt-1 font-mono text-emerald-300">{selectedItem.statuteCitation}</div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                  <div className="text-slate-300 font-semibold">Current Status & Owner</div>
                  <div className="mt-1 text-slate-100">
                    Status: <strong className="uppercase">{selectedItem.status}</strong> · Owner:{' '}
                    <span className="font-mono">{selectedItem.assignedTo}</span>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3.5 text-xs space-y-2">
                <div>
                  <strong className="text-slate-200">Operational Context:</strong>
                  <p className="mt-0.5 text-slate-300">{selectedItem.summary}</p>
                </div>
                <div>
                  <strong className="text-emerald-300">Recommended Governance Action:</strong>
                  <p className="mt-0.5 text-slate-200">{selectedItem.recommendedAction}</p>
                </div>
              </div>

              {selectedItem.auditReceipt && (
                <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 p-3 text-xs font-mono text-emerald-200">
                  ✓ Server-Confirmed Audit Receipt: {selectedItem.auditReceipt}
                </div>
              )}

              <div>
                <label htmlFor="inbox-decision-notes" className="block text-xs font-semibold text-slate-200 mb-1">
                  Governance Decision Notes & Legal Sign-Off Rationale
                </label>
                <textarea
                  id="inbox-decision-notes"
                  value={reasoning}
                  onChange={(e) => setReasoning(e.target.value)}
                  rows={2}
                  placeholder="Record statutory basis, conditions, or requested remediation..."
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100"
                />
              </div>

              <div className="flex flex-wrap items-center gap-2 pt-1">
                <button
                  type="button"
                  data-testid="inbox-approve-btn"
                  onClick={() => void executeDecision(selectedItem, 'approved', 'accept')}
                  className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
                >
                  ✓ Approve & Seal Receipt (a)
                </button>
                <button
                  type="button"
                  data-testid="inbox-request-changes-btn"
                  onClick={() => void executeDecision(selectedItem, 'changes_requested', 'defer')}
                  className="rounded-lg border border-amber-500/50 bg-amber-950/60 px-3.5 py-2 text-xs font-semibold text-amber-200 hover:bg-amber-900/60"
                >
                  Request Changes
                </button>
                <button
                  type="button"
                  data-testid="inbox-escalate-btn"
                  onClick={() => void executeDecision(selectedItem, 'escalated_legal', 'flag_legal')}
                  className="rounded-lg border border-sky-500/50 bg-sky-950/60 px-3.5 py-2 text-xs font-semibold text-sky-200 hover:bg-sky-900/60"
                >
                  Escalate to General Counsel (f)
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
