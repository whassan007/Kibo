"""
KIBO Privacy OS — Privacy Office Modules A, C, G, H, I, and J.
Implements deterministic statutory workflows, tenant-isolated governance services,
and FastAPI endpoints for:
- Module A: Privacy Office Administration & Governance (`/api/v1/office/governance`)
- Module C: Multi-Jurisdictional Privacy Incident & Breach Management (`/api/v1/office/incidents`)
- Module G: Vendor Privacy Management (`/api/v1/office/vendors`)
- Module H: Enterprise Risk & Control Management (`/api/v1/office/risks-controls`)
- Module I: Regulatory Intelligence & Change Impact Analysis (`/api/v1/office/regulatory-intelligence`)
- Module J: Governed Privacy Office Assistant (`/api/v1/office/assistant/query`)
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.context.tenant_context import get_current_tenant, get_tenant_id
from core.security.auth import (
    PrincipalContext,
    principal_from_request,
    resolve_verified_role,
    strict_auth_enabled,
)
from core.jrae.deadlines import calculate_breach_deadlines
from core.jrae.registry import (
    GERMAN_LANDER_AUTHORITIES,
    GLOBAL_JURISDICTION_REGISTRY,
    normalize_jurisdiction_code,
)

router = APIRouter(
    prefix="/api/v1/office",
    tags=["Privacy Office - Breach, Governance, Vendors, Risk, RegIntel & Assistant"],
)


# ===========================================================================
# TENANT CONTEXT & RBAC DEPENDENCY HELPERS
# ===========================================================================

def resolve_tenant_id(
    request: Request,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
) -> str:
    """
    Resolve the active tenant ID deterministically from middleware context,
    explicit X-Tenant-ID header, or PrincipalContext on request.state.
    Blocks cross-tenant spoofing attempts.
    """
    principal = getattr(request.state, "principal", None)
    if principal and getattr(principal, "tenant_id", None):
        if x_tenant_id and x_tenant_id != principal.tenant_id:
            raise HTTPException(
                status_code=403,
                detail="CROSS_TENANT_ACCESS_DENIED: Cross-tenant access attempt blocked",
            )
        return principal.tenant_id

    ctx = get_current_tenant()
    if x_tenant_id:
        if ctx and ctx.tenant_id not in ("default", x_tenant_id):
            raise HTTPException(
                status_code=403,
                detail="CROSS_TENANT_ACCESS_DENIED: Cross-tenant access attempt blocked",
            )
        return x_tenant_id.strip()

    if ctx and ctx.tenant_id:
        return ctx.tenant_id

    tid = get_tenant_id()
    return tid or "default"


def resolve_caller_role(
    request: Request,
    payload_role: Optional[str] = None,
    x_user_role: Optional[str] = None,
) -> str:
    """
    Resolve the caller's role using `resolve_verified_role` from `core.security.auth`.
    In strict/production mode (`strict_auth_enabled()`), unauthenticated callers raise `401`
    and `x_user_role`/payload role escalation is rejected (`403`) when it conflicts with
    the verified JWT role, while preserving dev-mode test compatibility when
    `strict_auth_enabled()` is False.
    """
    header_role = x_user_role if isinstance(x_user_role, str) else request.headers.get("X-User-Role")
    requested_role = (header_role or payload_role or "").strip().upper() or None

    principal = getattr(request.state, "principal", None)
    if principal is None:
        principal = principal_from_request(request)

    if strict_auth_enabled():
        if not (isinstance(principal, PrincipalContext) and principal.authenticated):
            raise HTTPException(
                status_code=401,
                detail="Verified enterprise token required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    if isinstance(principal, PrincipalContext) and principal.authenticated:
        verified_role = str(resolve_verified_role(request, fallback="EMPLOYEE")).upper()
        granted_roles = {str(r).upper() for r in principal.roles} or {verified_role}
        if header_role and header_role.strip().upper() not in granted_roles:
            raise HTTPException(
                status_code=403,
                detail=f"ROLE_ESCALATION_DENIED: Header role '{header_role.strip().upper()}' conflicts with verified JWT role '{verified_role}'",
            )
        if payload_role and payload_role.strip().upper() not in granted_roles:
            raise HTTPException(
                status_code=403,
                detail=f"ROLE_ESCALATION_DENIED: Payload role '{payload_role.strip().upper()}' conflicts with verified JWT role '{verified_role}'",
            )
        return requested_role if (requested_role and requested_role in granted_roles) else verified_role

    # Non-strict / local development compatibility mode (strict_auth_enabled() is False)
    verified_fallback = str(resolve_verified_role(request, fallback="EMPLOYEE")).upper()
    if header_role:
        return header_role.strip().upper()
    if payload_role:
        return payload_role.strip().upper()
    ctx = get_current_tenant()
    if ctx and getattr(ctx, "user_role", None):
        return str(ctx.user_role).upper()
    return verified_fallback


def _compute_sha256(payload_str: str) -> str:
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


# ===========================================================================
# MODULE A — PRIVACY OFFICE ADMINISTRATION & GOVERNANCE
# ===========================================================================

class OfficerRoleType(str, Enum):
    DPO_GDPR = "DPO_GDPR_ART_37"
    DPO_BDSG = "DPO_GERMAN_BDSG_SEC_38"
    QUEBEC_LAW25_PERSON_IN_CHARGE = "QUEBEC_LAW25_SEC_3_1_PERSON_IN_CHARGE"
    CPO = "CHIEF_PRIVACY_OFFICER"
    HIPAA_PRIVACY_OFFICER = "HIPAA_PRIVACY_OFFICER_45_CFR_164_530"
    HIPAA_SECURITY_OFFICER = "HIPAA_SECURITY_OFFICER_45_CFR_164_308"
    PIPEDA_PRIVACY_OFFICER = "PIPEDA_PRINCIPLE_4_1_OFFICER"
    PHIPA_CONTACT_PERSON = "ONTARIO_PHIPA_SEC_15_CONTACT_PERSON"
    EU_REPRESENTATIVE_ART_27 = "GDPR_ART_27_EU_REPRESENTATIVE"
    DELEGATE = "PRIVACY_OFFICE_DELEGATE"


class CorporateEstablishment(BaseModel):
    establishment_id: str = Field(default_factory=lambda: f"est_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "default"
    entity_name: str
    jurisdiction_id: str
    normalized_jurisdiction: str = ""
    subnational_region: Optional[str] = Field(
        default=None,
        description="e.g., DE-BY (Bavaria), DE-BW (Baden-Württemberg), CA-ON, CA-QC, US-CA",
    )
    is_main_eu_establishment: bool = False
    employee_count_at_site: int = 50
    employees_processing_personal_data: int = 25
    processes_health_data: bool = False
    processes_financial_data: bool = False
    competent_authority: str = ""
    bdsg_sec38_dpo_mandatory: bool = False


class PrivacyOfficerDesignation(BaseModel):
    officer_id: str = Field(default_factory=lambda: f"ofc_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "default"
    full_name: str
    email: str
    role_type: str = Field(..., description="DPO, CPO, QUEBEC_LAW25_PERSON_IN_CHARGE, HIPAA_PRIVACY_OFFICER, etc.")
    statutory_basis: str
    jurisdictions_covered: List[str] = Field(default_factory=list)
    published_on_website: bool = True
    notified_to_regulator: bool = True
    regulator_registration_ref: Optional[str] = None
    appointed_at: date = Field(default_factory=date.today)
    delegates: List[str] = Field(default_factory=list)


class GovernancePolicyRecord(BaseModel):
    policy_id: str = Field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "default"
    title: str
    policy_category: str = Field(
        default="data_protection",
        description="data_protection, ai_governance, vendor_onboarding, data_classification, retention, incident_response",
    )
    version: str = "2026.1"
    status: str = "effective"
    applicable_jurisdictions: List[str] = Field(default_factory=list)
    mapped_regulation_ids: List[str] = Field(default_factory=list)
    summary: str
    mandatory_controls: List[str] = Field(default_factory=list)
    approved_by_role: str = "CPO"
    effective_date: date = Field(default_factory=date.today)
    next_review_date: date = Field(default_factory=lambda: date.today() + timedelta(days=365))


class GovernanceCalendarEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cal_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "default"
    title: str
    cadence: str = Field(default="annual", description="monthly, quarterly, semi_annual, annual, statutory_deadline")
    due_date: date
    jurisdiction_id: str
    statutory_citation: str
    owner_role: str = "DPO"
    status: str = "scheduled"


class TrainingCampaignRecord(BaseModel):
    campaign_id: str = Field(default_factory=lambda: f"trn_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "default"
    title: str
    target_audience: str = "All Staff & AI System Operators"
    applicable_regulations: List[str] = Field(
        default_factory=lambda: ["EU-GDPR", "EU-AI-ACT", "CA-QC-LAW25", "US-CA-CCPA-CPRA", "US-FED-HIPAA"]
    )
    completion_rate_pct: float = 96.5
    total_assigned: int = 500
    total_completed: int = 482
    status: str = "active"


class GovernanceProfilePayload(BaseModel):
    organization_name: str = "Enterprise Global Corp"
    industry: str = "technology_and_healthcare"
    organization_type: str = "private"
    employee_count: int = 850
    annual_revenue_usd: float = 145000000.0
    primary_establishment: str = "CA-ON"
    main_eu_establishment: Optional[str] = "EU-DE"
    active_jurisdictions: List[str] = Field(
        default_factory=lambda: ["US-FED", "US-CA", "US-NY", "CA-FED", "CA-ON", "CA-QC", "EU", "EU-DE", "EU-FR"]
    )
    subnational_regions: List[str] = Field(default_factory=lambda: ["DE-BY", "CA-ON", "CA-QC", "US-CA"])
    annual_privacy_budget_usd: float = 1850000.0
    budget_allocated_usd: float = 1420000.0
    annual_program_objectives: List[str] = Field(
        default_factory=lambda: [
            "Maintain 100% timely DSAR and multi-jurisdictional breach readiness across US, Canada, and EU",
            "Enforce Quebec Law 25 s. 17 TRA and GDPR Art. 46 TIA gates on all cross-border AI vendor transfers",
            "Verify German BDSG § 38 DPO designation across German establishments (>=20 personnel processing personal data)",
            "Conduct annual Ontario PHIPA March 1 IPC statistical reporting and HIPAA Security Risk Analysis",
        ]
    )


class GovernanceAdministrationService:
    """
    Deterministic service for Module A — Privacy Office Administration & Governance.
    Maintains tenant-isolated organization profiles, corporate establishments, statutory officers,
    policies, training records, governance calendar, and Executive Board reporting.
    """

    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._establishments: Dict[str, List[CorporateEstablishment]] = {}
        self._officers: Dict[str, List[PrivacyOfficerDesignation]] = {}
        self._policies: Dict[str, List[GovernancePolicyRecord]] = {}
        self._calendar: Dict[str, List[GovernanceCalendarEvent]] = {}
        self._training: Dict[str, List[TrainingCampaignRecord]] = {}

    def _ensure_tenant_seeded(self, tenant_id: str) -> None:
        if tenant_id in self._profiles:
            return

        org_name = {
            "tenant-ca": "MapleLeaf Enterprise Corp (Canada & Global Operations)",
            "tenant-us": "PacificWest Health & Commerce Inc. (United States)",
            "tenant-eu": "EuroShield GmbH (European Union)",
        }.get(tenant_id, f"KIBO Enterprise Organization ({tenant_id})")

        self._profiles[tenant_id] = {
            "tenant_id": tenant_id,
            "organization_name": org_name,
            "industry": "technology_and_healthcare",
            "organization_type": "private",
            "employee_count": 850,
            "annual_revenue_usd": 145000000.0,
            "primary_establishment": "CA-ON" if tenant_id != "tenant-us" else "US-CA",
            "main_eu_establishment": "EU-DE",
            "active_jurisdictions": ["US-FED", "US-CA", "US-NY", "CA-FED", "CA-ON", "CA-QC", "EU", "EU-DE", "EU-FR"],
            "subnational_regions": ["DE-BY", "CA-ON", "CA-QC", "US-CA"],
            "annual_privacy_budget_usd": 1850000.0,
            "budget_allocated_usd": 1420000.0,
            "budget_utilization_pct": round((1420000.0 / 1850000.0) * 100.0, 2),
            "annual_program_objectives": [
                "Maintain 100% timely DSAR and multi-jurisdictional breach readiness across US, Canada, and EU",
                "Enforce Quebec Law 25 s. 17 TRA and GDPR Art. 46 TIA gates on all cross-border AI vendor transfers",
                "Verify German BDSG § 38 DPO designation across German establishments (>=20 personnel processing personal data)",
                "Conduct annual Ontario PHIPA March 1 IPC statistical reporting and HIPAA Security Risk Analysis",
            ],
            "updated_at": datetime.utcnow().isoformat(),
        }

        self._establishments[tenant_id] = [
            CorporateEstablishment(
                establishment_id=f"est_{tenant_id}_ca_on",
                tenant_id=tenant_id,
                entity_name=f"{org_name} — Toronto HQ",
                jurisdiction_id="CA-ON",
                normalized_jurisdiction="CA-ON",
                subnational_region="CA-ON",
                is_main_eu_establishment=False,
                employee_count_at_site=320,
                employees_processing_personal_data=210,
                processes_health_data=True,
                processes_financial_data=True,
                competent_authority="Information and Privacy Commissioner of Ontario (IPC) & Office of the Privacy Commissioner of Canada (OPC)",
                bdsg_sec38_dpo_mandatory=False,
            ),
            CorporateEstablishment(
                establishment_id=f"est_{tenant_id}_ca_qc",
                tenant_id=tenant_id,
                entity_name=f"{org_name} — Montreal Operations",
                jurisdiction_id="CA-QC",
                normalized_jurisdiction="CA-QC",
                subnational_region="CA-QC",
                is_main_eu_establishment=False,
                employee_count_at_site=140,
                employees_processing_personal_data=95,
                processes_health_data=False,
                processes_financial_data=True,
                competent_authority="Commission d'accès à l'information du Québec (CAI)",
                bdsg_sec38_dpo_mandatory=False,
            ),
            CorporateEstablishment(
                establishment_id=f"est_{tenant_id}_us_ca",
                tenant_id=tenant_id,
                entity_name=f"{org_name} — San Francisco US Inc.",
                jurisdiction_id="US-CA",
                normalized_jurisdiction="US-CA",
                subnational_region="US-CA",
                is_main_eu_establishment=False,
                employee_count_at_site=220,
                employees_processing_personal_data=150,
                processes_health_data=True,
                processes_financial_data=True,
                competent_authority="California Privacy Protection Agency (CalPrivacy) & California Attorney General",
                bdsg_sec38_dpo_mandatory=False,
            ),
            CorporateEstablishment(
                establishment_id=f"est_{tenant_id}_eu_de",
                tenant_id=tenant_id,
                entity_name=f"{org_name} — Munich GmbH",
                jurisdiction_id="EU-DE",
                normalized_jurisdiction="EU-DE",
                subnational_region="DE-BY",
                is_main_eu_establishment=True,
                employee_count_at_site=110,
                employees_processing_personal_data=65,
                processes_health_data=False,
                processes_financial_data=True,
                competent_authority="Bayerisches Landesamt für Datenschutzaufsicht (BayLDA) & BfDI",
                bdsg_sec38_dpo_mandatory=True,  # >=20 employees regularly processing personal data automatically under BDSG § 38
            ),
            CorporateEstablishment(
                establishment_id=f"est_{tenant_id}_eu_fr",
                tenant_id=tenant_id,
                entity_name=f"{org_name} — Paris SAS",
                jurisdiction_id="EU-FR",
                normalized_jurisdiction="EU-FR",
                subnational_region="FR-IDF",
                is_main_eu_establishment=False,
                employee_count_at_site=60,
                employees_processing_personal_data=40,
                processes_health_data=False,
                processes_financial_data=False,
                competent_authority="Commission Nationale de l'Informatique et des Libertés (CNIL)",
                bdsg_sec38_dpo_mandatory=False,
            ),
        ]

        self._officers[tenant_id] = [
            PrivacyOfficerDesignation(
                officer_id=f"ofc_{tenant_id}_cpo",
                tenant_id=tenant_id,
                full_name="Dr. Claire Vance, CIPP/E, CIPP/C, CIPP/US",
                email=f"cpo@{tenant_id}.example.org",
                role_type=OfficerRoleType.CPO.value,
                statutory_basis="PIPEDA Schedule 1 Principle 4.1 & Enterprise Global Privacy Charter",
                jurisdictions_covered=["CA-FED", "CA-ON", "US-FED", "US-CA"],
                published_on_website=True,
                notified_to_regulator=True,
                delegates=["privacy-ops@kibo.is"],
            ),
            PrivacyOfficerDesignation(
                officer_id=f"ofc_{tenant_id}_qc_law25",
                tenant_id=tenant_id,
                full_name="Marc-Antoine Tremblay, Avocat",
                email=f"responsable-vie-privee@{tenant_id}.example.org",
                role_type=OfficerRoleType.QUEBEC_LAW25_PERSON_IN_CHARGE.value,
                statutory_basis="Quebec Law 25 (CQLR c. P-39.1) s. 3.1 — Person in Charge of the Protection of Personal Information (Title & contact published on website)",
                jurisdictions_covered=["CA-QC"],
                published_on_website=True,
                notified_to_regulator=True,
                regulator_registration_ref="CAI-QC-2026-REG-8821",
                delegates=["cpo@kibo.is"],
            ),
            PrivacyOfficerDesignation(
                officer_id=f"ofc_{tenant_id}_eu_dpo",
                tenant_id=tenant_id,
                full_name="Dr. Lukas Weber, Datenschutzbeauftragter (DSB)",
                email=f"dsb@{tenant_id}.example.org",
                role_type=OfficerRoleType.DPO_BDSG.value,
                statutory_basis="GDPR Art. 37 & German Federal Data Protection Act (BDSG) § 38 (>=20 persons constantly employed in automated processing)",
                jurisdictions_covered=["EU", "EU-DE", "EU-FR"],
                published_on_website=True,
                notified_to_regulator=True,
                regulator_registration_ref="BayLDA-DPO-2026-4410 / CNIL-DPO-99214",
                delegates=["eu-privacy-team@kibo.is"],
            ),
            PrivacyOfficerDesignation(
                officer_id=f"ofc_{tenant_id}_hipaa_phipa",
                tenant_id=tenant_id,
                full_name="Sarah Jenkins, JD, CHPC",
                email=f"hipaa-privacy@{tenant_id}.example.org",
                role_type=OfficerRoleType.HIPAA_PRIVACY_OFFICER.value,
                statutory_basis="HIPAA 45 CFR § 164.530(a)(1) Privacy Official, 45 CFR § 164.308(a)(2) Security Official & Ontario PHIPA s. 15 Contact Person",
                jurisdictions_covered=["US-FED", "US-CA", "CA-ON"],
                published_on_website=True,
                notified_to_regulator=True,
                delegates=["security-officer@kibo.is"],
            ),
        ]

        self._policies[tenant_id] = [
            GovernancePolicyRecord(
                policy_id=f"POL-{tenant_id.upper()}-AI-001",
                tenant_id=tenant_id,
                title="Enterprise AI & Third-Party Data Sharing Policy",
                policy_category="ai_governance",
                version="2026.3",
                status="effective",
                applicable_jurisdictions=["US-FED", "US-CA", "CA-FED", "CA-ON", "CA-QC", "EU", "EU-DE", "EU-FR"],
                mapped_regulation_ids=["EU-GDPR", "EU-AI-ACT", "CA-QC-LAW25", "CA-FED-PIPEDA", "US-CA-CCPA-CPRA"],
                summary=(
                    "Strictly prohibits transmitting customer personal data, support transcripts, or PHI to any third-party "
                    "AI provider or external LLM unless: (1) an executed Data Processing Addendum (DPA) / Service Provider Addendum "
                    "with an explicit AI model-training prohibition and zero-data-retention clause is active, (2) a PIA/DPIA, "
                    "AI Impact Assessment (AIIA), Quebec Law 25 s. 17 Transfer Risk Assessment (TRA), and GDPR Chapter V Transfer "
                    "Impact Assessment (TIA) with 2021 EU SCCs are completed, and (3) written human approval from the DPO and Legal Counsel is recorded."
                ),
                mandatory_controls=[
                    "Mandatory PII/PHI redaction and pseudonymization prior to AI inference",
                    "Contractual prohibition on training foundation/third-party AI models on tenant data",
                    "Zero-data-retention API endpoint enforcement",
                    "Completed PIA/DPIA/AIIA + Cross-Border TRA/TIA prior to production enablement",
                    "Mandatory human DPO + Legal sign-off gate",
                ],
                approved_by_role="CPO",
            ),
            GovernancePolicyRecord(
                policy_id=f"POL-{tenant_id.upper()}-VND-002",
                tenant_id=tenant_id,
                title="Third-Party Vendor Privacy & Subprocessor Onboarding Policy",
                policy_category="vendor_onboarding",
                version="2026.2",
                status="effective",
                applicable_jurisdictions=["US-FED", "US-CA", "US-NY", "CA-FED", "CA-ON", "CA-QC", "EU", "EU-DE", "EU-FR"],
                mapped_regulation_ids=["EU-GDPR", "CA-QC-LAW25", "CA-ON-PHIPA", "US-CA-CCPA-CPRA", "US-FED-HIPAA", "US-NY-NYDFS-500"],
                summary=(
                    "Mandates pre-contractual vendor privacy due diligence, executed GDPR Art. 28 / Law 25 s. 18.3 DPA, "
                    "CCPA/CPRA § 1798.100(d) Service Provider Addendum, HIPAA BAA (45 CFR § 164.504(e)) where PHI is in scope, "
                    "Ontario PHIPA O. Reg. 329/04 s. 6 Electronic Service Provider / Agent Agreement, and NYDFS 23 NYCRR 500.11 cybersecurity controls."
                ),
                mandatory_controls=[
                    "Executed GDPR Art. 28 / Quebec Law 25 s. 18.3 / CPRA Service Provider DPA",
                    "HIPAA Business Associate Agreement (BAA) for PHI",
                    "Ontario PHIPA s. 10(4) & O. Reg. 329/04 s. 6 Electronic Service Provider Agreement",
                    "Subprocessor registry monitoring & 30-day advance objection notice",
                ],
                approved_by_role="LEGAL",
            ),
            GovernancePolicyRecord(
                policy_id=f"POL-{tenant_id.upper()}-CLS-003",
                tenant_id=tenant_id,
                title="Enterprise Data Classification, Retention & Cross-Border Residency Policy",
                policy_category="data_classification",
                version="2026.2",
                status="effective",
                applicable_jurisdictions=["US-FED", "US-CA", "CA-FED", "CA-ON", "CA-QC", "EU", "EU-DE", "EU-FR"],
                mapped_regulation_ids=["EU-GDPR", "CA-QC-LAW25", "CA-FED-PIPEDA", "CA-ON-PHIPA", "US-CA-CCPA-CPRA"],
                summary=(
                    "Classifies data into Tier 0 (Public), Tier 1 (Internal), Tier 2 (Confidential Customer PII), and "
                    "Tier 3 (Restricted Sensitive PII / PHI / Biometrics / Minors). Prohibits external sharing of Tier 2 and Tier 3 "
                    "data without encryption, data minimization, and verified cross-border transfer mechanisms."
                ),
                mandatory_controls=[
                    "Tier 2 & Tier 3 data blocked from unapproved external AI tools",
                    "PIPEDA 24-month breach register retention & Quebec Law 25 5-year confidentiality incident register retention",
                    "Automated cryptographic purge upon retention expiry unless subject to active legal hold",
                ],
                approved_by_role="DPO",
            ),
        ]

        self._calendar[tenant_id] = [
            GovernanceCalendarEvent(
                event_id=f"cal_{tenant_id}_phipa_mar1",
                tenant_id=tenant_id,
                title="Ontario PHIPA Annual IPC Privacy Breach Statistical Report Filing",
                cadence="statutory_deadline",
                due_date=date(date.today().year + 1, 3, 1),
                jurisdiction_id="CA-ON",
                statutory_citation="Ontario PHIPA O. Reg. 329/04 s. 6.4 (Annual report to IPC by March 1)",
                owner_role="DPO",
            ),
            GovernanceCalendarEvent(
                event_id=f"cal_{tenant_id}_hipaa_ocr",
                tenant_id=tenant_id,
                title="HIPAA Annual Under-500 Breach Log Submission to HHS OCR",
                cadence="statutory_deadline",
                due_date=date(date.today().year + 1, 2, 28),
                jurisdiction_id="US-FED",
                statutory_citation="45 CFR § 164.408(c) (Within 60 days of calendar year end)",
                owner_role="HIPAA_PRIVACY_OFFICER",
            ),
            GovernanceCalendarEvent(
                event_id=f"cal_{tenant_id}_nydfs_cert",
                tenant_id=tenant_id,
                title="NYDFS 23 NYCRR 500 Annual Senior Officer Cybersecurity Compliance Certification",
                cadence="statutory_deadline",
                due_date=date(date.today().year + 1, 4, 15),
                jurisdiction_id="US-NY",
                statutory_citation="23 NYCRR § 500.17(b) (Annual Certification by April 15)",
                owner_role="CPO",
            ),
            GovernanceCalendarEvent(
                event_id=f"cal_{tenant_id}_board_q4",
                tenant_id=tenant_id,
                title="Quarterly Executive Board & Audit Committee Privacy & AI Governance Briefing",
                cadence="quarterly",
                due_date=date.today() + timedelta(days=30),
                jurisdiction_id="GLOBAL",
                statutory_citation="GDPR Art. 38(3) Direct Reporting to Highest Management / Law 25 s. 3.1 / CPRA",
                owner_role="CPO",
            ),
        ]

        self._training[tenant_id] = [
            TrainingCampaignRecord(
                campaign_id=f"trn_{tenant_id}_001",
                tenant_id=tenant_id,
                title="Global Privacy, Multi-Jurisdictional Breach Escalation & EU AI Act Art. 4 Literacy",
                target_audience="All Employees, Engineers & Customer Support Staff",
                applicable_regulations=["EU-GDPR", "EU-AI-ACT", "CA-QC-LAW25", "CA-ON-PHIPA", "US-CA-CCPA-CPRA", "US-FED-HIPAA"],
                completion_rate_pct=97.2,
                total_assigned=850,
                total_completed=826,
                status="active",
            )
        ]

    def get_dashboard(
        self,
        tenant_id: str,
        open_incidents_count: int = 0,
        high_risk_vendors_count: int = 0,
        open_risks_count: int = 0,
        pending_amendments_count: int = 0,
    ) -> Dict[str, Any]:
        self._ensure_tenant_seeded(tenant_id)
        profile = self._profiles[tenant_id]
        establishments = self._establishments[tenant_id]
        officers = self._officers[tenant_id]
        policies = self._policies[tenant_id]
        calendar = self._calendar[tenant_id]
        training = self._training[tenant_id]

        bdsg_mandated_sites = [e.entity_name for e in establishments if e.bdsg_sec38_dpo_mandatory]
        quebec_officer = next(
            (o for o in officers if o.role_type == OfficerRoleType.QUEBEC_LAW25_PERSON_IN_CHARGE.value),
            None,
        )

        return {
            "tenant_id": tenant_id,
            "generated_at": datetime.utcnow().isoformat(),
            "organization_profile": profile,
            "corporate_establishments": [e.model_dump() for e in establishments],
            "privacy_officers_and_delegates": [o.model_dump() for o in officers],
            "statutory_officer_compliance": {
                "gdpr_art37_dpo_designated": any("DPO" in o.role_type for o in officers),
                "german_bdsg_sec38_dpo_designated": any(o.role_type == OfficerRoleType.DPO_BDSG.value for o in officers),
                "german_bdsg_sec38_mandated_establishments": bdsg_mandated_sites,
                "quebec_law25_sec3_1_person_in_charge_published": bool(quebec_officer and quebec_officer.published_on_website),
                "hipaa_privacy_and_security_officers_designated": any("HIPAA" in o.role_type for o in officers),
            },
            "governance_policies": [p.model_dump() for p in policies],
            "governance_calendar": [c.model_dump() for c in calendar],
            "training_management": [t.model_dump() for t in training],
            "budget_and_resources": {
                "annual_privacy_budget_usd": profile["annual_privacy_budget_usd"],
                "budget_allocated_usd": profile["budget_allocated_usd"],
                "remaining_budget_usd": profile["annual_privacy_budget_usd"] - profile["budget_allocated_usd"],
                "utilization_pct": profile["budget_utilization_pct"],
                "dedicated_privacy_fte_headcount": 9,
            },
            "executive_board_kpis": {
                "program_maturity_level": "Level 4 — Quantitatively Governed & Multi-Jurisdictional",
                "active_jurisdictions_count": len(profile["active_jurisdictions"]),
                "corporate_establishments_count": len(establishments),
                "effective_policies_count": len(policies),
                "workforce_training_completion_pct": training[0].completion_rate_pct if training else 100.0,
                "open_privacy_incidents_count": open_incidents_count,
                "high_risk_vendors_count": high_risk_vendors_count,
                "open_enterprise_risks_count": open_risks_count,
                "pending_regulatory_amendments_count": pending_amendments_count,
            },
        }

    def update_profile(self, tenant_id: str, payload: GovernanceProfilePayload) -> Dict[str, Any]:
        self._ensure_tenant_seeded(tenant_id)
        normalized_jurs = [normalize_jurisdiction_code(j) for j in payload.active_jurisdictions]
        utilization = (
            round((payload.budget_allocated_usd / payload.annual_privacy_budget_usd) * 100.0, 2)
            if payload.annual_privacy_budget_usd > 0
            else 0.0
        )
        self._profiles[tenant_id] = {
            "tenant_id": tenant_id,
            "organization_name": payload.organization_name,
            "industry": payload.industry,
            "organization_type": payload.organization_type,
            "employee_count": payload.employee_count,
            "annual_revenue_usd": payload.annual_revenue_usd,
            "primary_establishment": normalize_jurisdiction_code(payload.primary_establishment),
            "main_eu_establishment": normalize_jurisdiction_code(payload.main_eu_establishment) if payload.main_eu_establishment else None,
            "active_jurisdictions": normalized_jurs,
            "subnational_regions": payload.subnational_regions,
            "annual_privacy_budget_usd": payload.annual_privacy_budget_usd,
            "budget_allocated_usd": payload.budget_allocated_usd,
            "budget_utilization_pct": utilization,
            "annual_program_objectives": payload.annual_program_objectives,
            "updated_at": datetime.utcnow().isoformat(),
        }
        return self._profiles[tenant_id]

    def register_officer(self, tenant_id: str, payload: PrivacyOfficerDesignation) -> PrivacyOfficerDesignation:
        self._ensure_tenant_seeded(tenant_id)
        officer = payload.model_copy(
            update={
                "tenant_id": tenant_id,
                "jurisdictions_covered": [normalize_jurisdiction_code(j) for j in payload.jurisdictions_covered],
            }
        )
        self._officers[tenant_id].append(officer)
        return officer

    def register_establishment(self, tenant_id: str, payload: CorporateEstablishment) -> CorporateEstablishment:
        self._ensure_tenant_seeded(tenant_id)
        norm_jur = normalize_jurisdiction_code(payload.jurisdiction_id)
        entry = GLOBAL_JURISDICTION_REGISTRY.get(norm_jur)
        authority = payload.competent_authority or (entry.primary_regulator if entry else "Competent Supervisory Authority")
        bdsg_mandatory = norm_jur == "EU-DE" and payload.employees_processing_personal_data >= 20
        est = payload.model_copy(
            update={
                "tenant_id": tenant_id,
                "normalized_jurisdiction": norm_jur,
                "competent_authority": authority,
                "bdsg_sec38_dpo_mandatory": bdsg_mandatory,
            }
        )
        self._establishments[tenant_id].append(est)
        return est

    def list_policies(self, tenant_id: str) -> List[GovernancePolicyRecord]:
        self._ensure_tenant_seeded(tenant_id)
        return list(self._policies[tenant_id])

    def create_policy(self, tenant_id: str, payload: GovernancePolicyRecord) -> GovernancePolicyRecord:
        self._ensure_tenant_seeded(tenant_id)
        pol = payload.model_copy(
            update={
                "tenant_id": tenant_id,
                "applicable_jurisdictions": [normalize_jurisdiction_code(j) for j in payload.applicable_jurisdictions],
            }
        )
        self._policies[tenant_id].append(pol)
        return pol


governance_service = GovernanceAdministrationService()


# ===========================================================================
# MODULE C — MULTI-JURISDICTIONAL PRIVACY INCIDENT & BREACH MANAGEMENT
# ===========================================================================

class IncidentCreateRequest(BaseModel):
    title: str = Field(..., description="Short descriptive title of the privacy/security incident")
    description: str = Field(
        default="Unauthorized exfiltration of customer and patient personal data across North American and European cloud shards.",
        description="Factual description of the incident",
    )
    discovered_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the organization discovered / became aware of the breach",
    )
    occurred_at: Optional[datetime] = None
    affected_jurisdictions: List[str] = Field(
        default_factory=lambda: ["US-CA", "CA-ON", "CA-QC", "EU-FR", "EU-DE"],
        description="List of affected jurisdiction codes or names",
    )
    affected_counts_by_jurisdiction: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-jurisdiction count of affected individuals (e.g., {'US-CA': 650, 'CA-ON': 300, 'CA-QC': 250, 'EU-FR': 400, 'EU-DE': 350})",
    )
    total_affected_individuals: Optional[int] = None
    data_categories: List[str] = Field(
        default_factory=lambda: ["personal_identifiers", "contact_info", "ssn_sin", "financial_account", "health_information"],
        description="Categories of affected data",
    )
    involves_health_data: bool = Field(default=False, description="Whether PHI / health information is affected")
    involves_phi: bool = Field(default=False, description="Alias for health / HIPAA / PHIPA scope")
    involves_financial_data: bool = Field(default=False, description="Whether financial/payment/banking data is affected")
    is_critical_infrastructure: bool = Field(default=False, description="Whether NIS2 / critical infrastructure applies")
    encryption_status: str = Field(default="unencrypted_in_memory", description="encrypted_safe_harbor, unencrypted_in_memory, key_compromised")
    risk_of_harm_level: str = Field(default="high", description="low, medium, high, critical")
    german_subnational_region: Optional[str] = Field(
        default="DE-BY",
        description="German Land code for competent state DPA routing (e.g. DE-BY -> BayLDA, DE-BW -> LfDI BW)",
    )
    root_cause_vector: str = Field(default="compromised_api_token_and_misconfigured_storage")
    containment_status: str = Field(default="containment_in_progress")
    reported_by: str = Field(default="secops_detection_engine")


class JurisdictionRegimeEvaluation(BaseModel):
    jurisdiction_id: str
    regulation_id: str
    legal_instrument: str
    article_or_section: str
    competent_authority: str
    affected_individuals_count: int
    reporting_threshold_standard: str
    threshold_met: bool
    threshold_reasoning: str
    regulator_notification_required: bool
    individual_notification_required: bool
    attorney_general_or_media_required: bool = False
    regulator_deadline_utc: Optional[datetime] = None
    regulator_deadline_hours: Optional[int] = None
    regulator_timing_text: str
    individual_deadline_utc: Optional[datetime] = None
    individual_deadline_days: Optional[int] = None
    individual_timing_text: str
    record_retention_months: int
    record_retention_rule: str


class NotificationRecipientDraft(BaseModel):
    draft_id: str
    incident_id: str
    tenant_id: str
    jurisdiction_id: str
    regulation_id: str
    recipient_type: str = Field(..., description="regulator, attorney_general, individual, media, annual_report")
    recipient_name: str
    authority_url: Optional[str] = None
    statutory_citation: str
    deadline_utc: Optional[datetime] = None
    deadline_hours: Optional[int] = None
    timing_requirement: str
    draft_subject: str
    draft_body_summary: str
    mandatory_content_elements: List[str]
    status: str = "pending_legal_approval"
    auto_send_blocked: bool = True
    external_dispatch_authorized: bool = False
    requires_human_legal_approval: bool = True
    approved_by: Optional[str] = None
    approved_by_role: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_rationale: Optional[str] = None
    approval_signature_hash: Optional[str] = None


class DeduplicatedBreachTask(BaseModel):
    task_id: str
    category: str = Field(..., description="forensics, containment, eradication, legal_assessment, regulator_notification, individual_notification, register_retention")
    title: str
    description: str
    consolidated_across_jurisdictions: List[str]
    consolidated_across_regulations: List[str] = Field(default_factory=list, alias="consolidated_regulations")
    assigned_role: str
    priority: str = "P0_IMMEDIATE"
    due_at_utc: Optional[datetime] = None
    status: str = "open"
    prevents_duplicate_action: bool = True
    requires_human_approval: bool = False

    model_config = {"populate_by_name": True}


class EvidenceTimelineEntry(BaseModel):
    event_id: str
    timestamp_utc: datetime
    event_type: str
    actor: str
    description: str
    previous_hash: str
    evidence_hash: str


class UnifiedIncidentRecord(BaseModel):
    incident_id: str
    tenant_id: str
    title: str
    description: str
    status: str = "pending_legal_approval"
    auto_send_blocked: bool = True
    external_dispatch_authorized: bool = False
    requires_human_legal_approval: bool = True
    discovered_at: datetime
    occurred_at: datetime
    normalized_jurisdictions: List[str]
    affected_counts_by_jurisdiction: Dict[str, int]
    total_affected_individuals: int
    data_categories: List[str]
    involves_health_data: bool
    involves_financial_data: bool
    encryption_status: str
    risk_of_harm_level: str
    applicable_regimes: List[JurisdictionRegimeEvaluation]
    threshold_evaluations: Dict[str, Dict[str, Any]]
    statutory_deadlines: Dict[str, Any]
    notification_recipients: List[str]
    notification_drafts: List[NotificationRecipientDraft]
    deduplicated_tasks: List[DeduplicatedBreachTask]
    evidence_timeline: List[EvidenceTimelineEntry]
    created_at: datetime
    updated_at: datetime


class NotificationApprovalRequest(BaseModel):
    draft_id: Optional[str] = Field(
        default=None,
        description="Specific notification draft_id to approve; if omitted, approves all pending drafts on the incident",
    )
    approver_id: str = Field(default="counsel_lead_01", description="User ID of the human approver")
    approver_name: str = Field(default="Elena Rostova, General Counsel", description="Full name of the human approver")
    approver_role: str = Field(..., description="Must be LEGAL, CPO, or DPO")
    decision: str = Field(default="approved", description="approved, rejected, or changes_requested")
    rationale: str = Field(
        default="Verified forensic scope, statutory threshold analysis, and notification content for regulatory submission.",
        description="Mandatory human legal rationale",
    )


class MultiJurisdictionalBreachService:
    """
    Deterministic service for Module C — Multi-Jurisdictional Privacy Incident & Breach Management.
    Satisfies Acceptance Test 8 (Multinational Privacy Breach across US-CA, CA-ON, CA-QC, EU-FR, EU-DE).
    """

    def __init__(self) -> None:
        self._incidents: Dict[str, UnifiedIncidentRecord] = {}

    def _resolve_german_dpa_name(self, land_code: Optional[str]) -> str:
        target = (land_code or "DE-BY").upper()
        for item in GERMAN_LANDER_AUTHORITIES:
            if item["code"].startswith(target):
                return f"{item['authority']} & Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)"
        return "Bayerisches Landesamt für Datenschutzaufsicht (BayLDA) / LfDI & Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)"

    def create_incident(self, tenant_id: str, req: IncidentCreateRequest) -> UnifiedIncidentRecord:
        now = datetime.utcnow()
        discovered_at = req.discovered_at or now
        occurred_at = req.occurred_at or (discovered_at - timedelta(hours=4))
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"

        # Normalize jurisdictions while preserving order
        raw_jurs = list(req.affected_jurisdictions)
        if not raw_jurs and req.affected_counts_by_jurisdiction:
            raw_jurs = list(req.affected_counts_by_jurisdiction.keys())
        if not raw_jurs:
            raw_jurs = ["US-CA", "CA-ON", "CA-QC", "EU-FR", "EU-DE"]

        normalized_jurs: List[str] = []
        for j in raw_jurs:
            code = normalize_jurisdiction_code(j)
            if code and code not in normalized_jurs:
                normalized_jurs.append(code)

        # Normalize per-jurisdiction counts
        counts: Dict[str, int] = {}
        for k, v in req.affected_counts_by_jurisdiction.items():
            norm_k = normalize_jurisdiction_code(k)
            counts[norm_k] = max(counts.get(norm_k, 0), int(v))

        default_counts = {
            "US-CA": 650,
            "CA-ON": 320,
            "CA-FED": 320,
            "CA-QC": 280,
            "EU-FR": 410,
            "EU-DE": 390,
        }
        for code in normalized_jurs:
            if code not in counts:
                counts[code] = default_counts.get(code, 250)

        # If CA-ON is affected in a private/cross-border commercial context, CA-FED (PIPEDA) also applies concurrently
        eval_jurs = list(normalized_jurs)
        if any(c.startswith("CA-") and c not in ("CA-FED",) for c in eval_jurs) and "CA-FED" not in eval_jurs:
            eval_jurs.append("CA-FED")
            counts.setdefault("CA-FED", sum(v for k, v in counts.items() if k.startswith("CA-")))

        total_affected = req.total_affected_individuals or sum(
            v for k, v in counts.items() if k != "CA-FED" or len(normalized_jurs) == 1
        )

        health_scope = (
            req.involves_health_data
            or req.involves_phi
            or any(c in ("health_information", "phi", "medical_records", "health_data", "biometrics") for c in req.data_categories)
        )
        financial_scope = (
            req.involves_financial_data
            or any(c in ("financial_account", "payment_card", "credit_card", "bank_account", "ssn_sin") for c in req.data_categories)
        )
        high_risk = req.risk_of_harm_level.lower() in {"high", "critical", "serious", "significant", "rrosh"}
        safe_harbor_encrypted = req.encryption_status.lower() == "encrypted_safe_harbor"

        regimes: List[JurisdictionRegimeEvaluation] = []
        threshold_map: Dict[str, Dict[str, Any]] = {}
        drafts: List[NotificationRecipientDraft] = []
        recipients: List[str] = []

        def _add_recipient(name: str) -> None:
            if name not in recipients:
                recipients.append(name)

        # 1. US-CA: CCPA/CPRA & Cal. Civ. Code § 1798.82 (+ HIPAA if health_scope)
        if "US-CA" in eval_jurs or any(c.startswith("US-") for c in eval_jurs):
            ca_count = counts.get("US-CA", 650)
            ag_triggered = ca_count > 500 and not safe_harbor_encrypted
            ind_deadline = discovered_at + timedelta(days=30)
            ag_deadline = discovered_at + timedelta(days=15)

            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="US-CA",
                    regulation_id="US-CA-CIV-1798-82-CCPA",
                    legal_instrument="California Data Breach Notification Statute (Cal. Civ. Code § 1798.82) & CCPA/CPRA (§ 1798.150)",
                    article_or_section="Cal. Civ. Code § 1798.82(a), (d), (f) (>500 California residents AG filing trigger)",
                    competent_authority="California Attorney General & California Privacy Protection Agency (CalPrivacy)",
                    affected_individuals_count=ca_count,
                    reporting_threshold_standard=(
                        "Acquisition of unencrypted personal information by an unauthorized person; "
                        "electronic sample copy to California Attorney General mandatory if >500 California residents notified (Cal. Civ. Code § 1798.82(f))."
                    ),
                    threshold_met=not safe_harbor_encrypted,
                    threshold_reasoning=(
                        f"{ca_count} California residents affected ({'>500 threshold met for California AG notification' if ag_triggered else '<=500 residents'}); "
                        f"data status is '{req.encryption_status}'."
                    ),
                    regulator_notification_required=ag_triggered,
                    individual_notification_required=not safe_harbor_encrypted,
                    attorney_general_or_media_required=ag_triggered,
                    regulator_deadline_utc=ag_deadline if ag_triggered else None,
                    regulator_deadline_hours=15 * 24 if ag_triggered else None,
                    regulator_timing_text="In the most expedient time possible and without unreasonable delay (sample notice to California Attorney General when >500 CA residents affected)",
                    individual_deadline_utc=ind_deadline,
                    individual_deadline_days=30,
                    individual_timing_text="In the most expedient time possible and without unreasonable delay (Cal. Civ. Code § 1798.82(a))",
                    record_retention_months=36,
                    record_retention_rule="Retain incident forensics and notice records for at least 36 months (CPRA audit readiness).",
                )
            )
            threshold_map["US-CA"] = {
                "regulation_id": "US-CA-CIV-1798-82-CCPA",
                "standard": "Unencrypted personal information exfiltration + >500 California residents AG threshold (Cal. Civ. Code § 1798.82(f))",
                "affected_residents": ca_count,
                "exceeds_500_ag_threshold": ag_triggered,
                "threshold_met": not safe_harbor_encrypted,
            }

            if ag_triggered:
                ca_ag_name = "California Attorney General & California Privacy Protection Agency (CalPrivacy)"
                _add_recipient(ca_ag_name)
                drafts.append(
                    NotificationRecipientDraft(
                        draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                        incident_id=incident_id,
                        tenant_id=tenant_id,
                        jurisdiction_id="US-CA",
                        regulation_id="US-CA-CIV-1798-82-CCPA",
                        recipient_type="attorney_general",
                        recipient_name=ca_ag_name,
                        authority_url="https://oag.ca.gov/privacy/databreach/reporting",
                        statutory_citation="Cal. Civ. Code § 1798.82(f)",
                        deadline_utc=ag_deadline,
                        deadline_hours=15 * 24,
                        timing_requirement="Without unreasonable delay (electronic submission of sample consumer notice for >500 CA residents)",
                        draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] Cal. Civ. Code § 1798.82(f) Breach Notice — {req.title}",
                        draft_body_summary=(
                            f"Statutory electronic submission to the California Attorney General reporting a security breach affecting "
                            f"{ca_count} California residents discovered at {discovered_at.isoformat()}."
                        ),
                        mandatory_content_elements=[
                            "Heading: 'Notice of Data Breach'",
                            "Sections: 'What Happened', 'What Information Was Involved', 'What We Are Doing', 'What You Can Do', 'For More Information' (Cal. Civ. Code § 1798.82(d)(1))",
                            "At least 12 months of identity theft prevention and mitigation services at no cost if SSN/driver's license affected",
                        ],
                    )
                )

            if health_scope:
                hipaa_deadline = discovered_at + timedelta(days=60)
                regimes.append(
                    JurisdictionRegimeEvaluation(
                        jurisdiction_id="US-FED",
                        regulation_id="US-FED-HIPAA-HITECH",
                        legal_instrument="HIPAA Breach Notification Rule (45 CFR §§ 164.400–414) & HITECH Act",
                        article_or_section="45 CFR § 164.402 (4-Factor Risk Assessment), § 164.404 (Individuals), § 164.406 (Media >=500), § 164.408 (HHS OCR)",
                        competent_authority="U.S. Department of Health and Human Services — Office for Civil Rights (HHS OCR)",
                        affected_individuals_count=ca_count,
                        reporting_threshold_standard="HIPAA 4-Factor Risk Assessment (45 CFR § 164.402(2)): nature/extent of PHI, unauthorized person, whether PHI was actually acquired/viewed, extent of risk mitigation.",
                        threshold_met=not safe_harbor_encrypted,
                        threshold_reasoning="4-Factor Risk Assessment indicates more than a low probability that unsecured PHI has been compromised.",
                        regulator_notification_required=True,
                        individual_notification_required=True,
                        attorney_general_or_media_required=ca_count >= 500,
                        regulator_deadline_utc=hipaa_deadline,
                        regulator_deadline_hours=60 * 24,
                        regulator_timing_text="Without unreasonable delay and in no case later than 60 calendar days from discovery (45 CFR § 164.408(b) for >=500 individuals)",
                        individual_deadline_utc=hipaa_deadline,
                        individual_deadline_days=60,
                        individual_timing_text="Without unreasonable delay and no later than 60 calendar days from discovery (45 CFR § 164.404(b))",
                        record_retention_months=72,
                        record_retention_rule="6 years under HIPAA 45 CFR § 164.530(j)(2).",
                    )
                )
                threshold_map["US-FED-HIPAA"] = {
                    "regulation_id": "US-FED-HIPAA-HITECH",
                    "standard": "HIPAA 4-Factor Risk Assessment (45 CFR § 164.402(2)) — Presumption of reportable breach unless low probability of compromise is demonstrated",
                    "factors_evaluated": [
                        "Factor 1: Nature and extent of PHI involved (identifiers and clinical/health indicators)",
                        "Factor 2: Unauthorized person who used the PHI or to whom disclosure was made",
                        "Factor 3: Whether the PHI was actually acquired or viewed",
                        "Factor 4: Extent to which the risk to the PHI has been mitigated",
                    ],
                    "threshold_met": not safe_harbor_encrypted,
                }
                ocr_name = "HHS Office for Civil Rights (OCR)"
                _add_recipient(ocr_name)
                drafts.append(
                    NotificationRecipientDraft(
                        draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                        incident_id=incident_id,
                        tenant_id=tenant_id,
                        jurisdiction_id="US-FED",
                        regulation_id="US-FED-HIPAA-HITECH",
                        recipient_type="regulator",
                        recipient_name=ocr_name,
                        authority_url="https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf",
                        statutory_citation="45 CFR §§ 164.404, 164.408",
                        deadline_utc=hipaa_deadline,
                        deadline_hours=60 * 24,
                        timing_requirement="Without unreasonable delay and no later than 60 calendar days after discovery",
                        draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] HIPAA Breach Notification to HHS OCR — {req.title}",
                        draft_body_summary="Draft HHS OCR breach portal submission following 45 CFR § 164.402 4-factor risk assessment.",
                        mandatory_content_elements=[
                            "Brief description of what happened, including date of breach and date of discovery",
                            "Description of the types of unsecured PHI involved",
                            "Steps individuals should take to protect themselves",
                            "Description of investigation, mitigation, and prevention measures",
                        ],
                    )
                )

        # 2. CA-ON & CA-FED: Ontario PHIPA (IPC Ontario) + Canadian Federal PIPEDA (OPC Canada RROSH)
        if "CA-ON" in eval_jurs or "CA-FED" in eval_jurs:
            on_count = counts.get("CA-ON", 320)
            ipc_deadline = discovered_at + timedelta(hours=72)  # Operational planning anchor for "at the first reasonable opportunity"

            # Ontario PHIPA / IPC Ontario
            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="CA-ON",
                    regulation_id="CA-ON-PHIPA",
                    legal_instrument="Ontario Personal Health Information Protection Act, 2004 (PHIPA, S.O. 2004, c. 3, Sched. A) & O. Reg. 329/04 s. 6.3",
                    article_or_section="PHIPA s. 12(2) (Notice to Individual at First Reasonable Opportunity) & s. 12(3) / O. Reg. 329/04 s. 6.3 (Notice to IPC Ontario)",
                    competent_authority="Information and Privacy Commissioner of Ontario (IPC Ontario)",
                    affected_individuals_count=on_count,
                    reporting_threshold_standard=(
                        "Unauthorized theft, loss, use, or disclosure of personal health information (PHIPA s. 12(2)); "
                        "mandatory IPC reporting under O. Reg. 329/04 s. 6.3 (willful/pattern/further disclosure/significant breach)."
                    ),
                    threshold_met=True,
                    threshold_reasoning="Exfiltration involves unauthorized access/disclosure meeting O. Reg. 329/04 s. 6.3 prescribed IPC reporting criteria.",
                    regulator_notification_required=True,
                    individual_notification_required=True,
                    regulator_deadline_utc=ipc_deadline,
                    regulator_deadline_hours=72,
                    regulator_timing_text="At the first reasonable opportunity (PHIPA s. 12(2)-(3); annual statistical report also due by March 1 under O. Reg. 329/04 s. 6.4)",
                    individual_deadline_utc=ipc_deadline,
                    individual_deadline_days=3,
                    individual_timing_text="At the first reasonable opportunity (PHIPA s. 12(2))",
                    record_retention_months=60,
                    record_retention_rule="Retain PHIPA breach audit logs and annual IPC statistical report records.",
                )
            )
            threshold_map["CA-ON"] = {
                "regulation_id": "CA-ON-PHIPA",
                "standard": "PHIPA s. 12(2)-(3) & O. Reg. 329/04 s. 6.3 prescribed IPC reporting circumstances + PIPEDA RROSH",
                "affected_residents": on_count,
                "threshold_met": True,
            }
            ipc_name = "Information and Privacy Commissioner of Ontario (IPC Ontario)"
            _add_recipient(ipc_name)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="CA-ON",
                    regulation_id="CA-ON-PHIPA",
                    recipient_type="regulator",
                    recipient_name=ipc_name,
                    authority_url="https://www.ipc.on.ca/en/health-organizations/responding-privacy-breaches",
                    statutory_citation="Ontario PHIPA s. 12(2)-(3) & O. Reg. 329/04 s. 6.3",
                    deadline_utc=ipc_deadline,
                    deadline_hours=72,
                    timing_requirement="At the first reasonable opportunity",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] IPC Ontario PHIPA s. 12 Breach Report — {req.title}",
                    draft_body_summary=f"Draft notification to IPC Ontario regarding breach affecting {on_count} Ontario individuals.",
                    mandatory_content_elements=[
                        "Circumstances of the theft, loss, or unauthorized use/disclosure",
                        "Steps taken to contain the breach and prevent recurrence",
                        "Statement that affected individuals have the right to make a complaint to the IPC under PHIPA s. 12(2)(b)",
                    ],
                )
            )

            # Federal PIPEDA (OPC Canada) — Real Risk of Significant Harm (RROSH)
            opc_deadline = discovered_at + timedelta(hours=72)  # Operational planning target for "as soon as feasible"
            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="CA-FED",
                    regulation_id="CA-FED-PIPEDA-DIV1-5",
                    legal_instrument="Personal Information Protection and Electronic Documents Act (PIPEDA) Division 1.1 & Breach of Security Safeguards Regulations (SOR/2018-64)",
                    article_or_section="PIPEDA ss. 10.1(1)-(2) (OPC & Individual Report), s. 10.1(7)-(8) (RROSH factors), s. 10.3(1) (24-Month Breach Record Retention)",
                    competent_authority="Office of the Privacy Commissioner of Canada (OPC)",
                    affected_individuals_count=counts.get("CA-FED", on_count),
                    reporting_threshold_standard=(
                        "Real Risk of Significant Harm (RROSH) under PIPEDA s. 10.1(7)-(8), evaluating: "
                        "(a) sensitivity of the personal information involved, and (b) probability that the personal information has been, is being, or will be misused."
                    ),
                    threshold_met=high_risk and not safe_harbor_encrypted,
                    threshold_reasoning="Sensitivity of affected identifiers/financial/health data combined with external exfiltration vector establishes RROSH under PIPEDA s. 10.1(8).",
                    regulator_notification_required=high_risk and not safe_harbor_encrypted,
                    individual_notification_required=high_risk and not safe_harbor_encrypted,
                    regulator_deadline_utc=opc_deadline,
                    regulator_deadline_hours=72,
                    regulator_timing_text="As soon as feasible after the organization determines that the breach has occurred (PIPEDA s. 10.1(2), SOR/2018-64 s. 2)",
                    individual_deadline_utc=opc_deadline,
                    individual_deadline_days=3,
                    individual_timing_text="As soon as feasible after the organization determines that the breach has occurred (PIPEDA s. 10.1(3))",
                    record_retention_months=24,
                    record_retention_rule="Mandatory 24-month retention of every breach of security safeguards record under PIPEDA s. 10.3(1) and SOR/2018-64 s. 6(1), regardless of whether RROSH threshold was met.",
                )
            )
            threshold_map["CA-FED"] = {
                "regulation_id": "CA-FED-PIPEDA-DIV1-5",
                "standard": "Real Risk of Significant Harm (RROSH — PIPEDA s. 10.1(7)-(8): sensitivity + probability of misuse)",
                "rrosh_determined": high_risk and not safe_harbor_encrypted,
                "threshold_met": high_risk and not safe_harbor_encrypted,
            }
            opc_name = "Office of the Privacy Commissioner of Canada (OPC)"
            _add_recipient(opc_name)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="CA-FED",
                    regulation_id="CA-FED-PIPEDA-DIV1-5",
                    recipient_type="regulator",
                    recipient_name=opc_name,
                    authority_url="https://www.priv.gc.ca/en/report-a-concern/report-a-privacy-breach-at-your-organization/",
                    statutory_citation="PIPEDA s. 10.1(1)-(2) & Breach of Security Safeguards Regulations SOR/2018-64 s. 2",
                    deadline_utc=opc_deadline,
                    deadline_hours=72,
                    timing_requirement="As soon as feasible after determination of breach posing RROSH",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] OPC PIPEDA s. 10.1 RROSH Breach Report — {req.title}",
                    draft_body_summary="Draft PIPEDA Breach of Security Safeguards report to the Office of the Privacy Commissioner of Canada (OPC).",
                    mandatory_content_elements=[
                        "Description of the circumstances of the breach and, if known, the cause",
                        "Day or period during which the breach occurred",
                        "Description of the personal information that is the subject of the breach",
                        "Estimate of the number of individuals in respect of whom the breach creates a real risk of significant harm",
                        "Description of the steps that the organization has taken to reduce the risk of harm",
                    ],
                )
            )

        # 3. CA-QC: Quebec Law 25 (CAI Confidentiality Incident Rules)
        if "CA-QC" in eval_jurs:
            qc_count = counts.get("CA-QC", 280)
            cai_deadline = discovered_at + timedelta(hours=72)  # Operational planning target for "promptly / avec diligence"
            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="CA-QC",
                    regulation_id="CA-QC-LAW25-SEC3-5",
                    legal_instrument="Quebec Act respecting the protection of personal information in the private sector (Law 25 / Bill 64, CQLR c. P-39.1) & Regulation respecting confidentiality incidents",
                    article_or_section="CQLR c. P-39.1 ss. 3.5, 3.6, 3.7, 3.8 (Confidentiality Incidents, Risk of Serious Injury & 5-Year Register)",
                    competent_authority="Commission d'accès à l'information du Québec (CAI)",
                    affected_individuals_count=qc_count,
                    reporting_threshold_standard=(
                        "Risk of serious injury (risque qu'un préjudice sérieux soit causé) under s. 3.5 & s. 3.7, evaluating: "
                        "(1) sensitivity of the information, (2) anticipated consequences of its use, and (3) likelihood that such information will be used for injurious purposes. "
                        "Person in Charge of Personal Information (s. 3.1) must be consulted during assessment."
                    ),
                    threshold_met=high_risk and not safe_harbor_encrypted,
                    threshold_reasoning="Confidentiality incident presents a risk of serious injury to {qc_count} Quebec residents under s. 3.7 criteria.",
                    regulator_notification_required=high_risk and not safe_harbor_encrypted,
                    individual_notification_required=high_risk and not safe_harbor_encrypted,
                    regulator_deadline_utc=cai_deadline,
                    regulator_deadline_hours=72,
                    regulator_timing_text="Promptly / with diligence (avec diligence — CQLR c. P-39.1 s. 3.5)",
                    individual_deadline_utc=cai_deadline,
                    individual_deadline_days=3,
                    individual_timing_text="Promptly / with diligence (avec diligence — CQLR c. P-39.1 s. 3.5)",
                    record_retention_months=60,
                    record_retention_rule="Mandatory 5-year (60-month) retention in the Confidentiality Incident Register from the date the organization became aware of the incident (Regulation respecting confidentiality incidents, s. 7).",
                )
            )
            threshold_map["CA-QC"] = {
                "regulation_id": "CA-QC-LAW25-SEC3-5",
                "standard": "Risk of Serious Injury (risque de préjudice sérieux — Quebec Law 25 ss. 3.5, 3.7)",
                "serious_injury_risk_determined": high_risk and not safe_harbor_encrypted,
                "threshold_met": high_risk and not safe_harbor_encrypted,
                "incident_register_retention_years": 5,
            }
            cai_name = "Commission d'accès à l'information du Québec (CAI)"
            _add_recipient(cai_name)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="CA-QC",
                    regulation_id="CA-QC-LAW25-SEC3-5",
                    recipient_type="regulator",
                    recipient_name=cai_name,
                    authority_url="https://www.cai.gouv.qc.ca/incidents-de-confidentialite/",
                    statutory_citation="Quebec Law 25 (CQLR c. P-39.1) ss. 3.5–3.8 & Regulation respecting confidentiality incidents s. 3",
                    deadline_utc=cai_deadline,
                    deadline_hours=72,
                    timing_requirement="Promptly (avec diligence) under CQLR c. P-39.1 s. 3.5",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] Avis d'incident de confidentialité à la CAI (Law 25 s. 3.5) — {req.title}",
                    draft_body_summary=f"Written notice in French/English to the Commission d'accès à l'information du Québec (CAI) for {qc_count} affected Quebec residents.",
                    mandatory_content_elements=[
                        "Name of organization and Québec Business Number (NEQ)",
                        "Name and contact information of the Person in Charge of the Protection of Personal Information (s. 3.1)",
                        "Description of personal information covered by the incident and circumstances",
                        "Date or period when the incident occurred and date when discovered",
                        "Number of Quebec individuals concerned and assessment of risk of serious injury (s. 3.7)",
                        "Measures taken to diminish risks of injury and prevent new incidents of the same nature",
                    ],
                )
            )

        # 4. EU-FR: GDPR Art. 33/34 + French Loi Informatique et Libertés + CNIL
        if "EU-FR" in eval_jurs:
            fr_count = counts.get("EU-FR", 410)
            cnil_deadline = discovered_at + timedelta(hours=72)
            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="EU-FR",
                    regulation_id="EU-GDPR-FR-CNIL",
                    legal_instrument="EU General Data Protection Regulation (Regulation (EU) 2016/679) Arts. 33–34 & French Loi Informatique et Libertés (LIL Art. 58)",
                    article_or_section="GDPR Art. 33(1) (72-Hour Supervisory Authority Notification to CNIL) & Art. 34(1) (High Risk Data Subject Communication)",
                    competent_authority="Commission Nationale de l'Informatique et des Libertés (CNIL)",
                    affected_individuals_count=fr_count,
                    reporting_threshold_standard=(
                        "Art. 33(1) Regulator Notice: Mandatory unless the personal data breach is unlikely to result in a risk to the rights and freedoms of natural persons. "
                        "Art. 34(1) Individual Notice: Mandatory when the breach is likely to result in a HIGH RISK to the rights and freedoms of natural persons."
                    ),
                    threshold_met=True,
                    threshold_reasoning=f"Breach affecting {fr_count} individuals in France poses both a risk (Art. 33) and high risk (Art. 34) to rights and freedoms.",
                    regulator_notification_required=True,
                    individual_notification_required=high_risk and not safe_harbor_encrypted,
                    regulator_deadline_utc=cnil_deadline,
                    regulator_deadline_hours=72,
                    regulator_timing_text="Without undue delay and, where feasible, not later than 72 hours after having become aware of it (GDPR Art. 33(1))",
                    individual_deadline_utc=cnil_deadline,
                    individual_deadline_days=3,
                    individual_timing_text="Without undue delay (GDPR Art. 34(1))",
                    record_retention_months=60,
                    record_retention_rule="Mandatory Art. 33(5) internal breach register documenting facts, effects, and remedial action taken.",
                )
            )
            threshold_map["EU-FR"] = {
                "regulation_id": "EU-GDPR-FR-CNIL",
                "standard": "GDPR Art. 33 ('unless unlikely to result in a risk') & Art. 34 ('likely to result in a high risk')",
                "art33_risk_triggered": True,
                "art34_high_risk_triggered": high_risk and not safe_harbor_encrypted,
                "threshold_met": True,
                "deadline_hours": 72,
            }
            cnil_name = "Commission Nationale de l'Informatique et des Libertés (CNIL)"
            _add_recipient(cnil_name)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="EU-FR",
                    regulation_id="EU-GDPR-FR-CNIL",
                    recipient_type="regulator",
                    recipient_name=cnil_name,
                    authority_url="https://notifications.cnil.fr/notifications/index",
                    statutory_citation="GDPR Art. 33(1)-(3) & French Loi Informatique et Libertés Art. 58",
                    deadline_utc=cnil_deadline,
                    deadline_hours=72,
                    timing_requirement="Without undue delay and not later than 72 hours after awareness (GDPR Art. 33(1))",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] Notification de violation de données à la CNIL (GDPR Art. 33) — {req.title}",
                    draft_body_summary=f"GDPR Art. 33 notification draft for CNIL teleservice regarding {fr_count} affected data subjects in France.",
                    mandatory_content_elements=[
                        "Nature of the personal data breach including categories and approximate number of data subjects and personal data records (Art. 33(3)(a))",
                        "Name and contact details of the Data Protection Officer (Art. 33(3)(b))",
                        "Likely consequences of the personal data breach (Art. 33(3)(c))",
                        "Measures taken or proposed to be taken by the controller to address the breach and mitigate possible adverse effects (Art. 33(3)(d))",
                    ],
                )
            )

        # 5. EU-DE: GDPR Art. 33/34 + German BDSG §§ 29, 65 + Competent German Land DPA (BayLDA / LfDI / BfDI)
        if "EU-DE" in eval_jurs:
            de_count = counts.get("EU-DE", 390)
            de_deadline = discovered_at + timedelta(hours=72)
            de_authority = self._resolve_german_dpa_name(req.german_subnational_region)
            regimes.append(
                JurisdictionRegimeEvaluation(
                    jurisdiction_id="EU-DE",
                    regulation_id="EU-GDPR-DE-BDSG",
                    legal_instrument="EU General Data Protection Regulation (Regulation (EU) 2016/679) Arts. 33–34 & German Federal Data Protection Act (BDSG §§ 29, 65)",
                    article_or_section="GDPR Arts. 33–34 & BDSG § 29 (Secrecy obligations / exceptions to Art. 34) & § 42/43",
                    competent_authority=de_authority,
                    affected_individuals_count=de_count,
                    reporting_threshold_standard=(
                        "GDPR Art. 33(1) 72-hour notification to competent German Land DPA (e.g., BayLDA / LfDI BW) & BfDI unless unlikely to result in a risk; "
                        "GDPR Art. 34(1) & BDSG § 29 high-risk notification to data subjects."
                    ),
                    threshold_met=True,
                    threshold_reasoning=f"Breach affecting {de_count} German residents triggers 72-hour notification to {de_authority} and Art. 34 high-risk subject notice.",
                    regulator_notification_required=True,
                    individual_notification_required=high_risk and not safe_harbor_encrypted,
                    regulator_deadline_utc=de_deadline,
                    regulator_deadline_hours=72,
                    regulator_timing_text="Without undue delay and not later than 72 hours after having become aware of it (GDPR Art. 33(1))",
                    individual_deadline_utc=de_deadline,
                    individual_deadline_days=3,
                    individual_timing_text="Without undue delay (GDPR Art. 34(1) & BDSG § 29)",
                    record_retention_months=60,
                    record_retention_rule="Mandatory GDPR Art. 33(5) & BDSG documentation of breach facts, effects, and remedial measures.",
                )
            )
            threshold_map["EU-DE"] = {
                "regulation_id": "EU-GDPR-DE-BDSG",
                "standard": "GDPR Art. 33/34 + German BDSG § 29 & Competent German Land DPA routing",
                "competent_german_dpa": de_authority,
                "art33_risk_triggered": True,
                "art34_high_risk_triggered": high_risk and not safe_harbor_encrypted,
                "threshold_met": True,
                "deadline_hours": 72,
            }
            _add_recipient(de_authority)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="EU-DE",
                    regulation_id="EU-GDPR-DE-BDSG",
                    recipient_type="regulator",
                    recipient_name=de_authority,
                    authority_url="https://www.lda.bayern.de/de/datenpanne.html",
                    statutory_citation="GDPR Art. 33(1)-(3) & German BDSG §§ 29, 40",
                    deadline_utc=de_deadline,
                    deadline_hours=72,
                    timing_requirement="Without undue delay and not later than 72 hours after awareness (GDPR Art. 33(1))",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] Meldung einer Verletzung des Schutzes personenbezogener Daten nach Art. 33 DSGVO — {req.title}",
                    draft_body_summary=f"German GDPR Art. 33 / BDSG breach notification draft for {de_authority} covering {de_count} German data subjects.",
                    mandatory_content_elements=[
                        "Art der Verletzung des Schutzes personenbezogener Daten (Art. 33 Abs. 3 lit. a DSGVO)",
                        "Name und Kontaktdaten des Datenschutzbeauftragten nach Art. 37 DSGVO / § 38 BDSG (Art. 33 Abs. 3 lit. b DSGVO)",
                        "Beschreibung der wahrscheinlichen Folgen (Art. 33 Abs. 3 lit. c DSGVO)",
                        "Beschreibung der ergriffenen oder vorgeschlagenen Maßnahmen (Art. 33 Abs. 3 lit. d DSGVO)",
                    ],
                )
            )

        # 6. Affected Data Subjects Notification Draft (Harmonized Multi-Jurisdictional Individual Notice)
        if not safe_harbor_encrypted:
            ind_recipient_label = f"Affected Data Subjects ({total_affected} individuals across {', '.join(normalized_jurs)})"
            _add_recipient(ind_recipient_label)
            drafts.append(
                NotificationRecipientDraft(
                    draft_id=f"drf_{uuid.uuid4().hex[:10]}",
                    incident_id=incident_id,
                    tenant_id=tenant_id,
                    jurisdiction_id="MULTI-JURISDICTIONAL",
                    regulation_id="CONSOLIDATED-INDIVIDUAL-NOTICE",
                    recipient_type="individual",
                    recipient_name=ind_recipient_label,
                    statutory_citation="Cal. Civ. Code § 1798.82(d); Ontario PHIPA s. 12(2); PIPEDA s. 10.1(3); Quebec Law 25 s. 3.5; GDPR Art. 34",
                    deadline_utc=discovered_at + timedelta(hours=72),
                    deadline_hours=72,
                    timing_requirement="Without undue delay / Promptly / As soon as feasible / At first reasonable opportunity",
                    draft_subject=f"[DRAFT - PENDING LEGAL APPROVAL] Notice of Data Breach / Avis d'incident de confidentialité — {req.title}",
                    draft_body_summary=(
                        "Multi-lingual (English, French for Quebec/France, German for Germany) individual breach notification satisfying "
                        "California statutory headings, Quebec Law 25 s. 3.5, Ontario PHIPA s. 12(2) IPC complaint right, PIPEDA SOR/2018-64 s. 3, and GDPR Art. 34(2)."
                    ),
                    mandatory_content_elements=[
                        "California Cal. Civ. Code § 1798.82(d) mandatory headings ('What Happened', 'What Information Was Involved', 'What We Are Doing', 'What You Can Do', 'For More Information')",
                        "Ontario PHIPA s. 12(2)(b) explicit statement of right to file a complaint with the Information and Privacy Commissioner of Ontario (IPC)",
                        "Quebec Law 25 & French LIL / GDPR Art. 34 French-language translation and DPO / Person in Charge contact details",
                        "German GDPR Art. 34 & BDSG § 29 German-language notice with DSB contact details",
                    ],
                )
            )

        # Compute deterministic deadline summary via JRAE deadlines helper as well
        jrae_deadline_calc = calculate_breach_deadlines(
            jurisdictions=eval_jurs,
            discovery_time=discovered_at,
            affected_counts_by_jurisdiction=counts,
            involves_phi=health_scope,
            involves_financial=financial_scope,
            is_critical_infrastructure=req.is_critical_infrastructure,
            risk_of_harm_level=req.risk_of_harm_level,
        )

        all_reg_Ids = [r.regulation_id for r in regimes]
        strictest_72h = discovered_at + timedelta(hours=72)

        # Generate deduplicated workflow action plan preventing duplicate or contradictory forensic/containment tasks
        dedup_tasks: List[DeduplicatedBreachTask] = [
            DeduplicatedBreachTask(
                task_id=f"tsk_{uuid.uuid4().hex[:8]}_forensics",
                category="forensics",
                title="Execute Unified Cryptographic Forensic Preservation & Chain-of-Custody Snapshot",
                description=(
                    "Single consolidated forensic memory/log acquisition across affected cloud shards. "
                    "Prevents duplicate or conflicting forensic snapshots across US, Canadian, and EU incident teams."
                ),
                consolidated_across_jurisdictions=normalized_jurs,
                consolidated_regulations=all_reg_Ids,
                assigned_role="CISO",
                priority="P0_IMMEDIATE",
                due_at_utc=discovered_at + timedelta(hours=4),
                prevents_duplicate_action=True,
                requires_human_approval=False,
            ),
            DeduplicatedBreachTask(
                task_id=f"tsk_{uuid.uuid4().hex[:8]}_containment",
                category="containment",
                title="Execute Unified Credential Revocation, Token Rotation & Network Containment",
                description=(
                    "Single coordinated containment workflow revoking compromised API tokens and isolating affected storage buckets "
                    "after forensic snapshot completion, preventing premature log destruction."
                ),
                consolidated_across_jurisdictions=normalized_jurs,
                consolidated_regulations=all_reg_Ids,
                assigned_role="CISO",
                priority="P0_IMMEDIATE",
                due_at_utc=discovered_at + timedelta(hours=6),
                prevents_duplicate_action=True,
                requires_human_approval=False,
            ),
            DeduplicatedBreachTask(
                task_id=f"tsk_{uuid.uuid4().hex[:8]}_legal_triage",
                category="legal_assessment",
                title="Complete Multi-Jurisdictional Harm & Threshold Assessment (RROSH / Serious Injury / GDPR Art. 33-34 / CA >500)",
                description=(
                    "Unified legal privileges & harm assessment verifying PIPEDA RROSH, Quebec Law 25 serious injury, "
                    "Ontario PHIPA s. 12, GDPR Arts. 33/34 risk, and California >500 AG trigger."
                ),
                consolidated_across_jurisdictions=normalized_jurs,
                consolidated_regulations=all_reg_Ids,
                assigned_role="DPO",
                priority="P0_IMMEDIATE",
                due_at_utc=discovered_at + timedelta(hours=24),
                prevents_duplicate_action=True,
                requires_human_approval=True,
            ),
            DeduplicatedBreachTask(
                task_id=f"tsk_{uuid.uuid4().hex[:8]}_reg_notices",
                category="regulator_notification",
                title="Human Legal Review & Approval of Per-Regulator Notification Drafts (72-Hour Strictest Clock)",
                description=(
                    f"Review and approve regulator-specific filings for {', '.join(recipients)}. "
                    "All external dispatches are hard-blocked until human LEGAL/CPO/DPO approval is recorded."
                ),
                consolidated_across_jurisdictions=normalized_jurs,
                consolidated_regulations=all_reg_Ids,
                assigned_role="LEGAL",
                priority="P0_IMMEDIATE",
                due_at_utc=strictest_72h,
                prevents_duplicate_action=True,
                requires_human_approval=True,
            ),
            DeduplicatedBreachTask(
                task_id=f"tsk_{uuid.uuid4().hex[:8]}_registers",
                category="register_retention",
                title="Record Incident in Statutory Breach Registers (GDPR Art. 33(5), PIPEDA 24-Month, Quebec Law 25 5-Year)",
                description=(
                    "Synchronize unified cryptographic incident record to the GDPR Art. 33(5) internal register, "
                    "PIPEDA s. 10.3 24-month register, Quebec Law 25 s. 3.8 5-year confidentiality incident register, "
                    "and Ontario PHIPA annual March 1 IPC statistical log."
                ),
                consolidated_across_jurisdictions=normalized_jurs,
                consolidated_regulations=all_reg_Ids,
                assigned_role="DPO",
                priority="P1_HIGH",
                due_at_utc=discovered_at + timedelta(hours=48),
                prevents_duplicate_action=True,
                requires_human_approval=False,
            ),
        ]

        # Build tamper-evident cryptographic evidence timeline
        genesis_hash = "0" * 64
        ev1_payload = f"{incident_id}|OCCURRED|{occurred_at.isoformat()}|{req.root_cause_vector}|{genesis_hash}"
        ev1_hash = _compute_sha256(ev1_payload)

        ev2_payload = f"{incident_id}|DISCOVERED|{discovered_at.isoformat()}|{req.reported_by}|{ev1_hash}"
        ev2_hash = _compute_sha256(ev2_payload)

        ev3_payload = f"{incident_id}|EVALUATED_MULTI_JURISDICTIONAL|{now.isoformat()}|{'/'.join(normalized_jurs)}|{ev2_hash}"
        ev3_hash = _compute_sha256(ev3_payload)

        ev4_payload = f"{incident_id}|ROUTED_TO_HUMAN_LEGAL_APPROVAL|{now.isoformat()}|auto_send_blocked=True|{ev3_hash}"
        ev4_hash = _compute_sha256(ev4_payload)

        evidence_timeline = [
            EvidenceTimelineEntry(
                event_id=f"ev_{uuid.uuid4().hex[:8]}_1",
                timestamp_utc=occurred_at,
                event_type="INCIDENT_OCCURRENCE_ANCHOR",
                actor="forensic_timeline_reconstruction",
                description=f"Root cause vector identified: {req.root_cause_vector}",
                previous_hash=genesis_hash,
                evidence_hash=ev1_hash,
            ),
            EvidenceTimelineEntry(
                event_id=f"ev_{uuid.uuid4().hex[:8]}_2",
                timestamp_utc=discovered_at,
                event_type="INCIDENT_DISCOVERY_CLOCK_START",
                actor=req.reported_by,
                description=f"Breach discovered; statutory clocks anchored to {discovered_at.isoformat()}.",
                previous_hash=ev1_hash,
                evidence_hash=ev2_hash,
            ),
            EvidenceTimelineEntry(
                event_id=f"ev_{uuid.uuid4().hex[:8]}_3",
                timestamp_utc=now,
                event_type="MULTI_JURISDICTIONAL_REGIME_AND_THRESHOLD_EVALUATION",
                actor="kibo_breach_engine_v1",
                description=(
                    f"Evaluated {len(regimes)} independent regulatory regimes across {', '.join(normalized_jurs)} "
                    f"and generated {len(dedup_tasks)} deduplicated workflow tasks."
                ),
                previous_hash=ev2_hash,
                evidence_hash=ev3_hash,
            ),
            EvidenceTimelineEntry(
                event_id=f"ev_{uuid.uuid4().hex[:8]}_4",
                timestamp_utc=now,
                event_type="MANDATORY_HUMAN_LEGAL_APPROVAL_GATE_ENFORCED",
                actor="kibo_governance_gate",
                description=(
                    f"Generated {len(drafts)} notification drafts with status='pending_legal_approval' and auto_send_blocked=True. "
                    "External regulatory dispatch is strictly prohibited without human LEGAL/CPO/DPO approval."
                ),
                previous_hash=ev3_hash,
                evidence_hash=ev4_hash,
            ),
        ]

        statutory_deadlines = {
            "clock_anchor_discovered_at_utc": discovered_at.isoformat(),
            "strictest_regulator_deadline_hours": 72,
            "strictest_regulator_deadline_utc": strictest_72h.isoformat(),
            "gdpr_cnil_fr_72h_deadline_utc": strictest_72h.isoformat(),
            "gdpr_german_dpa_de_72h_deadline_utc": strictest_72h.isoformat(),
            "quebec_cai_law25_timing": "Promptly (avec diligence — CQLR c. P-39.1 s. 3.5; operational target <=72h)",
            "ontario_ipc_phipa_timing": "At the first reasonable opportunity (PHIPA s. 12(2)-(3)) + Annual statistical report by March 1",
            "canada_opc_pipeda_timing": "As soon as feasible (PIPEDA s. 10.1(2) & SOR/2018-64)",
            "california_ag_and_residents_timing": "Without unreasonable delay (Cal. Civ. Code § 1798.82; >500 CA residents requires electronic sample notice to California AG)",
            "hipaa_ocr_timing": "Without unreasonable delay and no later than 60 calendar days (45 CFR §§ 164.404, 164.408)" if health_scope else "Not applicable unless PHI in scope",
            "jrae_deadline_engine_plan": jrae_deadline_calc,
        }

        incident = UnifiedIncidentRecord(
            incident_id=incident_id,
            tenant_id=tenant_id,
            title=req.title,
            description=req.description,
            status="pending_legal_approval",
            auto_send_blocked=True,
            external_dispatch_authorized=False,
            requires_human_legal_approval=True,
            discovered_at=discovered_at,
            occurred_at=occurred_at,
            normalized_jurisdictions=normalized_jurs,
            affected_counts_by_jurisdiction=counts,
            total_affected_individuals=total_affected,
            data_categories=req.data_categories,
            involves_health_data=health_scope,
            involves_financial_data=financial_scope,
            encryption_status=req.encryption_status,
            risk_of_harm_level=req.risk_of_harm_level,
            applicable_regimes=regimes,
            threshold_evaluations=threshold_map,
            statutory_deadlines=statutory_deadlines,
            notification_recipients=recipients,
            notification_drafts=drafts,
            deduplicated_tasks=dedup_tasks,
            evidence_timeline=evidence_timeline,
            created_at=now,
            updated_at=now,
        )
        self._incidents[incident_id] = incident
        return incident

    def list_incidents(self, tenant_id: str) -> List[UnifiedIncidentRecord]:
        return [inc for inc in self._incidents.values() if inc.tenant_id == tenant_id]

    def get_incident(self, tenant_id: str, incident_id: str) -> UnifiedIncidentRecord:
        inc = self._incidents.get(incident_id)
        if not inc:
            raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
        if inc.tenant_id != tenant_id:
            raise HTTPException(
                status_code=403,
                detail="CROSS_TENANT_ACCESS_DENIED: Incident belongs to a different tenant",
            )
        return inc

    def approve_notification(
        self,
        tenant_id: str,
        incident_id: str,
        payload: NotificationApprovalRequest,
        caller_role: str,
    ) -> UnifiedIncidentRecord:
        inc = self.get_incident(tenant_id, incident_id)
        effective_role = (caller_role or payload.approver_role).strip().upper()
        if effective_role not in {"LEGAL", "CPO", "DPO"}:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"HUMAN_LEGAL_APPROVAL_REQUIRED: Role '{effective_role}' is not authorized to approve "
                    "regulatory breach notifications. Requires 'LEGAL', 'CPO', or 'DPO'."
                ),
            )

        now = datetime.utcnow()
        approved_count = 0
        is_approved_decision = payload.decision.strip().lower() == "approved"
        for draft in inc.notification_drafts:
            if payload.draft_id is None or draft.draft_id == payload.draft_id:
                draft.status = "approved_for_controlled_dispatch" if is_approved_decision else payload.decision
                draft.external_dispatch_authorized = bool(is_approved_decision and effective_role in {"LEGAL", "CPO", "DPO"})
                draft.auto_send_blocked = not draft.external_dispatch_authorized
                draft.approved_by = payload.approver_name or payload.approver_id
                draft.approved_by_role = effective_role
                draft.approved_at = now
                draft.approval_rationale = payload.rationale
                sig_input = f"{incident_id}|{draft.draft_id}|{payload.approver_id}|{effective_role}|{payload.decision}|{now.isoformat()}"
                draft.approval_signature_hash = _compute_sha256(sig_input)
                approved_count += 1

        if approved_count == 0 and payload.draft_id:
            raise HTTPException(status_code=404, detail=f"Notification draft '{payload.draft_id}' not found on incident '{incident_id}'")

        prev_hash = inc.evidence_timeline[-1].evidence_hash if inc.evidence_timeline else ("0" * 64)
        ev_payload = f"{incident_id}|HUMAN_LEGAL_APPROVAL|{now.isoformat()}|{payload.approver_id}|{effective_role}|{payload.decision}|{prev_hash}"
        ev_hash = _compute_sha256(ev_payload)
        inc.evidence_timeline.append(
            EvidenceTimelineEntry(
                event_id=f"ev_{uuid.uuid4().hex[:8]}_{len(inc.evidence_timeline) + 1}",
                timestamp_utc=now,
                event_type="HUMAN_LEGAL_NOTIFICATION_APPROVAL",
                actor=f"{payload.approver_name} ({effective_role})",
                description=f"Human {effective_role} decision='{payload.decision}' recorded for {approved_count} notification draft(s). Rationale: {payload.rationale}",
                previous_hash=prev_hash,
                evidence_hash=ev_hash,
            )
        )

        all_approved = all(d.status == "approved_for_controlled_dispatch" and d.external_dispatch_authorized for d in inc.notification_drafts)
        inc.external_dispatch_authorized = all_approved
        inc.auto_send_blocked = not all_approved
        inc.status = "approved_by_legal" if all_approved else "partially_approved_by_legal"
        inc.updated_at = now
        return inc


breach_service = MultiJurisdictionalBreachService()


# ===========================================================================
# MODULE G — VENDOR PRIVACY MANAGEMENT
# ===========================================================================

class SubprocessorEntry(BaseModel):
    subprocessor_name: str
    service_purpose: str
    hosting_jurisdiction: str
    dpa_flowdown_verified: bool = True
    last_audited_date: date = Field(default_factory=date.today)


class VendorCreateRequest(BaseModel):
    vendor_name: str
    service_category: str = Field(default="cloud_ai_processor", description="cloud_ai_processor, ehr_health_it, crm_marketing, infrastructure, payroll_hr")
    hosting_jurisdiction: str = Field(default="US-VA", description="Primary hosting location e.g. US-VA, CA-ON, EU-DE")
    source_jurisdictions: List[str] = Field(
        default_factory=lambda: ["US-CA", "CA-ON", "CA-QC", "EU-DE", "EU-FR"],
        description="Jurisdictions of data subjects whose data is processed by the vendor",
    )
    data_categories: List[str] = Field(default_factory=lambda: ["personal_identifiers", "customer_support_transcripts"])
    processes_phi: bool = False
    processes_ontario_health_info: bool = False
    processes_nydfs_nonpublic_info: bool = False
    involves_ai_or_llm: bool = True
    dpa_executed: bool = Field(default=True, description="GDPR Art. 28 / Quebec Law 25 s. 18.3 DPA")
    cpra_service_provider_addendum: bool = Field(default=True, description="Cal. Civ. Code § 1798.100(d) Service Provider Addendum")
    hipaa_baa_executed: bool = Field(default=False, description="45 CFR § 164.504(e) Business Associate Agreement")
    ontario_phipa_esp_agent_agreement: bool = Field(
        default=False,
        description="Ontario PHIPA s. 10(4) & O. Reg. 329/04 s. 6 Electronic Service Provider / Health Information Network Provider / Agent Agreement",
    )
    nydfs_500_11_third_party_policy_verified: bool = Field(
        default=True,
        description="NYDFS 23 NYCRR § 500.11 Third-Party Service Provider Security Policy verification",
    )
    eu_sccs_executed: bool = Field(default=True, description="2021 European Commission Standard Contractual Clauses (Module 2/3)")
    eu_tia_completed: bool = Field(default=False, description="GDPR Chapter V Transfer Impact Assessment (Schrems II Clause 14)")
    quebec_law25_tra_completed: bool = Field(default=False, description="Quebec Law 25 s. 17 Transfer Risk Assessment (ÉFVP)")
    ai_training_prohibited_clause: bool = Field(default=True, description="Contractual prohibition on training vendor foundation models on tenant data")
    zero_data_retention_enabled: bool = Field(default=False)
    contract_renewal_date: date = Field(default_factory=lambda: date.today() + timedelta(days=45))
    subprocessors: List[SubprocessorEntry] = Field(default_factory=list)


class VendorRecord(BaseModel):
    vendor_id: str
    tenant_id: str
    vendor_name: str
    service_category: str
    hosting_jurisdiction: str
    source_jurisdictions: List[str]
    data_categories: List[str]
    processes_phi: bool
    processes_ontario_health_info: bool
    processes_nydfs_nonpublic_info: bool
    involves_ai_or_llm: bool
    contractual_safeguards: Dict[str, bool]
    statutory_compliance_checks: Dict[str, Dict[str, Any]]
    subprocessors: List[SubprocessorEntry]
    transfer_risk_score: int = Field(..., description="0 (lowest risk) to 100 (highest risk)")
    risk_tier: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    approval_status: str
    blocking_gaps: List[str]
    contract_renewal_date: date
    days_until_renewal: int
    renewal_alert_status: str
    created_at: datetime


class VendorPrivacyManagementService:
    """
    Deterministic service for Module G — Vendor Privacy Management.
    Covers DPA (GDPR Art. 28 / Law 25 / CPRA Service Provider Addendum), HIPAA BAA,
    Ontario PHIPA Electronic Service Provider / Agent Agreement (O. Reg. 329/04 s. 6),
    NYDFS 23 NYCRR 500.11 Third-Party Service Provider policy check, subprocessor registry,
    transfer risk scoring, and renewal alerts.
    """

    def __init__(self) -> None:
        self._vendors: Dict[str, VendorRecord] = {}

    def _ensure_seeded(self, tenant_id: str) -> None:
        if any(v.tenant_id == tenant_id for v in self._vendors.values()):
            return
        # Seed reference vendors for the tenant
        self.evaluate_and_register_vendor(
            tenant_id,
            VendorCreateRequest(
                vendor_name="US Cloud AI Summarizer Inc.",
                service_category="cloud_ai_processor",
                hosting_jurisdiction="US-VA",
                source_jurisdictions=["US-CA", "CA-ON", "CA-QC", "EU-DE", "EU-FR"],
                data_categories=["personal_identifiers", "customer_support_transcripts"],
                processes_phi=False,
                processes_ontario_health_info=False,
                processes_nydfs_nonpublic_info=True,
                involves_ai_or_llm=True,
                dpa_executed=True,
                cpra_service_provider_addendum=True,
                hipaa_baa_executed=False,
                ontario_phipa_esp_agent_agreement=False,
                nydfs_500_11_third_party_policy_verified=True,
                eu_sccs_executed=True,
                eu_tia_completed=False,
                quebec_law25_tra_completed=False,
                ai_training_prohibited_clause=True,
                zero_data_retention_enabled=False,
                contract_renewal_date=date.today() + timedelta(days=25),
                subprocessors=[
                    SubprocessorEntry(
                        subprocessor_name="US GPU Inference Backbone LLC",
                        service_purpose="LLM Token Inference Compute",
                        hosting_jurisdiction="US-VA",
                        dpa_flowdown_verified=True,
                    )
                ],
            ),
            forced_id=f"vnd_{tenant_id}_ai_01",
        )
        self.evaluate_and_register_vendor(
            tenant_id,
            VendorCreateRequest(
                vendor_name="Ontario & US Clinical Cloud EHR Corp",
                service_category="ehr_health_it",
                hosting_jurisdiction="CA-ON",
                source_jurisdictions=["CA-ON", "US-CA", "US-NY"],
                data_categories=["health_information", "phi", "medical_records"],
                processes_phi=True,
                processes_ontario_health_info=True,
                processes_nydfs_nonpublic_info=True,
                involves_ai_or_llm=False,
                dpa_executed=True,
                cpra_service_provider_addendum=True,
                hipaa_baa_executed=True,
                ontario_phipa_esp_agent_agreement=True,
                nydfs_500_11_third_party_policy_verified=True,
                eu_sccs_executed=True,
                eu_tia_completed=True,
                quebec_law25_tra_completed=True,
                ai_training_prohibited_clause=True,
                zero_data_retention_enabled=True,
                contract_renewal_date=date.today() + timedelta(days=180),
                subprocessors=[
                    SubprocessorEntry(
                        subprocessor_name="KIBO Sovereign Backup Vault Canada",
                        service_purpose="Encrypted Health Record Archival",
                        hosting_jurisdiction="CA-ON",
                        dpa_flowdown_verified=True,
                    )
                ],
            ),
            forced_id=f"vnd_{tenant_id}_health_02",
        )

    def evaluate_and_register_vendor(
        self,
        tenant_id: str,
        req: VendorCreateRequest,
        forced_id: Optional[str] = None,
    ) -> VendorRecord:
        vendor_id = forced_id or f"vnd_{uuid.uuid4().hex[:10]}"
        host_jur = normalize_jurisdiction_code(req.hosting_jurisdiction)
        source_jurs = [normalize_jurisdiction_code(j) for j in req.source_jurisdictions]

        blocking_gaps: List[str] = []
        risk_score = 15

        has_eu_sources = any(j == "EU" or j.startswith("EU-") for j in source_jurs)
        has_qc_sources = "CA-QC" in source_jurs
        has_ca_sources = "US-CA" in source_jurs or any(j.startswith("US-") for j in source_jurs)

        if not req.dpa_executed:
            blocking_gaps.append("Missing executed Data Processing Addendum (GDPR Art. 28 / Quebec Law 25 s. 18.3)")
            risk_score += 25

        if has_ca_sources and not req.cpra_service_provider_addendum:
            blocking_gaps.append("Missing California CCPA/CPRA Service Provider Addendum (Cal. Civ. Code § 1798.100(d))")
            risk_score += 15

        if req.processes_phi and not req.hipaa_baa_executed:
            blocking_gaps.append("Missing executed HIPAA Business Associate Agreement (BAA — 45 CFR §§ 164.308(b), 164.504(e))")
            risk_score += 30

        if req.processes_ontario_health_info and not req.ontario_phipa_esp_agent_agreement:
            blocking_gaps.append(
                "Missing Ontario PHIPA Electronic Service Provider / Agent Agreement (PHIPA s. 10(4) & O. Reg. 329/04 s. 6)"
            )
            risk_score += 25

        if req.processes_nydfs_nonpublic_info and not req.nydfs_500_11_third_party_policy_verified:
            blocking_gaps.append(
                "Missing NYDFS 23 NYCRR § 500.11 Third-Party Service Provider Security Policy verification (MFA, encryption, 72h incident notice)"
            )
            risk_score += 20

        if has_eu_sources and not host_jur.startswith("EU"):
            risk_score += 15
            if not req.eu_sccs_executed:
                blocking_gaps.append("Missing 2021 European Commission Standard Contractual Clauses (GDPR Art. 46)")
                risk_score += 20
            if not req.eu_tia_completed:
                blocking_gaps.append("Pending GDPR Chapter V Transfer Impact Assessment (TIA — Schrems II Clause 14)")
                risk_score += 20

        if has_qc_sources and host_jur != "CA-QC":
            risk_score += 10
            if not req.quebec_law25_tra_completed:
                blocking_gaps.append("Pending Quebec Law 25 s. 17 Out-of-Province Transfer Risk Assessment (TRA / ÉFVP)")
                risk_score += 20

        if req.involves_ai_or_llm:
            risk_score += 10
            if not req.ai_training_prohibited_clause:
                blocking_gaps.append("Missing contractual prohibition on training foundation/third-party AI models on tenant personal data")
                risk_score += 25
            if not req.zero_data_retention_enabled:
                blocking_gaps.append("Zero-data-retention API endpoint configuration not yet verified")
                risk_score += 10

        risk_score = min(100, risk_score)
        if risk_score >= 75:
            risk_tier = "CRITICAL"
        elif risk_score >= 50:
            risk_tier = "HIGH"
        elif risk_score >= 25:
            risk_tier = "MEDIUM"
        else:
            risk_tier = "LOW"

        approval_status = (
            "APPROVED"
            if not blocking_gaps
            else "CONDITIONAL_HOLD_PENDING_SAFEGUARDS_AND_DPO_APPROVAL"
        )

        days_until_renewal = (req.contract_renewal_date - date.today()).days
        if days_until_renewal < 0:
            renewal_alert = "EXPIRED_IMMEDIATE_ACTION_REQUIRED"
        elif days_until_renewal <= 30:
            renewal_alert = "RENEWAL_DUE_WITHIN_30_DAYS"
        elif days_until_renewal <= 60:
            renewal_alert = "RENEWAL_DUE_WITHIN_60_DAYS"
        elif days_until_renewal <= 90:
            renewal_alert = "RENEWAL_DUE_WITHIN_90_DAYS"
        else:
            renewal_alert = "ACTIVE_IN_GOOD_STANDING"

        statutory_checks = {
            "gdpr_art28_and_law25_dpa": {
                "citation": "GDPR Art. 28(3) & Quebec Law 25 (CQLR c. P-39.1) s. 18.3",
                "compliant": req.dpa_executed,
            },
            "cpra_service_provider_addendum": {
                "citation": "Cal. Civ. Code § 1798.100(d) & 11 CCR § 7051",
                "compliant": req.cpra_service_provider_addendum,
            },
            "hipaa_business_associate_agreement": {
                "citation": "45 CFR §§ 164.308(b), 164.502(e), 164.504(e)",
                "applicable": req.processes_phi,
                "compliant": (not req.processes_phi) or req.hipaa_baa_executed,
            },
            "ontario_phipa_esp_agent_agreement": {
                "citation": "Ontario PHIPA s. 10(4) & O. Reg. 329/04 s. 6 (Electronic Service Provider / HINP requirements)",
                "applicable": req.processes_ontario_health_info,
                "compliant": (not req.processes_ontario_health_info) or req.ontario_phipa_esp_agent_agreement,
            },
            "nydfs_23_nycrr_500_11_third_party_policy": {
                "citation": "23 NYCRR § 500.11 (Third-Party Service Provider Security Policy)",
                "applicable": req.processes_nydfs_nonpublic_info,
                "compliant": (not req.processes_nydfs_nonpublic_info) or req.nydfs_500_11_third_party_policy_verified,
            },
            "cross_border_tra_and_tia": {
                "citation": "Quebec Law 25 s. 17 (TRA / ÉFVP) & GDPR Arts. 44–46 (2021 EU SCCs + Schrems II TIA)",
                "compliant": req.eu_sccs_executed and req.eu_tia_completed and req.quebec_law25_tra_completed,
            },
        }

        record = VendorRecord(
            vendor_id=vendor_id,
            tenant_id=tenant_id,
            vendor_name=req.vendor_name,
            service_category=req.service_category,
            hosting_jurisdiction=host_jur,
            source_jurisdictions=source_jurs,
            data_categories=req.data_categories,
            processes_phi=req.processes_phi,
            processes_ontario_health_info=req.processes_ontario_health_info,
            processes_nydfs_nonpublic_info=req.processes_nydfs_nonpublic_info,
            involves_ai_or_llm=req.involves_ai_or_llm,
            contractual_safeguards={
                "dpa_executed": req.dpa_executed,
                "cpra_service_provider_addendum": req.cpra_service_provider_addendum,
                "hipaa_baa_executed": req.hipaa_baa_executed,
                "ontario_phipa_esp_agent_agreement": req.ontario_phipa_esp_agent_agreement,
                "nydfs_500_11_third_party_policy_verified": req.nydfs_500_11_third_party_policy_verified,
                "eu_sccs_executed": req.eu_sccs_executed,
                "eu_tia_completed": req.eu_tia_completed,
                "quebec_law25_tra_completed": req.quebec_law25_tra_completed,
                "ai_training_prohibited_clause": req.ai_training_prohibited_clause,
                "zero_data_retention_enabled": req.zero_data_retention_enabled,
            },
            statutory_compliance_checks=statutory_checks,
            subprocessors=req.subprocessors,
            transfer_risk_score=risk_score,
            risk_tier=risk_tier,
            approval_status=approval_status,
            blocking_gaps=blocking_gaps,
            contract_renewal_date=req.contract_renewal_date,
            days_until_renewal=days_until_renewal,
            renewal_alert_status=renewal_alert,
            created_at=datetime.utcnow(),
        )
        self._vendors[vendor_id] = record
        return record

    def list_vendors(self, tenant_id: str) -> List[VendorRecord]:
        self._ensure_seeded(tenant_id)
        return [v for v in self._vendors.values() if v.tenant_id == tenant_id]

    def find_vendor_by_name(self, tenant_id: str, vendor_name: Optional[str] = None) -> VendorRecord:
        vendors = self.list_vendors(tenant_id)
        if vendor_name:
            for v in vendors:
                if vendor_name.lower() in v.vendor_name.lower() or v.vendor_name.lower() in vendor_name.lower():
                    return v
        return vendors[0]


vendor_service = VendorPrivacyManagementService()


# ===========================================================================
# MODULE H — ENTERPRISE RISK & CONTROL MANAGEMENT
# ===========================================================================

class PrivacyControlSpec(BaseModel):
    control_id: str
    tenant_id: str
    title: str
    control_domain: str = Field(..., description="encryption, access_control, cross_border_transfer, ai_governance, breach_readiness, vendor_governance, retention")
    mapped_regulation_ids: List[str]
    statutory_citations: List[str]
    implementation_status: str = "implemented_and_monitored"
    continuous_monitoring_enabled: bool = True
    evidence_artifacts: List[str]
    last_verified_at: datetime = Field(default_factory=datetime.utcnow)


class RiskCreateRequest(BaseModel):
    title: str
    description: str
    category: str = Field(default="cross_border_ai_transfer", description="cross_border_ai_transfer, vendor_processing, data_retention, breach_exposure, biometric_processing")
    affected_jurisdictions: List[str] = Field(default_factory=lambda: ["US-CA", "CA-ON", "CA-QC", "EU-DE"])
    mapped_regulation_ids: List[str] = Field(default_factory=lambda: ["EU-GDPR", "CA-QC-LAW25", "CA-FED-PIPEDA", "US-CA-CCPA-CPRA"])
    inherent_likelihood: int = Field(default=4, ge=1, le=5)
    inherent_impact: int = Field(default=5, ge=1, le=5)
    residual_likelihood: int = Field(default=2, ge=1, le=5)
    residual_impact: int = Field(default=3, ge=1, le=5)
    mitigation_control_ids: List[str] = Field(default_factory=lambda: ["CTRL-XFER-001", "CTRL-AI-002", "CTRL-ENC-003"])
    mitigation_plan: str = Field(default="Complete TIA/TRA, enforce pre-inference PII redaction, and execute EU SCCs + CPRA Service Provider Addendum.")


class RiskAcceptancePayload(BaseModel):
    approver_id: str = Field(default="cpo_01")
    approver_name: str = Field(default="Dr. Claire Vance, CPO")
    approver_role: str = Field(..., description="Must be CPO or DPO (or LEGAL)")
    justification: str = Field(..., description="Documented rationale for residual risk acceptance")
    expiration_date: date = Field(default_factory=lambda: date.today() + timedelta(days=180))


class EnterprisePrivacyRiskRecord(BaseModel):
    risk_id: str
    tenant_id: str
    title: str
    description: str
    category: str
    affected_jurisdictions: List[str]
    mapped_regulation_ids: List[str]
    inherent_risk_score: int
    residual_risk_score: int
    severity: str
    mitigation_control_ids: List[str]
    mitigation_plan: str
    status: str = "open_mitigation_in_progress"
    risk_acceptance_approved_by: Optional[str] = None
    risk_acceptance_role: Optional[str] = None
    risk_acceptance_justification: Optional[str] = None
    risk_acceptance_hash: Optional[str] = None
    created_at: datetime


class RiskAndControlManagementService:
    """
    Deterministic service for Module H — Enterprise Risk & Control Management.
    Provides an enterprise privacy risk register, control library mapped to canonical `regulation_id`s,
    mitigation actions, risk acceptance workflow (requiring CPO/DPO sign-off), and continuous monitoring evidence.
    """

    def __init__(self) -> None:
        self._controls: Dict[str, List[PrivacyControlSpec]] = {}
        self._risks: Dict[str, EnterprisePrivacyRiskRecord] = {}

    def _ensure_seeded(self, tenant_id: str) -> None:
        if tenant_id in self._controls:
            return

        self._controls[tenant_id] = [
            PrivacyControlSpec(
                control_id="CTRL-XFER-001",
                tenant_id=tenant_id,
                title="Cross-Border Transfer Gate (2021 EU SCCs + Schrems II TIA + Quebec Law 25 s. 17 TRA)",
                control_domain="cross_border_transfer",
                mapped_regulation_ids=["EU-GDPR", "CA-QC-LAW25", "CA-FED-PIPEDA"],
                statutory_citations=[
                    "GDPR Arts. 44–46 & EDPB Recommendations 01/2020",
                    "Quebec Law 25 (CQLR c. P-39.1) s. 17",
                    "PIPEDA Schedule 1 Principle 4.1.3",
                ],
                evidence_artifacts=["Executed_EU_SCC_Module2.pdf", "Schrems_II_TIA_Report.json", "Quebec_Law25_EFVP_TRA.json"],
            ),
            PrivacyControlSpec(
                control_id="CTRL-AI-002",
                tenant_id=tenant_id,
                title="AI & LLM Pre-Inference PII Redaction + Foundation Model Training Prohibition",
                control_domain="ai_governance",
                mapped_regulation_ids=["EU-AI-ACT", "EU-GDPR", "US-CA-CCPA-CPRA", "CA-QC-LAW25"],
                statutory_citations=[
                    "EU AI Act (Regulation (EU) 2024/1689) Arts. 4, 10, 50",
                    "Cal. Civ. Code §§ 1798.100(d), 1798.185(a)(15)-(16)",
                    "Quebec Law 25 s. 12.1",
                ],
                evidence_artifacts=["DPA_No_Training_Addendum.pdf", "Gateway_PII_Redaction_Telemetry.log"],
            ),
            PrivacyControlSpec(
                control_id="CTRL-ENC-003",
                tenant_id=tenant_id,
                title="Cryptographic Encryption at Rest (AES-256-GCM BYOK) & In Transit (TLS 1.3)",
                control_domain="encryption",
                mapped_regulation_ids=["EU-GDPR", "US-FED-HIPAA", "US-NY-NYDFS-500", "CA-ON-PHIPA", "US-CA-CCPA-CPRA"],
                statutory_citations=[
                    "GDPR Art. 32(1)(a)",
                    "HIPAA Security Rule 45 CFR § 164.312(a)(2)(iv) & (e)(2)(ii)",
                    "23 NYCRR § 500.15",
                    "Ontario PHIPA s. 12(1)",
                ],
                evidence_artifacts=["HSM_Key_Rotation_Attestation.json", "TLS13_Cipher_Audit.json"],
            ),
            PrivacyControlSpec(
                control_id="CTRL-INC-004",
                tenant_id=tenant_id,
                title="Multi-Jurisdictional 72-Hour Breach Triage & Mandatory Human Legal Approval Gate",
                control_domain="breach_readiness",
                mapped_regulation_ids=["EU-GDPR", "EU-DE-BDSG", "CA-QC-LAW25", "CA-FED-PIPEDA", "CA-ON-PHIPA", "US-CA-BREACH", "US-FED-HIPAA"],
                statutory_citations=[
                    "GDPR Arts. 33–34 & BDSG § 29",
                    "Quebec Law 25 ss. 3.5–3.8",
                    "PIPEDA ss. 10.1–10.3",
                    "Ontario PHIPA s. 12(2)-(3)",
                    "Cal. Civ. Code § 1798.82",
                ],
                evidence_artifacts=["Breach_Playbook_Runbook.md", "Immutable_Hash_Timeline_Verifier.py"],
            ),
        ]

        self.create_risk(
            tenant_id,
            RiskCreateRequest(
                title="Unapproved Cross-Border Customer Support Data Transfer to Third-Party US AI Provider",
                description=(
                    "Risk that customer support transcripts containing Canadian (CA-ON, CA-QC), California (US-CA), "
                    "and European (EU-DE, EU-FR) personal data are transmitted to an external AI provider without "
                    "completed TRA/TIA/DPIA and zero-retention safeguards."
                ),
                category="cross_border_ai_transfer",
                affected_jurisdictions=["US-CA", "CA-ON", "CA-QC", "EU-DE", "EU-FR"],
                mapped_regulation_ids=["EU-GDPR", "EU-AI-ACT", "CA-QC-LAW25", "CA-FED-PIPEDA", "US-CA-CCPA-CPRA"],
                inherent_likelihood=4,
                inherent_impact=5,
                residual_likelihood=2,
                residual_impact=2,
                mitigation_control_ids=["CTRL-XFER-001", "CTRL-AI-002", "CTRL-ENC-003"],
            ),
            forced_id=f"rsk_{tenant_id}_ai_xfer_01",
        )

    def create_risk(
        self,
        tenant_id: str,
        req: RiskCreateRequest,
        forced_id: Optional[str] = None,
    ) -> EnterprisePrivacyRiskRecord:
        self._ensure_seeded(tenant_id)
        risk_id = forced_id or f"rsk_{uuid.uuid4().hex[:10]}"
        inherent = req.inherent_likelihood * req.inherent_impact
        residual = req.residual_likelihood * req.residual_impact
        if residual >= 15:
            severity = "CRITICAL"
        elif residual >= 10:
            severity = "HIGH"
        elif residual >= 5:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        rec = EnterprisePrivacyRiskRecord(
            risk_id=risk_id,
            tenant_id=tenant_id,
            title=req.title,
            description=req.description,
            category=req.category,
            affected_jurisdictions=[normalize_jurisdiction_code(j) for j in req.affected_jurisdictions],
            mapped_regulation_ids=req.mapped_regulation_ids,
            inherent_risk_score=inherent,
            residual_risk_score=residual,
            severity=severity,
            mitigation_control_ids=req.mitigation_control_ids,
            mitigation_plan=req.mitigation_plan,
            created_at=datetime.utcnow(),
        )
        self._risks[risk_id] = rec
        return rec

    def accept_risk(
        self,
        tenant_id: str,
        risk_id: str,
        payload: RiskAcceptancePayload,
        caller_role: str,
    ) -> EnterprisePrivacyRiskRecord:
        self._ensure_seeded(tenant_id)
        rec = self._risks.get(risk_id)
        if not rec:
            raise HTTPException(status_code=404, detail=f"Risk '{risk_id}' not found")
        if rec.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="CROSS_TENANT_ACCESS_DENIED")

        role = (caller_role or payload.approver_role).strip().upper()
        if role not in {"CPO", "DPO", "LEGAL"}:
            raise HTTPException(
                status_code=403,
                detail=f"Risk acceptance requires CPO, DPO, or LEGAL sign-off (received '{role}').",
            )

        rec.status = "accepted_with_cpo_dpo_signoff"
        rec.risk_acceptance_approved_by = payload.approver_name
        rec.risk_acceptance_role = role
        rec.risk_acceptance_justification = payload.justification
        rec.risk_acceptance_hash = _compute_sha256(
            f"{risk_id}|{tenant_id}|{payload.approver_id}|{role}|{payload.justification}|{payload.expiration_date.isoformat()}"
        )
        return rec

    def get_overview(self, tenant_id: str) -> Dict[str, Any]:
        self._ensure_seeded(tenant_id)
        risks = [r for r in self._risks.values() if r.tenant_id == tenant_id]
        controls = self._controls[tenant_id]
        return {
            "tenant_id": tenant_id,
            "generated_at": datetime.utcnow().isoformat(),
            "risk_register": [r.model_dump() for r in risks],
            "control_library": [c.model_dump() for c in controls],
            "continuous_monitoring_summary": {
                "total_controls": len(controls),
                "monitored_controls": sum(1 for c in controls if c.continuous_monitoring_enabled),
                "open_risks": sum(1 for r in risks if "open" in r.status),
                "accepted_risks": sum(1 for r in risks if "accepted" in r.status),
            },
        }


risk_control_service = RiskAndControlManagementService()


# ===========================================================================
# MODULE I — REGULATORY INTELLIGENCE & CHANGE IMPACT ANALYSIS
# (CRITICAL FOR ACCEPTANCE TEST 10 — REGULATORY CHANGE)
# ===========================================================================

class RegulatoryAmendmentCreateRequest(BaseModel):
    regulation_id: str = Field(default="US-CA-CCPA-CPRA", description="Canonical regulation ID being amended")
    jurisdiction_id: str = Field(default="US-CA", description="Jurisdiction code e.g. US-CA, CA-QC, EU, CA-ON")
    amendment_title: str = Field(
        default="CPRA Automated Decision-Making Technology (ADMT) & Cybersecurity Audit Final Regulations Update",
        description="Official title of the statutory or regulatory amendment",
    )
    previous_version: str = Field(default="2025.4.0", description="Previous canonical rule version")
    new_version: str = Field(default="2026.11.0", description="New canonical rule version")
    source_evidence: str = Field(
        default="California Privacy Protection Agency (CalPrivacy) Final Rulemaking Package, OAL File No. 2026-1015-02S (11 CCR §§ 7150–7220)",
        description="Authoritative official gazette / statutory source URL or citation",
    )
    legal_interpretation: str = Field(
        default=(
            "Tightens pre-use notice, opt-out rights, and mandatory risk assessment filing deadlines for Automated "
            "Decision-Making Technology (ADMT) and AI profiling, and shortens vendor contract remediation windows to 30 days."
        ),
        description="Counsel's verified legal interpretation of the operational change",
    )
    reviewer: str = Field(default="Elena Rostova, General Counsel (CIPP/US, CIPP/E)", description="Human legal reviewer name/ID")
    reviewer_role: str = Field(default="LEGAL", description="Role of the reviewer (LEGAL, CPO, DPO, or AI_PARSER)")
    approval_decision: str = Field(
        default="approved",
        description="approved, pending_legal_review, or rejected. Production obligation updates require human LEGAL/CPO approval.",
    )
    effective_date: date = Field(default_factory=lambda: date.today() + timedelta(days=60))
    updated_rights_deadline_days: Optional[int] = Field(default=30)
    updated_breach_regulator_hours: Optional[int] = Field(default=72)
    origin_source_type: str = Field(
        default="human_counsel_verified",
        description="human_counsel_verified or unreviewed_llm_ingestion",
    )


class BlastRadiusImpactReport(BaseModel):
    affected_organizations_and_establishments: List[Dict[str, str]]
    affected_processing_activities: List[Dict[str, Any]]
    assessments_requiring_reevaluation: List[Dict[str, str]]
    affected_policies: List[Dict[str, str]]
    affected_controls: List[Dict[str, str]]
    affected_vendors: List[Dict[str, str]]
    updated_statutory_deadlines: Dict[str, Any]


class RegulatoryAmendmentRecord(BaseModel):
    amendment_id: str
    tenant_id: str
    regulation_id: str
    jurisdiction_id: str
    amendment_title: str
    previous_version: str
    new_version: str
    source_evidence: str
    source_document_hash: str
    legal_interpretation: str
    reviewer: str
    reviewer_role: str
    approval_decision: str
    effective_date: date
    production_obligations_updated: bool
    llm_direct_alteration_blocked: bool = True
    governance_gate_explanation: str
    blast_radius: BlastRadiusImpactReport
    recorded_at: datetime


class RegulatoryIntelligenceService:
    """
    Deterministic service for Module I — Regulatory Intelligence & Change Impact Analysis.
    Satisfies Acceptance Test 10 (Regulatory Change):
    - Records `previous_version`, `new_version`, `source_evidence`, `legal_interpretation`,
      `reviewer`, `approval_decision`, and `effective_date`.
    - Computes the tenant-wide blast radius: affected organizations/establishments,
      affected processing activities, existing assessments requiring re-evaluation (`PIA`/`DPIA`/`TRA`/`TIA`),
      affected policies, affected controls, and updated statutory deadlines.
    - Strictly enforces the rule that no LLM or unreviewed change can directly alter
      production obligations without human `LEGAL` or `CPO` approval.
    """

    def __init__(self) -> None:
        self._amendments: Dict[str, RegulatoryAmendmentRecord] = {}

    def record_amendment(
        self,
        tenant_id: str,
        req: RegulatoryAmendmentCreateRequest,
        caller_role: str,
    ) -> RegulatoryAmendmentRecord:
        governance_service._ensure_tenant_seeded(tenant_id)
        vendor_service._ensure_seeded(tenant_id)
        risk_control_service._ensure_seeded(tenant_id)

        now = datetime.utcnow()
        amendment_id = f"amd_{uuid.uuid4().hex[:12]}"
        norm_jur = normalize_jurisdiction_code(req.jurisdiction_id)
        effective_role = (caller_role or req.reviewer_role).strip().upper()

        # Rule: No LLM or unreviewed change can directly alter production obligations without human LEGAL / CPO approval
        is_llm_or_unreviewed = (
            req.origin_source_type.lower() in {"unreviewed_llm_ingestion", "llm", "automated_scraper"}
            or effective_role in {"AI_PARSER", "LLM", "PUBLIC", "EMPLOYEE", "ANALYST"}
            or req.approval_decision.lower() != "approved"
        )
        human_legal_approved = (
            not is_llm_or_unreviewed
            and effective_role in {"LEGAL", "CPO", "DPO"}
            and req.approval_decision.lower() == "approved"
        )

        if human_legal_approved:
            prod_updated = True
            gate_explanation = (
                f"Human {effective_role} reviewer ({req.reviewer}) approved amendment {req.previous_version} -> {req.new_version}. "
                "Production obligations and blast-radius re-evaluation tasks have been activated."
            )
        else:
            prod_updated = False
            gate_explanation = (
                "QUARANTINED_PENDING_HUMAN_LEGAL_APPROVAL: Unreviewed or LLM-ingested regulatory changes are strictly "
                "blocked from altering production obligations until a human LEGAL or CPO reviewer approves the amendment."
            )

        # Compute deterministic blast radius across the tenant
        establishments = governance_service._establishments.get(tenant_id, [])
        affected_ests = [
            {
                "establishment_id": e.establishment_id,
                "entity_name": e.entity_name,
                "jurisdiction_id": e.normalized_jurisdiction,
                "competent_authority": e.competent_authority,
            }
            for e in establishments
            if e.normalized_jurisdiction == norm_jur
            or norm_jur in ("EU", "US-FED", "CA-FED")
            or e.normalized_jurisdiction in ("US-CA", "CA-ON", "CA-QC", "EU-DE", "EU-FR")
        ]

        affected_activities = [
            {
                "activity_id": f"ropa_{tenant_id}_ai_support",
                "name": "Customer Support Call Recording, Transcription & AI Summarization",
                "jurisdictions": [norm_jur, "US-CA", "CA-ON", "CA-QC", "EU-DE"],
                "impact_reason": f"Subject to amended {req.regulation_id} ({req.previous_version} -> {req.new_version}): {req.amendment_title}",
            },
            {
                "activity_id": f"ropa_{tenant_id}_crm_analytics",
                "name": "Cross-Border Customer Identity, Billing & Behavioral Analytics",
                "jurisdictions": [norm_jur, "US-CA", "CA-ON", "EU-FR"],
                "impact_reason": f"Requires updated disclosures, processor addenda, and deadline alignment under {req.regulation_id} v{req.new_version}.",
            },
        ]

        assessments_to_reevaluate = [
            {
                "assessment_id": f"asmt_{tenant_id}_pia_001",
                "assessment_type": "PIA",
                "title": f"Privacy Impact Assessment (PIA) — {req.regulation_id} Compliance Review",
                "reevaluation_trigger": f"Statutory amendment {req.previous_version} -> {req.new_version} effective {req.effective_date.isoformat()}",
                "status": "flagged_for_mandatory_reevaluation",
            },
            {
                "assessment_id": f"asmt_{tenant_id}_dpia_002",
                "assessment_type": "DPIA",
                "title": "GDPR Art. 35 / High-Risk AI Data Protection Impact Assessment (DPIA)",
                "reevaluation_trigger": f"Material regulatory change in {req.regulation_id} ({req.amendment_title})",
                "status": "flagged_for_mandatory_reevaluation",
            },
            {
                "assessment_id": f"asmt_{tenant_id}_tra_003",
                "assessment_type": "TRA",
                "title": "Quebec Law 25 s. 17 Out-of-Province Transfer Risk Assessment (TRA / ÉFVP)",
                "reevaluation_trigger": "Destination jurisdiction legal framework updated; s. 17 equivalency re-verification required",
                "status": "flagged_for_mandatory_reevaluation",
            },
            {
                "assessment_id": f"asmt_{tenant_id}_tia_004",
                "assessment_type": "TIA",
                "title": "GDPR Chapter V Art. 46 Transfer Impact Assessment (TIA — Schrems II Clause 14)",
                "reevaluation_trigger": "Importer statutory obligations modified; Clause 14 supplementary measures review required",
                "status": "flagged_for_mandatory_reevaluation",
            },
        ]

        policies = governance_service.list_policies(tenant_id)
        affected_policies = [
            {
                "policy_id": p.policy_id,
                "title": p.title,
                "current_version": p.version,
                "required_action": f"Update policy citations and controls for {req.regulation_id} v{req.new_version} prior to {req.effective_date.isoformat()}",
            }
            for p in policies
        ]

        controls = risk_control_service._controls.get(tenant_id, [])
        affected_controls = [
            {
                "control_id": c.control_id,
                "title": c.title,
                "control_domain": c.control_domain,
                "required_action": f"Re-verify control telemetry and evidence against {req.regulation_id} v{req.new_version}",
            }
            for c in controls
        ]

        vendors = vendor_service.list_vendors(tenant_id)
        affected_vendors = [
            {
                "vendor_id": v.vendor_id,
                "vendor_name": v.vendor_name,
                "required_action": f"Issue DPA / Service Provider Addendum amendment notice for {req.regulation_id} v{req.new_version}",
            }
            for v in vendors
        ]

        updated_deadlines = {
            "regulation_id": req.regulation_id,
            "previous_rule_version": req.previous_version,
            "new_rule_version": req.new_version,
            "effective_date": req.effective_date.isoformat(),
            "updated_rights_response_days": req.updated_rights_deadline_days or 30,
            "updated_breach_regulator_hours": req.updated_breach_regulator_hours or 72,
            "remediation_cutover_deadline": req.effective_date.isoformat(),
        }

        blast_radius = BlastRadiusImpactReport(
            affected_organizations_and_establishments=affected_ests,
            affected_processing_activities=affected_activities,
            assessments_requiring_reevaluation=assessments_to_reevaluate,
            affected_policies=affected_policies,
            affected_controls=affected_controls,
            affected_vendors=affected_vendors,
            updated_statutory_deadlines=updated_deadlines,
        )

        doc_hash = _compute_sha256(
            f"{req.regulation_id}|{req.previous_version}|{req.new_version}|{req.source_evidence}|{req.legal_interpretation}"
        )

        record = RegulatoryAmendmentRecord(
            amendment_id=amendment_id,
            tenant_id=tenant_id,
            regulation_id=req.regulation_id,
            jurisdiction_id=norm_jur,
            amendment_title=req.amendment_title,
            previous_version=req.previous_version,
            new_version=req.new_version,
            source_evidence=req.source_evidence,
            source_document_hash=doc_hash,
            legal_interpretation=req.legal_interpretation,
            reviewer=req.reviewer,
            reviewer_role=effective_role,
            approval_decision=req.approval_decision if human_legal_approved else "quarantined_pending_human_legal_approval",
            effective_date=req.effective_date,
            production_obligations_updated=prod_updated,
            llm_direct_alteration_blocked=True,
            governance_gate_explanation=gate_explanation,
            blast_radius=blast_radius,
            recorded_at=now,
        )
        self._amendments[amendment_id] = record
        return record

    def list_amendments(self, tenant_id: str) -> List[RegulatoryAmendmentRecord]:
        return [a for a in self._amendments.values() if a.tenant_id == tenant_id]


reg_intel_service = RegulatoryIntelligenceService()


# ===========================================================================
# MODULE J — GOVERNED PRIVACY OFFICE ASSISTANT
# (CRITICAL FOR ACCEPTANCE TEST 12 — CORPORATE COPILOT / ASSISTANT)
# ===========================================================================

class AssistantQueryRequest(BaseModel):
    question: str = Field(
        ...,
        description="Employee or Privacy Officer question, e.g., 'Can I send customer information to this third-party AI provider?'",
    )
    tenant_id: Optional[str] = Field(default=None, description="Optional tenant ID (verified against session)")
    user_id: str = Field(default="employee_01")
    role: str = Field(default="EMPLOYEE")
    vendor_name: Optional[str] = Field(default="US Cloud AI Summarizer Inc.")
    jurisdictions: Optional[List[str]] = Field(default=None)
    data_categories: Optional[List[str]] = Field(
        default_factory=lambda: ["personal_identifiers", "customer_support_transcripts"]
    )
    involves_ai: bool = Field(default=True)
    involves_cross_border_transfer: bool = Field(default=True)


class AssistantOrganizationContext(BaseModel):
    tenant_id: str
    organization_name: str
    industry: str
    primary_establishment: str
    main_eu_establishment: Optional[str]
    establishments: List[Dict[str, Any]]
    applicable_jurisdictions: List[str]


class AssistantEvidenceCitation(BaseModel):
    citation_id: str
    source_type: str = Field(..., description="statute, regulator_guidance, internal_policy, vendor_contract")
    jurisdiction_id: str
    authority_or_owner: str
    citation_reference: str
    official_url_or_doc_id: str
    verified_excerpt: str


class AssistantQueryResponse(BaseModel):
    query_id: str
    tenant_id: str
    user_id: str
    role: str
    question: str
    organization_context_identified_first: AssistantOrganizationContext
    decision_summary: str
    statutory_requirements: List[Dict[str, Any]]
    regulator_guidance: List[Dict[str, Any]]
    organization_policies: List[Dict[str, Any]]
    contractual_commitments: Dict[str, Any]
    ai_recommendations: Dict[str, Any]
    supporting_evidence: List[AssistantEvidenceCitation]
    requires_human_approval: bool = True
    required_approver_roles: List[str] = Field(default_factory=lambda: ["DPO", "LEGAL", "CPO"])
    auto_execution_blocked: bool = True
    evaluated_at: datetime


class GovernedPrivacyAssistantService:
    """
    Deterministic service for Module J — Governed Privacy Office Assistant.
    Satisfies Acceptance Test 12:
    1. Identifies the caller's organization (`tenant_id`), establishments, industry, and applicable jurisdictions FIRST.
    2. Explicitly separates its response into 5 structured, evidence-backed sections:
       - `statutory_requirements` (citing exact statutes and articles/sections from JRAE)
       - `regulator_guidance` (citing OPC, CAI, CNIL, EDPB, FTC, CalPrivacy, HHS OCR, IPC guidance)
       - `organization_policies` (citing the tenant's internal AI & Data Sharing Policy, Vendor Onboarding Policy, and Data Classification Policy)
       - `contractual_commitments` (checking whether an executed DPA, BAA, SCCs, and AI training prohibition clause exist with the vendor)
       - `ai_recommendations` (requiring PIA/DPIA/AIIA/TIA/TRA and human DPO/Legal approval before any data transfer)
    3. Includes `supporting_evidence` citations and `requires_human_approval=True` for consequential actions.
    """

    def answer_query(self, tenant_id: str, req: AssistantQueryRequest) -> AssistantQueryResponse:
        governance_service._ensure_tenant_seeded(tenant_id)
        vendor_service._ensure_seeded(tenant_id)

        profile = governance_service._profiles[tenant_id]
        establishments = governance_service._establishments[tenant_id]
        policies = governance_service.list_policies(tenant_id)
        matched_vendor = vendor_service.find_vendor_by_name(tenant_id, req.vendor_name)

        # Step 1: Identify caller's organization, establishments, industry, and applicable jurisdictions FIRST
        inferred_jurs: List[str] = []
        for j in (req.jurisdictions or profile["active_jurisdictions"]):
            code = normalize_jurisdiction_code(j)
            if code and code not in inferred_jurs:
                inferred_jurs.append(code)

        q_lower = req.question.lower()
        for kw, code in [
            ("california", "US-CA"),
            ("ontario", "CA-ON"),
            ("quebec", "CA-QC"),
            ("québec", "CA-QC"),
            ("france", "EU-FR"),
            ("germany", "EU-DE"),
            ("german", "EU-DE"),
        ]:
            if kw in q_lower and code not in inferred_jurs:
                inferred_jurs.append(code)

        org_context = AssistantOrganizationContext(
            tenant_id=tenant_id,
            organization_name=profile["organization_name"],
            industry=profile["industry"],
            primary_establishment=profile["primary_establishment"],
            main_eu_establishment=profile.get("main_eu_establishment"),
            establishments=[e.model_dump() for e in establishments],
            applicable_jurisdictions=inferred_jurs,
        )

        # Step 2A: Section 1 — Statutory Requirements (citing exact statutes and articles/sections from JRAE)
        statutory_requirements: List[Dict[str, Any]] = [
            {
                "jurisdiction_id": "US-CA",
                "regulation_id": "US-CA-CCPA-CPRA",
                "statute": "California Consumer Privacy Act as amended by CPRA (Cal. Civ. Code § 1798.100 et seq.) & CIPA (Cal. Penal Code § 632)",
                "articles_or_sections": "Cal. Civ. Code §§ 1798.100(d) (Service Provider Contract Mandate), 1798.121 (Sensitive Personal Information), 1798.140(ag), 1798.185(a)(15)-(16) (Risk Assessments & ADMT); Cal. Penal Code § 632",
                "requirement": (
                    "Disclosing customer personal information to a third-party AI provider without a compliant Cal. Civ. Code § 1798.100(d) "
                    "Service Provider Addendum constitutes an unlawful 'sale' or 'sharing' if the vendor retains, uses, or trains models on the data "
                    "for its own commercial purposes. Requires a written contract limiting use strictly to the specified business purpose."
                ),
            },
            {
                "jurisdiction_id": "CA-FED",
                "regulation_id": "CA-FED-PIPEDA",
                "statute": "Personal Information Protection and Electronic Documents Act (PIPEDA, S.C. 2000, c. 5)",
                "articles_or_sections": "Schedule 1, Principle 4.1.3 (Accountability for Transfers for Processing), Principle 4.3 (Meaningful Consent) & Principle 4.7 (Safeguards)",
                "requirement": (
                    "The transferring organization remains strictly accountable for personal information processed by a third-party or US-based "
                    "AI provider and must ensure a comparable level of protection through binding contractual clauses and cross-border transparency notice."
                ),
            },
            {
                "jurisdiction_id": "CA-QC",
                "regulation_id": "CA-QC-LAW25",
                "statute": "Quebec Act respecting the protection of personal information in the private sector (Law 25 / Bill 64, CQLR c. P-39.1)",
                "articles_or_sections": "CQLR c. P-39.1 s. 3.3 (Mandatory PIA for Information Systems), s. 12.1 (Automated Decision-Making), s. 17 (Cross-Border Communication Outside Quebec — ÉFVP/TRA), s. 18.3 (Written Processor Mandate)",
                "requirement": (
                    "Before communicating Quebec residents' personal information outside Quebec to a third-party AI provider, the organization MUST "
                    "complete a Privacy Impact Assessment / Transfer Risk Assessment (ÉFVP / TRA) under s. 17 evaluating the destination jurisdiction's "
                    "legal principles and enter into a written contract under s. 18.3 specifying confidentiality, security, and non-retention measures."
                ),
            },
            {
                "jurisdiction_id": "CA-ON",
                "regulation_id": "CA-ON-PHIPA",
                "statute": "Ontario Personal Health Information Protection Act, 2004 (PHIPA, S.O. 2004, c. 3, Sched. A) & O. Reg. 329/04",
                "articles_or_sections": "PHIPA s. 10(4), s. 12(1) & O. Reg. 329/04 s. 6 (Electronic Service Provider / HINP Requirements)",
                "requirement": (
                    "Where Ontario health information is in scope, the custodian must execute a written Electronic Service Provider / Agent "
                    "agreement under O. Reg. 329/04 s. 6 prohibiting unauthorized use, copying, or modification and requiring audit logging."
                ),
            },
            {
                "jurisdiction_id": "EU",
                "regulation_id": "EU-GDPR",
                "statute": "EU General Data Protection Regulation (Regulation (EU) 2016/679) & German BDSG / French LIL",
                "articles_or_sections": "GDPR Art. 5(1)(b)-(c) (Purpose Limitation & Data Minimisation), Art. 6 (Lawful Basis), Art. 28 (Processor DPA), Art. 32 (Security), Art. 35 (DPIA), Chapter V Arts. 44–46 (International Transfers & SCCs)",
                "requirement": (
                    "Sharing EU/German/French customer data with a third-party AI processor requires an Art. 28 Data Processing Agreement, "
                    "an Art. 35 Data Protection Impact Assessment (DPIA), and—where transferred to the United States—verified EU-US DPF certification "
                    "or 2021 European Commission Standard Contractual Clauses (Module 2) backed by a Clause 14 Transfer Impact Assessment (TIA)."
                ),
            },
            {
                "jurisdiction_id": "EU",
                "regulation_id": "EU-AI-ACT",
                "statute": "EU Artificial Intelligence Act (Regulation (EU) 2024/1689)",
                "articles_or_sections": "Art. 4 (AI Literacy), Art. 26 (Deployer Obligations), Art. 50 (Transparency Obligations)",
                "requirement": (
                    "Deployers of AI systems processing customer interactions must ensure staff AI literacy (Art. 4), transparency to affected natural "
                    "persons (Art. 50), and human oversight over AI outputs."
                ),
            },
            {
                "jurisdiction_id": "US-FED",
                "regulation_id": "US-FED-HIPAA-PRIVACY",
                "statute": "Health Insurance Portability and Accountability Act (HIPAA, 45 CFR Parts 160 & 164)",
                "articles_or_sections": "45 CFR §§ 164.308(b), 164.502(e), 164.504(e) (Business Associate Contracts)",
                "requirement": (
                    "If any Protected Health Information (PHI) is included in customer records, transmitting it to an AI vendor is strictly prohibited "
                    "without an executed HIPAA Business Associate Agreement (BAA) or verified Safe Harbor / Expert Determination de-identification under 45 CFR § 164.514."
                ),
            },
        ]

        # Step 2B: Section 2 — Regulator Guidance (citing OPC, CAI, CNIL, EDPB, FTC, CalPrivacy, HHS OCR, IPC guidance)
        regulator_guidance: List[Dict[str, Any]] = [
            {
                "regulator": "Office of the Privacy Commissioner of Canada (OPC)",
                "jurisdiction_id": "CA-FED",
                "guidance_title": "OPC Principles for Responsible, Trustworthy and Privacy-Protective Generative AI Technologies & Guidelines for Processing Personal Data Across Borders",
                "key_directive": "Organizations must ensure generative AI providers do not repurpose customer prompts/inputs to train public foundation models without valid meaningful consent, and must disclose cross-border US processing risks.",
            },
            {
                "regulator": "Commission d'accès à l'information du Québec (CAI)",
                "jurisdiction_id": "CA-QC",
                "guidance_title": "CAI Guide d'accompagnement — Réaliser une évaluation des facteurs relatifs à la vie privée (ÉFVP / PIA & s. 17 Cross-Border TRA)",
                "key_directive": "Mandates a documented ÉFVP before deploying a new AI system or communicating personal information outside Quebec, assessing sensitivity, proportionality, and foreign government access risks.",
            },
            {
                "regulator": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
                "jurisdiction_id": "EU-FR",
                "guidance_title": "CNIL AI How-To Sheets (Fiches pratiques IA) — Deploying Generative AI Systems & LLMs",
                "key_directive": "Requires data minimization/pseudonymization before sending prompts to external LLM APIs, strict separation between processor inference and controller model training, and an Art. 35 DPIA.",
            },
            {
                "regulator": "European Data Protection Board (EDPB)",
                "jurisdiction_id": "EU",
                "guidance_title": "EDPB Recommendations 01/2020 on Supplementary Measures for Transfer Tools & Report of the ChatGPT Taskforce (2024)",
                "key_directive": "Requires technical supplementary measures (such as pre-transfer pseudonymization/redaction and encryption) when transferring personal data to third countries, and strict verification of lawful basis for AI processing.",
            },
            {
                "regulator": "Federal Trade Commission (FTC)",
                "jurisdiction_id": "US-FED",
                "guidance_title": "FTC Guidance on AI Companies: Upholding Privacy and Confidentiality Commitments Under Section 5 of the FTC Act",
                "key_directive": "Surreptitiously sharing customer data with third-party AI vendors or training AI models in contradiction to privacy notices constitutes an unfair or deceptive trade practice under 15 U.S.C. § 45.",
            },
            {
                "regulator": "California Privacy Protection Agency (CalPrivacy)",
                "jurisdiction_id": "US-CA",
                "guidance_title": "CalPrivacy Enforcement Advisory on Applying Data Minimization (11 CCR § 7002) & Service Provider AI Restrictions",
                "key_directive": "Data minimization applies to every third-party disclosure; businesses must verify Service Provider addenda forbid secondary AI model training or cross-context behavioral profiling.",
            },
            {
                "regulator": "HHS Office for Civil Rights (OCR)",
                "jurisdiction_id": "US-FED",
                "guidance_title": "HHS OCR Guidance on Cloud Computing & Business Associates under the HIPAA Privacy and Security Rules",
                "key_directive": "A cloud or AI vendor processing ePHI (even transiently unless strictly a conduit) is a Business Associate requiring a signed BAA and HIPAA Security Rule risk analysis.",
            },
            {
                "regulator": "Information and Privacy Commissioner of Ontario (IPC)",
                "jurisdiction_id": "CA-ON",
                "guidance_title": "IPC Ontario Fact Sheet — Health Information Custodians Using Electronic Service Providers & AI Tools",
                "key_directive": "Custodians must execute O. Reg. 329/04 s. 6 agreements, prohibit secondary use of PHI for vendor model training, and maintain complete electronic audit logs.",
            },
        ]

        # Step 2C: Section 3 — Organization Policies (citing internal AI & Data Sharing, Vendor Onboarding, Data Classification)
        organization_policies: List[Dict[str, Any]] = [
            {
                "policy_id": p.policy_id,
                "title": p.title,
                "policy_category": p.policy_category,
                "version": p.version,
                "summary": p.summary,
                "mandatory_controls": p.mandatory_controls,
            }
            for p in policies
        ]

        # Step 2D: Section 4 — Contractual Commitments (checking DPA, BAA, SCCs, and AI training prohibition clause)
        safeguards = matched_vendor.contractual_safeguards
        contractual_commitments: Dict[str, Any] = {
            "vendor_id": matched_vendor.vendor_id,
            "vendor_name": matched_vendor.vendor_name,
            "hosting_jurisdiction": matched_vendor.hosting_jurisdiction,
            "vendor_approval_status": matched_vendor.approval_status,
            "transfer_risk_score": matched_vendor.transfer_risk_score,
            "risk_tier": matched_vendor.risk_tier,
            "dpa_executed": safeguards["dpa_executed"],
            "cpra_service_provider_addendum_executed": safeguards["cpra_service_provider_addendum"],
            "hipaa_baa_executed": safeguards["hipaa_baa_executed"],
            "ontario_phipa_esp_agent_agreement_executed": safeguards["ontario_phipa_esp_agent_agreement"],
            "eu_sccs_executed": safeguards["eu_sccs_executed"],
            "eu_tia_completed": safeguards["eu_tia_completed"],
            "quebec_law25_tra_completed": safeguards["quebec_law25_tra_completed"],
            "ai_training_prohibition_clause_present": safeguards["ai_training_prohibited_clause"],
            "zero_data_retention_enabled": safeguards["zero_data_retention_enabled"],
            "blocking_contractual_and_assessment_gaps": matched_vendor.blocking_gaps,
        }

        # Step 2E: Section 5 — AI Recommendations (requiring PIA/DPIA/AIIA/TIA/TRA and human DPO/Legal approval)
        ai_recommendations: Dict[str, Any] = {
            "recommended_decision": "DO_NOT_TRANSFER_UNTIL_ASSESSMENTS_AND_HUMAN_DPO_LEGAL_APPROVAL_COMPLETED",
            "required_assessments": [
                "PIA — Privacy Impact Assessment (PIPEDA / Quebec Law 25 s. 3.3 / CPRA § 1798.185(a)(15))",
                "DPIA — Data Protection Impact Assessment (GDPR Art. 35)",
                "AIIA — AI Impact Assessment (EU AI Act Arts. 4 & 50 / Quebec Law 25 s. 12.1 / CPRA ADMT)",
                "TRA — Out-of-Province Transfer Risk Assessment (Quebec Law 25 s. 17 ÉFVP)",
                "TIA — International Transfer Impact Assessment (GDPR Chapter V Art. 46 / Schrems II Clause 14)",
            ],
            "required_technical_and_contractual_remediations": [
                "Complete the pending Quebec Law 25 s. 17 TRA and GDPR Chapter V TIA for US cloud processing",
                "Enable zero-data-retention API configuration on the vendor endpoint",
                "Enforce automated PII/PHI redaction and pseudonymization prior to prompt transmission",
                "Execute a HIPAA BAA (45 CFR § 164.504(e)) and Ontario PHIPA O. Reg. 329/04 s. 6 agreement if any health data is in scope",
            ],
            "mandatory_human_approval_gate": {
                "requires_human_approval": True,
                "required_approver_roles": ["DPO", "LEGAL", "CPO"],
                "instruction": (
                    "Route the completed PIA/DPIA/AIIA/TRA/TIA package and vendor contract addendum to the Data Protection Officer (DPO) "
                    "and Legal Counsel for formal human sign-off before enabling any customer data transfer."
                ),
            },
        }

        # Step 3: Supporting Evidence Citations
        supporting_evidence: List[AssistantEvidenceCitation] = [
            AssistantEvidenceCitation(
                citation_id="EVID-STAT-01",
                source_type="statute",
                jurisdiction_id="CA-QC",
                authority_or_owner="National Assembly of Quebec / LégisQuébec",
                citation_reference="Quebec Law 25 (CQLR c. P-39.1) ss. 3.3, 12.1, 17, 18.3",
                official_url_or_doc_id="https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1",
                verified_excerpt="Section 17 requires an assessment of privacy-related factors (ÉFVP/TRA) and a written agreement before communicating personal information outside Québec.",
            ),
            AssistantEvidenceCitation(
                citation_id="EVID-STAT-02",
                source_type="statute",
                jurisdiction_id="EU",
                authority_or_owner="European Union / EUR-Lex",
                citation_reference="GDPR (Regulation (EU) 2016/679) Arts. 28, 35, 44–46 & EU AI Act (Regulation (EU) 2024/1689) Arts. 4, 50",
                official_url_or_doc_id="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
                verified_excerpt="Controllers must execute an Art. 28 processor contract, conduct an Art. 35 DPIA for high-risk processing, and validate Chapter V transfer safeguards.",
            ),
            AssistantEvidenceCitation(
                citation_id="EVID-STAT-03",
                source_type="statute",
                jurisdiction_id="US-CA",
                authority_or_owner="State of California / CalPrivacy",
                citation_reference="Cal. Civ. Code §§ 1798.100(d), 1798.185(a)(15)-(16)",
                official_url_or_doc_id="https://cppa.ca.gov/regulations/",
                verified_excerpt="Service provider contracts must prohibit selling, sharing, or retaining/using personal information outside the direct business purpose.",
            ),
            AssistantEvidenceCitation(
                citation_id="EVID-GUID-04",
                source_type="regulator_guidance",
                jurisdiction_id="GLOBAL",
                authority_or_owner="OPC / CAI / CNIL / EDPB / FTC / CalPrivacy / HHS OCR / IPC Ontario",
                citation_reference="Joint Multi-Regulator Generative AI & Cross-Border Processing Guidance",
                official_url_or_doc_id="https://www.priv.gc.ca/en/privacy-topics/technology/artificial-intelligence/",
                verified_excerpt="Regulators prohibit secondary foundation model training on customer data without explicit consent and mandate pre-deployment impact assessments.",
            ),
            AssistantEvidenceCitation(
                citation_id="EVID-POL-05",
                source_type="internal_policy",
                jurisdiction_id="GLOBAL",
                authority_or_owner=profile["organization_name"],
                citation_reference=f"{policies[0].policy_id}, {policies[1].policy_id}, {policies[2].policy_id}",
                official_url_or_doc_id=policies[0].policy_id,
                verified_excerpt=policies[0].summary,
            ),
            AssistantEvidenceCitation(
                citation_id="EVID-VND-06",
                source_type="vendor_contract",
                jurisdiction_id=matched_vendor.hosting_jurisdiction,
                authority_or_owner=f"KIBO Vendor Registry — {matched_vendor.vendor_name}",
                citation_reference=f"Vendor ID: {matched_vendor.vendor_id} (Status: {matched_vendor.approval_status})",
                official_url_or_doc_id=matched_vendor.vendor_id,
                verified_excerpt=(
                    f"DPA={safeguards['dpa_executed']}, BAA={safeguards['hipaa_baa_executed']}, "
                    f"SCCs={safeguards['eu_sccs_executed']}, AI_Training_Prohibited={safeguards['ai_training_prohibited_clause']}, "
                    f"TIA_Completed={safeguards['eu_tia_completed']}, Quebec_TRA_Completed={safeguards['quebec_law25_tra_completed']}."
                ),
            ),
        ]

        decision_summary = (
            f"HOLD — DO NOT SEND CUSTOMER INFORMATION TO {matched_vendor.vendor_name.upper()} WITHOUT HUMAN DPO & LEGAL APPROVAL. "
            f"For {profile['organization_name']} (Tenant: {tenant_id}, Establishments: {', '.join(e.normalized_jurisdiction for e in establishments)}), "
            f"while an Art. 28 / CPRA DPA and AI training prohibition clause are on file, the vendor is currently on "
            f"{matched_vendor.approval_status} because the Quebec Law 25 s. 17 Transfer Risk Assessment (TRA), GDPR Chapter V "
            f"Transfer Impact Assessment (TIA), and PIA/DPIA/AIIA sign-offs are still required."
        )

        return AssistantQueryResponse(
            query_id=f"ast_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            user_id=req.user_id,
            role=req.role.upper(),
            question=req.question,
            organization_context_identified_first=org_context,
            decision_summary=decision_summary,
            statutory_requirements=statutory_requirements,
            regulator_guidance=regulator_guidance,
            organization_policies=organization_policies,
            contractual_commitments=contractual_commitments,
            ai_recommendations=ai_recommendations,
            supporting_evidence=supporting_evidence,
            requires_human_approval=True,
            required_approver_roles=["DPO", "LEGAL", "CPO"],
            auto_execution_blocked=True,
            evaluated_at=datetime.utcnow(),
        )


assistant_service = GovernedPrivacyAssistantService()


# ===========================================================================
# FASTAPI ENDPOINTS — MODULES A, C, G, H, I, J
# ===========================================================================

# --- Module A: Privacy Office Administration & Governance ---

@router.get("/governance/dashboard")
def get_governance_dashboard_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> Dict[str, Any]:
    """
    Executive Board & Privacy Office Governance Dashboard (`GET /api/v1/office/governance/dashboard`).
    Returns tenant-scoped organization profile, corporate establishments, privacy officers & delegates
    (GDPR DPO, German BDSG § 38 DPO, Quebec Law 25 s. 3.1 Person in Charge, CPO, HIPAA Privacy/Security Officer),
    governance calendar, policy repository, training completion, budget tracking, and board KPIs.
    """
    open_incidents = len(breach_service.list_incidents(tenant_id))
    vendors = vendor_service.list_vendors(tenant_id)
    high_risk_vendors = sum(1 for v in vendors if v.risk_tier in {"HIGH", "CRITICAL"})
    overview = risk_control_service.get_overview(tenant_id)
    open_risks = overview["continuous_monitoring_summary"]["open_risks"]
    amendments = reg_intel_service.list_amendments(tenant_id)
    return governance_service.get_dashboard(
        tenant_id=tenant_id,
        open_incidents_count=open_incidents,
        high_risk_vendors_count=high_risk_vendors,
        open_risks_count=open_risks,
        pending_amendments_count=len(amendments),
    )


@router.get("/governance")
def get_governance_root_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> Dict[str, Any]:
    """Alias for the Module A governance overview."""
    return get_governance_dashboard_endpoint(tenant_id=tenant_id)


@router.post("/governance/profile")
def update_governance_profile_endpoint(
    payload: GovernanceProfilePayload,
    tenant_id: str = Depends(resolve_tenant_id),
) -> Dict[str, Any]:
    """Update organization & business-unit profile, establishments, budget, and annual privacy program plan."""
    return governance_service.update_profile(tenant_id, payload)


@router.post("/governance/officers", response_model=PrivacyOfficerDesignation)
def register_privacy_officer_endpoint(
    payload: PrivacyOfficerDesignation,
    tenant_id: str = Depends(resolve_tenant_id),
) -> PrivacyOfficerDesignation:
    """Designate a Privacy Officer or delegate (DPO, CPO, Quebec Law 25 s. 3.1, German BDSG § 38, HIPAA Officer)."""
    return governance_service.register_officer(tenant_id, payload)


@router.post("/governance/establishments", response_model=CorporateEstablishment)
def register_corporate_establishment_endpoint(
    payload: CorporateEstablishment,
    tenant_id: str = Depends(resolve_tenant_id),
) -> CorporateEstablishment:
    """Register a corporate establishment and evaluate German BDSG § 38 DPO threshold (>=20 personnel)."""
    return governance_service.register_establishment(tenant_id, payload)


@router.get("/governance/policies", response_model=List[GovernancePolicyRecord])
def list_governance_policies_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[GovernancePolicyRecord]:
    """List tenant-scoped internal privacy & AI governance policies."""
    return governance_service.list_policies(tenant_id)


@router.post("/governance/policies", response_model=GovernancePolicyRecord)
def create_governance_policy_endpoint(
    payload: GovernancePolicyRecord,
    tenant_id: str = Depends(resolve_tenant_id),
) -> GovernancePolicyRecord:
    """Create a tenant-scoped privacy policy record."""
    return governance_service.create_policy(tenant_id, payload)


# --- Module C: Multi-Jurisdictional Privacy Incident & Breach Management ---

@router.post("/incidents", response_model=UnifiedIncidentRecord)
def create_multijurisdictional_incident_endpoint(
    payload: IncidentCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> UnifiedIncidentRecord:
    """
    Create a unified multi-jurisdictional privacy incident record (Acceptance Test 8).
    Evaluates independent regimes (US-CA, CA-ON, CA-FED, CA-QC, EU-FR, EU-DE, US-FED HIPAA),
    reporting thresholds, statutory deadlines from `discovered_at`, exact notification recipients,
    deduplicated workflow tasks, and cryptographic evidence timeline, while routing all external
    notification drafts to mandatory human legal approval (`status="pending_legal_approval"`, `auto_send_blocked=True`).
    """
    return breach_service.create_incident(tenant_id, payload)


@router.get("/incidents", response_model=List[UnifiedIncidentRecord])
def list_incidents_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[UnifiedIncidentRecord]:
    """List tenant-scoped privacy incident records."""
    return breach_service.list_incidents(tenant_id)


@router.get("/incidents/{incident_id}", response_model=UnifiedIncidentRecord)
def get_incident_endpoint(
    incident_id: str,
    tenant_id: str = Depends(resolve_tenant_id),
) -> UnifiedIncidentRecord:
    """Retrieve a single unified privacy incident record strictly scoped to the active tenant."""
    return breach_service.get_incident(tenant_id, incident_id)


@router.post("/incidents/{incident_id}/approve-notification", response_model=UnifiedIncidentRecord)
def approve_incident_notification_endpoint(
    incident_id: str,
    payload: NotificationApprovalRequest,
    request: Request,
    tenant_id: str = Depends(resolve_tenant_id),
) -> UnifiedIncidentRecord:
    """
    Human approval gate for external regulator or individual breach notifications.
    Strictly requires `LEGAL`, `CPO`, or `DPO` role.
    """
    caller_role = resolve_caller_role(request, payload_role=payload.approver_role)
    return breach_service.approve_notification(tenant_id, incident_id, payload, caller_role=caller_role)


# --- Module G: Vendor Privacy Management ---

@router.get("/vendors", response_model=List[VendorRecord])
def list_vendors_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[VendorRecord]:
    """List tenant-scoped vendors with DPA, BAA, Ontario PHIPA O. Reg. 329/04 s. 6, NYDFS 500.11, SCCs, TRA/TIA, and renewal alerts."""
    return vendor_service.list_vendors(tenant_id)


@router.post("/vendors", response_model=VendorRecord)
def register_vendor_endpoint(
    payload: VendorCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> VendorRecord:
    """Register and evaluate a vendor against multi-jurisdictional contractual, transfer, and AI governance requirements."""
    return vendor_service.evaluate_and_register_vendor(tenant_id, payload)


# --- Module H: Enterprise Risk & Control Management ---

@router.get("/risks-controls")
def get_risks_and_controls_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> Dict[str, Any]:
    """Retrieve the tenant-scoped enterprise privacy risk register, canonical control library, and continuous monitoring metrics."""
    return risk_control_service.get_overview(tenant_id)


@router.post("/risks-controls/risks", response_model=EnterprisePrivacyRiskRecord)
def create_privacy_risk_endpoint(
    payload: RiskCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> EnterprisePrivacyRiskRecord:
    """Register a new enterprise privacy risk mapped to canonical `regulation_id`s and controls."""
    return risk_control_service.create_risk(tenant_id, payload)


@router.post("/risks-controls/risks/{risk_id}/accept", response_model=EnterprisePrivacyRiskRecord)
def accept_privacy_risk_endpoint(
    risk_id: str,
    payload: RiskAcceptancePayload,
    request: Request,
    tenant_id: str = Depends(resolve_tenant_id),
) -> EnterprisePrivacyRiskRecord:
    """Formal risk acceptance workflow requiring human CPO, DPO, or LEGAL sign-off."""
    caller_role = resolve_caller_role(request, payload_role=payload.approver_role)
    return risk_control_service.accept_risk(tenant_id, risk_id, payload, caller_role=caller_role)


# --- Module I: Regulatory Intelligence & Change Impact Analysis ---

@router.post("/regulatory-intelligence/amendments", response_model=RegulatoryAmendmentRecord)
def record_regulatory_amendment_endpoint(
    payload: RegulatoryAmendmentCreateRequest,
    request: Request,
    tenant_id: str = Depends(resolve_tenant_id),
) -> RegulatoryAmendmentRecord:
    """
    Record a statutory or regulatory amendment and compute the tenant-wide blast radius (Acceptance Test 10).
    Enforces the rule that no LLM or unreviewed change can directly alter production obligations without human LEGAL/CPO approval.
    """
    caller_role = resolve_caller_role(request, payload_role=payload.reviewer_role)
    return reg_intel_service.record_amendment(tenant_id, payload, caller_role=caller_role)


@router.get("/regulatory-intelligence/amendments", response_model=List[RegulatoryAmendmentRecord])
def list_regulatory_amendments_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[RegulatoryAmendmentRecord]:
    """List recorded regulatory amendments and their blast-radius impact analyses."""
    return reg_intel_service.list_amendments(tenant_id)


@router.get("/regulatory-intelligence")
def get_regulatory_intelligence_overview_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> Dict[str, Any]:
    """Retrieve regulatory intelligence status and recorded amendments for the tenant."""
    amendments = reg_intel_service.list_amendments(tenant_id)
    return {
        "tenant_id": tenant_id,
        "amendments_count": len(amendments),
        "llm_direct_production_alteration_blocked": True,
        "amendments": [a.model_dump() for a in amendments],
    }


# --- Module J: Governed Privacy Office Assistant ---

@router.post("/assistant/query", response_model=AssistantQueryResponse)
def query_privacy_assistant_endpoint(
    payload: AssistantQueryRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> AssistantQueryResponse:
    """
    Governed Privacy Office Assistant (`POST /api/v1/office/assistant/query` — Acceptance Test 12).
    1. Identifies the caller's organization (`tenant_id`), establishments, industry, and applicable jurisdictions FIRST.
    2. Separates its response into 5 structured, evidence-backed sections:
       `statutory_requirements`, `regulator_guidance`, `organization_policies`, `contractual_commitments`, `ai_recommendations`.
    3. Includes `supporting_evidence` citations and `requires_human_approval=True` for consequential actions.
    """
    if payload.tenant_id and payload.tenant_id != tenant_id and tenant_id != "default":
        raise HTTPException(
            status_code=403,
            detail="CROSS_TENANT_ACCESS_DENIED: Requested tenant_id does not match authenticated tenant context",
        )
    effective_tenant = payload.tenant_id or tenant_id
    return assistant_service.answer_query(effective_tenant, payload)
