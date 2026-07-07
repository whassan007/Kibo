
# Trust Tiers Design Brief

Read `spec/review/kibo_is_frontend_ux_review.md` and `spec/review/privacy_inbox_redesign_spec.md` (follow that quality bar and state model exactly). Build in `kibo-is-frontend/src` using the shared component library (Button, Panel, SectionHeader, Field, Select, DataTable, Tag, Toast, ConfirmDialog, EmptyState, Skeleton, OfflineBanner, SlaBadge). Legacy JSX is reference ONLY — never copy its inline hex, alert(), or silent fetch. API base from `VITE_API_BASE`; non-2xx throws typed error; offline disables mutations and preserves unsent input. Deliver loading/empty/error states reachable via props. Definition of done: `npm run build` + `npm run lint` pass; renders with a `fixtures/trust_tiers.ts` mock file.

## WO-F · TRUST TIERS — FE `qwen3-coder:30b`, BE `devstral:24b`

**Purpose:** Show/govern the autonomy/deployability ladder — which agent actions are auto-allowed vs require human sign-off, per trust tier (maps to `.kibo` grants + deployability ladder).

**FE Specs:**
- Render tier cards clearly displaying:
  - `Tier Name`
  - `Allowed Action Scopes` (bulleted or pill list)
  - `Gate Type` (Human/Auto indicator)
  - `Current Agents` (count of active agents at this tier)
- Implement `Promote/Demote` controls exclusively behind a `ConfirmDialog` to strictly enforce `.kibo` boundary #5 (autonomy expansion is a governed, audited action).
- Bind the view to the new `fetchTrustTiers` service layer.
- Enforce the States triad:
  - **Loading:** Skeleton tier cards.
  - **Empty:** "No Trust Tiers configured."
  - **Offline:** Banner visible, read-only mode (promotion actions locked).

**BE Specs (devstral):**
- GET `/api/trust/tiers` (from `.kibo/state/autonomy/grants.json` + `deployability/ladder.json` — validate grants before returning, R-6 discipline).
- POST `/api/trust/tiers/{agent}/promote {reason}` -> `audit_ref`, routes autonomy change to judgment queue (never silent). R-5 errors.

**TEST HOOK:** GT-6 (privilege change must be authorized+audited), S1, R-2, R-9.
