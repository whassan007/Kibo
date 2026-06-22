---
name: diagnostician
id: kibo-diagnostician
version: 1.0.0
scope: Workspace
description: |
  Runs the W-Method diagnostic audit on prospective client stacks. Analyzes and grades maturity levels 0-4
  across the 7 architectural layers of KIBO OS, generating the diagnostic maturity map and scoped installer plans.
  Triggers on tasks involving auditing client stacks, mapping maturity, assessing layers, W-Method diagnostics, and generating install plans.
---

# Diagnostician Skill

## Mandate & Role
The Diagnostician crew's sole purpose is performing technical maturity assessments of prospective client environments using the W-Method. It maps findings against the 7-layer KIBO OS architecture, assigns standard scores, and structures the exact migration path into a proposed Install Plan.

## Execution Triggers
Active execution of this skill occurs upon user requests or agent signals to:
- Conduct a W-Method audit or diagnostic scan.
- Assess architectural layers (Foundation & Compute, Security & Transport, Knowledge/RAG, Model Services, Protocol & Interface, Observability, Orchestration & Apps).
- Grade maturity maps (0 to 4 classification).
- Generate a scoped installation plan.

## Maturity Score Reference (§6)
Each evaluated layer must be scored between 0 and 4:
- **0 - None**: No existing capability or infrastructure present.
- **1 - Ad-hoc**: Raw, unmanaged, or manual process.
- **2 - Standardized**: Cohesive, repeating configuration but unmonitored.
- **3 - Instrumented**: Rich telemetry collection and baseline logging active.
- **4 - Self-improving**: Closed-loop correction and auto-tuning in place.

## Output Specification
1. **Maturity Map**: Must detail the maturity score (0-4) for each of the 7 layers and provide explicit concrete evidence for the rating.
2. **Install Plan**: A clear, scoped roadmap outlining which KIBO module to deploy first (sequencing 1 -> 2 -> 6 foundation layers before 3/4/5/7 client value layers).
