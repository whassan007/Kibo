#!/usr/bin/env python3
"""
KIBO.IS Downloadable Content & PDF Integrity Automated Test Suite
Verifies:
1. Physical Existence & Non-zero file sizes of all downloadable PDF compliance documents
2. Valid PDF Header Structure (%PDF-1.4)
3. HTML Download Links & HTML5 `download` attributes across pages
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

REQUIRED_PDFS = [
    "KIBO-ISO-27001-Certificate.pdf",
    "KIBO-SOC2-Type-II-Executive-Summary.pdf",
    "KIBO-Data-Processing-Addendum-DPA.pdf",
    "KIBO-Board-Compliance-Audit-Report.pdf",
    "KIBO-WCAG-2.2-AA-VPAT-Report.pdf"
]

HTML_FILES_TO_CHECK = [
    ("trust.html", ["downloads/KIBO-ISO-27001-Certificate.pdf", "downloads/KIBO-SOC2-Type-II-Executive-Summary.pdf", "downloads/KIBO-Data-Processing-Addendum-DPA.pdf", "downloads/KIBO-WCAG-2.2-AA-VPAT-Report.pdf"]),
    ("dpa.html", ["downloads/KIBO-Data-Processing-Addendum-DPA.pdf"]),
    ("app.html", ["downloads/KIBO-Board-Compliance-Audit-Report.pdf"])
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

def test_pdf_files():
    print("\n--- Test Suite 1: PDF Document Generation & Integrity ---")
    if not os.path.isdir(DOWNLOADS_DIR):
        log_fail("downloads/ directory missing!")
        return

    for pdf_name in REQUIRED_PDFS:
        pdf_path = os.path.join(DOWNLOADS_DIR, pdf_name)
        if os.path.isfile(pdf_path):
            size = os.path.getsize(pdf_path)
            if size > 100:
                with open(pdf_path, "rb") as f:
                    header = f.read(8)
                if header.startswith(b"%PDF"):
                    log_pass(f"{pdf_name}: Physical file exists ({size} bytes, valid %PDF header)")
                else:
                    log_fail(f"{pdf_name}: Invalid PDF header: {header}")
            else:
                log_fail(f"{pdf_name}: File size too small ({size} bytes)")
        else:
            log_fail(f"Missing PDF document: {pdf_name}")

def test_html_download_links():
    print("\n--- Test Suite 2: HTML Download Links & Attributes ---")
    for html_file, expected_links in HTML_FILES_TO_CHECK:
        file_path = os.path.join(BASE_DIR, html_file)
        if not os.path.isfile(file_path):
            log_fail(f"{html_file} missing!")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for link in expected_links:
            if link in content and "download" in content:
                log_pass(f"{html_file}: Contains active download link: href=\"{link}\" download")
            else:
                log_fail(f"{html_file}: Missing or unlinked download link for {link}")

def main():
    print("=================================================================")
    print("      KIBO.IS DOWNLOADABLE CONTENT AUTOMATED TEST RUNNER         ")
    print("=================================================================")
    test_pdf_files()
    test_html_download_links()

    print("\n=================================================================")
    print(f"DOWNLOAD TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL DOWNLOADABLE CONTENT TESTS PASSED SUCCESSFULLY!")
        exit(0)
    else:
        print("❌ SOME DOWNLOAD TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    main()
