# Compliance & Certification Frameworks — Agent & Skill Library

Certification/assessment agents complementing the jurisdictional CPO agents. One agent + skill file per framework.

## Frameworks

- **HIPAA (45 CFR Parts 160/162/164)** (`hipaa/`)
- **Canada Health Infoway — PIA + HTRA/TRA-1** (`infoway-htra/`)
- **ISO/IEC 27701:2025 PIMS** (`iso-27701-2025/`)
- **AICPA SOC 2 (Trust Services Criteria)** (`soc2/`)

## Structure

```
compliance-frameworks/
  hipaa/        # HIPAA (45 CFR Parts 160/162/164)
    AGENT.md
    SKILL.md
  infoway-htra/        # Canada Health Infoway — PIA + HTRA/TRA-1
    AGENT.md
    SKILL.md
  iso-27701-2025/        # ISO/IEC 27701:2025 PIMS
    AGENT.md
    SKILL.md
  soc2/        # AICPA SOC 2 (Trust Services Criteria)
    AGENT.md
    SKILL.md
```

## Coverage notes

- **HIPAA** — Privacy/Security/Breach rules + 2025 NPRM (90 FR 898) readiness (MFA, encryption, annual risk assessment, vuln scans, pen test, 72h DR, BA certification).
- **Canada Health Infoway** — dual-track PIA (ten fair-information principles / PHIPA) + HTRA/TRA-1 (CSE/RCMP; Risk = f(Threat, Vulnerability, Impact)); delta-TRA triggers; NAPRA PPMS application.
- **ISO/IEC 27701:2025** — standalone PIMS, Clauses 4–10, Annex A (controllers) / Annex B (processors), 2019->2025 transition.
- **SOC 2** — five Trust Services Criteria (Security required) + COSO-derived Common Criteria CC1–CC9; Type II operating-effectiveness evidence.

## Cross-framework synthesis (from source analysis)

1. **Eradication of subjective flexibility** — HIPAA's 2025 NPRM removes 'addressable' controls, converging toward the continuous, tested posture long standard in SOC 2 and ISO.
2. **Decoupling of privacy from security** — ISO 27701:2025 standalone + SOC 2's split of Confidentiality vs Privacy + Canada's PIA/TRA split: privacy is now an independent governance discipline.
3. **Supply-chain liability** — Business Associates (HIPAA), PII Processors (27701 Annex B), HINPs (Canada), Vendor Risk Mgmt (SOC 2 CC9): liability cannot be outsourced.

These artifacts are decision-support scaffolding, **not legal or audit advice**. The HIPAA 2025 NPRM baselines are treated as mandatory for readiness but reach final action ~May 2026; verify before relying. Every agent escalates legal/audit-opinion judgment to a human.
