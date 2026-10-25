# KIBO Privacy OS — 25-Agent Distributed UX & Live Experience Assignments (`docs/ux/AGENT-ASSIGNMENTS.md`)

**Orchestrator (`A0`):** Antigravity Principal Product Designer, Staff Frontend Architect & Engineering Orchestrator  
**Baseline Tag:** `v2026.10.1` (`e2147b3ec4cc5c6848d2698145f9830d1ae47c20`)  
**Integration Branch:** `ux/v2026.10.1/integration`  
**Worktree Root:** `/tmp/kibo-ux-worktrees/<agent-id>`

---

## 1. Gemini Worker Agents (`G01`–`G16`)

| Agent ID | Role / Workstream | Branch Name | Owned Files | Dependencies |
|---|---|---|---|---|
| `G01` | Information Architecture, 11-Section Navigation & Role Switcher | `ux/v2026.10.1/G01-navigation-ia` | `kibo-is/src/features/navigation/WorkspaceNavigation.tsx` | `A0` contracts |
| `G02` | Executive Home Dashboard & Real KPI Drill-Downs | `ux/v2026.10.1/G02-executive-home` | `kibo-is/src/features/home/ExecutiveHomeView.tsx` | `A0`, `G12` |
| `G03` | Unified Privacy Inbox (7 Views, Keyboard Shortcuts, SLA, Undo) | `ux/v2026.10.1/G03-privacy-inbox` | `kibo-is/src/features/inbox/UnifiedInboxView.tsx`, `kibo-is/src/views/PrivacyInbox.tsx` | `A0`, `G12` |
| `G04` | 9-Step Guided Privacy Assessment Wizard & Draft Persistence | `ux/v2026.10.1/G04-assessment-wizard` | `kibo-is/src/features/assessments/GuidedAssessmentWizard.tsx` | `A0`, `X02` |
| `G05` | Multi-Jurisdictional Breach & Incident Workspace | `ux/v2026.10.1/G05-breach-workspace` | `kibo-is/src/features/incidents/BreachWorkspaceView.tsx` | `A0`, `X02` |
| `G06` | Privacy Rights & 5-Stage DSAR Operational Workflow | `ux/v2026.10.1/G06-dsar-rights` | `kibo-is/src/features/rights/PrivacyRightsView.tsx` | `A0`, `X02` |
| `G07` | Jurisdiction Engine UX & Paginated 113-Jurisdiction Matrix | `ux/v2026.10.1/G07-jurisdiction-ux` | `kibo-is/src/features/jurisdictions/JurisdictionWorkspaceView.tsx` | `A0`, `X02` |
| `G08` | Regulatory Intelligence UI, Freshness Metadata & Review Queue | `ux/v2026.10.1/G08-regintel-ui` | `kibo-is/src/features/regulatory/RegulatoryIntelView.tsx` | `A0`, `X01` |
| `G09` | Risks & Controls Governance + Executive & Audit Reports | `ux/v2026.10.1/G09-reports-analytics` | `kibo-is/src/features/reports/ReportsAnalyticsView.tsx` | `A0`, `G12` |
| `G10` | Governed Assistant Interaction & Verified AI Hub Status | `ux/v2026.10.1/G10-governed-assistant` | `kibo-is/src/features/assistant/GovernedAssistantView.tsx` | `A0`, `X02` |
| `G11` | Empty Organization State & 4-Step Guided Onboarding Wizard | `ux/v2026.10.1/G11-guided-onboarding` | `kibo-is/src/features/onboarding/GuidedOnboardingView.tsx` | `A0`, `G12` |
| `G12` | Shared Design System Primitives, Tokens & `HitlQueue.tsx` Repair | `ux/v2026.10.1/G12-design-system` | `kibo-is/src/design-system/tokens.ts`, `kibo-is/src/design-system/primitives.tsx`, `kibo-is/src/views/HitlQueue.tsx` | `A0` |
| `G13` | Motion, Microinteractions, Stage Progress & Live Activity Feed | `ux/v2026.10.1/G13-motion-feedback` | `kibo-is/src/features/activity/LiveActivityFeed.tsx` | `A0`, `X01`, `G12` |
| `G14` | Global Search & `Cmd+K` / `Ctrl+K` Command Palette | `ux/v2026.10.1/G14-command-palette` | `kibo-is/src/features/search/CommandPaletteModal.tsx` | `A0`, `G01` |
| `G15` | Responsive Mobile/Tablet Layouts & Administration Console | `ux/v2026.10.1/G15-responsive-admin` | `kibo-is/src/features/admin/AdministrationView.tsx` | `A0`, `G01` |
| `G16` | WCAG 2.2 AA Accessibility & `EN`/`FR`/`DE` Localization | `ux/v2026.10.1/G16-a11y-i18n` | `kibo-is/src/i18n/translations.ts` | `A0` |

---

## 2. Codex Worker Agents (`X01`–`X03`)

| Agent ID | Role / Workstream | Branch Name | Owned Files | Dependencies |
|---|---|---|---|---|
| `X01` | Authenticated Live-Event SSE Broker & State Propagation | `ux/v2026.10.1/X01-live-events-sse` | `kibo-is/core/live_events/__init__.py`, `kibo-is/src/services/liveEventClient.ts`, `kibo-is/tests/test_live_events_x01.py` | `A0` |
| `X02` | 7-State API Client, Cache, Draft Persistence & Zero-POST Bootstrap | `ux/v2026.10.1/X02-api-client-reliability` | `kibo-is/src/services/privacyOsService.ts` | `A0` |
| `X03` | `UX-01` through `UX-15` Security, API & Playwright Journey Tests | `ux/v2026.10.1/X03-ux-journey-tests` | `kibo-is/tests/test_ux_journeys_x03.py` | `G01`–`G16`, `X01`–`X02` |

---

## 3. DGX Spark Worker Agents (`D01`–`D02`)

| Agent ID | Role / Workstream | Branch Name | Owned Files | Dependencies |
|---|---|---|---|---|
| `D01` | DGX Spark Local Assistant Latency, Streaming & Stage Evaluation | `ux/v2026.10.1/D01-dgx-assistant-latency` | `kibo-is/core/live_events/dgx_assistant_ux_benchmark.py`, `kibo-is/core/live_events/dgx_d01_ux_results.json` | `X01` |
| `D02` | DGX Spark 1,000-Record Workload & Live-Event Stress Benchmark | `ux/v2026.10.1/D02-dgx-event-stress` | `kibo-is/core/live_events/dgx_event_stress_benchmark.py`, `kibo-is/core/live_events/dgx_d02_ux_results.json` | `X01` |

---

## 4. Claude Independent Review Agents (`C01`–`C04`)

| Agent ID | Role / Workstream | Branch Name | Owned Files | Dependencies |
|---|---|---|---|---|
| `C01` | Independent Usability Review & Nielsen Heuristic Evaluation | `ux/v2026.10.1/C01-heuristic-review` | `docs/ux/reviews/C01-heuristic-evaluation.md` | `G01`–`G16` |
| `C02` | Privacy-Professional Workflows & IA Validation | `ux/v2026.10.1/C02-workflow-ia-review` | `docs/ux/reviews/C02-privacy-workflow-review.md` | `G01`–`G16` |
| `C03` | UX Writing, Legal Terminology & Multilingual Guidance Review | `ux/v2026.10.1/C03-ux-writing-review` | `docs/ux/reviews/C03-ux-writing-review.md` | `G01`–`G16` |
| `C04` | Adversarial Usability, WCAG 2.2 AA Accessibility & Consistency Review | `ux/v2026.10.1/C04-adversarial-a11y-review` | `docs/ux/reviews/C04-adversarial-a11y-review.md` | `G01`–`G16`, `X01`–`X02` |
