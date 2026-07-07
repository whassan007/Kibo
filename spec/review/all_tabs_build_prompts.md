# KIBO — Per-Tab Build Orders (local fleet only)

One paste-ready work order per tab/view. Same shape as the Privacy Inbox order:
build INTO `kibo-is-frontend` (TS twin) using the shared component library; env
API base only (R-1); typed errors on non-2xx (R-5); loading/empty/offline states
(R-2); no `alert()`; sentence case; two font weights. Every mutating action gives
visible feedback + audit reference.

**NO CLOUD MODELS.** Local Ollama only — Mac `127.0.0.1:11434`
(`gemma4:latest`, `qwen3-coder:latest`), DGX `waelbot:11434` (everything else).
`nemotron-3-super:cloud` is BANNED — use `:latest`. Settings: temperature 0.0,
`num_ctx` 32768.

## Source map (real files/endpoints — reference, don't invent)

| Tab | Persona/host | Legacy file | Endpoints (existing) |
|---|---|---|---|
| Meetings Planner | Expert/PSR · App.jsx | App.jsx `meetings` | `/api/expert/meetings`, `/api/psr/meetings` |
| Training Admin | Expert · App.jsx | App.jsx `training_admin` | `/api/expert/training/compliance`, `/api/expert/training/{...}` |
| Employee Mode | Employee · App.jsx | App.jsx (employee) | `/api/employee/{id}/risks|training|inventory` |
| PSR Committee | PSR · App.jsx | App.jsx (psr) | `/api/psr/risk-queue`, `/api/psr/risk/{id}`, `/api/psr/meetings` |
| Authoritative Sources | Admin · AdminDashboard.jsx | tab `source_viewer` | `/api/sources` |
| Trust Tiers | Admin · AdminDashboard.jsx | tab `trust_tiers` | (none — add `/api/trust/tiers`) |
| HITL Governance Queue | Admin · AdminDashboard.jsx | tab `hitl` | `/api/transactions`, `/api/transactions/{id}/decision` |
| Deployment Center | Admin · AdminDashboard.jsx | tab `deployment` | (add `/api/deploy/ladder`, `/api/deploy/{step}/gate`) |
| UX Telemetry | Admin · AdminDashboard.jsx | tab `telemetry` | (add `/api/telemetry/feedback`) |
| Compliance Coverage Map | Admin · ComplianceCoverageMap.jsx | that file | `/api/compliance/coverage`, `/api/compliance/gaps/create_task` |
| Compliance Net Ontology | Admin · OntologyVisualizer.jsx | that file | `/api/ontology/export`, `/api/ontology/import` |

**Fleet split:** interactive CRUD tabs → `qwen3-coder:30b`; data-viz/graph tabs
(map, ontology, telemetry) → `gpt-oss:120b` (better at D3/canvas); backend
additions → `devstral:24b`; tests → `coder-core`. Run 2–3 per DGX slot. For each
tab: design brief FIRST (write `spec/review/tabs/<tab>.md`), then FE, then BE if
new endpoints, then tests. The design brief prompt below is generic; the
per-tab prompt fills the specifics.

---

## GENERIC DESIGN-BRIEF PREAMBLE (prepend to every FE order)
```
Read spec/review/kibo_is_frontend_ux_review.md and
spec/review/privacy_inbox_redesign_spec.md (follow that quality bar and state
model exactly). Build in kibo-is-frontend/src using the shared component library
(Button, Panel, SectionHeader, Field, Select, DataTable, Tag, Toast,
ConfirmDialog, EmptyState, Skeleton, OfflineBanner, SlaBadge). Legacy JSX is
reference ONLY — never copy its inline hex, alert(), or silent fetch. API base
from VITE_API_BASE; non-2xx throws typed error; offline disables mutations and
preserves unsent input. Deliver loading/empty/error states reachable via props.
Definition of done: npm run build + npm run lint pass; renders with a
fixtures/<tab>.ts mock file.
```

---

## WO-A · MEETINGS PLANNER — FE `qwen3-coder:30b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/MeetingsPlanner.tsx replacing App.jsx 'meetings'.
Purpose: CPO/PSR schedule + run compliance meetings, capture minutes/actions.
FE:
- Create-meeting form via Field/Select: date (styled date-time picker, not raw
  native), meeting type (Weekly Privacy & Security / PSR Committee / ad-hoc),
  attendees (multi-select of roles), recurrence, agenda items (repeatable rows).
  Full validation: no submit with empty date; required marks; inline errors;
  success toast with meeting ref.
- Meetings list (DataTable): upcoming/past, sortable by date, status column,
  click → detail pane with minutes editor + action-item rows (assignee, due
  date, linked risk id) that POST into the transaction/queue pipeline so an
  action item becomes tracked work — not dead text.
- Commissioner research libraries: keep the 9 working links, render as a
  labeled resource list component (not inline anchors).
- States: empty ("No meetings scheduled" + Create CTA); loading skeleton;
  offline banner.
GT-5 is the target thread (schedule -> context retrieval -> summary).
BE (devstral): extend /api/expert/meetings + /api/psr/meetings with POST
(create), GET detail, PATCH minutes, POST action-item (routes into intake).
Action items append to audit trail. No sync sqlite in async handlers (R-3 —
mark TODO if unavoidable). Errors return {detail} 4xx (R-5).
TEST HOOK: GT-5, S1, R-2, R-5.
```

## WO-B · TRAINING ADMIN — FE `qwen3-coder:30b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/TrainingAdmin.tsx replacing App.jsx 'training_admin'.
Fixes the "Loading compliance data…" infinite-spinner defect (R-2/R-5).
FE:
- Org compliance metric cards (completion %, overdue count, at-risk employees)
  bound to /api/expert/training/compliance; NEVER an infinite spinner — resolve
  to data, empty, or error.
- Per-employee roster DataTable: name, role, course, status, due date; sort/
  filter/search/export CSV (auditor need).
- Bulk actions "Reset & Assign Courses" and "Send Overdue Reminders" MUST open
  a ConfirmDialog with scope preview ("assign 3 courses to 42 employees") and
  return an audit ref; no fire-and-forget (these are destructive/mass actions).
- States triad; offline disables the two bulk buttons.
BE: GET /api/expert/training/compliance returns {metrics, roster}; POST
/api/expert/training/assign and /reminders take an explicit id list, append
audit, return {affected, audit_ref}.
TEST HOOK: GT-7, S1, R-2, R-5; confirm-dialog g
on bulk actions is a named frontend test.
```

## WO-C · EMPLOYEE MODE — FE `qwen3-coder:30b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/EmployeeHome.tsx (persona 'employee').
FE three sections:
1. My assigned compliance risks (DataTable, empty state already good — keep it).
2. Role-based training (FIPPA track): course cards with launch + completion
   status bound to /api/employee/{id}/training.
3. Data inventory contribution form: system name, data types (chips), purpose,
   retention (STRUCTURED duration picker, not free text), third-party sharing.
   On submit → confirmation with reference ID + append to a "My submissions"
   list (closes the silent-send loop). Draft auto-save to localStorage.
4. ADD a "Report an incident" primary action (currently missing — highest-value
   employee task): minimal form (what happened, systems, data types, when) →
   creates an incident that surfaces in the Expert HITL queue.
BE: employee inventory POST returns ref + persists; new POST
/api/employee/{id}/incident creates incident + routes to queue. R-5 error shape.
TEST HOOK: GT-4/GT-7, S1, R-2, R-5.
```

## WO-D · PSR COMMITTEE — FE `qwen3-coder:30b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/PsrCommittee.tsx (persona 'psr').
FE:
- Advisory review materials: resource list (download/view) with version + review
  status badges bound to material metadata.
- Risk Advisory Queue (DataTable) bound to /api/psr/risk-queue: each item opens
  a decision pane where a committee member RECORDS AN OPINION — approve /
  request-changes / escalate / comment — with a reasoning field. This is the
  missing workflow; today the persona is read-only. Decisions POST to
  /api/psr/risk/{id} and append to audit + feed GT-2 (HITL/self_improvement).
- Link PSR meetings (from WO-A) to the materials shown here.
- States triad; offline disables opinion submission.
BE: POST /api/psr/risk/{id}/opinion {decision, reasoning} -> audit_ref;
feeds self_improvement ingestion. R-5 errors.
TEST HOOK: GT-2, S1, R-2, R-5.
```

## WO-E · AUTHORITATIVE SOURCES — FE `qwen3-coder:30b`
```
[PREAMBLE]. Build views/AuthoritativeSources.tsx replacing AdminDashboard
'source_viewer'. Purpose: registry of source-of-truth legal documents + diff
comparator (EDPB guidelines, Law 25 text, commissioner bulletins).
FE: searchable/filterable DataTable of sources (title, jurisdiction, type,
version, last-checked) bound to /api/sources; row → side-by-side diff viewer
(previous vs current version) with changed clauses highlighted; "route to Phase
1 / create task" action for material changes (ties to horizon-scanning). This is
where R-6 (ontology integrity) surfaces in UI: show each source's provenance +
last verified timestamp. States triad; offline read-only.
TEST HOOK: S1, R-2; GT-1 (feeds ontology onboarding). Diff-render correctness is
a named frontend test with a 2-version fixture.
```

## WO-F · TRUST TIERS — FE `qwen3-coder:30b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/TrustTiers.tsx replacing AdminDashboard 'trust_tiers'.
Purpose: show/govern the autonomy/deployability ladder — which agent actions are
auto-allowed vs require human sign-off, per trust tier (maps to .kibo grants +
deployability ladder). FE: tier cards (tier name, allowed action scopes, gate
type human/auto, current agents at this tier); promote/demote controls behind a
ConfirmDialog (autonomy expansion is a governed, audited action — .kibo boundary
#5). Bind to a NEW endpoint (BE below). States triad.
BE (devstral): GET /api/trust/tiers (from .kibo/state/autonomy/grants.json +
deployability/ladder.json — validate grants before returning, R-6 discipline);
POST /api/trust/tiers/{agent}/promote {reason} -> audit_ref, routes autonomy
change to judgment queue (never silent). R-5 errors.
TEST HOOK: GT-6 (privilege change must be authorized+audited), S1, R-2, R-9.
```

## WO-G · HITL GOVERNANCE QUEUE — FE `qwen3-coder:30b` (BE mostly exists)
```
[PREAMBLE]. Build views/HitlQueue.tsx replacing AdminDashboard 'hitl'. This is
the product's core loop — give it first-class treatment.
FE: queue DataTable bound to /api/transactions (pending only), sorted by SLA,
with priority/jurisdiction/agent columns and a live SLA countdown (SlaBadge
bound to real deadline data, never client clock). Row → decision pane with the
enriched intake derivation VISIBLE (active_frameworks, mandated_controls,
mandated_artifacts from the ontology router) + the 5-action decision block:
Approve now / Approve always (expands reasoning field → trains rule engine) /
Flag to legal / Review later / Reject. POST /api/transactions/{id}/decision.
Show the SHA-256 audit receipt after a decision. States triad; offline disables
decisions (never lose a HITL commit).
TEST HOOK: GT-2 + GT-3 (derivation visible, confidence/citations), S1, R-2, R-5.
```

## WO-H · DEPLOYMENT CENTER — FE `gpt-oss:120b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/DeploymentCenter.tsx replacing AdminDashboard
'deployment'. Purpose: the W-Method 7-layer deployment flow (Attract→Acquire→
Diagnose→Agree→Install→Operate→Compound) with human gates.
FE: horizontal 7-stage flow (use the shared design tokens; each stage = card
with status, gate_type human/auto, current asset); stages with gate_type=human
show a "sign off" action behind ConfirmDialog that routes to the judgment queue.
Bind to NEW endpoints. States triad; offline read-only.
BE (devstral): GET /api/deploy/ladder (from .kibo/config/deployment-flow.yaml +
state); POST /api/deploy/{step}/gate {decision, reason} -> audit_ref, human gate
routes to judgment queue. R-5 errors, R-6 write discipline.
TEST HOOK: GT-6, S1, R-2.
```

## WO-I · UX TELEMETRY FEEDBACK — FE `gpt-oss:120b`, BE `devstral:24b`
```
[PREAMBLE]. Build views/Telemetry.tsx replacing AdminDashboard 'telemetry'.
Purpose: operator dashboard of UX/feedback signals feeding self-improvement.
FE: metric cards + charts (Chart.js from CDN allowlist) — feedback volume, agent
suggestion accept/override rate, view-level friction; time-range selector
(30/90/365d); anomaly flags. Bind to NEW /api/telemetry/feedback. Charts must
render the SAME numbers the API returned (no client recompute drift). Respect
Resilience Rule 1: polling must not block main thread (use visibilitychange to
pause when hidden). States triad.
BE (devstral): GET /api/telemetry/feedback?range= -> {series, cards, anomalies}
from feedback/log + evals/scores. Read-only. R-5 errors.
TEST HOOK: GT-7, S1, R-2; dashboard-number==API-number is a named test.
```

## WO-J · COMPLIANCE COVERAGE MAP — FE `gpt-oss:120b`, BE `devstral:24b`
```
[PREAMBLE]. Refactor ComplianceCoverageMap.jsx into
kibo-is-frontend views/ComplianceCoverageMap.tsx (1063 lines → split into map +
gap panel + legend components). Purpose: jurisdiction-by-jurisdiction coverage
heat/status with gap → task creation.
FE: choropleth/grid of jurisdictions (D3 or SVG) bound to
/api/compliance/coverage; color = coverage status (define semantic tokens);
click jurisdiction → gap panel listing uncovered obligations with a "create
task" action (POST /api/compliance/gaps/create_task) that returns a task ref +
appears in the queue. Legend required (color legend rule). States triad;
offline read-only.
BE: ensure coverage endpoint derives from the ontology (enforcesFramework/
mandatesControl traversal — reuse derive_compliance_routing) so the map reflects
the real graph, not a static list. R-5 errors.
TEST HOOK: GT-3/GT-7, S1, R-2; coverage-reflects-ontology is a named backend test.
```

## WO-K · COMPLIANCE NET ONTOLOGY — FE `gpt-oss:120b`, BE `devstral:24b`
```
[PREAMBLE]. Refactor components/OntologyVisualizer.jsx into
kibo-is-frontend views/OntologyVisualizer.tsx. Purpose: interactive view of the
491-edge compliance graph (jurisdictions→frameworks→controls→artifacts→
penalties) built from neuralnet_ontology.
FE: force-directed graph (D3 from CDN allowlist) bound to /api/ontology/export
(JSON-LD); node color by class (Jurisdiction/LegalFramework/PrivacyTort/
GovernanceControl/Certification/PenaltyExposure/AssessmentArtifact — legend);
click node → detail (predicates in/out); path highlight for a selected
transaction's derivation. Import is GOVERNED: any /api/ontology/import goes
through a confirm + validation preview, NEVER a silent wipe (this is defect R-6,
the linksTo incident). Show predicate census before/after import. Performance:
virtualize/limit rendered edges; don't block main thread. States triad.
BE (devstral): harden /api/ontology/import — reject/quarantine payloads missing
canonical predicates or introducing unknown ones; require change-log entry;
enforce predicate census >= seed baseline. GET /api/ontology/export unchanged.
TEST HOOK: R-6 (import guard + census invariant), GT-1, S1, R-2. The import-wipe
prevention is a strict xfail until the guard ships.
```

---

## RUN SHEET
```
Slot 1: WO-G (HITL, qwen3-coder) + WO-J (map, gpt-oss)        + BE devstral: G/J endpoints
Slot 2: WO-A (meetings) + WO-B (training) [qwen3-coder]       + BE devstral: A/B
Slot 3: WO-C (employee) + WO-D (psr) [qwen3-coder]            + BE devstral: C/D
Slot 4: WO-K (ontology, gpt-oss) + WO-E (sources, qwen3-coder)+ BE devstral: K
Slot 5: WO-F (trust) + WO-H (deploy) + WO-I (telemetry)       + BE devstral
Slot 6: coder-core writes tests for all merged tabs; deepseek-r1 single review pass
Mac (continuous): gemma4/qwen3-coder — fixtures/<tab>.ts, design briefs
  spec/review/tabs/<tab>.md, CSV-export helpers, lint fixups.
```
Done per tab = FE builds+lints, BE endpoint returns real (not mock) data or a
flagged offline state (R-7), states triad present, and the tab's TEST HOOK is
green or a documented strict xfail (R-2/R-5/R-6/R-9 baselines only).
```
