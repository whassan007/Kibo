# Chief Privacy Officer — Agent & Skill Library

Multi-agent CPO system. **3 jurisdictions × 5 task domains = 15 agents**, each paired with a jurisdiction-specific `SKILL.md`.

Each folder contains:
- `AGENT.md` — the agent system prompt (role, scope, operating principles, output contract).
- `SKILL.md` — operational knowledge (controlling law, workflow, deadlines, guardrails, references) the agent loads first.

## Structure

```
cpo-agents/
  us/
    01-jurisdictional-governance/        # Jurisdictional & Regulatory Governance
      AGENT.md
      SKILL.md
    02-dsar-rights-management/        # Data Subject Rights & Inquiry Management
      AGENT.md
      SKILL.md
    03-auditing-policy-governance/        # Continuous Auditing & Policy Governance
      AGENT.md
      SKILL.md
    04-risk-assessment-legal/        # Risk Assessment & Legal Analysis
      AGENT.md
      SKILL.md
    05-advisory-training-incident/        # Advisory, Training & Incident Response
      AGENT.md
      SKILL.md
  canada/
    01-jurisdictional-governance/        # Jurisdictional & Regulatory Governance
      AGENT.md
      SKILL.md
    02-dsar-rights-management/        # Data Subject Rights & Inquiry Management
      AGENT.md
      SKILL.md
    03-auditing-policy-governance/        # Continuous Auditing & Policy Governance
      AGENT.md
      SKILL.md
    04-risk-assessment-legal/        # Risk Assessment & Legal Analysis
      AGENT.md
      SKILL.md
    05-advisory-training-incident/        # Advisory, Training & Incident Response
      AGENT.md
      SKILL.md
  eu/
    01-jurisdictional-governance/        # Jurisdictional & Regulatory Governance
      AGENT.md
      SKILL.md
    02-dsar-rights-management/        # Data Subject Rights & Inquiry Management
      AGENT.md
      SKILL.md
    03-auditing-policy-governance/        # Continuous Auditing & Policy Governance
      AGENT.md
      SKILL.md
    04-risk-assessment-legal/        # Risk Assessment & Legal Analysis
      AGENT.md
      SKILL.md
    05-advisory-training-incident/        # Advisory, Training & Incident Response
      AGENT.md
      SKILL.md
```

## Task domains

1. **Jurisdictional & Regulatory Governance** (`01-jurisdictional-governance`)
2. **Data Subject Rights & Inquiry Management** (`02-dsar-rights-management`)
3. **Continuous Auditing & Policy Governance** (`03-auditing-policy-governance`)
4. **Risk Assessment & Legal Analysis** (`04-risk-assessment-legal`)
5. **Advisory, Training & Incident Response** (`05-advisory-training-incident`)

## Jurisdictions

- **us** — United States (CCPA/CPRA + state patchwork, MHMDA, federal sectoral)
- **canada** — Canada (PIPEDA / Bill C-27 CPPA, Quebec Law 25, provincial)
- **eu** — European Union / EEA (GDPR, ePrivacy, related)

## Orchestration note

Designed for an agent router (e.g., MCP-based dispatch): a top-level CPO orchestrator selects jurisdiction + task domain, loads the matching `SKILL.md`, then runs the `AGENT.md` prompt. Skill files are the single source of truth for thresholds and deadlines — update the skill, not the prompt, when law changes.

## Important

These artifacts encode operational logic and statutory references current to mid-2026. They are decision-support scaffolding, **not legal advice**. Pending reforms (US APRA, Canada Bill C-27) are flagged as prospective. Every agent escalates novel legal judgment to human counsel.
