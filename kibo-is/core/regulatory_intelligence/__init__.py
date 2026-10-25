"""
KIBO Privacy OS — Continuous Regulatory Intelligence, Discovery & Legal Annotation Schemas
Owned by Orchestrator A0 as the shared contract across G01-G24, C01-C05, X01-X05, and D01-D02.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DiscoveryStatusCode(str, Enum):
    OK = "OK"
    VERIFIED = "OK"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    UNVERIFIED = "UNVERIFIED"
    REQUIRES_LEGAL_REVIEW = "REQUIRES_LEGAL_REVIEW"
    QUARANTINED = "QUARANTINED"
    BLOCKED_SECURITY = "BLOCKED_SECURITY"


VerificationStatus = DiscoveryStatusCode


class LegalPromotionState(str, Enum):
    DISCOVERED = "DISCOVERED"
    RETRIEVED = "RETRIEVED"
    VERIFIED_SOURCE = "VERIFIED_SOURCE"
    ANNOTATED = "ANNOTATED"
    TECHNICALLY_VALIDATED = "TECHNICALLY_VALIDATED"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    SUSPENDED = "SUSPENDED"
    REQUIRES_LEGAL_REVIEW = "REQUIRES_LEGAL_REVIEW"


class DocumentClassType(str, Enum):
    STATUTE = "statute"
    REGULATION = "regulation"
    LEGISLATIVE_BILL = "legislative_bill"
    OFFICIAL_GUIDANCE = "official_guidance"
    REGULATORY_ENFORCEMENT_DECISION = "regulatory_enforcement_decision"
    ADMINISTRATIVE_TRIBUNAL_RULING = "administrative_tribunal_ruling"
    COURT_JUDGMENT = "court_judgment"
    CONSENT_ORDER_SETTLEMENT = "consent_order_settlement"
    REGULATORY_CONSULTATION = "regulatory_consultation"
    OFFICIAL_POLICY_DIRECTIVE = "official_policy_directive"


class SourceHealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNREACHABLE = "unreachable"
    REQUIRES_CREDENTIALS = "requires_credentials"
    STALE_CHECKPOINT = "stale_checkpoint"
    RATE_LIMITED = "rate_limited"


class RegulatorySourceEntry(BaseModel):
    """Section 4.1 — Curated machine-readable source registry entry."""
    source_id: str = Field(..., description="Unique source identifier, e.g. SRC-US-FED-ECFR")
    jurisdiction_id: str = Field(..., description="Canonical jurisdiction code, e.g. US-FED, US-CA, CA-ON, EU-DE")
    parent_jurisdiction: Optional[str] = Field(default=None, description="Parent jurisdiction, e.g. US-FED, CA-FED, EU")
    authority_name: str = Field(..., description="Official issuing authority or court/regulator name")
    authority_type: str = Field(
        ...,
        description="legislature, data_protection_authority, sector_regulator, attorney_general, court, tribunal, official_gazette",
    )
    official_domain: str = Field(..., description="Authoritative domain allowlist entry, e.g. eur-lex.europa.eu")
    discovery_endpoint: str = Field(..., description="Official API, XML, RSS/Atom, bulk download, or structured URL")
    feed_format: str = Field(..., description="api_json, xml_akoma_ntoso, xml_justice_ca, rss_atom, cellar_rdf, html_structured, bulk_zip")
    auth_requirements: str = Field(default="public_unauthenticated", description="public_unauthenticated, api_key, oauth2, licensed_token")
    licensing_and_reuse: str = Field(
        default="Crown Copyright / Public Domain / EU Decision 2011/833/EU — attribution required",
        description="Licensing and reuse terms",
    )
    rate_limit_rpm: int = Field(default=30, description="Max requests per minute")
    update_frequency: str = Field(default="daily", description="every_6_hours, daily, weekly, controlled_backfill")
    publication_coverage: List[str] = Field(
        default_factory=lambda: ["privacy", "data_protection", "cybersecurity"],
        description="Substantive domains covered",
    )
    legal_instrument_types: List[str] = Field(
        default_factory=lambda: ["statute", "regulation"],
        description="DocumentClassType values provided by this source",
    )
    source_priority: int = Field(default=1, description="1 = primary authoritative, 2 = official mirror")
    languages: List[str] = Field(default_factory=lambda: ["en"], description="ISO 639-1 language codes")
    last_successful_retrieval: Optional[datetime] = None
    last_failed_retrieval: Optional[datetime] = None
    health_status: SourceHealthStatus = SourceHealthStatus.HEALTHY
    checkpoint_cursor: Optional[str] = None


class CanonicalLegalDocument(BaseModel):
    """Section 6.1 — Versioned Canonical Document Record."""
    document_id: str
    document_type: DocumentClassType
    canonical_title: str
    jurisdiction_id: str
    parent_jurisdictions: List[str] = Field(default_factory=list)
    issuing_authority: str
    issuing_authority_type: str
    official_source_url: str
    official_document_id: Optional[str] = None
    official_citation: Optional[str] = None
    neutral_citation: Optional[str] = None
    eli_or_celex_identifier: Optional[str] = None
    docket_or_case_number: Optional[str] = None
    publication_date: Optional[date] = None
    decision_date: Optional[date] = None
    effective_date: Optional[date] = None
    repeal_or_expiry_date: Optional[date] = None
    source_last_modified: Optional[datetime] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"
    translation_status: str = Field(
        default="original_authoritative",
        description="original_authoritative, official_bilingual_coauthoritative, verified_translation, unverified_machine_translation",
    )
    raw_document_sha256: str
    normalized_text_sha256: str
    document_version: str = "1.0.0"
    supersedes: Optional[str] = None
    amends: List[str] = Field(default_factory=list)
    is_amended_by: List[str] = Field(default_factory=list)
    appeal_status: Optional[str] = Field(default=None, description="none, under_appeal, affirmed, reversed, modified")
    binding_status: str = Field(default="binding_statute", description="binding_statute, binding_regulation, binding_precedent, administrative_order, persuasive_guidance")
    review_status: LegalPromotionState = LegalPromotionState.VERIFIED_SOURCE
    license: str = "Public / Official Government Publication"
    source_snapshot_reference: str
    normalized_text: str = ""
    original_language_passages: Dict[str, str] = Field(default_factory=dict)
    translated_passages: Dict[str, str] = Field(default_factory=dict)


class LegalPassageAnnotation(BaseModel):
    """Section 6.2 — Passage-level source-grounded Legal Annotation Model."""
    annotation_id: str
    document_id: str
    document_version: str
    annotation_type: str = Field(
        default="statutory_obligation",
        description="statutory_obligation, prohibition, exemption, threshold, deadline, definition, judicial_holding, judicial_dicta, remedy_order",
    )
    jurisdiction_id: str
    source_section: str
    article: Optional[str] = None
    subsection: Optional[str] = None
    paragraph: Optional[str] = None
    page_number: Optional[int] = None
    text_start_offset: int
    text_end_offset: int
    exact_source_excerpt: str
    source_language: str = "en"
    normalized_legal_concept: str
    plain_language_explanation: str
    legal_requirement: str
    applicability_conditions: List[str] = Field(default_factory=list)
    exemptions: List[str] = Field(default_factory=list)
    thresholds: Dict[str, Any] = Field(default_factory=dict)
    effective_date: Optional[date] = None
    statutory_deadline: Optional[str] = None
    affected_organization_types: List[str] = Field(default_factory=list)
    affected_industries: List[str] = Field(default_factory=list)
    affected_data_categories: List[str] = Field(default_factory=list)
    affected_processing_activities: List[str] = Field(default_factory=list)
    regulatory_authority: str
    required_controls: List[str] = Field(default_factory=list)
    required_assessments: List[str] = Field(default_factory=list)
    related_regulations: List[str] = Field(default_factory=list)
    related_decisions: List[str] = Field(default_factory=list)
    interpretation_status: str = Field(
        default="source_grounded_deterministic",
        description="source_grounded_deterministic, requires_legal_review, verified_by_counsel",
    )
    evidence_strength: str = Field(default="authoritative_primary_text")
    extraction_model: str = Field(default="kibo-deterministic-legal-parser-v2")
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    verification_status: str = Field(default="VERIFIED", description="VERIFIED, UNVERIFIED, REQUIRES_LEGAL_REVIEW, REJECTED")
    reviewer: Optional[str] = None
    review_timestamp: Optional[datetime] = None


class DecisionVerdictAnnotation(BaseModel):
    """Section 6.3 — Case Law, Regulator Enforcement Action, and Tribunal Ruling Annotation."""
    decision_id: str
    document_id: str
    case_name: str
    neutral_citation_or_id: str
    court_tribunal_or_regulator: str
    jurisdiction_id: str
    decision_date: date
    parties: List[str] = Field(default_factory=list)
    material_facts: str
    legal_issues: List[str] = Field(default_factory=list)
    statutory_provisions_considered: List[str] = Field(default_factory=list)
    relevant_reasoning_passages: List[Dict[str, Any]] = Field(default_factory=list)
    legal_holdings: List[str] = Field(default_factory=list)
    dicta_and_commentary: List[str] = Field(default_factory=list)
    operative_orders: List[str] = Field(default_factory=list)
    remedies_and_penalties: List[str] = Field(default_factory=list)
    binding_vs_persuasive_status: str = Field(
        default="binding_administrative_order",
        description="binding_precedent, binding_administrative_order, persuasive_authority, requires_legal_review",
    )
    concurring_or_dissenting_notes: Optional[str] = None
    subsequent_appeals: List[str] = Field(default_factory=list)
    reversals_or_modifications: List[str] = Field(default_factory=list)
    related_cases: List[str] = Field(default_factory=list)
    related_statutory_provisions: List[str] = Field(default_factory=list)
    practical_privacy_program_implications: List[str] = Field(default_factory=list)
    review_status: LegalPromotionState = LegalPromotionState.VERIFIED_SOURCE


class CitationVerificationResult(BaseModel):
    """Section 6.4 — Passage-level Citation Verification result."""
    citation_query: str
    document_id: Optional[str] = None
    valid: bool
    status: DiscoveryStatusCode
    document_identity_verified: bool = False
    citation_accuracy_verified: bool = False
    section_existence_verified: bool = False
    passage_consistency_verified: bool = False
    version_applicability_verified: bool = False
    authority_identity_verified: bool = False
    effective_date_relevance_verified: bool = False
    matched_offset_start: Optional[int] = None
    matched_offset_end: Optional[int] = None
    matched_excerpt: Optional[str] = None
    rejection_reasons: List[str] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class ProvisionDiffRecord(BaseModel):
    """Section 5.2 & RD-03/RD-04 — Provision-level structural amendment diff."""
    diff_id: str
    document_id: str
    jurisdiction_id: str
    provision_ref: str
    previous_version: str
    current_version: str
    previous_effective_date: Optional[date] = None
    current_effective_date: Optional[date] = None
    previous_text: str
    current_text: str
    Previous_sha256: str = ""
    current_sha256: str = ""
    change_type: str = Field(
        ...,
        description="substantive_amendment, new_provision, repealed_provision, deadline_change, threshold_change, editorial_formatting_only",
    )
    is_substantive: bool = True
    changed_elements_summary: List[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


def compute_sha256_hex(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


# Canonical aliases used by Applicability, Impact Analysis, and Promotion Workflow engines (G21)
StatutoryAnnotation = LegalPassageAnnotation
DecisionAnnotation = DecisionVerdictAnnotation


class RemediationTaskSpec(BaseModel):
    """Section 9 & RD-09 — Prioritized remediation task with statutory deadline and human approval gate."""
    task_id: str
    jurisdiction_id: str
    priority: str = Field(..., description="P0, P1, or P2")
    title: str
    description: str
    statutory_deadline: str
    owner_role: str = Field(default="DPO", description="CPO, DPO, or LEGAL")
    affected_artifacts: List[str] = Field(default_factory=list)
    citation_reference: str = ""
    requires_human_approval: bool = True


class JurisdictionBlastRadius(BaseModel):
    """Section 9 & RD-09 — Per-jurisdiction blast radius breakdown for a tenant."""
    jurisdiction_id: str
    jurisdiction_name: str
    applicable: bool = True
    competent_authority: str
    triggered_by_facts: List[str] = Field(default_factory=list)
    affected_organizations: List[Dict[str, Any]] = Field(default_factory=list)
    affected_establishments: List[str] = Field(default_factory=list)
    affected_processing_activities: List[Dict[str, Any]] = Field(default_factory=list)
    affected_data_categories: List[str] = Field(default_factory=list)
    affected_data_subjects: List[str] = Field(default_factory=list)
    triggered_assessments: List[str] = Field(default_factory=list)
    affected_contracts_dpas_sccs: List[Dict[str, Any]] = Field(default_factory=list)
    affected_retention_schedules: List[Dict[str, Any]] = Field(default_factory=list)
    affected_notices: List[Dict[str, Any]] = Field(default_factory=list)
    affected_dsar_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    affected_controls: List[str] = Field(default_factory=list)
    affected_evidence_artifacts: List[str] = Field(default_factory=list)
    remediation_tasks: List[RemediationTaskSpec] = Field(default_factory=list)
    required_human_approvals: List[str] = Field(default_factory=lambda: ["CPO", "DPO", "LEGAL"])

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ImpactAssessmentReport(BaseModel):
    """Section 9 & RD-09 — Multi-jurisdictional tenant blast radius and impact analysis report."""
    report_id: str
    tenant_id: str = "enterprise-multi-jurisdiction-tenant"
    organization_name: str
    trigger_record_id: str
    trigger_record_type: str = Field(
        default="regulatory_change",
        description="statutory_annotation, decision_annotation, provision_diff, canonical_document",
    )
    trigger_title: str
    trigger_citation: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    evaluated_jurisdictions: List[str] = Field(default_factory=list)
    affected_jurisdictions: List[str] = Field(default_factory=list)
    per_jurisdiction_blast_radius: Dict[str, JurisdictionBlastRadius] = Field(default_factory=dict)
    affected_organizations: List[Dict[str, Any]] = Field(default_factory=list)
    affected_establishments: List[str] = Field(default_factory=list)
    affected_processing_activities: List[Dict[str, Any]] = Field(default_factory=list)
    affected_data_categories: List[str] = Field(default_factory=list)
    affected_data_subjects: List[str] = Field(default_factory=list)
    triggered_assessments: List[str] = Field(default_factory=list)
    affected_contracts: List[Dict[str, Any]] = Field(default_factory=list)
    affected_retention_schedules: List[Dict[str, Any]] = Field(default_factory=list)
    affected_notices: List[Dict[str, Any]] = Field(default_factory=list)
    affected_dsar_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    affected_controls: List[str] = Field(default_factory=list)
    affected_evidence_artifacts: List[str] = Field(default_factory=list)
    recommended_remediation_tasks: List[RemediationTaskSpec] = Field(default_factory=list)
    required_human_approvals: List[str] = Field(default_factory=lambda: ["CPO", "DPO", "LEGAL"])
    requires_legal_review: bool = True
    summary: str = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class PromotionTransitionAuditRecord(BaseModel):
    """Section 10 & RD-16 — Immutable audit trail record of a legal promotion state transition."""
    audit_id: str
    candidate_id: str
    from_state: Optional[LegalPromotionState] = None
    to_state: LegalPromotionState
    transitioned_at: datetime = Field(default_factory=datetime.utcnow)
    actor_id: str
    actor_role: str
    review_notes: str = ""
    source_hash: str = ""
    verbatim_quote: str = ""
    citation_verification_status: Optional[str] = None
    citation_verified: bool = False
    superseded_by_id: Optional[str] = None
    emergency_reason: Optional[str] = None
    previous_audit_hash: str = "GENESIS"
    record_sha256: str = ""

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

