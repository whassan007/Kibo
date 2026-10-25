"""
KIBO Privacy OS — Privacy Office Modules B, D, E, and F.
Implements deterministic statutory workflows and FastAPI endpoints for:
- Module B: Jurisdiction-Specific Privacy Assessments (PIA, DPIA, TRA, TIA, LIA, AIIA, VENDOR_PRIVACY, DATA_SHARING, CHANGE_IMPACT)
- Module D: Multi-Jurisdictional Privacy Rights Management (DSAR, Cross-Border Applicability, SLAs, Exemptions, Appeals)
- Module E: Data Inventory, RoPA & Cross-Border Transfers (Art. 30 / Law 25 / CPRA RoPA, Adequacy, SCCs, TIA, Localization)
- Module F: Consent & Preferences Management (Regime Evaluation, CNIL/LIL Art. 82, US Opt-Out/GPC/UOOM, Consent Ledger)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.context.tenant_context import get_current_tenant, get_tenant_id
from core.jrae.registry import (
    EU_MEMBER_STATES,
    GLOBAL_JURISDICTION_REGISTRY,
    normalize_jurisdiction_code,
)
from core.jrae.schemas import OrganizationProfileInput, ProcessingActivityInput

router = APIRouter(
    prefix="/api/v1/office",
    tags=["Privacy Office - Assessments, Rights, RoPA & Consent"],
)


# ===========================================================================
# TENANT CONTEXT DEPENDENCY
# ===========================================================================

def resolve_tenant_id(
    request: Request,
    x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-ID"),
) -> str:
    """
    Resolve the active tenant ID deterministically from middleware context,
    explicit X-Tenant-ID header, or PrincipalContext on request.state.
    """
    principal = getattr(request.state, "principal", None)
    if principal and getattr(principal, "tenant_id", None):
        if x_tenant_id and x_tenant_id != principal.tenant_id:
            raise HTTPException(status_code=403, detail="Cross-tenant access attempt blocked")
        return principal.tenant_id

    ctx = get_current_tenant()
    if x_tenant_id:
        if ctx and ctx.tenant_id not in ("default", x_tenant_id):
            raise HTTPException(status_code=403, detail="Cross-tenant access attempt blocked")
        return x_tenant_id.strip()

    if ctx and ctx.tenant_id:
        return ctx.tenant_id

    tid = get_tenant_id()
    return tid or "default"


# ===========================================================================
# MODULE B — JURISDICTION-SPECIFIC PRIVACY ASSESSMENTS
# ===========================================================================

class AssessmentType(str, Enum):
    PIA = "PIA"
    DPIA = "DPIA"
    TRA = "TRA"
    TIA = "TIA"
    LIA = "LIA"
    AIIA = "AIIA"
    VENDOR_PRIVACY = "VENDOR_PRIVACY"
    DATA_SHARING = "DATA_SHARING"
    CHANGE_IMPACT = "CHANGE_IMPACT"


class ApprovalRole(str, Enum):
    DPO = "DPO"
    CPO = "CPO"
    LEGAL = "LEGAL"
    CISO = "CISO"


class AssessmentQuestionSpec(BaseModel):
    question_id: str
    section: str
    jurisdiction_id: str
    statutory_citation: str
    question_text: str
    required: bool = True
    expected_evidence: List[str] = Field(default_factory=list)
    answer: Optional[str] = None


class AssessmentRecommendationItem(BaseModel):
    assessment_type: AssessmentType
    title: str
    mandatory: bool = True
    triggering_jurisdictions: List[str]
    statutory_citations: List[str]
    trigger_reasoning: str
    mandatory_questions: List[AssessmentQuestionSpec]
    required_evidence_artifacts: List[str]
    required_approval_roles: List[ApprovalRole]
    prior_regulator_consultation_trigger: Optional[str] = None


class AssessmentRecommendRequest(BaseModel):
    organization: OrganizationProfileInput = Field(default_factory=OrganizationProfileInput)
    jurisdictions: List[str] = Field(default_factory=list)
    data_categories: List[str] = Field(default_factory=list)
    processing_activities: List[str] = Field(default_factory=list)
    activity_details: Optional[ProcessingActivityInput] = None
    involves_cross_border_transfer: bool = False
    involves_ai_or_admt: bool = False
    involves_vendors_or_processors: bool = False
    involves_data_sharing_or_joint_controller: bool = False
    involves_system_or_process_change: bool = False
    relies_on_legitimate_interests: bool = False


class AssessmentRecommendResponse(BaseModel):
    recommendation_id: str
    evaluated_at: datetime
    normalized_jurisdictions: List[str]
    recommended_assessments: List[AssessmentRecommendationItem]
    required_approval_roles: List[ApprovalRole]
    required_evidence_artifacts: List[str]
    deterministic_engine_mode: str = "OFFLINE_CAPABLE_DETERMINISTIC_V1"


class AssessmentCreateRequest(BaseModel):
    title: str
    assessment_type: AssessmentType
    jurisdictions: List[str] = Field(default_factory=list)
    data_categories: List[str] = Field(default_factory=list)
    processing_activities: List[str] = Field(default_factory=list)
    system_or_project_name: str = "Core Processing System"
    organization: Optional[OrganizationProfileInput] = None
    initial_answers: Dict[str, str] = Field(default_factory=dict)
    risk_level: str = Field(default="high", description="low, medium, high, critical")


class AssessmentApprovalRecord(BaseModel):
    approval_id: str
    assessment_id: str
    tenant_id: str
    approver_role: ApprovalRole
    approver_user_id: str
    decision: str = Field(default="approved", description="approved, rejected, conditional")
    rationale: str
    approved_at: datetime
    cryptographic_hash: str


class AssessmentApproveRequest(BaseModel):
    approver_role: ApprovalRole
    approver_user_id: str = "dpo_officer"
    decision: str = "approved"
    rationale: str
    residual_risk_accepted: bool = True


class AssessmentInstance(BaseModel):
    assessment_id: str
    tenant_id: str
    title: str
    assessment_type: AssessmentType
    system_or_project_name: str
    jurisdictions: List[str]
    data_categories: List[str]
    processing_activities: List[str]
    risk_level: str
    status: str = Field(default="pending_approval", description="draft, pending_approval, approved, rejected, requires_regulator_consultation")
    statutory_citations: List[str]
    questions: List[AssessmentQuestionSpec]
    required_evidence_artifacts: List[str]
    required_approval_roles: List[ApprovalRole]
    approvals: List[AssessmentApprovalRecord] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    deterministic_mode: bool = True
    content_hash: str


# Canonical Statutory Templates for all 9 Assessment Types
ASSESSMENT_CATALOG_TEMPLATES: Dict[AssessmentType, Dict[str, Any]] = {
    AssessmentType.PIA: {
        "title": "Privacy Impact Assessment (PIA — PIPEDA / Quebec Law 25 s. 3.3 / US E-Gov Act)",
        "citations": [
            "Quebec Act respecting the protection of personal information in the private sector (Law 25), s. 3.3",
            "PIPEDA Schedule 1, Principle 4.1 (Accountability) & OPC PIA Expectations",
            "US E-Government Act of 2002, Section 208 (Federal PIA)",
        ],
        "roles": [ApprovalRole.CPO, ApprovalRole.DPO],
        "evidence": [
            "Data Flow Diagram & System Architecture",
            "Proportionality & Necessity Analysis",
            "Quebec Law 25 s. 3.3 Sensitivity & Purpose Matrix",
            "Retention and De-identification Schedule",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="PIA-QC-01",
                section="Proportionality & Necessity",
                jurisdiction_id="CA-QC",
                statutory_citation="Quebec Law 25 s. 3.3 & s. 4",
                question_text="Is the collection and processing of personal information necessary, serious, and legitimate, and is the sensitivity of the data proportional to the stated purpose?",
                expected_evidence=["Purpose Specification Document", "Data Minimization Matrix"],
            ),
            AssessmentQuestionSpec(
                question_id="PIA-CA-02",
                section="Accountability & Safeguards",
                jurisdiction_id="CA-FED",
                statutory_citation="PIPEDA Schedule 1 Principles 4.1 & 4.7",
                question_text="What administrative, technical, and physical safeguards protect the information against loss, theft, or unauthorized access throughout its lifecycle?",
                expected_evidence=["Security Controls Inventory", "Encryption Configuration"],
            ),
            AssessmentQuestionSpec(
                question_id="PIA-US-03",
                section="Notice & Collection Authority",
                jurisdiction_id="US-FED",
                statutory_citation="E-Government Act of 2002 § 208 / FTC Act § 5",
                question_text="How are individuals provided clear, conspicuous notice prior to collection, and what statutory or policy authority governs the information system?",
                expected_evidence=["Privacy Notice Snapshot", "Collection Consent Flow"],
            ),
        ],
    },
    AssessmentType.DPIA: {
        "title": "Data Protection Impact Assessment (DPIA — GDPR Art. 35 / US State Data Protection Assessments)",
        "citations": [
            "Regulation (EU) 2016/679 (GDPR) Articles 35 & 36",
            "EDPB Guidelines WP248 rev.01 on Data Protection Impact Assessment",
            "California CCPA/CPRA Cal. Civ. Code § 1798.185(a)(15) Risk Assessment",
            "Colorado CPA C.R.S. § 6-1-1309 / Virginia VCDPA § 59.1-580 Data Protection Assessment",
        ],
        "roles": [ApprovalRole.DPO, ApprovalRole.CPO, ApprovalRole.LEGAL],
        "evidence": [
            "Systematic Description of Processing Operations (GDPR Art. 35(7)(a))",
            "Necessity and Proportionality Assessment (GDPR Art. 35(7)(b))",
            "Risk Matrix to Rights and Freedoms of Data Subjects (GDPR Art. 35(7)(c))",
            "Signed DPO Advice Opinion (GDPR Art. 35(2))",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="DPIA-EU-01",
                section="Systematic Description & High-Risk Triggers",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 35(1), Art. 35(3), Art. 35(7)(a)",
                question_text="Describe the nature, scope, context, and purposes of processing, including whether it involves systematic profiling, large-scale special category data (Art. 9), or public area monitoring.",
                expected_evidence=["Processing Operations Specification", "Art. 35(3) Trigger Checklist"],
            ),
            AssessmentQuestionSpec(
                question_id="DPIA-EU-02",
                section="Necessity, Proportionality & Fundamental Rights",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 35(7)(b)-(c)",
                question_text="How are necessity and proportionality ensured in relation to the purposes, and what are the likelihood and severity of risks to the rights and freedoms of data subjects?",
                expected_evidence=["Fundamental Rights Risk Scoring Sheet"],
            ),
            AssessmentQuestionSpec(
                question_id="DPIA-EU-03",
                section="Mitigation Measures & Prior Consultation (Art. 36)",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 35(7)(d) & Art. 36(1)",
                question_text="What safeguards, security measures, and mechanisms mitigate the identified risks, and does residual high risk require prior consultation with the supervisory authority under Art. 36?",
                expected_evidence=["Risk Mitigation Plan", "DPO Written Advice Record"],
            ),
        ],
    },
    AssessmentType.TRA: {
        "title": "Threat & Risk Assessment (TRA — Ontario PHIPA / Canada Health Infoway HTRA / Security Rule)",
        "citations": [
            "Ontario Personal Health Information Protection Act (PHIPA), S.O. 2004, c. 3, s. 12(1) & O. Reg. 329/04",
            "Canada Health Infoway Harmonized Threat and Risk Assessment (HTRA) Methodology",
            "HIPAA Security Rule 45 CFR § 164.308(a)(1)(ii)(A) Security Risk Analysis",
        ],
        "roles": [ApprovalRole.CISO, ApprovalRole.CPO],
        "evidence": [
            "Asset & Threat Catalog (HTRA / NIST SP 800-30)",
            "Vulnerability & Penetration Test Report",
            "PHIPA s. 12 Electronic Audit Log Verification",
            "Residual Security Risk Acceptance Sign-Off",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="TRA-ON-01",
                section="Custodian Safeguards & Threat Modeling",
                jurisdiction_id="CA-ON",
                statutory_citation="Ontario PHIPA s. 12(1) & IPC Ontario TRA Guidance",
                question_text="Have all administrative, technical, and physical threats against Personal Health Information (PHI) or sensitive repositories been inventoried and scored for exploitability and impact?",
                expected_evidence=["Threat Modeling Matrix", "Vulnerability Scan Report"],
            ),
            AssessmentQuestionSpec(
                question_id="TRA-ON-02",
                section="Audit Logging & Unauthorized Access Detection",
                jurisdiction_id="CA-ON",
                statutory_citation="Ontario PHIPA s. 10(3), s. 12(2) & O. Reg. 329/04 s. 6",
                question_text="Does the electronic system maintain immutable audit logs recording every viewing, handling, or modification of health/sensitive records with automated alerting on anomalous access?",
                expected_evidence=["Audit Log Schema & Retention Proof"],
            ),
        ],
    },
    AssessmentType.TIA: {
        "title": "Transfer Impact Assessment (TIA — Quebec Law 25 s. 17 / GDPR Schrems II Clause 14)",
        "citations": [
            "Quebec Law 25 s. 17 (Communication of personal information outside Québec)",
            "GDPR Chapter V (Arts. 44-49) & CJEU C-311/18 (Schrems II)",
            "European Commission Implementing Decision (EU) 2021/914 (2021 EU SCCs Clause 14)",
            "EDPB Recommendations 01/2020 on Supplementary Measures",
        ],
        "roles": [ApprovalRole.DPO, ApprovalRole.LEGAL, ApprovalRole.CISO],
        "evidence": [
            "Destination Jurisdiction Surveillance & Rule-of-Law Analysis",
            "2021 EU SCC Module Selection & Signed Annexes I-III",
            "Quebec Law 25 s. 17 Written Cross-Border Agreement",
            "EDPB Supplementary Technical Measures (Encryption Key Custody Proof)",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="TIA-QC-01",
                section="Quebec Law 25 s. 17 Equivalency Assessment",
                jurisdiction_id="CA-QC",
                statutory_citation="Quebec Law 25 s. 17",
                question_text="Taking into account the sensitivity of the information, the purposes, the protection measures (contractual or otherwise), and the legal framework applicable in the destination state, will the information receive adequate protection equivalent to Quebec standards?",
                expected_evidence=["Destination Legal Regime Equivalency Memo", "Written s. 17 Contract Clauses"],
            ),
            AssessmentQuestionSpec(
                question_id="TIA-EU-02",
                section="Schrems II Clause 14 & Government Access Evaluation",
                jurisdiction_id="EU",
                statutory_citation="2021 EU SCCs Clause 14 & EDPB Recommendations 01/2020",
                question_text="Do laws and practices in the third country regarding public authority access (e.g., national security / surveillance laws) impinge on the effectiveness of the Article 46 transfer tool, and what supplementary technical measures (e.g., BYOK/HYOK encryption in transit and at rest) prevent access in the clear?",
                expected_evidence=["Clause 14 Surveillance Law Assessment", "Cryptographic Key Management Architecture"],
            ),
        ],
    },
    AssessmentType.LIA: {
        "title": "Legitimate Interests Assessment (LIA — GDPR Art. 6(1)(f) Three-Part Balancing Test)",
        "citations": [
            "Regulation (EU) 2016/679 (GDPR) Article 6(1)(f) & Recital 47",
            "EDPB Guidelines 1/2024 on processing of personal data based on Article 6(1)(f) GDPR",
        ],
        "roles": [ApprovalRole.DPO, ApprovalRole.LEGAL],
        "evidence": [
            "Three-Part LIA Balancing Test Record (Purpose, Necessity, Balancing)",
            "Reasonable Expectations of Data Subjects Analysis (Recital 47)",
            "Art. 21 Right to Object Opt-Out Implementation Proof",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="LIA-EU-01",
                section="Part 1: Purpose Test",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 6(1)(f)",
                question_text="What is the specific, real, and present legitimate interest pursued by the controller or a third party, and is it lawful, clearly articulated, and non-speculative?",
                expected_evidence=["Legitimate Interest Statement"],
            ),
            AssessmentQuestionSpec(
                question_id="LIA-EU-02",
                section="Part 2: Necessity Test",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 6(1)(f) & Art. 5(1)(c)",
                question_text="Is the processing strictly necessary to achieve the legitimate interest, or could the objective reasonably be achieved through less intrusive means or fewer data elements?",
                expected_evidence=["Less Intrusive Alternatives Analysis"],
            ),
            AssessmentQuestionSpec(
                question_id="LIA-EU-03",
                section="Part 3: Balancing Test & Safeguards",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 6(1)(f), Recital 47 & Art. 21",
                question_text="Do the fundamental rights, freedoms, or interests of the data subjects override the controller's interest, considering data subject expectations, vulnerability (e.g., children), and unconditional Art. 21 opt-out mechanisms?",
                expected_evidence=["Balancing Test Matrix", "Art. 21 Objection Flow"],
            ),
        ],
    },
    AssessmentType.AIIA: {
        "title": "AI & Automated Decision-Making Impact Assessment (EU AI Act FRIA / Colorado AI Act / CalPrivacy ADMT / Quebec Law 25 s. 12.1 / Ontario Bill 194)",
        "citations": [
            "Regulation (EU) 2024/1689 (EU AI Act) Article 27 (Fundamental Rights Impact Assessment) & Annex III",
            "GDPR Article 22 (Automated Individual Decision-Making, Including Profiling)",
            "Colorado Artificial Intelligence Act (SB 24-205) C.R.S. § 6-1-1703 Impact Assessment",
            "California CCPA/CPRA Automated Decisionmaking Technology (ADMT) Regulations",
            "Quebec Law 25 s. 12.1 (Fully Automated Decision-Making Transparency & Review Rights)",
            "Ontario Bill 194 (Enhancing Digital Security and Trust Act, 2024 — Public Sector AI Accountability)",
        ],
        "roles": [ApprovalRole.CPO, ApprovalRole.DPO, ApprovalRole.LEGAL, ApprovalRole.CISO],
        "evidence": [
            "Model Card & Training Data Lineage Provenance",
            "Algorithmic Bias & Disparate Impact Evaluation Report",
            "Human-in-the-Loop Intervention & Override SOP (GDPR Art. 22 / Law 25 s. 12.1)",
            "Pre-Use ADMT Notice & Opt-Out Mechanism (CalPrivacy / Colorado AI Act)",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="AIIA-EU-01",
                section="EU AI Act Classification & Fundamental Rights Impact (Art. 27)",
                jurisdiction_id="EU",
                statutory_citation="EU AI Act (Reg. 2024/1689) Art. 5, Art. 6, Annex III & Art. 27",
                question_text="Does the AI system involve prohibited practices (Art. 5) or high-risk Annex III use cases (e.g., employment, credit, essential services, biometrics), and what are the specific risks of harm to marginalized groups and fundamental rights?",
                expected_evidence=["EU AI Act Risk Tier Classification", "Fundamental Rights Impact Matrix"],
            ),
            AssessmentQuestionSpec(
                question_id="AIIA-US-02",
                section="Algorithmic Discrimination & ADMT Opt-Out / Appeal Rights",
                jurisdiction_id="US-CO",
                statutory_citation="Colorado AI Act C.R.S. § 6-1-1703 & CalPrivacy ADMT Rules",
                question_text="What quantitative bias testing verifies the absence of algorithmic discrimination across protected classes, and how can consumers exercise pre-use opt-out, explanation, and human appeal rights for consequential decisions?",
                expected_evidence=["Disparate Impact Audit Statistical Report", "ADMT Consumer Opt-Out & Appeal Flow"],
            ),
            AssessmentQuestionSpec(
                question_id="AIIA-CA-03",
                section="Automated Decision Transparency & Human Review (Law 25 s. 12.1)",
                jurisdiction_id="CA-QC",
                statutory_citation="Quebec Law 25 s. 12.1 & Ontario Bill 194",
                question_text="Are individuals informed at or before the time of a decision based exclusively on automated processing of the personal information used, the principal factors and parameters leading to the decision, and their right to submit observations to a human qualified to review the decision?",
                expected_evidence=["Law 25 s. 12.1 Disclosure Template", "Human Reviewer Escalation Workflow"],
            ),
        ],
    },
    AssessmentType.VENDOR_PRIVACY: {
        "title": "Vendor Privacy & Security Due Diligence Assessment (GDPR Art. 28 / CPRA Service Provider / Law 25 s. 18.3)",
        "citations": [
            "GDPR Article 28 (Processor Due Diligence & Mandatory DPA Clauses)",
            "California CCPA/CPRA Cal. Civ. Code § 1798.100(d) (Service Provider / Contractor / Third Party Contracts)",
            "Quebec Law 25 s. 18.3 (Written Mandate for Processing Without Consent)",
            "PIPEDA Schedule 1 Principle 4.1.3 (Accountability for Third-Party Processing)",
        ],
        "roles": [ApprovalRole.DPO, ApprovalRole.CISO, ApprovalRole.LEGAL],
        "evidence": [
            "Executed Data Processing Agreement (GDPR Art. 28 / CPRA § 1798.100(d) / Law 25 s. 18.3)",
            "SOC 2 Type II / ISO 27001 Certification & Subprocessor List",
            "Vendor Breach Notification SLA Commitment (<= 24-48 Hours)",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="VPA-GLOBAL-01",
                section="Statutory DPA & Purpose Limitation Clauses",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 28(3), CPRA § 1798.100(d), Quebec Law 25 s. 18.3",
                question_text="Does the executed contract bind the vendor to process personal data solely on documented instructions, prohibit selling/sharing or retaining data outside the direct business relationship, require prior subprocessor authorization, and mandate deletion/return upon termination?",
                expected_evidence=["Signed Data Processing Addendum (DPA)", "Subprocessor Registry"],
            ),
            AssessmentQuestionSpec(
                question_id="VPA-GLOBAL-02",
                section="Technical & Organizational Security Posture",
                jurisdiction_id="US-CA",
                statutory_citation="GDPR Art. 32, Quebec Law 25 s. 18.3(1), HIPAA § 164.308(b)",
                question_text="Has the vendor demonstrated independent security assurance (SOC 2 Type II / ISO 27001), encryption at rest and in transit, tenant isolation, and contractual breach reporting within 24-48 hours?",
                expected_evidence=["SOC 2 Type II Report", "Incident Response Addendum"],
            ),
        ],
    },
    AssessmentType.DATA_SHARING: {
        "title": "Data Sharing, Joint Controller & Research Agreement Assessment (GDPR Art. 26 / Law 25 s. 21 / HIPAA DUA)",
        "citations": [
            "GDPR Article 26 (Joint Controllers Arrangement)",
            "Quebec Law 25 s. 21 & s. 21.0.1 (Study, Research, or Statistics Disclosure Agreement)",
            "HIPAA 45 CFR § 164.514(e) (Limited Data Set & Data Use Agreement)",
        ],
        "roles": [ApprovalRole.LEGAL, ApprovalRole.DPO, ApprovalRole.CPO],
        "evidence": [
            "Joint Controller Responsibility Allocation Matrix (GDPR Art. 26(1))",
            "Data Sharing / Research Data Use Agreement (DUA)",
            "Transparency Summary for Data Subjects (GDPR Art. 26(2))",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="DSA-EU-01",
                section="Controller Role Determination & Art. 26 Allocation",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 26(1)-(2)",
                question_text="Have the parties transparently determined their respective responsibilities for compliance with GDPR obligations—particularly regarding the exercise of data subject rights and Art. 13/14 notices—and made the essence of the arrangement available to data subjects?",
                expected_evidence=["Art. 26 Joint Controller Agreement", "Public Essence Notice"],
            ),
            AssessmentQuestionSpec(
                question_id="DSA-CA-02",
                section="Research / External Sharing Safeguards",
                jurisdiction_id="CA-QC",
                statutory_citation="Quebec Law 25 s. 21 / HIPAA § 164.514(e)",
                question_text="If disclosed for external collaboration or research, is a formal PIA completed, is data de-identified or minimized, and does the written agreement prohibit re-identification and unauthorized onward disclosure?",
                expected_evidence=["Executed Data Sharing / Research Agreement"],
            ),
        ],
    },
    AssessmentType.CHANGE_IMPACT: {
        "title": "Privacy Change Impact Assessment (Material Change in Purpose, System Architecture, or Jurisdiction)",
        "citations": [
            "GDPR Art. 25 (Data Protection by Design and by Default) & Art. 35(11) (DPIA Review on Change)",
            "Quebec Law 25 s. 3.3 (PIA Mandatory on Acquisition, Development, or Overhaul of IS)",
            "CPRA Cal. Civ. Code § 1798.100(a)(1) (Incompatible Secondary Purpose Notice & Consent)",
        ],
        "roles": [ApprovalRole.DPO, ApprovalRole.CPO],
        "evidence": [
            "Architecture & Data Flow Delta Diff",
            "Purpose Compatibility & Notice Update Checklist",
            "Existing DPIA/PIA Re-Validation Sign-Off",
        ],
        "questions": [
            AssessmentQuestionSpec(
                question_id="CIA-GLOBAL-01",
                section="Materiality & Purpose Compatibility Analysis",
                jurisdiction_id="EU",
                statutory_citation="GDPR Art. 6(4), Art. 35(11), Quebec Law 25 s. 3.3",
                question_text="Does the proposed product, schema, vendor, or geographic change introduce new data categories, new cross-border transfers, automated profiling, or a purpose incompatible with the original collection notice?",
                expected_evidence=["Change Request Architecture Diff", "Purpose Compatibility Memo"],
            ),
        ],
    },
}


class PrivacyAssessmentService:
    """
    Deterministic engine for recommending, instantiating, retrieving, and approving
    jurisdiction-specific privacy assessments (Module B).
    Operates 100% deterministically without requiring LLM connectivity (Acceptance Test 15).
    """

    def __init__(self) -> None:
        self._store: Dict[str, AssessmentInstance] = {}

    def recommend_assessments(self, req: AssessmentRecommendRequest) -> AssessmentRecommendResponse:
        norm_jurisdictions = []
        for j in req.jurisdictions or req.organization.establishments:
            code = normalize_jurisdiction_code(j)
            if code and code not in norm_jurisdictions:
                norm_jurisdictions.append(code)
        if not norm_jurisdictions:
            norm_jurisdictions = ["US-FED"]

        cats_lower = {c.lower() for c in req.data_categories}
        acts_lower = {a.lower() for a in req.processing_activities}
        if req.activity_details:
            cats_lower.update(c.lower() for c in req.activity_details.data_categories)
            acts_lower.add(req.activity_details.purpose.lower())

        has_eu = any(j == "EU" or j.startswith("EU-") for j in norm_jurisdictions)
        has_ca = any(j.startswith("CA-") for j in norm_jurisdictions)
        has_qc = "CA-QC" in norm_jurisdictions
        has_on = "CA-ON" in norm_jurisdictions
        has_us = any(j.startswith("US-") for j in norm_jurisdictions)
        has_health_or_sensitive = bool(
            cats_lower & {
                "health", "phi", "medical", "biometric", "biometrics", "genetic",
                "sensitive", "precise_geolocation", "children", "financial", "ssn", "sin",
            }
        )
        has_ai = (
            req.involves_ai_or_admt
            or (req.activity_details and req.activity_details.involves_ai_or_admt)
            or any(k in " ".join(acts_lower) for k in ("ai", "automated", "admt", "profiling", "machine_learning", "llm", "scoring"))
        )
        has_transfer = (
            req.involves_cross_border_transfer
            or (req.activity_details and bool(req.activity_details.involves_cross_border_transfer or req.activity_details.transfer_destinations))
            or any(k in " ".join(acts_lower) for k in ("transfer", "cross_border", "cross-border", "export"))
            or (len({j.split("-")[0] for j in norm_jurisdictions}) > 1)
        )
        has_vendor = (
            req.involves_vendors_or_processors
            or (req.activity_details and req.activity_details.third_party_processors)
            or any(k in " ".join(acts_lower) for k in ("vendor", "processor", "subprocessor", "cloud", "saas", "outsourc"))
        )
        has_sharing = (
            req.involves_data_sharing_or_joint_controller
            or req.organization.role == "joint_controller"
            or any(k in " ".join(acts_lower) for k in ("sharing", "joint_controller", "research", "partner", "third_party_disclosure"))
        )
        has_change = (
            req.involves_system_or_process_change
            or any(k in " ".join(acts_lower) for k in ("change", "migration", "overhaul", "redesign", "new_feature"))
        )
        has_lia = (
            req.relies_on_legitimate_interests
            or any(k in " ".join(acts_lower) for k in ("legitimate_interest", "legitimate interest", "b2b_marketing", "fraud_analytics"))
        )

        selected_types: List[Tuple[AssessmentType, str, List[str]]] = []

        # 1. DPIA (GDPR Art. 35 / US State Data Protection Assessments)
        if has_eu or has_health_or_sensitive or has_ai or any(
            j in norm_jurisdictions for j in ("US-CA", "US-CO", "US-VA", "US-CT", "US-TX")
        ):
            trig_j = [j for j in norm_jurisdictions if j == "EU" or j.startswith("EU-") or j.startswith("US-")] or norm_jurisdictions
            selected_types.append((
                AssessmentType.DPIA,
                "Triggered by high-risk processing, sensitive data categories, profiling/AI, or EU GDPR Art. 35 / US State Data Protection Assessment mandates.",
                trig_j,
            ))

        # 2. PIA (Canada PIPEDA / Quebec Law 25 s. 3.3 / US Federal)
        if has_ca or has_qc or "US-FED" in norm_jurisdictions or not selected_types:
            trig_j = [j for j in norm_jurisdictions if j.startswith("CA-") or j == "US-FED"] or norm_jurisdictions
            selected_types.append((
                AssessmentType.PIA,
                "Triggered by Quebec Law 25 s. 3.3 IS/electronic service overhaul or PIPEDA / Federal Privacy Impact Assessment obligations.",
                trig_j,
            ))

        # 3. TRA (Ontario PHIPA / Healthcare / Sensitive Infrastructure)
        if has_on or has_health_or_sensitive or req.organization.organization_type in (
            "healthcare_covered_entity", "health_information_custodian", "business_associate"
        ):
            trig_j = [j for j in norm_jurisdictions if j in ("CA-ON", "CA-FED", "US-FED")] or norm_jurisdictions
            selected_types.append((
                AssessmentType.TRA,
                "Triggered by processing of health/sensitive data or Ontario PHIPA s. 12 / Canada Health Infoway HTRA / HIPAA Security Risk Analysis obligations.",
                trig_j,
            ))

        # 4. TIA (Cross-Border Transfers — Quebec Law 25 s. 17 / GDPR Schrems II)
        if has_transfer:
            selected_types.append((
                AssessmentType.TIA,
                "Triggered by cross-border communication of personal data outside Quebec (Law 25 s. 17) or outside the EEA (GDPR Art. 46 / Schrems II Clause 14).",
                norm_jurisdictions,
            ))

        # 5. LIA (GDPR Art. 6(1)(f) Legitimate Interests)
        if has_lia or (has_eu and "marketing" in " ".join(acts_lower)):
            trig_j = [j for j in norm_jurisdictions if j == "EU" or j.startswith("EU-")] or norm_jurisdictions
            selected_types.append((
                AssessmentType.LIA,
                "Triggered by reliance on GDPR Art. 6(1)(f) legitimate interests requiring a documented three-part balancing test.",
                trig_j,
            ))

        # 6. AIIA (AI / ADMT / Automated Decision-Making)
        if has_ai:
            selected_types.append((
                AssessmentType.AIIA,
                "Triggered by AI/ML or Automated Decision-Making Technology (EU AI Act Art. 27 FRIA, Colorado AI Act, CalPrivacy ADMT, Quebec Law 25 s. 12.1, Ontario Bill 194).",
                norm_jurisdictions,
            ))

        # 7. VENDOR_PRIVACY
        if has_vendor:
            selected_types.append((
                AssessmentType.VENDOR_PRIVACY,
                "Triggered by engagement of third-party processors/service providers requiring GDPR Art. 28 / CPRA § 1798.100(d) / Law 25 s. 18.3 due diligence.",
                norm_jurisdictions,
            ))

        # 8. DATA_SHARING
        if has_sharing:
            selected_types.append((
                AssessmentType.DATA_SHARING,
                "Triggered by external data sharing, joint controllership (GDPR Art. 26), or research disclosures (Quebec Law 25 s. 21).",
                norm_jurisdictions,
            ))

        # 9. CHANGE_IMPACT
        if has_change:
            selected_types.append((
                AssessmentType.CHANGE_IMPACT,
                "Triggered by material system architecture, vendor, or processing purpose change requiring Privacy by Design delta review.",
                norm_jurisdictions,
            ))

        recommendations: List[AssessmentRecommendationItem] = []
        all_roles: List[ApprovalRole] = []
        all_evidence: List[str] = []

        for atype, reason, trig_j in selected_types:
            tpl = ASSESSMENT_CATALOG_TEMPLATES[atype]
            questions = [q.model_copy(deep=True) for q in tpl["questions"]]
            roles = list(tpl["roles"])
            evidence = list(tpl["evidence"])

            prior_consult = None
            if atype == AssessmentType.DPIA and has_eu:
                prior_consult = "GDPR Art. 36(1): Mandatory prior consultation with competent Supervisory Authority if unmitigated residual risk remains high."
            elif atype == AssessmentType.TIA and has_qc:
                prior_consult = "Quebec Law 25 s. 17: Transfer prohibited if TIA concludes destination jurisdiction does not provide adequate protection equivalent to Quebec."

            recommendations.append(
                AssessmentRecommendationItem(
                    assessment_type=atype,
                    title=tpl["title"],
                    mandatory=True,
                    triggering_jurisdictions=trig_j,
                    statutory_citations=list(tpl["citations"]),
                    trigger_reasoning=reason,
                    mandatory_questions=questions,
                    required_evidence_artifacts=evidence,
                    required_approval_roles=roles,
                    prior_regulator_consultation_trigger=prior_consult,
                )
            )
            for r in roles:
                if r not in all_roles:
                    all_roles.append(r)
            for ev in evidence:
                if ev not in all_evidence:
                    all_evidence.append(ev)

        return AssessmentRecommendResponse(
            recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
            evaluated_at=datetime.utcnow(),
            normalized_jurisdictions=norm_jurisdictions,
            recommended_assessments=recommendations,
            required_approval_roles=all_roles,
            required_evidence_artifacts=all_evidence,
        )

    def create_assessment(self, tenant_id: str, req: AssessmentCreateRequest) -> AssessmentInstance:
        norm_jurisdictions = [normalize_jurisdiction_code(j) for j in req.jurisdictions if j] or ["US-FED"]
        tpl = ASSESSMENT_CATALOG_TEMPLATES[req.assessment_type]

        questions: List[AssessmentQuestionSpec] = []
        for q in tpl["questions"]:
            q_copy = q.model_copy(deep=True)
            if q_copy.question_id in req.initial_answers:
                q_copy.answer = req.initial_answers[q_copy.question_id]
            questions.append(q_copy)

        now = datetime.utcnow()
        assessment_id = f"asmt_{uuid.uuid4().hex[:12]}"
        payload_for_hash = {
            "assessment_id": assessment_id,
            "tenant_id": tenant_id,
            "assessment_type": req.assessment_type.value,
            "jurisdictions": norm_jurisdictions,
            "created_at": now.isoformat(),
        }
        content_hash = hashlib.sha256(json.dumps(payload_for_hash, sort_keys=True).encode("utf-8")).hexdigest()

        instance = AssessmentInstance(
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            title=req.title or tpl["title"],
            assessment_type=req.assessment_type,
            system_or_project_name=req.system_or_project_name,
            jurisdictions=norm_jurisdictions,
            data_categories=req.data_categories,
            processing_activities=req.processing_activities,
            risk_level=req.risk_level,
            status="pending_approval",
            statutory_citations=list(tpl["citations"]),
            questions=questions,
            required_evidence_artifacts=list(tpl["evidence"]),
            required_approval_roles=list(tpl["roles"]),
            approvals=[],
            created_at=now,
            updated_at=now,
            deterministic_mode=True,
            content_hash=content_hash,
        )
        self._store[assessment_id] = instance
        return instance

    def list_assessments(self, tenant_id: str) -> List[AssessmentInstance]:
        return [a for a in self._store.values() if a.tenant_id == tenant_id]

    def get_assessment(self, tenant_id: str, assessment_id: str) -> AssessmentInstance:
        inst = self._store.get(assessment_id)
        if not inst:
            raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
        if inst.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Cross-tenant access attempt blocked")
        return inst

    def approve_assessment(
        self, tenant_id: str, assessment_id: str, req: AssessmentApproveRequest
    ) -> AssessmentInstance:
        inst = self.get_assessment(tenant_id, assessment_id)
        now = datetime.utcnow()
        approval_id = f"appr_{uuid.uuid4().hex[:10]}"
        hash_input = (
            f"{approval_id}|{assessment_id}|{tenant_id}|{req.approver_role.value}|"
            f"{req.approver_user_id}|{req.decision}|{req.rationale}|{now.isoformat()}"
        )
        crypto_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        record = AssessmentApprovalRecord(
            approval_id=approval_id,
            assessment_id=assessment_id,
            tenant_id=tenant_id,
            approver_role=req.approver_role,
            approver_user_id=req.approver_user_id,
            decision=req.decision,
            rationale=req.rationale,
            approved_at=now,
            cryptographic_hash=crypto_hash,
        )
        inst.approvals.append(record)
        inst.updated_at = now

        if req.decision.lower() == "rejected":
            inst.status = "rejected"
        elif not req.residual_risk_accepted and inst.assessment_type == AssessmentType.DPIA:
            inst.status = "requires_regulator_consultation"
        else:
            inst.status = "approved"

        return inst


assessment_service = PrivacyAssessmentService()


# ===========================================================================
# MODULE D — MULTI-JURISDICTIONAL PRIVACY RIGHTS MANAGEMENT
# ===========================================================================

class RightsRequestType(str, Enum):
    ACCESS = "access"
    CORRECTION = "correction"
    DELETION = "deletion"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    WITHDRAW_CONSENT = "withdraw_consent"
    OBJECTION = "objection"
    RESTRICTION = "restriction"
    APPEAL = "appeal"
    AUTHORIZED_AGENT = "authorized_agent"


class RightsEvaluateRequest(BaseModel):
    subject_residence: str = Field(..., description="Jurisdiction code of data subject residence, e.g. EU-DE, US-CA, CA-ON")
    subject_nationality: Optional[str] = Field(default=None, description="Optional nationality code, e.g. EU-DE")
    request_type: RightsRequestType = RightsRequestType.DELETION
    organization_establishments: List[str] = Field(
        default_factory=lambda: ["US-FED", "US-CA"],
        description="Jurisdictions where the organization has establishments or operations, e.g. ['US-CA', 'CA-ON']",
    )
    processing_or_collection_locations: List[str] = Field(
        default_factory=list,
        description="Jurisdictions where personal data was actually collected or processed",
    )
    targets_subject_jurisdiction: bool = Field(
        default=False,
        description="Whether the organization intentionally offers goods/services to subjects in subject_residence (GDPR Art. 3(2)(a))",
    )
    monitors_subject_behavior: bool = Field(
        default=False,
        description="Whether the organization monitors behavior of subjects within subject_residence (GDPR Art. 3(2)(b))",
    )
    data_categories: List[str] = Field(default_factory=list)
    is_authorized_agent: bool = False
    has_active_legal_hold_or_tax_obligation: bool = False
    received_at: Optional[datetime] = None
    persist_request: bool = True


class StatutoryExemptionItem(BaseModel):
    statute: str
    citation: str
    exemption_category: str
    applies_to_request: bool
    scope_of_retention_or_refusal: str


class RightsEvaluateResponse(BaseModel):
    request_id: str
    tenant_id: str
    request_type: str
    normalized_subject_residence: str
    normalized_establishments: List[str]
    gdpr_applicable: bool
    gdpr_territorial_reasoning: str
    applicable_regimes: List[str]
    applicable_statutory_citations: List[str]
    non_applicable_regimes_reasoning: Dict[str, str]
    response_window_days: int
    response_day_type: str
    extension_max_days: int
    extension_conditions: str
    sla_due_date: date
    days_remaining: int
    appeal_window_days: int
    appeal_authority_escalation: str
    identity_verification_requirements: List[str]
    authorized_agent_requirements: List[str]
    statutory_exemptions: List[StatutoryExemptionItem]
    recommended_disposition: str
    received_at: datetime


class MultiJurisdictionalRightsService:
    """
    Deterministic evaluator and SLA tracker for Multi-Jurisdictional Privacy Rights (Module D).
    Implements strict GDPR Art. 3(1)/3(2) territorial boundary logic (Acceptance Test 9).
    """

    def __init__(self) -> None:
        self._requests: Dict[str, RightsEvaluateResponse] = {}

    @staticmethod
    def _is_eu_code(code: str) -> bool:
        return code == "EU" or code.startswith("EU-") or code in ("NO", "IS", "LI")

    def evaluate_request(self, tenant_id: str, req: RightsEvaluateRequest) -> RightsEvaluateResponse:
        res_code = normalize_jurisdiction_code(req.subject_residence)
        nat_code = normalize_jurisdiction_code(req.subject_nationality or "")
        est_codes = [normalize_jurisdiction_code(e) for e in req.organization_establishments if e]
        proc_codes = [normalize_jurisdiction_code(p) for p in req.processing_or_collection_locations if p] or list(est_codes)

        subject_in_eu = self._is_eu_code(res_code)
        org_has_eu_establishment = any(self._is_eu_code(e) for e in est_codes)
        org_has_ca_establishment = any(e.startswith("CA-") for e in est_codes + proc_codes)
        org_has_us_establishment = any(e.startswith("US-") for e in est_codes + proc_codes)

        # CRITICAL GDPR Art. 3(1) & Art. 3(2) Territorial Scope Check (Acceptance Test 9)
        if org_has_eu_establishment:
            gdpr_applicable = True
            gdpr_reasoning = (
                f"GDPR APPLIES under Article 3(1): The controller/processor maintains an establishment in the Union "
                f"({[e for e in est_codes if self._is_eu_code(e)]}) and processes personal data in the context of that establishment."
            )
        elif subject_in_eu and (req.targets_subject_jurisdiction or req.monitors_subject_behavior):
            gdpr_applicable = True
            triggers = []
            if req.targets_subject_jurisdiction:
                triggers.append("Art. 3(2)(a) offering of goods or services to data subjects in the Union")
            if req.monitors_subject_behavior:
                triggers.append("Art. 3(2)(b) monitoring of behavior taking place within the Union")
            gdpr_reasoning = (
                f"GDPR APPLIES extraterritorially under Article 3(2) ({' and '.join(triggers)}) "
                f"for data subject residing in {res_code}."
            )
        else:
            gdpr_applicable = False
            gdpr_reasoning = (
                f"GDPR DOES NOT APPLY under Article 3(1) or Article 3(2): Although the requester resides in {res_code}"
                + (f" (and holds {nat_code} nationality)" if nat_code else "")
                + f", GDPR applicability is NEVER triggered solely by German/EU nationality or residence. "
                f"The organization has no EU establishment ({est_codes}), does not target goods or services to the EU "
                f"(Art. 3(2)(a) = False), and does not monitor behavior within the EU (Art. 3(2)(b) = False)."
            )

        applicable_regimes: List[str] = []
        citations: List[str] = []
        non_applicable_reasons: Dict[str, str] = {}

        if not gdpr_applicable and (subject_in_eu or self._is_eu_code(nat_code)):
            non_applicable_reasons["EU_GDPR"] = gdpr_reasoning

        if gdpr_applicable:
            applicable_regimes.append("EU_GDPR")
            citations.extend([
                "GDPR Art. 12(3) (1-month response window, extendable by 2 months)",
                "GDPR Art. 15-22 (Data Subject Rights: Access, Rectification, Erasure Art. 17, Portability Art. 20, Objection Art. 21)",
            ])
            if res_code == "EU-DE":
                applicable_regimes.append("DE_BDSG")
                citations.append("German Federal Data Protection Act (BDSG) §§ 34-35 (Access & Erasure limitations)")

        # Evaluate Canadian Federal (PIPEDA) & Provincial Laws if Canadian operations/processing exist or subject in Canada
        if org_has_ca_establishment or res_code.startswith("CA-"):
            if "CA-QC" in est_codes or "CA-QC" in proc_codes or res_code == "CA-QC":
                applicable_regimes.append("CA_QC_LAW25")
                citations.append(
                    "Quebec Law 25 ss. 27-32 (Right of access, rectification, cessation of dissemination/de-indexing, portability; 30-day response window)"
                )
            if org_has_ca_establishment or res_code.startswith("CA-"):
                applicable_regimes.append("CA_PIPEDA")
                citations.append(
                    "PIPEDA Section 8(3) & Schedule 1 Principle 4.9 (Individual Access, Correction, and Withdrawal of Consent / Disposal under Principle 4.5.3; 30 calendar days response window; applies to data collected/processed by Canadian operations regardless of requester nationality)"
                )
            if ("CA-ON" in est_codes or "CA-ON" in proc_codes or res_code == "CA-ON") and any(
                c.lower() in ("health", "phi", "medical") for c in req.data_categories
            ):
                applicable_regimes.append("CA_ON_PHIPA")
                citations.append("Ontario PHIPA ss. 52-55 (Access and Correction to Personal Health Information; 30-day window)")

        # Evaluate US State / Federal Laws
        if res_code.startswith("US-"):
            if res_code == "US-CA":
                applicable_regimes.append("US_CA_CCPA_CPRA")
                citations.append(
                    "California CCPA/CPRA Cal. Civ. Code §§ 1798.105 (Deletion), 1798.106 (Correction), 1798.110 (Access), 1798.130(a)(2) (45 calendar days response window, 10 business days acknowledgement)"
                )
            elif res_code in ("US-CO", "US-CT", "US-VA", "US-TX", "US-OR", "US-DE", "US-NJ", "US-MN", "US-MD"):
                applicable_regimes.append(f"{res_code.replace('-', '_')}_STATE_PRIVACY_ACT")
                citations.append(
                    f"{res_code} Comprehensive Consumer Privacy Act (45 calendar days response window, +45 days extension, mandatory internal appeal process)"
                )
        elif org_has_us_establishment and not res_code.startswith("US-"):
            non_applicable_reasons["US_STATE_CONSUMER_PRIVACY_LAWS"] = (
                f"US state comprehensive privacy statutes (e.g., California CCPA/CPRA Cal. Civ. Code § 1798.140(i)) "
                f"define 'consumer' strictly as a natural person who is a resident of that US state. "
                f"Because the requester resides in {res_code}, US state residency-gated consumer rights do not directly attach unless extended by contract/policy."
            )
            applicable_regimes.append("US_FTC_ACT_AND_CONTRACTUAL_BASELINE")
            citations.append("FTC Act Section 5 (15 U.S.C. § 45 — honoring published privacy policy deletion/access commitments)")

        if not applicable_regimes:
            applicable_regimes.append("GLOBAL_BASELINE_PRIVACY_COMMITMENT")
            citations.append("Published Privacy Notice Contractual Fulfillment")

        # Determine strictest applicable response window
        if any(r in applicable_regimes for r in ("EU_GDPR", "CA_PIPEDA", "CA_QC_LAW25", "CA_ON_PHIPA")):
            window_days = 30
            day_type = "calendar_days"
            ext_days = 30 if "CA_PIPEDA" in applicable_regimes and not gdpr_applicable else 60
            ext_cond = (
                "PIPEDA s. 8(4): Extendable by up to 30 days if meeting the time limit would unreasonably interfere with activities or require consultations."
                if "CA_PIPEDA" in applicable_regimes and not gdpr_applicable
                else "GDPR Art. 12(3): Extendable by up to 60 days (2 further months) taking into account complexity and number of requests, with notice within 30 days."
            )
        else:
            window_days = 45
            day_type = "calendar_days"
            ext_days = 45
            ext_cond = "US State Privacy Laws (CCPA/CPA/VCDPA): Extendable once by 45 additional calendar days when reasonably necessary, provided consumer is notified within initial 45-day window."

        received = req.received_at or datetime.utcnow()
        due_date = (received + timedelta(days=window_days)).date()
        days_rem = max(0, (due_date - datetime.utcnow().date()).days)

        # Identity verification requirements
        id_verification = [
            "Match at least 2-3 data points provided by requester against existing account/transactional records (Data Minimization: do not collect new government ID unless strictly necessary for high-risk disclosure).",
            "Require authenticated session verification if the requester holds an active password-protected account.",
            "Log verification timestamp and method in immutable DSAR audit trail without retaining raw verification credentials after verification completes.",
        ]

        agent_reqs: List[str] = []
        if req.is_authorized_agent or req.request_type == RightsRequestType.AUTHORIZED_AGENT:
            agent_reqs = [
                "Signed written permission from the data subject authorizing the agent to submit the request on their behalf (CCPA 11 CCR § 7063 / PIPEDA consent verification).",
                "Direct verification of the data subject's own identity and confirmation that they granted the agent permission (unless agent provides a valid statutory Power of Attorney).",
                "Verification of the authorized agent's own business/identity registration where applicable.",
            ]

        # Statutory Exemptions (specifically addressing deletion/erasure retention conflicts)
        exemptions: List[StatutoryExemptionItem] = [
            StatutoryExemptionItem(
                statute="GDPR Art. 17(3)(b) & (e) / PIPEDA Principle 4.5.3 / CCPA § 1798.105(d)",
                citation="GDPR Art. 17(3)(b),(e); PIPEDA Schedule 1 Principle 4.5; Cal. Civ. Code § 1798.105(d)(1),(8)",
                exemption_category="legal_obligation_and_legal_claims",
                applies_to_request=req.has_active_legal_hold_or_tax_obligation or req.request_type in (RightsRequestType.DELETION, RightsRequestType.ERASURE),
                scope_of_retention_or_refusal=(
                    "Partial exemption: Records subject to mandatory statutory tax/accounting retention (e.g., 6-7 years under CRA ITA s. 230 / IRS 26 U.S.C. § 6001) "
                    "or active litigation hold must be isolated, restricted from marketing/active processing, and retained strictly for the statutory compliance purpose, "
                    "while all non-exempt commercial/marketing profile data is permanently deleted."
                ),
            ),
            StatutoryExemptionItem(
                statute="Security & Fraud Prevention Carve-Out",
                citation="Cal. Civ. Code § 1798.105(d)(2); PIPEDA s. 7(3); GDPR Recital 47",
                exemption_category="security_incident_and_fraud_prevention",
                applies_to_request=req.request_type in (RightsRequestType.DELETION, RightsRequestType.ERASURE),
                scope_of_retention_or_refusal=(
                    "Minimal suppression list / security blocklist identifiers may be retained solely to prevent fraud, detect security incidents, or honor suppression."
                ),
            ),
        ]

        appeal_authority = (
            "Office of the Privacy Commissioner of Canada (OPC) / Commission d'accès à l'information du Québec (CAI)"
            if "CA_PIPEDA" in applicable_regimes or "CA_QC_LAW25" in applicable_regimes
            else (
                "Competent EU Supervisory Authority (e.g., BfDI / German Land DPA under GDPR Art. 77)"
                if gdpr_applicable
                else "California Privacy Protection Agency (CalPrivacy) / State Attorney General (with 45-60 day internal appeal right)"
            )
        )

        disposition = (
            f"Verify requester identity; execute {req.request_type.value} across systems in {proc_codes} within {window_days} {day_type}; "
            f"apply partial legal-obligation isolation for tax/audit records if applicable; issue statutory response citing {', '.join(applicable_regimes)}."
        )

        resp = RightsEvaluateResponse(
            request_id=f"dsar_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            request_type=req.request_type.value,
            normalized_subject_residence=res_code,
            normalized_establishments=est_codes,
            gdpr_applicable=gdpr_applicable,
            gdpr_territorial_reasoning=gdpr_reasoning,
            applicable_regimes=applicable_regimes,
            applicable_statutory_citations=citations,
            non_applicable_regimes_reasoning=non_applicable_reasons,
            response_window_days=window_days,
            response_day_type=day_type,
            extension_max_days=ext_days,
            extension_conditions=ext_cond,
            sla_due_date=due_date,
            days_remaining=days_rem,
            appeal_window_days=60 if not gdpr_applicable else 30,
            appeal_authority_escalation=appeal_authority,
            identity_verification_requirements=id_verification,
            authorized_agent_requirements=agent_reqs,
            statutory_exemptions=exemptions,
            recommended_disposition=disposition,
            received_at=received,
        )
        if req.persist_request:
            self._requests[resp.request_id] = resp
        return resp

    def list_requests(self, tenant_id: str) -> List[RightsEvaluateResponse]:
        return [r for r in self._requests.values() if r.tenant_id == tenant_id]


rights_service = MultiJurisdictionalRightsService()


# ===========================================================================
# MODULE E — DATA INVENTORY, RoPA & CROSS-BORDER TRANSFERS
# ===========================================================================

class RoPARecordCreateRequest(BaseModel):
    business_process: str
    organization_role: str = Field(default="controller", description="controller, processor, joint_controller")
    controller_name_and_contact: str = "Enterprise Data Controller (privacy@enterprise.example)"
    dpo_contact: str = "Data Protection Officer (dpo@enterprise.example)"
    systems_and_applications: List[str] = Field(default_factory=list)
    databases_and_storage: List[str] = Field(default_factory=list)
    data_categories: List[str] = Field(default_factory=list)
    data_subject_categories: List[str] = Field(default_factory=lambda: ["customers", "employees"])
    purposes_of_processing: List[str] = Field(default_factory=list)
    legal_bases_by_jurisdiction: Dict[str, str] = Field(
        default_factory=lambda: {
            "EU": "GDPR Art. 6(1)(b) Contract Performance",
            "CA-FED": "PIPEDA Principle 4.3 Meaningful Consent",
            "CA-QC": "Quebec Law 25 s. 12 Express/Valid Consent",
            "US-CA": "CCPA/CPRA Notice at Collection & Business Purpose (§ 1798.140(e))",
        }
    )
    source_jurisdictions: List[str] = Field(default_factory=list)
    destination_jurisdictions: List[str] = Field(default_factory=list)
    vendors_and_recipients: List[str] = Field(default_factory=list)
    cross_border_transfer_mechanisms: List[str] = Field(default_factory=list)
    retention_schedule: str = "Active contract duration + 7 years for statutory tax/audit compliance"
    disposal_method: str = "NIST SP 800-88 Rev. 1 Cryptographic Erasure & Database Record Purging"
    technical_and_organizational_measures: List[str] = Field(
        default_factory=lambda: [
            "AES-256 Encryption at Rest",
            "TLS 1.3 in Transit",
            "Strict Tenant Isolation & RBAC/ABAC",
            "Immutable Cryptographic Audit Logging",
        ]
    )


class RoPARecord(RoPARecordCreateRequest):
    record_id: str
    tenant_id: str
    statutory_compliance_coverage: List[str]
    created_at: datetime
    updated_at: datetime


class TransferValidateRequest(BaseModel):
    source_jurisdiction: str = Field(..., description="e.g. EU-DE, EU-FR, CA-QC, CA-ON, CA-BC, CA-NS, US-CA")
    destination_jurisdiction: str = Field(..., description="e.g. US-CA, US-FED, CA-ON, GB, CH, IN")
    data_categories: List[str] = Field(default_factory=list)
    transfer_mechanisms: List[str] = Field(
        default_factory=list,
        description="e.g. ['EU_US_DPF', 'SCC_MODULE_2_C2P', 'TIA_COMPLETED', 'QUEBEC_S17_AGREEMENT', 'BCR']",
    )
    exporter_role: str = Field(default="controller", description="controller, processor")
    vendor_role: str = Field(default="processor", description="controller, processor, subprocessor")
    organization_sector: str = Field(default="private", description="private, public, health_information_custodian")
    encryption_in_transit_and_rest: bool = True
    exporter_retains_encryption_keys: bool = False


class TransferValidateResponse(BaseModel):
    validation_id: str
    source_jurisdiction: str
    destination_jurisdiction: str
    transfer_permitted: bool
    transfer_status: str = Field(..., description="permitted, conditionally_permitted, blocked_missing_safeguards")
    adequacy_status: str
    recommended_scc_module: Optional[str] = None
    tia_required: bool
    tia_completed: bool
    quebec_law25_s17_required: bool
    canadian_public_or_health_localization_restrictions: List[str]
    mandatory_remediation_steps: List[str]
    statutory_citations: List[str]
    evaluated_at: datetime


class RoPAAndTransferService:
    """
    Deterministic service for Module E:
    - Records of Processing Activities (GDPR Art. 30, Quebec Law 25, CPRA Inventory)
    - Cross-Border Transfer Validation (EU Adequacy, 2021 SCC Modules 1-4, Schrems II TIA, Quebec Law 25 s. 17, PHIPA/FOIPPA/PIIDPA)
    """

    # Jurisdictions holding an active EU Commission Adequacy Decision under GDPR Art. 45
    EU_ADEQUATE_DESTINATIONS = {
        "GB": "EU-UK Adequacy Decision (GDPR Art. 45)",
        "CH": "EU-Switzerland Adequacy Decision (GDPR Art. 45)",
        "CA-FED": "EU-Canada Commercial Adequacy Decision (2002/2/EC — applies strictly to organizations subject to PIPEDA)",
        "CA-ON": "EU-Canada Commercial Adequacy Decision (2002/2/EC — commercial activities subject to PIPEDA)",
        "CA-BC": "EU-Canada Commercial Adequacy Decision (2002/2/EC — commercial activities)",
        "CA-AB": "EU-Canada Commercial Adequacy Decision (2002/2/EC — commercial activities)",
        "US-FED": "EU-U.S. Data Privacy Framework (DPF — Implementing Decision (EU) 2023/1795, requires active DPF certification)",
        "US-CA": "EU-U.S. Data Privacy Framework (DPF — requires active DPF certification by US recipient)",
    }

    def __init__(self) -> None:
        self._ropa_store: Dict[str, RoPARecord] = {}

    def create_ropa_record(self, tenant_id: str, req: RoPARecordCreateRequest) -> RoPARecord:
        now = datetime.utcnow()
        record_id = f"ropa_{uuid.uuid4().hex[:12]}"
        src = [normalize_jurisdiction_code(s) for s in req.source_jurisdictions if s]
        dst = [normalize_jurisdiction_code(d) for d in req.destination_jurisdictions if d]

        coverage = [
            "GDPR Article 30(1) Controller / Article 30(2) Processor Record of Processing Activities",
            "Quebec Law 25 s. 3.2 Governance Policies & Register of Processing / Communication",
            "California CCPA/CPRA 11 CCR § 7150 Data Inventory & Recordkeeping",
            "PIPEDA Schedule 1 Principle 4.1.4 Openness & Accountability Inventory",
        ]

        record = RoPARecord(
            record_id=record_id,
            tenant_id=tenant_id,
            business_process=req.business_process,
            organization_role=req.organization_role,
            controller_name_and_contact=req.controller_name_and_contact,
            dpo_contact=req.dpo_contact,
            systems_and_applications=req.systems_and_applications,
            databases_and_storage=req.databases_and_storage,
            data_categories=req.data_categories,
            data_subject_categories=req.data_subject_categories,
            purposes_of_processing=req.purposes_of_processing,
            legal_bases_by_jurisdiction=req.legal_bases_by_jurisdiction,
            source_jurisdictions=src,
            destination_jurisdictions=dst,
            vendors_and_recipients=req.vendors_and_recipients,
            cross_border_transfer_mechanisms=req.cross_border_transfer_mechanisms,
            retention_schedule=req.retention_schedule,
            disposal_method=req.disposal_method,
            technical_and_organizational_measures=req.technical_and_organizational_measures,
            statutory_compliance_coverage=coverage,
            created_at=now,
            updated_at=now,
        )
        self._ropa_store[record_id] = record
        return record

    def list_ropa_records(self, tenant_id: str) -> List[RoPARecord]:
        return [r for r in self._ropa_store.values() if r.tenant_id == tenant_id]

    @staticmethod
    def _select_scc_module(exporter_role: str, vendor_role: str) -> str:
        exp = exporter_role.lower()
        imp = vendor_role.lower()
        if exp in ("controller", "joint_controller") and imp in ("controller", "joint_controller"):
            return "2021 EU SCC Module 1 (Controller-to-Controller / C2C)"
        if exp in ("controller", "joint_controller") and imp in ("processor", "subprocessor", "service_provider"):
            return "2021 EU SCC Module 2 (Controller-to-Processor / C2P)"
        if exp == "processor" and imp in ("processor", "subprocessor"):
            return "2021 EU SCC Module 3 (Processor-to-Processor / P2P)"
        if exp == "processor" and imp == "controller":
            return "2021 EU SCC Module 4 (Processor-to-Controller / P2C)"
        return "2021 EU SCC Module 2 (Controller-to-Processor / C2P)"

    def validate_transfer(self, req: TransferValidateRequest) -> TransferValidateResponse:
        src = normalize_jurisdiction_code(req.source_jurisdiction)
        dst = normalize_jurisdiction_code(req.destination_jurisdiction)
        mechs_upper = {m.upper().replace("-", "_") for m in req.transfer_mechanisms}

        is_eu_src = src == "EU" or src.startswith("EU-") or src in ("NO", "IS", "LI")
        is_eu_dst = dst == "EU" or dst.startswith("EU-") or dst in ("NO", "IS", "LI")
        is_qc_src = src == "CA-QC"
        is_ca_src = src.startswith("CA-")

        citations: List[str] = []
        remediations: List[str] = []
        localization_notes: List[str] = []
        scc_module: Optional[str] = None
        tia_required = False
        tia_completed = any("TIA" in m for m in mechs_upper)
        quebec_s17_required = False
        adequacy_status = "No cross-border adequacy evaluation required (intra-jurisdiction or domestic flow)."

        # 1. EU / EEA Outbound Transfer Logic (GDPR Chapter V)
        if is_eu_src and not is_eu_dst:
            citations.append("GDPR Chapter V (Articles 44-49)")
            scc_module = self._select_scc_module(req.exporter_role, req.vendor_role)

            if dst in ("GB", "CH"):
                adequacy_status = self.EU_ADEQUATE_DESTINATIONS[dst]
                citations.append("GDPR Article 45 (Transfer on the basis of an adequacy decision)")
            elif dst.startswith("CA-") and dst != "CA-QC":
                adequacy_status = (
                    "EU Commission Decision 2002/2/EC: Adequate for commercial processing subject to Canadian federal PIPEDA. "
                    "Non-PIPEDA processing requires 2021 EU SCCs + TIA."
                )
            elif dst.startswith("US-"):
                has_dpf = any(k in mechs_upper for k in ("EU_US_DPF", "DPF", "DATA_PRIVACY_FRAMEWORK"))
                has_scc = any("SCC" in m for m in mechs_upper)
                has_bcr = any("BCR" in m for m in mechs_upper)

                if has_dpf:
                    adequacy_status = (
                        "Covered by EU-U.S. Data Privacy Framework (Implementing Decision (EU) 2023/1795) under GDPR Art. 45, "
                        "subject to verifying the US importer's active Department of Commerce DPF list certification."
                    )
                    citations.append("European Commission Implementing Decision (EU) 2023/1795 (EU-U.S. DPF)")
                else:
                    adequacy_status = (
                        "US recipient is not relying on EU-U.S. DPF Art. 45 adequacy; requires GDPR Art. 46 Appropriate Safeguards "
                        f"({scc_module} or Binding Corporate Rules) plus a Clause 14 Transfer Impact Assessment (TIA)."
                    )
                    tia_required = True
                    citations.extend([
                        "European Commission Implementing Decision (EU) 2021/914 (2021 EU SCCs Clause 14)",
                        "CJEU C-311/18 (Schrems II) & EDPB Recommendations 01/2020 on Supplementary Measures",
                    ])
                    if not (has_scc or has_bcr):
                        remediations.append(f"Execute {scc_module} or certify under the EU-U.S. Data Privacy Framework (DPF).")
                    if not tia_completed:
                        remediations.append(
                            "Complete a Transfer Impact Assessment (TIA) under 2021 SCC Clause 14 evaluating US public authority surveillance access (Executive Order 14086 safeguards)."
                        )
            else:
                adequacy_status = f"No EU Art. 45 Adequacy Decision for {dst}. Requires {scc_module} and Clause 14 TIA."
                tia_required = True
                has_scc = any("SCC" in m or "BCR" in m for m in mechs_upper)
                if not has_scc:
                    remediations.append(f"Execute {scc_module} with the data importer in {dst}.")
                if not tia_completed:
                    remediations.append(f"Complete a Schrems II Clause 14 Transfer Impact Assessment (TIA) for {dst}.")

        # 2. Quebec Law 25 Section 17 Outbound Transfer Logic (outside Quebec, including to other Canadian provinces or US/EU)
        if is_qc_src and dst != "CA-QC":
            quebec_s17_required = True
            tia_required = True
            citations.append(
                "Quebec Law 25 s. 17 (Mandatory Privacy Impact Assessment & Written Agreement prior to communicating personal information outside Québec)"
            )
            has_qc_agreement = any(k in mechs_upper for k in ("QUEBEC_S17_AGREEMENT", "LAW25_S17", "DPA", "SCC", "SCC_MODULE_2_C2P"))
            if not tia_completed:
                remediations.append(
                    f"Complete a mandatory Quebec Law 25 s. 17 Privacy/Transfer Impact Assessment evaluating sensitivity, purposes, contractual safeguards, and the legal regime of {dst}."
                )
            if not has_qc_agreement:
                remediations.append(
                    f"Execute a written agreement under Quebec Law 25 s. 17 taking into account the TIA results and binding the recipient in {dst} to equivalent protection."
                )

        # 3. Canadian Federal PIPEDA Principle 4.1.3 Cross-Border Accountability
        if is_ca_src and not dst.startswith("CA-"):
            citations.append(
                "PIPEDA Schedule 1 Principle 4.1.3 & OPC Guidelines for Processing Personal Data Across Borders (contractual comparable level of protection & transparency notice at collection)"
            )

        # 4. Canadian Provincial Public Sector & Health Data Localization / Restrictions (Ontario PHIPA, BC FOIPPA, NS PIIDPA)
        is_health_or_public = (
            req.organization_sector in ("public", "government_agency", "health_information_custodian", "healthcare_covered_entity")
            or any(c.lower() in ("health", "phi", "medical", "public_sector") for c in req.data_categories)
        )
        if src == "CA-ON" and is_health_or_public and not dst.startswith("CA-"):
            localization_notes.append(
                "Ontario PHIPA s. 10 / s. 12 & IPC Ontario Guidance: Health Information Custodians using electronic service providers outside Ontario/Canada must complete a Threat & Risk Assessment (TRA), execute a PHIPA s. 10(4) electronic service provider agreement, and provide transparent notice to patients."
            )
            citations.append("Ontario PHIPA S.O. 2004, c. 3, ss. 10(4), 12")
        if src == "CA-BC" and is_health_or_public and not dst.startswith("CA-"):
            localization_notes.append(
                "BC Freedom of Information and Protection of Privacy Act (FOIPPA) s. 33.1(1)(p.1): Public bodies disclosing/storing personal information outside Canada must complete a mandatory Privacy Impact Assessment (PIA) under s. 69(5.3) in accordance with Ministerial directions."
            )
            citations.append("BC FOIPPA RSBC 1996, c. 165, s. 33.1 & s. 69(5.3)")
        if src == "CA-NS" and is_health_or_public and not dst.startswith("CA-"):
            localization_notes.append(
                "Nova Scotia Personal Information International Disclosure Protection Act (PIIDPA) s. 5(1): Public bodies and their service providers must store and access personal information only within Canada unless the head of the public body authorizes storage/access outside Canada as strictly necessary and reports annually to the Minister."
            )
            citations.append("Nova Scotia PIIDPA, S.N.S. 2006, c. 3, s. 5")
            if "PIIDPA_HEAD_AUTHORIZATION" not in mechs_upper:
                remediations.append(
                    "Obtain and record written authorization from the Head of the Public Body under Nova Scotia PIIDPA s. 5(2) or restrict storage/access to Canadian data centers."
                )

        if not req.encryption_in_transit_and_rest:
            remediations.append("Enforce TLS 1.3 encryption in transit and AES-256 encryption at rest prior to any cross-border transfer.")

        permitted = len(remediations) == 0
        status = "permitted" if permitted else "blocked_missing_safeguards"

        if not citations:
            citations.append("Baseline Enterprise Data Transfer Policy")

        return TransferValidateResponse(
            validation_id=f"xVal_{uuid.uuid4().hex[:12]}",
            source_jurisdiction=src,
            destination_jurisdiction=dst,
            transfer_permitted=permitted,
            transfer_status=status,
            adequacy_status=adequacy_status,
            recommended_scc_module=scc_module,
            tia_required=tia_required,
            tia_completed=tia_completed,
            quebec_law25_s17_required=quebec_s17_required,
            canadian_public_or_health_localization_restrictions=localization_notes,
            mandatory_remediation_steps=remediations,
            statutory_citations=citations,
            evaluated_at=datetime.utcnow(),
        )


ropa_transfer_service = RoPAAndTransferService()


# ===========================================================================
# MODULE F — CONSENT & PREFERENCES MANAGEMENT
# ===========================================================================

class ConsentRegimeEvaluateRequest(BaseModel):
    jurisdiction: str = Field(..., description="e.g. EU-FR, EU-DE, US-CA, US-CO, US-WA, CA-FED, CA-QC")
    activity: str = Field(
        default="website_analytics_and_targeted_advertising",
        description="e.g. website_analytics_and_targeted_advertising, email_marketing, sensitive_health_collection",
    )
    data_categories: List[str] = Field(default_factory=lambda: ["online_identifiers", "browsing_history"])
    involves_sensitive_data: bool = False
    involves_children_or_minors: bool = False
    involves_consumer_health_data: bool = False
    analytics_strictly_first_party_exempt: bool = False


class ConsentRegimeEvaluateResponse(BaseModel):
    evaluation_id: str
    normalized_jurisdiction: str
    activity: str
    consent_model: str = Field(
        ...,
        description="strict_prior_opt_in, opt_out_with_universal_signal, express_opt_in_sensitive, implied_or_express_contextual",
    )
    requires_prior_opt_in: bool
    requires_symmetric_refuse_all_button: bool
    supports_cnil_exempt_audience_measurement: bool
    universal_opt_out_gpc_mandatory: bool
    universal_opt_out_signal_spec: Optional[str] = None
    required_ui_disclosures: List[str]
    banner_and_ux_requirements: List[str]
    proof_of_consent_retention_requirements: str
    statutory_and_regulator_citations: List[str]
    evaluated_at: datetime


class ConsentRecordCreateRequest(BaseModel):
    subject_identifier: str
    jurisdiction: str
    purpose: str = "targeted_advertising_and_analytics"
    consent_status: str = Field(..., description="granted, refused, withdrawn, opted_out_via_gpc")
    collection_mechanism: str = Field(
        default="cookie_banner_explicit_action",
        description="cookie_banner_explicit_action, preference_center, gpc_signal_header, account_settings",
    )
    notice_policy_version: str = "v2026.10"
    gpc_signal_detected: bool = False
    proof_metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsentRecord(ConsentRecordCreateRequest):
    consent_id: str
    tenant_id: str
    normalized_jurisdiction: str
    recorded_at: datetime
    cryptographic_proof_hash: str


class ConsentManagementService:
    """
    Deterministic Consent & Preferences Engine (Module F).
    Enforces jurisdictionally accurate consent regimes:
    - France (EU-FR, Acceptance Test 6): GDPR + French Loi Informatique et Libertés Art. 82 + CNIL Cookie/Analytics Guidelines.
    - US Opt-Out States (US-CA, US-CO, US-CT, US-TX, etc.): Opt-out of Sale/Sharing/Targeted Advertising + mandatory GPC/UOOM without falsely imposing EU-style prior opt-in unless sensitive data / children / WA MHMDA consumer health data is involved.
    - Canada (CA-QC Law 25 s. 8.1/9.1 default maximum confidentiality & express opt-in for tracking/profiling; CA-FED PIPEDA / CASL).
    """

    US_GPC_MANDATORY_STATES = {
        "US-CA": "CCPA/CPRA Cal. Civ. Code § 1798.135(b)(1) & 11 CCR § 7025 (Mandatory Global Privacy Control / Opt-Out Preference Signal)",
        "US-CO": "Colorado Privacy Act C.R.S. § 6-1-1306(1)(a)(IV) & 4 CCR 904-3 Rule 5 (Universal Opt-Out Mechanism / UOOM)",
        "US-CT": "Connecticut CTDPA Conn. Gen. Stat. § 42-520(a)(1)(B) (Opt-Out Preference Signal)",
        "US-TX": "Texas TDPSA Tex. Bus. & Com. Code § 541.055(e) (Universal Opt-Out Signal)",
        "US-MT": "Montana MCDPA MCA § 30-14-2812 (Opt-Out Preference Signal)",
        "US-OR": "Oregon OCPA ORS § 646A.578(4) (Universal Opt-Out Mechanism)",
        "US-DE": "Delaware DPDPA 6 Del. C. § 12D-105 (Universal Opt-Out Signal)",
        "US-NJ": "New Jersey NJDPA N.J.S.A. 56:8-166.11 (Universal Opt-Out Mechanism)",
        "US-NH": "New Hampshire NHPA RSA 507-H:5 (Opt-Out Preference Signal)",
        "US-NE": "Nebraska NDPA Neb. Rev. Stat. § 87-1109 (Universal Opt-Out Signal)",
        "US-MN": "Minnesota MCDPA Minn. Stat. § 325M.14 (Universal Opt-Out Mechanism)",
        "US-MD": "Maryland MODPA Md. Code Com. Law § 14-4605 (Universal Opt-Out Mechanism)",
    }

    def __init__(self) -> None:
        self._ledger: Dict[str, ConsentRecord] = {}

    def evaluate_regime(self, req: ConsentRegimeEvaluateRequest) -> ConsentRegimeEvaluateResponse:
        jur = normalize_jurisdiction_code(req.jurisdiction)
        cats_lower = {c.lower() for c in req.data_categories}
        is_sensitive = (
            req.involves_sensitive_data
            or req.involves_children_or_minors
            or req.involves_consumer_health_data
            or bool(cats_lower & {"sensitive", "health", "phi", "biometric", "precise_geolocation", "children"})
        )

        # 1. FRANCE (EU-FR) — Acceptance Test 6: GDPR + Loi Informatique et Libertés Art. 82 + CNIL Guidelines
        if jur == "EU-FR":
            return ConsentRegimeEvaluateResponse(
                evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
                normalized_jurisdiction=jur,
                activity=req.activity,
                consent_model="strict_prior_opt_in",
                requires_prior_opt_in=True,
                requires_symmetric_refuse_all_button=True,
                supports_cnil_exempt_audience_measurement=True,
                universal_opt_out_gpc_mandatory=False,
                universal_opt_out_signal_spec="Optional enhancement; primary legal requirement in France is prior explicit opt-in under LIL Art. 82.",
                required_ui_disclosures=[
                    "Clear disclosure of every distinct processing purpose prior to depositing or reading any non-essential tracker (CNIL Deliberation 2020-091).",
                    "Complete, accessible list of all data controllers and third-party ad-tech/analytics recipients prior to consent.",
                    "Explicit notification of the right to withdraw consent at any time as easily as it was granted (GDPR Art. 7(3)).",
                ],
                banner_and_ux_requirements=[
                    "STRICT PRIOR OPT-IN: Zero targeted advertising cookies or non-exempt analytics trackers may fire before explicit affirmative user action.",
                    "SYMMETRIC 'REFUSE ALL' ('TOUT REFUSER') BUTTON: Refusing cookies must be on the first layer of the banner with the exact same visual prominence, font size, and single-click simplicity as 'Accept All' ('Tout accepter') — CNIL Deliberation 2020-092.",
                    "CNIL Audience Measurement Exemption Check: First-party analytics may only operate without prior consent if strictly limited to anonymous statistical audience measurement for the publisher's sole account, with IP anonymization, no cross-site tracking, and lifespan <= 13 months (raw data <= 25 months).",
                    "Granular purpose-by-purpose toggle controls (Analytics vs. Targeted Advertising vs. Personalization).",
                ],
                proof_of_consent_retention_requirements=(
                    "Controller must retain verifiable cryptographic/timestamped proof of consent (banner version, exact UI text, user choice) "
                    "and renew consent choices at intervals matching CNIL recommendations (typically 6 months for cookie choices, max 13 months tracker lifespan)."
                ),
                statutory_and_regulator_citations=[
                    "French Data Protection Act (Loi Informatique et Libertés n° 78-17) Article 82 (transposing ePrivacy Directive 2002/58/EC Art. 5(3))",
                    "CNIL Deliberation No. 2020-091 of September 17, 2020 (Guidelines on Article 82 of the French Data Protection Act)",
                    "CNIL Deliberation No. 2020-092 of September 17, 2020 (Recommendation on practical modalities of collecting cookie/tracker consent)",
                    "Regulation (EU) 2016/679 (GDPR) Articles 4(11), 6(1)(a), and 7",
                ],
                evaluated_at=datetime.utcnow(),
            )

        # 2. Other EU / EEA Member States (e.g., Germany EU-DE TDDDG § 25 + GDPR)
        if jur == "EU" or jur.startswith("EU-") or jur in ("NO", "IS", "LI", "GB", "CH"):
            citations = [
                "Regulation (EU) 2016/679 (GDPR) Articles 4(11), 6(1)(a), 7",
                "ePrivacy Directive 2002/58/EC Article 5(3) (Terminal Equipment Storage & Access)",
                "EDPB Report of the Work Undertaken by the Cookie Banner Taskforce (Jan 2023)",
            ]
            if jur == "EU-DE":
                citations.append("German Telecommunications Digital Services Data Protection Act (TDDDG / formerly TTDSG) § 25")
            return ConsentRegimeEvaluateResponse(
                evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
                normalized_jurisdiction=jur,
                activity=req.activity,
                consent_model="strict_prior_opt_in",
                requires_prior_opt_in=True,
                requires_symmetric_refuse_all_button=True,
                supports_cnil_exempt_audience_measurement=False,
                universal_opt_out_gpc_mandatory=False,
                universal_opt_out_signal_spec=None,
                required_ui_disclosures=[
                    "Prior clear information on tracker purposes, lifespan, and third-party recipients.",
                    "First-layer Reject All button without deceptive dark patterns (EDPB Cookie Taskforce).",
                ],
                banner_and_ux_requirements=[
                    "Prior affirmative opt-in required before setting or reading non-essential analytics or advertising cookies.",
                    "Equal-prominence Reject All button on Layer 1.",
                    "Persistent icon/link to withdraw consent at any time (GDPR Art. 7(3)).",
                ],
                proof_of_consent_retention_requirements=(
                    "GDPR Art. 7(1): Controller must maintain auditable logs demonstrating when, how, and to which policy version the data subject consented."
                ),
                statutory_and_regulator_citations=citations,
                evaluated_at=datetime.utcnow(),
            )

        # 3. QUEBEC (CA-QC) — Law 25 ss. 8.1, 9.1, 12, 14 (Opt-in for tracking/profiling/identification & default privacy)
        if jur == "CA-QC":
            return ConsentRegimeEvaluateResponse(
                evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
                normalized_jurisdiction=jur,
                activity=req.activity,
                consent_model="strict_prior_opt_in",
                requires_prior_opt_in=True,
                requires_symmetric_refuse_all_button=True,
                supports_cnil_exempt_audience_measurement=False,
                universal_opt_out_gpc_mandatory=False,
                universal_opt_out_signal_spec=None,
                required_ui_disclosures=[
                    "Quebec Law 25 s. 8.1: Mandatory prior disclosure of the use of any technology that includes functions allowing the person to be identified, located, or profiled, and of the means available to activate those functions.",
                    "Quebec Law 25 s. 9.1: Technological products/services must have confidentiality parameters set by default to the highest level of confidentiality without user intervention.",
                ],
                banner_and_ux_requirements=[
                    "Profiling, location, or behavioral tracking functions must be deactivated by default and require explicit activation/opt-in by the user (Law 25 s. 8.1 & CAI Cookie Guidance).",
                    "Consent must be manifest, free, and enlightened, and given for specific purposes in simple and clear terms (Law 25 s. 14).",
                ],
                proof_of_consent_retention_requirements=(
                    "Retain timestamped proof of express activation of profiling/tracking functions and privacy notice version under Law 25 s. 3.2 & s. 14."
                ),
                statutory_and_regulator_citations=[
                    "Quebec Act respecting the protection of personal information in the private sector (Law 25) ss. 8.1, 9.1, 12, 14",
                    "Commission d'accès à l'information du Québec (CAI) Guidelines on Criteria for Valid Consent",
                ],
                evaluated_at=datetime.utcnow(),
            )

        # 4. CANADA FEDERAL / OTHER PROVINCES (CA-FED, CA-ON, CA-BC, CA-AB)
        if jur.startswith("CA-"):
            requires_express = is_sensitive or "targeted" in req.activity.lower() or "cross_site" in req.activity.lower()
            return ConsentRegimeEvaluateResponse(
                evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
                normalized_jurisdiction=jur,
                activity=req.activity,
                consent_model="express_opt_in_sensitive" if requires_express else "implied_or_express_contextual",
                requires_prior_opt_in=requires_express,
                requires_symmetric_refuse_all_button=requires_express,
                supports_cnil_exempt_audience_measurement=False,
                universal_opt_out_gpc_mandatory=False,
                universal_opt_out_signal_spec=None,
                required_ui_disclosures=[
                    "PIPEDA Section 6.1 & OPC Guidelines for Obtaining Meaningful Consent: Upfront emphasis on 4 key elements (what personal information is collected, with whom it is shared, for what purposes, and risk of residual harm).",
                    "CASL (S.C. 2010, c. 23) s. 6 & s. 8: Express consent required for commercial electronic messages or installation of computer programs.",
                ],
                banner_and_ux_requirements=[
                    "Express opt-in required where tracking involves sensitive information or falls outside reasonable expectations of the individual (OPC Online Behavioral Advertising Guidelines).",
                    "Accessible opt-out / withdrawal mechanism that takes effect immediately.",
                ],
                proof_of_consent_retention_requirements="Maintain auditable record of express/implied consent basis and notice version per PIPEDA Principle 4.3 & CASL.",
                statutory_and_regulator_citations=[
                    "Personal Information Protection and Electronic Documents Act (PIPEDA) s. 6.1 & Schedule 1 Principle 4.3",
                    "OPC Guidelines for Obtaining Meaningful Consent & Policy Position on Online Behavioral Advertising",
                    "Canada's Anti-Spam Legislation (CASL), S.C. 2010, c. 23",
                ],
                evaluated_at=datetime.utcnow(),
            )

        # 5. UNITED STATES — Special Case: Washington My Health My Data Act (US-WA Consumer Health Data) or Sensitive/Children
        if jur.startswith("US-") and is_sensitive:
            citations = [
                "Virginia VCDPA § 59.1-578(A)(5) / Colorado CPA C.R.S. § 6-1-1308(7) (Prior Opt-In Consent for Sensitive Data)",
                "COPPA 15 U.S.C. § 6502 (Verifiable Parental Consent for Children Under 13)",
            ]
            if jur == "US-WA" or req.involves_consumer_health_data:
                citations.insert(
                    0,
                    "Washington My Health My Data Act (MHMDA) RCW 19.373.030 (Separate affirmative opt-in consent required for collection/sharing of consumer health data; signed valid authorization under RCW 19.373.060 required for sale)",
                )
            return ConsentRegimeEvaluateResponse(
                evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
                normalized_jurisdiction=jur,
                activity=req.activity,
                consent_model="express_opt_in_sensitive",
                requires_prior_opt_in=True,
                requires_symmetric_refuse_all_button=True,
                supports_cnil_exempt_audience_measurement=False,
                universal_opt_out_gpc_mandatory=jur in self.US_GPC_MANDATORY_STATES,
                universal_opt_out_signal_spec=self.US_GPC_MANDATORY_STATES.get(jur),
                required_ui_disclosures=[
                    "Clear and conspicuous disclosure of sensitive/consumer health data categories, specific purposes, and third-party recipients prior to collection.",
                    "Separate, standalone consent prompt (cannot be bundled into general Terms of Service).",
                ],
                banner_and_ux_requirements=[
                    "Affirmative prior opt-in required because processing involves sensitive personal data, children/teens, or consumer health data (MHMDA / state sensitive data rules).",
                ],
                proof_of_consent_retention_requirements="Retain timestamped affirmative consent record (and for WA MHMDA sales, retain signed authorization for 6 years).",
                statutory_and_regulator_citations=citations,
                evaluated_at=datetime.utcnow(),
            )

        # 6. UNITED STATES — Standard Commercial / Website Analytics & Targeted Advertising (Opt-Out + Mandatory GPC/UOOM)
        gpc_mandatory = jur in self.US_GPC_MANDATORY_STATES
        gpc_spec = self.US_GPC_MANDATORY_STATES.get(
            jur,
            "Voluntary best practice in non-comprehensive US states; mandatory under CCPA/CPA/CTDPA/TDPSA.",
        )
        us_citations = [
            "California CCPA/CPRA Cal. Civ. Code §§ 1798.100 (Notice at Collection), 1798.120 (Right to Opt-Out of Sale/Sharing), 1798.135 ( Opt-Out Links & Global Privacy Control)",
            "FTC Act Section 5 (15 U.S.C. § 45 — prohibition on deceptive tracking disclosures)",
        ]
        if jur in self.US_GPC_MANDATORY_STATES:
            us_citations.insert(0, self.US_GPC_MANDATORY_STATES[jur])

        return ConsentRegimeEvaluateResponse(
            evaluation_id=f"cReg_{uuid.uuid4().hex[:12]}",
            normalized_jurisdiction=jur,
            activity=req.activity,
            consent_model="opt_out_with_universal_signal",
            requires_prior_opt_in=False,
            requires_symmetric_refuse_all_button=False,
            supports_cnil_exempt_audience_measurement=True,
            universal_opt_out_gpc_mandatory=gpc_mandatory,
            universal_opt_out_signal_spec=gpc_spec,
            required_ui_disclosures=[
                "Notice at Collection disclosing categories of personal information collected and whether data is sold or shared for cross-context behavioral / targeted advertising.",
                "Clear and conspicuous 'Do Not Sell or Share My Personal Information' / 'Your Privacy Choices' link in website footer.",
            ],
            banner_and_ux_requirements=[
                "DO NOT falsely impose GDPR-style prior opt-in blocking for non-sensitive adult website analytics/advertising in US opt-out states.",
                "Honor incoming Global Privacy Control (GPC / Sec-GPC: 1) HTTP header and DOM navigator.globalPrivacyControl signals automatically without friction.",
                "Provide frictionless opt-out of cross-context behavioral advertising / sale of personal data without requiring account creation.",
            ],
            proof_of_consent_retention_requirements=(
                "Respect opt-out state and GPC signal continuously; under CCPA 11 CCR § 7026(f), wait at least 12 months before asking an opted-out consumer to opt back in."
            ),
            statutory_and_regulator_citations=us_citations,
            evaluated_at=datetime.utcnow(),
        )

    def create_consent_record(self, tenant_id: str, req: ConsentRecordCreateRequest) -> ConsentRecord:
        now = datetime.utcnow()
        cid = f"cns_{uuid.uuid4().hex[:12]}"
        jur = normalize_jurisdiction_code(req.jurisdiction)
        status = "opted_out_via_gpc" if req.gpc_signal_detected and req.consent_status == "refused" else req.consent_status
        hash_payload = (
            f"{cid}|{tenant_id}|{req.subject_identifier}|{jur}|{req.purpose}|"
            f"{status}|{req.notice_policy_version}|{now.isoformat()}"
        )
        proof_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        record = ConsentRecord(
            consent_id=cid,
            tenant_id=tenant_id,
            subject_identifier=req.subject_identifier,
            jurisdiction=req.jurisdiction,
            normalized_jurisdiction=jur,
            purpose=req.purpose,
            consent_status=status,
            collection_mechanism=req.collection_mechanism,
            notice_policy_version=req.notice_policy_version,
            gpc_signal_detected=req.gpc_signal_detected,
            proof_metadata=req.proof_metadata,
            recorded_at=now,
            cryptographic_proof_hash=proof_hash,
        )
        self._ledger[cid] = record
        return record

    def list_consent_records(self, tenant_id: str, subject_identifier: Optional[str] = None) -> List[ConsentRecord]:
        items = [r for r in self._ledger.values() if r.tenant_id == tenant_id]
        if subject_identifier:
            items = [r for r in items if r.subject_identifier == subject_identifier]
        return items


consent_service = ConsentManagementService()


# ===========================================================================
# FASTAPI ENDPOINTS — MODULES B, D, E, F
# ===========================================================================

# --- Module B: Privacy Assessments ---

@router.post("/assessments/recommend", response_model=AssessmentRecommendResponse)
def recommend_assessments_endpoint(
    payload: AssessmentRecommendRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> AssessmentRecommendResponse:
    """
    Deterministically select required privacy assessments (PIA, DPIA, TRA, TIA, LIA, AIIA,
    VENDOR_PRIVACY, DATA_SHARING, CHANGE_IMPACT), statutory questions, required evidence,
    and approval gates (`DPO`, `CPO`, `LEGAL`, `CISO`). Works 100% offline.
    """
    return assessment_service.recommend_assessments(payload)


@router.post("/assessments", response_model=AssessmentInstance)
def create_assessment_endpoint(
    payload: AssessmentCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> AssessmentInstance:
    """Create a tenant-scoped jurisdiction-specific privacy assessment instance."""
    return assessment_service.create_assessment(tenant_id, payload)


@router.get("/assessments", response_model=List[AssessmentInstance])
def list_assessments_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[AssessmentInstance]:
    """List all privacy assessments strictly filtered by the active tenant."""
    return assessment_service.list_assessments(tenant_id)


@router.get("/assessments/{assessment_id}", response_model=AssessmentInstance)
def get_assessment_endpoint(
    assessment_id: str,
    tenant_id: str = Depends(resolve_tenant_id),
) -> AssessmentInstance:
    """Retrieve a single privacy assessment instance strictly scoped to the active tenant."""
    return assessment_service.get_assessment(tenant_id, assessment_id)


@router.post("/assessments/{assessment_id}/approve", response_model=AssessmentInstance)
def approve_assessment_endpoint(
    assessment_id: str,
    payload: AssessmentApproveRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> AssessmentInstance:
    """Record a human-in-the-loop approval gate with role, rationale, and cryptographic hash."""
    return assessment_service.approve_assessment(tenant_id, assessment_id, payload)


# --- Module D: Multi-Jurisdictional Privacy Rights ---

@router.post("/rights/evaluate-request", response_model=RightsEvaluateResponse)
def evaluate_rights_request_endpoint(
    payload: RightsEvaluateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> RightsEvaluateResponse:
    """
    Evaluate a cross-border or domestic privacy rights request across all 9 request types.
    Enforces strict GDPR Art. 3(1)/3(2) territorial scope (never assuming GDPR from EU residence/nationality alone)
    and calculates statutory response windows, identity verification rules, and exemptions.
    """
    return rights_service.evaluate_request(tenant_id, payload)


@router.get("/rights/requests", response_model=List[RightsEvaluateResponse])
def list_rights_requests_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[RightsEvaluateResponse]:
    """List tenant-scoped privacy rights requests with live SLA countdowns and appeal windows."""
    return rights_service.list_requests(tenant_id)


# --- Module E: Data Inventory, RoPA & Cross-Border Transfers ---

@router.post("/ropa/records", response_model=RoPARecord)
def create_ropa_record_endpoint(
    payload: RoPARecordCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> RoPARecord:
    """Create a tenant-scoped Record of Processing Activities (GDPR Art. 30 / Quebec Law 25 / CPRA)."""
    return ropa_transfer_service.create_ropa_record(tenant_id, payload)


@router.get("/ropa/records", response_model=List[RoPARecord])
def list_ropa_records_endpoint(
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[RoPARecord]:
    """List tenant-scoped RoPA records."""
    return ropa_transfer_service.list_ropa_records(tenant_id)


@router.post("/transfers/validate", response_model=TransferValidateResponse)
def validate_transfer_endpoint(
    payload: TransferValidateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> TransferValidateResponse:
    """
    Validate cross-border data transfers against EU Adequacy Decisions, 2021 EU SCC Modules 1-4,
    Schrems II Clause 14 TIA, Quebec Law 25 s. 17, and Canadian provincial public/health storage rules.
    """
    return ropa_transfer_service.validate_transfer(payload)


# --- Module F: Consent & Preferences Management ---

@router.post("/consent/evaluate-regime", response_model=ConsentRegimeEvaluateResponse)
def evaluate_consent_regime_endpoint(
    payload: ConsentRegimeEvaluateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> ConsentRegimeEvaluateResponse:
    """
    Evaluate the legally accurate consent model for a jurisdiction and activity
    (e.g., France CNIL/LIL Art. 82 strict prior opt-in + symmetric Refuse All vs. US state opt-out + GPC/UOOM).
    """
    return consent_service.evaluate_regime(payload)


@router.post("/consent/records", response_model=ConsentRecord)
def create_consent_record_endpoint(
    payload: ConsentRecordCreateRequest,
    tenant_id: str = Depends(resolve_tenant_id),
) -> ConsentRecord:
    """Record a tenant-scoped consent or withdrawal event with notice version and cryptographic proof."""
    return consent_service.create_consent_record(tenant_id, payload)


@router.get("/consent/records", response_model=List[ConsentRecord])
def list_consent_records_endpoint(
    subject_identifier: Optional[str] = Query(default=None),
    tenant_id: str = Depends(resolve_tenant_id),
) -> List[ConsentRecord]:
    """List tenant-scoped consent and withdrawal records."""
    return consent_service.list_consent_records(tenant_id, subject_identifier=subject_identifier)
