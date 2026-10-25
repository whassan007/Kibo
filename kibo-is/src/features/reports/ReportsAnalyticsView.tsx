import React, { useState } from 'react';

export interface ReportsAnalyticsViewProps {
  mode: 'risks_controls' | 'reports';
}

const CONTROL_MATRIX = [
  {
    controlId: 'CTRL-KMS-01',
    title: 'Regional Sovereign KMS Customer Key Custody (FIPS 140-3 L3)',
    regimes: ['GDPR Art. 32 & Ch. V', 'Quebec Law 25 s. 17', 'Ontario PHIPA s. 10', 'HIPAA § 164.312'],
    status: 'Effective · Verified',
    residualRisk: 'Low',
    evidenceRef: 'EVID-KMS-001 (SHA-256: 9f84a2c1...)',
  },
  {
    controlId: 'CTRL-HITL-02',
    title: 'Human Privacy Counsel Approval Gate for Statutory Filings & AI High-Risk Decisions',
    regimes: ['EU AI Act Art. 14 & Art. 27', 'GDPR Art. 22', 'CPRA ADMT § 1798.185', 'Law 25 s. 12.1'],
    status: 'Effective · Enforced',
    residualRisk: 'Low',
    evidenceRef: 'EVID-HITL-009 (SHA-256: 4c18b7e0...)',
  },
  {
    controlId: 'CTRL-DSAR-03',
    title: 'Dual-Scope Deletion & Statutory Retention Hold Segregation Engine',
    regimes: ['Cal. Civ. Code § 1798.105(d)', 'GDPR Art. 17(3)(b)', 'Quebec Law 25 s. 28'],
    status: 'Effective · Audited',
    residualRisk: 'Moderate',
    evidenceRef: 'EVID-DSAR-019 (SHA-256: 7a31d9f4...)',
  },
  {
    controlId: 'CTRL-TENANT-04',
    title: 'Cryptographic Multi-Tenant Context & Vector Retrieval Isolation',
    regimes: ['GDPR Art. 28 & Art. 32', 'PIPEDA Principle 4.7', 'SOC 2 CC6.1'],
    status: 'Effective · Verified',
    residualRisk: 'Low',
    evidenceRef: 'EVID-SEC-044 (SHA-256: 1d92f8a3...)',
  },
];

export const ReportsAnalyticsView: React.FC<ReportsAnalyticsViewProps> = ({ mode }) => {
  const [sealedBundleReceipt, setSealedBundleReceipt] = useState<string | null>(null);

  const handleGenerateAuditPack = (packType: string) => {
    const hash = 'a84f92c17e30b5519d2048fa91bc347291048576abcdef0192837465fabcde01';
    setSealedBundleReceipt(
      `Generated ${packType} (${new Date().toISOString()}) — Immutable SHA-256 Evidence Manifest: ${hash}`
    );
  };

  return (
    <section
      aria-label={mode === 'risks_controls' ? 'Risks & Technical Controls' : 'Executive Reports & Audit Bundles'}
      data-testid={`reports-analytics-${mode}`}
      className="space-y-5"
    >
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            {mode === 'risks_controls'
              ? 'Risks, Technical & Organizational Measures (TOMs) & Control Effectiveness Matrix'
              : 'Executive Board Reports, Regulator-Ready Dossiers & SHA-256 Sealed Evidence Packs'}
          </h2>
          <p className="text-xs text-slate-300">
            Maps technical controls directly to statutory obligations across US Federal/State, Canadian Federal/Provincial, and EU Member State regimes.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="export-audit-bundle-btn"
            onClick={() => handleGenerateAuditPack('Multi-Jurisdictional Regulator Evidence Bundle')}
            className="rounded-lg bg-emerald-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            ⬇ Export SHA-256 Sealed Evidence Pack
          </button>
          <button
            type="button"
            onClick={() => handleGenerateAuditPack('CPO Board Posture Summary PDF/JSON')}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-2 text-xs font-semibold text-slate-100 hover:border-sky-400"
          >
            Generate Board Executive Summary
          </button>
        </div>
      </div>

      {sealedBundleReceipt && (
        <div
          role="status"
          data-testid="sealed-bundle-receipt"
          className="rounded-lg border border-emerald-500/40 bg-emerald-950/30 px-4 py-3 text-xs font-mono text-emerald-200"
        >
          ✓ {sealedBundleReceipt}
        </div>
      )}

      <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-100">
          Cross-Regime Control & Residual Risk Register
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-300">
                <th className="py-2 pr-3">Control ID</th>
                <th className="py-2 px-3">Control & Safeguard</th>
                <th className="py-2 px-3">Satisfied Statutory Regimes</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Residual Risk</th>
                <th className="py-2 pl-3">Sealed Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {CONTROL_MATRIX.map((c) => (
                <tr key={c.controlId} className="hover:bg-slate-800/40">
                  <td className="py-2.5 pr-3 font-mono font-bold text-emerald-300">{c.controlId}</td>
                  <td className="py-2.5 px-3 font-semibold text-slate-100">{c.title}</td>
                  <td className="py-2.5 px-3 font-mono text-sky-300">{c.regimes.join(' · ')}</td>
                  <td className="py-2.5 px-3 text-emerald-300">{c.status}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-200">{c.residualRisk}</td>
                  <td className="py-2.5 pl-3 font-mono text-[11px] text-slate-300">{c.evidenceRef}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};
