import React from 'react';
import { MetricSummaryCard, SlaCountdownBadge, OperationalStatusBadge } from '../../design-system/primitives';
import type { OperationalDataStatus, WorkspaceRole } from '../../services/privacyOsService';
import type { LiveEventEnvelope } from '../../services/liveEventClient';
import type { SupportedLocale } from '../../i18n/translations';
import { TRANSLATIONS } from '../../i18n/translations';

export interface PriorityWorkItem {
  id: string;
  title: string;
  category: 'Assessment' | 'Incident' | 'DSAR' | 'Regulatory' | 'Vendor';
  jurisdiction: string;
  owner: string;
  deadlineLabel: string;
  hoursRemaining?: number;
  overdue?: boolean;
  requiresApproval: boolean;
  targetSection: 'inbox' | 'assessments' | 'incidents' | 'rights' | 'regulatory' | 'data_vendors';
}

export interface ExecutiveHomeViewProps {
  role: WorkspaceRole;
  locale: SupportedLocale;
  operationalStatus: OperationalDataStatus;
  priorityItems: PriorityWorkItem[];
  liveEvents: LiveEventEnvelope[];
  onNavigateSection: (
    section: 'inbox' | 'assessments' | 'incidents' | 'rights' | 'regulatory' | 'data_vendors' | 'reports' | 'assistant'
  ) => void;
  onQuickApproveItem?: (id: string) => void;
}

export const ExecutiveHomeView: React.FC<ExecutiveHomeViewProps> = ({
  role,
  locale,
  operationalStatus,
  priorityItems,
  liveEvents,
  onNavigateSection,
  onQuickApproveItem,
}) => {
  const t = TRANSLATIONS[locale];

  const overdueCount = priorityItems.filter((i) => i.overdue).length;
  const approvalCount = priorityItems.filter((i) => i.requiresApproval).length;
  const incidentCount = priorityItems.filter((i) => i.category === 'Incident').length;
  const regChangesCount = 4;

  const roleHeadlineMap: Record<WorkspaceRole, { headline: string; subhead: string }> = {
    CPO: {
      headline: 'Chief Privacy Officer Executive Command Center',
      subhead: 'Answer what is overdue, what needs executive sign-off, and where statutory risk is rising in under 30 seconds.',
    },
    DPO: {
      headline: 'Data Protection Officer (GDPR / Law 25 / PHIPA) Triage Desk',
      subhead: 'Prioritized DPIA/EFVP sign-offs, DSAR SLA clocks, cross-border TIAs, and supervisory authority readiness.',
    },
    LEGAL: {
      headline: 'Privacy Counsel & Statutory Provenance Review Desk',
      subhead: 'Human-gated regulatory promotions, breach notification legal privilege gates, and citation verification.',
    },
    ANALYST: {
      headline: 'Privacy Operations Analyst Queue',
      subhead: 'Assigned RoPA records, DSAR evidence packets, vendor DPA reviews, and draft impact assessments.',
    },
    SECURITY: {
      headline: 'Security & Breach Response Operations Center',
      subhead: 'Active multi-regime containment clocks (72h GDPR / RROSH Law 25 / 30d HIPAA) and forensic evidence logs.',
    },
    MANAGER: {
      headline: 'Business & Product Owner Privacy Portal',
      subhead: 'Guided project privacy intake, vendor onboarding status, and plain-language control requirements.',
    },
    EMPLOYEE: {
      headline: 'Employee Privacy Self-Service & Incident Intake',
      subhead: 'Ask governed privacy questions, report a suspected data incident, or start a guided project check.',
    },
    AUDITOR: {
      headline: 'Compliance Auditor & Evidence Verification Console',
      subhead: 'Read-only inspection of SHA-256 sealed audit chains, control effectiveness, and statutory mappings.',
    },
    ADMIN: {
      headline: 'Enterprise System & Connector Administration',
      subhead: 'Manage authorized tenant memberships, RBAC matrices, M365/Claude/Gemini connectors, and SSE health.',
    },
  };

  const roleBanner = roleHeadlineMap[role] || roleHeadlineMap.CPO;

  return (
    <div className="space-y-6" data-testid="executive-home-view">
      {/* Role-Specific Context Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded bg-emerald-500/20 border border-emerald-400/40 px-2 py-0.5 text-xs font-mono font-bold text-emerald-300">
              {role} VIEW
            </span>
            <h2 className="text-lg font-bold text-slate-100">{roleBanner.headline}</h2>
          </div>
          <p className="mt-1 text-xs text-slate-300">{roleBanner.subhead}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onNavigateSection('assessments')}
            data-testid="home-cta-start-assessment"
            className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            + Start Guided Assessment
          </button>
          <button
            type="button"
            onClick={() => onNavigateSection('incidents')}
            data-testid="home-cta-open-war-room"
            className="rounded-lg border border-rose-500/50 bg-rose-950/60 px-3.5 py-2 text-xs font-semibold text-rose-200 hover:bg-rose-900/60 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            ⚡ Triage Breach Incident
          </button>
          <button
            type="button"
            onClick={() => onNavigateSection('assistant')}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-200 hover:border-sky-400"
          >
            Ask Governed Assistant
          </button>
        </div>
      </div>

      {/* 4 Executive Summary Drill-Down Cards (UX-01: <30s Triage) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricSummaryCard
          testId="metric-card-overdue"
          title={t.metrics.overdue}
          value={overdueCount}
          subtitle="Click to open overdue SLA items in Unified Inbox"
          tone={overdueCount > 0 ? 'critical' : 'success'}
          icon="⚠"
          onClick={() => onNavigateSection('inbox')}
        />
        <MetricSummaryCard
          testId="metric-card-approvals"
          title={t.metrics.needApproval}
          value={approvalCount}
          subtitle="Human legal / DPO sign-off gates awaiting action"
          tone={approvalCount > 0 ? 'warning' : 'success'}
          icon="⚑"
          onClick={() => onNavigateSection('inbox')}
        />
        <MetricSummaryCard
          testId="metric-card-incidents"
          title={t.metrics.openIncidents}
          value={incidentCount}
          subtitle="Active multi-jurisdiction breach response timelines"
          tone={incidentCount > 0 ? 'critical' : 'info'}
          icon="⚡"
          onClick={() => onNavigateSection('incidents')}
        />
        <MetricSummaryCard
          testId="metric-card-reg-changes"
          title={t.metrics.regulatoryChanges}
          value={regChangesCount}
          subtitle="Verified statutory & enforcement updates (US / CA / EU)"
          tone="info"
          icon="⚖"
          onClick={() => onNavigateSection('regulatory')}
        />
      </div>

      {/* Main Two-Column Executive Grid: Priority Work + Recent Regulatory & Live Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: My Priority Work Table */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-100">Priority Action Queue & Approaching Deadlines</h3>
              <p className="text-xs text-slate-300">
                Sorted by statutory deadline urgency (GDPR 72h, Quebec Law 25 RROSH, CPRA/GDPR DSAR windows)
              </p>
            </div>
            <button
              type="button"
              onClick={() => onNavigateSection('inbox')}
              className="text-xs font-semibold text-emerald-300 hover:underline"
            >
              Open Full Inbox ({priorityItems.length}) →
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-300">
                  <th className="py-2 pr-3 font-semibold">Case / Item</th>
                  <th className="py-2 px-3 font-semibold">Jurisdiction</th>
                  <th className="py-2 px-3 font-semibold">SLA Clock</th>
                  <th className="py-2 pl-3 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70">
                {priorityItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/40">
                    <td className="py-3 pr-3">
                      <div className="font-mono text-[11px] text-emerald-300">{item.id}</div>
                      <div className="font-semibold text-slate-100">{item.title}</div>
                      <div className="text-[11px] text-slate-300">
                        {item.category} · Owner: {item.owner}
                      </div>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-200">{item.jurisdiction}</td>
                    <td className="py-3 px-3">
                      <SlaCountdownBadge
                        label={item.deadlineLabel}
                        hoursRemaining={item.hoursRemaining}
                        overdue={item.overdue}
                      />
                    </td>
                    <td className="py-3 pl-3 text-right space-x-2 whitespace-nowrap">
                      {item.requiresApproval && onQuickApproveItem && (
                        <button
                          type="button"
                          data-testid={`home-quick-approve-${item.id}`}
                          onClick={() => onQuickApproveItem(item.id)}
                          className="rounded bg-emerald-600 px-2.5 py-1 text-xs font-semibold text-white hover:bg-emerald-500"
                        >
                          Approve
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => onNavigateSection(item.targetSection)}
                        className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs text-slate-200 hover:border-sky-400"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: Recent Verified Regulatory Changes + Live SSE Stream Preview */}
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-100">Verified Regulatory Changes</h3>
              <button
                type="button"
                onClick={() => onNavigateSection('regulatory')}
                className="text-xs text-sky-300 hover:underline"
              >
                View All →
              </button>
            </div>
            <ul className="space-y-2.5 text-xs">
              <li className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-emerald-300">CA-QC · Law 25 s. 17</span>
                  <span className="rounded bg-emerald-950 px-1.5 py-0.5 text-[10px] text-emerald-300 border border-emerald-500/30">
                    ✓ Verified
                  </span>
                </div>
                <p className="mt-1 text-slate-200 font-medium">
                  CAI Cross-Border EFVP / TIA Equivalency & Encryption Key Custody Guidance
                </p>
                <p className="mt-0.5 text-[11px] text-slate-300">
                  Impacts 2 active cloud subprocessor transfers · Source: legisquebec.gouv.qc.ca
                </p>
              </li>
              <li className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-sky-300">EU-GDPR / EU-AI-ACT</span>
                  <span className="rounded bg-emerald-950 px-1.5 py-0.5 text-[10px] text-emerald-300 border border-emerald-500/30">
                    ✓ Verified
                  </span>
                </div>
                <p className="mt-1 text-slate-200 font-medium">
                  Regulation (EU) 2024/1689 Art. 27 Fundamental Rights Impact Assessment (FRIA)
                </p>
                <p className="mt-0.5 text-[11px] text-slate-300">
                  Impacts Clinical AI Triage DPIA-2026-0412 · Source: eur-lex.europa.eu
                </p>
              </li>
            </ul>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-100">Live Event Stream (SSE)</h3>
              <OperationalStatusBadge status={operationalStatus} compact />
            </div>
            <ul className="space-y-2 text-xs" data-testid="home-live-events-list">
              {liveEvents.slice(0, 4).map((ev) => (
                <li
                  key={ev.event_id}
                  className="rounded-lg border border-slate-800/90 bg-slate-950/60 p-2.5"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-300">
                    <span className="text-emerald-300">{ev.event_type}</span>
                    <span>#{ev.sequence_id}</span>
                  </div>
                  <div className="mt-0.5 font-semibold text-slate-100">{ev.title}</div>
                  <div className="mt-0.5 text-[11px] text-slate-300">{ev.summary}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
