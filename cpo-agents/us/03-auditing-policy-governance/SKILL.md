---
name: united-states-continuous-auditing
description: >-
  Keep public notices accurate, continuously detect undisclosed tracking technologies, maintain a CPRA-aligned processing inventory, and run a PIMS aligned to ISO/IEC 27701.
jurisdiction: United States
task_domain: Continuous Auditing & Policy Governance
version: 1.0
---

# SKILL: Continuous Auditing & Policy Governance — United States

## Purpose
Keep public notices accurate, continuously detect undisclosed tracking technologies, maintain a CPRA-aligned processing inventory, and run a PIMS aligned to ISO/IEC 27701.

## Controlling frameworks & key obligations
- **Notices:** CCPA notice-at-collection + privacy policy; "Do Not Sell or Share My Personal Information" and "Limit the Use of My Sensitive Personal Information" links; CalOPPA conspicuous policy for any site reaching Californians.
- **Tracking:** every cookie/pixel/SDK in use must be disclosed and, for sale/sharing, opt-out-enabled.
- **Inventory:** CPRA-aligned data map supporting risk assessments (functional RoPA).
- **IAM:** detect unencrypted PII and over-privileged access.
- **PIMS:** ISO/IEC 27701 controls layered on ISO 27001.

## Operational workflow
1. Schedule recurring crawls of sites/apps/repos; diff discovered trackers against the disclosed inventory.
2. For each undisclosed tracker, open a remediation ticket and update the notice.
3. Reconcile the data map against live data flows; flag drift and shadow processing.
4. Scan IAM for unencrypted PII stores and excessive privileges; flag for least-privilege remediation.
5. Version every notice change with an effective date and changelog.

## Statutory deadlines & thresholds
- Notice must be updated at least every 12 months under CCPA, and promptly on material change.
- Annual cybersecurity audit and risk-assessment cadence under CPRA regulations (as finalized).

## Guardrails (mandatory)
- Treat any tracker not in the published notice as a defect.
- Never publish a notice that overstates protections; truthfulness is enforceable under FTC Act §5.

## Authoritative references
- FTC privacy/security: https://www.ftc.gov/business-guidance/privacy-security
- California AG CCPA: https://oag.ca.gov/privacy/ccpa
- ISO/IEC 27701: https://www.iso.org/standard/71670.html
