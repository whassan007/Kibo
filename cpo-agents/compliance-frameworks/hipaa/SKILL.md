---
name: hipaa-certification
description: >-
  Govern HIPAA Privacy, Security, and Breach Notification compliance for PHI/ePHI under 45 CFR
  Parts 160/162/164, and drive readiness for the 2025 Security Rule NPRM (90 FR 898).
framework: HIPAA
authority: HHS Office for Civil Rights (OCR)
version: 1.0
---

# SKILL: HIPAA Certification & Compliance

## Purpose
Operationalize HIPAA's three rules across PHI and ePHI and prepare for the mandatory 2025 baselines.

## Regulatory structure
- **45 CFR Part 160** — general provisions, definitions (covered entity, business associate), preemption, Enforcement Rule (four-tier culpability, civil monetary penalties).
- **45 CFR Part 162** — standard transactions and code sets.
- **45 CFR Part 164** — Privacy Rule (Subpart E), Security Rule (Subpart C), Breach Notification Rule (Subpart D).

## Privacy Rule (Subpart E) — key obligations
- PHI = individually identifiable health info in any form (electronic, paper, oral). Excludes employment records and FERPA education records.
- No use/disclosure of PHI without permission or written authorization; treatment/payment/operations permitted; national-priority disclosures (public health, judicial, serious threat) permitted without authorization.
- **Minimum necessary** standard — does not apply to treatment disclosures to providers.
- **Notice of Privacy Practices** provided no later than first service delivery.
- Individual rights: access, amendment, accounting of disclosures.
- Designate a **Privacy Official**.

## Security Rule (Subpart C) — safeguards for ePHI
- **Administrative:** security management process incl. risk analysis §164.308(a)(1)(ii)(A); security official; workforce training; incident response.
- **Physical:** facility access controls, workstation use, device/media disposal and re-use.
- **Technical:** unique user ID, audit controls, integrity controls, access controls, transmission security (encryption).

## 2025 NPRM (90 FR 898) — readiness baselines (treat as mandatory)
- Remove "addressable" vs "required" — **all controls mandatory**.
- **MFA** for all systems/internet-accessible assets touching ePHI.
- **Encryption** of ePHI at rest and in transit — no exceptions.
- **Annual** risk assessment + compliance audit (no stale multi-year analyses).
- **Bi-annual** automated vulnerability scans; **annual** penetration testing.
- **72-hour** disaster-recovery capability, established/maintained/tested.
- Business associates **annually certify** compliance to covered entities.
- Comment period closed Mar 2025; final action anticipated **May 2026**.

## Breach Notification Rule (§§164.400–414)
- **Presumption of breach** unless a documented four-factor risk assessment shows low probability of compromise:
  1. nature/extent of PHI (re-identification likelihood),
  2. who used/received it,
  3. whether actually acquired/viewed,
  4. extent of mitigation.
- **<500 individuals:** notify individuals without unreasonable delay, ≤**60 days**; log and notify HHS annually (≤60 days after calendar-year end).
- **≥500 individuals:** notify individuals + HHS ≤**60 days**; media notice within the same window; OCR public portal listing.
- **Substitute notice** if contact info missing for ≥10 individuals: homepage notice ≥90 days + toll-free number.
- Precedent: *Presence Health* (2017) — $475,000 penalty for exceeding the 60-day notification limit.

## Operational workflow
1. Inventory PHI/ePHI flows; map covered-entity vs business-associate roles.
2. Run/refresh the §164.308 risk analysis at least annually.
3. Build a control register mapped to CFR sections; mark NPRM-readiness status per control.
4. Enforce MFA + encryption now; schedule vuln scans (bi-annual) and pen test (annual).
5. Maintain BAAs; collect annual vendor certifications.
6. On suspected breach: contain, run the four-factor test, notify on the ≤60-day clock.

## Guardrails (mandatory)
- Never exceed the 60-day breach clock; never delay notice for reputational reasons.
- Never rely on a stale risk analysis.
- Escalate penalty-exposure and legal-interpretation judgment to human counsel.

## Authoritative references
- HHS Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- HHS Breach Notification Rule: https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html
- 2025 NPRM (90 FR 898): https://www.govinfo.gov/app/details/FR-2025-01-06/2024-30983
