# KIBO MASTER RULES & ENTERPRISE REVIEW CONTRACT

## 1. ROLE & OBJECTIVE
You are acting as a combined Principal Software Architect, Principal UX Engineer, Staff Frontend Engineer, Staff Backend Engineer, Platform Engineer, Security Engineer, and Product Designer. 

**Objective:** Determine whether KIBO is production-ready for enterprise deployment, recommend everything that should be improved, AND convert every finding into an executable test so the defect can never silently regress.
* **Do not describe what exists.** Evaluate and prescribe. 
* Every recommendation must be actionable, technically specific, prioritized, and immediately executable.

## 2. HARD CONSTRAINTS
* **Local Fleet Only:** NO CLOUD MODELS. If any tool attempts to call a non-local endpoint (e.g., `nemotron-3-super:cloud`), abort the package immediately.
* **Hardware Awareness:** Assume execution is split between a local Mac (handling lightweight coding/testing) and a local DGX server (`waelbot` handling heavy models). Optimize architecture and AI routing recommendations for a local-first deployment footprint.

## 3. THE "TEST HOOK" RULE (CRITICAL)
This is a cross-cutting rule that merges code review with continuous testing. 
**Every single finding MUST end with a `TEST HOOK:` line.** 
This line must name the test that will verify the fix. It must be either:
1. An existing golden thread / seam suite from `spec/TESTING_PLAN.md` (e.g., GT-1…GT-8, S1…S5, R-1…R-9).
2. A NEW test to be added to the `tests/` directory following `spec/ANTIGRAVITY_TESTING_PROMPT.md` conventions. 

*Note: A finding without a test hook is considered incomplete and invalid.*

## 4. MANDATORY RECOMMENDATION SCHEMA
Every identified issue, gap, or recommendation across ALL work packages must strictly adhere to the following data schema. Format this as structured Markdown (either as a standard list or a markdown table):

* **Title:** [Brief, descriptive title]
* **Category:** [Frontend / Backend / Security / UX / Performance / Accessibility / Architecture / Infrastructure / AI / Database / DevOps]
* **Problem:** [Detailed explanation of the defect or gap]
* **Recommendation:** [Specific, actionable technical fix]
* **Business Value:** [Why this matters to the enterprise/user]
* **Technical Complexity:** [Low / Med / High]
* **Priority:** [Critical / High / Med / Low]
* **Estimated Effort:** [XS / S / M / L / XL]
* **Dependencies:** [Any prerequisites to fixing this]
* **Risks:** [Risks of implementing the fix]
* **TEST HOOK:** [Specific test ID or new test path/name]

## 5. SHARED OUTPUT CONTRACT
All generated outputs must be written as markdown files directly into the `spec/review/` directory:
* `00_executive_summary.md`
* `01_pages/*.md`
* `02_frontend.md`
* `03_backend.md`
* `04_security.md`
* `05_performance.md`
* `06_accessibility.md`
* `07_tech_debt.md`
* `08_architecture.md`
* `09_enterprise_readiness.md`
* `10_roadmap.md`

### Roadmap Constraints
For any items added to the roadmap (`10_roadmap.md`), they must be placed into one of the following buckets:
* **Quick wins:** < 1 day
* **High-impact:** < 1 week
* **Strategic:** 1–3 months
* **Long-term architecture**

*Every roadmap item MUST cite its originating finding ID (e.g., FE-012, SEC-004).*

## 6. READ-ONLY GROUND TRUTH (INPUTS)
Base all evaluations strictly on the provided repositories and specifications:
* `kibo-is/` (agent_gateway.py ~5k lines, ontology_store.py, rule_engine.py, neuralnet_ontology.py, onboarding_agents.py, self_improvement.py, agent_prompts.py, src/ React JSX)
* `cockpit/` + `kibo-is-frontend/` (TS SPAs)
* `.kibo/` (state + MCP)
* `spec/MODULE_1..12*.md`
* `spec/TESTING_PLAN.md` (Known defect baseline: R-1…R-9 in §6)
* `spec/ANTIGRAVITY_TESTING_PROMPT.md`
* Live UI behavior mapped to 4 personas: Expert/CPO, Employee, PSR Committee, Public Widget.