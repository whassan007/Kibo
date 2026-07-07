---
name: european-union-continuous-auditing
description: >-
  Maintain GDPR transparency and the Article 30 RoPA, enforce ePrivacy cookie-consent, and keep the inventory accurate; run a 27701 PIMS.
jurisdiction: European Union / EEA
task_domain: Continuous Auditing & Policy Governance
version: 1.0
---

# SKILL: Continuous Auditing & Policy Governance — European Union / EEA

## Purpose
Maintain GDPR transparency and the Article 30 RoPA, enforce ePrivacy cookie-consent, and keep the inventory accurate; run a 27701 PIMS.

## Controlling frameworks & key obligations
- **Transparency (Arts 13–14):** concise, intelligible, plain-language notices; layered policies.
- **ePrivacy:** prior opt-in consent required before storing/accessing non-essential cookies/trackers on a device; strictly-necessary exemption only.
- **Art 30 RoPA:** maintain accurate, current records of processing for controller and processor roles.
- **IAM:** detect unencrypted personal data and over-privileged access. **PIMS:** ISO/IEC 27701.

## Operational workflow
1. Crawl sites/apps/repos; detect cookies/trackers firing **before** consent; diff against the consent configuration.
2. Open remediation tickets for any pre-consent non-essential tracker.
3. Keep the Art 30 RoPA synchronized with live processing; flag drift and unmapped processing.
4. Scan IAM for unencrypted personal data and excess privilege.
5. Version transparency notices with effective dates and changelog.

## Statutory deadlines & thresholds
- Consent must be obtained **before** non-essential cookies are set (ePrivacy).
- RoPA must be made available to the supervisory authority on request (Art 30(4)).

## Guardrails (mandatory)
- Any non-essential tracker firing before opt-in is a violation.
- Keep the RoPA current; unmapped processing is a defect.

## Authoritative references
- GDPR transparency (Arts 13–14, 30): https://gdpr-info.eu/
- ePrivacy / cookies: https://gdpr.eu/cookies/
- EDPS ePrivacy: https://www.edps.europa.eu/data-protection/our-work/subjects/eprivacy-directive_en
- ISO/IEC 27701: https://www.iso.org/standard/71670.html
