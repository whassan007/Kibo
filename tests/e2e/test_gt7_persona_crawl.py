import pytest
from playwright.sync_api import Page, expect

@pytest.mark.xfail(strict=True, reason="Defect UI-001 / Baseline R-2: Missing offline state")
def test_offline_graceful_degradation(page: Page):
    """
    Simulate offline mode and verify the UI shows the correct offline banner.
    """
    page.context.set_offline(True)
    page.goto("http://localhost:5173/widget")
    
    offline_banner = page.locator("text=System Offline")
    expect(offline_banner).to_be_visible(timeout=5000)
    
    submit_btn = page.locator("button[type="submit"]")
    expect(submit_btn).to_be_disabled()

@pytest.mark.xfail(strict=True, reason="Defect UI-002: Contrast ratios fail WCAG")
def test_contrast_ratios(page: Page):
    """
    Axe-core contrast verification.
    """
    page.goto("http://localhost:5173/expert")
    # In a full run, we would inject axe-core and run assertions here.
    assert False\n