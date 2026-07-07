# KIBO MASTER PROMPT — Full Enterprise Review + Test Execution
## Local fleet only (Mac + waelbot DGX). NO CLOUD MODELS.

> **HARD CONSTRAINT:** Every work package runs on a locally-hosted Ollama model.
> `nemotron-3-super:cloud` is EXCLUDED — it routes to a cloud endpoint. Use
> `nemotron-3-super:latest` (86 GB, local) instead. If any tool attempts a
> non-local endpoint, abort the package. All model calls go to:
> - Mac: `http://127.0.0.1:11434` — `gemma4:latest`, `qwen3-coder:latest`
> - DGX: `http://waelbot:11434` (Tailscale/LAN) — all other models
> DGX loading rule: max ~150 GB resident. Never co-load `deepseek-r1:671b` with
> anything. Pairs that fit: `gpt-oss:120b`+one 20B coder; `llama4:scout`+one 20B;
> `reasoning-core`+`qwen2.5vl:72b` is too big — run sequentially.

---

## ROLE (applies to every work package)

You are acting as Principal Software Architect, Principal UX Engineer, Staff
Frontend Engineer, Staff Backend Engineer, Platform Engineer, Security Engineer,
and Product Designer. Objective: determine whether KIBO is production-ready for
enterprise deployment, recommend everything that should be improved, AND convert
every finding into an executable test so the finding can never silently regress.
Do not describe what exists — evaluate and prescribe. Every recommendation must
be actionable, technically specific, prioritized, and immediately executable.

**The cross-cutting rule that merges review with testing:** every finding MUST
end with a `TEST HOOK:` line naming the test that will verify the fix —
either an existing golden thread / seam suite from `spec/TESTING_PLAN.md`
(GT-1…GT-8, S1…S5, R-1…R-9) or a NEW test to add to `tests/` following
`spec/ANTIGRAVITY_TESTING_PROMPT.md` conventions. A finding without a test hook
is incomplete.

## MANDATORY RECOMMENDATION SCHEMA (all packages)

```
Title | Category (Frontend/Backend/Security/UX/Performance/Accessibility/
Architecture/Infrastructure/AI/Database/DevOps) | Problem | Recommendation |
Business Value | Technical Complexity (Low/Med/High) | Priority
(Critical/High/Med/Low) | Estimated Effort (XS/S/M/L/XL) | Dependencies |
Risks | TEST HOOK
```

## SHARED OUTPUT CONTRACT

All outputs are markdown files in `spec/review/`:
`00_executive_summary.md, 01_pages/*.md, 02_frontend.md, 03_backend.md,
04_security.md, 05_performance.md, 06_accessibility.md, 07_tech_debt.md,
08_architecture.md, 09_enterprise_readiness.md, 10_roadmap.md` — plus
`tests/` additions per the testing prompt's SHARED CONTRACT.
Roadmap buckets: Quick wins (<1 day), High-impact (<1 week), Strategic (1–3 mo),
Long-term architecture. Every roadmap item cites its finding ID (e.g. FE-012).

## INPUTS (read-only ground truth)

`kibo-is/` (agent_gateway.py ~5k lines, ontology_store.py, rule_engine.py,
neuralnet_ontology.py, onboarding_agents.py, self_improvement.py,
agent_prompts.py, src/ React JSX), `cockpit/` + `kibo-is-frontend/` (TS SPAs),
`.kibo/` (state + MCP), `spec/MODULE_1..12*.md`, `spec/TESTING_PLAN.md`,
`spec/ANTIGRAVITY_TESTING_PROMPT.md`, live UI at kibo.is (4 personas:
Expert/CPO, Employee, PSR Committee, Public Widget; views: Dashboard, Privacy
Inbox, Meetings Planner, Training Admin, Onboarding Checklist).
Known defect baseline (do not rediscover — extend): R-1…R-9 in TESTING_PLAN.md §6.

---

# WORK PACKAGES — WHAT TO RUN WHERE

## WP-1 · PAGE-BY-PAGE UI/UX REVIEW (vision)
**MODEL:** `qwen2.5vl:72b` @ DGX (solo load) · **INPUT:** screenshots of every
view × every persona × 3 states (loaded/empty/error — capture via Playwright
script from tests/e2e, viewport 1440/834/390 for desktop/tablet/mobile)
**PROMPT:**
```
For EACH screenshot set (one page, one persona), do not skip any page:
1. Purpose, target user, business workflow supported.
2. Information architecture: logical organization, prioritization, obviousness
   of key actions, workflow intuitiveness.
3. UX: navigation, discoverability, friction, cognitive load, consistency,
   responsiveness, empty/loading/error/success states, onboarding, progressive
   disclosure. Count unnecessary clicks for the page's primary task. Name
   confusing interactions. Propose workflow simplifications.
4. UI: spacing, typography, alignment, color, hierarchy, visual consistency,
   mobile/tablet/desktop behavior. Flag inconsistent or duplicated components.
5. Accessibility (visual pass): contrast, focus indicators, touch targets,
   text size. (Code-level WCAG in WP-3.)
6. Verdict: production-ready? (yes/no/conditional) + top 3 fixes.
Output: spec/review/01_pages/<persona>_<view>.md using the RECOMMENDATION
SCHEMA. Every finding ends with TEST HOOK (usually GT-7 persona crawl or a new
Playwright assertion).
KNOWN CONTEXT: dark monochrome E-ink-inspired design system (spec §5 tokens);
judge against that intent, not generic Material norms.
```

## WP-2 · FRONTEND CODE REVIEW
**MODEL:** `gpt-oss:120b` @ DGX (pair with `qwen3-coder:30b` for fix snippets)
**INPUT:** `kibo-is/src/`, `cockpit/src/`, `kibo-is-frontend/src/`, package.json×3
**PROMPT:**
```
Review all three frontends as one portfolio (kibo-is JSX is being rebuilt as
kibo-is-frontend TS — judge divergence and migration completeness).
1. Architecture: component organization, routing, state management (App.jsx
   monolith vs cockpit's Zustand), hooks/context patterns, data fetching,
   caching, duplication across the three apps, modularity.
2. Design system: extract the reusable component inventory that SHOULD exist
   (cards, tables, forms, dialogs, buttons, notifications, filters, search);
   list every duplicated implementation with file paths.
3. Forms (every one): validation, inline help, required fields, keyboard nav,
   grouping, auto-save/draft/undo, confirmation dialogs.
4. Tables (every one): sorting, filtering, pagination, virtualization, search,
   bulk actions, export, column customization.
5. Dashboards: KPIs, hierarchy, trends, drill-down, personalization.
6. Performance: re-renders (10s polling loops!), bundle size, code splitting,
   lazy loading, API overfetching, memoization.
7. Resilience: verify every fetch path against seam S1 rules — env-based URLs
   only (R-1), offline states (R-2), no silent failures (R-5).
Output: spec/review/02_frontend.md. Schema + TEST HOOK per finding. For each
Critical/High finding, produce the fix as a code snippet (delegate snippet
generation to qwen3-coder:30b).
```

## WP-3 · ACCESSIBILITY (WCAG 2.2 AA)
**MODEL:** `devstral:24b` @ DGX (agentic — runs tooling) · **INPUT:** built
frontend + axe-core/pa11y via the compose stack
**PROMPT:**
```
Run axe-core + keyboard-only traversal on every view × persona. Evaluate:
keyboard navigation, screen reader compatibility, ARIA usage, focus indicators,
color contrast (monochrome theme: verify #767676-on-dark passes 4.5:1 — it
likely fails), semantic HTML, heading hierarchy. Public Widget is
citizen-facing and legally exposed — treat as Critical scope.
Output: spec/review/06_accessibility.md — violation list (WCAG criterion,
element, page, severity) + remediation snippets + TEST HOOK: add
tests/e2e/test_a11y_axe.py gating CI at zero serious/critical violations.
```

## WP-4 · BACKEND & API REVIEW
**MODEL:** `qwen3-coder:30b` @ DGX first pass, then `reasoning-core:latest`
sequentially for architecture judgment · **INPUT:** all Python in kibo-is/, .kibo/tools/
**PROMPT:**
```
Pass 1 (qwen3-coder — mechanical): inventory every endpoint in agent_gateway.py:
method, path, auth check, tenant scoping, validation, pagination, idempotency,
error shape, versioning. Flag: bearer-token-equals-role-string auth, missing
rate limiting, SQL string interpolation, sync sqlite3 in async handlers,
mock-data fallbacks reachable in prod paths, hardcoded IPs (100.113.62.112).
Inventory business logic duplication and dead code.
Pass 2 (reasoning-core — judgment): service boundaries for the 5k-line
agent_gateway monolith vs MODULE_1..3 target architecture; domain modeling
gaps vs M1 spec; SQLite→PostgreSQL migration risks (LangGraph checkpointing,
concurrent writers — the documented db-lock defect); event-architecture
readiness vs M3; queue/background-job needs (canadian_verdicts_agent scheduler);
N+1 and slow-query candidates; caching opportunities; observability
(logging/tracing/metrics — currently print statements).
Output: spec/review/03_backend.md. Schema + TEST HOOK per finding
(map to S2/S3/S4 suites or new integration tests).
```

## WP-5 · SECURITY REVIEW
**MODEL:** `reasoning-core:latest` @ DGX (solo) · escalate the 5 worst findings
to `deepseek-r1:671b` in WP-9 · **INPUT:** backend code + .kibo grants/config +
frontend auth handling + docker/k8s specs (M9)
**PROMPT:**
```
Threat-model then review: authentication (role-string bearer tokens = no auth),
authorization/RBAC/ABAC vs the 7 declared roles, secrets management, encryption
at rest/in transit, session handling, CSRF, XSS (JSON tree viewer renders raw
payloads), SQL injection (check every f-string query), rate limiting, CORS,
audit logging integrity (ontology wipe incident R-6 = write path unguarded),
prompt-injection surface (onboarding_agents scrapes external websites → LLM;
.kibo boundary #4), MCP tool server exposure, Tailscale-IP leakage in client
bundles. Multi-tenancy: currently NONE — enumerate what M2 must gate.
For each vulnerability: exploit scenario, affected asset, CVSS-style severity,
fix, TEST HOOK (S1-CONTRACT fuzz, GT-6 attack cases, or new regression test).
Output: spec/review/04_security.md. This file gates enterprise readiness.
```

## WP-6 · AI COMPONENT REVIEW
**MODEL:** `nemotron-3-super:latest` @ DGX (solo) · **INPUT:** agent_prompts.py,
run_agent_node + routing code, self_improvement.py, onboarding_agents.py,
rule_engine.py, ontology router
**PROMPT:**
```
Review the AI layer: prompt engineering quality per statutory agent (PHIPA/
Law25/GDPR/CPRA/FAIR prompts); context retrieval & RAG (legal_ground_truth
usage); hallucination mitigation (statutory citations unverified? mock-data
fallback masquerading as model output — flag loudly); confidence scoring
(absent?); human approval workflows (HITL breakpoint coverage — which agent
outputs bypass it?); auditability & explainability (can a CPO trace WHY an
assessment said what it said?); model routing (token-count router: correctness,
failure modes when DGX unreachable); cost/latency optimization for the local
fleet; self-improvement guardrails (score≥8 auto-approval — adversarial risks).
Output: spec/review/08_architecture.md §AI + findings with TEST HOOK
(GT-3 checkpoints, new fixture-based agent-output contract tests: JSON schema
per agent, citation-presence assertions, mock-fallback detection flag).
```

## WP-7 · ENTERPRISE READINESS + TECH DEBT
**MODEL:** `llama4:scout` @ DGX (needs the huge context: ALL specs + ALL review
outputs from WP-1..6) · **RUN LAST of the parallel set**
**PROMPT:**
```
Synthesize WP-1..6 outputs + MODULE_1..12 specs + TESTING_PLAN.md.
1. Enterprise readiness scorecard: multi-tenancy, HA, DR, SOC 2, ISO 27001,
   GDPR, PIPEDA, HIPAA, CCPA/Law 25, audit logging, data retention, Privacy by
   Design. For each: current state, gap, owning module (M1–M12), test gate.
   Note the irony budget: a privacy-compliance product must itself be
   compliance-clean — flag any finding where KIBO violates the statutes it
   assesses (e.g., public widget with no consent notice, unencrypted PHI in
   kibo_state.db).
2. Technical debt register: duplicated code, dead code, complexity hotspots,
   naming inconsistency, missing abstractions, folder organization, missing
   tests, fragile implementations. Impact-estimate each (Low/Med/High × blast
   radius).
3. Deliverables: spec/review/07_tech_debt.md, 09_enterprise_readiness.md,
   10_roadmap.md (Quick wins <1d / High-impact <1wk / Strategic 1–3mo /
   Long-term), 00_executive_summary.md (≤2 pages, verdict up front:
   production-ready yes/no/conditional + the 10 items that change the answer).
Traceability: every roadmap item cites finding IDs and TEST HOOKs; cross-check
against tests/ markers — any Critical finding without a runnable test hook is
listed in a 'TEST GAPS' appendix.
```

## WP-8 · MAC SIDE-CHANNEL (runs continuously during WP-1..7)
**MODELS:** `gemma4:latest` + `qwen3-coder:latest` @ Mac
Tasks: convert WP findings into test skeletons (xfail strict) in `tests/` as
they land; fix-snippet generation for XS/S items; screenshot capture script for
WP-1; lint scripts (R-1 URL check); doc formatting of `spec/review/*`.
The Mac never blocks on the DGX — pull the latest finished WP file and process.

## WP-9 · FINAL ADVERSARIAL GATE (single pass)
**MODEL:** `deepseek-r1:671b` @ DGX (solo, nothing else loaded, once)
**INPUT:** 00_executive_summary.md + 04_security.md + 10_roadmap.md + tests/ tree
**PROMPT:**
```
Adversarial review. Answer only:
1. Which 5 findings, if wrong, most change the production-readiness verdict?
   Re-derive each from the code evidence cited — confirm or overturn.
2. Do the security fixes as specified actually close the exploit scenarios?
   Attack the fixes.
3. Are the roadmap priorities ordered by risk-adjusted value? Reorder max 5.
4. List every Critical finding whose TEST HOOK would pass even if the defect
   returned (weak tests). Specify the stronger assertion.
Output: spec/review/11_adversarial_gate.md with file:line evidence.
```

---

# EXECUTION SCHEDULE (wall-clock, DGX memory-aware)

```
Slot 1: WP-1 (qwen2.5vl solo)            | Mac: WP-8 screenshot capture first
Slot 2: WP-2 (gpt-oss) + WP-4p1 (qwen3-coder)     — pair fits
Slot 3: WP-3 (devstral) + WP-4p2 (reasoning-core) — pair fits
Slot 4: WP-5 (reasoning-core solo) then WP-6 (nemotron solo) — sequential
Slot 5: WP-7 (llama4:scout solo, max num_ctx)
Slot 6: WP-9 (deepseek-r1 solo) → Mac applies weak-test fixes → make test-all
```

Runtime settings: `OLLAMA_HOST=0.0.0.0 ollama serve` on DGX; set `num_ctx`
32768+ for WP-2/WP-7 (llama4/gpt-oss support it); temperature 0.2 for review
packages, 0.0 for code/test generation; every package writes its output file
BEFORE elaborating in chat, so a crashed session loses nothing.

Done = `spec/review/` complete, `make test-all` runs (greens + strict xfails
only), and 11_adversarial_gate.md has zero unresolved overturns.
