import React, { useState, useEffect } from 'react';
import { StageStepper } from '../../design-system/primitives';
import {
  PrivacyOsService,
  loadAssessmentDrafts,
  saveAssessmentDraft,
  type AssessmentDraftRecord,
  type RecommendedAssessmentTemplate,
} from '../../services/privacyOsService';
import { liveEventClient } from '../../services/liveEventClient';

export const ASSESSMENT_WIZARD_STEPS: string[] = [
  '1. Business Purpose',
  '2. Data Subjects & Categories',
  '3. Jurisdictions & Locations',
  '4. Vendors & Transfers',
  '5. Automated Trigger Analysis',
  '6. Tailored Questionnaire',
  '7. Evidence & Controls',
  '8. Risk Summary',
  '9. Review & Approval',
];

export interface GuidedAssessmentWizardProps {
  onStatusChange?: (live: boolean) => void;
}

export const GuidedAssessmentWizard: React.FC<GuidedAssessmentWizardProps> = ({ onStatusChange }) => {
  const [drafts, setDrafts] = useState<AssessmentDraftRecord[]>([]);
  const [activeDraftId, setActiveDraftId] = useState<string>('DPIA-2026-0412');
  const [title, setTitle] = useState('Clinical AI Diagnostic Triage & Cross-Border Cloud Analytics');
  const [activityName, setActivityName] = useState('AI-Assisted Patient Diagnostic Triage & Telemetry');
  const [selectedJurisdictions, setSelectedJurisdictions] = useState<string[]>([
    'US-CA',
    'CA-ON',
    'CA-QC',
    'EU-GDPR',
    'EU-DE',
  ]);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<string, string>>({
    businessPurpose:
      'Deploy clinical decision support model to assist hospital triage nurses while storing encrypted telemetry across regional cloud clusters.',
    lawfulBasis: 'GDPR Art. 6(1)(e) / Art. 9(2)(h) Healthcare Provision; Ontario PHIPA s. 37; HIPAA Treatment/Operations',
    dataSubjects: 'Patients, Hospital Clinicians, Member Portal Subscribers',
    dataCategories: 'PHI / Health Information, Biometric Vitals, Diagnostic Imagery, Session Identifiers',
    vendorsAndTransfers: 'Azure Sovereign Canada-East, Frankfurt EU-Central, and US-West Subprocessor Analytics',
    aiOversight: 'Mandatory licensed clinician sign-off before any treatment recommendation is acted upon (EU AI Act Art. 14 & Art. 27)',
    encryptionControl: 'Customer-Managed HSM Keys (FIPS 140-3 Level 3) with regional residency lock',
    retentionPeriod: '7 years statutory clinical archive; 90 days de-identified operational telemetry',
  });
  const [evidenceLinks, setEvidenceLinks] = useState<string[]>([
    'EVID-KMS-001: Sovereign HSM Key Custody Attestation (SHA-256: 9f84a2c1...)',
    'EVID-DPA-014: EU Standard Contractual Clauses (2021/914 Module 2) + Law 25 s. 17 Equivalency Matrix',
  ]);
  const [newEvidenceInput, setNewEvidenceInput] = useState('');
  const [templates, setTemplates] = useState<RecommendedAssessmentTemplate[]>([]);
  const [status, setStatus] = useState<AssessmentDraftRecord['status']>('draft');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [bannerMessage, setBannerMessage] = useState<string | null>(null);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    const saved = loadAssessmentDrafts();
    setDrafts(saved);
    if (saved.length > 0) {
      const first = saved[0];
      setActiveDraftId(first.draft_id);
      setTitle(first.title);
      setActivityName(first.activity_name);
      setSelectedJurisdictions(first.jurisdictions);
      setCurrentStep(first.current_step);
      setAnswers(first.answers);
      setEvidenceLinks(first.evidence_links);
      setStatus(first.status);
    }
  }, []);

  const handleSaveDraft = (nextStep = currentStep, nextStatus = status) => {
    const saved = saveAssessmentDraft({
      draft_id: activeDraftId,
      title,
      activity_name: activityName,
      jurisdictions: selectedJurisdictions,
      current_step: nextStep,
      answers,
      evidence_links: evidenceLinks,
      status: nextStatus,
      reviewer_notes: reviewerNotes,
    });
    setDrafts(loadAssessmentDrafts());
    setBannerMessage(`Draft ${saved.draft_id} saved at Step ${nextStep + 1} (${new Date(saved.updated_at).toLocaleTimeString()}).`);

    void liveEventClient.publishEvent({
      event_type: nextStatus === 'submitted_for_review' ? 'assessment.submitted' : nextStatus === 'approved' ? 'assessment.approved' : 'assessment.saved',
      title: `Assessment ${saved.draft_id} (${nextStatus.replace(/_/g, ' ').toUpperCase()})`,
      summary: `${title} — Step ${nextStep + 1}/9 across ${selectedJurisdictions.join(', ')}`,
      severity: nextStatus === 'approved' ? 'success' : 'info',
      entity_type: 'assessment',
      entity_id: saved.draft_id,
      target_section: 'assessments',
    });
  };

  const handleLoadDraft = (draft: AssessmentDraftRecord) => {
    setActiveDraftId(draft.draft_id);
    setTitle(draft.title);
    setActivityName(draft.activity_name);
    setSelectedJurisdictions(draft.jurisdictions);
    setCurrentStep(draft.current_step);
    setAnswers(draft.answers);
    setEvidenceLinks(draft.evidence_links);
    setStatus(draft.status);
    setReviewerNotes(draft.reviewer_notes || '');
    setBannerMessage(`Resumed saved draft ${draft.draft_id} at Step ${draft.current_step + 1}.`);
  };

  const handleRunTriggerAnalysis = async () => {
    setEvaluating(true);
    try {
      const res = await PrivacyOsService.recommendAssessments({
        activity_name: activityName,
        jurisdictions: selectedJurisdictions,
        involves_high_risk_processing: true,
        involves_ai_or_admt: true,
        involves_cross_border_transfer: true,
        involves_phi_or_hin: true,
        relies_on_legitimate_interests: false,
        is_public_sector: false,
      });
      setTemplates(res.recommendation.assessments);
      if (onStatusChange) onStatusChange(res.live);
      setBannerMessage(
        `Evaluated statutory assessment triggers (${res.recommendation.assessments.length} required instruments identified).`
      );
    } finally {
      setEvaluating(false);
    }
  };

  const handleAddEvidence = () => {
    if (!newEvidenceInput.trim()) return;
    setEvidenceLinks((prev) => [...prev, newEvidenceInput.trim()]);
    setNewEvidenceInput('');
  };

  return (
    <section aria-label="Guided Privacy Assessment Wizard" data-testid="guided-assessment-wizard" className="space-y-5">
      {/* Header & Reusable Organization Profile Banner */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold text-emerald-300">{activeDraftId}</span>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-xs font-mono uppercase text-slate-200">
              {status.replace(/_/g, ' ')}
            </span>
          </div>
          <h2 className="mt-1 text-base font-bold text-slate-100">
            Guided Multi-Jurisdictional Assessment (PIA · DPIA · PHIPA TRA · Law 25 EFVP/TIA · EU AI FRIA)
          </h2>
          <p className="text-xs text-slate-300">
            Organization Baseline Profile pre-populated (Controller · Healthcare & Regulated Finance · Establishments: US-CA, CA-ON, CA-QC, EU-DE)
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            data-testid="assessment-save-draft-btn"
            onClick={() => handleSaveDraft(currentStep, status)}
            className="rounded-lg border border-emerald-500/50 bg-emerald-950/60 px-3.5 py-2 text-xs font-semibold text-emerald-200 hover:bg-emerald-900/60"
          >
            💾 Save Draft
          </button>
          {drafts.length > 0 && (
            <button
              type="button"
              data-testid="assessment-resume-latest-btn"
              onClick={() => handleLoadDraft(drafts[0])}
              className="rounded-lg border border-sky-500/50 bg-sky-950/60 px-3.5 py-2 text-xs font-semibold text-sky-200 hover:bg-sky-900/60"
            >
              ↺ Resume Saved Draft ({drafts[0].draft_id})
            </button>
          )}
          <button
            type="button"
            data-testid="assessment-run-triggers-btn"
            onClick={() => void handleRunTriggerAnalysis()}
            disabled={evaluating}
            className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            {evaluating ? 'Evaluating Triggers...' : '⚡ Evaluate Statutory Triggers'}
          </button>
        </div>
      </div>

      {bannerMessage && (
        <div
          role="status"
          data-testid="assessment-status-banner"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-2.5 text-xs text-emerald-200"
        >
          ✓ {bannerMessage}
        </div>
      )}

      {/* 9-Step Stage Stepper */}
      <StageStepper
        stages={ASSESSMENT_WIZARD_STEPS}
        currentIndex={currentStep}
        onSelectStage={(idx) => setCurrentStep(idx)}
      />

      {/* Step Content Workspace */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-slate-100">{ASSESSMENT_WIZARD_STEPS[currentStep]}</h3>
          <span className="text-xs font-mono text-slate-300">Step {currentStep + 1} of 9</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label htmlFor="assessment-title-input" className="block font-semibold text-slate-200 mb-1">
              Assessment Title
            </label>
            <input
              id="assessment-title-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="assessment-jurisdictions-input" className="block font-semibold text-slate-200 mb-1">
              In-Scope Jurisdictions (Comma-Separated Codes)
            </label>
            <input
              id="assessment-jurisdictions-input"
              type="text"
              value={selectedJurisdictions.join(', ')}
              onChange={(e) =>
                setSelectedJurisdictions(
                  e.target.value
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean)
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-slate-100"
            />
          </div>
        </div>

        {/* Dynamic Questionnaire & Plain-Language Legal Explanation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <label htmlFor="wizard-business-purpose" className="block font-semibold text-slate-200 mb-1">
              Processing Activity Description & Necessity (GDPR Art. 35(7)(a) / Law 25 s. 3.3)
            </label>
            <textarea
              id="wizard-business-purpose"
              rows={3}
              value={answers.businessPurpose || ''}
              onChange={(e) => setAnswers({ ...answers, businessPurpose: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
            />
            <p className="mt-1 text-[11px] text-slate-300">
              Why we ask: Regulators require proportionality between the business purpose and the volume/sensitivity of personal data collected.
            </p>
          </div>

          <div>
            <label htmlFor="wizard-safeguards" className="block font-semibold text-slate-200 mb-1">
              Technical, Encryption & Human Oversight Safeguards (PHIPA s. 10 / EU AI Act Art. 14)
            </label>
            <textarea
              id="wizard-safeguards"
              rows={3}
              value={answers.encryptionControl || ''}
              onChange={(e) => setAnswers({ ...answers, encryptionControl: e.target.value })}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
            />
            <p className="mt-1 text-[11px] text-slate-300">
              Why we ask: Customer-controlled KMS encryption and human-in-the-loop clinical oversight mitigate high-risk ADMT and cross-border exposure.
            </p>
          </div>
        </div>

        {/* Evidence Attachment Section */}
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2 text-xs">
          <div className="font-semibold text-slate-200">Attached Technical & Contractual Evidence Artifacts</div>
          <ul className="space-y-1 text-slate-300 font-mono">
            {evidenceLinks.map((ev) => (
              <li key={ev}>✓ {ev}</li>
            ))}
          </ul>
          <div className="flex gap-2 pt-2">
            <input
              type="text"
              value={newEvidenceInput}
              onChange={(e) => setNewEvidenceInput(e.target.value)}
              placeholder="Add evidence artifact ID or SHA-256 reference..."
              aria-label="New evidence reference"
              data-testid="assessment-evidence-input"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
            />
            <button
              type="button"
              data-testid="assessment-add-evidence-btn"
              onClick={handleAddEvidence}
              className="rounded-lg bg-slate-800 border border-slate-600 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:border-emerald-400"
            >
              + Attach Evidence
            </button>
          </div>
        </div>

        {/* Triggered Templates Matrix */}
        {templates.length > 0 && (
          <div className="space-y-2" data-testid="assessment-triggered-templates">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-300">
              Triggered Statutory Assessment Modules ({templates.length})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {templates.map((tpl) => (
                <div
                  key={tpl.assessment_code}
                  className="rounded-lg border border-slate-800 bg-slate-950/80 p-3 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-emerald-300">{tpl.assessment_code}</span>
                    <span className="rounded bg-emerald-950 px-2 py-0.5 text-[10px] text-emerald-200">
                      {tpl.mandatory ? 'MANDATORY' : 'RECOMMENDED'}
                    </span>
                  </div>
                  <div className="font-semibold text-slate-100">{tpl.title}</div>
                  <div className="font-mono text-[11px] text-sky-300">{tpl.statutory_basis}</div>
                  <div className="text-slate-300">{tpl.trigger_reason}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step Navigation & Governance Approval Submission */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 pt-4">
          <div className="flex gap-2">
            <button
              type="button"
              disabled={currentStep === 0}
              onClick={() => setCurrentStep((s) => Math.max(0, s - 1))}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 disabled:opacity-40"
            >
              ← Previous Step
            </button>
            <button
              type="button"
              data-testid="assessment-next-step-btn"
              disabled={currentStep >= ASSESSMENT_WIZARD_STEPS.length - 1}
              onClick={() => {
                const next = Math.min(ASSESSMENT_WIZARD_STEPS.length - 1, currentStep + 1);
                setCurrentStep(next);
                handleSaveDraft(next, status);
              }}
              className="rounded-lg border border-emerald-500/50 bg-emerald-950/60 px-3 py-1.5 text-xs font-semibold text-emerald-200 disabled:opacity-40"
            >
              Next Step →
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              data-testid="assessment-submit-review-btn"
              onClick={() => {
                setStatus('submitted_for_review');
                handleSaveDraft(8, 'submitted_for_review');
              }}
              className="rounded-lg bg-sky-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-sky-500"
            >
              Submit for DPO / Counsel Review
            </button>
            <button
              type="button"
              data-testid="assessment-approve-btn"
              onClick={() => {
                setStatus('approved');
                handleSaveDraft(8, 'approved');
              }}
              className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
            >
              ✓ Counsel / DPO Sign-Off & Seal
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
