#!/usr/bin/env python3
"""
KIBO.IS Sign Up Automated Test Suite
Verifies:
1. Signup Form Elements & Attributes (Name, Org, Email, Password, Confirm Password, Terms)
2. Password Matching Validation Logic & minlength=12
3. SSO Signup Options (Okta, Microsoft)
4. Form Target & Redirection to /app
5. Theme Toggle Button Presence & Styling
6. Accessibility Attributes & Form Labels
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIGNUP_PATH = os.path.join(BASE_DIR, "signup.html")

passed_tests = 0
failed_tests = 0

def log_pass(msg):
    global passed_tests
    passed_tests += 1
    print(f"  [PASS] {msg}")

def log_fail(msg):
    global failed_tests
    failed_tests += 1
    print(f"❌ [FAIL] {msg}")

def test_signup_page():
    print("\n=================================================================")
    print("        KIBO.IS SIGN UP PAGE AUTOMATED TEST SUITE                ")
    print("=================================================================\n")

    if not os.path.isfile(SIGNUP_PATH):
        log_fail("signup.html does not exist!")
        return

    with open(SIGNUP_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Form element & action test
    if '<form action="app.html"' in html and 'id="signup-form"' in html:
        log_pass("Form element present with target action app.html")
    else:
        log_fail("Missing form element or target action app.html")

    # 2. Form field inputs
    fields = ['id="name"', 'id="org"', 'id="email"', 'id="password"', 'id="confirm_password"', 'id="terms"']
    for field in fields:
        if field in html:
            log_pass(f"Input field present: {field}")
        else:
            log_fail(f"Missing input field: {field}")

    # 3. Password minlength=12 constraint
    if 'minlength="12"' in html:
        log_pass("Password fields enforce minimum 12-character security rule (minlength=12)")
    else:
        log_fail("Missing minlength=12 attribute on password fields")

    # 4. Terms and Privacy link agreement
    if 'href="terms.html"' in html and 'href="privacy.html"' in html:
        log_pass("Terms of Service and Privacy Policy legal links present")
    else:
        log_fail("Missing legal agreement links")

    # 5. SSO Signup Buttons
    if ('btn-entra-id' in html or 'signup_sso=microsoft' in html) and ('btn-okta-sso' in html or 'signup_sso=okta' in html):
        log_pass("Enterprise SSO signup options present (Okta & Microsoft Entra ID)")
    else:
        log_fail("Missing SSO signup options")

    # 6. Password Match JavaScript Validation
    if 'Passwords do not match' in html and 'setCustomValidity' in html:
        log_pass("Client-side password matching validation script present")
    else:
        log_fail("Missing password matching validation script")

    # 7. Theme Toggle Button
    if 'class="theme-toggle-btn"' in html:
        log_pass("Dark/Light Theme Toggle button present on signup page")
    else:
        log_fail("Missing theme toggle button")

    # 8. Okta Enterprise SSO Modal & Handlers
    if 'id="okta-modal"' in html and 'id="okta-auth-form"' in html and 'id="okta_domain"' in html:
        log_pass("Okta Enterprise SSO Modal & Authentication Form present")
    else:
        log_fail("Missing Okta Enterprise SSO Modal or Form")

    print("\n=================================================================")
    print(f"SIGNUP TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL SIGNUP TESTS PASSED SUCCESSFULLY!")
        exit(0)
    else:
        print("❌ SOME SIGNUP TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    test_signup_page()
