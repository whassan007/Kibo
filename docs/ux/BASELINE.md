# KIBO Privacy OS — UX, Usability & Live Experience Baseline Audit (`Phase 0`)

**Baseline Tag:** `v2026.10.1` (`commit e2147b3ec4cc5c6848d2698145f9830d1ae47c20`)  
**Hardening Baseline Commit:** `a52a8ad` (`hardening/v2026.10.1/integration`)  
**UX Integration Branch:** `ux/v2026.10.1/integration`  
**Audit Date:** 2026-10-25  
**Browser Automation Engine:** Headless Chromium `145.0.7632.6` (Playwright)  
**Baseline Screenshots Directory:** [`docs/ux/screenshots/before/`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before)

---

## 1. Empirical Baseline Measurements (`docs/ux/baseline_metrics.json`)

| Metric | Baseline Value (`v2026.10.1`) | Root Cause / Observation |
|---|---|---|
| **Single JS Bundle Size** | `776,692 bytes` (`776.69 kB` raw / `194.63 kB` gzip) | Eagerly bundles both `PrivacyOSPortal.tsx` (`1,959` lines), `privacyOsService.ts` (`2,069` lines), and `src/legacy/App.jsx` (`1,172` lines) into one chunk with zero `React.lazy()` code-splitting. |
| **CSS Bundle Size** | `105,921 bytes` (`105.92 kB` raw / `16.59 kB` gzip) | Single stylesheet without structured design-system semantic tokens for light/dark themes. |
| **Initial Page Load (`/privacy-os`)** | `641.34 ms` (`FCP: 132 ms`, `DOM nodes: 903`) | Mounts an 8-endpoint `Promise.all` bootstrap on initial render, waiting on 5 `POST` calls and 3 `GET` calls before hydrating state. |
| **Unsolicited `POST` Mutations on Page Mount (`UX-15` Violation)** | **5 automatic `POST` requests on mount:**<br>1. `POST /api/v1/compliance/applicability/evaluate`<br>2. `POST /api/v1/office/incidents`<br>3. `POST /api/v1/office/assessments/recommend`<br>4. `POST /api/v1/office/rights/evaluate-request`<br>5. `POST /api/v1/office/assistant/query` | Simply opening `/privacy-os` in a browser triggers `POST /api/v1/office/incidents`, which creates a persistent breach incident record (`inc_*`) in the backend! |
| **Editable Identity Header Inputs (`UX-08` Violation)** | `hasEditableTenantHeaderInput: true`<br>`hasEditableUserHeaderInput: true` | [`PrivacyOSPortal.tsx:472-487`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/views/PrivacyOSPortal.tsx#L472-L487) renders raw `<input aria-label="X-Tenant-ID">` and `<input aria-label="X-User-ID">` fields allowing users to edit headers directly in the top bar. |
| **Silent Synthetic Offline Fallback (`UX-07` Violation)** | `apiRequestWithFallback` catches all network/HTTP errors and returns synthetic evaluation, incident, DSAR, and assistant objects | When the backend is unreachable, `FALLBACK_INTEGRATION_STATUS` still reports `status: 'connected'` for Microsoft 365 Copilot, Claude MCP, and Gemini Enterprise (`privacyOsService.ts:1909-1961`). |
| **Tab Switch Latency** | `168.42 ms` – `194.46 ms` | Large un-virtualized lists (all 113 jurisdictions rendered simultaneously) and monolithic state re-renders inside `PrivacyOSPortal.tsx`. |

---

## 2. Inventory of Active, Duplicated, Broken, and Legacy Frontend Code

| Path | Lines / Size | Status | Action Plan |
|---|---|---|---|
| [`kibo-is/src/views/PrivacyOSPortal.tsx`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/views/PrivacyOSPortal.tsx) | `1,959 lines` (`102 kB`) | **ACTIVE — MONOLITHIC & DEFECTIVE** | Refactor into modular role-aware workspace shell with 11 task-oriented navigation sections (`Home`, `Inbox`, `Assessments`, `Incidents`, `Privacy Rights`, `Data & Vendors`, `Regulatory Intelligence`, `Risks & Controls`, `Reports`, `Assistant`, `Administration`) while preserving backward-compatible tabs/test hooks. |
| [`kibo-is/src/services/privacyOsService.ts`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/services/privacyOsService.ts) | `2,069 lines` (`100 kB`) | **ACTIVE — SILENT FALLBACK DEFECT** | Replace silent fallback with explicit 7-state `OperationalDataEnvelope` (`live`, `updating`, `stale`, `offline`, `demo`, `error`, `unverified`), verified profile/organization switcher, request cancellation, and local draft persistence. Never report AI hubs as `connected` when offline. |
| [`kibo-is/src/App.tsx`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/App.tsx) | `18 lines` | **ACTIVE — SUBOPTIMAL ROUTING** | Route `/` to the unified KIBO Privacy OS workspace (`PrivacyOSPortal`) with route-based lazy loading for `/legacy/*` so initial bundle size drops dramatically. |
| [`kibo-is/src/views/PrivacyInbox.tsx`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/views/PrivacyInbox.tsx) & [`src/components/inbox/*`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/components/inbox/DataRow.tsx) | `148 lines` + 6 stub files (`33–93 bytes` each) | **INCOMPLETE STUB** | Integrate a full, unified Privacy Inbox (`G03`) into the main workspace with views (`Assigned to me`, `Unassigned`, `Needs review`, `Awaiting approval`, `Overdue`, `Recently completed`, `All permitted cases`), SLA badges, keyboard shortcuts (`j`/`k`/`/`/`a`/`f`), server-confirmed mutations, and undo support. |
| [`kibo-is/src/views/HitlQueue.tsx`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/views/HitlQueue.tsx) | `326 lines` | **BROKEN / ORPHANED** | Starts with a markdown fence ```` ```tsx ```` on line 1 and imports non-existent `@kibo/shared-components/*`. Repair into valid TypeScript using our unified design system. |
| [`kibo-is/src/legacy/App.jsx`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/legacy/App.jsx) | `1,172 lines` | **LEGACY — SIMULATED TELEMETRY** | Contains hardcoded fake agent telemetry (`cpu: '68%'`, `cost: '$0.015'`) and simulated logs. Isolate behind lazy route `/legacy/*` and clearly badge as Legacy Reference Archive. |
| `cockpit/` & `kibo-is-frontend/` | Duplicate directories | **DUPLICATE ARCHIVES** | Documented as legacy standalone copies; `kibo-is/` is the canonical production frontend served by FastAPI (`agent_gateway.py`) and built into `kibo-is/dist/`. |

---

## 3. Baseline Screenshots Captured

All 7 baseline screenshots were captured via headless Chromium at `1440×900` before any UX modifications:
1. [`docs/ux/screenshots/before/00_legacy_root_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/00_legacy_root_before.png)
2. [`docs/ux/screenshots/before/01_jrae_tab_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/01_jrae_tab_before.png)
3. [`docs/ux/screenshots/before/02_breach_war_room_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/02_breach_war_room_before.png)
4. [`docs/ux/screenshots/before/03_assessments_dsar_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/03_assessments_dsar_before.png)
5. [`docs/ux/screenshots/before/04_coverage_matrix_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/04_coverage_matrix_before.png)
6. [`docs/ux/screenshots/before/05_ai_hubs_assistant_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/05_ai_hubs_assistant_before.png)
7. [`docs/ux/screenshots/before/06_regulatory_intelligence_before.png`](file:///Users/wael/Code/iCloudCode/kibo.is/docs/ux/screenshots/before/06_regulatory_intelligence_before.png)
