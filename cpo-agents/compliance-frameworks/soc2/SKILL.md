---
name: soc2-attestation
description: >-
  Prepare and sustain AICPA SOC 2 readiness across the five Trust Services Criteria (Security
  required) and the COSO-derived Common Criteria CC1-CC9, evidencing operating effectiveness for
  a Type II examination.
framework: AICPA SOC 2 (Trust Services Criteria)
authority: AICPA; independent service auditor (CPA firm)
version: 1.0
---

# SKILL: SOC 2 Attestation Readiness

## Purpose
Build and continuously operate the controls a SOC 2 service auditor will test, and assemble period evidence.

## What SOC 2 is
- A B2B attestation for technology/cloud/SaaS providers evaluating the **operating effectiveness** of chosen controls over a defined period.
- Governed by the **2017 Trust Services Criteria**, updated **2022**.
- **Type I** = design at a point in time; **Type II** = operating effectiveness over a period (the market standard).

## Five Trust Services Criteria
- **Security (REQUIRED):** protection against unauthorized access/disclosure and logical/physical damage.
- **Availability (optional):** uptime vs SLAs — capacity, backup, DR testing, environmental protection.
- **Processing Integrity (optional):** complete/valid/accurate/timely/authorized processing — input validation (PI1.2), accurate processing (PI1.3), reliable output (PI1.4).
- **Confidentiality (optional):** sensitive corporate data (IP, source code, plans) — classification (C1.1), protection/secure destruction (C1.2).
- **Privacy (optional):** personal information (PII) — notice, choice/consent, collection limitation, access/correction; mirrors PIPEDA 10 principles and ISO 27701 Annex A.

## Common Criteria (CC1–CC9) — Security, COSO-derived
| Domain | Focus | COSO |
| --- | --- | --- |
| **CC1** Control Environment | integrity, ethics, board independence, HR/onboarding, security culture | Principles 1–5 |
| **CC2** Communication & Information | internal/external comms of policies, boundaries, incidents | Principles 13–15 |
| **CC3** Risk Assessment | identify/analyze/monitor risk incl. change-driven risk | Principles 6–9 |
| **CC4** Monitoring Activities | evaluate control effectiveness; remediate deficiencies | Principles 16–17 |
| **CC5** Control Activities | controls designed, documented, executed | Principles 10–12 |
| **CC6** Logical & Physical Access | encryption, RBAC, MFA, segmentation, firewalls, facility security | system-specific |
| **CC7** System Operations | monitoring, logging, anomaly detection, incident response, DR | system-specific |
| **CC8** Change Management | secure tested/peer-reviewed/approved changes | system-specific |
| **CC9** Risk Mitigation | business-process mitigation, vendor risk management, insurance | system-specific |

## Operational workflow
1. Scope: select TSC (Security mandatory) per business model.
2. Map CC1–CC9 to existing controls; close gaps using AICPA **points of focus**.
3. Stand up continuous evidence collection (logs, tickets, reviews) for the Type II window.
4. Run vendor risk management under CC9 (third-party due diligence).
5. Produce a pre-audit readiness gap report; engage the service auditor.

## Guardrails (mandatory)
- Security/Common Criteria is always in scope — never omit it.
- Evidence operating effectiveness over the period, not just policy documents.
- Escalate scoping and report-opinion judgment to the service auditor / human owner.

## Authoritative references
- AICPA Trust Services Criteria: https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services
- Secureframe SOC 2 Common Criteria: https://secureframe.com/hub/soc-2/common-criteria
