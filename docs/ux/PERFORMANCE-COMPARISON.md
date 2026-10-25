# KIBO Privacy OS — Performance & Bundle Size Comparison (`v2026.10.1`)

## 1. Empirical Frontend & Network Measurements

Measured via headless Chromium (`145.0.7632.6`) and Vite `v8.1.0` production build (`docs/ux/baseline_metrics.json` vs. `docs/ux/after_metrics.json`):

| Metric | Baseline (`Before`) | Hardened UX (`After`) | Delta / Improvement |
|---|---:|---:|---|
| **Primary Entry JS Bundle (`dist/assets/index-*.js`)** | `776,692 B` (`778.58 kB`) | `443,294 B` (`443.29 kB`) | **`-42.9%` (`-333.4 kB`)** via `React.lazy()` code-splitting |
| **Primary Entry Gzipped JS** | `195.37 kB` | `130.60 kB` | **`-33.2%` (`-64.77 kB`)** |
| **Automatic `POST` Mutations on Page Mount (`UX-15`)** | `5` unsolicited `POST` calls | `0` `POST` calls | **`-100%` (Zero surprise mutations)** |
| **Initial Workspace Load (`networkidle`)** | `1,622.3 ms` | `600.42 ms` | **`-63.0%` (`2.7x` faster)** |
| **1,020-Record Jurisdiction Scale Render & Pagination (`UX-14`)** | Unpaginated DOM render | `< 440 ms` paginated (`25/page`) | Zero frame drops; instant filtering |
| **Production Build Time (`vite build`)** | `411 ms` | `389 ms` | **`-5.4%`** |

---

## 2. DGX Spark (`waelbot` `aarch64`) Local Latency & Event Stress Benchmarks

Executed on `waelbot` (`aarch64`) and recorded in `docs/ux/dgx_d01_assistant_latency.json` and `docs/ux/dgx_d02_event_stress.json`:

1. **`D01` — 5-Stage Governed Assistant Pipeline Overhead**:
   - Stage 1 (`Understanding Organization Context`): `0.0087 ms`
   - Stage 2 (`Evaluating Jurisdictional Applicability`): `0.0055 ms`
   - Stage 3 (`Retrieving Verified Legal Sources & Citations`): `0.0047 ms`
   - Stage 4 (`Checking Internal Policies & Contractual DPAs`): `0.0046 ms`
   - Stage 5 (`Preparing Governed Recommendation`): `0.0036 ms`
   - Total deterministic orchestration overhead: **`0.723 ms`**.
2. **`D02` — 5,000-Event SSE Storm & Deduplication Stress Test**:
   - Ingested `5,000` rapid SSE events (`1,000` unique IDs + `4,000` duplicate frames).
   - Retained `1,000` unique events and dropped `4,000` duplicates in **`0.678 ms`** with zero memory leak.
