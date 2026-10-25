"""
Canonical Regulation Model & Jurisdictional Regulatory Applicability Engine (JRAE) Schemas.
Enforces Section 3 & Section 7 of the KIBO Privacy OS specification.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JurisdictionType(str, Enum):
    SUPRANATIONAL = "supranational"
    FEDERAL = "federal"
    STATE = "state"
    PROVINCE = "province"
    TERRITORY = "territory"
    MEMBER_STATE = "member_state"
    SUBNATIONAL = "subnational"
    SECTORAL = "sectoral"


class RegulatoryStatus(str, Enum):
    PROPOSED = "proposed"
    ENACTED_NOT_EFFECTIVE = "enacted_not_effective"
    EFFECTIVE = "effective"
    AMENDED = "amended"
    REPEALED = "repealed"
    SUPERSEDED = "superseded"
    UNDER_LEGAL_REVIEW = "under_legal_review"


class DeploymentStatus(str, Enum):
    DISCOVERED = "discovered"
    PARSED = "parsed"
    TESTED = "tested"
    LEGALLY_REVIEWED = "legally_reviewed"
    APPROVED = "approved"
    PRODUCTION_ENABLED = "production_enabled"


class LegalReviewStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REQUIRES_COUNSEL_SIGNOFF = "requires_counsel_signoff"
    REJECTED = "rejected"


class JurisdictionEntry(BaseModel):
    jurisdiction_id: str = Field(..., description="ISO-like canonical code e.g. US-FED, US-CA, CA-FED, CA-ON, CA-QC, EU, EU-DE, EU-FR, EU-IE")
    name: str
    jurisdiction_type: JurisdictionType
    country: str
    state_or_province: Optional[str] = None
    member_state: Optional[str] = None
    parent_jurisdiction_id: Optional[str] = None
    primary_regulator: str
    regulator_url: str
    subnational_authorities: List[Dict[str, str]] = Field(default_factory=list)
    has_comprehensive_privacy_law: bool = True
    catalogued: bool = True
    implemented: bool = True
    tested: bool = True
    legally_reviewed: bool = True
    production_enabled: bool = True


class StatutoryThreshold(BaseModel):
    metric: str = Field(..., description="e.g., annual_revenue_usd, consumer_records_count, data_broker_revenue_pct, employee_count")
    operator: str = Field(..., description=">=, >, ==, in")
    value: Any
    currency: Optional[str] = None
    logic_group: str = Field(default="OR", description="AND / OR group for multi-prong thresholds (e.g. CCPA 3 prongs)")
    description: str


class ExemptionRule(BaseModel):
    exemption_id: str
    exemption_type: str = Field(..., description="entity_level, data_level, activity_level")
    condition_field: str
    condition_values: List[str]
    carve_out_statute: Optional[str] = None
    description: str


class PreemptionRule(BaseModel):
    rule_id: str
    preempts_or_yields: str = Field(..., description="preempts, yields_to, concurrent_with, opening_clause_derogation")
    target_regulation_id: str
    scope_condition: str
    description: str


class ResponseDeadlineSpec(BaseModel):
    rights_request_initial_days: Optional[int] = None
    rights_request_day_type: str = "calendar_days"
    rights_request_extension_days: Optional[int] = None
    rights_request_appeal_days: Optional[int] = None
    identity_verification_required: bool = True
    breach_regulator_hours: Optional[int] = None
    breach_regulator_days: Optional[int] = None
    breach_regulator_text: str = "Without unreasonable delay"
    breach_attorney_general_threshold_individuals: Optional[int] = None
    breach_individual_notification_days: Optional[int] = None
    breach_individual_text: str = "Without unreasonable delay"
    cure_period_days: Optional[int] = None
    record_retention_years: Optional[int] = None


class CanonicalRegulation(BaseModel):
    """
    Canonical versioned representation of a legal obligation (Section 3.3).
    """
    regulation_id: str
    jurisdiction_id: str
    jurisdiction_type: JurisdictionType
    country: str
    state_or_province: Optional[str] = None
    member_state: Optional[str] = None
    legal_authority: str
    legal_instrument: str
    official_source_url: str
    source_document_hash: str
    article_or_section: str
    original_language: str = "en"
    verified_translation: Optional[str] = "en"
    effective_date: date
    repeal_date: Optional[date] = None
    transition_period_end: Optional[date] = None
    last_verified_at: datetime = Field(default_factory=datetime.utcnow)
    applicability_conditions: Dict[str, Any] = Field(default_factory=dict)
    thresholds: List[StatutoryThreshold] = Field(default_factory=list)
    exemptions: List[ExemptionRule] = Field(default_factory=list)
    preemption_rules: List[PreemptionRule] = Field(default_factory=list)
    organization_types: List[str] = Field(default_factory=list)
    industry_sectors: List[str] = Field(default_factory=list)
    data_subject_categories: List[str] = Field(default_factory=list)
    data_categories: List[str] = Field(default_factory=list)
    processing_activities: List[str] = Field(default_factory=list)
    required_actions: List[str] = Field(default_factory=list)
    required_assessments: List[str] = Field(default_factory=list)
    response_deadlines: ResponseDeadlineSpec = Field(default_factory=ResponseDeadlineSpec)
    notification_requirements: List[str] = Field(default_factory=list)
    required_evidence: List[str] = Field(default_factory=list)
    approval_requirements: List[str] = Field(default_factory=list)
    competent_regulator: str
    subnational_regulators: Dict[str, str] = Field(default_factory=dict)
    regulatory_status: RegulatoryStatus = RegulatoryStatus.EFFECTIVE
    deployment_status: DeploymentStatus = DeploymentStatus.PRODUCTION_ENABLED
    legal_review_status: LegalReviewStatus = LegalReviewStatus.VERIFIED
    rule_version: str = "2026.10.1"
    domain_category: str = Field(default="privacy", description="privacy, health_privacy, financial_privacy, children_privacy, biometric_privacy, breach_notification, ai_governance, cybersecurity, electronic_communications, public_sector")


class OrganizationProfileInput(BaseModel):
    name: Optional[str] = "Enterprise Organization"
    industry: str = Field(default="technology")
    organization_type: str = Field(default="private", description="private, public, government_agency, nonprofit, healthcare_covered_entity, business_associate, health_information_custodian, financial_institution, educational_institution")
    employee_count: Optional[int] = None
    annual_revenue_usd: Optional[float] = None
    consumer_records_count: Optional[int] = None
    data_broker_revenue_pct: Optional[float] = None
    is_federally_regulated_canada: bool = False
    hipaa_status: Optional[str] = Field(default=None, description="covered_entity, business_associate, non_hipaa, hybrid_entity")
    role: str = Field(default="controller", description="controller, processor, service_provider, joint_controller")
    establishments: List[str] = Field(default_factory=list, description="List of jurisdiction codes e.g. ['CA-ON', 'US-CA', 'IE']")
    main_eu_establishment: Optional[str] = None
    subnational_regions: List[str] = Field(default_factory=list, description="e.g. ['DE-BY', 'DE-BE']")


class ProcessingActivityInput(BaseModel):
    purpose: str
    data_categories: List[str] = Field(default_factory=list)
    data_subject_categories: List[str] = Field(default_factory=lambda: ["consumers"])
    subject_locations: List[str] = Field(default_factory=list)
    processing_locations: List[str] = Field(default_factory=list)
    transfer_destinations: List[str] = Field(default_factory=list)
    third_party_processors: bool = False
    involves_ai_or_admt: bool = False
    involves_biometrics: bool = False
    involves_children: bool = False
    involves_targeted_advertising_or_cookies: bool = False
    involves_cross_border_transfer: Optional[bool] = None
    targets_goods_or_services_to_subjects: bool = True
    monitors_subject_behavior: bool = False
    transfer_mechanisms_in_place: List[str] = Field(default_factory=list)


class ApplicabilityEvaluationRequest(BaseModel):
    organization: OrganizationProfileInput
    activity: ProcessingActivityInput
    evaluation_date: Optional[date] = None
    include_non_effective_laws: bool = True


class ApplicableInstrumentOutcome(BaseModel):
    regulation_id: str
    jurisdiction_id: str
    legal_instrument: str
    article_or_section: str
    domain_category: str
    applicability_status: str = Field(..., description="applicable, applicable_future_preparation, conditionally_applicable, exempt, preempted")
    applicability_reasoning: str
    triggered_by_facts: List[str]
    thresholds_evaluated: List[Dict[str, Any]] = Field(default_factory=list)
    exemptions_evaluated: List[Dict[str, Any]] = Field(default_factory=list)
    preemption_notes: List[str] = Field(default_factory=list)
    mandatory_controls: List[str]
    required_assessments: List[str]
    response_deadlines: ResponseDeadlineSpec
    competent_authority: str
    required_approval_gates: List[str]
    required_evidence: List[str]
    official_source_url: str
    rule_version: str
    regulatory_status: RegulatoryStatus
    deployment_status: DeploymentStatus
    legal_review_status: LegalReviewStatus
    confidence: float = 0.98
    requires_legal_review: bool = False


class ConflictOrAmbiguityItem(BaseModel):
    conflict_id: str
    regulations_involved: List[str]
    jurisdictions_involved: List[str]
    issue_type: str = Field(..., description="preemption_split, conflicting_deadlines, conflicting_retention_vs_deletion, extraterritorial_uncertainty, threshold_fact_missing, unverified_rule_status")
    description: str
    sources: List[str]
    resolution_strategy: str
    requires_legal_review: bool = True


class ApplicabilityEvaluationResponse(BaseModel):
    evaluation_id: str
    evaluated_at: datetime
    evaluation_date: date
    organization_summary: Dict[str, Any]
    activity_summary: Dict[str, Any]
    applicable_instruments: List[ApplicableInstrumentOutcome]
    future_preparation_obligations: List[ApplicableInstrumentOutcome] = Field(default_factory=list)
    exempt_or_preempted_instruments: List[ApplicableInstrumentOutcome] = Field(default_factory=list)
    mandatory_controls: List[str]
    required_assessments: List[str]
    applicable_deadlines: Dict[str, Any]
    responsible_authorities: List[Dict[str, str]]
    lead_supervisory_authority: Optional[Dict[str, str]] = None
    cross_border_transfer_analysis: Dict[str, Any]
    required_approval_gates: List[str]
    unresolved_questions: List[str]
    conflicts_and_escalations: List[ConflictOrAmbiguityItem]
    authoritative_source_links: List[Dict[str, str]]
    rule_versions: Dict[str, str]
    requires_legal_review: bool
    legal_review_reasons: List[str]
