import React, { useState } from 'react';
import { OperationalStatusBadge } from '../../design-system/primitives';
import type {
  AuthorizedOrganizationEntry,
  OperationalDataStatus,
  WorkspaceRole,
} from '../../services/privacyOsService';
import type { SupportedLocale } from '../../i18n/translations';
import { TRANSLATIONS } from '../../i18n/translations';
import type { ThemeMode } from '../../design-system/tokens';

export type PrimarySectionId =
  | 'home'
  | 'inbox'
  | 'assessments'
  | 'incidents'
  | 'rights'
  | 'data_vendors'
  | 'regulatory'
  | 'risks_controls'
  | 'reports'
  | 'assistant'
  | 'admin'
  // Legacy alias compatibility for existing tests & deep links
  | 'applicability'
  | 'war_room'
  | 'dsar_ropa'
  | 'ai_hubs'
  | 'coverage_matrix';

export interface WorkspaceNavigationProps {
  activeSection: PrimarySectionId;
  onSelectSection: (section: PrimarySectionId) => void;
  activeRole: WorkspaceRole;
  onChangeRole: (role: WorkspaceRole) => void;
  organizations: AuthorizedOrganizationEntry[];
  activeTenantId: string;
  onSelectOrganization: (tenantId: string) => void;
  operationalStatus: OperationalDataStatus;
  cachedAt?: string;
  locale: SupportedLocale;
  onChangeLocale: (locale: SupportedLocale) => void;
  theme: ThemeMode;
  onToggleTheme: () => void;
  demoMode: boolean;
  onToggleDemoMode: () => void;
  onOpenCommandPalette: () => void;
  inboxCount: number;
  incidentCount: number;
  userDisplayName: string;
  sessionVerified: boolean;
}

export const ALL_WORKSPACE_ROLES: Array<{ role: WorkspaceRole; label: string; focus: string }> = [
  { role: 'CPO', label: 'Chief Privacy Officer (CPO)', focus: 'Executive Risk, Sign-offs & Board Posture' },
  { role: 'DPO', label: 'Data Protection Officer (DPO)', focus: 'GDPR/Law 25 Assessments, DSARs & Supervisory Authority Liaison' },
  { role: 'LEGAL', label: 'Privacy Counsel / Legal', focus: 'Citation Verification, Privilege Gates & Regulatory Promotions' },
  { role: 'ANALYST', label: 'Privacy Analyst', focus: 'Queue Triage, RoPA Maintenance, Evidence & Draft Assessments' },
  { role: 'SECURITY', label: 'Security & Incident Response', focus: 'Breach Containment, Forensics & Statutory Notification Clocks' },
  { role: 'MANAGER', label: 'Business / Product Owner', focus: 'Project Privacy Intake, Vendor Requests & Control Evidence' },
  { role: 'EMPLOYEE', label: 'Employee Self-Service', focus: 'Guided Privacy Questions, Policy Lookup & Incident Reporting' },
  { role: 'AUDITOR', label: 'Compliance & External Auditor', focus: 'SHA-256 Sealed Evidence Packs, Control Matrix & Audit Trail' },
  { role: 'ADMIN', label: 'System Administrator', focus: 'Authorized Tenants, SSO/RBAC, AI Hub Connectors & SSE Health' },
];

export const WorkspaceNavigation: React.FC<WorkspaceNavigationProps> = ({
  activeSection,
  onSelectSection,
  activeRole,
  onChangeRole,
  organizations,
  activeTenantId,
  onSelectOrganization,
  operationalStatus,
  cachedAt,
  locale,
  onChangeLocale,
  theme,
  onToggleTheme,
  demoMode,
  onToggleDemoMode,
  onOpenCommandPalette,
  inboxCount,
  incidentCount,
  userDisplayName,
  sessionVerified,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const t = TRANSLATIONS[locale];

  const primaryNavItems: Array<{
    id: PrimarySectionId;
    label: string;
    badge?: number;
    roles?: WorkspaceRole[];
  }> = [
    { id: 'home', label: `1. ${t.nav.home}` },
    { id: 'inbox', label: `2. ${t.nav.inbox}`, badge: inboxCount },
    { id: 'assessments', label: `3. ${t.nav.assessments}` },
    { id: 'incidents', label: `4. ${t.nav.incidents}`, badge: incidentCount },
    { id: 'rights', label: `5. ${t.nav.rights}` },
    { id: 'data_vendors', label: `6. ${t.nav.dataVendors}` },
    { id: 'regulatory', label: `7. ${t.nav.regulatory}` },
    { id: 'risks_controls', label: `8. ${t.nav.risksControls}` },
    { id: 'reports', label: `9. ${t.nav.reports}` },
    { id: 'assistant', label: `10. ${t.nav.assistant}` },
    { id: 'admin', label: `11. ${t.nav.admin}` },
  ];

  const isNavActive = (id: PrimarySectionId): boolean => {
    if (activeSection === id) return true;
    if (id === 'incidents' && activeSection === 'war_room') return true;
    if (id === 'rights' && activeSection === 'dsar_ropa') return true;
    if (id === 'assistant' && activeSection === 'ai_hubs') return true;
    if (id === 'regulatory' && (activeSection === 'applicability' || activeSection === 'coverage_matrix')) return true;
    return false;
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/95 backdrop-blur sticky top-0 z-30">
      <a
        href="#main-workspace-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-lg focus:bg-sky-500 focus:px-4 focus:py-2 focus:text-xs focus:font-bold focus:text-slate-950"
      >
        {t.skipToMain}
      </a>

      {/* Top Enterprise Identity, Organization Switcher & Operational Status Bar */}
      <div className="mx-auto max-w-7xl px-4 py-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/20 border border-emerald-400/50 text-emerald-300 font-bold font-mono text-sm">
            K
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-slate-100">{t.brandTitle}</h1>
              <OperationalStatusBadge status={operationalStatus} cachedAt={cachedAt} />
            </div>
            <p className="text-xs text-slate-300">{t.brandSubtitle}</p>
          </div>
        </div>

        {/* Command Palette Trigger + Verified Session & Authorized Org Switcher (Replaces UX-08 Spoofing Inputs) */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={onOpenCommandPalette}
            data-testid="open-command-palette-btn"
            aria-label="Open global command palette"
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:border-sky-400 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            <span>⌕</span>
            <span>{t.commandPaletteHint}</span>
          </button>

          {/* Authorized Organization Switcher (UX-08) */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="authorized-org-switcher" className="text-[11px] font-medium text-slate-300">
              Organization:
            </label>
            <select
              id="authorized-org-switcher"
              data-testid="authorized-org-switcher"
              value={activeTenantId}
              onChange={(e) => onSelectOrganization(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-400"
            >
              {organizations.map((org) => (
                <option key={org.tenant_id} value={org.tenant_id}>
                  {org.name} ({org.is_empty_workspace ? 'Empty Setup' : org.industry})
                </option>
              ))}
            </select>
          </div>

          {/* Role-Aware Workspace Switcher (Section 5: 9 Roles) */}
          <div className="flex items-center gap-1.5">
            <label htmlFor="workspace-role-switcher" className="text-[11px] font-medium text-slate-300">
              Role:
            </label>
            <select
              id="workspace-role-switcher"
              data-testid="workspace-role-switcher"
              value={activeRole}
              onChange={(e) => onChangeRole(e.target.value as WorkspaceRole)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-xs font-semibold text-emerald-300 focus:outline-none focus:ring-2 focus:ring-sky-400"
            >
              {ALL_WORKSPACE_ROLES.map((r) => (
                <option key={r.role} value={r.role}>
                  {r.role} — {r.label}
                </option>
              ))}
            </select>
          </div>

          {/* Verified User Session Badge (No Raw Header Spoofing) */}
          <div
            data-testid="verified-user-session-badge"
            className="hidden xl:flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900/90 px-2.5 py-1 text-xs text-slate-200"
            title="Authenticated enterprise session principal (raw header spoofing disabled)"
          >
            <span className="text-emerald-400" aria-hidden="true">
              {sessionVerified ? '🔒' : '🛡'}
            </span>
            <span className="truncate max-w-[160px]">{userDisplayName}</span>
          </div>

          {/* Language Selector (EN / FR / DE) */}
          <select
            aria-label="Interface Language"
            data-testid="locale-switcher"
            value={locale}
            onChange={(e) => onChangeLocale(e.target.value as SupportedLocale)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            <option value="en">EN</option>
            <option value="fr">FR</option>
            <option value="de">DE</option>
          </select>

          {/* Light / Dark Theme Toggle */}
          <button
            type="button"
            onClick={onToggleTheme}
            data-testid="theme-toggle-btn"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
            className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-xs text-slate-200 hover:border-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
          >
            {theme === 'dark' ? '☀ Light' : '☾ Dark'}
          </button>

          {/* Explicit Demo Sandbox Toggle */}
          <button
            type="button"
            onClick={onToggleDemoMode}
            data-testid="demo-mode-toggle-btn"
            aria-pressed={demoMode}
            className={`rounded-lg border px-2.5 py-1.5 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-sky-400 ${
              demoMode
                ? 'border-purple-400 bg-purple-950/80 text-purple-200'
                : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-500'
            }`}
          >
            {demoMode ? '◈ Demo Sandbox Active' : '◈ Demo Mode Off'}
          </button>

          {/* Mobile Drawer Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle mobile navigation menu"
            className="md:hidden rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
          >
            ☰ Menu
          </button>
        </div>
      </div>

      {/* 11-Section Task-Oriented Primary Navigation Bar */}
      <nav
        aria-label="Primary Privacy Office Navigation"
        className={`mx-auto max-w-7xl px-4 pb-2 ${mobileMenuOpen ? 'block' : 'hidden md:block'}`}
      >
        <div className="flex flex-wrap items-center gap-1.5">
          {primaryNavItems.map((item) => {
            const active = isNavActive(item.id);
            return (
              <button
                key={item.id}
                type="button"
                data-testid={`nav-section-${item.id}`}
                aria-current={active ? 'page' : undefined}
                onClick={() => {
                  onSelectSection(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-sky-400 ${
                  active
                    ? 'bg-emerald-500/20 border border-emerald-400 text-emerald-200 font-semibold'
                    : 'border border-transparent text-slate-300 hover:bg-slate-900 hover:text-slate-100'
                }`}
              >
                <span>{item.label}</span>
                {typeof item.badge === 'number' && item.badge > 0 && (
                  <span className="rounded-full bg-amber-500/20 border border-amber-400/40 px-1.5 py-0.2 text-[10px] font-mono text-amber-200">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
};
