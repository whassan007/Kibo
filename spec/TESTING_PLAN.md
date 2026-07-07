# KIBO TESTING PLAN & BASELINE

## 1. Overview
This document defines the quality assurance architecture for KIBO. It outlines the core End-to-End user journeys (Golden Threads), the critical system boundaries (Seam Suites), and the regression baseline of known architectural defects.

## 2. Golden Threads (E2E User Journeys)
Golden Threads (GT) represent the critical paths that must operate flawlessly across the full stack (Frontend -> Gateway -> Local AI Fleet -> Database).
* **GT-1: Ontology Onboarding:** E2E workflow from `onboarding_agents.py` scraping external context to populating the `neuralnet_ontology`.
* **GT-2: PSR Committee Approval:** The human-in-the-loop (HITL) breakpoint loop. Agent generates assessment -> CPO/Committee reviews -> overrides or approves -> `self_improvement.py` ingests feedback.
* **GT-3: AI Output Checkpoints:** Verifying that statutory agents (PHIPA/Law25/GDPR) return mathematically verifiable confidence scores and exact statutory citations, not generalized advice.
* **GT-4: Privacy Inbox Triaging:** Employee submission of a privacy request -> automatic classification -> routing to correct queue.
* **GT-5: Meetings Planner Integration:** E2E verification of scheduling, context retrieval, and summary generation.
* **GT-6: Security & RBAC Attack Cases:** Asserting that cross-tenant access, unauthorized role escalation, and direct endpoint manipulation fail.
* **GT-7: Persona Crawl:** Automated Playwright traversal of every view (Expert, Employee, PSR Committee, Public Widget) ensuring correct layout, state management, and 200 OK network responses.
* **GT-8: Public Widget Consent Flow:** Citizen-facing privacy interaction, verifying strict zero-cookie baseline and proper consent logging.

## 3. Seam Suites (Integration & Boundary Tests)
Seam Suites (S) isolate and test the boundaries between KIBO's internal modules and external dependencies.
* **S1: API Fetch Path Resilience:** Frontend-to-Backend contract fuzzing. Tests 500s, network timeouts, offline states, and malformed JSON payloads.
* **S2: Database Concurrency:** Tests the SQLite boundary. Spamming concurrent writes from `agent_gateway.py` and LangGraph checkpointing to expose lock failures.
* **S3: Local Fleet Router & Fallback:** Tests the model routing logic. Simulates DGX unreachability to ensure graceful degradation (or safe failure) without leaking to cloud models.
* **S4: External Scraping/MCP Boundary:** Tests the `onboarding_agents.py` tool server exposure and mitigates prompt-injection vectors from external data.
* **S5: File & State I/O:** Verifies the integrity, encryption, and permission scoping of the local `.kibo` state folder.

## 4. Frontend Resilience Rules
* **Rule 1:** UI must never block the main thread during heavy local model polling.
* **Rule 2:** Empty states, loading states, and error states must be explicitly designed and tested per view.

## 5. Security & AI Guardrails
* **Rule 1:** Zero Cloud. Any network request to OpenAI, Anthropic, or external hosted LLMs must trigger a hard test failure.
* **Rule 2:** PII/PHI must never be written to plaintext application logs.

## 6. Known Defect Baseline (Regression Register)
The following defects (R-1 through R-9) are documented realities of the current architecture. Tests written against these must use strict `xfail` until remediated.
* **R-1 (Frontend):** Hardcoded URLs (e.g., `100.113.62.112`) exist in client bundles instead of environment-based routing.
* **R-2 (Frontend):** Missing offline and degraded network states for API fetch calls.
* **R-3 (Backend):** The `db-lock` defect. `agent_gateway.py` async handlers writing synchronously to SQLite cause database locking under moderate concurrent load.
* **R-4 (AI/Router):** Token-count router fails ungracefully when the DGX node is unreachable.
* **R-5 (Backend):** Silent failures in API error handling (exceptions caught and ignored, returning 200 OK with empty arrays).
* **R-6 (Security/Data):** The "Ontology Wipe Incident." Write paths to `ontology_store.py` lack strict audit logging and overwrite protections.
* **R-7 (AI):** Mock-data fallbacks in `agent_gateway.py` can masquerade as live model outputs in production paths.
* **R-8 (Observability):** Pervasive use of standard `print()` statements instead of a structured logging/tracing framework.
* **R-9 (Security):** Authentication is currently bypassed using bearer-token-equals-role-string checks (Critical).