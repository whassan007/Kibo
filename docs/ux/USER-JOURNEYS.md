# KIBO Privacy OS — User Journeys & Operational Workflows (`UX-01` through `UX-15`)

This document maps the 9 enterprise user roles and the 15 mandatory user journeys (`UX-01` through `UX-15`) to concrete screens, state transitions, and backend API/SSE contracts.

---

## 1. Role-Aware Experience Matrix (Section 4)

| Role ID | Role Title | Default Landing View | Primary Tasks & Quick Actions | Server-Verified Permissions |
|---|---|---|---|---|
| `CPO` | Chief Privacy Officer | `Home` (Executive Overview) | Program posture, overdue SLA escalations, final rule/assessment/breach sign-offs, board reporting | Full read/write + `approve_assessment`, `approve_breach_notice`, `promote_regulatory_rule` |
| `DPO` | Data Protection Officer / Privacy Officer | `Home` / `Inbox` | GDPR Art. 35 DPIAs, Quebec Law 25 EFVPs, supervisory authority consultations, DSAR escalations | Full read/write + `approve_assessment`, `approve_dsar_delivery`, `promote_regulatory_rule` |
| `ANALYST` | Privacy Analyst | `Inbox` / `Assessments` | Draft PIAs/DPIAs/TIAs, collect DSAR records, update RoPA & vendor questionnaires | Read/write drafts (`create_assessment_draft`, `update_dsar_stage`), cannot self-approve final gates |
| `LEGAL` | Legal Counsel | `Inbox` / `Regulatory Intelligence` | Review `REQUIRES_LEGAL_REVIEW` citations, legal privilege holds on breaches, statutory exemptions | Full legal review + `verify_citation`, `promote_regulatory_rule`, `approve_breach_notice` |
| `SECURITY` | Security / Incident Response | `Incidents` (Breach War Room) | Triage security incidents, log containment tasks & forensic evidence, track 72h/36h/15d clocks | Create/update incidents & containment evidence; cannot dispatch external notices without Legal/CPO |
| `MANAGER` | Department Manager | `Home` / `Data & Vendors` | Submit new processing activity or vendor intake, attest to departmental data inventory | Scoped read + intake submission |
| `EMPLOYEE` | Employee | `Assistant` / `Home` | Ask governed privacy questions, check approved AI tools, submit privacy concern or intake | Read-only guidance + intake submission |
| `AUDITOR` | Internal / External Auditor | `Reports` / `Risks & Controls` | Inspect SHA-256 evidence chains, approval signatures, RoPA ledger, and temporal regulatory history | Read-only audit & evidence export |
| `ADMIN` | Platform Administrator | `Administration` | Configure authorized tenant memberships, SSO/JWT settings, AI Hub connectors, and source cadences | System & integration configuration |

---

## 2. Mandatory User Journeys (`UX-01` through `UX-15`)

### `UX-01`: First-Time Privacy Officer
1. **Trigger:** Privacy Officer opens KIBO Privacy OS (`/` or `/privacy-os`).
2. **Experience:** Verified User Profile Badge displays authenticated user (`usr-cpo-counsel-01`), role (`CPO`), and authorized organization (`Aegis Global Health & FinTech Corp`), plus connection status (`LIVE`, `OFFLINE`, `STALE`, or `DEMO`).
3. **Outcome:** Executive Home immediately presents 4 actionable summary cards (`Overdue`, `Need Approval`, `Open Incidents`, `Verified Regulatory Updates`), `My Priority Work` table with direct drill-down buttons, `Recent Regulatory Changes`, and `Live Activity / System Status`.

### `UX-02`: Create a Privacy Assessment
1. **Trigger:** Privacy Analyst navigates to `Assessments` (`3. Privacy Assessments`).
2. **Experience:** Guided 9-step workflow (`1. Project Overview` → `2. Organization & Jurisdiction` → `3. Processing Activities` → `4. Data Categories` → `5. Vendors & Transfers` → `6. Risk & Obligation Analysis` → `7. Recommended Controls` → `8. Evidence & Attachments` → `9. Review & Approval`).
3. **Outcome:** Analyst saves a draft (`localStorage` + server draft), resumes it without data loss, attaches evidence with SHA-256 hash, and submits for `DPO`/`CPO` review.

### `UX-03`: Respond to a Breach
1. **Trigger:** Privacy Officer opens `Incidents` (`2. Multi-Jurisdiction Breach War Room`).
2. **Experience:** Displays incident severity, status, owner, current response phase (`Detection` → `Containment` → `Legal Assessment` → `Notification Drafting` → `Approved / Closed`), affected jurisdictions, JRAE-calculated statutory deadlines (`72h` GDPR, `ASAP` PHIPA/Law 25), evidence collected, and notification drafts.
3. **Outcome:** Officer routes a regulator/individual notification decision for human `LEGAL`/`CPO` approval; auto-send remains blocked until approved.

### `UX-04`: Complete a Rights Request (DSAR)
1. **Trigger:** Analyst opens `Privacy Rights` (`DSARs & Individual Rights`).
2. **Experience:** Shows request type, requester verification state (`Verified` / `Pending`), applicable jurisdictions, JRAE response deadline, 5-stage progress tracker (`Intake` → `Identity Verification` → `Record Collection` → `Redaction & Exemption Check` → `Final Approval & Delivery`), and assigned officer.
3. **Outcome:** Analyst advances collection and redaction stages and routes final delivery package for approval.

### `UX-05`: New Regulatory Decision
1. **Trigger:** A `regulation.verified` or `regulation.discovered` SSE event arrives (or user inspects `Regulatory Intelligence`).
2. **Experience:** Regulatory Intelligence view updates without page reload, displaying publication date, last retrieved timestamp, last verified timestamp, issuing authority, jurisdiction, SHA-256 hash, and organizational impact badge.
3. **Outcome:** Unverified discoveries (`UNVERIFIED`, `REQUIRES_LEGAL_REVIEW`) are clearly badged and never labeled as active binding obligations until promoted.

### `UX-06`: Live Approval
1. **Trigger:** Reviewer approves a pending assessment or inbox item (`POST /api/v1/office/assessments/{id}/approve` or `POST /api/v1/events/publish`).
2. **Experience:** Server emits `approval.completed` over SSE (`/api/v1/events/stream`); UI updates status badge and Live Activity feed in real time without manual refresh.

### `UX-07`: Network Failure
1. **Trigger:** Backend connection is unavailable or interrupted.
2. **Experience:** Header status badge transitions to `OFFLINE` (or `STALE` if displaying cached prior data); an explicit Offline Recovery Banner explains what is cached vs. unavailable; local assessment drafts remain editable and saved locally; AI Hubs (`Copilot`, `Claude`, `Gemini`) show `offline` (never fake `connected`); mutations are prevented from faking server success.

### `UX-08`: Unauthorized Identity Change
1. **Trigger:** Attempt to spoof `X-Tenant-ID`, `X-User-ID`, or `X-User-Role` via headers or unauthorized organization switch.
2. **Experience:** Raw header inputs are removed from the UI; Organization Switcher only lists server-authorized memberships; backend rejects cross-tenant or escalated requests with HTTP `401`/`403`.

### `UX-09`: Screen Reader & Keyboard Navigation
1. **Trigger:** User navigates workspace using `Tab`, `Shift+Tab`, `Arrow` keys, `Enter`/`Space`, `Cmd+K`/`Ctrl+K`, and `/` search shortcut.
2. **Experience:** Skip-to-main-content link, semantic `<nav aria-label="Primary Privacy Workspace Navigation">`, `role="tablist"`/`role="tab"`/`role="tabpanel"`, `aria-live="polite"` status announcements, and labeled form controls meet WCAG 2.2 AA.

### `UX-10`: Mobile and Tablet Usability
1. **Trigger:** Viewport resized to mobile (`375×812`) or tablet (`768×1024`).
2. **Experience:** Collapsible mobile navigation drawer, responsive card grids, horizontal-scroll-safe tables, and touch-friendly (`>= 40px`) action targets.

### `UX-11`: Real-Time SSE Reconnect & Deduplication
1. **Trigger:** SSE connection drops and reconnects with `last_event_id` cursor.
2. **Experience:** Client resumes from `last_event_id`, deduplicates events by `event_id` in a bounded set, and avoids duplicate notifications or state mutations.

### `UX-12`: Long-Running Governed Agent Task
1. **Trigger:** User runs a multi-stage Governed Privacy Analysis or JRAE evaluation.
2. **Experience:** Displays actual stage progression (`1. Validating Tenant & Facts` → `2. Evaluating Statutory Thresholds & Preemption` → `3. Verifying Citations & SHA-256 Hashes` → `4. Complete`) with elapsed time and cancel support.

### `UX-13`: Empty Organization Onboarding
1. **Trigger:** Newly provisioned tenant with zero assessments, incidents, or RoPA records is selected (`Empty Organization` mode).
2. **Experience:** Displays truthful zero-count KPIs, clear empty states, and a 4-step Guided Setup checklist (`Configure Organization Profile`, `Select Operating Jurisdictions`, `Import or Register First Processing Activity`, `Configure Approval Roles`).

### `UX-14`: Large Organization Scale (`1,000+` Records)
1. **Trigger:** High-volume enterprise dataset (`1,000+` tasks/records/citations) is loaded.
2. **Experience:** Debounced search, instant client/server filtering, and paginated table rendering (`25` / `50` / `100` rows per page) keep interaction latency under `50 ms`.

### `UX-15`: No Surprise Mutations on Page Load
1. **Trigger:** User opens `/` or `/privacy-os` and clicks through all 11 primary navigation sections.
2. **Experience:** Zero `POST`, `PUT`, `PATCH`, or `DELETE` requests are fired on component mount or navigation change; persistent records are created only when the user explicitly clicks a submit/create button.
