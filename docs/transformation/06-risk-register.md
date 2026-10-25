# KIBO Privacy OS — Phase 0: Enterprise Risk Register

**Date:** 2026-10-25  
**Platform:** KIBO Privacy OS (`https://kibo.is`)

---

## 1. Release & Architectural Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Mitigation & Control | Status |
|---|---|---|---|---|---|---|
| **R-01** | Legal / Regulatory | Unverified LLM-parsed legal rules promoted to production as authoritative law. | Medium | Critical | Enforce strict dual state machines (`regulatory_status` and `deployment_status`). Only rules with `deployment_status == "production_enabled"` and `legal_review_status == "verified"` can drive authoritative decisions; all others return `requires_legal_review = True`. | Mitigated in JRAE schema |
| **R-02** | Legal / Applicability | Generic country/region checklists applied without testing thresholds, exemptions, or extraterritorial nexus (e.g., assuming GDPR applies solely from nationality or assuming a 5-employee onboarding filter is a statutory threshold). | High | Critical | JRAE evaluates establishment, targeting/offering nexus, revenue/consumer count thresholds, sector, role, and exemptions independently per statute. | Mitigated in JRAE engine |
| **R-03** | Security / Multi-Tenancy | Cross-tenant data leakage through SQL queries, MCP tool invocations, or AI/RAG context retrieval. | Low | Critical | Enforce `TenantIsolationMiddleware`, mandatory `tenant_id` scoping on all repositories, and explicit tenant context verification in MCP and assistant endpoints (tested in Acceptance Test 11). | Mitigated & Tested |
| **R-04** | Reliability / AI Dependency | Outage of local or cloud LLM blocks incident reporting, deadline calculation, or DSAR tracking. | Medium | High | Hybrid neuro-symbolic design: JRAE, statutory deadline engine, case management, and audit ledger are 100% deterministic Python rules that run with zero LLM dependency (tested in Acceptance Test 15). | Mitigated & Tested |
| **R-05** | Legal / Preemption & Conflict | Simultaneous application of conflicting laws (e.g., PIPEDA vs Quebec Law 25 vs Ontario PHIPA, or US state law vs HIPAA, or conflicting retention vs deletion mandates). | High | High | JRAE preemption and conflict detector surfaces both legal sources, applies codified substantial-similarity / sectoral exemptions where unambiguous, and routes unresolved conflicts to human legal review (`requires_legal_review = True`, Acceptance Test 14). | Mitigated in JRAE engine |
| **R-06** | Legal / Effective Dates | Enacted laws not yet in force (or transition provisions) enforced as immediate compliance violations. | Medium | High | JRAE compares `effective_date` and `transition_period_end` against evaluation date, separating `present_obligations` from `future_preparation_tasks` (Acceptance Test 13). | Mitigated in JRAE engine |
| **R-07** | Technical / Database | SQLAlchemy declarative base collision (`Vendor` defined twice in `core/models/assets.py` and `core/modules/vendor_risk/models.py`) breaking ORM initialization. | High | High | Unify `Vendor` model in `core/models/assets.py` with full backward-compatible fields and re-export in `core/modules/vendor_risk/models.py`. | Mitigated in Phase 1 |
| **R-08** | Operational / Breach Notification | Automated dispatch of regulatory breach notifications without human legal counsel sign-off. | Low | Critical | Hard architectural guardrail: all regulator and data subject notifications are created in `draft_pending_approval` state and require explicit `LEGAL` / `CPO` / `DPO` human approval before dispatch (Acceptance Test 8). | Mitigated in Breach Engine |
