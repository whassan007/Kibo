# KIBO Privacy OS — Unified Enterprise Design System (`docs/ux/DESIGN-SYSTEM.md`)

## 1. Visual & Semantic Color System (Section 9)

Every status badge, alert, and operational indicator pairs a semantic color token with an explicit text label and icon (never relying on color alone for meaning, satisfying WCAG 2.2 AA 1.4.1):

| Semantic Meaning | Token Name | Dark Surface Class | Light Surface Class | Icon / Prefix | Usage |
|---|---|---|---|---|---|
| **Informational / Neutral** | `neutral` | `bg-slate-800/90 text-slate-200 border-slate-700` | `bg-slate-100 text-slate-800 border-slate-300` | `● INFO` | Metadata, jurisdiction codes, neutral counts |
| **Active / In Progress / Updating** | `active` | `bg-blue-500/20 text-blue-200 border-blue-500/40` | `bg-blue-50 text-blue-800 border-blue-300` | `↻ UPDATING` | Active workflow stages, running agent evaluations |
| **Attention Required / Stale / Review** | `warning` | `bg-amber-500/20 text-amber-200 border-amber-500/40` | `bg-amber-50 text-amber-900 border-amber-300` | `⚠ ATTENTION` | Approaching SLAs (`<48h`), `STALE` cache, `REQUIRES_LEGAL_REVIEW` |
| **Critical / Blocked / Error / Overdue** | `critical` | `bg-rose-500/20 text-rose-200 border-rose-500/40` | `bg-rose-50 text-rose-900 border-rose-300` | `⛔ CRITICAL` | Overdue DSAR/breach clocks, `OFFLINE` mutation block, `ERROR` |
| **Confirmed Success / Live / Verified** | `success` | `bg-emerald-500/20 text-emerald-200 border-emerald-500/40` | `bg-emerald-50 text-emerald-900 border-emerald-300` | `✓ VERIFIED` | `LIVE` backend connection, SHA-256 verified citations, approved gates |
| **Inactive / Unavailable / Offline** | `inactive` | `bg-zinc-800/80 text-zinc-300 border-zinc-700` | `bg-zinc-100 text-zinc-700 border-zinc-300` | `○ OFFLINE` | Disconnected integrations, disabled controls |

---

## 2. Typography & Spacing Scale

- **Font Stack:**
  - Sans (`--font-sans`): `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
  - Monospace (`--font-mono`): `'JetBrains Mono', 'SFMono-Regular', Menlo, Monaco, Consolas, monospace` (used for SHA-256 hashes, statutory citations, CELEX/ELI IDs, and audit references)
- **Hierarchy:**
  - Workspace Title (`h1`): `text-xl font-bold tracking-tight` (`20px`, line-height `28px`)
  - Section Header (`h2`): `text-base font-bold tracking-tight` (`16px`, line-height `24px`)
  - Card Title (`h3`): `text-sm font-semibold` (`14px`, line-height `20px`)
  - Body / Table Cell: `text-xs` or `text-sm` (`12px`–`14px`, minimum `4.5:1` contrast ratio)

---

## 3. Motion & Liveliness Standards (Sections 3 & 9)

1. **Operational Liveliness:** Driven strictly by real backend state transitions and Server-Sent Events (`/api/v1/events/stream`).
2. **Interaction Liveliness:**
   - Button press acknowledgment (`active:scale-[0.99] transition-transform duration-100`)
   - Progressive form validation with inline field guidance
   - Multi-stage task progress stepper (`StageProgress`) showing real stages (`Validating Facts` → `Evaluating Thresholds` → `Verifying Citations` → `Complete`)
   - Draft auto-save indicator (`Draft saved locally at HH:MM:SS`)
3. **Visual Restraint & `prefers-reduced-motion`:**
   - All transitions respect `@media (prefers-reduced-motion: reduce)` by collapsing animation durations to `0ms`.
   - Zero continuous decorative spinners on idle screens; progress animations immediately stop when a job completes or fails.
