"""
KIBO Privacy OS — Regulatory Applicability Bridge (Worker G21)
Implements Section 8 & RD-09 / RD-15:
- Connects `StatutoryAnnotation` (`LegalPassageAnnotation`), `DecisionAnnotation`
  (`DecisionVerdictAnnotation`), and `ProvisionDiffRecord` to
  `core.jrae.engine.JurisdictionalApplicabilityEngine`.
- Maps discovered provisions and enforcement/judicial decisions to JRAE `Obligation`
  candidates (`CanonicalRegulation`), `JurisdictionLayer`, `RegulatedRole`,
  `SectorClassification`, `DataCategory`, and `ProcessingActivityType`.
- Evaluates whether a newly discovered or amended regulation/decision applies to an
  `OrganizationProfile` (`OrganizationProfileInput`), testing jurisdiction establishment,
  data subject location, sector, role, sensitive data categories, and statutory thresholds,
  and NEVER assuming employee count > 5 alone triggers applicability.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

from core.jrae.engine import JurisdictionalApplicabilityEngine
from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code
from core.jrae.schemas import (
    ApplicabilityEvaluationRequest,
    ApplicabilityEvaluationResponse,
    ApplicableInstrumentOutcome,
    CanonicalRegulation,
    DeploymentStatus,
    ExemptionRule,
    JurisdictionType,
    LegalReviewStatus,
    OrganizationProfileInput,
    ProcessingActivityInput,
    RegulatoryStatus,
    ResponseDeadlineSpec,
    StatutoryThreshold,
)
from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DecisionAnnotation,
    DecisionVerdictAnnotation,
    LegalPassageAnnotation,
    LegalPromotionState,
    ProvisionDiffRecord,
    StatutoryAnnotation,
    compute_sha256_hex,
)


class JurisdictionLayer(str, Enum):
    """Canonical jurisdictional layer taxonomy bridging regulatory intelligence to JRAE."""
    SUPRANATIONAL = "supranational"
    FEDERAL = "federal"
    STATE = "state"
    PROVINCE = "province"
    TERRITORY = "territory"
    MEMBER_STATE = "member_state"
    SUBNATIONAL = "subnational"
    SECTORAL = "sectoral"


class RegulatedRole(str, Enum):
    """Canonical regulated entity roles across GDPR, CCPA/CPRA, HIPAA, PIPEDA/Law 25, and PHIPA."""
    CONTROLLER = "controller"
    PROCESSOR = "processor"
    JOINT_CONTROLLER = "joint_controller"
    BUSINESS = "business"
    SERVICE_PROVIDER = "service_provider"
    CONTRACTOR = "contractor"
    THIRD_PARTY = "third_party"
    COVERED_ENTITY = "covered_entity"
    BUSINESS_ASSOCIATE = "business_associate"
    HEALTH_INFORMATION_CUSTODIAN = "health_information_custodian"
    AGENT_OF_CUSTODIAN = "agent_of_custodian"
    DEPLOYER = "deployer"
    PROVIDER = "provider"


class SectorClassification(str, Enum):
    """Canonical sector classifications for JRAE scoping."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    HOSPITAL = "hospital"
    FINANCIAL_SERVICES = "financial_services"
    BANKING = "banking"
    INSURANCE = "insurance"
    RETAIL = "retail"
    ECOMMERCE = "ecommerce"
    ADTECH = "adtech"
    EDUCATION = "education"
    PUBLIC_SECTOR = "public_sector"
    TELECOMMUNICATIONS = "telecommunications"
    AI_AND_ANALYTICS = "ai_and_analytics"
    CROSS_SECTOR = "cross_sector"


class DataCategory(str, Enum):
    """Canonical data categories for JRAE evaluation."""
    PERSONAL_INFORMATION = "personal_information"
    PERSONAL_DATA = "personal_data"
    SENSITIVE_PERSONAL_INFORMATION = "sensitive_personal_information"
    PROTECTED_HEALTH_INFORMATION = "phi"
    HEALTH_INFORMATION = "health_information"
    MEDICAL_RECORDS = "medical_records"
    BIOMETRIC_DATA = "biometric_data"
    FINANCIAL_DATA = "financial_data"
    CREDIT_DATA = "credit_data"
    CHILDREN_DATA = "children_data"
    EMPLOYEE_DATA = "employee_data"
    ONLINE_IDENTIFIERS = "online_identifiers"
    COOKIES_AND_TRACKERS = "cookies"
    PRECISE_GEOLOCATION = "precise_geolocation"
    AI_TRAINING_AND_PROFILING_DATA = "ai_training_and_profiling_data"


class ProcessingActivityType(str, Enum):
    """Canonical processing activity types mapped from regulatory provisions and decisions."""
    DATA_COLLECTION = "data_collection"
    AI_OR_ADMT_PROFILING = "ai_or_admt_profiling"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"
    TARGETED_ADVERTISING_OR_COOKIES = "targeted_advertising_or_cookies"
    BIOMETRIC_AUTHENTICATION = "biometric_authentication"
    HEALTH_RECORD_CUSTODY = "health_record_custody"
    EMPLOYEE_MONITORING_AND_HR = "employee_monitoring_and_hr"
    DSAR_FULFILLMENT = "dsar_fulfillment"
    BREACH_DETECTION_AND_RESPONSE = "breach_detection_and_response"
    VENDOR_AND_PROCESSOR_DISCLOSURE = "vendor_and_processor_disclosure"
    DATA_RETENTION_AND_DELETION = "data_retention_and_deletion"


# Alias OrganizationProfile to JRAE's OrganizationProfileInput for seamless interoperability
OrganizationProfile = OrganizationProfileInput


class Obligation(BaseModel):
    """
    JRAE Obligation candidate derived deterministically from a `StatutoryAnnotation`,
    `DecisionAnnotation`, or `ProvisionDiffRecord`.
    """
    obligation_id: str
    regulation_id: str
    source_record_id: str
    source_record_type: str = Field(
        ...,
        description="statutory_annotation, decision_annotation, provision_diff",
    )
    jurisdiction_id: str
    jurisdiction_layer: JurisdictionLayer
    legal_authority: str
    legal_instrument: str
    official_citation: str
    official_source_url: str
    source_document_hash: str
    verbatim_quote: str
    title: str
    legal_requirement: str
    domain_category: str = "privacy"
    regulated_roles: List[RegulatedRole] = Field(default_factory=list)
    sectors: List[SectorClassification] = Field(default_factory=list)
    data_categories: List[DataCategory] = Field(default_factory=list)
    processing_activities: List[ProcessingActivityType] = Field(default_factory=list)
    thresholds: List[StatutoryThreshold] = Field(default_factory=list)
    exemptions: List[ExemptionRule] = Field(default_factory=list)
    required_controls: List[str] = Field(default_factory=list)
    required_assessments: List[str] = Field(default_factory=list)
    response_deadlines: ResponseDeadlineSpec = Field(default_factory=ResponseDeadlineSpec)
    statutory_deadline_text: Optional[str] = None
    effective_date: date = Field(default_factory=lambda: date(2026, 1, 1))
    requires_legal_review: bool = True
    promotion_state: LegalPromotionState = LegalPromotionState.ANNOTATED
    canonical_regulation: Optional[CanonicalRegulation] = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ApplicabilityMappingOutcome(BaseModel):
    """Result of evaluating whether a discovered/amended obligation or decision applies to an OrganizationProfile."""
    evaluation_id: str
    organization_name: str
    jurisdiction_id: str
    jurisdiction_layer: JurisdictionLayer
    applies: bool
    applicability_status: str = Field(
        ...,
        description="applicable, conditionally_applicable, applicable_future_preparation, exempt, not_applicable",
    )
    confidence: float = 0.95
    requires_legal_review: bool = False
    matched_establishments: List[str] = Field(default_factory=list)
    matched_subject_locations: List[str] = Field(default_factory=list)
    matched_sectors: List[str] = Field(default_factory=list)
    matched_roles: List[str] = Field(default_factory=list)
    matched_data_categories: List[str] = Field(default_factory=list)
    matched_processing_activities: List[str] = Field(default_factory=list)
    thresholds_evaluated: List[Dict[str, Any]] = Field(default_factory=list)
    exemptions_evaluated: List[Dict[str, Any]] = Field(default_factory=list)
    employee_count_guardrail_verified: bool = True
    reasoning: str
    triggered_controls: List[str] = Field(default_factory=list)
    triggered_assessments: List[str] = Field(default_factory=list)
    statutory_deadlines: Dict[str, Any] = Field(default_factory=dict)
    obligation: Obligation
    jrae_response: Optional[ApplicabilityEvaluationResponse] = None

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class RegulatoryApplicabilityBridge:
    """
    Connects `StatutoryAnnotation` (`LegalPassageAnnotation`), `DecisionAnnotation`
    (`DecisionVerdictAnnotation`), and `ProvisionDiffRecord` to
    `core.jrae.engine.JurisdictionalApplicabilityEngine`.

    Enforces:
    - Exact mapping to JRAE `Obligation` candidates, `JurisdictionLayer`, `RegulatedRole`,
      `SectorClassification`, `DataCategory`, and `ProcessingActivityType`.
    - Multi-factor applicability evaluation against `OrganizationProfile` (jurisdiction
      establishment, data subject location, sector, role, sensitive data categories, and
      statutory thresholds).
    - Strict guardrail: NEVER assumes `employee_count > 5` alone triggers regulatory
      applicability.
    """

    def __init__(
        self,
        jrae_engine: Optional[JurisdictionalApplicabilityEngine] = None,
    ) -> None:
        self.jrae_engine = jrae_engine or JurisdictionalApplicabilityEngine()

    # ------------------------------------------------------------------
    # Taxonomy Mapping Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def resolve_jurisdiction_layer(jurisdiction_id: str) -> JurisdictionLayer:
        code = normalize_jurisdiction_code(jurisdiction_id)
        entry = GLOBAL_JURISDICTION_REGISTRY.get(code)
        if entry is not None:
            jtype = entry.jurisdiction_type.value
            for member in JurisdictionLayer:
                if member.value == jtype:
                    return member
        if code == "EU":
            return JurisdictionLayer.SUPRANATIONAL
        if code in {"US-FED", "CA-FED"}:
            return JurisdictionLayer.FEDERAL
        if code.startswith("US-"):
            return JurisdictionLayer.STATE
        if code.startswith("CA-"):
            return JurisdictionLayer.PROVINCE
        if code.startswith("EU-"):
            return JurisdictionLayer.MEMBER_STATE
        return JurisdictionLayer.FEDERAL

    @staticmethod
    def map_regulated_roles(raw_roles: Iterable[str], text_hint: str = "") -> List[RegulatedRole]:
        roles: List[RegulatedRole] = []
        combined = " ".join(list(raw_roles) + [text_hint]).lower()

        mapping: List[Tuple[Tuple[str, ...], RegulatedRole]] = [
            (("covered_entity", "covered entity", "healthcare_provider", "health_plan"), RegulatedRole.COVERED_ENTITY),
            (("business_associate", "business associate"), RegulatedRole.BUSINESS_ASSOCIATE),
            (("health_information_custodian", "health information custodian", "custodian", "phipa"), RegulatedRole.HEALTH_INFORMATION_CUSTODIAN),
            (("agent", "electronic service provider"), RegulatedRole.AGENT_OF_CUSTODIAN),
            (("service_provider", "service provider"), RegulatedRole.SERVICE_PROVIDER),
            (("contractor",), RegulatedRole.CONTRACTOR),
            (("third_party", "third party"), RegulatedRole.THIRD_PARTY),
            (("joint_controller", "joint controller"), RegulatedRole.JOINT_CONTROLLER),
            (("processor", "auftragsverarbeiter", "cloud_service_processor"), RegulatedRole.PROCESSOR),
            (("business", "for-profit"), RegulatedRole.BUSINESS),
            (("deployer",), RegulatedRole.DEPLOYER),
            (("controller", "verantwortlicher", "enterprise", "organization", "regulated_entity"), RegulatedRole.CONTROLLER),
        ]
        for keywords, role_enum in mapping:
            if any(kw in combined for kw in keywords) and role_enum not in roles:
                roles.append(role_enum)

        if not roles:
            roles.append(RegulatedRole.CONTROLLER)
        return roles

    @staticmethod
    def map_sectors(raw_sectors: Iterable[str], text_hint: str = "", jurisdiction_id: str = "") -> List[SectorClassification]:
        sectors: List[SectorClassification] = []
        combined = " ".join(list(raw_sectors) + [text_hint]).lower()

        mapping: List[Tuple[Tuple[str, ...], SectorClassification]] = [
            (("hospital", "inpatient", "emergency department", "phipa"), SectorClassification.HOSPITAL),
            (("healthcare", "health", "medical", "hipaa", "cmia", "clinical", "life_sciences"), SectorClassification.HEALTHCARE),
            (("financial", "credit", "glba", "nydfs", "fintech"), SectorClassification.FINANCIAL_SERVICES),
            (("banking", "bank"), SectorClassification.BANKING),
            (("insurance", "insurer"), SectorClassification.INSURANCE),
            (("retail", "consumer_goods"), SectorClassification.RETAIL),
            (("e_commerce", "ecommerce", "online store"), SectorClassification.ECOMMERCE),
            (("advertising", "adtech", "cookie", "tracker", "behavioral", "analytics"), SectorClassification.ADTECH),
            (("education", "school", "university", "student", "ferpa"), SectorClassification.EDUCATION),
            (("public_sector", "government", "federal_agency"), SectorClassification.PUBLIC_SECTOR),
            (("telecom", "electronic_communications"), SectorClassification.TELECOMMUNICATIONS),
            (("ai", "admt", "automated decision", "profiling", "machine learning"), SectorClassification.AI_AND_ANALYTICS),
            (("technology", "cloud", "saas", "software", "platform"), SectorClassification.TECHNOLOGY),
        ]
        for keywords, sec_enum in mapping:
            if any(kw in combined for kw in keywords) and sec_enum not in sectors:
                sectors.append(sec_enum)

        if any(w in combined for w in ("all_private_sector", "all_canadian_commercial", "cross_sector", "general", "all")):
            if SectorClassification.CROSS_SECTOR not in sectors:
                sectors.append(SectorClassification.CROSS_SECTOR)

        if not sectors:
            sectors.append(SectorClassification.CROSS_SECTOR)
        return sectors

    @staticmethod
    def map_data_categories(raw_categories: Iterable[str], text_hint: str = "") -> List[DataCategory]:
        categories: List[DataCategory] = []
        combined = " ".join(list(raw_categories) + [text_hint]).lower()

        mapping: List[Tuple[Tuple[str, ...], DataCategory]] = [
            (("phi", "protected_health_information", "unsecured_phi", "protected health information"), DataCategory.PROTECTED_HEALTH_INFORMATION),
            (("health_information", "health", "medical_records", "medical", "phipa", "patient"), DataCategory.HEALTH_INFORMATION),
            (("biometric", "facial recognition", "fingerprint", "voiceprint", "bipa"), DataCategory.BIOMETRIC_DATA),
            (("financial", "payment", "bank", "account_number"), DataCategory.FINANCIAL_DATA),
            (("credit", "consumer report", "fcra", "schufa"), DataCategory.CREDIT_DATA),
            (("children", "minor", "under 13", "under 16", "coppa", "student"), DataCategory.CHILDREN_DATA),
            (("employee", "beschäftigte", "worker", "hr", "employment", "applicant"), DataCategory.EMPLOYEE_DATA),
            (("cookie", "tracker", "traceur", "terminal equipment", "art. 82", "eprivacy"), DataCategory.COOKIES_AND_TRACKERS),
            (("online_identifier", "ip address", "device_id", "advertising id"), DataCategory.ONLINE_IDENTIFIERS),
            (("geolocation", "location"), DataCategory.PRECISE_GEOLOCATION),
            (("admt", "automated decision", "profiling", "ai_training", "scoring"), DataCategory.AI_TRAINING_AND_PROFILING_DATA),
            (("sensitive", "special category", "art. 9"), DataCategory.SENSITIVE_PERSONAL_INFORMATION),
            (("renseignement_personnel", "personal_information", "personal information", "consumer"), DataCategory.PERSONAL_INFORMATION),
            (("personenbezogene_daten", "personal_data", "personal data", "données personnelles"), DataCategory.PERSONAL_DATA),
        ]
        for keywords, cat_enum in mapping:
            if any(kw in combined for kw in keywords) and cat_enum not in categories:
                categories.append(cat_enum)

        if not categories:
            categories.append(DataCategory.PERSONAL_DATA)
        return categories

    @staticmethod
    def map_processing_activities(raw_activities: Iterable[str], text_hint: str = "") -> List[ProcessingActivityType]:
        activities: List[ProcessingActivityType] = []
        combined = " ".join(list(raw_activities) + [text_hint]).lower()

        mapping: List[Tuple[Tuple[str, ...], ProcessingActivityType]] = [
            (("admt", "automated decision", "profiling", "ai", "scoring", "art. 22", "7150", "1798.185"), ProcessingActivityType.AI_OR_ADMT_PROFILING),
            (("cross_border", "cross-border", "outside québec", "outside quebec", "extérieur du québec", "third country", "transfer", "art. 17"), ProcessingActivityType.CROSS_BORDER_TRANSFER),
            (("cookie", "tracker", "traceur", "advertising", "analytics", "selling", "sharing", "art. 82", "5(3)"), ProcessingActivityType.TARGETED_ADVERTISING_OR_COOKIES),
            (("biometric", "facial", "fingerprint"), ProcessingActivityType.BIOMETRIC_AUTHENTICATION),
            (("phi", "medical record", "electronic health", "lockbox", "custodian", "hospital"), ProcessingActivityType.HEALTH_RECORD_CUSTODY),
            (("employee", "beschäftigte", "bdsg § 26", "§ 26 bdsg", "workplace", "hr", "monitoring"), ProcessingActivityType.EMPLOYEE_MONITORING_AND_HR),
            (("dsar", "deletion", "erasure", "access request", "portability", "opt-out", "opt_out"), ProcessingActivityType.DSAR_FULFILLMENT),
            (("breach", "incident", "unsecured", "notification", "164.404", "s. 12", "rrosh"), ProcessingActivityType.BREACH_DETECTION_AND_RESPONSE),
            (("vendor", "processor", "service provider", "contractor", "subprocessor", "1798.100(d)", "art. 28"), ProcessingActivityType.VENDOR_AND_PROCESSOR_DISCLOSURE),
            (("retention", "deletion", "minimization", "purge", "schedule"), ProcessingActivityType.DATA_RETENTION_AND_DELETION),
            (("collection", "notice at collection", "1798.100"), ProcessingActivityType.DATA_COLLECTION),
        ]
        for keywords, act_enum in mapping:
            if any(kw in combined for kw in keywords) and act_enum not in activities:
                activities.append(act_enum)

        if not activities:
            activities.append(ProcessingActivityType.DATA_COLLECTION)
        return activities

    @staticmethod
    def _infer_domain_category(
        jurisdiction_id: str,
        data_categories: List[DataCategory],
        activities: List[ProcessingActivityType],
        text_hint: str,
    ) -> str:
        t = text_hint.lower()
        if DataCategory.PROTECTED_HEALTH_INFORMATION in data_categories or DataCategory.HEALTH_INFORMATION in data_categories or "phipa" in t or "hipaa" in t or "cmia" in t:
            return "health_privacy"
        if DataCategory.BIOMETRIC_DATA in data_categories or "bipa" in t:
            return "biometric_privacy"
        if DataCategory.COOKIES_AND_TRACKERS in data_categories or "art. 82" in t or "eprivacy" in t or "cookie" in t:
            return "electronic_communications"
        if ProcessingActivityType.AI_OR_ADMT_PROFILING in activities or "ai act" in t or "admt" in t:
            return "ai_governance"
        if DataCategory.FINANCIAL_DATA in data_categories or "glba" in t:
            return "financial_privacy"
        if DataCategory.CHILDREN_DATA in data_categories or "coppa" in t:
            return "children_privacy"
        if ProcessingActivityType.BREACH_DETECTION_AND_RESPONSE in activities and "breach" in t:
            return "breach_notification"
        return "privacy"

    # ------------------------------------------------------------------
    # Obligation Candidate Builders
    # ------------------------------------------------------------------
    def map_statutory_annotation_to_obligation(
        self,
        annotation: StatutoryAnnotation,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> Obligation:
        """
        Maps a `StatutoryAnnotation` (`LegalPassageAnnotation`) into a JRAE `Obligation`
        candidate and corresponding `CanonicalRegulation`.
        """
        jur = normalize_jurisdiction_code(annotation.jurisdiction_id)
        layer = self.resolve_jurisdiction_layer(jur)
        text_hint = " ".join(
            [
                annotation.source_section,
                annotation.normalized_legal_concept,
                annotation.legal_requirement,
                annotation.plain_language_explanation,
                annotation.exact_source_excerpt,
            ]
        )

        roles = self.map_regulated_roles(annotation.affected_organization_types, text_hint)
        sectors = self.map_sectors(annotation.affected_industries, text_hint, jur)
        data_cats = self.map_data_categories(annotation.affected_data_categories, text_hint)
        activities = self.map_processing_activities(annotation.affected_processing_activities, text_hint)
        domain = self._infer_domain_category(jur, data_cats, activities, text_hint)

        thresholds: List[StatutoryThreshold] = []
        if "1798" in annotation.source_section or (jur == "US-CA" and "ccpa" in text_hint.lower()):
            thresholds.extend(
                [
                    StatutoryThreshold(
                        metric="annual_revenue_usd",
                        operator=">=",
                        value=26625000,
                        currency="USD",
                        logic_group="OR",
                        description="CCPA/CPRA gross annual revenue threshold ($26.625M)",
                    ),
                    StatutoryThreshold(
                        metric="consumer_records_count",
                        operator=">=",
                        value=100000,
                        logic_group="OR",
                        description="CCPA/CPRA 100,000+ California consumers or households",
                    ),
                    StatutoryThreshold(
                        metric="data_broker_revenue_pct",
                        operator=">=",
                        value=50,
                        logic_group="OR",
                        description="CCPA/CPRA >=50% annual revenue from selling/sharing consumer personal information",
                    ),
                ]
            )
        for metric_key, metric_val in (annotation.thresholds or {}).items():
            if isinstance(metric_val, (int, float)):
                thresholds.append(
                    StatutoryThreshold(
                        metric=str(metric_key),
                        operator=">=",
                        value=metric_val,
                        logic_group="OR",
                        description=f"Extracted statutory threshold {metric_key} >= {metric_val}",
                    )
                )

        exemptions: List[ExemptionRule] = []
        for idx, ex_text in enumerate(annotation.exemptions or []):
            exemptions.append(
                ExemptionRule(
                    exemption_id=f"EX-{annotation.annotation_id}-{idx + 1}",
                    exemption_type="data_level" if "phi" in ex_text.lower() or "hipaa" in ex_text.lower() else "activity_level",
                    condition_field="data_categories",
                    condition_values=["phi"] if "hipaa" in ex_text.lower() else [],
                    carve_out_statute=annotation.source_section,
                    description=ex_text,
                )
            )

        deadlines = self._build_deadline_spec(jur, annotation.statutory_deadline, text_hint)
        source_hash = (
            document.normalized_text_sha256
            if document is not None and document.normalized_text_sha256
            else compute_sha256_hex(annotation.exact_source_excerpt)
        )
        source_url = (
            document.official_source_url
            if document is not None and document.official_source_url
            else GLOBAL_JURISDICTION_REGISTRY.get(jur, GLOBAL_JURISDICTION_REGISTRY["US-FED"]).regulator_url
        )
        instrument_name = (
            document.canonical_title
            if document is not None and document.canonical_title
            else f"{jur} Statutory Instrument ({annotation.source_section})"
        )
        citation = (
            document.official_citation
            if document is not None and document.official_citation
            else annotation.source_section
        )
        eff_date = annotation.effective_date or (document.effective_date if document else None) or date(2026, 1, 1)

        reg_id = f"REG-{jur}-{compute_sha256_hex(annotation.annotation_id + ':' + annotation.source_section)[:10].upper()}"
        ob_id = f"OBL-{jur}-{compute_sha256_hex(annotation.annotation_id)[:12].upper()}"

        canonical_reg = CanonicalRegulation(
            regulation_id=reg_id,
            jurisdiction_id=jur,
            jurisdiction_type=JurisdictionType(layer.value),
            country=GLOBAL_JURISDICTION_REGISTRY[jur].country if jur in GLOBAL_JURISDICTION_REGISTRY else jur.split("-")[0],
            legal_authority=annotation.regulatory_authority,
            legal_instrument=instrument_name,
            official_source_url=source_url,
            source_document_hash=source_hash,
            article_or_section=annotation.source_section,
             original_language=annotation.source_language,
            effective_date=eff_date,
            thresholds=thresholds,
            exemptions=exemptions,
            organization_types=[r.value for r in roles],
            industry_sectors=[s.value for s in sectors],
            data_categories=[d.value for d in data_cats],
            processing_activities=[a.value for a in activities],
            required_actions=list(annotation.required_controls),
            required_assessments=list(annotation.required_assessments),
            response_deadlines=deadlines,
            competent_regulator=annotation.regulatory_authority,
            regulatory_status=RegulatoryStatus.EFFECTIVE,
            deployment_status=DeploymentStatus.TESTED,
            legal_review_status=(
                LegalReviewStatus.VERIFIED
                if annotation.verification_status == "VERIFIED" and annotation.interpretation_status != "requires_legal_review"
                else LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF
            ),
            rule_version=annotation.document_version,
            domain_category=domain,
        )

        return Obligation(
            obligation_id=ob_id,
            regulation_id=reg_id,
            source_record_id=annotation.annotation_id,
            source_record_type="statutory_annotation",
            jurisdiction_id=jur,
            jurisdiction_layer=layer,
            legal_authority=annotation.regulatory_authority,
            legal_instrument=instrument_name,
            official_citation=citation,
            official_source_url=source_url,
            source_document_hash=source_hash,
            verbatim_quote=annotation.exact_source_excerpt,
            title=annotation.normalized_legal_concept,
            legal_requirement=annotation.legal_requirement,
            domain_category=domain,
            regulated_roles=roles,
            sectors=sectors,
            data_categories=data_cats,
            processing_activities=activities,
            thresholds=thresholds,
            exemptions=exemptions,
            required_controls=list(annotation.required_controls),
            required_assessments=list(annotation.required_assessments),
            response_deadlines=deadlines,
            statutory_deadline_text=annotation.statutory_deadline,
            effective_date=eff_date,
            requires_legal_review=(annotation.interpretation_status == "requires_legal_review" or annotation.verification_status != "VERIFIED"),
            promotion_state=LegalPromotionState.ANNOTATED,
            canonical_regulation=canonical_reg,
        )

    def map_decision_annotation_to_obligation(
        self,
        decision: DecisionAnnotation,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> Obligation:
        """
        Maps a `DecisionAnnotation` (`DecisionVerdictAnnotation`) into a JRAE `Obligation`
        candidate and corresponding `CanonicalRegulation`.
        Strictly grounds obligations in `legal_holdings` and `operative_orders` (never dicta).
        """
        jur = normalize_jurisdiction_code(decision.jurisdiction_id)
        layer = self.resolve_jurisdiction_layer(jur)

        holdings_text = " ".join(decision.legal_holdings + decision.operative_orders + decision.remedies_and_penalties)
        text_hint = " ".join(
            [
                decision.case_name,
                decision.neutral_citation_or_id,
                decision.material_facts,
                holdings_text,
                " ".join(decision.statutory_provisions_considered),
            ]
        )

        roles = self.map_regulated_roles([], text_hint)
        sectors = self.map_sectors([], text_hint, jur)
        data_cats = self.map_data_categories([], text_hint)
        activities = self.map_processing_activities([], text_hint)
        domain = self._infer_domain_category(jur, data_cats, activities, text_hint)

        verbatim_quote = ""
        if decision.relevant_reasoning_passages:
            for p in decision.relevant_reasoning_passages:
                if p.get("passage_role") in ("judicial_holding", "holding", "remedy_order") and p.get("exact_source_excerpt"):
                    verbatim_quote = str(p["exact_source_excerpt"])
                    break
            if not verbatim_quote and decision.relevant_reasoning_passages[0].get("exact_source_excerpt"):
                verbatim_quote = str(decision.relevant_reasoning_passages[0]["exact_source_excerpt"])
        if not verbatim_quote:
            verbatim_quote = decision.legal_holdings[0] if decision.legal_holdings else decision.material_facts

        source_hash = (
            document.normalized_text_sha256
            if document is not None and document.normalized_text_sha256
            else compute_sha256_hex(verbatim_quote)
        )
        source_url = (
            document.official_source_url
            if document is not None and document.official_source_url
            else GLOBAL_JURISDICTION_REGISTRY.get(jur, GLOBAL_JURISDICTION_REGISTRY["US-FED"]).regulator_url
        )

        controls = list(decision.operative_orders) + list(decision.practical_privacy_program_implications)
        if not controls:
            controls = [f"Enforce compliance with holding in {decision.case_name} ({decision.neutral_citation_or_id})"]

        assessments = self._infer_assessments_from_text(jur, text_hint)
        deadlines = self._build_deadline_spec(jur, None, text_hint)

        reg_id = f"REG-DEC-{jur}-{compute_sha256_hex(decision.decision_id)[:10].upper()}"
        ob_id = f"OBL-DEC-{jur}-{compute_sha256_hex(decision.decision_id)[:12].upper()}"

        is_reversed = bool(decision.reversals_or_modifications) or decision.review_status == LegalPromotionState.SUPERSEDED
        requires_review = (
            decision.binding_vs_persuasive_status == "requires_legal_review"
            or decision.review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW
            or is_reversed
        )

        requirement_summary = (
            decision.legal_holdings[0]
            if decision.legal_holdings
            else (decision.operative_orders[0] if decision.operative_orders else decision.material_facts)
        )

        canonical_reg = CanonicalRegulation(
            regulation_id=reg_id,
            jurisdiction_id=jur,
            jurisdiction_type=JurisdictionType(layer.value),
            country=GLOBAL_JURISDICTION_REGISTRY[jur].country if jur in GLOBAL_JURISDICTION_REGISTRY else jur.split("-")[0],
            legal_authority=decision.court_tribunal_or_regulator,
            legal_instrument=f"{decision.case_name} ({decision.neutral_citation_or_id})",
            official_source_url=source_url,
            source_document_hash=source_hash,
            article_or_section=", ".join(decision.statutory_provisions_considered) or decision.neutral_citation_or_id,
            effective_date=decision.decision_date,
            organization_types=[r.value for r in roles],
            industry_sectors=[s.value for s in sectors],
            data_categories=[d.value for d in data_cats],
            processing_activities=[a.value for a in activities],
            required_actions=controls,
            required_assessments=assessments,
            response_deadlines=deadlines,
            competent_regulator=decision.court_tribunal_or_regulator,
            regulatory_status=RegulatoryStatus.SUPERSEDED if is_reversed else RegulatoryStatus.EFFECTIVE,
            deployment_status=DeploymentStatus.TESTED,
            legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF if requires_review else LegalReviewStatus.VERIFIED,
            rule_version="1.0.0",
            domain_category=domain,
        )

        return Obligation(
            obligation_id=ob_id,
            regulation_id=reg_id,
            source_record_id=decision.decision_id,
            source_record_type="decision_annotation",
            jurisdiction_id=jur,
            jurisdiction_layer=layer,
            legal_authority=decision.court_tribunal_or_regulator,
            legal_instrument=decision.case_name,
            official_citation=decision.neutral_citation_or_id,
            official_source_url=source_url,
            source_document_hash=source_hash,
            verbatim_quote=verbatim_quote,
            title=f"{decision.case_name} [{decision.neutral_citation_or_id}]",
            legal_requirement=requirement_summary,
            domain_category=domain,
            regulated_roles=roles,
            sectors=sectors,
            data_categories=data_cats,
            processing_activities=activities,
            required_controls=controls,
            required_assessments=assessments,
            response_deadlines=deadlines,
            effective_date=decision.decision_date,
            requires_legal_review=requires_review,
            promotion_state=decision.review_status,
            canonical_regulation=canonical_reg,
        )

    def map_provision_diff_to_obligation(
        self,
        diff: ProvisionDiffRecord,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> Obligation:
        """
        Maps a `ProvisionDiffRecord` (amended statutory or regulatory provision) into a
        JRAE `Obligation` candidate.
        """
        jur = normalize_jurisdiction_code(diff.jurisdiction_id)
        layer = self.resolve_jurisdiction_layer(jur)
        text_hint = " ".join([diff.provision_ref, diff.current_text, " ".join(diff.changed_elements_summary)])

        roles = self.map_regulated_roles([], text_hint)
        sectors = self.map_sectors([], text_hint, jur)
        data_cats = self.map_data_categories([], text_hint)
        activities = self.map_processing_activities([], text_hint)
        domain = self._infer_domain_category(jur, data_cats, activities, text_hint)

        thresholds: List[StatutoryThreshold] = []
        if jur == "US-CA" and ("1798" in diff.provision_ref or "ccpa" in diff.document_id.lower()):
            thresholds.extend(
                [
                    StatutoryThreshold(
                        metric="annual_revenue_usd",
                        operator=">=",
                        value=26625000,
                        currency="USD",
                        logic_group="OR",
                        description="CCPA/CPRA gross annual revenue threshold ($26.625M)",
                    ),
                    StatutoryThreshold(
                        metric="consumer_records_count",
                        operator=">=",
                        value=100000,
                        logic_group="OR",
                        description="CCPA/CPRA 100,000+ California consumers or households",
                    ),
                    StatutoryThreshold(
                        metric="data_broker_revenue_pct",
                        operator=">=",
                        value=50,
                        logic_group="OR",
                        description="CCPA/CPRA >=50% annual revenue from selling/sharing consumer personal information",
                    ),
                ]
            )

        controls = self._infer_controls_from_text(jur, diff.provision_ref, text_hint)
        assessments = self._infer_assessments_from_text(jur, text_hint)
        deadlines = self._build_deadline_spec(jur, None, text_hint)

        source_hash = diff.current_sha256 or compute_sha256_hex(diff.current_text or diff.previous_text)
        source_url = (
            document.official_source_url
            if document is not None and document.official_source_url
            else GLOBAL_JURISDICTION_REGISTRY.get(jur, GLOBAL_JURISDICTION_REGISTRY["US-FED"]).regulator_url
        )
        authority = (
            document.issuing_authority
            if document is not None and document.issuing_authority
            else GLOBAL_JURISDICTION_REGISTRY.get(jur, GLOBAL_JURISDICTION_REGISTRY["US-FED"]).primary_regulator
        )
        eff_date = diff.current_effective_date or diff.previous_effective_date or date(2026, 1, 1)

        reg_id = f"REG-DIFF-{jur}-{compute_sha256_hex(diff.diff_id)[:10].upper()}"
        ob_id = f"OBL-DIFF-{jur}-{compute_sha256_hex(diff.diff_id)[:12].upper()}"

        reg_status = (
            RegulatoryStatus.REPEALED
            if diff.change_type == "repealed_provision"
            else RegulatoryStatus.AMENDED
        )

        canonical_reg = CanonicalRegulation(
            regulation_id=reg_id,
            jurisdiction_id=jur,
            jurisdiction_type=JurisdictionType(layer.value),
            country=GLOBAL_JURISDICTION_REGISTRY[jur].country if jur in GLOBAL_JURISDICTION_REGISTRY else jur.split("-")[0],
            legal_authority=authority,
            legal_instrument=f"{diff.document_id} ({diff.provision_ref})",
            official_source_url=source_url,
            source_document_hash=source_hash,
            article_or_section=diff.provision_ref,
            effective_date=eff_date,
            thresholds=thresholds,
            organization_types=[r.value for r in roles],
            industry_sectors=[s.value for s in sectors],
            data_categories=[d.value for d in data_cats],
            processing_activities=[a.value for a in activities],
            required_actions=controls,
            required_assessments=assessments,
            response_deadlines=deadlines,
            competent_regulator=authority,
            regulatory_status=reg_status,
            deployment_status=DeploymentStatus.TESTED,
            legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
            rule_version=diff.current_version,
            domain_category=domain,
        )

        return Obligation(
            obligation_id=ob_id,
            regulation_id=reg_id,
            source_record_id=diff.diff_id,
            source_record_type="provision_diff",
            jurisdiction_id=jur,
            jurisdiction_layer=layer,
            legal_authority=authority,
            legal_instrument=f"{diff.document_id} ({diff.provision_ref})",
            official_citation=diff.provision_ref,
            official_source_url=source_url,
            source_document_hash=source_hash,
            verbatim_quote=diff.current_text or diff.previous_text,
            title=f"Amendment to {diff.provision_ref} ({diff.previous_version} -> {diff.current_version})",
            legal_requirement=diff.current_text or f"Repealed provision {diff.provision_ref}",
            domain_category=domain,
            regulated_roles=roles,
            sectors=sectors,
            data_categories=data_cats,
            processing_activities=activities,
            thresholds=thresholds,
            required_controls=controls,
            required_assessments=assessments,
            response_deadlines=deadlines,
            effective_date=eff_date,
            requires_legal_review=True,
            promotion_state=LegalPromotionState.ANNOTATED,
            canonical_regulation=canonical_reg,
        )

    def to_obligation(
        self,
        item: Union[StatutoryAnnotation, DecisionAnnotation, ProvisionDiffRecord, Obligation],
        document: Optional[CanonicalLegalDocument] = None,
    ) -> Obligation:
        """Polymorphic dispatcher converting any annotation or diff record into a JRAE `Obligation`."""
        if isinstance(item, Obligation):
            return item
        if isinstance(item, LegalPassageAnnotation):
            return self.map_statutory_annotation_to_obligation(item, document=document)
        if isinstance(item, DecisionVerdictAnnotation):
            return self.map_decision_annotation_to_obligation(item, document=document)
        if isinstance(item, ProvisionDiffRecord):
            return self.map_provision_diff_to_obligation(item, document=document)
        raise TypeError(f"Unsupported regulatory record type for JRAE bridge: {type(item)!r}")

    # ------------------------------------------------------------------
    # Applicability Evaluation against OrganizationProfile & ProcessingActivity
    # ------------------------------------------------------------------
    def evaluate_applicability(
        self,
        item: Union[StatutoryAnnotation, DecisionAnnotation, ProvisionDiffRecord, Obligation],
        organization: Union[OrganizationProfileInput, Dict[str, Any]],
        activity: Optional[Union[ProcessingActivityInput, Dict[str, Any]]] = None,
        *,
        evaluation_date: Optional[date] = None,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> ApplicabilityMappingOutcome:
        """
        Evaluates whether a newly discovered or amended regulation/decision (`StatutoryAnnotation`,
        `DecisionAnnotation`, `ProvisionDiffRecord`, or `Obligation`) applies to an
        `OrganizationProfile` (and optional `ProcessingActivityInput`).

        Tests:
        1. Jurisdiction establishment (`organization.establishments`) & data subject location (`activity.subject_locations`)
        2. Sector (`organization.industry`, `organization.organization_type`)
        3. Regulated role (`organization.role`, `organization.hipaa_status`)
        4. Sensitive & regulated data categories (`activity.data_categories`)
        5. Statutory business/processing thresholds (e.g., CCPA revenue/consumer count, BDSG § 38 20-person automated processing DPO rule)
        6. Employee-count guardrail: NEVER assumes `employee_count > 5` alone triggers applicability.
        """
        obligation = self.to_obligation(item, document=document)
        org = (
            organization.model_copy(deep=True)
            if isinstance(organization, OrganizationProfileInput)
            else OrganizationProfileInput(**organization)
        )
        if activity is None:
            act = ProcessingActivityInput(
                purpose="Enterprise Regulated Data Processing",
                data_categories=[c.value for c in obligation.data_categories] or ["personal_data"],
                subject_locations=list(org.establishments),
                processing_locations=list(org.establishments),
                involves_ai_or_admt=(ProcessingActivityType.AI_OR_ADMT_PROFILING in obligation.processing_activities),
                involves_biometrics=(DataCategory.BIOMETRIC_DATA in obligation.data_categories),
                involves_children=(DataCategory.CHILDREN_DATA in obligation.data_categories),
                involves_targeted_advertising_or_cookies=(
                    DataCategory.COOKIES_AND_TRACKERS in obligation.data_categories
                    or ProcessingActivityType.TARGETED_ADVERTISING_OR_COOKIES in obligation.processing_activities
                ),
            )
        elif isinstance(activity, ProcessingActivityInput):
            act = activity.model_copy(deep=True)
        else:
            act = ProcessingActivityInput(**activity)

        when = evaluation_date or date(2026, 10, 25)

        # Normalize jurisdictions
        org_est = {normalize_jurisdiction_code(x) for x in org.establishments if x}
        subj_locs = {normalize_jurisdiction_code(x) for x in act.subject_locations if x}
        proc_locs = {normalize_jurisdiction_code(x) for x in act.processing_locations if x}
        nexus = org_est | subj_locs | proc_locs

        jur = normalize_jurisdiction_code(obligation.jurisdiction_id)

        # Run underlying JRAE engine for full multi-jurisdictional context
        jrae_req = ApplicabilityEvaluationRequest(
            organization=org,
            activity=act,
            evaluation_date=when,
            include_non_effective_laws=True,
        )
        jrae_resp = self.jrae_engine.evaluate(jrae_req)

        # 1. Check Editorial-Only Diff or Repealed Status
        if isinstance(item, ProvisionDiffRecord) and not item.is_substantive:
            return ApplicabilityMappingOutcome(
                evaluation_id=jrae_resp.evaluation_id,
                organization_name=org.name or "Enterprise Organization",
                jurisdiction_id=jur,
                jurisdiction_layer=obligation.jurisdiction_layer,
                applies=False,
                applicability_status="not_applicable",
                confidence=0.99,
                requires_legal_review=False,
                reasoning="Editorial or formatting-only change; no substantive legal obligation altered.",
                obligation=obligation,
                jrae_response=jrae_resp,
            )

        # 2. Territorial Nexus Check (Establishment or Data Subject / Extraterritorial Scope)
        matched_est: List[str] = []
        matched_subj: List[str] = []
        territorial_match = False

        if jur == "EU":
            matched_est = sorted(c for c in org_est if c == "EU" or c.startswith("EU-"))
            matched_subj = sorted(c for c in subj_locs if c == "EU" or c.startswith("EU-"))
            territorial_match = bool(
                matched_est
                or (matched_subj and (act.targets_goods_or_services_to_subjects or act.monitors_subject_behavior))
            )
        elif jur == "US-FED":
            matched_est = sorted(c for c in org_est if c.startswith("US-"))
            matched_subj = sorted(c for c in subj_locs if c.startswith("US-"))
            territorial_match = bool(matched_est or matched_subj)
        elif jur == "CA-FED":
            matched_est = sorted(c for c in org_est if c.startswith("CA-"))
            matched_subj = sorted(c for c in subj_locs if c.startswith("CA-"))
            territorial_match = bool(matched_est or matched_subj)
        else:
            if jur in org_est:
                matched_est.append(jur)
            if jur in subj_locs:
                matched_subj.append(jur)
            if jur.startswith("EU-"):
                territorial_match = bool(
                    matched_est
                    or (matched_subj and (act.targets_goods_or_services_to_subjects or act.monitors_subject_behavior))
                )
            else:
                territorial_match = bool(matched_est or matched_subj or jur in proc_locs)

        if not territorial_match:
            return ApplicabilityMappingOutcome(
                evaluation_id=jrae_resp.evaluation_id,
                organization_name=org.name or "Enterprise Organization",
                jurisdiction_id=jur,
                jurisdiction_layer=obligation.jurisdiction_layer,
                applies=False,
                applicability_status="not_applicable",
                confidence=0.98,
                requires_legal_review=False,
                reasoning=(
                    f"No jurisdictional nexus in {jur} (establishments={sorted(org_est)}, "
                    f"subject_locations={sorted(subj_locs)}). Employee count ({org.employee_count}) "
                    "never establishes territorial jurisdiction."
                ),
                obligation=obligation,
                jrae_response=jrae_resp,
            )

        # 3. Sector & Regulated Role Check
        matched_sectors = self._evaluate_sector_match(org, obligation)
        matched_roles = self._evaluate_role_match(org, obligation)
        matched_data = self._evaluate_data_category_match(org, act, obligation)
        matched_acts = self._evaluate_activity_match(act, obligation)

        # Specific sectoral gates (e.g. Ontario PHIPA, US HIPAA, US GLBA)
        title_and_inst = f"{obligation.title} {obligation.legal_instrument} {obligation.official_citation}".lower()
        if "phipa" in title_and_inst or (jur == "CA-ON" and obligation.domain_category == "health_privacy"):
            is_ontario_hic = (
                org.organization_type in {"health_information_custodian", "hospital", "healthcare_covered_entity"}
                or org.industry in {"healthcare", "hospital"}
                or bool(set(act.data_categories) & {"phi", "health_information", "medical_records", "personal_health_information"})
            )
            if not is_ontario_hic:
                return ApplicabilityMappingOutcome(
                    evaluation_id=jrae_resp.evaluation_id,
                    organization_name=org.name or "Enterprise Organization",
                    jurisdiction_id=jur,
                    jurisdiction_layer=obligation.jurisdiction_layer,
                    applies=False,
                    applicability_status="exempt",
                    confidence=0.96,
                    requires_legal_review=False,
                    matched_establishments=matched_est,
                    matched_subject_locations=matched_subj,
                    reasoning="Ontario PHIPA applies to Health Information Custodians (HICs) and their agents handling personal health information; organization sector/data is outside PHIPA scope.",
                    obligation=obligation,
                    jrae_response=jrae_resp,
                )

        if "hipaa" in title_and_inst or "164.404" in title_and_inst:
            is_hipaa = (
                org.hipaa_status in {"covered_entity", "business_associate", "hybrid_entity"}
                or org.organization_type in {"healthcare_covered_entity", "business_associate"}
                or (org.industry in {"healthcare", "hospital"} and bool(matched_data))
            )
            if not is_hipaa:
                return ApplicabilityMappingOutcome(
                    evaluation_id=jrae_resp.evaluation_id,
                    organization_name=org.name or "Enterprise Organization",
                    jurisdiction_id=jur,
                    jurisdiction_layer=obligation.jurisdiction_layer,
                    applies=False,
                    applicability_status="exempt",
                    confidence=0.96,
                    requires_legal_review=False,
                    matched_establishments=matched_est,
                    matched_subject_locations=matched_subj,
                    reasoning="HIPAA obligation requires Covered Entity or Business Associate status handling PHI.",
                    obligation=obligation,
                    jrae_response=jrae_resp,
                )

        # 4. Statutory Threshold Evaluation (with strict Employee Count > 5 Guardrail)
        thresholds_eval, thresholds_passed, threshold_missing = self._evaluate_thresholds(org, act, obligation)

        if not thresholds_passed and not threshold_missing:
            return ApplicabilityMappingOutcome(
                evaluation_id=jrae_resp.evaluation_id,
                organization_name=org.name or "Enterprise Organization",
                jurisdiction_id=jur,
                jurisdiction_layer=obligation.jurisdiction_layer,
                applies=False,
                applicability_status="exempt",
                confidence=0.96,
                requires_legal_review=False,
                matched_establishments=matched_est,
                matched_subject_locations=matched_subj,
                matched_sectors=matched_sectors,
                matched_roles=matched_roles,
                matched_data_categories=matched_data,
                matched_processing_activities=matched_acts,
                thresholds_evaluated=thresholds_eval,
                reasoning=(
                    f"Organization in {jur} does not meet statutory applicability thresholds "
                    f"(evaluated: {thresholds_eval}). Note: employee_count={org.employee_count} (>5) "
                    "alone never triggers statutory applicability."
                ),
                obligation=obligation,
                jrae_response=jrae_resp,
            )

        status = "conditionally_applicable" if threshold_missing else "applicable"
        if obligation.effective_date > when:
            status = "applicable_future_preparation"

        requires_review = bool(threshold_missing or obligation.requires_legal_review)
        reasoning_parts = [
            f"Jurisdictional nexus established in {jur} (establishments={matched_est}, subjects={matched_subj}).",
            f"Matched role={matched_roles}, sector={matched_sectors}, data_categories={matched_data}, activities={matched_acts}.",
        ]
        if thresholds_eval:
            reasoning_parts.append(f"Statutory thresholds evaluated: {thresholds_eval} (employee count > 5 never assumed sufficient).")
        else:
            reasoning_parts.append("No unmet statutory threshold exclusions; employee count > 5 guardrail enforced.")

        return ApplicabilityMappingOutcome(
            evaluation_id=jrae_resp.evaluation_id,
            organization_name=org.name or "Enterprise Organization",
            jurisdiction_id=jur,
            jurisdiction_layer=obligation.jurisdiction_layer,
            applies=True,
            applicability_status=status,
            confidence=0.75 if requires_review else 0.96,
            requires_legal_review=requires_review,
            matched_establishments=matched_est,
            matched_subject_locations=matched_subj,
            matched_sectors=matched_sectors,
            matched_roles=matched_roles,
            matched_data_categories=matched_data,
            matched_processing_activities=matched_acts,
            thresholds_evaluated=thresholds_eval,
            employee_count_guardrail_verified=True,
            reasoning=" ".join(reasoning_parts),
            triggered_controls=list(obligation.required_controls),
            triggered_assessments=list(obligation.required_assessments),
            statutory_deadlines=obligation.response_deadlines.model_dump(),
            obligation=obligation,
            jrae_response=jrae_resp,
        )

    # ------------------------------------------------------------------
    # Internal Evaluation Helpers
    # ------------------------------------------------------------------
    def _evaluate_sector_match(self, org: OrganizationProfileInput, obligation: Obligation) -> List[str]:
        org_ind = (org.industry or "").lower()
        org_type = (org.organization_type or "").lower()
        matched: List[str] = []
        for sec in obligation.sectors:
            if sec == SectorClassification.CROSS_SECTOR:
                matched.append(org_ind or "cross_sector")
            elif sec.value in org_ind or org_ind in sec.value or sec.value in org_type:
                matched.append(sec.value)
            elif sec in (SectorClassification.HEALTHCARE, SectorClassification.HOSPITAL) and (
                "health" in org_ind or "hospital" in org_ind or "health" in org_type
            ):
                matched.append(sec.value)
        if not matched:
            matched.append(org_ind or "general")
        return sorted(set(matched))

    def _evaluate_role_match(self, org: OrganizationProfileInput, obligation: Obligation) -> List[str]:
        org_role = (org.role or "controller").lower()
        matched: List[str] = []
        for r in obligation.regulated_roles:
            if r.value == org_role:
                matched.append(r.value)
            elif org_role == "controller" and r in (RegulatedRole.CONTROLLER, RegulatedRole.BUSINESS, RegulatedRole.DEPLOYER):
                matched.append(r.value)
            elif org_role in ("processor", "service_provider") and r in (RegulatedRole.PROCESSOR, RegulatedRole.SERVICE_PROVIDER, RegulatedRole.CONTRACTOR):
                matched.append(r.value)
        if not matched:
            matched.append(org_role)
        return sorted(set(matched))

    def _evaluate_data_category_match(
        self,
        org: OrganizationProfileInput,
        act: ProcessingActivityInput,
        obligation: Obligation,
    ) -> List[str]:
        declared = {c.lower() for c in act.data_categories}
        matched: List[str] = []
        for cat in obligation.data_categories:
            if cat.value in declared or cat in (DataCategory.PERSONAL_DATA, DataCategory.PERSONAL_INFORMATION):
                matched.append(cat.value)
            elif cat in (DataCategory.PROTECTED_HEALTH_INFORMATION, DataCategory.HEALTH_INFORMATION) and (
                declared & {"phi", "health_information", "health_data", "medical_records", "personal_health_information"}
            ):
                matched.append(cat.value)
            elif cat == DataCategory.COOKIES_AND_TRACKERS and act.involves_targeted_advertising_or_cookies:
                matched.append(cat.value)
            elif cat == DataCategory.BIOMETRIC_DATA and act.involves_biometrics:
                matched.append(cat.value)
            elif cat == DataCategory.AI_TRAINING_AND_PROFILING_DATA and act.involves_ai_or_admt:
                matched.append(cat.value)
        if not matched and declared:
            matched.extend(sorted(declared))
        return sorted(set(matched))

    def _evaluate_activity_match(self, act: ProcessingActivityInput, obligation: Obligation) -> List[str]:
        matched = [a.value for a in obligation.processing_activities]
        if act.involves_ai_or_admt and ProcessingActivityType.AI_OR_ADMT_PROFILING.value not in matched:
            matched.append(ProcessingActivityType.AI_OR_ADMT_PROFILING.value)
        if act.involves_targeted_advertising_or_cookies and ProcessingActivityType.TARGETED_ADVERTISING_OR_COOKIES.value not in matched:
            matched.append(ProcessingActivityType.TARGETED_ADVERTISING_OR_COOKIES.value)
        if act.involves_cross_border_transfer and ProcessingActivityType.CROSS_BORDER_TRANSFER.value not in matched:
            matched.append(ProcessingActivityType.CROSS_BORDER_TRANSFER.value)
        return sorted(set(matched))

    def _evaluate_thresholds(
        self,
        org: OrganizationProfileInput,
        act: ProcessingActivityInput,
        obligation: Obligation,
    ) -> Tuple[List[Dict[str, Any]], bool, bool]:
        """
        Evaluates statutory thresholds on `obligation`.
        Never assumes `employee_count > 5` alone triggers applicability.
        Returns `(evaluated_list, passed, has_missing_metric)`.
        """
        evaluated: List[Dict[str, Any]] = []
        jur = obligation.jurisdiction_id

        # Check California CCPA/CPRA 3-prong business thresholds whenever evaluating a CCPA/CPRA obligation
        is_ccpa = jur == "US-CA" and (
            "1798" in obligation.official_citation
            or "ccpa" in obligation.title.lower()
            or "cpra" in obligation.title.lower()
            or "cppa" in obligation.legal_authority.lower()
        )
        if is_ccpa:
            if org.organization_type in {"nonprofit", "government_agency", "public"}:
                evaluated.append(
                    {
                        "metric": "for_profit_business_status",
                        "value": org.organization_type,
                        "threshold": "private_for_profit",
                        "met": False,
                    }
                )
                return evaluated, False, False

            prongs = [
                ("annual_revenue_usd", org.annual_revenue_usd, 26625000),
                ("consumer_records_count", org.consumer_records_count, 100000),
                ("data_broker_revenue_pct", org.data_broker_revenue_pct, 50.0),
            ]
            for name, val, minimum in prongs:
                met = None if val is None else (float(val) >= float(minimum))
                evaluated.append({"metric": name, "value": val, "threshold": minimum, "met": met})

            # Explicitly record that employee_count > 5 does NOT satisfy CCPA/CPRA thresholds
            evaluated.append(
                {
                    "metric": "employee_count_guardrail",
                    "value": org.employee_count,
                    "threshold": "never_triggers_ccpa_alone",
                    "met": False,
                }
            )
            any_met = any(item["met"] is True for item in evaluated if item["metric"] != "employee_count_guardrail")
            any_missing = any(item["met"] is None for item in evaluated if item["metric"] != "employee_count_guardrail")
            return evaluated, any_met, (not any_met and any_missing)

        # Check German BDSG § 38 DPO designation threshold (20 persons in automated processing OR Art. 35 DPIA / profiling)
        if jur == "EU-DE" and ("38" in obligation.official_citation or "bdsg_38" in obligation.title.lower()):
            emp = org.employee_count
            met_headcount = None if emp is None else (emp >= 20)
            met_dpia_override = bool(act.involves_ai_or_admt or act.involves_biometrics)
            evaluated.append(
                {
                    "metric": "min_persons_automated_processing_bdsg_38",
                    "value": emp,
                    "threshold": 20,
                    "met": met_headcount,
                }
            )
            evaluated.append(
                {
                    "metric": "bdsg_38_sentence_2_dpia_high_risk_override",
                    "value": met_dpia_override,
                    "threshold": True,
                    "met": met_dpia_override,
                }
            )
            passed = (met_headcount is True) or met_dpia_override
            missing = (not passed) and (met_headcount is None)
            return evaluated, passed, missing

        return evaluated, True, False

    @staticmethod
    def _build_deadline_spec(jur: str, deadline_text: Optional[str], text_hint: str) -> ResponseDeadlineSpec:
        t = (deadline_text or "") + " " + text_hint.lower()
        dsar_days = 30 if jur.startswith(("CA-", "EU")) else 45
        if "15 business days" in t:
            dsar_days = 15
        breach_hours = 72 if jur.startswith("EU") else None
        breach_ind_days = 60 if "164.404" in t or "60 calendar days" in t else None
        return ResponseDeadlineSpec(
            rights_request_initial_days=dsar_days,
            rights_request_day_type="business_days" if "15 business days" in t else "calendar_days",
            rights_request_extension_days=60 if jur.startswith("EU") else 45 if jur.startswith("US-") else 30,
            breach_regulator_hours=breach_hours,
            breach_individual_notification_days=breach_ind_days,
            breach_regulator_text=deadline_text or "Without unreasonable delay",
        )

    @staticmethod
    def _infer_controls_from_text(jur: str, provision_ref: str, text_hint: str) -> List[str]:
        t = text_hint.lower()
        controls: List[str] = []
        if "1798.100(d)" in provision_ref or "contractor" in t or "service provider" in t:
            controls.append("CTRL-CPRA-1798-100D-SERVICE-PROVIDER-CONTRACTOR-DPA")
        if "1798.185" in provision_ref or "cybersecurity audit" in t or "admt" in t:
            controls.extend(["CTRL-CPPA-ADMT-PRE-USE-NOTICE-AND-OPTOUT", "CTRL-CPPA-ANNUAL-CYBERSECURITY-AUDIT"])
        if "5(3)" in provision_ref or "cookie" in t or "art. 82" in t:
            controls.append("CTRL-PRIOR-OPT-IN-COOKIE-CONSENT-BANNER")
        if "35" in provision_ref or "dpia" in t:
            controls.append("CTRL-GDPR-ART35-PRE-PROCESSING-DPIA-GATE")
        if not controls:
            controls.append(f"CTRL-{jur}-STATUTORY-COMPLIANCE-GATE")
        return controls

    @staticmethod
    def _infer_assessments_from_text(jur: str, text_hint: str) -> List[str]:
        t = text_hint.lower()
        assessments: List[str] = []
        if jur == "US-CA" and ("admt" in t or "risk assessment" in t or "1798.185" in t or "profiling" in t):
            assessments.append("CPPA_ADMT_and_Privacy_Risk_Assessment")
        if jur == "CA-QC" or "law 25" in t or "loi 25" in t or "éfvp" in t or "efvp" in t:
            assessments.append("Quebec_Law25_EFVP_PIA")
        if jur == "CA-ON" or "phipa" in t:
            assessments.extend(["Ontario_PHIPA_s12_Lockbox_and_Breach_Review", "PHIPA_TRA_and_PIA"])
        if jur == "EU-FR" or "cnil" in t or "art. 82" in t or "cookie" in t:
            assessments.append("CNIL_Art82_Cookie_and_Tracker_Consent_Audit")
        if jur == "EU-DE" or "bdsg" in t:
            assessments.append("German_BDSG_s26_s38_DPO_and_Employee_Monitoring_DPIA")
        if jur.startswith("EU") and ("dpia" in t or "art. 35" in t or "high risk" in t):
            assessments.append("GDPR_Art35_DPIA")
        if not assessments:
            assessments.append(f"{jur}_Regulatory_Impact_Assessment")
        return assessments


__all__ = [
    "ApplicabilityMappingOutcome",
    "DataCategory",
    "JurisdictionLayer",
    "Obligation",
    "OrganizationProfile",
    "ProcessingActivityType",
    "RegulatedRole",
    "RegulatoryApplicabilityBridge",
    "SectorClassification",
]
