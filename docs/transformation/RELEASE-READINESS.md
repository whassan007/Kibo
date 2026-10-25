# KIBO Privacy OS — Production Release Readiness & Deployment Runbook

**Platform:** KIBO Privacy OS (`https://kibo.is`)  
**Release Version:** `2026.10.1`  
**Status:** **READY FOR STAGING & PRODUCTION CUTOVER (68/68 Tests Passing)**  

---

## 1. Release Gate Checklist

| Gate | Requirement | Status | Verification Command / Artifact |
| :--- | :--- | :--- | :--- |
| **G1. 15 Mandatory Acceptance Tests** | All 15 multi-jurisdictional acceptance scenarios pass (`US`, `CA`, `EU`, Breach, DSAR, RegChange, Tenant Isolation, Copilot, Future Law, Conflicts, LLM Offline) | **PASS (15/15)** | `pytest kibo-is/tests/test_acceptance_15.py -v` |
| **G2. Core Backend Regression Suite** | All 53 existing unit tests (Audit, DSAR, Event-Driven, Models, Multitenancy, Phase 3, Vendor Risk) pass alongside new modules | **PASS (53/53)** | `pytest kibo-is/tests -v` (`68 passed in 1.48s`) |
| **G3. KIBO OS State & URI Contract** | Schema validation, `kibo://` URI resolution, weekly brief KPIs, and down-state read-only enforcement pass | **PASS (4/4)** | `python3 .kibo/tools/test_suite.py` |
| **G4. DGX Spark GPU Benchmark** | Multi-jurisdictional regulatory reasoning benchmark evaluated on DGX Spark (`waelbot`, NVIDIA GB10, `gemma4:26b`) | **PASS (5/5)** | [`kibo-is/core/eval/benchmark_results.json`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/eval/benchmark_results.json) |
| **G5. Frontend Production Build** | React 19 + TypeScript + Vite 8 production bundle compiles cleanly with `/privacy-os` portal | **PASS** | `cd kibo-is && npm run build` (`448ms`) |
| **G6. Human Legal Approval Safeguards** | External regulatory breach notifications and production regulatory rule amendments cannot execute without human `LEGAL`/`CPO`/`DPO` sign-off | **ENFORCED** | Verified in Acceptance Tests 8, 10, 12, 14, and 15 |
| **G7. Deterministic Offline Mode** | Core applicability, deadlines, assessments, DSAR, breach triage, and audit trails operate 100% deterministically when `KIBO_DISABLE_LLMS=1` | **ENFORCED** | Verified in Acceptance Test 15 |

---

## 2. Production Deployment Architecture

KIBO Privacy OS deploys as a **containerized modular monolith** backed by PostgreSQL 16 and Redis 7 (`docker-compose.yml` and `Dockerfile`):

- **API & Orchestration Service (`kibo-api`)**:
  - FastAPI application (`kibo-is/agent_gateway.py`) exposing **238 routes** including `/api/v1/compliance/*`, `/api/v1/office/*`, and `/api/v1/integrations/*`.
  - Connects to PostgreSQL 16 via `DATABASE_URL` (`postgresql+psycopg2://...`) with automatic fallback to SQLite for local/isolated testing.
- **Database (`kibo-postgres`)**:
  - PostgreSQL 16 (`postgres:16-alpine`) with persistent volume `kibo_pgdata` and healthcheck.
- **Queue / Cache (`kibo-redis`)**:
  - Redis 7 (`redis:7-alpine`) with AOF persistence for background tasks and rate limiting.
- **GPU Inference & Regulatory Evaluation Node (`dgx` / `waelbot`)**:
  - Optional remote Ollama endpoint (`OLLAMA_DGX_URL`) for large-model regulatory ingestion and evaluation; all compliance decisions remain grounded in deterministic JRAE rules.

---

## 3. Staging & Production Cutover Runbook

### Step 1: Pre-Cutover Verification
```bash
# 1. Run full backend + acceptance test suite
pytest kibo-is/tests -v

# 2. Run KIBO OS scaffold verification
python3 .kibo/tools/test_suite.py

# 3. Build production frontend bundle
cd kibo-is && npm run build && cd ..
```

### Step 2: Containerized Stack Startup
```bash
# Build and launch PostgreSQL 16, Redis 7, and KIBO Privacy OS API
docker compose up -d --build

# Verify health and loaded regulatory packs
curl -s http://localhost:8000/api/v1/compliance/jurisdictions | jq '.total_jurisdictions, .total_regulations'
curl -s http://localhost:8000/api/v1/integrations/status | jq '.status, .approved_tools_count'
```

### Step 3: Corporate AI Hub Registration
1. **Microsoft 365 Copilot & Teams**: Upload package from [`kibo-is/integrations/m365_copilot/`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/integrations/m365_copilot/manifest.json) in Microsoft 365 Admin Center -> Integrated Apps.
2. **Claude Enterprise MCP**: Register [`kibo-is/integrations/claude_mcp/kibo_privacy_mcp.py`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/integrations/claude_mcp/kibo_privacy_mcp.py) (`stdio` or `/api/v1/integrations/mcp/invoke` HTTP JSON-RPC).
3. **Google Gemini Enterprise**: Import [`kibo-is/integrations/gemini_enterprise/gemini_extension.json`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/integrations/gemini_enterprise/gemini_extension.json) in Google Cloud Vertex AI / Gemini Enterprise Extensions.

---

## 4. Rollback Plan

1. **Application Rollback**:
   - Revert container image tag to previous commit SHA (`docker compose down && git checkout <prev-tag> && docker compose up -d`).
2. **Regulatory Rule Rollback**:
   - Every `CanonicalRegulation` carries an explicit `rule_version` (`2026.10.1`) and `deployment_status`. If a specific rule pack requires suspension, set its `deployment_status` to `DeploymentStatus.UNDER_LEGAL_REVIEW` or revert via `POST /api/v1/office/regulatory-intelligence/amendments`.
3. **LLM / AI Hub Isolation Switch**:
   - Set `KIBO_DISABLE_LLMS=1` in environment variables to immediately force 100% deterministic rule evaluation while keeping all Privacy Office workflows operational.
