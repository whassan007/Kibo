# KIBO Privacy OS — UX & Frontend Architecture (`docs/ux/UX-ARCHITECTURE.md`)

## 1. Architectural Principles

1. **Task-Oriented Information Architecture (11 Primary Sections + Backward-Compatible Engine Views):**
   - Primary navigation is organized around privacy-office user goals:
     1. `home` — **Home:** My work, organizational status, overdue SLAs, and priorities.
     2. `inbox` — **Inbox:** Unified work queue for cases, approvals, requests, and escalations.
     3. `assessments` — **Assessments:** 9-step guided PIAs, DPIAs, TIAs, TRAs, and FRIA/ADMT reviews (`assessments_dsar` compatible).
     4. `incidents` — **Incidents:** Multi-jurisdiction breach war room, response phases, timelines, and notice approvals (`breach_war_room` compatible).
     5. `rights` — **Privacy Rights:** DSAR intake, identity verification, collection, redaction, and delivery approval.
     6. `data_vendors` — **Data & Vendors:** RoPA inventory, cross-border transfer validation, and subprocessor risk (`jrae` & `coverage_matrix` accessible).
     7. `regulatory_intelligence` — **Regulatory Intelligence:** Discovered laws, commissioner/court decisions, amendments, verified passage annotations, and legal review queue.
     8. `risks_controls` — **Risks & Controls:** Enterprise privacy governance, JRAE applicability engine (`jrae`), and global jurisdiction coverage matrix (`coverage_matrix`).
     9. `reports` — **Reports:** Operational, executive, and SHA-256-sealed audit reports.
     10. `assistant` — **Assistant:** Governed privacy guidance and verified Corporate AI Hub status (`ai_hubs_assistant` compatible).
     11. `administration` — **Administration:** Authorized tenant memberships, role permissions, integrations, and onboarding configuration.

2. **Zero Surprise Mutations on Mount (`UX-15`):**
   - Initial workspace load executes only idempotent `GET` requests (`/api/v1/compliance/jurisdictions`, `/api/v1/office/ropa/records`, `/api/v1/integrations/status`, `/api/v1/events/recent`).
   - Mutating `POST` endpoints (`/api/v1/office/incidents`, `/api/v1/office/assessments`, `/api/v1/compliance/applicability/evaluate`, etc.) are invoked **only** when the user explicitly clicks an action button.

3. **Explicit 7-State Operational Status Model (Section 8):**
   - Every data resource and header indicator explicitly tracks:
     - `LIVE` — Verified authoritative response from backend.
     - `UPDATING` — Request or multi-stage background job actively running.
     - `STALE` — Displaying previously verified cached response while refreshing or disconnected.
     - `OFFLINE` — Backend unreachable; synthetic demo data is **never** presented as live.
     - `DEMO` — Explicit synthetic sandbox mode toggled by the user (`DEMO MODE ACTIVE` banner).
     - `ERROR` — Operation failed with actionable recovery explanation.
     - `UNVERIFIED` — Regulatory source or annotation awaiting legal verification.

4. **Server-Verified Identity & Organization Switcher (`UX-08`):**
   - Removes raw `<input aria-label="X-Tenant-ID">` and `<input aria-label="X-User-ID">` fields from the UI.
   - Displays a read-only `UserProfileBadge` and an `OrganizationSwitcher` restricted to backend-authorized tenant memberships (`GET /api/v1/auth/session` or verified session claims).

---

## 2. Component & File Ownership Boundaries (25-Agent Conflict Prevention)

```text
kibo-is/
├── core/
│   └── live_events/
│       └── __init__.py                  # X01: Authenticated SSE broker, resume cursor, 20 event types
├── tests/
│   ├── test_live_events_x01.py          # X01: SSE tenant isolation, cursor resume & dedup tests
│   └── test_ux_journeys_x03.py          # X03: UX-01..UX-15 backend & Playwright integration suite
└── src/
    ├── App.tsx                          # A0: Root router with React.lazy() code-splitting
    ├── design-system/
    │   ├── tokens.ts                    # G12: Semantic color, spacing, typography & motion tokens
    │   └── primitives.tsx               # G12/G13: StatusBadge, SlaBadge, StageProgress, EmptyState, Drawer, ErrorBoundary
    ├── i18n/
    │   └── translations.ts              # G16: EN / FR / DE UI localization + legal source language guard
    ├── services/
    │   ├── liveEventClient.ts           # X01/G13: Page-visibility-aware SSE client with backoff & dedup
    │   └── privacyOsService.ts          # X02: 7-state API client, cache, draft persistence, zero-POST bootstrap
    ├── features/
    │   ├── navigation/
    │   │   └── WorkspaceNavigation.tsx  # G01/G15: 11-item sidebar, Role switcher, Mobile drawer, Identity badge
    │   ├── home/
    │   │   └── ExecutiveHomeView.tsx    # G02: Executive Home Dashboard, KPI drill-downs, My Priority Work
    │   ├── inbox/
    │   │   └── UnifiedInboxView.tsx     # G03: 7-view Privacy Inbox, keyboard shortcuts, SLA, undo
    │   ├── assessments/
    │   │   └── GuidedAssessmentWizard.tsx # G04: 9-step PIA/DPIA/TIA/TRA/FRIA wizard + draft save/resume
    │   ├── incidents/
    │   │   └── BreachWorkspaceView.tsx  # G05: Incident severity, phases, timeline, human approval routing
    │   ├── rights/
    │   │   └── PrivacyRightsView.tsx    # G06: DSAR 5-stage workflow, JRAE deadlines, redaction & delivery gate
    │   ├── jurisdictions/
    │   │   └── JurisdictionWorkspaceView.tsx # G07: JRAE interactive evaluator + paginated 113-jurisdiction matrix
    │   ├── regulatory/
    │   │   └── RegulatoryIntelView.tsx  # G08: Freshness metadata, legal review queue, live SSE updates
    │   ├── reports/
    │   │   └── ReportsAnalyticsView.tsx # G09: Risks & Controls matrix + Executive & Audit Reports
    │   ├── assistant/
    │   │   └── GovernedAssistantView.tsx # G10: Multi-stage Governed Assistant + verified AI Hub status
    │   ├── onboarding/
    │   │   └── GuidedOnboardingView.tsx # G11: Empty Organization state + 4-step setup wizard
    │   └── search/
    │       └── CommandPaletteModal.tsx  # G14: Cmd+K / Ctrl+K global search & command palette
    └── views/
        ├── PrivacyOSPortal.tsx          # A0: Unified orchestrator shell integrating G01-G16 & X01-X02
        ├── PrivacyInbox.tsx             # G03: Re-exports UnifiedInboxView for route compatibility
        └── HitlQueue.tsx                # G12: Repaired valid TypeScript HITL queue component
```
