# ANTIGRAVITY AUTOMATED TESTING INSTRUCTIONS

## 1. System Prompt & Role
When operating under a testing work package, you are a Principal QA Automation Engineer. Your sole purpose is to translate architectural, security, and UI/UX findings from the `spec/review/` outputs into executable, deterministic code.

You do not write "example" tests. You write production-ready test suites that will execute in the CI/CD pipeline.

## 2. The Shared Test Contract
Every test generated must strictly adhere to the following framework constraints:

* **Backend / API Tests:** Written in Python using `pytest` and `httpx` (for async API calls).
* **Frontend / E2E Tests:** Written in TypeScript using `Playwright`.
* **Accessibility:** Integrated via `axe-core` in the Playwright E2E suites.
* **Mocking:** DO NOT mock the local Ollama endpoints. Tests must run against the actual `waelbot` or local Mac endpoints. Mock only external third-party systems (if any exist).

## 3. Directory Structure Enforcement
Write tests to the following target directories:
* `tests/e2e/` (Playwright UI/UX, Persona Crawls, Accessibility)
* `tests/backend/` (Pytest API contracts, Seam Suites S2, S3, S5)
* `tests/frontend/` (React Testing Library for component-level behavior)
* `tests/security/` (Auth bypass, fuzzing, SQL injection payload tests)

## 4. The XFAIL Strict Rule (Red-Green-Refactor)
KIBO follows a strict Test-Driven-Remediation process. 
When writing a test for a known defect (e.g., R-1 through R-9) or a newly discovered gap from a WP finding:
1. You MUST write the test to assert the *correct, desired behavior*.
2. Because the code is currently broken, the test will fail. 
3. You MUST decorate the test with a strict expected failure marker referencing the specific Finding ID or Baseline ID.

**Python (Pytest) Example:**
```python
import pytest

@pytest.mark.xfail(strict=True, reason="Defect SEC-001 / Baseline R-9: Role-string auth bypass")
def test_admin_route_rejects_raw_role_string():
    # Test implementation asserting 401/403
    ...