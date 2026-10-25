import React, { useState } from 'react';
import { StageStepper } from '../../design-system/primitives';

export const ONBOARDING_STEPS: string[] = [
  '1. Organization Profile & Establishments',
  '2. Active Jurisdictions (US / CA / EU)',
  '3. Core Processing Activities & Vendors',
  '4. Governance Roles & First Baseline Assessment',
];

export interface GuidedOnboardingViewProps {
  organizationName: string;
  onCompleteOnboarding: () => void;
}

export const GuidedOnboardingView: React.FC<GuidedOnboardingViewProps> = ({
  organizationName,
  onCompleteOnboarding,
}) => {
  const [step, setStep] = useState(0);
  const [industry, setIndustry] = useState('Healthcare Provider & Clinical Diagnostics');
  const [employeeCount, setEmployeeCount] = useState(185);
  const [selectedJurisdictions, setSelectedJurisdictions] = useState<string[]>([
    'CA-ON',
    'CA-QC',
    'US-NY',
    'EU-GDPR',
  ]);
  const [dpoEmail, setDpoEmail] = useState('dpo@novamed-clinic.org');

  return (
    <section
      aria-label="Guided Privacy Office Onboarding"
      data-testid="guided-onboarding-view"
      className="rounded-2xl border border-emerald-500/40 bg-slate-900/90 p-6 space-y-5"
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="rounded bg-emerald-500/20 border border-emerald-400/40 px-2.5 py-0.5 font-mono text-xs font-bold text-emerald-300">
            NEW WORKSPACE ONBOARDING (UX-13)
          </span>
          <h2 className="mt-1.5 text-lg font-bold text-slate-100">
            Welcome to {organizationName} — Guided Privacy Office Setup
          </h2>
          <p className="text-xs text-slate-300">
            This organization has no configured records yet. Complete this 4-step guided setup to establish your baseline profile, active jurisdictions, and first assessment.
          </p>
        </div>
      </div>

      <StageStepper
        stages={ONBOARDING_STEPS}
        currentIndex={step}
        onSelectStage={(idx) => setStep(idx)}
      />

      <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-5 space-y-4 text-xs">
        <h3 className="text-sm font-bold text-slate-100">{ONBOARDING_STEPS[step]}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="onboard-industry" className="block font-semibold text-slate-200 mb-1">
              Primary Regulated Sector / Industry
            </label>
            <input
              id="onboard-industry"
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="onboard-employees" className="block font-semibold text-slate-200 mb-1">
              Employee Headcount
            </label>
            <input
              id="onboard-employees"
              type="number"
              value={employeeCount}
              onChange={(e) => setEmployeeCount(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="onboard-jurisdictions" className="block font-semibold text-slate-200 mb-1">
              Target Jurisdictions
            </label>
            <input
              id="onboard-jurisdictions"
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
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-slate-100"
            />
          </div>
          <div>
            <label htmlFor="onboard-dpo-email" className="block font-semibold text-slate-200 mb-1">
              Designated Privacy Officer / DPO Contact (Quebec Law 25 s. 3.1 / GDPR Art. 37)
            </label>
            <input
              id="onboard-dpo-email"
              type="email"
              value={dpoEmail}
              onChange={(e) => setDpoEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-slate-100"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-800">
          <div className="flex gap-2">
            <button
              type="button"
              disabled={step === 0}
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-slate-200 disabled:opacity-40"
            >
              ← Previous
            </button>
            <button
              type="button"
              data-testid="onboarding-next-step-btn"
              disabled={step >= ONBOARDING_STEPS.length - 1}
              onClick={() => setStep((s) => Math.min(ONBOARDING_STEPS.length - 1, s + 1))}
              className="rounded-lg border border-emerald-500/50 bg-emerald-950/60 px-3 py-1.5 font-semibold text-emerald-200 disabled:opacity-40"
            >
              Next Step →
            </button>
          </div>

          <button
            type="button"
            data-testid="onboarding-complete-btn"
            onClick={onCompleteOnboarding}
            className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold text-white hover:bg-emerald-500"
          >
            ✓ Initialize Workspace & Launch First Assessment
          </button>
        </div>
      </div>
    </section>
  );
};
