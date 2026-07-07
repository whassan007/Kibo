---
name: canada-infoway-pia-htra
description: >-
  Govern dual-track Canadian health-data assessments — Privacy Impact Assessment (PIA) against
  PIPEDA/PHIPA and the ten fair-information principles, and the Harmonized Threat & Risk
  Assessment (HTRA/TRA-1) for technical cyber defense — under Canada Health Infoway architecture.
framework: Canada Health Infoway (PIA + HTRA/TRA-1)
authority: OPC (federal), provincial commissioners (e.g., Ontario IPC), CSE/RCMP (HTRA)
version: 1.0
---

# SKILL: Canada Health Infoway — PIA + HTRA/TRA-1

## Purpose
Clear new health systems/services through parallel PIA (legal/ethical) and TRA (technical) evaluations and keep both current.

## Legislative foundation
- **PIPEDA** incorporates **CAN/CSA-Q830-96** via Schedule 1 — the ten fair-information principles.
- Provincial health statutes (e.g., Ontario **PHIPA**) govern Health Information Custodians (HICs); Health Information Network Providers (HINPs) carry network duties.
- **Canada Health Infoway** PSA + Infoway Privacy and Security Assessment Policy mandate structured risk assessments for Infoway-associated initiatives.

## The ten fair-information principles (PIA evaluation baseline)
1. Accountability — designate a Privacy Officer; liability not outsourceable (enforce DSAs/vendor risk).
2. Identifying Purposes — purposes fixed at/before collection; no mission creep.
3. Consent — informed consent except narrow emergencies; supports lockbox/masking directives.
4. Limiting Collection — data minimization in schema design.
5. Limiting Use/Disclosure/Retention — lifecycle management and cryptographic shredding.
6. Accuracy — accurate/complete/current (clinical-safety critical).
7. Safeguards — protection commensurate with sensitivity (encryption, access control, audit logs).
8. Openness — public, understandable privacy policies.
9. Individual Access — access, verify, challenge, amend; computable export via portals.
10. Challenging Compliance — documented complaint/remediation pathway.

## Privacy Impact Assessment (PIA)
- Qualitative methodology evaluating a system against applicable law (e.g., PHIPA) across the full PHI lifecycle (collection → destruction).
- Three phases: collect systemic information → determine privacy risks → propose mitigations.
- Evaluates e.g. whether implied consent suffices, whether identity is isolated from analytics.
- **Submit PIA summaries to the oversight body (e.g., Ontario Health) as a precondition for integration.**

## Harmonized Threat & Risk Assessment (HTRA / TRA-1)
Methodology (CSE + RCMP) lifecycle:
1. **Asset identification & valuation** — physical/logical/personnel assets vs CIA value.
2. **Threat assessment** — actor capability, intent, prevalence (external, insider, negligent).
3. **Vulnerability appraisal** — architectural/physical/administrative weaknesses.
4. **Risk analysis** — Risk = f(Threat, Vulnerability, Impact).
5. **Control analysis & risk treatment** — mitigate to acceptable threshold; controls from **ISO/IEC 27799** or **NIST 800-30**.
- **Delta TRA** required on significant architectural change, support-model shift, or PHIPA update.

## Convergence rule
PIA defines **what** data may lawfully exist/flow; TRA defines **how** it is defended. Both are required; neither substitutes for the other.

## Sector application — Pharmacy Practice Management Systems (NAPRA PPMS)
- Mandatory TRA + PIA before deployment.
- E-prescription generation must be a deliberate, auditable act by an identified authorized prescriber/pharmacist.
- Requires granular access controls, automatic logout, and drug-utilization reporting (patient-identified or safely de-identified/aggregated).

## Guardrails (mandatory)
- Never deploy without both a completed PIA and TRA.
- Never let the PIA stand in for the TRA (or vice versa).
- Trigger a delta TRA on qualifying change; escalate residual high risk to human counsel.

## Authoritative references
- Infoway Privacy & Security: https://www.infoway-inforoute.ca/en/what-we-do/connected-care/privacy-security
- Harmonized TRA (TRA-1), Canadian Centre for Cyber Security: https://www.cyber.gc.ca/en/tools-services/harmonized-tra-methodology
- OPC PIPEDA: https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/
