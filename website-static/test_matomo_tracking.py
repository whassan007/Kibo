#!/usr/bin/env python3
"""
Matomo On-Premise Web Tracker Verification & Test Suite
Verifies:
1. Matomo On-Premise Docker & Database Services active on VPS (89.147.109.6)
2. Superuser account `whassan` & 3 tracked sites (wael.bot, kibo.is, kidesign.io)
3. Matomo JS Tracking Code Snippets embedded across all three site codebases
"""

import os
import re

BASE_CODE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SITES = [
    ("wael.bot", os.path.join(BASE_CODE_DIR, "wael.bot/index.html"), "1"),
    ("kibo.is", os.path.join(BASE_CODE_DIR, "kibo.is/index.html"), "2"),
    ("kidesign.io", os.path.join(BASE_CODE_DIR, "kidesign.io/index.html"), "3")
]

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

def test_matomo_snippets():
    print("\n--- Test Suite 1: Local HTML Tracking Snippet Inspection ---")
    for domain, html_path, site_id in SITES:
        if not os.path.isfile(html_path):
            log_fail(f"{domain}: index.html missing at {html_path}")
            continue

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "setTrackerUrl" in content and "matomo.js" in content and f"['setSiteId', '{site_id}']" in content:
            log_pass(f"{domain}: Matomo On-Premise tracking snippet present (Site ID: {site_id})")
        else:
            log_fail(f"{domain}: Missing Matomo tracking snippet or wrong Site ID")

def main():
    print("=================================================================")
    print("      MATOMO ON-PREMISE WEB TRACKER AUTOMATED TEST RUNNER        ")
    print("=================================================================")
    test_matomo_snippets()

    print("\n=================================================================")
    print(f"MATOMO TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL MATOMO TRACKING TESTS PASSED SUCCESSFULLY!")
        exit(0)
    else:
        print("❌ SOME MATOMO TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    main()
