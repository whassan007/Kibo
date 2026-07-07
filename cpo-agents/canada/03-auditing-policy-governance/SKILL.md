---
name: canada-continuous-auditing
description: >-
  Uphold PIPEDA openness and Law 25 transparency/confidentiality-by-default; detect trackers continuously; maintain processing records and a breach register; run a 27701 PIMS.
jurisdiction: Canada
task_domain: Continuous Auditing & Policy Governance
version: 1.0
---

# SKILL: Continuous Auditing & Policy Governance — Canada

## Purpose
Uphold PIPEDA openness and Law 25 transparency/confidentiality-by-default; detect trackers continuously; maintain processing records and a breach register; run a 27701 PIMS.

## Controlling frameworks & key obligations
- **Openness (PIPEDA Principle 8):** policies must be readily available and understandable.
- **Law 25 transparency:** disclose use of technologies that identify/locate/profile individuals (incl. cookies) and the means to deactivate them; **confidentiality by default** for technological products/services.
- **Records:** internal processing records and a confidentiality-incident/breach register.
- **IAM:** detect unencrypted PII and over-privileged access. **PIMS:** ISO/IEC 27701.

## Operational workflow
1. Crawl sites/apps/repos; diff trackers against disclosure; open tickets for undisclosed trackers.
2. Audit default settings for confidentiality-by-default compliance; flag exposures requiring active consent.
3. Maintain processing records and the breach register.
4. Scan IAM for unencrypted PII and excess privilege.
5. Version policies with effective dates and changelog.

## Statutory deadlines & thresholds
- Confidentiality-by-default is mandatory under Law 25 for technological products/services.
- Breach register must be maintained regardless of notifiability.

## Guardrails (mandatory)
- Treat undisclosed trackers as defects.
- Never default a technological product to a setting that discloses personal information without active consent (Law 25).

## Authoritative references
- OPC PIPEDA principles: https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/
- Quebec CAI: https://www.cai.gouv.qc.ca/en/
- ISO/IEC 27701: https://www.iso.org/standard/71670.html
