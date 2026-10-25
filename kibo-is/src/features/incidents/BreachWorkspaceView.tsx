import React, { useState } from 'react';
import { StageStepper, SlaCountdownBadge } from '../../design-system/primitives';
import {
  PrivacyOsService,
  type BreachIncidentInput,
  type BreachWarRoomResponse,
} from '../../services/privacyOsService';
import { liveEventClient } from '../../services/liveEventClient';

export const BREACH_RESPONSE_PHASES: string[] = [
  '1. Detection & Intake',
  '2. Containment & Forensics',
  '3. Multi-Regime Harm & Deadline Triage',
  '4. Counsel Notification Approval Gate',
  '5. Regulator & Individual Dispatch',
];

export interface BreachWorkspaceViewProps {
  initialWarRoom?: BreachWarRoomResponse | null;
  onStatusChange?: (live: boolean) => void;
}

export const BreachWorkspaceView: React.FC<BreachWorkspaceViewProps> = ({
  initialWarRoom,
  onStatusChange,
}) => {
  const [phaseIndex, setPhaseIndex] = useState<number>(2);
  const [owner, setOwner] = useState('usr-cpo-counsel-01 (Elena Vance, CIPP/E)');
  const [incidentForm, setIncidentForm] = useState<BreachIncidentInput>({
    title: 'Multi-Region Clinical & Financial Cloud Subprocessor Telemetry Exposure',
    discovery_timestamp: '2026-10-25T08:15:00Z',
    jurisdictions: ['US-FED', 'US-CA', 'US-NY', 'CA-FED', 'CA-QC', 'CA-ON', 'EU-GDPR', 'EU-DE'],
    affected_counts_by_jurisdiction: {
      'US-CA': 1420,
      'US-NY': 610,
      'CA-QC': 890,
      'CA-ON': 540,
      'EU-DE': 950,
    },
    data_categories: ['health_phi', 'financial_account', 'government_id', 'contact_identifiers'],
    involves_phi: true,
    involves_financial: true,
    is_critical_infrastructure: true,
    risk_of_harm_level: 'rrosh',
    encryption_or_safe_harbor_intact: false,
    description:
      'Unauthorized API token replay against regional staging telemetry mirror containing unmasked clinical & billing identifiers across US, Canadian, and German establishments.',
  });

  const [warRoom, setWarRoom] = useState<BreachWarRoomResponse | null>(initialWarRoom || null);
  const [evaluating, setEvaluating] = useState(false);
  const [evidenceLog, setEvidenceLog] = useState<
    Array<{ id: string; timestamp: string; actor: string; note: string }>
  >([
    {
      id: 'EV-INC-01',
      timestamp: '2026-10-25T08:19:00Z',
      actor: 'sec-soc-lead-01',
      note: 'Revoked compromised subprocessor OAuth service principal and isolated staging mirror.',
    },
    {
      id: 'EV-INC-02',
      timestamp: '2026-10-25T08:42:00Z',
      actor: 'usr-legal-counsel-01',
      note: 'Placed forensic investigation under external privacy counsel privilege hold.',
    },
  ]);
  const [newEvidenceNote, setNewEvidenceNote] = useState('');
  const [approvalStatusByRegime, setApprovalStatusByRegime] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);

  const handleRunTriage = async () => {
    setEvaluating(true);
    try {
      const res = await PrivacyOsService.evaluateIncidentWarRoom(incidentForm);
      setWarRoom(res.warRoom);
      if (onStatusChange) onStatusChange(res.live);
      setPhaseIndex(2);
      setBanner(
        `Evaluated incident ${res.warRoom.incident_id}: Strictest regulator clock = ${
          res.warRoom.strictest_regulator_deadline_hours ?? 72
        }h.`
      );
      void liveEventClient.publishEvent({
        event_type: 'incident.deadline_updated',
        title: `Breach Triage Updated: ${res.warRoom.incident_id}`,
        summary: `Strictest regulator deadline: ${
          res.warRoom.strictest_regulator_deadline_hours ?? 72
        }h across ${incidentForm.jurisdictions.join(', ')}`,
        severity: 'critical',
        entity_type: 'incident',
        entity_id: res.warRoom.incident_id,
        target_section: 'incidents',
        requires_human_review: true,
      });
    } finally {
      setEvaluating(false);
    }
  };

  const handleApproveRegimeNotice = (jurisdictionId: string, regimeLabel: string) => {
    setApprovalStatusByRegime((prev) => ({
      ...prev,
      [jurisdictionId]: 'counsel_approved',
    }));
    setPhaseIndex(3);
    setBanner(`Human Privacy Counsel approved regulator notification package for ${jurisdictionId} (${regimeLabel}).`);
    void liveEventClient.publishEvent({
      event_type: 'approval.completed',
      title: `Counsel Approved Breach Notice: ${jurisdictionId}`,
      summary: `${regimeLabel} notification package signed off by ${owner}.`,
      severity: 'success',
      entity_type: 'incident',
      entity_id: warRoom?.incident_id || 'INC-2026-WARROOM',
      target_section: 'incidents',
    });
  };

  const handleAddEvidence = () => {
    if (!newEvidenceNote.trim()) return;
    setEvidenceLog((prev) => [
      {
        id: `EV-INC-0${prev.length + 1}`,
        timestamp: new Date().toISOString(),
        actor: owner,
        note: newEvidenceNote.trim(),
      },
      ...prev,
    ]);
    setNewEvidenceNote('');
  };

  return (
    <section aria-label="Breach & Incident Response Workspace" data-testid="breach-workspace-view" className="space-y-5">
      {/* Incident Command Header */}
      <div className="rounded-xl border border-rose-500/40 bg-slate-900/90 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-rose-950 border border-rose-500/50 px-2 py-0.5 font-mono text-xs font-bold text-rose-200">
              SEVERITY: {incidentForm.risk_of_harm_level.toUpperCase()}
            </span>
            <SlaCountdownBadge
              label={`Strictest Regulator Clock: ${warRoom?.strictest_regulator_deadline_hours ?? 72}h (GDPR Art. 33 / Law 25 RROSH)`}
              hoursRemaining={warRoom?.strictest_regulator_deadline_hours ?? 72}
            />
            <span className="text-xs font-mono text-slate-300">Incident Commander: {owner}</span>
          </div>
          <h2 className="mt-1.5 text-base font-bold text-slate-100">{incidentForm.title}</h2>
          <p className="text-xs text-slate-300">
            Explicitly invokes JRAE & Breach War Room Engine only on user action — zero unsolicited background mutations.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            data-testid="breach-run-triage-btn"
            onClick={() => void handleRunTriage()}
            disabled={evaluating}
            className="rounded-lg bg-rose-600 px-4 py-2 text-xs font-semibold text-white hover:bg-rose-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            {evaluating ? 'Calculating Deadlines...' : '⚡ Calculate Multi-Regime Deadlines'}
          </button>
        </div>
      </div>

      {banner && (
        <div
          role="status"
          data-testid="breach-status-banner"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-2.5 text-xs text-emerald-200"
        >
          ✓ {banner}
        </div>
      )}

      {/* 5-Phase Incident Stepper */}
      <StageStepper
        stages={BREACH_RESPONSE_PHASES}
        currentIndex={phaseIndex}
        onSelectStage={(idx) => setPhaseIndex(idx)}
      />

      {/* Incident Fact Parameters & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-slate-100">Incident Parameters & Harm Standard</h3>
          <div>
            <label htmlFor="breach-title-input" className="block font-semibold text-slate-200 mb-1">
              Incident Title
            </label>
            <input
              id="breach-title-input"
              type="text"
              value={incidentForm.title}
              onChange={(e) => setIncidentForm({ ...incidentForm, title: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="breach-owner-input" className="block font-semibold text-slate-200 mb-1">
              Incident Commander / Lead Counsel
            </label>
            <input
              id="breach-owner-input"
              type="text"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="breach-harm-select" className="block font-semibold text-slate-200 mb-1">
              Assessed Harm Threshold (RROSH / GDPR Art. 33)
            </label>
            <select
              id="breach-harm-select"
              value={incidentForm.risk_of_harm_level}
              onChange={(e) =>
                setIncidentForm({
                  ...incidentForm,
                  risk_of_harm_level: e.target.value as BreachIncidentInput['risk_of_harm_level'],
                })
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
            >
              <option value="rrosh">Real Risk of Significant Harm (RROSH — PIPEDA / Law 25 / High GDPR Risk)</option>
              <option value="high">High Risk to Rights & Freedoms (GDPR Art. 34 Individual Notice)</option>
              <option value="moderate">Moderate Risk (Regulator Filing Required)</option>
              <option value="low">Low Risk (Internal Breach Registry Only)</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-slate-200">
            <input
              type="checkbox"
              checked={incidentForm.encryption_or_safe_harbor_intact}
              onChange={(e) =>
                setIncidentForm({
                  ...incidentForm,
                  encryption_or_safe_harbor_intact: e.target.checked,
                })
              }
            />
            <span>FIPS 140-3 Encryption Safe Harbor Intact (Keys Uncompromised)</span>
          </label>
        </div>

        {/* Chronological Evidence & Containment Log */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-slate-100">
            Chronological Containment & Forensic Evidence Log
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              value={newEvidenceNote}
              onChange={(e) => setNewEvidenceNote(e.target.value)}
              placeholder="Log forensic containment action, key rotation, or counsel privilege note..."
              aria-label="New forensic containment log entry"
              data-testid="breach-evidence-input"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
            />
            <button
              type="button"
              data-testid="breach-add-evidence-btn"
              onClick={handleAddEvidence}
              className="rounded-lg bg-slate-800 border border-slate-600 px-3 py-1.5 font-semibold text-slate-100 hover:border-emerald-400"
            >
              + Append Log
            </button>
          </div>
          <ul className="space-y-2 max-h-48 overflow-y-auto" data-testid="breach-evidence-list">
            {evidenceLog.map((entry) => (
              <li
                key={entry.id}
                className="rounded-lg border border-slate-800 bg-slate-950/70 p-2.5 flex items-start justify-between gap-3"
              >
                <div>
                  <span className="font-mono font-bold text-emerald-300">{entry.id}</span> ·{' '}
                  <span className="text-slate-100">{entry.note}</span>
                </div>
                <span className="font-mono text-[11px] text-slate-300 whitespace-nowrap">
                  {entry.actor}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Jurisdiction-Specific Notification Deadlines & Human Counsel Approval Routing */}
      {warRoom && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 space-y-4" data-testid="breach-regime-matrix">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Jurisdiction-Specific Notification Deadlines & Mandatory Counsel Gate ({warRoom.incident_id})
              </h3>
              <p className="text-xs text-slate-300">
                No external regulator or affected individual notification can be dispatched without explicit human Privacy Counsel approval.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {warRoom.regime_evaluations.map((reg) => {
              const effectiveStatus = approvalStatusByRegime[reg.jurisdiction_id] || reg.approval_status;
              return (
                <div
                  key={`${reg.jurisdiction_id}-${reg.regulation_id}`}
                  className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-emerald-300">
                      {reg.jurisdiction_id} · {reg.regime_label}
                    </span>
                    <span
                      className={`rounded px-2 py-0.5 font-mono text-[10px] uppercase ${
                        effectiveStatus === 'counsel_approved'
                          ? 'bg-emerald-950 text-emerald-200 border border-emerald-500/40'
                          : 'bg-amber-950 text-amber-200 border border-amber-500/40'
                      }`}
                    >
                      {effectiveStatus}
                    </span>
                  </div>
                  <div className="text-slate-200">
                    <strong>Supervisory Authority:</strong> {reg.regulator_authority}
                  </div>
                  <div className="text-rose-200 font-mono">
                    <strong>Regulator Deadline:</strong> {reg.regulator_deadline_text}
                  </div>
                  <div className="text-slate-300">
                    <strong>Individual Notice:</strong> {reg.individual_notification_text}
                  </div>
                  <div className="pt-2 flex items-center justify-between">
                    <span className="text-[11px] text-slate-300">
                      Retention: {reg.record_retention_requirement}
                    </span>
                    <button
                      type="button"
                      data-testid={`breach-approve-regime-${reg.jurisdiction_id}`}
                      onClick={() => handleApproveRegimeNotice(reg.jurisdiction_id, reg.regime_label)}
                      className="rounded-lg bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-500"
                    >
                      {effectiveStatus === 'counsel_approved'
                        ? '✓ Approved for Dispatch'
                        : 'Approve Regulator Notice'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
};
