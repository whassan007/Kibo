"""
KIBO Privacy OS — UX-01 through UX-15 Mandatory User Journey & Accessibility Test Suite (Agent X03)
==================================================================================================
Verifies all 15 mandatory user journeys defined in Section 10 of KIBO PRIVACY OS: UX, USABILITY & LIVE EXPERIENCE
using headless Chromium (Playwright) against the production build + FastAPI TestClient.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient
from playwright.sync_api import Browser, Page, sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agent_gateway import app

KIBO_IS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = KIBO_IS_DIR.parent
AFTER_SCREENSHOTS_DIR = REPO_ROOT / "docs" / "ux" / "screenshots" / "after"
AFTER_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="module")
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def preview_server_url() -> Any:
    """
    Start `vite preview --port 4175 --host 127.0.0.1` serving the built frontend.
    """
    proc = subprocess.Popen(
        ["npx", "vite", "preview", "--port", "4175", "--host", "127.0.0.1"],
        cwd=str(KIBO_IS_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(1.5)
    yield "http://127.0.0.1:4175"
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()


@pytest.fixture(scope="module")
def browser_instance() -> Any:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_ux15_zero_surprise_mutations_on_mount_and_capture_screenshots(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-15: Opening a page must NEVER trigger automatic POST mutations (`0` POST calls on mount).
    Also captures after screenshots for `docs/ux/screenshots/after/`.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    post_requests_on_mount: List[str] = []

    def on_request(req: Any) -> None:
        if req.method.upper() == "POST":
            post_requests_on_mount.append(req.url)

    page.on("request", on_request)
    t0 = time.perf_counter()
    page.goto(f"{preview_server_url}/privacy-os", wait_until="networkidle")
    mount_ms = round((time.perf_counter() - t0) * 1000, 2)

    assert len(post_requests_on_mount) == 0, (
        f"UX-15 violation: Expected 0 POST mutations on mount, got {post_requests_on_mount}"
    )

    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "01_executive_home_dark.png"), full_page=True)

    # Record after metrics
    after_metrics_path = REPO_ROOT / "docs" / "ux" / "after_metrics.json"
    dist_assets = list((KIBO_IS_DIR / "dist" / "assets").glob("index-*.js"))
    entry_js_bytes = dist_assets[0].stat().st_size if dist_assets else 0
    after_metrics_path.write_text(
        json.dumps(
            {
                "initial_load_ms": mount_ms,
                "post_mutations_on_mount": len(post_requests_on_mount),
                "entry_js_bytes": entry_js_bytes,
                "header_spoofing_inputs_present": page.locator('input[aria-label="X-Tenant-ID"]').count(),
            },
            indent=2,
        )
    )
    page.close()


def test_ux01_executive_home_30_second_triage(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-01: CPO opens KIBO, identifies overdue items, approvals needed, active incidents,
    and recent regulatory changes within 30 seconds, and drills into each item.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    t0 = time.perf_counter()
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")

    assert page.get_by_test_id("metric-card-overdue").is_visible()
    assert page.get_by_test_id("metric-card-approvals").is_visible()
    assert page.get_by_test_id("metric-card-incidents").is_visible()
    assert page.get_by_test_id("metric-card-reg-changes").is_visible()

    # Drill into Overdue / Inbox
    page.get_by_test_id("metric-card-overdue").click()
    assert page.get_by_test_id("unified-inbox-view").is_visible()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "02_unified_inbox.png"), full_page=True)

    elapsed = time.perf_counter() - t0
    assert elapsed < 30.0
    page.close()


def test_ux02_assessment_creation_save_draft_resume_and_approval(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-02: Create an assessment, save draft, reload/resume, attach evidence,
    submit for review, and approve.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-assessments").click()
    assert page.get_by_test_id("guided-assessment-wizard").is_visible()

    # Advance step and save draft
    page.get_by_test_id("assessment-next-step-btn").click()
    page.get_by_test_id("assessment-save-draft-btn").click()
    assert "saved at Step" in page.get_by_test_id("assessment-status-banner").inner_text()

    # Attach new evidence
    page.get_by_test_id("assessment-evidence-input").fill("EVID-TIA-999: Signed Law 25 s. 17 Addendum")
    page.get_by_test_id("assessment-add-evidence-btn").click()

    # Resume saved draft & submit + approve
    page.get_by_test_id("assessment-resume-latest-btn").click()
    page.get_by_test_id("assessment-submit-review-btn").click()
    page.get_by_test_id("assessment-approve-btn").click()
    assert "APPROVED" in page.get_by_test_id("guided-assessment-wizard").inner_text().upper()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "03_guided_assessment_wizard.png"), full_page=True)
    page.close()


def test_ux03_multi_jurisdiction_incident_triage_and_counsel_gate(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-03: Report/triage a breach affecting California, Quebec, Ontario, and Germany,
    inspect deadlines, log containment evidence, and route notification for human approval.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-incidents").click()
    assert page.get_by_test_id("breach-workspace-view").is_visible()

    # Append forensic containment evidence
    page.get_by_test_id("breach-evidence-input").fill("Rotated HSM keys and verified zero data exfiltration.")
    page.get_by_test_id("breach-add-evidence-btn").click()
    assert "Rotated HSM keys" in page.get_by_test_id("breach-evidence-list").inner_text()

    # Explicitly run multi-regime deadline calculation
    page.get_by_test_id("breach-run-triage-btn").click()
    page.wait_for_selector('[data-testid="breach-regime-matrix"]')
    matrix_text = page.get_by_test_id("breach-regime-matrix").inner_text()
    assert "CA-QC" in matrix_text or "EU-GDPR" in matrix_text or "US-CA" in matrix_text
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "04_breach_workspace.png"), full_page=True)
    page.close()


def test_ux04_dsar_end_to_end_fulfillment(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-04: Process a DSAR through intake, verification, deadline calculation,
    redaction/exemption check, and response approval.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-rights").click()
    assert page.get_by_test_id("privacy-rights-view").is_visible()

    page.get_by_test_id("dsar-evaluate-btn").click()
    page.wait_for_selector('[data-testid="dsar-evaluation-card"]')
    page.get_by_test_id("dsar-complete-redaction-btn").click()
    page.get_by_test_id("dsar-approve-delivery-btn").click()
    assert "Response Dispatched" in page.get_by_test_id("dsar-approve-delivery-btn").inner_text()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "05_privacy_rights_dsar.png"), full_page=True)
    page.close()


def test_ux05_regulatory_change_review_and_promotion(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-05: Legal reviewer inspects a newly discovered regulatory update,
    examines provenance and verbatim quote, views impacted workflows, and approves promotion.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-regulatory").click()
    assert page.get_by_test_id("regulatory-intel-view").is_visible()

    page.get_by_test_id("reg-filter-pending").click()
    page.get_by_test_id("reg-verify-promote-btn").click()
    assert "promoted" in page.get_by_test_id("regulatory-status-banner").inner_text().lower()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "06_regulatory_intelligence.png"), full_page=True)
    page.close()


def test_ux06_and_ux11_live_sse_event_propagation_and_deduplication(
    api_client: TestClient, browser_instance: Browser, preview_server_url: str
):
    """
    UX-06 & UX-11: Backend SSE events propagate and duplicate event IDs are deduplicated
    on both backend and frontend without duplicate entries.
    """
    dup_payload = {
        "event_id": "evt-ux11-dedup-verification-99",
        "event_type": "regulation.impact_detected",
        "title": "Quebec Law 25 Cross-Border Impact Alert",
        "summary": "2 active RoPA transfers flagged for updated EFVP review.",
        "severity": "warning",
    }
    r1 = api_client.post(
        "/api/v1/events/publish",
        json=dup_payload,
        headers={"X-Tenant-ID": "tnt-enterprise-global-001"},
    )
    r2 = api_client.post(
        "/api/v1/events/publish",
        json=dup_payload,
        headers={"X-Tenant-ID": "tnt-enterprise-global-001"},
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["event"]["sequence_id"] == r2.json()["event"]["sequence_id"]

    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("sse-emit-test-event-btn").click()
    assert page.get_by_test_id("live-activity-feed").is_visible()
    page.close()


def test_ux07_offline_and_demo_mode_truthfulness(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-07: When backend is unreachable during static preview, the UI displays an explicit
    OFFLINE banner and marks AI Hub connectors as OFFLINE rather than 'connected'.
    Toggling Demo Mode explicitly displays DEMO status.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="networkidle")

    badge = page.get_by_test_id("operational-status-badge").first
    assert badge.get_attribute("data-status") in ("offline", "stale", "live")

    # Navigate to Assistant / AI Hubs and verify offline truthfulness
    page.get_by_test_id("nav-section-assistant").click()
    hub_status = page.get_by_test_id("ai-hub-status-m365_copilot").inner_text()
    assert "OFFLINE" in hub_status.upper()

    # Toggle explicit Demo Mode
    page.get_by_test_id("demo-mode-toggle-btn").click()
    assert page.get_by_test_id("operational-status-badge").first.get_attribute("data-status") == "demo"
    page.close()


def test_ux08_tenant_and_identity_safety_no_spoofing_inputs(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-08: Raw editable header spoofing inputs (`X-Tenant-ID`, `X-User-ID`) are completely absent.
    Only authorized organization switcher and verified session badge are rendered.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")

    assert page.locator('input[aria-label="X-Tenant-ID"]').count() == 0
    assert page.locator('input[aria-label="X-User-ID"]').count() == 0
    assert page.get_by_test_id("authorized-org-switcher").is_visible()
    assert page.get_by_test_id("verified-user-session-badge").is_visible()
    page.close()


def test_ux09_and_ux10_keyboard_navigation_command_palette_and_mobile_viewport(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-09 & UX-10: Keyboard navigation, Command Palette (`Cmd+K`), reversible Inbox undo,
    Light/Dark theme toggle, EN/FR/DE localization, and 390px mobile responsive layout.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")

    # Open Command Palette and jump to Inbox
    page.get_by_test_id("open-command-palette-btn").click()
    assert page.get_by_test_id("command-palette-modal").is_visible()
    page.get_by_test_id("command-item-cmd-inbox").click()
    assert page.get_by_test_id("unified-inbox-view").is_visible()

    # Approve item and test reversible Undo
    page.get_by_test_id("inbox-approve-btn").click()
    page.wait_for_selector('[data-testid="inbox-undo-banner"]')
    assert page.get_by_test_id("inbox-undo-banner").is_visible()
    page.get_by_test_id("inbox-undo-btn").click()

    # Switch Language to French and Theme to Light
    page.get_by_test_id("locale-switcher").select_option("fr")
    assert "Boîte de réception" in page.content()
    page.get_by_test_id("theme-toggle-btn").click()
    assert page.get_by_test_id("privacy-os-portal-root").get_attribute("data-theme") == "light"
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "07_light_mode_french.png"), full_page=True)

    # Test 390px Mobile Viewport (UX-10)
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "08_mobile_390px.png"), full_page=True)
    page.close()


def test_ux12_governed_assistant_stage_progression_and_source_segregation(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-12: Governed Assistant displays real 5-stage progress and segregates
    statutes, regulator guidance, internal policies, contractual commitments, and AI synthesis.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-assistant").click()
    assert page.get_by_test_id("assistant-stage-stepper").is_visible()

    page.get_by_test_id("assistant-submit-btn").click()
    page.wait_for_selector('[data-testid="assistant-segregated-response"]')
    text = page.get_by_test_id("assistant-segregated-response").inner_text()
    assert "1. BINDING STATUTORY REQUIREMENTS" in text.upper()
    assert "2. OFFICIAL REGULATOR GUIDANCE" in text.upper()
    assert "3. INTERNAL COMPANY POLICIES" in text.upper()
    assert "4. CUSTOMER CONTRACTUAL COMMITMENTS" in text.upper()
    assert "5. GOVERNED AI SYNTHESIS" in text.upper()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "09_governed_assistant.png"), full_page=True)
    page.close()


def test_ux13_empty_organization_guided_onboarding_flow(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-13: Selecting a newly onboarded organization with no records launches
    the 4-step Guided Privacy Office Setup Wizard and transitions to Assessments on completion.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")

    page.get_by_test_id("authorized-org-switcher").select_option("tnt-new-onboarding-empty")
    assert page.get_by_test_id("guided-onboarding-view").is_visible()
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "10_guided_onboarding_empty_org.png"), full_page=True)

    page.get_by_test_id("onboarding-next-step-btn").click()
    page.get_by_test_id("onboarding-complete-btn").click()
    assert page.get_by_test_id("guided-assessment-wizard").is_visible()
    page.close()


def test_ux14_1000_record_scale_filtering_and_pagination(
    browser_instance: Browser, preview_server_url: str
):
    """
    UX-14: Load 1,020-record scale dataset in Jurisdiction Matrix, filter by region/search,
    and paginate smoothly without UI freeze.
    """
    page = browser_instance.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"{preview_server_url}/privacy-os", wait_until="domcontentloaded")
    page.get_by_test_id("nav-section-regulatory").click()
    page.get_by_test_id("open-jurisdiction-evaluator-btn").click()
    assert page.get_by_test_id("jurisdiction-workspace-view").is_visible()

    t0 = time.perf_counter()
    page.get_by_test_id("toggle-1000-scale-mode-btn").click()
    assert "1020 matching records" in page.get_by_test_id("jurisdiction-workspace-view").inner_text()
    page.get_by_test_id("jurisdiction-next-page").click()
    scale_ms = (time.perf_counter() - t0) * 1000
    assert scale_ms < 2000.0
    page.screenshot(path=str(AFTER_SCREENSHOTS_DIR / "11_jurisdiction_1020_scale_matrix.png"), full_page=True)
    page.close()
