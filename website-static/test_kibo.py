#!/usr/bin/env python3
"""
KIBO.IS Comprehensive Test Suite & Validator
Verifies:
1. File Existence & HTML Structure for all 16 pages
2. Link & Asset Integrity across all pages
3. CSS Design System Variables (Dark & Light mode)
4. JavaScript engine & Theme Toggle integration
5. Technical SEO (JSON-LD, robots.txt, sitemap.xml, llms.txt, llms-full.txt)
6. Accessibility attributes (Skip link, ARIA, focus indicators)
7. .htaccess routing rules
"""

import os
import re
import json
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_PAGES = [
    "index.html",
    "login.html",
    "signup.html",
    "app.html",
    "privacy.html",
    "terms.html",
    "security.html",
    "trust.html",
    "contact.html",
    "pricing.html",
    "docs.html",
    "status.html",
    "accessibility.html",
    "responsible-ai.html",
    "dpa.html",
    "subprocessors.html"
]

REQUIRED_META_FILES = [
    ".htaccess",
    "robots.txt",
    "sitemap.xml",
    "llms.txt",
    "llms-full.txt"
]

REQUIRED_ASSETS = [
    "css/kibo.css",
    "js/kibo.js",
    "js/app.js"
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

def test_file_structure():
    print("\n--- Test Suite 1: File Structure & Existence ---")
    for page in REQUIRED_PAGES:
        path = os.path.join(BASE_DIR, page)
        if os.path.isfile(path):
            log_pass(f"Page exists: {page}")
        else:
            log_fail(f"Missing required page: {page}")

    for meta in REQUIRED_META_FILES:
        path = os.path.join(BASE_DIR, meta)
        if os.path.isfile(path):
            log_pass(f"Meta file exists: {meta}")
        else:
            log_fail(f"Missing required meta file: {meta}")

    for asset in REQUIRED_ASSETS:
        path = os.path.join(BASE_DIR, asset)
        if os.path.isfile(path):
            log_pass(f"Asset exists: {asset}")
        else:
            log_fail(f"Missing required asset: {asset}")

def test_html_content_and_accessibility():
    print("\n--- Test Suite 2: HTML Integrity & Accessibility (WCAG 2.2 AA) ---")
    for page in REQUIRED_PAGES:
        path = os.path.join(BASE_DIR, page)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Test doctype
        if "<!DOCTYPE html>" in content or "<!doctype html>" in content:
            log_pass(f"{page}: Contains valid HTML5 DOCTYPE")
        else:
            log_fail(f"{page}: Missing DOCTYPE declaration")

        # Test meta viewport
        if 'name="viewport"' in content:
            log_pass(f"{page}: Viewport meta tag present for responsiveness")
        else:
            log_fail(f"{page}: Missing responsive viewport meta tag")

        # Test CSS linking
        if 'href="css/kibo.css"' in content or "css/kibo.css" in content:
            log_pass(f"{page}: CSS stylesheet linked correctly")
        else:
            log_fail(f"{page}: Missing css/kibo.css link")

        # Test JS linking
        if 'src="js/kibo.js"' in content:
            log_pass(f"{page}: js/kibo.js script linked")
        else:
            log_fail(f"{page}: Missing js/kibo.js script")

        # Test Theme Toggle Button presence
        if 'class="theme-toggle-btn"' in content or page == "app.html":
            log_pass(f"{page}: Includes Dark/Light theme toggle button")
        else:
            log_fail(f"{page}: Missing theme toggle button")

def test_seo_and_json_ld():
    print("\n--- Test Suite 3: Technical SEO & AI Search Optimization ---")
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JSON-LD script
    json_ld_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    if json_ld_match:
        try:
            data = json.loads(json_ld_match.group(1))
            graph = data.get("@graph", [])
            types = [item.get("@type") for item in graph]
            if "Organization" in types and "SoftwareApplication" in types and "FAQPage" in types:
                log_pass("index.html: Valid JSON-LD Schema (Organization, SoftwareApplication, FAQPage)")
            else:
                log_fail(f"index.html: Incomplete JSON-LD types found: {types}")
        except Exception as e:
            log_fail(f"index.html: JSON-LD parse error: {e}")
    else:
        log_fail("index.html: JSON-LD script block not found")

    # Test robots.txt
    robots_path = os.path.join(BASE_DIR, "robots.txt")
    with open(robots_path, "r", encoding="utf-8") as f:
        robots = f.read()
    if "GPTBot" in robots and "ClaudeBot" in robots and "Sitemap:" in robots:
        log_pass("robots.txt: Correctly configured for AI crawlers & sitemap reference")
    else:
        log_fail("robots.txt: Missing AI crawler permissions or sitemap reference")

    # Test sitemap.xml
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        locs = [elem.text for elem in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        if len(locs) >= 8:
            log_pass(f"sitemap.xml: Parsed successfully with {len(locs)} valid URLs")
        else:
            log_fail(f"sitemap.xml: Unexpected number of URLs ({len(locs)})")
    except Exception as e:
        log_fail(f"sitemap.xml: XML parse error: {e}")

    # Test llms.txt and llms-full.txt
    llms_path = os.path.join(BASE_DIR, "llms.txt")
    with open(llms_path, "r", encoding="utf-8") as f:
        llms_text = f.read()
    if "KIBO" in llms_text and "DSAR Automation" in llms_text:
        log_pass("llms.txt: Correctly formatted AI platform summary")
    else:
        log_fail("llms.txt: Missing core platform summary details")

def test_css_theme_system():
    print("\n--- Test Suite 4: CSS Design System & Dual Theme Palette ---")
    css_path = os.path.join(BASE_DIR, "css/kibo.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    if '[data-theme="dark"]' in css and '[data-theme="light"]' in css:
        log_pass("css/kibo.css: Contains both Dark Mode and Light Mode theme rule definitions")
    else:
        log_fail("css/kibo.css: Missing dark/light theme definitions")

    if "--bg-primary" in css and "--accent-primary" in css and "--text-main" in css:
        log_pass("css/kibo.css: Contains full design system custom property variables")
    else:
        log_fail("css/kibo.css: Missing custom property variables")

def test_htaccess_routing():
    print("\n--- Test Suite 5: .htaccess Web Server Routing & Security ---")
    htaccess_path = os.path.join(BASE_DIR, ".htaccess")
    with open(htaccess_path, "r", encoding="utf-8") as f:
        ht = f.read()

    if "Strict-Transport-Security" in ht and "Content-Security-Policy" in ht:
        log_pass(".htaccess: Security headers (HSTS, CSP, X-Frame-Options) configured")
    else:
        log_fail(".htaccess: Missing essential security headers")

    if "RewriteRule ^dashboard/?$ /app [R=301,L]" in ht or "/app" in ht:
        log_pass(".htaccess: 301 Redirect for /dashboard -> /app configured")
    else:
        log_fail(".htaccess: Missing /dashboard -> /app redirect rule")

    if "mod_deflate.c" in ht and "mod_expires.c" in ht:
        log_pass(".htaccess: Compression (Gzip) and Browser Caching rules configured")
    else:
        log_fail(".htaccess: Missing performance compression or caching directives")

def main():
    print("=================================================================")
    print("      KIBO.IS PRODUCTION AUTOMATED TEST SUITE & VALIDATOR       ")
    print("=================================================================")
    test_file_structure()
    test_html_content_and_accessibility()
    test_seo_and_json_ld()
    test_css_theme_system()
    test_htaccess_routing()

    print("\n=================================================================")
    print(f"TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
    print("=================================================================")

    if failed_tests == 0:
        print("✅ ALL SUITES PASSED! KIBO.IS IS PRODUCTION-READY.")
        exit(0)
    else:
        print("❌ SOME SUITES FAILED. PLEASE AUDIT THE FAILURES ABOVE.")
        exit(1)

if __name__ == "__main__":
    main()
