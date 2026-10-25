#!/usr/bin/env python3
"""
KIBO.IS & WAEL.BOT Contact Forms Automated Test Suite
Verifies:
1. Form Fields & Validation Attributes (First Name, Last Name, Email, Company, Framework Select)
2. Honeypot Anti-Spam Field Presence & Drop Logic
3. CASL & CAN-SPAM Express Consent Checkboxes
4. Submission Event Handlers & User Feedback Success Banners
"""

import os
import re

KIBO_CONTACT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/contact.html"
WAELBOT_CONNECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/wael.bot/pages/ConnectPage.tsx"

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

def test_kibo_contact_form():
    print("\n--- Test Suite 1: KIBO.IS Contact & Demo Form ---")
    if not os.path.isfile(KIBO_CONTACT_PATH):
        log_fail("kibo.is contact.html missing!")
        return

    with open(KIBO_CONTACT_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Form tag & ID
    if '<form' in html and 'id="contact-form"' in html:
        log_pass("kibo.is: Form element present with id=contact-form")
    else:
        log_fail("kibo.is: Missing form tag or id=contact-form")

    # Inputs
    inputs = ['id="first_name"', 'id="last_name"', 'id="work_email"', 'id="company_name"', 'id="framework"']
    for inp in inputs:
        if inp in html:
            log_pass(f"kibo.is: Input field present: {inp}")
        else:
            log_fail(f"kibo.is: Missing input field: {inp}")

    # Honeypot Anti-Spam
    if 'id="b_honeypot"' in html or 'name="b_honeypot"' in html:
        log_pass("kibo.is: Honeypot anti-spam field present")
    else:
        log_fail("kibo.is: Missing honeypot anti-spam field")

    # CASL Consent Checkbox
    if 'id="casl_consent"' in html or 'casl_consent' in html:
        log_pass("kibo.is: CASL/CAN-SPAM express consent checkbox present")
    else:
        log_fail("kibo.is: Missing CASL consent checkbox")

    # Success Banner & JS Submit Handler
    if 'id="contact-success-msg"' in html and 'contactForm.style.display = \'none\'' in html:
        log_pass("kibo.is: Success message banner & interactive JS submit handler present")
    else:
        log_fail("kibo.is: Missing success message banner or JS submit handler")

def test_waelbot_connect_form():
    print("\n--- Test Suite 2: WAEL.BOT Advisory Connect Form ---")
    if not os.path.isfile(WAELBOT_CONNECT_PATH):
        log_fail("wael.bot ConnectPage.tsx missing!")
        return

    with open(WAELBOT_CONNECT_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    # Form & Handlers
    if 'onSubmit={handleSubmit}' in code:
        log_pass("wael.bot: React Form submit handler registered (handleSubmit)")
    else:
        log_fail("wael.bot: Missing onSubmit handler")

    # Fields
    if 'formData.name' in code and 'formData.email' in code and 'formData.message' in code:
        log_pass("wael.bot: Input state fields (Name, Email, Message) present")
    else:
        log_fail("wael.bot: Missing state input fields")

    # Honeypot Anti-Spam
    if 'b_honeypot' in code and 'formData.b_honeypot' in code:
        log_pass("wael.bot: Honeypot anti-spam prevention logic active")
    else:
        log_fail("wael.bot: Missing honeypot anti-spam logic")

    # CASL Express Consent
    if 'caslConsent' in code and 'CASL / CAN-SPAM' in code:
        log_pass("wael.bot: CASL/CAN-SPAM express consent control present")
    else:
        log_fail("wael.bot: Missing CASL consent control")

    # Success Message
    if 'submitted' in code and 'Thank you for your inquiry' in code:
        log_pass("wael.bot: Success message state transition present")
    else:
        log_fail("wael.bot: Missing success message state transition")

def main():
    print("=================================================================")
    print("      KIBO.IS & WAEL.BOT CONTACT FORMS TEST SUITE RUNNER         ")
    print("=================================================================")
    test_kibo_contact_form()
    test_waelbot_connect_form()

    print("\n=================================================================")
    print(f"CONTACT TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL CONTACT FORM TESTS PASSED SUCCESSFULLY!")
        exit(0)
    else:
        print("❌ SOME CONTACT FORM TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    main()
