# KIBO.IS Live Site — Role-Based Functionality Review

Reviewed: https://kibo.is/ on 2026-07-02 (Chrome, all four role modes exercised).

## 1. What the live site actually is

The deployed site is a **"Localized Compliance Gateway"** scoped to **Ontario FIPPA** (Regulator: IPC Ontario, 30-day response clock), with a role switcher exposing four personas: Expert Mode (Super User), Employee Mode, PSR Committee Member, and Public Widget. This is a much smaller, Canada-focused app than the v2.0 spec (US patchwork, 10-phase model, Action Queue, Evidence Vault).

## 2. Critical blocker (affects every role)

The frontend calls `http://100.113.62.112:8000/api/...` — a private (Tailscale-range) IP over plain HTTP from an HTTPS page. The request never completes (mixed-content block + unreachable host), so **every data-driven panel is permanently empty** with no error surfaced:

- Dashboard: "Active FIPPA Compliance Assessments" renders nothing.
- Privacy Inbox: no email list at all, only the placeholder detail pane.
- Training Admin: stuck on "Loading compliance data..." forever.
- Employee Mode: "No risks currently assigned"; training track section is empty.
- PSR Risk Advisory Queue: empty.

There is no offline banner, retry, or error state — the spec's §7.1 "GATEWAY OFFLINE: PIPELINE SUSPENDED" guardrail is not implemented. A CPO cannot distinguish "no pending work" from "backend down," which is dangerous for SLA-driven work. Fix: put the API behind `https://api.kibo.is` (or same-origin `/api`), and implement the offline banner + disabled action buttons.

Secondary defects: the jurisdiction selector (globe icon) is an **empty dropdown** — no options load; the **Onboarding Checklist** view is completely blank (no heading, no empty-state).

## 3. Role-by-role review

### 3.1 Expert Mode — the CPO/DPO cockpit

| View | Works | Gaps vs. CPO tasks |
|---|---|---|
| Dashboard | Headings + "Run Activities Audit" and "SOC 1 / SOC 2 Assessment" buttons render | No assessments load; audit buttons produce no visible result. No KPIs, no SLA countdowns, no risk register. A CPO's first question — "what needs my decision today?" — is unanswerable. |
| Privacy Inbox | Triage layout (list + detail pane) exists | Empty. No intake stream, no DSAR/FOI queue, no triage actions visible. This was the spec's core HITL Action Queue (approve/reject/flag-legal/defer) — none of those controls appear. |
| Meetings Planner | Best-built view: create meeting (date, type: Weekly Privacy & Security / PSR Committee), agenda items, minutes + action-item pane, and 9 working links to Canadian commissioner libraries (OPC, CAI, BC/AB/ON/SK/NS/NL OIPC, MB Ombudsman) | No attendee/role assignment, no recurrence, no link from action items to risks or assessments. Created meetings likely don't persist (backend unreachable). |
| Training Admin | "Reset & Assign Courses" and "Send Overdue Reminders" buttons | Metrics never load; no per-employee completion table, no course catalog, no evidence export for regulators. |
| Onboarding Checklist | — | Entirely blank. |

Missing entirely for the CPO role: PIA/DPIA workflow, breach/incident management (RROSH assessment, notification clocks), vendor/TIA assessments, data inventory review (employees can submit, but Expert Mode has no view of the central ledger), rule engine, evidence vault, and audit trail/signatures.

### 3.2 Employee Mode — data stewards / staff

The strongest role-fit on the site. Tasks supported: view assigned compliance risks, see role-based FIPPA training, and a well-designed **Data Inventory Contribution form** (system name, data types, purpose of collection, retention rule, third-party sharing) feeding a "central ledger" — this correctly operationalizes Phase 2 inventory as a distributed task.

Gaps: submission fate is invisible (no confirmation of where it went, and no Expert-side view to review/approve contributions); no way for an employee to report an incident or suspected breach — the single most important employee privacy task; no training launch/completion action.

### 3.3 PSR Committee Member — governance committee

Supported: advisory review materials (Quebec Law 25 Diagnostic Posture.pdf, Cross-Border Transfer TIA v1.docx, Commissioner Rulings Newsletter — download/view), same commissioner research libraries, and a Risk Advisory Queue.

Gaps: the queue is empty with no workflow — a committee member's task is to *deliberate and record an opinion* (approve/escalate/comment), and there is no voting, commenting, or sign-off mechanism; no meeting materials tied to PSR meetings created in the planner; documents are static uploads with no versioning or review status.

### 3.4 Public Widget — data subjects / citizens

A clean embeddable FOI/DSAR portal: file a request (Access / Delete / Opt-out of Profiling / Correct), track by reference ID, and a regulatory notice block (FIPPA, IPC, 30-day clock). The shortcode rendering (`[kibo_privacy_widget jurisdiction="ontario"]`) is a good embed story.

Gaps: submissions go to the unreachable backend, so a real citizen's request would silently vanish — a **compliance liability**, not just a bug; no identity verification step; no confirmation email flow; only one jurisdiction despite the selector; no accessibility review evident (low-contrast gray-on-dark text will fail WCAG for a public-facing government-adjacent form).

## 4. Roles with no home

Several personas around a privacy office have no mode: **Legal counsel** (spec's "Flag Legal" routing has no receiving workspace), **auditors/regulators** (no read-only evidence vault or export), **IT/security** (no incident intake or system-registration approval), and **vendor contacts** (no DPA/TIA submission portal). The role switcher itself is an unauthenticated dropdown — fine for a demo, but it means there is no actual access control separating employee, committee, and super-user data.

## 5. Live site vs. the v2.0 spec

The deployed app implements roughly one of the spec's four modules (a slim Sensory/intake + meetings layer) and none of: Action Queue with the 5-state decision block (Approve Now/Always, Flag Legal, Review Later, Reject) and reasoning-trained RuleEngine; 10-Phase Lifecycle kanban; Evidence Vault with SHA-256 signed artifacts; sectoral questionnaires (HIPAA/CPRA/COPPA/GLBA); resiliency guardrails (§7). Also the spec targets the US patchwork while the live build targets Canadian FIPPA — the jurisdiction dropdown suggests multi-statute support is intended but not wired.

## 6. Prioritized recommendations

1. **P0 — Backend reachability + error states.** Public HTTPS API endpoint; offline banner; disable submit buttons when the gateway is down. The Public Widget must never accept a request it can't deliver.
2. **P0 — Fix empty shells:** Onboarding Checklist view and jurisdiction selector (populate FIPPA/PHIPA/PIPEDA/Law 25… and drive the footer statute/regulator/clock from it — the plumbing for that context already exists).
3. **P1 — Build the Action Queue.** The HITL decision block is the product's core differentiator per the spec and is the CPO's daily task loop; without it Expert Mode is read-only scaffolding.
4. **P1 — Close the loops:** employee inventory submissions → Expert review queue; PSR advisory queue → recorded opinions; meeting action items → assigned risks.
5. **P2 — Add incident reporting** (employee-facing) and breach triage (expert-facing) — the highest-liability workflow currently absent.
6. **P2 — Real authentication/RBAC** to replace the role dropdown, plus an audit trail on every decision (spec §8).
7. **P3 — Accessibility pass** on the public widget (contrast, labels, keyboard nav) and confirmation/tracking emails for data-subject requests.

## 7. What's working well

Role segmentation is the right product shape — CPO cockpit, employee contribution, committee advisory, and public intake mirror how a privacy office actually distributes work. The Meetings Planner with jurisdiction-correct commissioner libraries is immediately useful. The data inventory form asks exactly the right five questions. The embeddable widget with statute-aware response clocks is a strong differentiator worth finishing first.
