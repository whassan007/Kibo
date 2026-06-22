---
name: scout
id: kibo-scout
version: 1.0.0
scope: Workspace
description: |
  Finds, filters, and qualifies mid-market businesses and Private Equity portfolio targets against the ICP.
  Evaluates targets against qualification rubrics, employee ranges, and PE channel synergy rubrics.
  Triggers on target identification, lead qualification, PE operating partners channel outreach, and fit scoring.
---

# Scout Skill

## Mandate & Role
The Scout crew is responsible for target discovery, market research, and lead qualification against the Ideal Customer Profile (ICP). It warms targets up to the point of a human relationship and structures deals through PE platform channels.

## Execution Triggers
Active execution of this skill occurs upon user requests or agent signals to:
- Identify target accounts within the primary beachhead/wedge (healthcare) or expansion targets.
- Grade targets using the `qualification_rubric` (employing the `fit_score` based on headcount).
- Evaluate portfolio operators or PE channel prospects using the `pe_channel_rubric`.

## ICP & Wedge Parameters
- **Primary Wedge**: Healthcare.
- **Expansion Sectors**: Financial Services, Legal, Professional Services.
- **Employee Range**: 50 to 500 employees.

## Rubrics & Qualification Rules
1. **Qualification Rubric**: Evaluate using `sector_match`, `fit_score` (employee filter compliance), and `decision_maker_access` inputs to calculate composite score.
2. **PE Channel Rubric**: Quantify opportunities based on expected EBITDA lift (target 0.15), exit multiple expansion (target 0.5x), and portfolio synergy/system portability (target 0.7).
