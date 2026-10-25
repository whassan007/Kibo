# KIBO Privacy OS — Phase 0: Target Enterprise Architecture

**Date:** 2026-10-25  
**Platform:** KIBO Privacy OS (`https://kibo.is`)  
**Architecture Pattern:** Modular Monolith with Versioned Legal Packs & Hybrid Neuro-Symbolic Execution

---

## 1. Architectural Principles

1. **Modular Monolith by Default**: A single authoritative FastAPI + SQLAlchemy 2.0 backend serves the KIBO Web Portal, Microsoft 365 Copilot, Claude Enterprise, Gemini Enterprise, and REST/MCP APIs.
2. **Hybrid Neuro-Symbolic Compliance**:
   - **Deterministic Symbolic Layer**: Versioned, legally reviewed canonical regulation packs and the **Jurisdictional Regulatory Applicability Engine (JRAE)** govern all enforceable compliance decisions, statutory thresholds, deadlines, preemption rules, and approval gates.
   - **Neural Layer (LangGraph + LLMs)**: Used for intake classification, document extraction, narrative drafting, RAG summarization, and regulatory change interpretation. LLMs **never** directly alter production legal obligations or bypass statutory rules.
3. **Strict Multi-Tenancy & Regional Data Residency**: Every database entity, RAG vector/search query, background job, and MCP tool invocation is bound to a verified `TenantContext` (`tenant_id`, `user_id`, `roles`, `scopes`, `residency_region`).
4. **Zero-LLM Graceful Degradation**: If all LLMs are offline or disabled, case management, JRAE applicability evaluation, statutory deadline calculations, workflows, and cryptographic audit logging continue to operate deterministically (Acceptance Test 15).

---

## 2. System Topology

```mermaid
flowchart TD
    subgraph Access["Corporate Access & Collaboration Hubs"]
        Web["KIBO Enterprise Web Portal (React/TS)"]
        M365["Microsoft 365 Copilot & Teams Agent"]
        Claude["Claude Enterprise (Remote MCP)"]
        Gemini["Gemini Enterprise (MCP / OpenAPI Extension)"]
        API["Enterprise REST APIs (/api/v1/*)"]
    end

    subgraph Gateway["Identity, Tenant Isolation & MCP Gateway"]
        Auth["OIDC / SAML / Entra ID / JWT Verifier"]
        TenantMW["TenantIsolationMiddleware (Strict ContextVar + RLS)"]
        RBAC["RBAC + ABAC Policy Engine & Scope Guard"]
        MCP["KIBO Privacy Office MCP Server (Read-Only Default + HITL Write)"]
    end

    subgraph Core["KIBO Privacy Office Engine (Modular Monolith)"]
        Admin["A. Privacy Office Admin & Governance"]
        Assess["B. Assessments (PIA, DPIA, TRA, TIA, LIA, AIIA)"]
        Breach["C. Incident & Breach Response Engine"]
        Rights["D. Privacy Rights / DSAR Engine"]
        RoPA["E. Data Inventory, RoPA & Transfers"]
        Consent["F. Consent, Notices & GPC Signals"]
        Vendor["G. Vendor Privacy, DPAs, BAAs & Subprocessors"]
        Risk["H. Enterprise Risk & Control Register"]
        RegIntel["I. Regulatory Intelligence & Change Impact"]
        Assistant["J. Governed Privacy Office Assistant"]
    end

    subgraph JRAE["Jurisdictional Regulatory Applicability Engine (JRAE)"]
        Registry["Global Jurisdiction Registry (US 50+DC+Fed, CA 13+Fed, EU 27+Union)"]
        Evaluator["Multi-Layer Applicability & Threshold Evaluator"]
        Conflict["Preemption, Conflict & Uncertainty Escalation Engine"]
        Deadline["State / Provincial / Member-State Deadline Calculator"]
        Packs["Versioned Canonical Legal Packs (YAML/JSON + SHA-256)"]
    end

    subgraph Execution["Hybrid Neuro-Symbolic Execution & Persistence"]
        Ontology["W3C JSON-LD Legal Ontology & Graph Store"]
        LangGraph["LangGraph Orchestrator + HITL Checkpoints"]
        DGX["Model Gateway (DGX Spark Ollama / Cloud LLM / Offline Fallback)"]
        DB[("PostgreSQL 16 / SQLite Test Engine")]
        Audit[("SHA-256 Hash-Chained Audit Ledger")]
    end

    Access --> Gateway
    Gateway --> Core
    Core --> JRAE
    Core --> Execution
    JRAE --> Packs
    JRAE --> Ontology
    Execution --> DB
    Execution --> Audit
    Execution --> DGX
```

---

## 3. Jurisdictional Regulatory Applicability Engine (JRAE) Design

### 3.1 Canonical Regulation Data Model (`kibo-is/core/jrae/schemas.py`)

Every regulation and statutory obligation is represented as a versioned, deterministic `CanonicalRegulation` object:

- **Identity & Provenance**: `regulation_id`, `jurisdiction_id`, `jurisdiction_type` (`supranational`, `federal`, `state`, `province`, `territory`, `member_state`, `subnational`, `sectoral`), `country`, `state_or_province`, `member_state`, `legal_authority`, `legal_instrument`, `official_source_url`, `source_document_hash`, `article_or_section`, `original_language`, `verified_translation`.
- **Lifecycle & Governance**:
  - `effective_date`, `repeal_date`, `transition_period_end`, `last_verified_at`, `rule_version`.
  - `regulatory_status`: `proposed` | `enacted_not_effective` | `effective` | `amended` | `repealed` | `superseded` | `under_legal_review`.
  - `deployment_status`: `discovered` | `parsed` | `tested` | `legally_reviewed` | `approved` | `production_enabled`.
  - `legal_review_status`: `pending` | `verified` | `requires_counsel_signoff` | `rejected`.
- **Applicability Predicates**:
  - `applicability_conditions`: Structured boolean/threshold rules over `organization_types` (`private`, `public`, `nonprofit`, `government_agency`, `healthcare_covered_entity`, `business_associate`, `health_information_custodian`, `financial_institution`), `industry_sectors`, `establishments`, `subject_locations`, `processing_locations`, `transfer_destinations`, `data_subject_categories`, `data_categories`, `processing_activities`, `roles` (`controller`, `processor`, `service_provider`, `third_party`).
  - `thresholds`: Revenue thresholds (e.g., CCPA `$25M` / `$26.625M` adjusted), consumer/resident record count thresholds (e.g., `100,000` consumers, `25,000` with revenue share), employee count (only where legally specified, never assumed universal).
  - `exemptions`: Entity-level exemptions (e.g., GLBA entity exemption vs data-level exemption, nonprofit exemption, HIPAA PHI exemption, B2B/employee exemptions).
  - `preemption_rules`: Federal preemption, Canadian provincial substantial similarity (`AB PIPA`, `BC PIPA`, `QC Law 25`, `ON PHIPA` vs `PIPEDA` intraprovincial/interprovincial split), EU GDPR opening clauses (Arts. 6(2), 8, 9(4), 88).
- **Enforceable Outputs**:
  - `required_actions`, `required_assessments` (`PIA`, `DPIA`, `TRA`, `TIA`, `LIA`, `AIIA`, `ROPA`, `VENDOR_ASSESSMENT`), `response_deadlines` (DSAR initial, extension, appeal; breach regulator, AG, individual), `notification_requirements`, `required_evidence`, `approval_requirements`, `competent_regulator` (including subnational routing such as German Länder DPAs).

### 3.2 Evaluation Pipeline (`POST /api/v1/compliance/applicability/evaluate`)

1. **Candidate Selection**: Resolve all candidate regulations matching any of the organization's `establishments`, `subject_locations`, `processing_locations`, or `transfer_destinations`, plus parent federal/supranational regimes (`US-FED`, `CA-FED`, `EU`).
2. **Lifecycle Filtering**:
   - Exclude `repealed` or `superseded` laws.
   - Separate `enacted_not_effective` or `proposed` rules into `future_preparation_obligations` (Acceptance Test 13) so they never masquerade as current legal mandates.
   - Only treat rules with `deployment_status == "production_enabled"` and `legal_review_status == "verified"` as production-authoritative; flag unverified rules with `requires_legal_review = True`.
3. **Nexus & Scope Testing**:
   - Evaluate territorial establishment vs extraterritorial targeting/offering (e.g., GDPR Art. 3(1) vs Art. 3(2); Quebec Law 25 nexus; California doing-business + subject residence). Never assume residence or nationality alone triggers GDPR or state law without statutory nexus (Acceptance Test 9).
4. **Threshold & Exemption Evaluation**:
   - Test statutory thresholds (revenue, consumer volume, data broker status). Missing fact inputs required to evaluate a threshold produce `unresolved_questions` and set `requires_legal_review = True`.
   - Apply entity-level and data-level exemptions (e.g., HIPAA PHI exemption under state consumer privacy laws vs non-HIPAA health data under WA MHMDA).
5. **Preemption & Conflict Resolution**:
   - Apply explicit statutory preemption (e.g., PIPEDA yielding to QC Law 25 / AB PIPA / BC PIPA for intraprovincial commercial activity while remaining applicable to interprovincial/international commercial transfers or federal works/undertakings).
   - Detect overlapping or conflicting deadlines/obligations across simultaneously applicable regimes, surface all sources, compute the strictest operational deadline for workflow scheduling while preserving per-jurisdiction statutory deadlines, and flag material legal conflicts with `requires_legal_review = True` (Acceptance Test 14).
6. **Competent Authority & Subnational Routing**:
   - Identify all competent regulators (e.g., HHS OCR + CalPrivacy + CA AG for California hospital; CNIL for France; DPC for Ireland with One-Stop-Shop lead authority evaluation; German Landesbeauftragte für Datenschutz by federal state + BfDI for federal/telecom).

---

## 4. Database & Persistence Architecture

- **Primary Database Engine**: SQLAlchemy 2.0 configured via `DATABASE_URL` environment variable:
  - Production / Staging: `postgresql+psycopg2://kibo:...@postgres:5432/kibo_privacy_os`
  - Local Dev / Standalone CI: `sqlite:///kibo_state.db` with WAL journaling and foreign key enforcement.
- **Unified Declarative Registry**: All models inherit from `core.models.base.Base` (`TenantScoped`, `VersionedEntity`, `Timestamped`).
- **Cryptographic Audit Ledger**: Every state mutation across assessments, incidents, DSARs, rules, and approvals appends an immutable record to `audit_logs` with `previous_hash` and `entry_hash` (`SHA-256`).
