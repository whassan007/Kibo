# BUILD ORDER — Privacy Inbox Redesign (local fleet only)

Two work orders. Run WO-1 and WO-2 in parallel (both fit on the DGX together),
then WO-3 (tests) after either merges. NO CLOUD MODELS — local Ollama only
(Mac `127.0.0.1:11434`, DGX `waelbot:11434`; `nemotron-3-super:cloud` is banned).
Settings: temperature 0.0, `num_ctx` 32768.

---

## WO-1 · FRONTEND — MODEL: `qwen3-coder:30b` @ waelbot

```
You are a Staff Frontend Engineer implementing the KIBO Privacy Inbox redesign.

READ FIRST (ground truth, in this order):
1. spec/review/privacy_inbox_redesign_spec.md   — the design you are building. Follow it exactly.
2. kibo-is-frontend/src/                         — the TypeScript app you are building INTO (mirror its structure, styling approach, and service patterns; this is the TS twin of the legacy JSX app).
3. kibo-is/src/PrivacyInbox.jsx                  — legacy reference only. Do NOT copy its patterns (inline hex colors, alert(), silent fetch failures).

DELIVER (all in kibo-is-frontend/src/):
1. components/inbox/: DataRow.tsx, Tag.tsx, SlaBadge.tsx, ConfidenceBar.tsx,
   TriageCard.tsx, ActionBar.tsx, EmptyState.tsx, OfflineBanner.tsx, Toast.tsx
   — typed props, design tokens from a single tokens.css (create it: surface,
   border, text-primary/secondary/muted, accent, danger, warning, success;
   light theme matching the current deployed look — white surfaces, blue accent,
   monospace only for IDs/SLA/metadata).
2. views/PrivacyInbox.tsx composing them: toolbar (title, SLA-at-risk pill,
   search, deadline sort), filter chips (All/DSAR/Breach/Opt-out/Vendor/
   Unclassified), list pane, detail pane (header + AI triage card with
   confidence bar, statute, suggested route, "why" line + body + action bar +
   reasoning field + inline confirmation).
3. services/inboxService.ts: GET /api/inbox?sort=sla&type=&q= (paginated),
   POST /api/inbox/{id}/decision {action, reclassify_to?, reasoning}.
   API base from env (VITE_API_BASE) ONLY — a hardcoded URL is defect R-1.
   Non-2xx responses MUST throw a typed error (R-5). Track online/offline
   state; offline => OfflineBanner shown, action buttons disabled, reasoning
   text preserved (R-2: never lose a decision).
4. States per view (Resilience Rule 2): loading = 5 skeleton rows + skeleton
   card (never an infinite spinner); empty = "Inbox clear" + explainer + CTA;
   error = inline retry. All three must be reachable via props for testing.
5. Keyboard: j/k navigate, a accept-and-route, f flag, d defer, / focus search.
   Rows are real <button> elements, aria-selected on active, confidence bar
   has aria-label, toast uses role="status", visible 2px accent focus ring.
   NO alert(). NO window.confirm().

RULES: TypeScript strict; two font weights (400/500); no new dependencies
beyond what package.json already has; sentence case for all UI copy; every
mutating action gives visible feedback with an audit reference.
Definition of done: `npm run build` and `npm run lint` pass; component renders
with mock data via a Storybook-style fixtures file (fixtures/inbox.ts with the
6 items from the spec: breach 61h / DSAR 27d / deletion 24d / GPC batch /
DPA renewal / unclassified 0.41-confidence).
```

## WO-2 · BACKEND — MODEL: `devstral:24b` @ waelbot

```
You are a Staff Backend Engineer adding the Privacy Inbox API to KIBO.

READ FIRST: spec/review/privacy_inbox_redesign_spec.md (data contract section);
kibo-is/agent_gateway.py (auth headers, DecisionPayload semantics, DB access
patterns — note defect R-3: do NOT add new sync sqlite3 writes inside async
handlers; use a thread-executor wrapper or the existing pattern with a TODO(R-3)
marker); kibo-is/ontology_store.py (derive_compliance_routing — use it to
compute statute[] and suggested_route for classified items).

DELIVER:
1. inbox_store.py: SQLite table privacy_inbox (id TEXT PK, type, subject,
   sender, received_at, statute_json, sla_deadline, confidence REAL,
   suggested_route, why, body, unread INT, status, decision_json, tenant TEXT
   DEFAULT 'default'); seed_inbox() with the 6 fixture items from the spec.
2. Endpoints in agent_gateway.py:
   GET  /api/inbox?sort=sla&type=&q=&page=&size=   -> {items, total, sla_at_risk}
   GET  /api/inbox/{id}
   POST /api/inbox/{id}/decision  {action: accept|reclassify|flag_legal|defer|spam,
        reclassify_to?, reasoning}  -> {status, audit_ref}
   Decisions append to the audit trail (reuse the existing audit/hash pattern);
   'accept' invokes routing: create a transaction via the existing intake path
   with the item's context so it flows into route_to_statutory_artifacts.
   'reclassify' with reasoning registers a rule-engine hint (reuse POST /api/rules
   semantics). Non-happy paths return proper 4xx with {detail} — no silent
   200-with-empty-array (R-5).
3. Classification stub: classify_inbox_item(text) that calls the LOCAL Ollama
   router (run_agent_node) and returns {type, confidence, why}; if the model is
   unreachable, return type='Unclassified', confidence=0.0, why='model offline'
   — clearly flagged, never fake data (R-7).
RULES: keep everything compatible with the existing bearer/role headers; log
via the logging module, not print() (R-8, for new code only).
```

## WO-3 · TESTS — MODEL: `coder-core` @ waelbot (after WO-1 or WO-2 merges)

```
You are a Principal QA Automation Engineer. Follow
spec/ANTIGRAVITY_TESTING_PROMPT.md exactly (framework contract, directories,
XFAIL strict rule).

DELIVER:
1. tests/backend/test_inbox_api.py (pytest + httpx): list sort=sla ordering;
   filter/search; pagination; decision actions incl. audit_ref returned;
   non-2xx on bad action (assert NOT 200-empty — mark xfail strict
   reason="Baseline R-5" if it fails); accept routes into the transaction
   pipeline (assert thread created); unreachable-Ollama classification returns
   flagged Unclassified (Baseline R-7 check — do NOT mock the local Ollama
   endpoint; stop/point it at a dead port for the negative case).
2. tests/frontend/PrivacyInbox.test.tsx (React Testing Library): three states
   render (loading/empty/error); offline disables actions and preserves
   reasoning text (xfail strict reason="Baseline R-2" until implemented);
   keyboard j/k/a; decision shows confirmation with audit ref.
3. tests/e2e/inbox.spec.ts (Playwright TS): GT-4 flow — seeded item appears
   classified -> accept -> confirmation with audit ref -> item leaves default
   filter; axe-core scan of the view with zero serious/critical violations.
Tag tests: GT-4, S1, R-2, R-5, R-7 in test names or markers.
```

Merge order: WO-1 + WO-2 parallel → wire `VITE_API_BASE` → WO-3 → fix reds →
done when GT-4 e2e is green and remaining xfails are only R-2/R-5 baseline items.
