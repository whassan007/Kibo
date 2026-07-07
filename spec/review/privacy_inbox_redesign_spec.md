# Privacy Inbox — Redesign Specification
Companion to the interactive prototype shown in chat. Matches the new light theme (white surfaces, blue accent, mono for metadata).

## Design intent
The current page is a two-pane shell: an invisible/empty list and a placeholder detail pane ("Select an email…"). The primary user (CPO/analyst) needs a **triage cockpit**: see what's waiting, in deadline order, and clear each item in one decision. The redesign turns every inbox item into a *pre-classified, statute-aware work item* and makes the AI do the first pass — with the human confirming, which doubles as GT-4 classification training.

## Layout (3 zones replacing the current 2)
1. **Toolbar** — title + "N SLA at risk" pill (danger tint), search, sort indicator ("sorted by deadline" — deadline sort is the default and only default; no unread-first vanity sorting).
2. **List pane (left, ~260px)** — filter chips (All / DSAR / Breach / Opt-out / Vendor / Unclassified). Each row: classification tag (color-coded), SLA countdown badge (mono; danger <72h, warn <14d), subject (bold when unread), sender, unread dot. Keyboard: j/k to move.
3. **Detail pane (right)** with three stacked blocks:
   - **Header:** subject, sender, received time, reference ID as a copy button (mono).
   - **AI triage card** (accent tint): classification + confidence bar (green ≥75%, amber ≥50%, red below), statute(s) with clock, suggested routing destination, and a one-line "Why" explanation (explainability requirement, GT-3). Low-confidence items (<50%) surface as "Unclassified — human decision trains the classifier."
   - **Body excerpt** then the **action bar**: `Accept and route` (single accent-filled primary — one per view), Reclassify, Flag to legal, Defer, Spam. Below it a reasoning field labeled as feeding the audit log and rule engine (approve-always training), then an inline confirmation line (no alert() dialogs).

## Data contract (backend needs per item)
`id, type, subject, from, received_at, statute[], sla_deadline, confidence, suggested_route, why, body, unread, status`
Endpoints: `GET /api/inbox?sort=sla&type=&q=` (paginated), `POST /api/inbox/{id}/decision {action, reclassify_to?, reasoning}` → returns audit ref. Decision actions map to the existing DecisionPayload semantics.

## States (all designed, all tested — Resilience Rule 2)
- **Empty:** icon + "Inbox clear" + explainer + "Connect a mailbox" CTA. Never a blank column.
- **Loading:** 5 skeleton rows in the list, skeleton card in detail (never an infinite spinner).
- **Offline/degraded:** warning-tint banner "Gateway unreachable — showing cached queue from N min ago. Actions are paused so nothing is lost." + Retry. Action buttons disabled while offline (R-2; never lose a decision).
- **Error on action:** inline danger text under the action bar + retry; the item stays selected, reasoning text preserved.

## Interaction rules
- Selecting marks read (local + PATCH). Decision → optimistic status change + inline confirmation with audit reference; row leaves the default filter.
- Keyboard: j/k navigate, a accept-and-route, f flag, d defer, / focus search. Shortcut legend in the footer strip.
- Bulk: checkbox appears on row hover; bulk actions limited to Defer/Spam/Assign (never bulk-approve breaches).
- SLA pill in the toolbar filters to at-risk items when clicked.

## Accessibility specifics
List rows are `<button>` elements (full-row), `aria-selected` on the active row, `role="list"`; confidence bar has `aria-label="confidence 88%"`; toasts use `role="status"`; focus ring = 2px accent outline; all tags ≥11px with AA contrast (danger/warn/success text tokens on their tint backgrounds).

## Test hooks
- GT-4: submit fixture email → appears classified in list → accept → lands in correct queue with audit ref.
- GT-7: persona crawl asserts empty/loading/offline states render; zero no-op buttons.
- S1: kill gateway mid-session → offline banner ≤10s, actions disabled, retry recovers without reload.
- R-5 regression: non-2xx on decision POST must surface inline error, never silent success.

## Build notes
Implement in `kibo-is-frontend` (TS) using the component library from the UX review (#6): `DataRow`, `Tag`, `SlaBadge`, `ConfidenceBar`, `TriageCard`, `ActionBar`, `EmptyState`, `OfflineBanner`, `Toast`. Estimated effort: M (3–7 days) once components exist; L standalone.
