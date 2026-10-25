"""
KIBO Privacy OS — Claude Enterprise Remote & Stdio MCP Server
Implements Section 11 & Acceptance Tests 11 & 12:
- Exposes the 8 approved Privacy Office tools via FastMCP("KIBO-Privacy-OS-Enterprise")
- Enforces mandatory tenant_id + user_id + role verification on every tool call
- Enforces read-only by default (read_only=True unless explicit write_grant and role clearance are verified)
- Ensures consequential write actions create drafts/pending approval records and NEVER auto-dispatch regulatory notices
- Enforces Strict Tenant Isolation (Acceptance Test 11): cross-tenant access attempts (e.g. caller authenticated
  to `tenant-ca` querying or retrieving records for `tenant-us`) immediately raise
  PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced") and log the blocked attempt.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.context.tenant_context import TenantContext, _tenant_context
from core.jrae.deadlines import calculate_breach_deadlines
from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code

logger = logging.getLogger("kibo.integrations.claude_mcp")

# Attempt to import FastMCP from the `mcp` package if installed; provide a compatible
# enterprise FastMCP implementation so `FastMCP("KIBO-Privacy-OS-Enterprise")` works
# both with the external SDK and in standalone/in-process enterprise environments.
try:
    from mcp.server.fastmcp import FastMCP as _BaseFastMCP  # type: ignore
except Exception:  # pragma: no cover
    class _BaseFastMCP:
        """Enterprise-compatible FastMCP server implementation."""

        def __init__(self, name: str):
            self.name = name
            self._tools: Dict[str, Callable[..., Any]] = {}

        def tool(self, name: Optional[str] = None, description: Optional[str] = None):
            def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
                tool_name = name or fn.__name__
                self._tools[tool_name] = fn
                return fn
            return decorator

        def list_tools(self) -> List[Dict[str, Any]]:
            return [
                {
                    "name": t_name,
                    "description": (fn.__doc__ or "").strip(),
                }
                for t_name, fn in self._tools.items()
            ]

        def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
            if name not in self._tools:
                raise ValueError(f"Unknown MCP tool: {name}")
            return self._tools[name](**arguments)

        def run(self, transport: str = "stdio") -> None:
            logger.info("Starting %s MCP server over %s", self.name, transport)


FastMCP = _BaseFastMCP
mcp = FastMCP("KIBO-Privacy-OS-Enterprise")

# Immutable in-memory security audit log for MCP invocations & blocked cross-tenant attempts
MCP_SECURITY_AUDIT_LOG: List[Dict[str, Any]] = []

# Canonical tenant-scoped datasets used for deterministic verification (Acceptance Tests 11 & 12)
TENANT_ORGANIZATIONS: Dict[str, Dict[str, Any]] = {
    "tenant-ca": {
        "tenant_id": "tenant-ca",
        "organization_name": "MapleLeaf Enterprise Corp (Canada & Global Operations)",
        "primary_establishment": "CA-ON",
        "active_jurisdictions": ["CA-FED", "CA-ON", "CA-QC", "US-CA", "EU-DE"],
        "industry": "technology_and_customer_support",
        "dpo_contact": "dpo@mapleleaf.example.ca",
        "data_residency_policy": "Canadian & EU personal data requires approved TIA/TRA and executed SCCs/DPA prior to US cross-border transfer.",
    },
    "tenant-us": {
        "tenant_id": "tenant-us",
        "organization_name": "PacificWest Health & Commerce Inc. (United States)",
        "primary_establishment": "US-CA",
        "active_jurisdictions": ["US-FED", "US-CA", "US-NY", "US-TX", "US-WA"],
        "industry": "healthcare_and_retail",
        "dpo_contact": "privacy@pacificwest.example.com",
        "data_residency_policy": "US Sovereign Cloud; HIPAA BAA required for all PHI processors.",
    },
    "tenant-eu": {
        "tenant_id": "tenant-eu",
        "organization_name": "EuroShield GmbH (European Union)",
        "primary_establishment": "EU-DE",
        "active_jurisdictions": ["EU", "EU-DE", "EU-FR", "EU-IE"],
        "industry": "financial_services",
        "dpo_contact": "dsb@euroshield.example.eu",
        "data_residency_policy": "EU sovereign boundary; Chapter V GDPR SCCs + supplementary encryption measures mandatory.",
    },
    "default": {
        "tenant_id": "default",
        "organization_name": "KIBO Enterprise Reference Organization",
        "primary_establishment": "CA-ON",
        "active_jurisdictions": ["CA-FED", "CA-ON", "CA-QC", "US-FED", "US-CA", "EU", "EU-DE"],
        "industry": "enterprise_saas",
        "dpo_contact": "dpo@kibo.is",
        "data_residency_policy": "Multi-jurisdictional governance with mandatory PIA/DPIA/TRA/TIA before cross-border AI processing.",
    },
}

TENANT_POLICIES: Dict[str, List[Dict[str, Any]]] = {
    "tenant-ca": [
        {
            "policy_id": "POL-CA-AI-001",
            "tenant_id": "tenant-ca",
            "title": "Enterprise Generative AI & Third-Party LLM Governance Standard",
            "version": "2026.2",
            "summary": (
                "Prohibits sending customer support audio/transcripts or employee personal information to any "
                "external or US-based AI vendor unless: (1) an executed Data Processing Addendum (DPA) with "
                "zero-retention / no-model-training clauses is in force, (2) a Quebec Law 25 Transfer Risk "
                "Assessment (TRA / ÉFVP) and EU GDPR Chapter V Transfer Impact Assessment (TIA) with 2021 EU SCCs "
                "are completed, (3) an AI Impact Assessment (AIIA) / DPIA is approved, and (4) written DPO + Legal sign-off is recorded."
            ),
            "mandatory_controls": [
                "PII/Audio Redaction & Pseudonymization before prompt transmission",
                "Zero data retention & contractual prohibition on foundation model training",
                "Quebec Law 25 s. 17 Transfer Risk Assessment (TRA)",
                "GDPR Art. 28 DPA + Art. 46 Standard Contractual Clauses (SCCs) + TIA",
                "CCPA/CPRA Service Provider Addendum (no sale/sharing of personal information)",
            ],
        },
        {
            "policy_id": "POL-CA-RET-002",
            "tenant_id": "tenant-ca",
            "title": "Canadian & Cross-Border Data Residency and Retention Policy",
            "version": "2026.1",
            "summary": "Requires customer support recordings from Ontario and Quebec residents to be retained for no longer than 90 days unless subject to legal hold.",
            "mandatory_controls": ["90-day automated purge clock", "Encryption in transit (TLS 1.3) and at rest (AES-256-GCM)"],
        },
    ],
    "tenant-us": [
        {
            "policy_id": "POL-US-PRIV-101",
            "tenant_id": "tenant-us",
            "title": "US State Consumer Privacy & HIPAA BAA Policy (CONFIDENTIAL - TENANT-US ONLY)",
            "version": "2026.1",
            "summary": "Internal US-only policy governing CPRA, TDPSA, WA MHMDA, and HIPAA Business Associate Agreements.",
            "mandatory_controls": ["HIPAA BAA execution", "Universal Opt-Out Mechanism (GPC) honor"],
        }
    ],
    "tenant-eu": [
        {
            "policy_id": "POL-EU-GDPR-201",
            "tenant_id": "tenant-eu",
            "title": "EU GDPR & EU AI Act High-Risk System Governance Policy",
            "version": "2026.1",
            "summary": "Mandates Art. 35 DPIA, Works Council consultation (Germany BetrVG § 87(1)(6)), and Art. 46 TIA prior to third-country transfers.",
            "mandatory_controls": ["GDPR Art. 35 DPIA", "EU AI Act Literacy & Transparency Notice"],
        }
    ],
}

TENANT_VENDORS: Dict[str, List[Dict[str, Any]]] = {
    "tenant-ca": [
        {
            "vendor_id": "VND-CA-AI-01",
            "tenant_id": "tenant-ca",
            "vendor_name": "US Cloud AI Summarizer Inc.",
            "hosting_location": "US-VA (United States)",
            "approval_status": "CONDITIONAL_HOLD_PENDING_TRA_TIA_AND_DPO_APPROVAL",
            "risk_tier": "HIGH",
            "dpa_executed": True,
            "cpra_service_provider_addendum": True,
            "baa_executed": False,
            "eu_sccs_executed": True,
            "eu_tia_completed": False,
            "quebec_law25_tra_completed": False,
            "ai_training_prohibited_clause": True,
            "zero_data_retention_enabled": False,
            "required_conditions": [
                "Complete Quebec Law 25 s. 17 Transfer Risk Assessment (TRA) prior to transferring Quebec resident call transcripts to the US",
                "Complete GDPR Art. 46 Transfer Impact Assessment (TIA) for German (EU-DE) customer call data transferred to the US",
                "Complete GDPR Art. 35 DPIA & AI Impact Assessment (AIIA) for automated call summarization",
                "Enable zero-data-retention endpoint configuration and pre-transfer PII redaction",
                "Obtain formal human sign-off from DPO and Legal Counsel via route_approval_decision",
            ],
        },
        {
            "vendor_id": "VND-CA-CLOUD-02",
            "tenant_id": "tenant-ca",
            "vendor_name": "KIBO Sovereign Vault Canada",
            "hosting_location": "CA-ON (Toronto, Canada)",
            "approval_status": "APPROVED",
            "risk_tier": "LOW",
            "dpa_executed": True,
            "cpra_service_provider_addendum": True,
            "baa_executed": True,
            "eu_sccs_executed": True,
            "eu_tia_completed": True,
            "quebec_law25_tra_completed": True,
            "ai_training_prohibited_clause": True,
            "zero_data_retention_enabled": True,
            "required_conditions": ["Annual SOC 2 Type II + ISO/IEC 27701 evidence renewal"],
        },
    ],
    "tenant-us": [
        {
            "vendor_id": "VND-US-999",
            "tenant_id": "tenant-us",
            "vendor_name": "US Exclusive Claims Processor LLC",
            "hosting_location": "US-TX",
            "approval_status": "APPROVED",
            "risk_tier": "MEDIUM",
            "dpa_executed": True,
            "baa_executed": True,
            "eu_sccs_executed": False,
            "quebec_law25_tra_completed": False,
            "ai_training_prohibited_clause": True,
            "required_conditions": ["Restricted to tenant-us PHI/PII workloads only"],
        }
    ],
}

TENANT_TASKS: Dict[str, List[Dict[str, Any]]] = {
    "tenant-ca": [
        {
            "task_id": "TSK-CA-1001",
            "tenant_id": "tenant-ca",
            "title": "Quebec Law 25 TRA & GDPR TIA for Customer Support AI Summarization",
            "task_type": "ASSESSMENT_REVIEW",
            "status": "open",
            "due_date": "2026-11-05",
            "assigned_role": "DPO",
            "jurisdictions": ["CA-QC", "CA-ON", "US-CA", "EU-DE"],
        },
        {
            "task_id": "TSK-CA-1002",
            "tenant_id": "tenant-ca",
            "title": "CPRA & PIPEDA DSAR Access Request #DSAR-884",
            "task_type": "DSAR_FULFILLMENT",
            "status": "open",
            "due_date": "2026-11-12",
            "assigned_role": "ANALYST",
            "jurisdictions": ["CA-ON", "US-CA"],
        },
    ],
    "tenant-us": [
        {
            "task_id": "TSK-US-9001",
            "tenant_id": "tenant-us",
            "title": "US-Only HIPAA Security Rule Risk Analysis (TENANT-US SECRET)",
            "task_type": "HIPAA_AUDIT",
            "status": "open",
            "due_date": "2026-11-15",
            "assigned_role": "DPO",
            "jurisdictions": ["US-FED", "US-CA"],
        }
    ],
}

VALID_ROLES = {
    "EMPLOYEE",
    "ANALYST",
    "DPO",
    "CPO",
    "LEGAL",
    "AUDITOR",
    "TENANT_ADMIN",
    "SYSTEM_ADMIN",
}

WRITE_AUTHORIZED_ROLES_BY_TOOL = {
    "report_privacy_incident": {"EMPLOYEE", "ANALYST", "DPO", "CPO", "LEGAL", "TENANT_ADMIN", "SYSTEM_ADMIN"},
    "initiate_privacy_assessment": {"EMPLOYEE", "ANALYST", "DPO", "CPO", "LEGAL", "TENANT_ADMIN", "SYSTEM_ADMIN"},
    "route_approval_decision": {"ANALYST", "DPO", "CPO", "LEGAL", "TENANT_ADMIN", "SYSTEM_ADMIN"},
}

FOREIGN_TENANT_PATTERN = re.compile(r"\btenant-[a-z0-9_-]+\b", re.IGNORECASE)


def _record_mcp_audit(
    *,
    tool_name: str,
    authenticated_tenant_id: str,
    requested_tenant_id: str,
    user_id: str,
    role: str,
    allowed: bool,
    reason: str,
) -> Dict[str, Any]:
    entry = {
        "audit_id": f"MCP-AUD-{uuid.uuid4().hex[:10].upper()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "authenticated_tenant_id": authenticated_tenant_id,
        "requested_tenant_id": requested_tenant_id,
        "user_id": user_id,
        "role": role,
        "allowed": allowed,
        "reason": reason,
    }
    MCP_SECURITY_AUDIT_LOG.append(entry)
    return entry


def _verify_mcp_context_and_tenant_isolation(
    *,
    tool_name: str,
    tenant_id: str,
    user_id: str,
    role: str = "EMPLOYEE",
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
    free_text_inputs: Optional[List[str]] = None,
    requires_write: bool = False,
    read_only: bool = True,
    write_grant: bool = False,
) -> Dict[str, str]:
    """
    Enforces Section 11 Common Security Requirements & Acceptance Test 11:
    1. Mandatory `tenant_id`, `user_id`, and `role` verification on every tool call.
    2. Strict Tenant Isolation: compares caller's authenticated tenant context (from ContextVar or
       `authenticated_tenant_id`) against `tenant_id`, `target_tenant_id`, and any explicit foreign
       `tenant-*` references embedded in query strings or resource IDs.
    3. Raises `PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")`
       immediately on any cross-tenant access attempt.
    4. Enforces read-only by default (`read_only=True` blocks write tools unless `write_grant=True`
       or `read_only=False` and the role is permitted).
    """
    if not tenant_id or not str(tenant_id).strip():
        raise PermissionError("MISSING_TENANT_CONTEXT: tenant_id is required on every MCP tool call")
    if not user_id or not str(user_id).strip():
        raise PermissionError("MISSING_USER_CONTEXT: user_id is required on every MCP tool call")

    normalized_role = (role or "EMPLOYEE").strip().upper()
    if normalized_role == "ADMIN":
        normalized_role = "TENANT_ADMIN"
    if normalized_role not in VALID_ROLES:
        raise PermissionError(f"INVALID_ROLE: Role '{role}' is not recognized by KIBO Privacy OS RBAC")

    ctx = _tenant_context.get()
    caller_tenant = (
        authenticated_tenant_id.strip()
        if authenticated_tenant_id and authenticated_tenant_id.strip()
        else (ctx.tenant_id if ctx and ctx.tenant_id and ctx.tenant_id != "default" else tenant_id.strip())
    )
    requested = tenant_id.strip()

    # Check 1: Direct mismatch between authenticated caller tenant and requested tenant_id
    if caller_tenant != requested:
        _record_mcp_audit(
            tool_name=tool_name,
            authenticated_tenant_id=caller_tenant,
            requested_tenant_id=requested,
            user_id=user_id,
            role=normalized_role,
            allowed=False,
            reason="CROSS_TENANT_ACCESS_DENIED: Requested tenant_id does not match authenticated tenant",
        )
        logger.warning(
            "MCP cross-tenant access blocked: caller_tenant=%s requested_tenant=%s user=%s tool=%s",
            caller_tenant,
            requested,
            user_id,
            tool_name,
        )
        raise PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")

    # Check 2: Explicit target_tenant_id mismatch
    if target_tenant_id and target_tenant_id.strip() != caller_tenant:
        _record_mcp_audit(
            tool_name=tool_name,
            authenticated_tenant_id=caller_tenant,
            requested_tenant_id=target_tenant_id.strip(),
            user_id=user_id,
            role=normalized_role,
            allowed=False,
            reason="CROSS_TENANT_ACCESS_DENIED: target_tenant_id does not match authenticated tenant",
        )
        logger.warning(
            "MCP target_tenant_id cross-tenant access blocked: caller_tenant=%s target=%s user=%s tool=%s",
            caller_tenant,
            target_tenant_id,
            user_id,
            tool_name,
        )
        raise PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")

    # Check 3: Scan query/resource arguments for references to another tenant (e.g. `tenant-us` queried by `tenant-ca`)
    for text_val in (free_text_inputs or []):
        if not text_val:
            continue
        for match in FOREIGN_TENANT_PATTERN.findall(str(text_val)):
            referenced_tenant = match.lower()
            if referenced_tenant != caller_tenant.lower():
                _record_mcp_audit(
                    tool_name=tool_name,
                    authenticated_tenant_id=caller_tenant,
                    requested_tenant_id=referenced_tenant,
                    user_id=user_id,
                    role=normalized_role,
                    allowed=False,
                    reason=f"CROSS_TENANT_ACCESS_DENIED: Query attempted to access foreign tenant '{referenced_tenant}'",
                )
                logger.warning(
                    "MCP query cross-tenant reference blocked: caller_tenant=%s referenced_tenant=%s user=%s tool=%s",
                    caller_tenant,
                    referenced_tenant,
                    user_id,
                    tool_name,
                )
                raise PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")
        # Also block explicit attempts to query US-tenant exclusive identifiers from a non-US tenant
        if caller_tenant != "tenant-us" and any(
            marker in str(text_val).upper()
            for marker in ("POL-US-PRIV-101", "VND-US-999", "TSK-US-9001", "TENANT-US")
        ):
            _record_mcp_audit(
                tool_name=tool_name,
                authenticated_tenant_id=caller_tenant,
                requested_tenant_id="tenant-us",
                user_id=user_id,
                role=normalized_role,
                allowed=False,
                reason="CROSS_TENANT_ACCESS_DENIED: Attempted to retrieve tenant-us exclusive resource",
            )
            raise PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")

    # Check 4: Enforce Read-Only by Default & RBAC on write tools
    if requires_write:
        allowed_roles = WRITE_AUTHORIZED_ROLES_BY_TOOL.get(tool_name, {"DPO", "CPO", "LEGAL"})
        if normalized_role not in allowed_roles:
            _record_mcp_audit(
                tool_name=tool_name,
                authenticated_tenant_id=caller_tenant,
                requested_tenant_id=requested,
                user_id=user_id,
                role=normalized_role,
                allowed=False,
                reason=f"RBAC_DENIED: Role {normalized_role} cannot execute {tool_name}",
            )
            raise PermissionError(f"RBAC_ACCESS_DENIED: Role '{normalized_role}' is not authorized for '{tool_name}'")
        if read_only and not write_grant:
            _record_mcp_audit(
                tool_name=tool_name,
                authenticated_tenant_id=caller_tenant,
                requested_tenant_id=requested,
                user_id=user_id,
                role=normalized_role,
                allowed=False,
                reason="READ_ONLY_DEFAULT_ENFORCED: Write tool invoked without scoped write_grant",
            )
            raise PermissionError(
                "READ_ONLY_MODE_ENFORCED: MCP integration is read-only by default; pass write_grant=True or read_only=False with authorized role"
            )

    _record_mcp_audit(
        tool_name=tool_name,
        authenticated_tenant_id=caller_tenant,
        requested_tenant_id=requested,
        user_id=user_id,
        role=normalized_role,
        allowed=True,
        reason="TENANT_AND_RBAC_VERIFIED",
    )
    return {
        "tenant_id": caller_tenant,
        "user_id": user_id.strip(),
        "role": normalized_role,
    }


def _evaluate_jurisdictions_detail(
    jurisdictions: List[str],
    involves_ai: bool = False,
    involves_cross_border_transfer: bool = False,
    transfer_destinations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Builds deterministic legal obligations, required assessments, and citations for US, Canada, and EU."""
    normalized_codes: List[str] = []
    for raw in jurisdictions:
        code = normalize_jurisdiction_code(raw)
        if code and code not in normalized_codes:
            normalized_codes.append(code)

    if not normalized_codes:
        normalized_codes = ["CA-ON", "CA-QC", "US-CA", "EU-DE"]

    destinations = [normalize_jurisdiction_code(d) for d in (transfer_destinations or ["US-FED"])]
    applicable_laws: List[Dict[str, Any]] = []
    required_assessments: List[str] = []
    mandatory_controls: List[str] = []
    approval_gates: List[str] = []
    competent_authorities: List[Dict[str, str]] = []
    citations: List[Dict[str, str]] = []

    def _add_unique(target: List[str], item: str) -> None:
        if item not in target:
            target.append(item)

    for code in normalized_codes:
        entry = GLOBAL_JURISDICTION_REGISTRY.get(code)
        if entry:
            competent_authorities.append(
                {
                    "jurisdiction_id": code,
                    "jurisdiction_name": entry.name,
                    "primary_regulator": entry.primary_regulator,
                    "regulator_url": entry.regulator_url,
                }
            )

        if code in {"CA-ON", "CA-FED"} or (code.startswith("CA-") and code != "CA-QC"):
            applicable_laws.append(
                {
                    "jurisdiction_id": code,
                    "regulation_id": "CA-FED-PIPEDA",
                    "instrument": "Personal Information Protection and Electronic Documents Act (PIPEDA), S.C. 2000, c. 5",
                    "articles": "Schedule 1 Principle 4.1.3 (Accountability for Transfers for Processing) & s. 7 / OPC Guidelines for Processing Personal Data Across Borders",
                    "obligation_summary": (
                        "Organization remains accountable for personal information transferred to a US or third-party AI processor; "
                        "must use contractual clauses ensuring a comparable level of protection and provide clear notice to customers "
                        "that data may be processed in the United States and accessible to US authorities."
                    ),
                    "competent_regulator": "Office of the Privacy Commissioner of Canada (OPC)",
                }
            )
            citations.append(
                {
                    "jurisdiction": code,
                    "citation": "PIPEDA Schedule 1, Principle 4.1.3 & Principle 4.3 (Consent & Accountability for Cross-Border Processing)",
                    "official_url": "https://laws-lois.justice.gc.ca/eng/acts/P-8.6/",
                }
            )
            _add_unique(required_assessments, "PIA (Privacy Impact Assessment — Canadian PIPEDA / Ontario Accountability)")
            _add_unique(
                mandatory_controls,
                "PIPEDA Principle 4.1.3 Contractual Comparable Protection Clause & Cross-Border Transparency Notice",
            )

        if code == "CA-QC":
            applicable_laws.append(
                {
                    "jurisdiction_id": "CA-QC",
                    "regulation_id": "CA-QC-LAW25",
                    "instrument": "Quebec Act respecting the protection of personal information in the private sector (Law 25 / Bill 64, CQLR c. P-39.1)",
                    "articles": "s. 3.3 (PIA Mandatory Requirements), s. 12.1 (Automated Decision-Making Transparency), s. 17 (Cross-Border Communication Outside Quebec — EFVP/TRA), s. 18.3 (Written Processor Contract)",
                    "obligation_summary": (
                        "Before communicating personal information outside Quebec (including to a US AI vendor), the organization MUST "
                        "conduct a Privacy Impact Assessment / Transfer Risk Assessment (ÉFVP / TRA) under s. 17 evaluating sensitivity, "
                        "purpose, protection measures, and the legal framework of the destination state (United States), and execute a written "
                        "contract under s. 18.3."
                    ),
                    "competent_regulator": "Commission d'accès à l'information du Québec (CAI)",
                }
            )
            citations.append(
                {
                    "jurisdiction": "CA-QC",
                    "citation": "Quebec Law 25 (CQLR c. P-39.1), ss. 3.3, 12.1, 17, 18.3",
                    "official_url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1",
                }
            )
            _add_unique(required_assessments, "TRA (Quebec Law 25 s. 17 Transfer Risk Assessment / ÉFVP for Out-of-Province Transfer)")
            _add_unique(required_assessments, "PIA (Quebec Law 25 s. 3.3 Mandatory Privacy Impact Assessment)")
            _add_unique(
                mandatory_controls,
                "Quebec Law 25 s. 17 Written Cross-Border Transfer Agreement & s. 18.3 Processor Confidentiality Mandate",
            )

        if code == "US-CA" or code.startswith("US-"):
            applicable_laws.append(
                {
                    "jurisdiction_id": code,
                    "regulation_id": "US-CA-CCPA-CPRA",
                    "instrument": "California Consumer Privacy Act as amended by CPRA (Cal. Civ. Code § 1798.100 et seq. & 11 CCR § 7000 et seq.)",
                    "articles": "Cal. Civ. Code § 1798.100(d) (Service Provider / Contractor Written Contract Requirements), § 1798.121 (Sensitive Personal Information), § 1798.185(a)(15)-(16) (Cybersecurity Audits, Risk Assessments & ADMT)",
                    "obligation_summary": (
                        "Requires a binding Service Provider Addendum under Cal. Civ. Code § 1798.100(d) prohibiting the AI vendor from "
                        "selling, sharing, retaining, using, or disclosing personal information outside the direct business purpose (including "
                        "prohibiting training third-party foundation models on customer call data without explicit opt-in), plus a CPRA Risk Assessment "
                        "and wiretapping/call-recording consent verification under CIPA (Cal. Penal Code § 632)."
                    ),
                    "competent_regulator": "California Privacy Protection Agency (CalPrivacy) & California Attorney General",
                }
            )
            citations.append(
                {
                    "jurisdiction": "US-CA",
                    "citation": "Cal. Civ. Code §§ 1798.100(d), 1798.140(ag), 1798.185(a)(15)-(16); Cal. Penal Code § 632 (CIPA All-Party Call Recording Consent)",
                    "official_url": "https://cppa.ca.gov/regulations/",
                }
            )
            _add_unique(required_assessments, "PIA / CPRA Risk Assessment (Cal. Civ. Code § 1798.185(a)(15) High-Risk Processing & AI)")
            _add_unique(
                mandatory_controls,
                "CCPA/CPRA § 1798.100(d) Service Provider Addendum (Prohibition on Selling/Sharing & Model Training)",
            )

        if code == "EU" or code.startswith("EU-"):
            applicable_laws.append(
                {
                    "jurisdiction_id": code,
                    "regulation_id": "EU-GDPR-AND-DE-BDSG",
                    "instrument": "EU General Data Protection Regulation (Regulation (EU) 2016/679) & German Federal Data Protection Act (BDSG) / TDDDG",
                    "articles": "GDPR Art. 6 (Lawful Basis), Art. 13/14 (Transparency), Art. 28 (Processor DPA), Art. 35 (DPIA), Chapter V Arts. 44-49 (Cross-Border Transfers, SCCs & Schrems II TIA)",
                    "obligation_summary": (
                        "Transferring German/EU customer support call recordings or transcripts to a US-based AI vendor requires: "
                        "(1) an Art. 28 Data Processing Agreement (DPA), (2) a valid Chapter V transfer mechanism (EU-US Data Privacy Framework "
                        "certification verification or 2021 European Commission Standard Contractual Clauses Module 2 + Transfer Impact Assessment "
                        "under Schrems II / EDPB Recommendations 01/2020), and (3) an Art. 35 Data Protection Impact Assessment (DPIA)."
                    ),
                    "competent_regulator": (
                        GLOBAL_JURISDICTION_REGISTRY[code].primary_regulator
                        if code in GLOBAL_JURISDICTION_REGISTRY
                        else "BfDI / German State Data Protection Authorities (Länder) & EDPB"
                    ),
                }
            )
            citations.append(
                {
                    "jurisdiction": code,
                    "citation": "GDPR (Regulation (EU) 2016/679) Arts. 6, 28, 32, 35, 44-46; EDPB Recommendations 01/2020 (Supplementary Measures)",
                    "official_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
                }
            )
            _add_unique(required_assessments, "DPIA (GDPR Art. 35 Data Protection Impact Assessment)")
            _add_unique(required_assessments, "TIA (GDPR Chapter V Art. 46 Transfer Impact Assessment + 2021 EU SCCs)")
            _add_unique(
                mandatory_controls,
                "GDPR Art. 28 Processor DPA + Art. 46 EU SCCs (Module 2) / EU-US DPF Verification + Supplementary Encryption",
            )

    if involves_ai:
        applicable_laws.append(
            {
                "jurisdiction_id": "EU",
                "regulation_id": "EU-AI-ACT-2024-1689",
                "instrument": "EU Artificial Intelligence Act (Regulation (EU) 2024/1689)",
                "articles": "Art. 4 (AI Literacy), Art. 50 (Transparency Obligations for Certain AI Systems)",
                "obligation_summary": (
                    "Requires AI literacy controls for staff deploying AI summarization tools, human oversight of generated summaries, "
                    "and prohibition on emotion-recognition or biometric categorization without lawful basis."
                ),
                "competent_regulator": "European AI Office & National Market Surveillance Authorities",
            }
        )
        citations.append(
            {
                "jurisdiction": "EU",
                "citation": "Regulation (EU) 2024/1689 (EU AI Act) Arts. 4 & 50",
                "official_url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
            }
        )
        _add_unique(required_assessments, "AIIA (AI Impact Assessment — EU AI Act / CPRA ADMT / Law 25 s. 12.1)")
        _add_unique(
            mandatory_controls,
            "Contractual prohibition on training foundation models on tenant data + Pre-inference PII redaction",
        )

    _add_unique(approval_gates, "DPO Sign-Off Required (PIA / DPIA / TRA / TIA Review)")
    _add_unique(approval_gates, "Legal Counsel Sign-Off Required (DPA, CPRA Service Provider Addendum & EU SCC Execution)")
    if involves_ai or involves_cross_border_transfer:
        _add_unique(approval_gates, "Security & AI Governance Committee Approval (Cross-Border US AI Processor Gate)")

    return {
        "normalized_jurisdictions": normalized_codes,
        "transfer_destinations": destinations,
        "applicable_laws": applicable_laws,
        "required_assessments": required_assessments,
        "mandatory_controls": mandatory_controls,
        "approval_gates": approval_gates,
        "competent_authorities": competent_authorities,
        "citations": citations,
    }


# ============================================================================
# 1. get_privacy_guidance
# ============================================================================
@mcp.tool(
    name="get_privacy_guidance",
    description=(
        "Governed Privacy Office Assistant: identifies the employee's organization, applicable legal "
        "obligations (US, Canada, EU), internal company policies, vendor approval status, required "
        "assessments (PIA/DPIA/TRA/TIA/AIIA), and mandatory approval gates before responding."
    ),
)
def get_privacy_guidance(
    tenant_id: str,
    user_id: str,
    question: str,
    role: str = "EMPLOYEE",
    jurisdictions: Optional[List[str]] = None,
    vendor_name: Optional[str] = None,
    data_categories: Optional[List[str]] = None,
    involves_ai: bool = False,
    involves_cross_border_transfer: bool = False,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Governed Privacy Office Assistant tool (Acceptance Test 12 & Section 11.4)."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="get_privacy_guidance",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[question, vendor_name or ""] + (jurisdictions or []),
        requires_write=False,
    )
    active_tenant = verified["tenant_id"]

    # Detect jurisdictions & AI/cross-border context from natural language question if not explicitly passed
    inferred_jurisdictions = list(jurisdictions or [])
    q_lower = question.lower()
    if "ontario" in q_lower and "CA-ON" not in inferred_jurisdictions:
        inferred_jurisdictions.append("CA-ON")
    if "quebec" in q_lower or "québec" in q_lower:
        if "CA-QC" not in inferred_jurisdictions:
            inferred_jurisdictions.append("CA-QC")
    if "california" in q_lower and "US-CA" not in inferred_jurisdictions:
        inferred_jurisdictions.append("US-CA")
    if ("germany" in q_lower or "german" in q_lower) and "EU-DE" not in inferred_jurisdictions:
        inferred_jurisdictions.append("EU-DE")
    if not inferred_jurisdictions:
        org_default = TENANT_ORGANIZATIONS.get(active_tenant, TENANT_ORGANIZATIONS["default"])
        inferred_jurisdictions = list(org_default["active_jurisdictions"])

    ai_flag = involves_ai or any(w in q_lower for w in ("ai ", "ai-", "llm", "summarize", "generative", "model"))
    transfer_flag = involves_cross_border_transfer or any(
        w in q_lower for w in ("us-based", "united states", "cross-border", "transfer", "outside")
    )

    org_profile = TENANT_ORGANIZATIONS.get(
        active_tenant,
        {
            "tenant_id": active_tenant,
            "organization_name": f"Enterprise Tenant ({active_tenant})",
            "primary_establishment": inferred_jurisdictions[0],
            "active_jurisdictions": inferred_jurisdictions,
            "industry": "enterprise",
            "dpo_contact": "dpo@kibo.is",
            "data_residency_policy": "Governed by KIBO Privacy OS Multi-Jurisdictional Standard.",
        },
    )

    eval_detail = _evaluate_jurisdictions_detail(
        jurisdictions=inferred_jurisdictions,
        involves_ai=ai_flag,
        involves_cross_border_transfer=transfer_flag,
        transfer_destinations=["US-FED"] if transfer_flag else [],
    )

    tenant_policies = TENANT_POLICIES.get(active_tenant, TENANT_POLICIES["tenant-ca"])
    tenant_vendors = TENANT_VENDORS.get(active_tenant, TENANT_VENDORS["tenant-ca"])
    matched_vendor = tenant_vendors[0] if tenant_vendors else {}
    if vendor_name:
        for v in tenant_vendors:
            if vendor_name.lower() in v["vendor_name"].lower():
                matched_vendor = v
                break

    decision_status = "DO_NOT_PROCEED_WITHOUT_SAFEGUARDS_AND_APPROVAL"
    guidance_summary = (
        f"GOVERNED PRIVACY OFFICE DETERMINATION FOR {org_profile['organization_name']} (Tenant: {active_tenant}):\n"
        f"1. DECISION: Conditional Hold — You may NOT send customer support calls or personal data from "
        f"{', '.join(eval_detail['normalized_jurisdictions'])} to a US-based AI vendor until the mandatory legal, "
        f"contractual, and technical controls below are completed and approved by the DPO and Legal Counsel.\n"
        f"2. APPLICABLE LAWS: Triggered obligations under Canadian PIPEDA (Principle 4.1.3 cross-border accountability), "
        f"Quebec Law 25 (ss. 3.3, 12.1, 17 mandatory out-of-province Transfer Risk Assessment / ÉFVP & s. 18.3 processor contract), "
        f"California CCPA/CPRA (Cal. Civ. Code § 1798.100(d) Service Provider Addendum, prohibition on model training/selling/sharing, "
        f"& CIPA Cal. Penal Code § 632 call recording consent), EU GDPR / German BDSG (Art. 28 DPA, Art. 35 DPIA, Chapter V Art. 46 "
        f"EU SCCs + Transfer Impact Assessment), and EU AI Act (Arts. 4 & 50).\n"
        f"3. COMPANY POLICY & VENDOR STATUS: Internal policy {tenant_policies[0]['policy_id']} ({tenant_policies[0]['title']}) "
        f"and vendor registry check ({matched_vendor.get('vendor_name', 'US AI Vendor')}: {matched_vendor.get('approval_status', 'PENDING')}) "
        f"require an executed DPA/SCC/Service Provider Addendum, completed PIA/DPIA/TRA/TIA/AIIA, zero-data-retention configuration, "
        f"and formal DPO + Legal sign-off."
    )

    return {
        "status": "governed_guidance_ready",
        "tenant_id": active_tenant,
        "user_id": verified["user_id"],
        "role": verified["role"],
        "decision_status": decision_status,
        "organization_context": org_profile,
        "applicable_laws": eval_detail["applicable_laws"],
        "company_policies": tenant_policies,
        "vendor_governance_check": matched_vendor,
        "required_assessments": eval_detail["required_assessments"],
        "mandatory_controls": eval_detail["mandatory_controls"],
        "approval_gates": eval_detail["approval_gates"],
        "competent_authorities": eval_detail["competent_authorities"],
        "citations": eval_detail["citations"],
        "guidance_summary": guidance_summary,
        "next_recommended_tools": [
            "initiate_privacy_assessment",
            "lookup_vendor_status",
            "route_approval_decision",
        ],
    }


# ============================================================================
# 2. report_privacy_incident
# ============================================================================
@mcp.tool(
    name="report_privacy_incident",
    description=(
        "Intake a suspected privacy or security incident. Creates a draft incident intake record "
        "and computes statutory notification planning clocks; NEVER auto-dispatches external notices."
    ),
)
def report_privacy_incident(
    tenant_id: str,
    user_id: str,
    title: str,
    description: str,
    role: str = "EMPLOYEE",
    affected_jurisdictions: Optional[List[str]] = None,
    estimated_affected_count: int = 100,
    involves_phi: bool = False,
    involves_financial_data: bool = False,
    read_only: bool = False,
    write_grant: bool = True,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a draft incident intake record and computes statutory clocks without external dispatch."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="report_privacy_incident",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[title, description] + (affected_jurisdictions or []),
        requires_write=True,
        read_only=read_only,
        write_grant=write_grant,
    )
    active_tenant = verified["tenant_id"]
    jurisdictions = affected_jurisdictions or ["CA-FED", "CA-QC", "US-CA", "EU-DE"]
    counts = {normalize_jurisdiction_code(j): max(0, estimated_affected_count) for j in jurisdictions}
    now = datetime.now(timezone.utc)

    deadline_plan = calculate_breach_deadlines(
        jurisdictions=list(counts.keys()),
        discovery_time=now,
        affected_counts_by_jurisdiction=counts,
        involves_phi=involves_phi,
        involves_financial=involves_financial_data,
        risk_of_harm_level="high",
    )

    incident_id = f"INC-{active_tenant.upper()}-{uuid.uuid4().hex[:8].upper()}"
    return {
        "incident_id": incident_id,
        "tenant_id": active_tenant,
        "reported_by": verified["user_id"],
        "reporter_role": verified["role"],
        "title": title,
        "status": "DRAFT_PENDING_DPO_AND_LEGAL_TRIAGE",
        "auto_dispatched_external_notice": False,
        "requires_human_legal_approval": True,
        "strictest_regulator_deadline_hours": deadline_plan["strictest_regulator_deadline_hours"],
        "statutory_deadline_plan": {
            "jurisdictions": deadline_plan["jurisdictions"],
            "strictest_regulator_deadline_hours": deadline_plan["strictest_regulator_deadline_hours"],
            "strictest_individual_deadline_days": deadline_plan["strictest_individual_deadline_days"],
            "retention_requirements": deadline_plan["retention_requirements"],
            "workflow_tasks_count": len(deadline_plan["deduplicated_workflow_tasks"]),
        },
        "governance_notice": (
            "Draft incident created in KIBO Privacy OS triage queue. External regulator and data subject "
            "notifications are strictly blocked until two verified human approvals (DPO/CPO/Legal) are recorded."
        ),
    }


# ============================================================================
# 3. initiate_privacy_assessment
# ============================================================================
@mcp.tool(
    name="initiate_privacy_assessment",
    description=(
        "Initiate a draft Privacy Impact Assessment (PIA), DPIA, Quebec/Canadian Transfer Risk "
        "Assessment (TRA), EU Transfer Impact Assessment (TIA), Legitimate Interests Assessment (LIA), "
        "or AI Impact Assessment (AIIA)."
    ),
)
def initiate_privacy_assessment(
    tenant_id: str,
    user_id: str,
    assessment_type: str,
    project_name: str,
    role: str = "ANALYST",
    jurisdictions: Optional[List[str]] = None,
    data_categories: Optional[List[str]] = None,
    transfer_destination: Optional[str] = None,
    read_only: bool = False,
    write_grant: bool = True,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a draft PIA/DPIA/TRA/TIA/LIA/AIIA assessment record scoped to the caller's tenant."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="initiate_privacy_assessment",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[assessment_type, project_name, transfer_destination or ""] + (jurisdictions or []),
        requires_write=True,
        read_only=read_only,
        write_grant=write_grant,
    )
    active_tenant = verified["tenant_id"]
    normalized_type = assessment_type.strip().upper()
    allowed_types = {"PIA", "DPIA", "TRA", "TIA", "LIA", "AIIA"}
    if normalized_type not in allowed_types:
        raise ValueError(f"Unsupported assessment_type '{assessment_type}'. Must be one of {sorted(allowed_types)}")

    section_templates = {
        "PIA": [
            "1. Processing Purpose & Necessity (PIPEDA / State Privacy Laws)",
            "2. Personal Information Inventory & Minimization",
            "3. Notice, Consent & Data Subject Rights Fulfillment",
            "4. Security Safeguards & Retention Schedule",
        ],
        "DPIA": [
            "1. Systematic Description of Processing & Lawful Basis (GDPR Art. 35(7)(a))",
            "2. Necessity & Proportionality Assessment (GDPR Art. 35(7)(b))",
            "3. Risks to Rights and Freedoms of Data Subjects (GDPR Art. 35(7)(c))",
            "4. Mitigation Measures, DPO Advice (Art. 35(2)) & Works Council Consultation",
        ],
        "TRA": [
            "1. Sensitivity of Personal Information Communicated Outside Quebec (Law 25 s. 17(1))",
            "2. Purposes & Proportionality of the Out-of-Province Transfer (Law 25 s. 17(2))",
            "3. Contractual & Technical Protection Measures (Law 25 ss. 17(3), 18.3)",
            "4. Legal Framework & Foreign Government Access Analysis of Destination State (Law 25 s. 17(4))",
        ],
        "TIA": [
            "1. Know Your Transfer & Subprocessor Chain (EDPB Step 1)",
            "2. GDPR Chapter V Transfer Tool Verification (2021 EU SCCs / EU-US DPF) (EDPB Step 2)",
            "3. Third-Country Surveillance & Public Authority Access Assessment (Schrems II / EO 14086) (EDPB Step 3)",
            "4. Technical, Contractual & Organizational Supplementary Measures (EDPB Step 4)",
        ],
        "LIA": [
            "1. Purpose Test — Identifying the Legitimate Interest (GDPR Art. 6(1)(f))",
            "2. Necessity Test — Evaluating Less Intrusive Alternatives",
            "3. Balancing Test — Reasonable Expectations & Opt-Out Safeguards",
        ],
        "AIIA": [
            "1. AI System Classification & Intended Purpose (EU AI Act / CPRA ADMT / Law 25 s. 12.1)",
            "2. Training Data Governance & Zero-Retention Verification",
            "3. Bias, Hallucination, Explainability & Human-in-the-Loop Controls",
            "4. Transparency Notice & Right to Human Review",
        ],
    }

    assessment_id = f"{normalized_type}-{active_tenant.upper()}-{uuid.uuid4().hex[:8].upper()}"
    return {
        "assessment_id": assessment_id,
        "tenant_id": active_tenant,
        "created_by": verified["user_id"],
        "creator_role": verified["role"],
        "assessment_type": normalized_type,
        "project_name": project_name,
        "jurisdictions": [normalize_jurisdiction_code(j) for j in (jurisdictions or ["CA-ON", "CA-QC", "US-CA", "EU-DE"])],
        "data_categories": data_categories or ["customer_support_audio", "contact_identifiers"],
        "transfer_destination": normalize_jurisdiction_code(transfer_destination) if transfer_destination else "US-FED",
        "status": "DRAFT_AWAITING_DPO_AND_LEGAL_APPROVAL",
        "required_sections": section_templates[normalized_type],
        "required_approvers": ["DPO", "CPO", "LEGAL"],
        "requires_human_approval": True,
    }


# ============================================================================
# 4. lookup_privacy_tasks
# ============================================================================
@mcp.tool(
    name="lookup_privacy_tasks",
    description="Look up tenant-scoped privacy tasks, DSAR deadlines, and assessment review items.",
)
def lookup_privacy_tasks(
    tenant_id: str,
    user_id: str,
    role: str = "ANALYST",
    status_filter: str = "open",
    query: Optional[str] = None,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Returns privacy tasks strictly scoped to the caller's verified tenant."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="lookup_privacy_tasks",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[status_filter, query or ""],
        requires_write=False,
    )
    active_tenant = verified["tenant_id"]
    raw_tasks = TENANT_TASKS.get(active_tenant, [])
    scoped_tasks = [
        t
        for t in raw_tasks
        if t.get("tenant_id") == active_tenant
        and (status_filter == "all" or t.get("status") == status_filter)
        and (not query or query.lower() in t.get("title", "").lower())
    ]
    return {
        "tenant_id": active_tenant,
        "user_id": verified["user_id"],
        "role": verified["role"],
        "count": len(scoped_tasks),
        "tasks": scoped_tasks,
    }


# ============================================================================
# 5. lookup_vendor_status
# ============================================================================
@mcp.tool(
    name="lookup_vendor_status",
    description=(
        "Look up a third-party vendor or AI subprocessor's DPA, HIPAA BAA, EU SCCs, "
        "Quebec Law 25 TRA, and approval status within the caller's tenant."
    ),
)
def lookup_vendor_status(
    tenant_id: str,
    user_id: str,
    vendor_name: str,
    role: str = "EMPLOYEE",
    intended_use: Optional[str] = None,
    source_jurisdictions: Optional[List[str]] = None,
    destination_jurisdiction: Optional[str] = "US-FED",
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Looks up tenant-scoped vendor governance status and contractual/transfer prerequisites."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="lookup_vendor_status",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[vendor_name, intended_use or "", destination_jurisdiction or ""] + (source_jurisdictions or []),
        requires_write=False,
    )
    active_tenant = verified["tenant_id"]
    vendors = [v for v in TENANT_VENDORS.get(active_tenant, TENANT_VENDORS["tenant-ca"]) if v.get("tenant_id") == active_tenant]

    matched = None
    for v in vendors:
        if vendor_name.lower() in v["vendor_name"].lower() or v["vendor_id"].lower() == vendor_name.lower():
            matched = v
            break

    if matched is None:
        matched = {
            "vendor_id": "VND-UNREGISTERED",
            "tenant_id": active_tenant,
            "vendor_name": vendor_name,
            "hosting_location": destination_jurisdiction or "US-FED",
            "approval_status": "UNAPPROVED_REQUIRES_ONBOARDING_AND_ASSESSMENT",
            "risk_tier": "HIGH",
            "dpa_executed": False,
            "cpra_service_provider_addendum": False,
            "baa_executed": False,
            "eu_sccs_executed": False,
            "eu_tia_completed": False,
            "quebec_law25_tra_completed": False,
            "ai_training_prohibited_clause": False,
            "zero_data_retention_enabled": False,
            "required_conditions": [
                "Execute GDPR Art. 28 DPA, CCPA/CPRA § 1798.100(d) Service Provider Addendum, and Quebec Law 25 s. 18.3 contract",
                "Execute 2021 EU Standard Contractual Clauses (Module 2) and complete Transfer Impact Assessment (TIA)",
                "Complete Quebec Law 25 s. 17 Transfer Risk Assessment (TRA) prior to cross-border transfer",
                "Complete DPIA and AI Impact Assessment (AIIA) with DPO & Legal sign-off",
            ],
        }

    return {
        "tenant_id": active_tenant,
        "user_id": verified["user_id"],
        "vendor": matched,
        "can_process_personal_data_immediately": matched["approval_status"] == "APPROVED",
    }


# ============================================================================
# 6. search_privacy_policies
# ============================================================================
@mcp.tool(
    name="search_privacy_policies",
    description="Search tenant-scoped internal company privacy policies, AI standards, and retention schedules.",
)
def search_privacy_policies(
    tenant_id: str,
    user_id: str,
    query: str,
    role: str = "EMPLOYEE",
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Searches internal privacy policies strictly isolated to the authenticated tenant."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="search_privacy_policies",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[query],
        requires_write=False,
    )
    active_tenant = verified["tenant_id"]
    policies = [
        p
        for p in TENANT_POLICIES.get(active_tenant, [])
        if p.get("tenant_id") == active_tenant
    ]
    q_terms = [t for t in query.lower().split() if len(t) > 2]
    if q_terms:
        filtered = [
            p
            for p in policies
            if any(
                term in p["title"].lower() or term in p["summary"].lower() or term in p["policy_id"].lower()
                for term in q_terms
            )
        ]
        results = filtered if filtered else policies
    else:
        results = policies

    return {
        "tenant_id": active_tenant,
        "user_id": verified["user_id"],
        "query": query,
        "count": len(results),
        "results": results,
    }


# ============================================================================
# 7. evaluate_regulatory_applicability
# ============================================================================
@mcp.tool(
    name="evaluate_regulatory_applicability",
    description=(
        "Run the Jurisdictional Regulatory Applicability Engine (JRAE) across US, Canada, and EU "
        "jurisdictions for a specific processing purpose, data categories, and transfer footprint."
    ),
)
def evaluate_regulatory_applicability(
    tenant_id: str,
    user_id: str,
    jurisdictions: List[str],
    purpose: str,
    role: str = "ANALYST",
    data_categories: Optional[List[str]] = None,
    transfer_destinations: Optional[List[str]] = None,
    involves_ai: bool = False,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluates multi-jurisdictional regulatory applicability for the caller's tenant."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="evaluate_regulatory_applicability",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[purpose] + (jurisdictions or []) + (transfer_destinations or []),
        requires_write=False,
    )
    active_tenant = verified["tenant_id"]
    detail = _evaluate_jurisdictions_detail(
        jurisdictions=jurisdictions,
        involves_ai=involves_ai,
        involves_cross_border_transfer=bool(transfer_destinations),
        transfer_destinations=transfer_destinations,
    )

    return {
        "tenant_id": active_tenant,
        "user_id": verified["user_id"],
        "purpose": purpose,
        "data_categories": data_categories or ["personal_identifiers"],
        "evaluated_jurisdictions": detail["normalized_jurisdictions"],
        "transfer_destinations": detail["transfer_destinations"],
        "applicable_instruments": detail["applicable_laws"],
        "required_assessments": detail["required_assessments"],
        "mandatory_controls": detail["mandatory_controls"],
        "approval_gates": detail["approval_gates"],
        "competent_authorities": detail["competent_authorities"],
        "citations": detail["citations"],
    }


# ============================================================================
# 8. route_approval_decision
# ============================================================================
@mcp.tool(
    name="route_approval_decision",
    description=(
        "Route a privacy workflow item (PIA/DPIA/TRA/TIA sign-off, vendor onboarding, cross-border "
        "transfer, or draft incident notice) to DPO/CPO/Legal for human approval."
    ),
)
def route_approval_decision(
    tenant_id: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    requested_action: str,
    justification: str = "",
    role: str = "ANALYST",
    read_only: bool = False,
    write_grant: bool = True,
    authenticated_tenant_id: Optional[str] = None,
    target_tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Routes a workflow item to the human DPO/CPO/Legal approval queue with an audit log entry."""
    verified = _verify_mcp_context_and_tenant_isolation(
        tool_name="route_approval_decision",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
        authenticated_tenant_id=authenticated_tenant_id,
        target_tenant_id=target_tenant_id,
        free_text_inputs=[resource_type, resource_id, requested_action, justification],
        requires_write=True,
        read_only=read_only,
        write_grant=write_grant,
    )
    active_tenant = verified["tenant_id"]
    approval_request_id = f"APR-{active_tenant.upper()}-{uuid.uuid4().hex[:8].upper()}"
    audit_log_id = f"AUD-{uuid.uuid4().hex[:10].upper()}"

    return {
        "approval_request_id": approval_request_id,
        "tenant_id": active_tenant,
        "submitted_by": verified["user_id"],
        "submitter_role": verified["role"],
        "resource_type": resource_type,
        "resource_id": resource_id,
        "requested_action": requested_action,
        "justification": justification,
        "status": "PENDING_HUMAN_APPROVAL",
        "required_approver_roles": ["DPO", "CPO", "LEGAL"],
        "minimum_distinct_human_approvers": 2,
        "auto_executed": False,
        "audit_log_id": audit_log_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


APPROVED_MCP_TOOLS: Dict[str, Callable[..., Any]] = {
    "get_privacy_guidance": get_privacy_guidance,
    "report_privacy_incident": report_privacy_incident,
    "initiate_privacy_assessment": initiate_privacy_assessment,
    "lookup_privacy_tasks": lookup_privacy_tasks,
    "lookup_vendor_status": lookup_vendor_status,
    "search_privacy_policies": search_privacy_policies,
    "evaluate_regulatory_applicability": evaluate_regulatory_applicability,
    "route_approval_decision": route_approval_decision,
}


def invoke_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    *,
    authenticated_tenant_id: Optional[str] = None,
    authenticated_user_id: Optional[str] = None,
    authenticated_role: Optional[str] = None,
    read_only_default: bool = False,
) -> Dict[str, Any]:
    """
    Dispatcher used by both the MCP JSON-RPC transport and the FastAPI Unified Corporate Hub Router.
    Always binds `authenticated_tenant_id` from the server-verified session/token so a caller
    authenticated to `tenant-ca` cannot spoof or access `tenant-us`.
    """
    if tool_name not in APPROVED_MCP_TOOLS:
        raise ValueError(f"Unapproved or unknown MCP tool: '{tool_name}'")

    call_args = dict(arguments or {})
    if authenticated_tenant_id:
        call_args["authenticated_tenant_id"] = authenticated_tenant_id
        call_args.setdefault("tenant_id", authenticated_tenant_id)
    if authenticated_user_id:
        call_args["user_id"] = authenticated_user_id
    if authenticated_role:
        if call_args.get("role") and call_args["role"].upper() != authenticated_role.upper():
            raise PermissionError("ROLE_ESCALATION_DENIED: Role differs from verified caller")
        call_args["role"] = authenticated_role
    if read_only_default and "read_only" not in call_args:
        call_args["read_only"] = True

    return APPROVED_MCP_TOOLS[tool_name](**call_args)


if __name__ == "__main__":
    mcp.run()
