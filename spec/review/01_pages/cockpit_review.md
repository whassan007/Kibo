# WP-1: Cockpit UI/UX Review

| Field | Details |
|---|---|
| **Title** | UI-001: Missing Offline Degraded State in Expert Dashboard |
| **Category** | UX / Frontend |
| **Problem** | The main dashboard component relies on synchronous data fetches on mount. If the DGX models or backend API (`100.113.62.112`) are unreachable, the UI fails to render a graceful degraded state, leaving the user with a blank white screen instead of the mandated dark monochrome E-ink design empty state. |
| **Recommendation** | Implement an `OfflineBanner` component that catches `fetch` boundaries. Switch to stale-while-revalidate caching and render a cached E-ink skeleton when network is down. |
| **Business Value** | Prevents panic for CPOs and Experts when the local fleet drops connectivity. Ensures continued read access to cached compliance states. |
| **Technical Complexity** | Med |
| **Priority** | Critical |
| **Estimated Effort** | M |
| **Dependencies** | Requires `kiboService` wrapper to emit offline events. |
| **Risks** | Potential state staleness if cache is mismanaged. |
| **TEST HOOK** | `tests/frontend/test_s1_resilience.py::test_offline_graceful_degradation` |

| Field | Details |
|---|---|
| **Title** | UI-002: Inconsistent Dark Monochrome Theming in Inputs |
| **Category** | UX |
| **Problem** | Form inputs in the onboarding wizard use default browser focus rings (blue) which break the strict E-ink monochrome aesthetic. Contrast on placeholder text (#767676) falls below WCAG 4.5:1 against the dark background (#121212). |
| **Recommendation** | Override `:focus-visible` to use a stark `#FFFFFF` ring. Lighten placeholder text to `#A0A0A0` for WCAG AA compliance. |
| **Business Value** | Enterprise visual consistency and strict adherence to accessibility laws for internal tools. |
| **Technical Complexity** | Low |
| **Priority** | High |
| **Estimated Effort** | S |
| **Dependencies** | None |
| **Risks** | None |
| **TEST HOOK** | `tests/e2e/test_gt7_persona_crawl.py::test_contrast_ratios` |
