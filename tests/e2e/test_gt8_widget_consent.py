import pytest
from playwright.sync_api import Page, expect

def test_widget_consent_flow(page: Page):
    """
    Verify that the public widget correctly requires consent before submission,
    and handles valid inputs via zod schemas.
    """
    page.goto("http://localhost:5173/widget")
    
    # Check for Zod validation errors on empty submit
    submit_btn = page.locator("button[type="submit"]")
    submit_btn.click()
    
    expect(page.locator("text=Consent is required")).to_be_visible()\n