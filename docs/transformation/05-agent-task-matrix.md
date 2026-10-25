# KIBO Privacy OS — Phase 0: Distributed Agent Task Matrix

**Date:** 2026-10-25  
**Orchestrator:** Antigravity (A0)

---

## 1. Agent Allocation & File Ownership Contracts

To prevent concurrent modification conflicts, each agent is assigned strict file ownership boundaries and isolated worktrees/branches where applicable.

| Agent ID | Runtime & Host | Role | Branch / Worktree | Owned Paths & Deliverables |
|---|---|---|---|---|
| **A0** | Antigravity (Primary) | Chief Architect, JRAE Core Contract & Final Integration | `main` | `docs/transformation/*`, `kibo-is/core/jrae/__init__.py`, `kibo-is/core/jrae/schemas.py`, final integration & verification |
| **A1** | Claude Code (Laptop CLI) | US Federal & 50-State + DC Regulatory Framework | `worktree-a1-us` (`kibo-is/core/regulatory_packs/us_*.py`) | `kibo-is/core/regulatory_packs/us_federal.py`, `kibo-is/core/regulatory_packs/us_states.py` |
| **A2** | Claude Code (Laptop CLI) | Canadian Federal, 10 Provinces & 3 Territories Framework | `worktree-a2-ca` (`kibo-is/core/regulatory_packs/canada.py`) | `kibo-is/core/regulatory_packs/canada.py` |
| **A3** | Claude Code (Laptop CLI) | EU-Wide & 27 Member-State Regulatory Framework | `worktree-a3-eu` (`kibo-is/core/regulatory_packs/eu.py`) | `kibo-is/core/regulatory_packs/eu.py` |
| **A4** | Codex CLI (Laptop) | Backend, Database Unification & JRAE Engine | `worktree-a4-backend` | `kibo-is/core/models/assets.py`, `kibo-is/core/modules/vendor_risk/models.py`, `kibo-is/core/jrae/engine.py`, `kibo-is/core/jrae/deadlines.py`, `kibo-is/core/jrae/registry.py` |
| **A5** | Codex CLI (Laptop) | Identity, OIDC/SAML, RBAC/ABAC & Tenant Isolation | `worktree-a5-security` | `kibo-is/core/security/auth.py`, `kibo-is/core/security/rbac.py`, `kibo-is/core/middleware/tenant_isolation.py` |
| **A6** | DGX Spark (`ssh dgx`) | Local LLMs, Ontology Consistency, RAG & Benchmark Eval | `dgx:/tmp/kibo-eval` → `kibo-is/core/eval/` | `kibo-is/core/eval/dgx_evaluator.py`, `kibo-is/core/eval/benchmark_results.json` |
| **A7** | Antigravity Subagent | Privacy Assessments, DSAR Rights, RoPA & Consent | `kibo-is/core/office/assessments_rights.py` | `kibo-is/core/office/assessments_rights.py` |
| **A8** | Antigravity Subagent | Breach/Incident, Governance, Vendor, Risk, RegIntel & Assistant | `kibo-is/core/office/breach_governance.py` | `kibo-is/core/office/breach_governance.py` |
| **A9** | Antigravity Subagent | React Enterprise Portal & Multi-Jurisdiction UI | `kibo-is/src/` | `kibo-is/src/views/PrivacyOSPortal.tsx`, `kibo-is/src/services/privacyOsService.ts` |
| **A10** | Antigravity Subagent | Corporate AI Hubs (M365 Copilot, Claude MCP, Gemini) | `kibo-is/integrations/`, `.kibo/tools/kibo_mcp.py` | `kibo-is/integrations/m365_copilot/*`, `kibo-is/integrations/claude_mcp/*`, `kibo-is/integrations/gemini_enterprise/*`, `.kibo/tools/kibo_mcp.py` |
| **A11** | Antigravity Subagent | DevOps, Docker/Postgres, 15 Acceptance Tests & Release | `kibo-is/tests/test_acceptance_15.py`, `docker-compose.yml` | `kibo-is/tests/test_acceptance_15.py`, `docker-compose.yml`, `Dockerfile`, `docs/transformation/*.csv` |

---

## 2. Interface Verification Protocol

1. **Schema Lock First**: A0 writes `kibo-is/core/jrae/schemas.py` before launching A1, A2, A3, A4, A7, A8, A10.
2. **No Shared-File Contention**: Each agent writes to dedicated module files (`us_federal.py`, `us_states.py`, `canada.py`, `eu.py`, `assessments_rights.py`, `breach_governance.py`, etc.), which A0 mounts into `agent_gateway.py`.
3. **Verifiable Telemetry**: Every agent execution logs its start/end time, commit SHA, files changed, tests executed, pass/fail counts, and resource usage into `docs/transformation/AGENT-EXECUTION-LOG.csv`.
