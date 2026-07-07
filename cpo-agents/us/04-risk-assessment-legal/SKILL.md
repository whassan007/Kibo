---
name: united-states-risk-assessment
description: >-
  Embed risk assessments in the SDLC, run Transfer Impact Assessments, and govern vendor DPA risk under US state privacy law.
jurisdiction: United States
task_domain: Risk Assessment & Legal Analysis
version: 1.0
---

# SKILL: Risk Assessment & Legal Analysis — United States

## Purpose
Embed risk assessments in the SDLC, run Transfer Impact Assessments, and govern vendor DPA risk under US state privacy law.

## Controlling frameworks & key obligations
- **State data protection assessments:** required by CO, CT, VA, TX, OR and others before targeted advertising, sale of PI, sensitive-data processing, and profiling with legal/significant effects.
- **CPRA:** risk assessments and cybersecurity audits (per CPPA regulations).
- **Cross-border:** TIA for flows to/from third countries; sub-processor mapping.
- **Vendors:** DPA/addendum review; service-provider vs third-party characterization under CCPA.

## Operational workflow
1. Pull the processing description from the inventory at design time; auto-populate the assessment template.
2. Determine if the activity is "high risk" (targeted ads, sale, sensitive data, profiling with significant effects) → mandatory assessment.
3. For automated decision-making, document logic, impact, and human-review safeguards required by the applicable state.
4. Map data flows and sub-processors; run the TIA.
5. Review vendor DPA; require service-provider restrictions, security, sub-processor flow-down, and breach-cooperation clauses.
6. Block launch if a required assessment is incomplete; escalate residual high risk.

## Statutory deadlines & thresholds
- Assessments must precede the high-risk processing.
- Retain assessments for regulator production on request.

## Guardrails (mandatory)
- Do not self-certify legal adequacy; escalate residual high risk to human counsel.
- Block high-risk launches lacking a completed assessment.

## Authoritative references
- CPPA rulemaking: https://cppa.ca.gov/regulations/
- Colorado AG (rules): https://coag.gov/
- State comparison: https://www.troutman.com/insights/
