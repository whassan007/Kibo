
# Training Admin Design Brief

Read `spec/review/kibo_is_frontend_ux_review.md` and `spec/review/privacy_inbox_redesign_spec.md` (follow that quality bar and state model exactly). Build in `kibo-is-frontend/src` using the shared component library. Legacy JSX is reference ONLY — never copy its inline hex, alert(), or silent fetch. API base from `VITE_API_BASE`; non-2xx throws typed error; offline disables mutations and preserves unsent input. Deliver loading/empty/error states reachable via props. Definition of done: `npm run build` + `npm run lint` pass; renders with a `fixtures/training_admin.ts` mock file.

## WO-B · TRAINING ADMIN — FE `qwen3-coder:30b`, BE `devstral:24b`

**Purpose:** Fixes the "Loading compliance data…" infinite-spinner defect (R-2/R-5). Manage employee roster and compliance metrics.

**FE Specs:**
- Org compliance metric cards (completion %, overdue count, at-risk employees) bound to `/api/expert/training/compliance`; NEVER an infinite spinner — resolve to data, empty, or error.
- Per-employee roster DataTable: name, role, course, status, due date; sort/filter/search/export CSV (auditor need).
- Bulk actions "Reset & Assign Courses" and "Send Overdue Reminders" MUST open a ConfirmDialog with scope preview ("assign 3 courses to 42 employees") and return an audit ref; no fire-and-forget (these are destructive/mass actions).
- States triad; offline disables the two bulk buttons.

**BE Specs:** 
- GET `/api/expert/training/compliance` returns {metrics, roster}; POST `/api/expert/training/assign` and `/reminders` take an explicit id list, append audit, return {affected, audit_ref}.

**TEST HOOK:** GT-7, S1, R-2, R-5; confirm-dialog on bulk actions is a named frontend test.
