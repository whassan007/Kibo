# KIBO.IS — Comprehensive Frontend Architecture, UX & UI Review

**Reviewed:** live site https://kibo.is (all 4 personas, all views, desktop 1428px) + full source audit (`kibo-is/src`, 8,361 lines) — 2026-07-06
**Reviewer stance:** Principal Frontend Engineer / Staff UX / Product Design / Accessibility / Design Systems
**Method note:** desktop visual review is from live navigation; mobile/tablet and WCAG findings are code-derived (layout classes, contrast tokens, ARIA census) and marked for tooling confirmation via GT-7 / axe suites.

---

## 1. EXECUTIVE SUMMARY

KIBO.IS has the right *product shape* — four role-scoped surfaces (CPO Expert, Employee, PSR Committee, Public Widget) that mirror how a privacy office distributes work — and a distinctive, coherent monochrome terminal aesthetic. But it is not enterprise-ready. The deployed build points at an unreachable backend so **every data view renders permanently empty with no error state**; the deployed bundle doesn't match the current source (source uses same-origin API base; production calls a private Tailscale IP — a release-management failure, Baseline R-1). The frontend is a single 3,959-line component holding 96 `useState` hooks with zero ARIA attributes, zero focus styles, `alert()` for error surfacing, and no reusable component layer. The CPO — the daily power user — has no way to answer "what needs my decision right now," which is the product's core promise.

**Verdict: not production-ready. Conditional path: ~6 weeks of focused frontend work (backlog below) reaches enterprise-pilot grade.**

## 2. FRONTEND HEALTH SCORE: **34 / 100**

| Dimension | Score | Driver |
|---|---|---|
| Product/IA fit | 7/10 | Role model is right; navigation is clean |
| UX workflows | 3/10 | Core loops dead-end (empty queue, dead buttons, no feedback) |
| UI consistency | 6/10 | Strong visual language; inline-hex drift across files |
| Design system | 2/10 | No shared components; duplicated patterns everywhere |
| Accessibility | 1/10 | 0 ARIA, 0 `focus:` styles, contrast failures, `alert()` dialogs |
| Responsiveness | 3/10 | Fixed 3-pane %-widths; some grid breakpoints; untested mobile |
| Performance | 5/10 | Small app, but 10s polling + monolith re-renders everything |
| Architecture | 2/10 | 3,959-line App.jsx, 96 useState, no router, no state layer |
| Resilience | 2/10 | Silent empty states; deployed URL defect; no retry/offline UX |
| Enterprise capability | 2/10 | No shortcuts, bulk ops, saved views, audit visibility, personalization |

---

## 3. PAGE-BY-PAGE REVIEW

### 3.1 Dashboard (Expert/CPO)
**Purpose:** command center for active FIPPA assessments + statutory audits. **User:** CPO. **Workflow:** "what needs me today."
- Renders two headings and two buttons; assessment list permanently empty in prod (backend unreachable) with *no* empty/error/loading distinction — a CPO cannot tell "no work" from "system down." (R-2, R-5)
- "Run Activities Audit" and "SOC 1 / SOC 2 Assessment" produce no visible result, no spinner, no toast — dead-feeling controls. GT-7 persona crawl must fail on no-op buttons.
- Missing entirely: KPI strip (pending decisions, SLA breaches, overdue training), deadline countdowns, trend sparklines, drill-down. The lifecycle/kanban view from the v2.0 spec is absent.
**Top fixes:** empty/error/loading triad; decision-queue KPI header with click-through; make audit buttons async jobs with progress + completion toast.

### 3.2 Privacy Inbox (Expert)
**Purpose:** triage privacy requests. **Workflow:** select → review → act.
- Detail pane placeholder is good ("Select an email…"), but the list column renders nothing when empty — no empty state, no "connect mailbox" onboarding, no manual-create action. The primary workflow cannot start.
- No filters, search, sort, tags, or SLA indicators specified anywhere in the view.
- 533-line `PrivacyInbox.jsx` uses its own color system (`#1E294B`, `#0E1325`) — visually divergent from App.jsx tokens.
**Top fixes:** designed empty state with primary action; list virtualization + filter bar (status/statute/SLA); unify tokens.

### 3.3 Meetings Planner (Expert / PSR)
**Best view in the app.** Create-meeting form, minutes/action-items pane, 9 working commissioner-library links.
- Form defects: no validation (submits with empty date), no required-field marks, placeholder-as-help in agenda textarea, no success feedback, meeting type only 2 options, no attendees/recurrence. Date input is native and unstyled against the dark theme.
- "Upcoming & Past Meetings" renders nothing when empty (no empty state).
- Action items can't be assigned, dated, or linked to risks — minutes become dead text.
**Top fixes:** validation + inline errors + success toast; empty state; action-item assignee/due-date chips linked to the queue.

### 3.4 Training Admin (Expert)
- Stuck on "Loading compliance data..." forever — a loading state that never resolves is worse than an error state. (R-2/R-5)
- "Reset & Assign Courses" and "Send Overdue Reminders" are destructive/bulk actions with **no confirmation dialog, no scope preview, no undo**.
- Missing: per-employee completion table (sortable, filterable, exportable), course catalog, evidence export for auditors.

### 3.5 Onboarding Checklist (Expert)
- **Completely blank view** — no heading, no content, no empty state. Ship a skeleton + "coming soon" card or remove from nav. Blank nav destinations destroy trust in the whole product.

### 3.6 Employee Mode
- Strongest role-fit. Data-inventory contribution form asks exactly the right 5 questions.
- Defects: no validation; free-text retention ("e.g. 5 years") invites garbage — use structured duration picker; "Submit to Central Inventory" gives no confirmation, no reference ID, no "my submissions" history (silent-send, same class as R-5); no draft/auto-save.
- "My Assigned Compliance Risks: No risks currently assigned" — good, the only real empty state in the app; replicate this pattern everywhere.
- Missing: **report-an-incident action** — the single most important employee privacy task; training section renders nothing.

### 3.7 PSR Committee Member
- Advisory materials with Download/View is useful; Risk Advisory Queue is an empty region with no explanation.
- A committee member's job is to *record an opinion* — there is no approve/comment/escalate control anywhere. The persona is read-only, which makes it a document folder, not a workflow.
- No versioning/review-status on materials; no link between PSR meetings (plannable in 3.3) and materials here.

### 3.8 Public Widget (citizen-facing — legally exposed surface)
- Clean layout, correct statute framing (FIPPA / IPC / 30-day clock), good shortcode embed story.
- **Critical:** submit posts to an unreachable backend → the request silently vanishes. For a legally-clocked FOI request this is a liability, not a bug. Submit must be blocked with a visible outage notice when the API is down. (R-1/R-2/R-5, GT-8)
- No identity verification step, no email confirmation loop, no consent notice/checkbox (GT-8 requires zero-cookie + consent logging), no file-number persistence for the tracker, no CAPTCHA/rate-limit UX.
- Form: no validation, no required marks, placeholder-only labels on tracker input, no keyboard-visible focus.
- Jurisdiction selector (globe) is an **empty dropdown**; footer statute block is hardcoded FIPPA while the widget advertises `jurisdiction="ontario"` configurability.

---

## 4. UX FINDINGS (cross-cutting)

1. **No feedback loop anywhere.** No toasts, no optimistic UI, no progress indicators; errors via `alert()` (15 call sites). Every mutation feels like a void. — Critical
2. **Empty ≠ error ≠ loading.** One real empty state exists (employee risks). Everything else renders blank or spins forever. Define the triad per view and test it (Frontend Resilience Rule 2). — Critical
3. **The CPO has no queue.** The HITL decision loop (the product's differentiator) has no UI surface: no pending count, no SLA sort, no decision block (approve/always/flag/defer/reject from the spec). — Critical
4. **Workflows dead-end.** Employee submits inventory → no visibility; PSR reads docs → can't respond; CPO runs audit → nothing returns. Close every loop with a visible artifact (reference ID, status row, toast + queue entry). — High
5. **No onboarding/guidance.** First-run of any persona gives no orientation; no tooltips (`title=` count: 0 meaningful), no keyboard-shortcut help. — Medium
6. **Role switcher is a dropdown** — great for demo, but personas share one SPA state; switching mid-task silently discards context. Gate persona behind auth (R-9) and preserve per-persona view state. — High

## 5. UI FINDINGS

1. **Two competing palettes.** Live site is near-black terminal + amber accent; source files carry light-theme grays (`#E5E7EB` ×270, `#111827`, `#6B7280`) and PrivacyInbox has its own navy family (`#1E294B`, `#0E1325`). Consolidate to design tokens (CSS variables) with ONE semantic scale: bg/surface/border/text-primary/text-secondary/accent/danger/success. — High
2. **Secondary text contrast:** `#767676`-class grays on near-black fail WCAG 4.5:1 for 11–12px text (spec §5.1 tokens as written fail their own accessibility bar). Bump to ≥ #9A9A9A or enlarge text. — High
3. **Status color semantics missing:** priority/status communicated by borders and casing only; amber is the sole accent. Define danger/success/warn tokens even within monochrome discipline (e.g., inverse-fill for danger, hatched for warn). — Medium
4. **Typography:** monospace-everywhere aids the terminal aesthetic but hurts scanability of prose (advisory materials, meeting minutes). Use sans for body content, mono for IDs/payloads/telemetry (spec §5.2 already says this — implementation ignores it). 10–11px labels are below comfortable minimums. — Medium
5. **Density without hierarchy:** section headers (`// UPPERCASE`) are the only level; cards/tables/forms share identical border weight so nothing is visually primary. Introduce 2-tier surface elevation via border weight/fill (no shadows needed). — Medium

## 6. DESIGN SYSTEM ASSESSMENT

None exists. Every button, card, field, and badge is hand-rolled inline per usage; PrivacyInbox/UserGovernanceCockpit/AdminDashboard/ComplianceCoverageMap each re-implement panels and lists.
**Build a 12-component library first (this unblocks everything else):** `Button` (primary/secondary/danger/disabled+loading), `Panel/Card`, `SectionHeader`, `Field` (label+input+error+help), `Select`, `DataTable` (sort/filter/paginate/sticky header/export), `Tag/Badge`, `Toast`, `ConfirmDialog`, `EmptyState`, `Skeleton`, `CountdownChip` (SLA). Extract design tokens to `tokens.css`. Every recommendation below assumes these exist.

## 7. NAVIGATION ASSESSMENT

Sidebar (5 items + persona switcher + jurisdiction globe) is clear at desktop. Gaps: no active-route deep-linking (no router — one SPA state var, so refresh loses location, cannot share links, no browser back), no breadcrumbs for drill-ins (none exist yet), empty jurisdiction dropdown is dead UI in the global header, no keyboard nav or `⌘K` command palette (enterprise power users). **Adopt react-router with URL-per-view+persona as a prerequisite for everything else.** — High

## 8. FORMS ASSESSMENT

Every form (meeting create, inventory contribution, FOI submit, FOI tracker, reasoning textarea): no validation, no required indicators, placeholder-as-label, no inline errors, no success confirmation, no draft/auto-save, no keyboard flow audit, labels present (26 `<label>`) but unassociated (no `htmlFor`). Standardize on one `Field` component + zod/yup schema validation + per-form success toast + draft persistence (localStorage is fine here — it's the user's own browser).

## 9. TABLES & DATA GRIDS

9 `<table>` in App.jsx + 2 in AdminDashboard: static markup, no sorting/filtering/pagination/virtualization/export/bulk selection anywhere. For CPO scale (hundreds of transactions/DSARs) this fails immediately. One `DataTable` with server-side sort/filter/paginate covers Inbox, Training roster, Queue, and vendor lists (M5).

## 10. DASHBOARD ASSESSMENT

No KPIs, charts, trends, or drill-downs exist. Minimum enterprise bar: pending-decisions count (click → queue), SLA-at-risk count with worst-case countdown, DSARs by status funnel, training completion %, 30-day intake sparkline. All available from existing endpoints once M10 lands; design now, bind later.

## 11. ACCESSIBILITY REPORT (WCAG 2.2 AA)

Code census: **0 `aria-` attributes, 0 `focus:` styles, 0 skip links; 15 `alert()`; labels unassociated; icon-only buttons unlabeled; div-click rows (inbox cards) not keyboard-reachable.**
Violations (fix order): (1) keyboard operability of all interactive divs → real `<button>`/`<a>` — 2.1.1; (2) visible focus indicators (amber 2px outline fits the aesthetic) — 2.4.7; (3) contrast for secondary text and 10px labels — 1.4.3; (4) form label association + error `aria-describedby` — 3.3.x; (5) heading hierarchy (h1 per view, section h2s) — 1.3.1; (6) replace `alert()` with accessible toast/dialog (`role="alert"`, focus trap) — 4.1.3; (7) semantic landmarks (`nav/main/aside`) — 1.3.1. Public Widget must reach AA first — it's citizen-facing and statutory. Gate CI with axe (zero serious/critical) per GT-7.

## 12. RESPONSIVE DESIGN

Fixed `w-[15%]/w-[55%]/w-[30%]` three-pane grid with only 40 responsive utility usages (mostly `grid-cols`): at 390px the panes become unusable slivers; native date input and 10px mono text compound it. Public Widget is the only surface where mobile is mandatory (citizens) — make it fully responsive first (single column, 44px touch targets); Expert console can declare 1280px minimum with a graceful "use desktop" notice at tablet, then adaptive drawer-based panes later. *(Code-derived — confirm with GT-7 viewport matrix.)*

## 13. PERFORMANCE

Monolith App.jsx re-renders wholesale on every keystroke (96 state hooks, no memoization); 10s polling refetches even when tab hidden (pause via `visibilitychange`, don't block main thread — Resilience Rule 1); no code splitting (one bundle for 4 personas — lazy-load per persona); no `React.Suspense`/skeletons; JSON tree in inspector re-parses `raw` every render. None of this is fatal at current data volume; all of it is fatal at enterprise volume. Fix alongside the architecture split below.

## 14. FRONTEND ARCHITECTURE

- **App.jsx = 3,959 lines, 96 useState, 3 useEffect, 6 fetch sites.** Split: `views/` per persona-view, `components/` (design system), `hooks/` (`useKiboQuery` wrapping kiboFetch with retry/backoff/online-state), `state/` (Zustand — already proven in cockpit).
- **kiboFetch is a good seed** (scope header, online flag) but drops response-status handling: non-2xx currently flows through as success → empty arrays (Baseline R-5). Add `if (!res.ok) throw` + typed error envelope.
- **Deploy-sync defect:** live bundle calls `http://100.113.62.112:8000`; current source uses same-origin. The fix exists in source but isn't deployed — add build-stamp display (`v1.1.0+sha`) in the sidebar footer and a CI check comparing deployed hash to main. (R-1)
- **TS migration:** `kibo-is-frontend/` (TypeScript twin) is the strategic home — do the component-library work THERE, not in the JSX legacy, and port views incrementally.

## 15. TECHNICAL DEBT REGISTER

| Item | Impact | Effort |
|---|---|---|
| App.jsx monolith split | High (velocity, re-renders, testability) | L |
| No router / URL state | High (sharing, back button, tests) | M |
| Inline hex → tokens | Medium (theming, consistency) | S |
| alert() + silent failures | High (trust, a11y) | S |
| Duplicate panels across 5 files | Medium | M |
| Deployed bundle ≠ source | Critical (release integrity) | S |
| Zero component tests | High (regressions invisible) | M (start with design-system lib) |

## 16. ENTERPRISE READINESS

Missing for daily enterprise use: keyboard shortcuts (j/k queue nav, a/r decisions, ⌘K palette), bulk operations (multi-select approve/defer), saved views/filters, per-user personalization, audit visibility in-UI (who decided what, when — data exists in backend audit chain), notification center (M8 has no frontend surface), session management/re-auth UX (blocked on R-9), export everywhere (CSV for auditors). None are XL items once DataTable + router + state layer exist.

---

## 17. PRIORITIZED RECOMMENDATION BACKLOG

Format: Title · Category · Priority · Effort · (test hook)

**CRITICAL**
1. Block/queue Public Widget submits when API is down; visible outage notice; never lose a citizen request · UX/Resilience · S · (GT-8, S1)
2. Empty/loading/error triad on every view; kill infinite "Loading…" · UX · M · (GT-7 states matrix)
3. Fix deployed-bundle drift: env-based API base actually shipped; build stamp in footer; CI hash check · Architecture/DevOps · S · (R-1 regression)
4. `kiboFetch`: throw on non-2xx; global error toast; retry with backoff · Architecture · S · (R-5 regression, S1)
5. CPO Decision Queue surface: pending list + SLA countdown + 5-action decision block wired to `/api/transactions/{id}/decision` · UX/Product · L · (new GT: HITL loop)

**HIGH**
6. Design-token extraction + 12-component library (in TS twin) · Design System · L
7. React Router: URL per persona+view; preserve state per persona · Architecture · M · (GT-7 deep-link cases)
8. Keyboard + focus pass: real buttons, focus rings, skip link, form label association · Accessibility · M · (axe CI gate)
9. Public Widget AA + mobile: single-column responsive, consent notice + logging, email confirmation, reference-ID persistence · Accessibility/UX · L · (GT-8)
10. Form framework: validation, required marks, inline errors, success toasts, drafts · Forms · M
11. Confirmation dialogs on bulk/destructive actions (training reset/reminders) · UX · XS
12. Close employee loop: submission → reference ID + "my submissions" list; add Report-an-Incident action · UX/Product · M
13. Populate jurisdiction selector from `/api/jurisdictions` (endpoint exists in source!) and bind footer statute block to it · UX · S

**MEDIUM**
14. PSR opinion workflow: approve/comment/escalate on queue items + material version status · Product · M
15. DataTable rollout: Inbox, Training roster, Queue (sort/filter/paginate/export) · Tables · M
16. Dashboard KPI strip with drill-through · Dashboard · M
17. Typography: sans for prose, mono for data; raise 10px floors to 12px · UI · S
18. Contrast fixes for secondary text (≥4.5:1) · Accessibility · XS
19. Pause polling when tab hidden; per-view query caching · Performance · S
20. Blank Onboarding Checklist: skeleton + content or remove from nav · UX · XS

**STRATEGIC (1–3 months)**
21. Complete TS migration of Expert console into kibo-is-frontend using the component library · Architecture · XL
22. Command palette + shortcut system + saved views · Enterprise UX · L
23. Notification center (M8 frontend) + audit-trail visibility per record · Enterprise UX · L
24. Lifecycle kanban (10-phase board from v2.0 spec) · Product · XL

## 18. QUICK WINS (< 1 day each)
#3 build stamp, #4 kiboFetch throw+toast, #11 confirm dialogs, #13 jurisdiction bind, #18 contrast bump, #20 blank view fix, focus-ring CSS (part of #8), disable widget submit on offline flag (part of #1).

## 19. HIGH-IMPACT (< 1 week)
#2 state triad, #5 minimal queue list (even before full decision block), #7 router, #10 form validation on the two public-facing forms, #12 employee loop closure.

## 20. STRATEGIC (1–3 months)
#6 + #21 component library & TS migration, #22–24, plus the accessibility CI gate expansion across all personas.

---

*Every numbered item above should land with its test hook per `spec/ANTIGRAVITY_TESTING_PROMPT.md` (xfail-strict where the fix isn't merged yet). The GT-7 persona crawl + axe suite is the standing verification that this report's fixes stay fixed.*
