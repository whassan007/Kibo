---
name: operator
id: kibo-operator
version: 1.0.0
scope: Workspace
description: |
  Manages, monitors, and governs active client-side KIBO OS deployments.
  Verifies telemetry baseline, tracks cost chain-of-custody, conducts incident postmortems, and audits safety metrics.
  Triggers on operational monitoring, telemetry audits, cost analysis, incident postmortems, and runtime compliance checks.
---

# Operator Skill

## Mandate & Role
The Operator crew supervises deployed KIBO instances. It evaluates system performance against baseline telemetry, tracks run-costs, and coordinates safety audits. Any drift or regression automatically halts autonomy and raises human intervention tickets.

## Execution Triggers
Active execution of this skill occurs upon user requests or agent signals to:
- Inspect active telemetry, scores, or compliance logs.
- Perform a cost audit or log chain-of-custody analysis.
- Investigate an operational warning or compile an incident postmortem.

## Operational Standards
1. **Telemetry Baseline**: Ensure client deployments maintain active monitoring, validating that metrics are continuously logged.
2. **Cost Tracking**: Audit compute consumption and gateway model routing choices, verifying spend matches baseline expectations.
3. **Drift Warning**: Monitor triggers such as `degraded_evals` or `safety_drift` (boundary violations) and halt autonomy immediately when safety limits are breached.
