---
name: european-union-risk-assessment
description: >-
  Run Article 35 DPIAs, govern international transfers post-Schrems II, and negotiate Article 28 processor terms.
jurisdiction: European Union / EEA
task_domain: Risk Assessment & Legal Analysis
version: 1.0
---

# SKILL: Risk Assessment & Legal Analysis — European Union / EEA

## Purpose
Run Article 35 DPIAs, govern international transfers post-Schrems II, and negotiate Article 28 processor terms.

## Controlling frameworks & key obligations
- **DPIA (Art 35):** mandatory for high-risk processing — large-scale special-category data, systematic monitoring of public areas, automated decision-making with legal/significant effects, and processing on EDPB/DPA blacklists.
- **Prior consultation (Art 36):** where residual high risk remains after mitigation.
- **Transfers (Ch V):** adequacy decisions; Art 46 mechanisms (SCCs, BCRs); Schrems II requires a TIA of destination surveillance law + supplementary measures.
- **Processors (Art 28):** binding DPA with required clauses; sub-processor authorization.

## Operational workflow
1. Auto-populate the DPIA from the RoPA at design time.
2. Apply the Art 35 trigger test; run the DPIA for high-risk processing.
3. If residual high risk persists, route to Art 36 prior consultation.
4. For each transfer, confirm an Art 45/46 basis; run the TIA; mandate supplementary measures (encryption, pseudonymization) where adequacy is absent.
5. Negotiate Art 28 DPAs: purpose limitation, confidentiality, security (Art 32), sub-processor flow-down, assistance, deletion/return, audit.
6. Block high-risk launches without a completed DPIA; escalate prior-consultation triggers.

## Statutory deadlines & thresholds
- DPIA must precede high-risk processing.
- Art 36 prior consultation before processing where residual high risk remains.
- Breach context: see Incident skill for the 72-hour clock.

## Guardrails (mandatory)
- Do not self-certify transfer adequacy; escalate residual high risk to human counsel.
- Block high-risk launches lacking a completed DPIA.

## Authoritative references
- GDPR DPIA (Arts 35–36): https://gdpr-info.eu/
- Transfers / SCCs: https://commission.europa.eu/law/law-topic/data-protection_en
- EDPB guidelines: https://edpb.ec.europa.eu/our-work-tools/our-documents_en
