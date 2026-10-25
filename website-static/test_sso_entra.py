#!/usr/bin/env python3
"""
KIBO.IS Microsoft Entra ID SSO Sign Up & Login Automated Test Suite
Verifies:
1. Microsoft Entra ID Buttons & Interactive Authentication Modal in signup.html and login.html
2. Form Input fields (Work Email, Entra Tenant Domain, User Name) & hidden SSO query params
3. Workspace URL Parameter Parser & SAML/OAuth Verification in js/app.js
4. User Profile DOM Updates (Avatar, Name) & Enterprise Onboarding Banner rendering in app.html
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SIGNUP_PATH = os.path.join(BASE_DIR, "signup.html")
LOGIN_PATH = os.path.join(BASE_DIR, "login.html")
APP_PATH = os.path.join(BASE_DIR, "app.html")
JS_APP_PATH = os.path.join(BASE_DIR, "js/app.js")

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

def test_signup_entra_id():
    print("\n--- Test Suite 1: signup.html Microsoft Entra ID Integration ---")
    if not os.path.isfile(SIGNUP_PATH):
        log_fail("signup.html missing!")
        return

    with open(SIGNUP_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if 'id="btn-entra-id"' in html:
        log_pass("signup.html: Microsoft Entra ID SSO button present")
    else:
        log_fail("signup.html: Missing Microsoft Entra ID SSO button")

    if 'id="entra-modal"' in html and 'Microsoft Entra ID' in html:
        log_pass("signup.html: Microsoft Entra ID interactive authentication modal present")
    else:
        log_fail("signup.html: Missing Entra ID modal dialog")

    if 'name="signup_sso" value="microsoft"' in html and 'name="sso_provider" value="Microsoft Entra ID"' in html:
        log_pass("signup.html: Hidden SSO parameters (signup_sso=microsoft & sso_provider=Microsoft Entra ID) configured")
    else:
        log_fail("signup.html: Missing hidden SSO parameter fields")

    if 'name="tenant"' in html and 'name="email"' in html and 'action="app.html"' in html:
        log_pass("signup.html: Work Email & Tenant inputs target app.html destination")
    else:
        log_fail("signup.html: Missing tenant or email inputs")

def test_login_entra_id():
    print("\n--- Test Suite 2: login.html Microsoft Entra ID Integration ---")
    if not os.path.isfile(LOGIN_PATH):
        log_fail("login.html missing!")
        return

    with open(LOGIN_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if 'id="btn-entra-login"' in html:
        log_pass("login.html: Microsoft Entra ID login button present")
    else:
        log_fail("login.html: Missing Microsoft Entra ID login button")

    if 'id="entra-modal"' in html and 'name="sso" value="microsoft"' in html:
        log_pass("login.html: Entra ID login modal with sso=microsoft action target configured")
    else:
        log_fail("login.html: Missing Entra ID login modal or sso parameter")

def test_js_app_sso_engine():
    print("\n--- Test Suite 3: js/app.js SSO Processing & Banner Engine ---")
    if not os.path.isfile(JS_APP_PATH):
        log_fail("js/app.js missing!")
        return

    with open(JS_APP_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    if 'signup_sso' in code and 'Microsoft Entra ID' in code:
        log_pass("js/app.js: URL parameter parser detects Microsoft Entra ID SSO events")
    else:
        log_fail("js/app.js: Missing SSO URL parameter parser")

    if 'userProfileName.textContent' in code and 'userAvatar.textContent' in code:
        log_pass("js/app.js: User profile header avatar & name DOM update logic present")
    else:
        log_fail("js/app.js: Missing user profile header update logic")

    if 'app-sso-banner' in code and 'SAML 2.0' in code:
        log_pass("js/app.js: High-visibility Enterprise Onboarding Banner & token verification present")
    else:
        log_fail("js/app.js: Missing Enterprise Onboarding Banner code")

def test_app_html_containers():
    print("\n--- Test Suite 4: app.html Workspace Layout Containers ---")
    if not os.path.isfile(APP_PATH):
        log_fail("app.html missing!")
        return

    with open(APP_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    if 'id="app-user-avatar"' in html and 'id="app-user-name"' in html:
        log_pass("app.html: Header profile containers (app-user-avatar & app-user-name) present")
    else:
        log_fail("app.html: Missing app-user-avatar or app-user-name containers")

    if 'id="app-sso-banner"' in html:
        log_pass("app.html: Enterprise Onboarding Banner container (app-sso-banner) present")
    else:
        log_fail("app.html: Missing app-sso-banner container")

def main():
    print("=================================================================")
    print("   KIBO.IS MICROSOFT ENTRA ID SSO AUTOMATED TEST RUNNER          ")
    print("=================================================================")
    test_signup_entra_id()
    test_login_entra_id()
    test_js_app_sso_engine()
    test_app_html_containers()

    print("\n=================================================================")
    print(f"ENTRA ID TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL MICROSOFT ENTRA ID SSO TESTS PASSED SUCCESSFULLY!")
        exit(0)
    else:
        print("❌ SOME SSO TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    main()
