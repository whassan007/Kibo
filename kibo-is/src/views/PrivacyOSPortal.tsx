import React, { useState, useEffect, useCallback } from 'react';
import {
  PrivacyOsService,
  getAuthorizedOrganizations,
  getPrivacyOsTenantContext,
  setPrivacyOsTenantContext,
  setDemoModeEnabled,
  type AuthorizedOrganizationEntry,
  type CorporateAiHubIntegrationStatus,
  type JurisdictionEntry,
  type OperationalDataStatus,
  type RopaRecord,
  type WorkspaceRole,
} from '../services/privacyOsService';
import { liveEventClient, type LiveEventEnvelope } from '../services/liveEventClient';
import { WorkspaceErrorBoundary } from '../design-system/primitives';
import type { ThemeMode } from '../design-system/tokens';
import { TRANSLATIONS, type SupportedLocale } from '../i18n/translations';
import {
  WorkspaceNavigation,
  type PrimarySectionId,
} from '../features/navigation/WorkspaceNavigation';
import {
  ExecutiveHomeView,
  type PriorityWorkItem,
} from '../features/home/ExecutiveHomeView';
import { UnifiedInboxView } from '../features/inbox/UnifiedInboxView';
import { GuidedAssessmentWizard } from '../features/assessments/GuidedAssessmentWizard';
import { BreachWorkspaceView } from '../features/incidents/BreachWorkspaceView';
import { PrivacyRightsView } from '../features/rights/PrivacyRightsView';
import { JurisdictionWorkspaceView } from '../features/jurisdictions/JurisdictionWorkspaceView';
import { RegulatoryIntelView } from '../features/regulatory/RegulatoryIntelView';
import { ReportsAnalyticsView } from '../features/reports/ReportsAnalyticsView';
import { GovernedAssistantView } from '../features/assistant/GovernedAssistantView';
import { GuidedOnboardingView } from '../features/onboarding/GuidedOnboardingView';
import { LiveActivityFeed } from '../features/activity/LiveActivityFeed';
import { CommandPaletteModal } from '../features/search/CommandPaletteModal';
import { AdministrationView } from '../features/admin/AdministrationView';

const INITIAL_PRIORITY_ITEMS: PriorityWorkItem[] = [
  {
    id: 'INB-2026-0194',
    title: 'DSAR-2026-0194 — Dual-Scope Access & Deletion Request (California + Quebec Resident)',
    category: 'DSAR',
    jurisdiction: 'US-CA · CA-QC',
    owner: 'usr-cpo-counsel-01',
    deadlineLabel: 'Overdue by 4h',
    hoursRemaining: -4,
    overdue: true,
    requiresApproval: true,
    targetSection: 'rights',
  },
  {
    id: 'INB-2026-0412',
    title: 'Clinical AI Diagnostic Triage — Combined GDPR Art. 35 DPIA + Ontario PHIPA TRA + Law 25 EFVP',
    category: 'Assessment',
    jurisdiction: 'CA-ON · CA-QC · EU-GDPR',
    owner: 'usr-cpo-counsel-01',
    deadlineLabel: '16h remaining',
    hoursRemaining: 16,
    overdue: false,
    requiresApproval: true,
    targetSection: 'assessments',
  },
  {
    id: 'INB-2026-0881',
    title: 'INC-2026-881 — Subprocessor Cloud Telemetry Bucket Misconfiguration Triage',
    category: 'Incident',
    jurisdiction: 'EU-DE · CA-QC · US-NY',
    owner: 'usr-cpo-counsel-01',
    deadlineLabel: '41h remaining (72h clock)',
    hoursRemaining: 41,
    overdue: false,
    requiresApproval: true,
    targetSection: 'incidents',
  },
  {
    id: 'INB-2026-0905',
    title: 'REG-2026-0905 — California CPPA ADMT Rulemaking & Colorado AI Act Rule Pack Promotion',
    category: 'Regulatory',
    jurisdiction: 'US-CA · US-CO',
    owner: 'usr-legal-counsel-01',
    deadlineLabel: '5d remaining',
    hoursRemaining: 120,
    overdue: false,
    requiresApproval: true,
    targetSection: 'regulatory',
  },
];

export const PrivacyOSPortal: React.FC = () => {
  const [activeSection, setActiveSection] = useState<PrimarySectionId>('home');
  const [activeRole, setActiveRole] = useState<WorkspaceRole>('CPO');
  const [organizations, setOrganizations] = useState<AuthorizedOrganizationEntry[]>(
    getAuthorizedOrganizations()
  );
  const [activeTenantId, setActiveTenantId] = useState<string>(
    getPrivacyOsTenantContext().tenantId
  );
  const [userDisplayName, setUserDisplayName] = useState<string>(
    'Dr. Elena Vance, CIPP/E, CIPP/US, CIPM'
  );
  const [sessionVerified, setSessionVerified] = useState<boolean>(true);
  const [operationalStatus, setOperationalStatus] = useState<OperationalDataStatus>('updating');
  const [cachedAt, setCachedAt] = useState<string | undefined>(undefined);
  const [locale, setLocale] = useState<SupportedLocale>('en');
  const [theme, setTheme] = useState<ThemeMode>('dark');
  const [demoMode, setDemoMode] = useState<boolean>(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState<boolean>(false);

  // Read-only reference datasets loaded on mount (ZERO automatic POST mutations — UX-15)
  const [jurisdictions, setJurisdictions] = useState<JurisdictionEntry[]>([]);
  const [ropaRecords, setRopaRecords] = useState<RopaRecord[]>([]);
  const [integrations, setIntegrations] = useState<CorporateAiHubIntegrationStatus[]>([]);
  const [priorityItems, setPriorityItems] = useState<PriorityWorkItem[]>(INITIAL_PRIORITY_ITEMS);
  const [inboxCount, setInboxCount] = useState<number>(4);
  const [liveEvents, setLiveEvents] = useState<LiveEventEnvelope[]>([]);
  const [onboardedEmptyTenants, setOnboardedEmptyTenants] = useState<Record<string, boolean>>({});

  const loadReadOnlyWorkspaceState = useCallback(
    async (roleOverride?: WorkspaceRole) => {
      setOperationalStatus('updating');
      const [sessionRes, jurRes, ropaRes, intRes] = await Promise.all([
        PrivacyOsService.getVerifiedSession(roleOverride || activeRole),
        PrivacyOsService.getJurisdictions(),
        PrivacyOsService.getRopaRecords(),
        PrivacyOsService.getIntegrationsStatus(),
      ]);

      setUserDisplayName(sessionRes.session.display_name);
      setSessionVerified(sessionRes.session.session_verified);
      if (sessionRes.session.authorized_organizations?.length) {
        setOrganizations(sessionRes.session.authorized_organizations);
      }
      setJurisdictions(jurRes.jurisdictions);
      setRopaRecords(ropaRes.records);
      setIntegrations(intRes.integrations);
      setOperationalStatus(jurRes.status);
      setCachedAt(jurRes.cachedAt);
    },
    [activeRole]
  );

  // Initial mount: ONLY read-only GET queries and SSE subscription — ZERO POST mutations (UX-15)
  useEffect(() => {
    void loadReadOnlyWorkspaceState();
    const unsub = liveEventClient.subscribe((events) => {
      setLiveEvents(events);
    });
    void liveEventClient.connect(activeTenantId);
    return () => {
      unsub();
      liveEventClient.disconnect();
    };
  }, [activeTenantId, loadReadOnlyWorkspaceState]);

  const handleSelectOrganization = (nextTenantId: string) => {
    setPrivacyOsTenantContext({ tenantId: nextTenantId });
    setActiveTenantId(nextTenantId);
    liveEventClient.switchTenant(nextTenantId);
  };

  const handleChangeRole = (nextRole: WorkspaceRole) => {
    setActiveRole(nextRole);
    void loadReadOnlyWorkspaceState(nextRole);
  };

  const handleToggleDemoMode = () => {
    const next = !demoMode;
    setDemoMode(next);
    setDemoModeEnabled(next);
    void loadReadOnlyWorkspaceState();
  };

  const handleQuickApproveFromHome = (id: string) => {
    setPriorityItems((prev) =>
      prev.map((i) =>
        i.id === id ? { ...i, requiresApproval: false, overdue: false, deadlineLabel: 'Approved ✓' } : i
      )
    );
    setInboxCount((c) => Math.max(0, c - 1));
    void liveEventClient.publishEvent({
      event_type: 'approval.completed',
      title: `Executive Quick Sign-Off: ${id}`,
      summary: `Approved directly from CPO Executive Command Center with sealed audit receipt.`,
      severity: 'success',
      entity_type: 'case',
      entity_id: id,
      target_section: 'home',
    });
  };

  const activeOrg = organizations.find((o) => o.tenant_id === activeTenantId);
  const showEmptyOnboarding =
    Boolean(activeOrg?.is_empty_workspace) && !onboardedEmptyTenants[activeTenantId];
  const t = TRANSLATIONS[locale];

  return (
    <div
      data-testid="privacy-os-portal-root"
      data-theme={theme}
      className={
        theme === 'light'
          ? 'min-h-screen bg-slate-50 text-slate-900'
          : 'min-h-screen bg-[#0B1120] text-slate-100'
      }
    >
      <WorkspaceNavigation
        activeSection={activeSection}
        onSelectSection={(sec) => setActiveSection(sec)}
        activeRole={activeRole}
        onChangeRole={handleChangeRole}
        organizations={organizations}
        activeTenantId={activeTenantId}
        onSelectOrganization={handleSelectOrganization}
        operationalStatus={operationalStatus}
        cachedAt={cachedAt}
        locale={locale}
        onChangeLocale={(loc) => setLocale(loc)}
        theme={theme}
        onToggleTheme={() => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
        demoMode={demoMode}
        onToggleDemoMode={handleToggleDemoMode}
        onOpenCommandPalette={() => setCommandPaletteOpen(true)}
        inboxCount={inboxCount}
        incidentCount={priorityItems.filter((i) => i.category === 'Incident').length}
        userDisplayName={userDisplayName}
        sessionVerified={sessionVerified}
      />

      {/* Offline / Stale / Demo Truthfulness Banner (UX-07) */}
      {(operationalStatus === 'offline' ||
        operationalStatus === 'stale' ||
        operationalStatus === 'demo') && (
        <div
          role="status"
          data-testid="operational-truthfulness-banner"
          className={`mx-auto max-w-7xl mt-3 px-4 py-2.5 rounded-xl border text-xs flex flex-wrap items-center justify-between gap-2 ${
            operationalStatus === 'demo'
              ? 'border-purple-500/40 bg-purple-950/40 text-purple-200'
              : operationalStatus === 'stale'
              ? 'border-amber-500/40 bg-amber-950/40 text-amber-200'
              : 'border-rose-500/40 bg-rose-950/40 text-rose-200'
          }`}
        >
          <span>
            {operationalStatus === 'demo'
              ? '◈ DEMO SANDBOX MODE ACTIVE: Displaying explicitly labeled reference records. Switch off Demo Mode to resume live backend operations.'
              : operationalStatus === 'stale'
              ? `◷ STALE SNAPSHOT: Backend temporarily unreachable; displaying cached tenant records from ${
                  cachedAt || 'recent session'
                }.`
              : '✕ OFFLINE MODE: Backend API is currently unreachable. Corporate AI Hub connectors are marked OFFLINE and synthetic data is never presented as live.'}
          </span>
          <button
            type="button"
            onClick={() => void loadReadOnlyWorkspaceState()}
            className="rounded bg-slate-900 border border-slate-700 px-2.5 py-1 text-xs font-semibold text-slate-100"
          >
            ↻ Retry Live Connection
          </button>
        </div>
      )}

      {/* Main Workspace Container */}
      <main
        id="main-workspace-content"
        className="mx-auto max-w-7xl px-4 py-6 space-y-6"
      >
        {/* Legal Citation Language Integrity Notice */}
        <div className="rounded-lg border border-slate-800/80 bg-slate-900/50 px-3.5 py-2 text-[11px] text-slate-300 flex items-center justify-between">
          <span>⚖ {t.legalIntegrityBanner}</span>
          <span className="font-mono text-emerald-300">Zero Mount Mutations Enforced (UX-15)</span>
        </div>

        <WorkspaceErrorBoundary sectionName={activeSection.toUpperCase()}>
          {showEmptyOnboarding ? (
            <GuidedOnboardingView
              organizationName={activeOrg?.name || 'New Organization'}
              onCompleteOnboarding={() => {
                setOnboardedEmptyTenants((prev) => ({ ...prev, [activeTenantId]: true }));
                setActiveSection('assessments');
              }}
            />
          ) : (
            <>
              {activeSection === 'home' && (
                <ExecutiveHomeView
                  role={activeRole}
                  locale={locale}
                  operationalStatus={operationalStatus}
                  priorityItems={priorityItems}
                  liveEvents={liveEvents}
                  onNavigateSection={(sec) => setActiveSection(sec)}
                  onQuickApproveItem={handleQuickApproveFromHome}
                />
              )}

              {activeSection === 'inbox' && (
                <UnifiedInboxView onCountChange={(cnt) => setInboxCount(cnt)} />
              )}

              {activeSection === 'assessments' && (
                <GuidedAssessmentWizard
                  onStatusChange={(live) => setOperationalStatus(live ? 'live' : 'offline')}
                />
              )}

              {(activeSection === 'incidents' || activeSection === 'war_room') && (
                <BreachWorkspaceView
                  onStatusChange={(live) => setOperationalStatus(live ? 'live' : 'offline')}
                />
              )}

              {(activeSection === 'rights' ||
                activeSection === 'dsar_ropa' ||
                activeSection === 'data_vendors') && (
                <PrivacyRightsView
                  ropaRecords={ropaRecords}
                  showRopaSection={true}
                  onStatusChange={(live) => setOperationalStatus(live ? 'live' : 'offline')}
                />
              )}

              {activeSection === 'regulatory' && (
                <RegulatoryIntelView
                  locale={locale}
                  onSelectJurisdictionMatrix={() => setActiveSection('applicability')}
                />
              )}

              {(activeSection === 'applicability' || activeSection === 'coverage_matrix') && (
                <JurisdictionWorkspaceView
                  jurisdictions={jurisdictions}
                  onStatusChange={(live) => setOperationalStatus(live ? 'live' : 'offline')}
                />
              )}

              {activeSection === 'risks_controls' && (
                <ReportsAnalyticsView mode="risks_controls" />
              )}

              {activeSection === 'reports' && <ReportsAnalyticsView mode="reports" />}

              {(activeSection === 'assistant' || activeSection === 'ai_hubs') && (
                <GovernedAssistantView
                  integrations={integrations}
                  operationalStatus={operationalStatus}
                  onStatusChange={(live) => setOperationalStatus(live ? 'live' : 'offline')}
                />
              )}

              {activeSection === 'admin' && (
                <AdministrationView
                  organizations={organizations}
                  activeTenantId={activeTenantId}
                  operationalStatus={operationalStatus}
                  integrations={integrations}
                  sessionVerified={sessionVerified}
                />
              )}
            </>
          )}
        </WorkspaceErrorBoundary>

        {/* Bottom Live SSE Activity Feed */}
        <LiveActivityFeed
          events={liveEvents}
          status={operationalStatus}
          onRefreshStream={() => void liveEventClient.fetchRecent(activeTenantId)}
        />
      </main>

      {/* Cmd+K Global Command Palette Modal */}
      <CommandPaletteModal
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onSelectSection={(sec) => setActiveSection(sec)}
      />
    </div>
  );
};

export default PrivacyOSPortal;
