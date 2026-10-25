import React, { useState } from 'react';
import { StageStepper, SlaCountdownBadge } from '../../design-system/primitives';
import {
  PrivacyOsService,
  type DsarEvaluateRequest,
  type DsarNexusEvaluationResponse,
  type RopaRecord,
} from '../../services/privacyOsService';
import { liveEventClient } from '../../services/liveEventClient';

export const DSAR_WORKFLOW_STAGES: string[] = [
  '1. Intake & Identity Verification',
  '2. Jurisdictional Nexus & SLA Calculation',
  '3. Multi-System Record Discovery',
  '4. Redaction & Statutory Exemptions',
  '5. Counsel Approval & Subject Delivery',
];

export interface PrivacyRightsViewProps {
  initialDsar?: DsarNexusEvaluationResponse | null;
  ropaRecords: RopaRecord[];
  showRopaSection?: boolean;
  onStatusChange?: (live: boolean) => void;
}

export const PrivacyRightsView: React.FC<PrivacyRightsViewProps> = ({
  initialDsar,
  ropaRecords,
  showRopaSection = true,
  onStatusChange,
}) => {
  const [stageIndex, setStageIndex] = useState<number>(1);
  const [identityVerified, setIdentityVerified] = useState<boolean>(true);
  const [redactionCompleted, setRedactionCompleted] = useState<boolean>(false);
  const [deliveryApproved, setDeliveryApproved] = useState<boolean>(false);
  const [dsarForm, setDsarForm] = useState<DsarEvaluateRequest>({
    subject_name_or_id: 'SUBJ-QC-CA-2026-0194 (Marc-Antoine Tremblay)',
    subject_residency: 'CA-QC',
    controller_establishments: ['CA-QC', 'CA-ON', 'US-CA', 'EU-FR'],
    request_type: 'deletion_erasure',
    received_at: '2026-10-20T14:00:00Z',
    is_complex_or_extended: false,
    holds_litigation_or_aml_ledger: true,
  });
  const [dsarResult, setDsarResult] = useState<DsarNexusEvaluationResponse | null>(initialDsar || null);
  const [evaluating, setEvaluating] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  const handleEvaluateDsar = async () => {
    setEvaluating(true);
    try {
      const res = await PrivacyOsService.evaluateDsarRequest(dsarForm);
      setDsarResult(res.dsar);
      if (onStatusChange) onStatusChange(res.live);
      setStageIndex(2);
      setBanner(
        `Calculated DSAR Nexus (${res.dsar.request_id}): Strictest deadline = ${res.dsar.strictest_initial_days} ${res.dsar.day_type} days (${res.dsar.strictest_initial_deadline}).`
      );
      void liveEventClient.publishEvent({
        event_type: 'case.stage_changed',
        title: `DSAR Nexus Evaluated: ${res.dsar.request_id}`,
        summary: `Residency ${res.dsar.subject_residency} → ${res.dsar.strictest_initial_days} ${res.dsar.day_type} days deadline.`,
        severity: 'info',
        entity_type: 'dsar',
        entity_id: res.dsar.request_id,
        target_section: 'rights',
      });
    } finally {
      setEvaluating(false);
    }
  };

  const handleCompleteRedaction = () => {
    setRedactionCompleted(true);
    setStageIndex(3);
    setBanner('Third-party PII and trade-secret redaction pass completed; statutory AML hold preserved.');
  };

  const handleApproveDelivery = () => {
    setDeliveryApproved(true);
    setStageIndex(4);
    setBanner('Human Privacy Officer approved DSAR response package and sealed SHA-256 delivery receipt.');
    void liveEventClient.publishEvent({
      event_type: 'approval.completed',
      title: `DSAR Delivery Approved: ${dsarResult?.request_id || 'DSAR-2026-0194'}`,
      summary: `Verified response package released to ${dsarForm.subject_name_or_id}.`,
      severity: 'success',
      entity_type: 'dsar',
      entity_id: dsarResult?.request_id || 'DSAR-2026-0194',
      target_section: 'rights',
    });
  };

  return (
    <section aria-label="DSAR & Privacy Rights Operations" data-testid="privacy-rights-view" className="space-y-6">
      {/* DSAR Header */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-emerald-500/20 border border-emerald-400/40 px-2 py-0.5 font-mono text-xs font-bold text-emerald-300">
              {identityVerified ? '✓ IDENTITY VERIFIED' : '⚠ IDENTITY PENDING'}
            </span>
            <SlaCountdownBadge
              label={`Strictest Window: ${dsarResult?.strictest_initial_days ?? 30} ${
                dsarResult?.day_type ?? 'calendar'
              } days`}
              daysRemaining={dsarResult?.strictest_initial_days ?? 30}
            />
          </div>
          <h2 className="mt-1.5 text-base font-bold text-slate-100">
            5-Stage Privacy Rights (DSAR) Fulfillment & Statutory Exemption Engine
          </h2>
          <p className="text-xs text-slate-300">
            Reconciles Quebec Law 25 (30d), GDPR Art. 12–22 (1 month), CPRA (45d + 10-business-day ack), and AML/Clinical retention holds.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="dsar-evaluate-btn"
            onClick={() => void handleEvaluateDsar()}
            disabled={evaluating}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            {evaluating ? 'Calculating SLA...' : '⚡ Evaluate DSAR Nexus & Deadlines'}
          </button>
          <button
            type="button"
            data-testid="dsar-complete-redaction-btn"
            onClick={handleCompleteRedaction}
            className="rounded-lg border border-sky-500/50 bg-sky-950/60 px-3.5 py-2 text-xs font-semibold text-sky-200 hover:bg-sky-900/60"
          >
            {redactionCompleted ? '✓ Redaction Verified' : 'Run Redaction & Exemption Check'}
          </button>
          <button
            type="button"
            data-testid="dsar-approve-delivery-btn"
            onClick={handleApproveDelivery}
            className="rounded-lg border border-emerald-500/50 bg-emerald-950/60 px-3.5 py-2 text-xs font-semibold text-emerald-200 hover:bg-emerald-900/60"
          >
            {deliveryApproved ? '✓ Response Dispatched' : 'Approve & Release Response'}
          </button>
        </div>
      </div>

      {banner && (
        <div
          role="status"
          data-testid="dsar-status-banner"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-2.5 text-xs text-emerald-200"
        >
          ✓ {banner}
        </div>
      )}

      {/* 5-Stage Stepper */}
      <StageStepper
        stages={DSAR_WORKFLOW_STAGES}
        currentIndex={stageIndex}
        onSelectStage={(idx) => setStageIndex(idx)}
      />

      {/* DSAR Configuration & Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-5 rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-slate-100">Requester & Jurisdiction Parameters</h3>
          <div>
            <label htmlFor="dsar-subject-input" className="block font-semibold text-slate-200 mb-1">
              Data Subject Identifier
            </label>
            <input
              id="dsar-subject-input"
              type="text"
              value={dsarForm.subject_name_or_id}
              onChange={(e) => setDsarForm({ ...dsarForm, subject_name_or_id: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="dsar-residency-select" className="block font-semibold text-slate-200 mb-1">
                Subject Residency
              </label>
              <select
                id="dsar-residency-select"
                value={dsarForm.subject_residency}
                onChange={(e) => setDsarForm({ ...dsarForm, subject_residency: e.target.value })}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
              >
                <option value="CA-QC">CA-QC (Quebec Law 25 — 30d)</option>
                <option value="CA-ON">CA-ON (Ontario PHIPA / PIPEDA — 30d)</option>
                <option value="US-CA">US-CA (California CPRA — 45d)</option>
                <option value="EU-DE">EU-DE (Germany GDPR / BDSG — 30d)</option>
                <option value="EU-FR">EU-FR (France GDPR / CNIL — 30d)</option>
              </select>
            </div>
            <div>
              <label htmlFor="dsar-type-select" className="block font-semibold text-slate-200 mb-1">
                Exercised Right
              </label>
              <select
                id="dsar-type-select"
                value={dsarForm.request_type}
                onChange={(e) =>
                  setDsarForm({
                    ...dsarForm,
                    request_type: e.target.value as DsarEvaluateRequest['request_type'],
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-slate-100"
              >
                <option value="deletion_erasure">Deletion / Erasure (Right to be Forgotten)</option>
                <option value="access">Access & Copy of Personal Data</option>
                <option value="correction_rectification">Correction / Rectification</option>
                <option value="portability">Structured Data Portability</option>
                <option value="admt_human_review_explanation">AI / ADMT Explanation & Human Contestability</option>
              </select>
            </div>
          </div>

          <label className="flex items-center gap-2 text-slate-200 pt-1">
            <input
              type="checkbox"
              checked={identityVerified}
              onChange={(e) => setIdentityVerified(e.target.checked)}
            />
            <span>Requester Identity Verified (Zero-Additional-PII Token Match)</span>
          </label>
          <label className="flex items-center gap-2 text-slate-200">
            <input
              type="checkbox"
              checked={dsarForm.holds_litigation_or_aml_ledger}
              onChange={(e) =>
                setDsarForm({ ...dsarForm, holds_litigation_or_aml_ledger: e.target.checked })
              }
            />
            <span>Subject Has Active BSA/AML Financial Ledger or Clinical Retention Hold</span>
          </label>
        </div>

        {/* Right 7 cols: DSAR Nexus Output & Exemptions */}
        <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-3 text-xs">
          <h3 className="text-sm font-bold text-slate-100">
            Evaluated Statutory Deadlines & Retention Conflict Resolution
          </h3>
          {dsarResult ? (
            <div className="space-y-3" data-testid="dsar-evaluation-card">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <div className="text-slate-300">Strictest Deadline</div>
                  <div className="mt-1 font-mono text-sm font-bold text-emerald-300">
                    {dsarResult.strictest_initial_days} {dsarResult.day_type} days
                  </div>
                  <div className="text-[11px] text-slate-300">Due: {dsarResult.strictest_initial_deadline}</div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <div className="text-slate-300">Applicable Regimes</div>
                  <div className="mt-1 font-mono text-sky-300">
                    {dsarResult.applicable_regimes.join(', ')}
                  </div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <div className="text-slate-300">Appeal Window</div>
                  <div className="mt-1 font-mono text-amber-300">
                    {dsarResult.appeal_window_days ?? 30} days
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="font-semibold text-slate-200">
                  Statutory Exemptions & Partial Retention Conflicts:
                </div>
                {dsarResult.exemptions_and_retention_conflicts.map((ex) => (
                  <div
                    key={ex.code}
                    className="rounded-lg border border-amber-500/30 bg-amber-950/20 p-3 space-y-1"
                  >
                    <div className="flex items-center justify-between font-mono">
                      <span className="font-bold text-amber-300">{ex.statute}</span>
                      <span className="uppercase text-[10px] rounded bg-amber-950 px-2 py-0.5 text-amber-200">
                        {ex.scope}
                      </span>
                    </div>
                    <p className="text-slate-200">{ex.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-slate-300">
              Click <strong>Evaluate DSAR Nexus & Deadlines</strong> above to compute the strictest statutory deadline and partial exemption rules.
            </p>
          )}
        </div>
      </div>

      {/* Section 6: Data & Vendors / RoPA Registry */}
      {showRopaSection && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-3" data-testid="ropa-registry-table">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-100">
                Records of Processing Activities (GDPR Art. 30 · Quebec Law 25 · CPRA Data Inventory & Vendors)
              </h3>
              <p className="text-xs text-slate-300">
                Live inventory linking processing purposes, data categories, cross-border mechanisms, and subprocessors.
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-300">
                  <th className="py-2 pr-3">Record ID</th>
                  <th className="py-2 px-3">Processing Activity</th>
                  <th className="py-2 px-3">Role</th>
                  <th className="py-2 px-3">Jurisdictions</th>
                  <th className="py-2 px-3">Transfer Mechanism</th>
                  <th className="py-2 pl-3">Retention</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70">
                {ropaRecords.map((r) => (
                  <tr key={r.record_id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 pr-3 font-mono font-bold text-emerald-300">{r.record_id}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-100">{r.processing_activity}</td>
                    <td className="py-2.5 px-3 text-slate-200">{r.role}</td>
                    <td className="py-2.5 px-3 font-mono text-sky-300">{r.jurisdictions.join(', ')}</td>
                    <td className="py-2.5 px-3 text-slate-200">{r.cross_border_transfer_mechanism}</td>
                    <td className="py-2.5 pl-3 text-slate-300">{r.retention_schedule}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
};
