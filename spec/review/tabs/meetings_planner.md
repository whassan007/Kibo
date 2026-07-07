
# Meetings Planner Design Brief

Read `spec/review/kibo_is_frontend_ux_review.md` and `spec/review/privacy_inbox_redesign_spec.md` (follow that quality bar and state model exactly). Build in `kibo-is-frontend/src` using the shared component library (Button, Panel, SectionHeader, Field, Select, DataTable, Tag, Toast, ConfirmDialog, EmptyState, Skeleton, OfflineBanner, SlaBadge). Legacy JSX is reference ONLY — never copy its inline hex, alert(), or silent fetch. API base from `VITE_API_BASE`; non-2xx throws typed error; offline disables mutations and preserves unsent input. Deliver loading/empty/error states reachable via props. Definition of done: `npm run build` + `npm run lint` pass; renders with a `fixtures/meetings_planner.ts` mock file.

## WO-A · MEETINGS PLANNER — FE `qwen3-coder:30b`, BE `devstral:24b`

**Purpose:** CPO/PSR schedule + run compliance meetings, capture minutes/actions.

**FE Specs:**
- Create-meeting form via Field/Select: date (styled date-time picker, not raw native), meeting type (Weekly Privacy & Security / PSR Committee / ad-hoc), attendees (multi-select of roles), recurrence, agenda items (repeatable rows). Full validation: no submit with empty date; required marks; inline errors; success toast with meeting ref.
- Meetings list (DataTable): upcoming/past, sortable by date, status column, click → detail pane with minutes editor + action-item rows (assignee, due date, linked risk id) that POST into the transaction/queue pipeline so an action item becomes tracked work — not dead text.
- Commissioner research libraries: keep the 9 working links, render as a labeled resource list component (not inline anchors).
- States: empty ("No meetings scheduled" + Create CTA); loading skeleton; offline banner.

**BE Specs:** 
- Extend `/api/expert/meetings` + `/api/psr/meetings` with POST (create), GET detail, PATCH minutes, POST action-item (routes into intake). Action items append to audit trail. No sync sqlite in async handlers (R-3 — mark TODO if unavoidable). Errors return {detail} 4xx (R-5).

**TEST HOOK:** GT-5, S1, R-2, R-5.
