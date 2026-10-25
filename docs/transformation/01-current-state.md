# KIBO Privacy OS — Phase 0: Current-State Architecture & Capability Inventory

**Date:** 2026-10-25  
**Repository:** `https://github.com/whassan007/Kibo` (`kibo-is/`)  
**Platform:** KIBO Privacy OS (`https://kibo.is`)  
**Role:** Principal Architect & Autonomous Orchestrator (A0)

---

## 1. Executive Summary

KIBO currently exists as a multi-project monorepo combining a FastAPI + LangGraph privacy workflow engine (`kibo-is/`), an operator cockpit (`cockpit/`), a partial TypeScript frontend migration (`kibo-is-frontend/`), an MCP state surface (`.kibo/`), and a prompt-only library of regional CPO skills (`cpo-agents/`).

While the repository contains foundational elements for ontology-based routing, LangGraph human-in-the-loop (HITL) orchestration, DSAR lifecycle services, vendor risk assessments, audit logging, and multi-tenant middleware, **it is not yet a production-grade, multi-jurisdictional Privacy Office Operating System**. Critical defects currently prevent the unit test suite from passing (e.g., duplicate `Vendor` SQLAlchemy declarative classes causing mapper registry failures), regulatory rules are limited to 4 static demo JSON files (`PIPEDA`, `Ontario FIPPA`, `EU GDPR`, `US CPRA`) plus a 7-jurisdiction SQLite ontology, and there is no deterministic **Jurisdictional Regulatory Applicability Engine (JRAE)** capable of evaluating multi-layered federal, state, provincial, territorial, EU member-state, and sector-specific legal obligations.

---

## 2. Existing Repository Inventory

### 2.1 Backend (`kibo-is/`)
| Component | Path | Current Implementation Status |
|---|---|---|
| API Gateway & LangGraph | `kibo-is/agent_gateway.py` (6,894 LOC) | Monolithic FastAPI app combining raw SQLite queries (`kibo_state.db`), SQLAlchemy ORM sessions, LangGraph compliance workflow (`phipa_tra_node`, `law25_tia_node`, `law25_pia_node`, `article35_dpia_node`, `cpra_admt_node`, `node_quantify_fair_risk`, `node_human_approval`), and 140+ endpoints. |
| Regulatory Ontology | `kibo-is/ontology_store.py`, `neuralnet_ontology.py` | SQLite tables (`ontology_classes`, `ontology_instances`, `ontology_edges`, `ontology_change_log`) with JSON-LD import/export and 2-hop graph routing (`derive_compliance_routing`). Currently seeds only 7 jurisdictions (`CA_Federal`, `EU_Union`, `Quebec`, `Ontario`, `California`, `Virginia`, `Texas`). |
| Rule Engine | `kibo-is/rule_engine.py`, `rules.json` | Simple flat dictionary string matcher (`client`, `type`, `jurisdiction`) for auto-approving HITL transactions. Not a statutory applicability or deadline calculation engine. |
| Core Domain Models | `kibo-is/core/models/` | SQLAlchemy 2.0 models (`Base`, `VersionedEntity`, `TenantScoped`, `Timestamped`) covering `Asset`, `System`, `Vendor`, `DataElement`, `Process`, `Assessment` (`PIAssessment`, `DPIAssessment`, `TIAssessment`), `Risk`, `Control`, `Contract`, `Tenant`, `TenantMembership`, `AuditLog`, `EntityVersion`, `DataSubjectAccessRequest`, `VendorRiskAssessment`, `DataProcessingAgreement`, `SubprocessorRegistry`. |
| Duplicate Legacy Modules | `kibo-is/core/modules/vendor_risk/models.py` | Defines a second `Vendor` class on the same SQLAlchemy `Base` registry as `core/models/assets.py`, breaking SQLAlchemy mapper initialization across all ORM tests. |
| Multi-Tenancy & Context | `kibo-is/core/middleware/tenant_isolation.py`, `core/context/tenant_context.py` | `TenantIsolationMiddleware` extracts `X-Tenant-ID` and `X-User-ID` (or Bearer JWT), validates `Tenant` and `TenantMembership`, and binds `ContextVar` state. However, legacy raw-SQLite endpoints in `agent_gateway.py` bypass SQLAlchemy tenant scoping. |
| Authentication & RBAC | `kibo-is/agent_gateway.py`, `core/security/permissions.py` | `agent_gateway.py` accepts raw role strings as Bearer tokens (`Bearer CPO`) and defaults unauthenticated calls to `UserRole.CPO`. Lacks production OIDC/SAML/JWT verification and strict ABAC enforcement. |
| Event Bus & Audit | `kibo-is/core/events/`, `core/audit/` | `InMemoryEventBus`, `RedisEventBus`, `EventProcessor`, `AuditService`, SHA-256 hash-chained `AuditLog`, temporal entity versioning (`EntityVersion`), and `AuditMiddleware`. |
| Onboarding & Self-Improvement | `kibo-is/onboarding_agents.py`, `self_improvement.py`, `extractors/`, `normalization/` | LangGraph onboarding pipeline (website/document/system extraction → profile normalization → gap detection) and bounded RAG self-improvement loop with human approval gate. |
| Regulatory Feeds & Verdicts | `kibo-is/sources_sync_agent.py`, `canadian_verdicts_agent.py`, `legalnet_grow_agent.py` | Background threads syncing `Sources.md` and Canadian commissioner verdicts into SQLite. |
| ML & Analytics | `kibo-is/core/analytics/`, `core/ml/` | IsolationForest anomaly detection, risk prediction, control recommendation, and approver routing scaffolds. |

### 2.2 Frontends & Static Portal
| Component | Path | Current Implementation Status |
|---|---|---|
| Primary Compliance SPA | `kibo-is/src/` | Vite + React (TypeScript shell wrapping `src/legacy/App.jsx` + `modes/PublicMode.jsx`, `EmployeeMode.jsx`, `ExpertMode.jsx`, `PsrMode.jsx`, `AdminMode.jsx` and modern TS views `src/views/PrivacyInbox.tsx`, `DataInventoryForm.tsx`, `FOISubmitForm.tsx`, `HitlQueue.tsx`, `TrustTiers.tsx`). |
| Operator Cockpit | `cockpit/` | React/TypeScript SPA reading `.kibo/state/` YAML/JSON files. |
| Duplicate Frontend | `kibo-is-frontend/` | Partial copy of `kibo-is/src/` with only `/inbox` and `/widget` routes wired in `App.tsx`. |
| Marketing & Docs Site | Root `*.html`, `css/`, `js/`, `website-static/` | Static HTML landing pages (`index.html`, `app.html`, `login.html`, `signup.html`, `dpa.html`, `privacy.html`, `trust.html`). |

### 2.3 MCP & Agent Libraries
| Component | Path | Current Implementation Status |
|---|---|---|
| KIBO OS FastMCP Server | `.kibo/tools/kibo_mcp.py`, `kibo_surface.py` | Exposes `.kibo/state/` resources and governance tools (`proposal.create`, `queue.resolve`, etc.), hardcoded to `/Users/iceman/Documents/Code/Kibo`. Does not expose Privacy Office operational tools (JRAE applicability, incident intake, DSAR, vendor lookup, policy search). |
| CPO Agent & Skill Library | `cpo-agents/` | Markdown prompt/skill definitions for US, Canada, EU across 5 domains plus HIPAA, SOC2, ISO 27701, Infoway HTRA. Not compiled into machine-readable, versioned canonical regulation packs. |

---

## 3. Disposition Matrix (Retain, Refactor, Replace, Integrate, Delete)

Per Section 2 of the Master Prompt, we do not build a second system alongside the existing one. Every existing component is dispositioned as follows:

### 3.1 RETAIN
1. **SQLAlchemy Core Domain Models (`kibo-is/core/models/`)**: Retain `Base`, `VersionedEntity`, `TenantScoped`, `Timestamped`, `Asset`, `System`, `Vendor`, `DataElement`, `Process`, `Assessment`, `Risk`, `Control`, `Tenant`, `TenantMembership`, `AuditLog`, `EntityVersion`, `DataSubjectAccessRequest`, `DataProcessingAgreement`, `SubprocessorRegistry`.
2. **Audit Trail & Temporal Versioning (`kibo-is/core/audit/`)**: Retain `AuditService`, `ChangeTracker`, `TemporalQuery`, and `EvidenceExport`.
3. **Domain Event Bus (`kibo-is/core/events/`, `core/handlers/`)**: Retain `InMemoryEventBus` / `RedisEventBus` and `EventProcessor` for cross-module signal propagation.
4. **DSAR & Vendor Risk Services (`kibo-is/core/services/dsar_*.py`, `vendor_*.py`, `dpa_management_service.py`)**: Retain and wire into the jurisdiction-specific deadline and applicability engine.
5. **Onboarding & Self-Improvement Pipelines (`kibo-is/onboarding_agents.py`, `self_improvement.py`, `extractors/`, `normalization/`)**: Retain LangGraph pipelines and human approval gates.
6. **Ontology Graph Store (`kibo-is/ontology_store.py`)**: Retain W3C JSON-LD export/import and graph traversal, expanding it to link with the Canonical Regulation Model.

### 3.2 REFACTOR
1. **`kibo-is/agent_gateway.py`**: Refactor into a clean modular monolith (`kibo-is/core/api/` routers mounted on `agent_gateway.py`) while preserving all existing `/api/*` and `/api/v1/*` routes for backward compatibility. Fix database engine configuration to support PostgreSQL (`DATABASE_URL` env var) with SQLite fallback for local/offline testing.
2. **Multi-Tenancy & Identity (`kibo-is/core/middleware/tenant_isolation.py`, `core/security/`)**: Upgrade to production OIDC/SAML/JWT authentication, RBAC + ABAC policy enforcement, strict tenant isolation across all endpoints, MCP calls, and RAG queries (Acceptance Test 11), and remove unauthenticated `CPO` elevation in production mode.
3. **LangGraph Orchestration (`kibo-is/agent_gateway.py`)**: Ensure deterministic fallback when all LLMs are unavailable (Acceptance Test 15) so core case management, deterministic rules, statutory deadlines, and audit history operate uninterrupted.
4. **Primary React Portal (`kibo-is/src/`)**: Consolidate `kibo-is/src/` as the single authoritative enterprise web portal supporting Tenant Onboarding, Multi-Region Operating Dashboards, JRAE Applicability Evaluator, Assessments (PIA/DPIA/TRA/TIA/LIA/AIIA), Breach & Incident Response, Privacy Rights (DSAR), Data Inventory & RoPA, Consent & Preferences, Vendor Privacy Management, Risk & Control Register, Regulatory Intelligence & Legal Review, and the Governed Privacy Office Assistant.
5. **MCP Server (`.kibo/tools/kibo_mcp.py` & `kibo-is/core/integrations/mcp_server.py`)**: Fix hardcoded `/Users/iceman/...` paths and expose tenant-isolated, server-authorized corporate AI tools for Microsoft 365 Copilot, Claude Enterprise, and Gemini Enterprise.

### 3.3 REPLACE
1. **Toy Rule Engine (`kibo-is/rule_engine.py`, `cpra_rules.json`, `gdpr_rules.json`, `law25_rules.json`)**: Replace with the **Jurisdictional Regulatory Applicability Engine (JRAE)** (`kibo-is/core/jrae/`) and versioned **Canonical Regulation Model** (`kibo-is/core/regulatory_packs/`), while keeping a legacy adapter on `RuleEngine` so existing `/api/rules` callers do not break.
2. **Hardcoded 30/45-day DSAR & Breach Timers**: Replace with the **Multi-Jurisdictional Deadline & Threshold Engine** supporting US Federal + 50 States + DC + territories, Canada Federal + 10 Provinces + 3 Territories, and EU + 27 Member States.

### 3.4 INTEGRATE
1. **`cpo-agents/` Knowledge Base**: Extract statutory citations, thresholds, deadlines, exemptions, regulators, and assessment triggers from `cpo-agents/{us,canada,eu,compliance-frameworks}` into structured, versioned, testable regulatory packs (`kibo-is/core/regulatory_packs/`).
2. **DGX Spark (`dgx` / `waelbot`)**: Integrate local Ollama models (`qwen3.6:35b-a3b-q8_0`, `qwen3-coder:30b`, `gemma4:26b`) on DGX Spark for regulatory RAG evaluation, ontology consistency verification, and synthetic compliance benchmarking.

### 3.5 DELETE / DEPRECATE
1. **Duplicate `Vendor` SQLAlchemy Model in `kibo-is/core/modules/vendor_risk/models.py`**: Consolidate into `kibo-is/core/models/assets.py` (re-exporting from `core/modules/vendor_risk/models.py` for import compatibility) to eliminate the SQLAlchemy declarative registry collision.
2. **Legacy Duplicate Model Files (`kibo-is/core/models/dsar_scope.py`, `kibo-is/core/models/vendor_risk_assessment.py`)**: Remove duplicate unreferenced table definitions.
3. **Backup Clutter (`spec/review/tabs/backup/`, `kibo-is/src.legacy.bak/`)**: Exclude from active runtime build.
