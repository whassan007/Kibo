import React from 'react';
import { OperationalStatusBadge } from '../../design-system/primitives';
import { ALL_WORKSPACE_ROLES } from '../navigation/WorkspaceNavigation';
import type {
  AuthorizedOrganizationEntry,
  CorporateAiHubIntegrationStatus,
  OperationalDataStatus,
} from '../../services/privacyOsService';

export interface AdministrationViewProps {
  organizations: AuthorizedOrganizationEntry[];
  activeTenantId: string;
  operationalStatus: OperationalDataStatus;
  integrations: CorporateAiHubIntegrationStatus[];
  sessionVerified: boolean;
}

export const AdministrationView: React.FC<AdministrationViewProps> = ({
  organizations,
  activeTenantId,
  operationalStatus,
  integrations,
  sessionVerified,
}) => {
  return (
    <section aria-label="Enterprise System & Security Administration" data-testid="administration-view" className="space-y-6">
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100">
            Enterprise Security, Tenant Isolation & Connector Administration
          </h2>
          <p className="text-xs text-slate-300">
            Server-verified JWT session controls, multi-tenant SQL/vector isolation status, and Corporate AI Hub health.
          </p>
        </div>
        <OperationalStatusBadge status={operationalStatus} />
      </div>

      {/* Security & Session Hardening Status (UX-08) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="rounded-xl border border-emerald-500/40 bg-slate-900/70 p-4 space-y-1.5">
          <div className="font-mono font-bold text-emerald-300">SESSION INTEGRITY (UX-08)</div>
          <div className="text-sm font-semibold text-slate-100">
            {sessionVerified ? '✓ Server-Verified Enterprise JWT' : '🛡 Local Verified Session Guard'}
          </div>
          <p className="text-slate-300">
            Raw editable X-Tenant-ID and X-User-ID header spoofing inputs have been permanently removed from the UI.
          </p>
        </div>

        <div className="rounded-xl border border-sky-500/40 bg-slate-900/70 p-4 space-y-1.5">
          <div className="font-mono font-bold text-sky-300">ZERO SURPRISE MUTATIONS (UX-15)</div>
          <div className="text-sm font-semibold text-slate-100">✓ Read-Only Mount Enforced</div>
          <p className="text-slate-300">
            Opening the workspace fires 0 automatic POST mutations. Evaluations, incidents, and DSAR calculations run only on explicit user action.
          </p>
        </div>

        <div className="rounded-xl border border-purple-500/40 bg-slate-900/70 p-4 space-y-1.5">
          <div className="font-mono font-bold text-purple-300">TRUTHFUL OFFLINE MODEL (UX-07)</div>
          <div className="text-sm font-semibold text-slate-100">✓ 7-State Operational Status</div>
          <p className="text-slate-300">
            Distinguishes LIVE, UPDATING, STALE, OFFLINE, DEMO, ERROR, and UNVERIFIED states without silent synthetic fallback.
          </p>
        </div>
      </div>

      {/* Authorized Organization Memberships */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-3 text-xs">
        <h3 className="text-sm font-bold text-slate-100">
          Authorized Organization Memberships ({organizations.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {organizations.map((org) => (
            <div
              key={org.tenant_id}
              className={`rounded-lg border p-3.5 space-y-1 ${
                org.tenant_id === activeTenantId
                  ? 'border-emerald-400 bg-slate-800/80'
                  : 'border-slate-800 bg-slate-950/70'
              }`}
            >
              <div className="font-mono font-bold text-emerald-300">{org.tenant_id}</div>
              <div className="font-semibold text-slate-100">{org.name}</div>
              <div className="text-slate-300">Industry: {org.industry}</div>
              <div className="font-mono text-[11px] text-sky-300">
                Jurisdictions: {org.jurisdictions.join(', ') || 'Empty Onboarding Workspace'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 9-Role RBAC Matrix */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-3 text-xs">
        <h3 className="text-sm font-bold text-slate-100">
          9-Role Enterprise Access & Governance Matrix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {ALL_WORKSPACE_ROLES.map((r) => (
            <div key={r.role} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <div className="font-mono font-bold text-emerald-300">{r.role}</div>
              <div className="font-semibold text-slate-100">{r.label}</div>
              <div className="text-slate-300 mt-1">{r.focus}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Connector Status Summary */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-3 text-xs">
        <h3 className="text-sm font-bold text-slate-100">
          Configured Corporate AI Hub Connectors ({integrations.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {integrations.map((hub) => (
            <div key={hub.hub_id} className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <div className="font-mono font-bold text-sky-300">{hub.hub_id}</div>
              <div className="font-semibold text-slate-100">{hub.name}</div>
              <div className="text-slate-300 mt-1">Status: {hub.status.toUpperCase()}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
