"""
KIBO Privacy OS — Canadian Regulatory Pack (JRAE canonical regulations).

Coverage:
- Federal (CA-FED): PIPEDA, Privacy Act (+ TBS PIA/Privacy Practices directives),
  Access to Information Act, CASL, OSFI B-13 / B-10.
- All 10 provinces and 3 territories: private-sector, public-sector and
  health-information statutes.

Conventions:
- `applicability_conditions` keys mirror `OrganizationProfileInput` /
  `ProcessingActivityInput` field names with an `_any` suffix meaning
  "intersects any of" (e.g. `establishments_any`, `subject_locations_any`,
  `organization_types_any`, `data_categories_any`).
- `source_document_hash` is a deterministic SHA-256 of the citation key
  (regulation id, instrument, section, source URL, rule version). It identifies
  the catalogued citation, NOT a hash of the fetched statute text; the ingestion
  pipeline replaces it once the official document is fetched and hashed.
- Entries whose deadlines or in-force dates come from recent amendments that
  have not been re-verified against the official consolidation are marked
  `LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF` and carry a `counsel_review_note`
  in `applicability_conditions`.
"""

import hashlib
from datetime import date, datetime
from typing import Any, Dict, List

from core.jrae.schemas import (
    CanonicalRegulation,
    DeploymentStatus,
    ExemptionRule,
    JurisdictionType,
    LegalReviewStatus,
    PreemptionRule,
    RegulatoryStatus,
    ResponseDeadlineSpec,
    StatutoryThreshold,
)

RULE_VERSION = "2026.10.1"
LAST_VERIFIED_AT = datetime(2026, 10, 25, 0, 0, 0)

# Provinces whose private-sector statutes are declared "substantially similar"
# to PIPEDA Part 1 (Organizations in the Province of Quebec Exemption Order,
# SOR/2003-374; Alberta SOR/2004-219; British Columbia SOR/2004-220).
SUBSTANTIALLY_SIMILAR_PRIVATE_SECTOR = {
    "CA-QC-LAW25": "CA-QC",
    "CA-AB-PIPA": "CA-AB",
    "CA-BC-PIPA": "CA-BC",
}

# Health-information statutes declared substantially similar to PIPEDA for
# health information custodians (Ontario SOR/2005-399; New Brunswick
# SOR/2011-265; Newfoundland and Labrador SOR/2012-72; Nova Scotia SOR/2016-62).
SUBSTANTIALLY_SIMILAR_HEALTH = {
    "CA-ON-PHIPA": ("CA-ON", "SOR/2005-399"),
    "CA-NB-PHIPAA": ("CA-NB", "SOR/2011-265"),
    "CA-NL-PHIA": ("CA-NL", "SOR/2012-72"),
    "CA-NS-PHIA": ("CA-NS", "SOR/2016-62"),
}

PUBLIC_SECTOR_ORG_TYPES = ["public", "government_agency", "educational_institution"]
HEALTH_ORG_TYPES = ["health_information_custodian", "healthcare_covered_entity"]
HEALTH_DATA = ["health", "personal_health_information", "medical", "genetic"]


def _source_hash(regulation_id: str, instrument: str, section: str, url: str) -> str:
    key = "|".join([regulation_id, instrument, section, url, RULE_VERSION])
    return "sha256:" + hashlib.sha256(key.encode("utf-8")).hexdigest()


def _reg(**kwargs: Any) -> CanonicalRegulation:
    """Fill in shared Canadian defaults and the citation hash."""
    kwargs.setdefault("country", "CA")
    kwargs.setdefault("rule_version", RULE_VERSION)
    kwargs.setdefault("last_verified_at", LAST_VERIFIED_AT)
    kwargs.setdefault("deployment_status", DeploymentStatus.PRODUCTION_ENABLED)
    kwargs.setdefault("regulatory_status", RegulatoryStatus.EFFECTIVE)
    kwargs.setdefault("legal_review_status", LegalReviewStatus.VERIFIED)
    kwargs["source_document_hash"] = _source_hash(
        kwargs["regulation_id"],
        kwargs["legal_instrument"],
        kwargs["article_or_section"],
        kwargs["official_source_url"],
    )
    return CanonicalRegulation(**kwargs)


def _province(code: str, name: str, territory: bool = False) -> Dict[str, Any]:
    return {
        "jurisdiction_id": code,
        "jurisdiction_type": JurisdictionType.TERRITORY if territory else JurisdictionType.PROVINCE,
        "state_or_province": name,
    }


# ---------------------------------------------------------------------------
# 1. FEDERAL (CA-FED)
# ---------------------------------------------------------------------------

def _federal() -> List[CanonicalRegulation]:
    fed = {"jurisdiction_id": "CA-FED", "jurisdiction_type": JurisdictionType.FEDERAL}
    regs: List[CanonicalRegulation] = []

    pipeda_preemption = [
        PreemptionRule(
            rule_id=f"CA-FED-PIPEDA-YIELDS-{target}",
            preempts_or_yields="yields_to",
            target_regulation_id=target,
            scope_condition=(
                f"organization establishments include {prov} AND collection/use/disclosure occurs "
                f"entirely within {prov} in the course of commercial activity AND "
                "is_federally_regulated_canada == False"
            ),
            description=(
                f"{target} is declared substantially similar to PIPEDA Part 1 (PIPEDA s. 26(2)(b) "
                "exemption order). Intraprovincial commercial handling is governed by the provincial "
                "statute; PIPEDA continues to apply to federal works, undertakings or businesses "
                "and to personal information crossing provincial or national borders."
            ),
        )
        for target, prov in SUBSTANTIALLY_SIMILAR_PRIVATE_SECTOR.items()
    ]
    pipeda_preemption += [
        PreemptionRule(
            rule_id=f"CA-FED-PIPEDA-YIELDS-{target}",
            preempts_or_yields="yields_to",
            target_regulation_id=target,
            scope_condition=(
                f"organization_type == 'health_information_custodian' AND establishments include {prov} "
                "AND personal health information handled within the province"
            ),
            description=(
                f"Health information custodians subject to {target} are exempt from PIPEDA Part 1 for "
                f"intraprovincial collection, use and disclosure of personal health information ({order})."
            ),
        )
        for target, (prov, order) in SUBSTANTIALLY_SIMILAR_HEALTH.items()
    ]
    pipeda_preemption += [
        PreemptionRule(
            rule_id="CA-FED-PIPEDA-FWUB",
            preempts_or_yields="preempts",
            target_regulation_id="CA-QC-LAW25,CA-AB-PIPA,CA-BC-PIPA",
            scope_condition="is_federally_regulated_canada == True",
            description=(
                "Federal works, undertakings or businesses (banks, telecommunications, broadcasting, "
                "interprovincial transportation, airlines, etc.) remain subject to PIPEDA in every "
                "province, including for employee personal information (PIPEDA s. 4(1)(b))."
            ),
        ),
        PreemptionRule(
            rule_id="CA-FED-PIPEDA-CROSSBORDER",
            preempts_or_yields="concurrent_with",
            target_regulation_id="CA-QC-LAW25,CA-AB-PIPA,CA-BC-PIPA",
            scope_condition=(
                "personal information is disclosed across a provincial or national border for "
                "consideration / in the course of commercial activity"
            ),
            description=(
                "Interprovincial and international flows of personal information in commercial "
                "activity remain subject to PIPEDA concurrently with the provincial statute."
            ),
        ),
    ]

    regs.append(_reg(
        **fed,
        regulation_id="CA-FED-PIPEDA",
        legal_authority="Parliament of Canada",
        legal_instrument="Personal Information Protection and Electronic Documents Act (S.C. 2000, c. 5)",
        official_source_url="https://laws-lois.justice.gc.ca/eng/acts/P-8.6/",
        article_or_section=(
            "Part 1, ss. 4-10.3; Schedule 1 (CSA Model Code principles 4.1-4.10); s. 8(3)-(4) access "
            "deadlines; ss. 10.1-10.3 breach of security safeguards; Breach of Security Safeguards "
            "Regulations (SOR/2018-64)"
        ),
        effective_date=date(2001, 1, 1),
        applicability_conditions={
            "commercial_activity": True,
            "organization_types_any": ["private", "nonprofit_commercial_activity", "financial_institution"],
            "applies_if_is_federally_regulated_canada": True,
            "applies_to_interprovincial_or_international_flows": True,
            "applies_intraprovincially_except_in": ["CA-QC", "CA-AB", "CA-BC"],
            "employee_information_only_if_federally_regulated": True,
            "full_application_date": "2004-01-01",
            "breach_provisions_in_force": "2018-11-01",
            "note": (
                "Bill C-27 (Consumer Privacy Protection Act / AIDA) died on the Order Paper on "
                "prorogation in January 2025; PIPEDA remains the operative federal private-sector law."
            ),
        },
        thresholds=[
            StatutoryThreshold(
                metric="commercial_activity",
                operator="==",
                value=True,
                logic_group="OR",
                description="Collects, uses or discloses personal information in the course of commercial activity (s. 4(1)(a)).",
            ),
            StatutoryThreshold(
                metric="is_federally_regulated_canada",
                operator="==",
                value=True,
                logic_group="OR",
                description="Federal work, undertaking or business — PIPEDA applies including to employee information (s. 4(1)(b)).",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CA-FED-PIPEDA-EX-PERSONAL",
                exemption_type="activity_level",
                condition_field="purpose",
                condition_values=["personal", "domestic"],
                description="Personal or domestic purposes are excluded (s. 4(2)(b)).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-PIPEDA-EX-JOURNALISTIC",
                exemption_type="activity_level",
                condition_field="purpose",
                condition_values=["journalistic", "artistic", "literary"],
                description="Journalistic, artistic or literary purposes are excluded (s. 4(2)(c)).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-PIPEDA-EX-BCI",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["business_contact_information"],
                description="Business contact information used solely to communicate in relation to employment/business (s. 4.01).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-PIPEDA-EX-PUBLIC-SECTOR",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["government_agency"],
                carve_out_statute="CA-FED-PRIVACY-ACT",
                description="Government institutions subject to the Privacy Act are excluded (s. 4(2)(a)).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-PIPEDA-EX-PROVINCIAL-EMPLOYEE",
                exemption_type="data_level",
                condition_field="data_subject_categories",
                condition_values=["employees"],
                description="Employee personal information of provincially regulated employers is outside PIPEDA (s. 4(1)(b) limited to FWUBs).",
            ),
        ],
        preemption_rules=pipeda_preemption,
        organization_types=["private", "financial_institution", "nonprofit"],
        industry_sectors=["all_commercial", "banking", "telecommunications", "broadcasting", "transportation", "technology"],
        data_subject_categories=["consumers", "customers", "employees_of_fwub"],
        data_categories=["personal_information", "sensitive_personal_information"],
        processing_activities=["collection", "use", "disclosure", "cross_border_transfer", "retention"],
        required_actions=[
            "Designate an individual accountable for compliance (Principle 4.1)",
            "Identify purposes at or before collection (Principle 4.2)",
            "Obtain meaningful consent; express consent for sensitive information (Principle 4.3, s. 6.1)",
            "Limit collection, use, disclosure and retention to identified purposes (Principles 4.4-4.5)",
            "Implement security safeguards proportionate to sensitivity (Principle 4.7)",
            "Publish privacy policies and practices (Principle 4.8)",
            "Respond to access/correction requests within 30 days (s. 8(3))",
            "Use contractual or other means to ensure comparable protection when transferring to third-party processors (Principle 4.1.3)",
            "Notify individuals of cross-border processing by service providers (OPC Guidelines for Processing Personal Data Across Borders)",
            "Report breaches posing a real risk of significant harm to the OPC as soon as feasible (s. 10.1(1)-(2))",
            "Notify affected individuals and relevant third parties as soon as feasible (s. 10.1(3)-(6), s. 10.2)",
            "Maintain records of every breach of security safeguards for 24 months (s. 10.3; SOR/2018-64 s. 6)",
        ],
        required_assessments=["RROSH_Assessment", "PIA_Recommended", "Cross_Border_Transfer_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="calendar_days",
            rights_request_extension_days=30,
            identity_verification_required=True,
            breach_regulator_text=(
                "As soon as feasible after the organization determines the breach creates a real "
                "risk of significant harm (RROSH) — report to the Privacy Commissioner of Canada (s. 10.1(2))"
            ),
            breach_individual_text=(
                "As soon as feasible after determining RROSH; direct notification unless indirect "
                "notification is permitted under SOR/2018-64 s. 5 (s. 10.1(3), (6))"
            ),
            record_retention_years=2,
        ),
        notification_requirements=[
            "OPC breach report (RROSH) — content per SOR/2018-64 s. 2",
            "Individual breach notification — content per SOR/2018-64 s. 3",
            "Third-party / government institution notification where it may reduce or mitigate harm (s. 10.2)",
            "Notice of extension of access deadline within initial 30 days (s. 8(4))",
        ],
        required_evidence=[
            "Breach record register retained 24 months, available to OPC on request",
            "RROSH determination memo (sensitivity + probability of misuse)",
            "Consent records and privacy policy versions",
            "Access request log with response dates",
            "Service provider contracts with privacy/security clauses",
        ],
        approval_requirements=["Privacy Officer sign-off on RROSH determination", "Legal review of OPC breach report"],
        competent_regulator="Office of the Privacy Commissioner of Canada (OPC)",
        subnational_regulators={
            "CA-QC": "Commission d'accès à l'information du Québec (CAI)",
            "CA-AB": "Office of the Information and Privacy Commissioner of Alberta (OIPC-AB)",
            "CA-BC": "Office of the Information and Privacy Commissioner for British Columbia (OIPC-BC)",
        },
        domain_category="privacy",
    ))

    regs.append(_reg(
        **fed,
        regulation_id="CA-FED-PRIVACY-ACT",
        legal_authority="Parliament of Canada; Treasury Board of Canada Secretariat (TBS)",
        legal_instrument=(
            "Privacy Act (R.S.C., 1985, c. P-21); TBS Policy on Privacy Protection; "
            "Directive on Privacy Impact Assessment; Directive on Privacy Practices"
        ),
        official_source_url="https://laws-lois.justice.gc.ca/eng/acts/P-21/",
        article_or_section=(
            "ss. 4-8 collection/use/disclosure; s. 10 personal information banks; ss. 12-15 access "
            "(30 days + up to 30-day extension); TBS Directive on PIA; Directive on Privacy Practices "
            "(material privacy breach reporting)"
        ),
        effective_date=date(1983, 7, 1),
        applicability_conditions={
            "organization_types_any": ["government_agency", "public"],
            "establishments_any": ["CA-FED"],
            "federal_government_institution": True,
            "schedule": "Government institutions listed in the Schedule to the Privacy Act",
        },
        exemptions=[
            ExemptionRule(
                exemption_id="CA-FED-PA-EX-PRIVATE",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["private", "nonprofit", "financial_institution"],
                carve_out_statute="CA-FED-PIPEDA",
                description="Private-sector organizations are governed by PIPEDA, not the Privacy Act.",
            ),
        ],
        organization_types=["government_agency", "public"],
        industry_sectors=["federal_government", "crown_corporations"],
        data_subject_categories=["citizens", "residents", "federal_employees"],
        data_categories=["personal_information"],
        processing_activities=["collection", "use", "disclosure", "retention", "program_administration"],
        required_actions=[
            "Collect only information relating directly to an operating program or activity (s. 4)",
            "Collect directly from the individual and inform of purpose where possible (s. 5)",
            "Retain personal information used for an administrative purpose for at least two years after last use (Privacy Regulations s. 4)",
            "Register Personal Information Banks in Info Source (s. 10-11)",
            "Respond to access requests within 30 days; extensions up to 30 days with notice (ss. 14-15)",
            "Complete a PIA for new or substantially modified programs/activities using personal information (Directive on PIA)",
            "Report material privacy breaches to OPC and TBS (Directive on Privacy Practices)",
        ],
        required_assessments=["Federal_PIA", "Material_Breach_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_extension_days=30,
            breach_regulator_days=7,
            breach_regulator_text=(
                "Material privacy breaches reported to the OPC and TBS no later than 7 days after the "
                "institution determines the breach is material (Directive on Privacy Practices)"
            ),
            breach_individual_text="Notify affected individuals of material breaches as soon as possible",
            record_retention_years=2,
        ),
        notification_requirements=[
            "PIA copy to OPC and TBS; PIA summary published",
            "Material privacy breach report to OPC and TBS",
            "Access extension notice to requester (and to OPC where > 30 days for consultation/translation)",
        ],
        required_evidence=["Approved PIA", "Info Source PIB registration", "ATIP request log", "Privacy breach register"],
        approval_requirements=["Deputy head / delegated ATIP Coordinator approval of PIA"],
        competent_regulator="Office of the Privacy Commissioner of Canada (OPC); Treasury Board of Canada Secretariat (policy)",
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **fed,
        regulation_id="CA-FED-ATIA",
        legal_authority="Parliament of Canada",
        legal_instrument="Access to Information Act (R.S.C., 1985, c. A-1)",
        official_source_url="https://laws-lois.justice.gc.ca/eng/acts/A-1/",
        article_or_section=(
            "s. 4 right of access; s. 7 30-day response; s. 9 extensions; s. 20 third-party "
            "commercial information; ss. 27-28 third-party notice; Part 2 proactive publication (Bill C-58, 2019)"
        ),
        effective_date=date(1983, 7, 1),
        applicability_conditions={
            "organization_types_any": ["government_agency", "public"],
            "establishments_any": ["CA-FED"],
            "also_relevant_to_private_vendors": (
                "Vendors supplying records/confidential commercial information to federal institutions "
                "receive s. 27 third-party notice and may make representations within 20 days (s. 28)"
            ),
        },
        organization_types=["government_agency", "public", "private_government_supplier"],
        industry_sectors=["federal_government", "government_contracting"],
        data_subject_categories=["requesters", "third_parties"],
        data_categories=["government_records", "confidential_commercial_information"],
        processing_activities=["records_management", "access_request_handling", "proactive_disclosure"],
        required_actions=[
            "Respond to access requests within 30 days (s. 7)",
            "Notify Information Commissioner of extensions longer than 30 days (s. 9(2))",
            "Give notice to third parties whose confidential commercial information may be disclosed (s. 27)",
            "Proactively publish prescribed information (Part 2)",
            "Mark supplier submissions containing confidential commercial information (s. 20(1)(b))",
        ],
        required_assessments=["Third_Party_Commercial_Info_Review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_extension_days=None,
            identity_verification_required=False,
            breach_regulator_text="Not applicable (access-to-information statute)",
            breach_individual_text="Not applicable",
        ),
        notification_requirements=["Extension notice to requester; Information Commissioner notified if > 30 days", "s. 27 third-party notice"],
        required_evidence=["Access request log", "Third-party consultation records", "Proactive publication records"],
        competent_regulator="Office of the Information Commissioner of Canada",
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **fed,
        regulation_id="CA-FED-CASL",
        legal_authority="Parliament of Canada",
        legal_instrument="Canada's Anti-Spam Legislation (S.C. 2010, c. 23); Electronic Commerce Protection Regulations (SOR/2013-221; CRTC 2012-36)",
        official_source_url="https://laws-lois.justice.gc.ca/eng/acts/E-1.6/",
        article_or_section=(
            "s. 6 commercial electronic messages (consent, identification, unsubscribe); s. 10 express "
            "and implied consent; s. 8 installation of computer programs; s. 13 onus of proving consent; "
            "s. 20 administrative monetary penalties"
        ),
        effective_date=date(2014, 7, 1),
        applicability_conditions={
            "processing_activities_any": ["email_marketing", "sms_marketing", "commercial_electronic_messages", "software_installation"],
            "message_sent_to_or_from_computer_in_canada": True,
            "software_installation_provisions_in_force": "2015-01-15",
            "private_right_of_action": "Not in force (ss. 47-51 suspended)",
        },
        thresholds=[
            StatutoryThreshold(
                metric="implied_consent_existing_business_relationship_months",
                operator="<=",
                value=24,
                description="Implied consent from purchase/lease/contract lasts 2 years from the transaction (s. 10(10)).",
            ),
            StatutoryThreshold(
                metric="implied_consent_inquiry_months",
                operator="<=",
                value=6,
                description="Implied consent from an inquiry or application lasts 6 months (s. 10(10)(b), (d)).",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CA-FED-CASL-EX-PERSONAL",
                exemption_type="activity_level",
                condition_field="relationship",
                condition_values=["family_relationship", "personal_relationship"],
                description="Messages between individuals with a family or personal relationship (s. 6(5)(a)).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-CASL-EX-B2B",
                exemption_type="activity_level",
                condition_field="relationship",
                condition_values=["b2b_existing_relationship"],
                description="Messages between employees/organizations with a relationship, concerning the recipient's activities (Regulations s. 3(a)).",
            ),
            ExemptionRule(
                exemption_id="CA-FED-CASL-EX-TRANSACTIONAL",
                exemption_type="activity_level",
                condition_field="message_type",
                condition_values=["quote_requested", "transaction_confirmation", "warranty_safety", "account_status", "employment_benefit"],
                description="Consent not required for prescribed transactional messages, but identification and unsubscribe still apply (s. 6(6)).",
            ),
        ],
        organization_types=["private", "nonprofit", "public"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "business_contacts"],
        data_categories=["electronic_address", "contact_information"],
        processing_activities=["email_marketing", "sms_marketing", "direct_messaging", "software_installation"],
        required_actions=[
            "Obtain express or implied consent before sending a commercial electronic message (s. 6(1)(a), s. 10)",
            "Express consent requests must state purpose, sender identity and that consent can be withdrawn (s. 10(1))",
            "Identify the sender and provide contact information valid for at least 60 days (s. 6(2)-(3))",
            "Provide a functioning unsubscribe mechanism valid for at least 60 days after sending (s. 11(1))",
            "Give effect to unsubscribe requests within 10 business days (s. 11(3))",
            "Retain proof of consent — sender bears the onus (s. 13)",
            "Obtain express consent before installing computer programs on another's device (s. 8)",
        ],
        required_assessments=["Consent_Basis_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=10,
            rights_request_day_type="business_days",
            identity_verification_required=False,
            breach_regulator_text="Not applicable",
            breach_individual_text="Not applicable",
        ),
        notification_requirements=["Unsubscribe confirmation processed within 10 business days"],
        required_evidence=["Consent records (date, method, wording, source)", "Unsubscribe processing log", "Implied consent expiry tracking"],
        competent_regulator="Canadian Radio-television and Telecommunications Commission (CRTC); Competition Bureau; OPC",
        domain_category="electronic_communications",
    ))

    # OSFI guidelines are sectoral (federally regulated financial institutions only).
    regs.append(_reg(
        jurisdiction_id="CA-FED",
        jurisdiction_type=JurisdictionType.SECTORAL,
        regulation_id="CA-FED-OSFI-B13",
        legal_authority="Office of the Superintendent of Financial Institutions (OSFI), under the OSFI Act, Bank Act, Insurance Companies Act and Trust and Loan Companies Act",
        legal_instrument=(
            "OSFI Guideline B-13: Technology and Cyber Risk Management (July 2022); OSFI Guideline B-10: "
            "Third-Party Risk Management (April 2023); OSFI Technology and Cyber Security Incident Reporting Advisory"
        ),
        official_source_url="https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/technology-cyber-risk-management",
        article_or_section=(
            "B-13 Domains 1-3 (governance & risk management; technology operations & resilience; cyber "
            "security); B-10 third-party risk lifecycle; Incident Reporting Advisory (24-hour report)"
        ),
        effective_date=date(2024, 1, 1),
        applicability_conditions={
            "organization_types_any": ["financial_institution"],
            "is_federally_regulated_canada": True,
            "frfi": True,
            "b10_effective_date": "2024-05-01",
            "b10_source_url": "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/third-party-risk-management-guideline",
        },
        thresholds=[
            StatutoryThreshold(
                metric="organization_type",
                operator="==",
                value="financial_institution",
                logic_group="AND",
                description="Federally regulated financial institution (banks, federally incorporated insurers, trust and loan companies).",
            ),
            StatutoryThreshold(
                metric="is_federally_regulated_canada",
                operator="==",
                value=True,
                logic_group="AND",
                description="Supervised by OSFI.",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CA-FED-OSFI-EX-PROVINCIAL",
                exemption_type="entity_level",
                condition_field="regulator",
                condition_values=["provincial_credit_union", "provincial_insurer", "AMF_regulated"],
                description="Provincially regulated institutions (e.g. credit unions, AMF-regulated insurers) are outside OSFI guidelines.",
            ),
        ],
        organization_types=["financial_institution"],
        industry_sectors=["banking", "insurance", "trust_and_loan"],
        data_subject_categories=["customers", "employees"],
        data_categories=["financial", "personal_information", "system_data"],
        processing_activities=["technology_operations", "outsourcing", "cloud_hosting", "third_party_arrangements"],
        required_actions=[
            "Establish technology and cyber risk governance with defined accountability (B-13 Domain 1)",
            "Maintain technology asset inventory and resilience / disaster recovery testing (B-13 Domain 2)",
            "Implement cyber security controls, threat intelligence and continuous monitoring (B-13 Domain 3)",
            "Report technology or cyber security incidents to OSFI within 24 hours or sooner and provide regular updates",
            "Maintain a third-party arrangement inventory and risk-based due diligence (B-10)",
            "Include audit, data location, security, subcontracting and exit provisions in third-party contracts (B-10)",
            "Notify OSFI of material third-party arrangements as required (B-10)",
        ],
        required_assessments=["Technology_Cyber_Risk_Assessment", "Third_Party_Risk_Assessment", "Cloud_Concentration_Risk_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            breach_regulator_hours=24,
            breach_regulator_text=(
                "Report reportable technology/cyber security incidents to the OSFI Lead Supervisor and "
                "TRD@osfi-bsif.gc.ca within 24 hours, or sooner if possible"
            ),
            breach_individual_text="Governed by PIPEDA s. 10.1 where personal information is involved",
            identity_verification_required=False,
        ),
        notification_requirements=["OSFI incident report (24h) with subsequent updates", "Post-incident review summary to OSFI on request"],
        required_evidence=["Technology risk framework", "Third-party inventory", "Incident reports and timelines", "Resilience test results"],
        approval_requirements=["Senior management accountability for incident reporting", "Board oversight of technology and third-party risk"],
        competent_regulator="Office of the Superintendent of Financial Institutions (OSFI)",
        domain_category="cybersecurity",
    ))

    return regs


# ---------------------------------------------------------------------------
# 2. QUEBEC (CA-QC)
# ---------------------------------------------------------------------------

def _quebec() -> List[CanonicalRegulation]:
    qc = _province("CA-QC", "Quebec")
    cai = "Commission d'accès à l'information du Québec (CAI)"
    regs: List[CanonicalRegulation] = []

    regs.append(_reg(
        **qc,
        regulation_id="CA-QC-LAW25",
        legal_authority="Assemblée nationale du Québec",
        legal_instrument=(
            "Act respecting the protection of personal information in the private sector (CQLR c. P-39.1), "
            "as amended by the Act to modernize legislative provisions as regards the protection of personal "
            "information (Law 25 / Bill 64, S.Q. 2021, c. 25); Regulation respecting confidentiality incidents "
            "(c. P-39.1, r. 3.1)"
        ),
        official_source_url="https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1",
        article_or_section=(
            "s. 3.1 person in charge of protection of personal information; s. 3.2 governance policies; "
            "s. 3.3 PIA for information systems / electronic service delivery; ss. 3.5-3.8 confidentiality "
            "incidents and register; s. 4.1 minors under 14; s. 8.1 profiling/tracking technologies; "
            "s. 9.1 privacy by default; s. 12.1 automated decisions; s. 17 communication outside Quebec; "
            "s. 27 access and computerized portability; s. 28.1 de-indexation; s. 32 30-day response; "
            "ss. 90.1-90.17 administrative monetary penalties; ss. 91-92.1 penal offences"
        ),
        original_language="fr",
        verified_translation="en",
        effective_date=date(1994, 1, 1),
        applicability_conditions={
            "establishments_any": ["CA-QC"],
            "subject_locations_any": ["CA-QC"],
            "organization_types_any": ["private", "nonprofit", "financial_institution", "processor"],
            "enterprise_within_civil_code_art_1525": True,
            "law25_phase_dates": {
                "phase_1": "2022-09-22 (privacy officer, incident reporting, biometrics disclosure)",
                "phase_2": "2023-09-22 (PIA, s. 17 transfers, consent, transparency, ADM, de-indexation, privacy by default)",
                "phase_3": "2024-09-22 (computerized data portability, s. 27 para. 3)",
            },
            "language_requirement": (
                "Charter of the French Language (CQLR c. C-11) as amended by Bill 96 (S.Q. 2022, c. 14): "
                "privacy notices, consent forms and contracts of adhesion must be available in French; "
                "French version prevails / must be at least as favourable"
            ),
        },
        thresholds=[
            StatutoryThreshold(
                metric="minor_age",
                operator="<",
                value=14,
                description="Consent for a minor under 14 must be given by the person having parental authority or the tutor (s. 4.1).",
            ),
            StatutoryThreshold(
                metric="amp_max_cad",
                operator="<=",
                value="max(10000000, 0.02 * worldwide_turnover)",
                currency="CAD",
                description="Administrative monetary penalty ceiling: CAD 10M or 2% of worldwide turnover of the preceding fiscal year (s. 90.12).",
            ),
            StatutoryThreshold(
                metric="penal_fine_max_cad",
                operator="<=",
                value="max(25000000, 0.04 * worldwide_turnover)",
                currency="CAD",
                description="Penal fines up to CAD 25M or 4% of worldwide turnover (s. 91).",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CA-QC-LAW25-EX-JOURNALISTIC",
                exemption_type="activity_level",
                condition_field="purpose",
                condition_values=["journalistic", "historical", "genealogical"],
                description="Journalistic, historical or genealogical material collected for the legitimate information of the public (s. 1 para. 4).",
            ),
            ExemptionRule(
                exemption_id="CA-QC-LAW25-EX-BCI",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["business_contact_information"],
                description="Divisions 3 and 4 do not apply to business contact information concerning a person's role in an enterprise (s. 1 para. 5).",
            ),
            ExemptionRule(
                exemption_id="CA-QC-LAW25-EX-PUBLIC-BODY",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["government_agency", "public"],
                carve_out_statute="CA-QC-PUBLIC-ACCESS",
                description="Public bodies are governed by CQLR c. A-2.1.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="CA-QC-LAW25-SUBSTANTIALLY-SIMILAR",
                preempts_or_yields="preempts",
                target_regulation_id="CA-FED-PIPEDA",
                scope_condition="intraprovincial commercial activity in Quebec AND is_federally_regulated_canada == False",
                description="Organizations in the Province of Quebec Exemption Order (SOR/2003-374) exempts intraprovincial activity from PIPEDA Part 1.",
            ),
            PreemptionRule(
                rule_id="CA-QC-LAW25-CONCURRENT-PIPEDA",
                preempts_or_yields="concurrent_with",
                target_regulation_id="CA-FED-PIPEDA",
                scope_condition="personal information crosses Quebec's border in commercial activity OR is_federally_regulated_canada == True",
                description="PIPEDA applies concurrently to interprovincial/international flows and to federal works, undertakings or businesses.",
            ),
        ],
        organization_types=["private", "nonprofit", "financial_institution", "processor"],
        industry_sectors=["all_commercial"],
        data_subject_categories=["consumers", "customers", "employees", "minors"],
        data_categories=["personal_information", "sensitive_personal_information", "biometric", "location", "health"],
        processing_activities=[
            "collection", "use", "communication", "cross_border_transfer", "profiling",
            "automated_decision_making", "tracking_technologies", "information_system_projects",
        ],
        required_actions=[
            "Person exercising the highest authority is the person in charge of the protection of personal information by default; may delegate in writing (s. 3.1)",
            "Publish the privacy officer's title and contact information on the enterprise website (s. 3.1)",
            "Adopt and publish governance policies and practices in clear, simple terms (s. 3.2)",
            "Conduct a PIA for any project to acquire, develop or overhaul an information system or electronic service delivery involving personal information (s. 3.3)",
            "Conduct a PIA (Law25_TIA) before communicating personal information outside Quebec, considering sensitivity, purpose, protection measures (incl. contractual) and the legal framework of the destination; communication only if adequate protection; written agreement required (s. 17)",
            "Notify the CAI and affected persons promptly of confidentiality incidents presenting a risk of serious injury (s. 3.5)",
            "Maintain a confidentiality incident register and provide it to the CAI on request (s. 3.8)",
            "Obtain consent of the parent/tutor for minors under 14 (s. 4.1)",
            "Obtain express consent for sensitive personal information (s. 12)",
            "Disable by default technology functions that identify, locate or profile; inform persons of their use (ss. 8.1, 9.1)",
            "Ensure highest level of confidentiality by default for technological products/services offered to the public (s. 9.1)",
            "Inform persons of decisions based exclusively on automated processing and of their right to have the decision reviewed (s. 12.1)",
            "Respond to access, rectification, portability and de-indexation requests within 30 days (ss. 27, 28, 28.1, 32)",
            "Provide computerized personal information in a structured, commonly used technological format on request (s. 27 para. 3)",
            "Destroy or anonymize personal information once purposes are achieved (s. 23)",
            "Make privacy notices and consent materials available in French (Charter of the French Language / Bill 96)",
        ],
        required_assessments=["Law25_PIA", "Law25_TIA", "Confidentiality_Incident_Risk_Of_Serious_Injury_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="calendar_days",
            rights_request_extension_days=None,
            identity_verification_required=True,
            breach_regulator_text=(
                "Promptly notify the CAI of any confidentiality incident presenting a risk of serious "
                "injury (s. 3.5; Regulation c. P-39.1, r. 3.1 s. 3)"
            ),
            breach_individual_text=(
                "Promptly notify each person whose information is concerned where there is a risk of "
                "serious injury; public notice permitted in prescribed cases (s. 3.5; r. 3.1 ss. 4-5)"
            ),
            record_retention_years=5,
        ),
        notification_requirements=[
            "CAI confidentiality incident notice (r. 3.1 s. 3 content)",
            "Individual notice of confidentiality incident (r. 3.1 s. 4 content)",
            "Notice to persons/bodies that could reduce the risk (s. 3.5 para. 3)",
            "Notice of automated decision and right to review (s. 12.1)",
            "Notice of use of identification/location/profiling technology (s. 8.1)",
            "Failure to respond within 30 days is deemed a refusal (s. 32)",
        ],
        required_evidence=[
            "Written delegation of privacy officer function (if delegated)",
            "Published governance policy",
            "PIA reports (information systems and s. 17 communications outside Quebec)",
            "Written agreements for communications outside Quebec",
            "Confidentiality incident register retained at least 5 years after the enterprise became aware of the incident (r. 3.1 s. 11)",
            "Consent records including parental consent for under-14s",
            "French-language versions of privacy notices",
        ],
        approval_requirements=[
            "Privacy officer consulted from the outset of any PIA project (s. 3.3)",
            "Privacy officer sign-off on s. 17 TIA before any communication outside Quebec",
        ],
        competent_regulator=cai,
        domain_category="privacy",
    ))

    regs.append(_reg(
        **qc,
        regulation_id="CA-QC-PUBLIC-ACCESS",
        legal_authority="Assemblée nationale du Québec",
        legal_instrument=(
            "Act respecting Access to documents held by public bodies and the Protection of personal "
            "information (CQLR c. A-2.1), as amended by Law 25"
        ),
        official_source_url="https://www.legisquebec.gouv.qc.ca/en/document/cs/A-2.1",
        article_or_section=(
            "s. 8 person in charge of access/protection; s. 47 20-day response (+10 days); s. 63.3 "
            "governance; s. 63.5 PIA for information systems; ss. 63.8-63.11 confidentiality incidents; "
            "s. 70.1 PIA before communication outside Quebec"
        ),
        original_language="fr",
        effective_date=date(1982, 6, 23),
        applicability_conditions={"establishments_any": ["CA-QC"], "organization_types_any": PUBLIC_SECTOR_ORG_TYPES},
        exemptions=[
            ExemptionRule(
                exemption_id="CA-QC-PA-EX-PRIVATE",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["private", "nonprofit"],
                carve_out_statute="CA-QC-LAW25",
                description="Private enterprises are governed by CQLR c. P-39.1.",
            ),
        ],
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["municipal", "school_service_centre"],
        industry_sectors=["provincial_government", "municipal", "education"],
        data_subject_categories=["citizens", "residents", "public_employees"],
        data_categories=["personal_information", "government_records"],
        processing_activities=["collection", "use", "communication", "cross_border_transfer", "access_request_handling"],
        required_actions=[
            "Respond to access requests within 20 days; extend by up to 10 days with notice (s. 47)",
            "Adopt governance rules approved by the access/privacy committee (s. 63.3)",
            "Conduct PIA for information system / electronic service delivery projects (s. 63.5)",
            "Notify CAI and individuals of confidentiality incidents presenting a risk of serious injury; keep a register (ss. 63.8-63.11)",
            "Conduct PIA before communicating personal information outside Quebec (s. 70.1)",
        ],
        required_assessments=["Law25_PIA", "Law25_TIA"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=20,
            rights_request_extension_days=10,
            breach_regulator_text="Promptly notify the CAI of confidentiality incidents presenting a risk of serious injury (s. 63.8)",
            breach_individual_text="Promptly notify affected persons (s. 63.8)",
            record_retention_years=5,
        ),
        notification_requirements=["CAI confidentiality incident notice", "Individual notice"],
        required_evidence=["PIA reports", "Incident register", "Access request log"],
        competent_regulator=cai,
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **qc,
        regulation_id="CA-QC-HEALTH",
        legal_authority="Assemblée nationale du Québec",
        legal_instrument=(
            "Act respecting health and social services information (CQLR c. R-22.1; enacted as Bill 3, "
            "S.Q. 2023, c. 5)"
        ),
        official_source_url="https://www.legisquebec.gouv.qc.ca/en/document/cs/R-22.1",
        article_or_section=(
            "Health and social services bodies; information officer; access and rectification; "
            "confidentiality incidents; communication outside Quebec; governance rules; technological "
            "product/service certification"
        ),
        original_language="fr",
        effective_date=date(2024, 7, 1),
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        applicability_conditions={
            "establishments_any": ["CA-QC"],
            "organization_types_any": HEALTH_ORG_TYPES + ["public", "private_health_provider"],
            "data_categories_any": HEALTH_DATA,
            "counsel_review_note": (
                "Access deadlines and incident-notification mechanics under R-22.1 and its regulations "
                "must be re-verified against the current LégisQuébec consolidation and ministerial "
                "regulations before production reliance."
            ),
        },
        organization_types=HEALTH_ORG_TYPES + ["public", "private_health_provider", "technology_vendor"],
        industry_sectors=["healthcare", "social_services"],
        data_subject_categories=["patients", "service_users"],
        data_categories=HEALTH_DATA,
        processing_activities=["collection", "use", "communication", "research", "cross_border_transfer", "information_system_projects"],
        required_actions=[
            "Designate the person in charge of information protection within the body",
            "Adopt governance rules for health and social services information",
            "Conduct PIA before acquiring/developing technological products or services and before communication outside Quebec",
            "Use only technological products or services meeting ministerial requirements",
            "Notify the CAI and affected persons of confidentiality incidents presenting a risk of serious injury; maintain an incident register",
            "Log and audit accesses to health information",
        ],
        required_assessments=["Law25_PIA", "Law25_TIA", "Confidentiality_Incident_Risk_Of_Serious_Injury_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=20,
            rights_request_extension_days=10,
            breach_regulator_text="Promptly notify the CAI of confidentiality incidents presenting a risk of serious injury",
            breach_individual_text="Promptly notify affected persons",
        ),
        notification_requirements=["CAI confidentiality incident notice", "Individual notice"],
        required_evidence=["Governance rules", "PIA reports", "Access logs", "Incident register"],
        competent_regulator=cai,
        subnational_regulators={"CA-QC-MSSS": "Ministère de la Santé et des Services sociaux (MSSS)"},
        domain_category="health_privacy",
    ))

    return regs


# ---------------------------------------------------------------------------
# 3. ONTARIO (CA-ON)
# ---------------------------------------------------------------------------

def _ontario() -> List[CanonicalRegulation]:
    on = _province("CA-ON", "Ontario")
    ipc = "Information and Privacy Commissioner of Ontario (IPC)"
    regs: List[CanonicalRegulation] = []

    regs.append(_reg(
        **on,
        regulation_id="CA-ON-PHIPA",
        legal_authority="Legislative Assembly of Ontario",
        legal_instrument="Personal Health Information Protection Act, 2004 (S.O. 2004, c. 3, Sched. A); O. Reg. 329/04",
        official_source_url="https://www.ontario.ca/laws/statute/04p03",
        article_or_section=(
            "s. 3 health information custodians; s. 10(4) & O. Reg. 329/04 s. 6 electronic service "
            "providers / health information network providers; s. 12 safeguards and breach notice; "
            "s. 17 agents; ss. 37(1)(a), 38(1)(a), 50(1)(e) consent directives (lockbox); s. 54 access "
            "(30 days + 30); s. 55 correction; O. Reg. 329/04 ss. 6.3-6.4 IPC breach reporting and "
            "annual statistics; ss. 61.1, 72 penalties"
        ),
        effective_date=date(2004, 11, 1),
        applicability_conditions={
            "establishments_any": ["CA-ON"],
            "organization_types_any": HEALTH_ORG_TYPES + ["agent", "electronic_service_provider", "health_information_network_provider"],
            "data_categories_any": HEALTH_DATA,
        },
        thresholds=[
            StatutoryThreshold(
                metric="organization_type",
                operator="in",
                value=["health_information_custodian", "agent", "electronic_service_provider", "health_information_network_provider"],
                description="Applies to HICs and to agents/electronic service providers acting for HICs (ss. 3, 10(4), 17).",
            ),
            StatutoryThreshold(
                metric="offence_fine_max_cad_organization",
                operator="<=",
                value=1000000,
                currency="CAD",
                description="Offence fines up to CAD 1,000,000 for organizations; CAD 200,000 for individuals (s. 72(2)).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="CA-ON-PHIPA-SUBSTANTIALLY-SIMILAR",
                preempts_or_yields="preempts",
                target_regulation_id="CA-FED-PIPEDA",
                scope_condition="organization_type == 'health_information_custodian' AND intraprovincial PHI handling in Ontario",
                description="Health Information Custodians in the Province of Ontario Exemption Order (SOR/2005-399).",
            ),
        ],
        organization_types=HEALTH_ORG_TYPES + ["agent", "electronic_service_provider", "health_information_network_provider"],
        industry_sectors=["healthcare", "digital_health", "health_technology"],
        data_subject_categories=["patients"],
        data_categories=HEALTH_DATA,
        processing_activities=["collection", "use", "disclosure", "electronic_health_records", "hosting", "research"],
        required_actions=[
            "Designate a contact person and publish a written public statement of information practices (ss. 15-16)",
            "Implement reasonable administrative, technical and physical safeguards (s. 12(1))",
            "Electronic service providers: use/disclose PHI only as necessary to provide services; no agent status unless retained as agent (s. 10(4); O. Reg. 329/04 s. 6(1))",
            "Health information network providers: written agreement with each HIC; perform and provide a Threat Risk Assessment (PHIPA_TRA) and PIA; audit logging; notify HIC of breaches at first reasonable opportunity (O. Reg. 329/04 s. 6(3))",
            "Agents act only within HIC authority under written or documented terms (s. 17)",
            "Honour consent directives (lockbox) and notify recipients when PHI is withheld (ss. 37(1)(a), 38(1)(a), 50(1)(e), 50(2))",
            "Respond to access requests within 30 days; extension up to 30 days with written notice (s. 54(2)-(4))",
            "Respond to correction requests within 30 days; extension up to 30 days (s. 55(3))",
            "Notify individuals at the first reasonable opportunity of theft, loss or unauthorized use/disclosure (s. 12(2))",
            "Notify the IPC of breaches meeting O. Reg. 329/04 s. 6.3 criteria at first reasonable opportunity (s. 12(3))",
            "Submit annual breach statistics report to the IPC by March 1 for the previous calendar year (O. Reg. 329/04 s. 6.4)",
        ],
        required_assessments=["PHIPA_TRA", "PHIPA_PIA", "Breach_Reportability_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_extension_days=30,
            breach_regulator_text=(
                "At the first reasonable opportunity, notify the IPC where O. Reg. 329/04 s. 6.3 criteria "
                "are met (e.g. theft, further use/disclosure, pattern, disciplinary reporting, significant breach)"
            ),
            breach_individual_text="At the first reasonable opportunity, with notice of the right to complain to the IPC (s. 12(2))",
        ),
        notification_requirements=[
            "Individual breach notice (s. 12(2))",
            "IPC breach report (s. 12(3); O. Reg. 329/04 s. 6.3)",
            "Annual breach statistics to IPC by March 1 (O. Reg. 329/04 s. 6.4)",
            "Notice to recipient that PHI is incomplete due to consent directive (s. 38(2), 50(2))",
            "Electronic service provider / HINP notifies HIC of breaches",
        ],
        required_evidence=[
            "Written HINP / electronic service provider agreements",
            "Threat Risk Assessment and PIA reports delivered to HICs",
            "Audit logs of PHI access",
            "Consent directive register",
            "Breach log and annual statistics submission",
            "Agent confidentiality agreements",
        ],
        approval_requirements=["HIC approval of agent/ESP arrangements", "Privacy officer review of IPC breach reports"],
        competent_regulator=ipc,
        domain_category="health_privacy",
    ))

    regs.append(_reg(
        **on,
        regulation_id="CA-ON-FIPPA",
        legal_authority="Legislative Assembly of Ontario",
        legal_instrument=(
            "Freedom of Information and Protection of Privacy Act (R.S.O. 1990, c. F.31), as amended by "
            "the Strengthening Cyber Security and Building Trust in the Public Sector Act, 2024 (Bill 194, "
            "S.O. 2024, c. 24), incl. Sched. 1 Enhancing Digital Security and Trust Act, 2024"
        ),
        official_source_url="https://www.ontario.ca/laws/statute/90f31",
        article_or_section=(
            "s. 26 30-day response; s. 27 extensions; Part III protection of privacy (ss. 38-49); "
            "Bill 194 amendments: privacy impact assessments, breach reporting to IPC and notice to "
            "individuals (real risk of significant harm); EDSTA: cyber security programs and AI "
            "accountability/disclosure for public-sector entities"
        ),
        effective_date=date(1988, 1, 1),
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        applicability_conditions={
            "establishments_any": ["CA-ON"],
            "organization_types_any": PUBLIC_SECTOR_ORG_TYPES + ["hospital", "university"],
            "bill_194_royal_assent": "2024-11-25",
            "counsel_review_note": (
                "Bill 194 FIPPA privacy amendments (PIA, breach notification) in force 2025-07-01 per "
                "proclamation; EDSTA AI/cyber obligations take effect via regulations — verify current "
                "regulations before production reliance."
            ),
        },
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["hospital", "university", "college"],
        industry_sectors=["provincial_government", "education", "healthcare_public"],
        data_subject_categories=["citizens", "residents", "students", "public_employees"],
        data_categories=["personal_information", "government_records"],
        processing_activities=["collection", "use", "disclosure", "ai_systems", "access_request_handling"],
        required_actions=[
            "Respond to access requests within 30 days; extend for a reasonable period with notice (ss. 26-27)",
            "Collect personal information only as authorized, necessary or for law enforcement (s. 38(2))",
            "Complete a written PIA before collecting personal information (Bill 194 amendments)",
            "Report thefts, losses or unauthorized use/disclosure posing a real risk of significant harm to the IPC and notify individuals (Bill 194 amendments)",
            "Maintain cyber security programs and comply with AI use accountability, disclosure and risk management requirements (EDSTA, Sched. 1)",
        ],
        required_assessments=["Ontario_Public_Sector_PIA", "AI_Accountability_Assessment", "RROSH_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_extension_days=None,
            breach_regulator_text="Report to the IPC breaches posing a real risk of significant harm as soon as feasible (Bill 194)",
            breach_individual_text="Notify affected individuals as soon as feasible (Bill 194)",
        ),
        notification_requirements=["IPC breach report", "Individual breach notice", "Annual breach statistics to IPC"],
        required_evidence=["PIA reports", "AI use disclosures", "Cyber security program documentation", "Access request log"],
        competent_regulator=ipc,
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **on,
        regulation_id="CA-ON-MFIPPA",
        legal_authority="Legislative Assembly of Ontario",
        legal_instrument="Municipal Freedom of Information and Protection of Privacy Act (R.S.O. 1990, c. M.56)",
        official_source_url="https://www.ontario.ca/laws/statute/90m56",
        article_or_section="s. 19 30-day response; s. 20 extensions; Part II protection of privacy (ss. 27-38)",
        effective_date=date(1991, 1, 1),
        applicability_conditions={
            "establishments_any": ["CA-ON"],
            "organization_types_any": ["public", "government_agency", "municipal", "school_board", "police_services_board"],
        },
        organization_types=["municipal", "school_board", "police_services_board", "public"],
        industry_sectors=["municipal", "education", "policing"],
        data_subject_categories=["residents", "students"],
        data_categories=["personal_information", "government_records"],
        processing_activities=["collection", "use", "disclosure", "access_request_handling"],
        required_actions=[
            "Respond to access requests within 30 days; extend for a reasonable period with notice (ss. 19-20)",
            "Collect personal information only as authorized or necessary (s. 28(2))",
            "Ensure reasonable measures to prevent unauthorized access (R.R.O. 1990, Reg. 823)",
        ],
        required_assessments=["PIA_Recommended"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            breach_regulator_text="No statutory obligation; IPC guidance recommends prompt voluntary reporting",
            breach_individual_text="IPC guidance recommends prompt notification",
        ),
        required_evidence=["Access request log", "Privacy breach protocol"],
        competent_regulator=ipc,
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **on,
        regulation_id="CA-ON-CYFSA",
        legal_authority="Legislative Assembly of Ontario",
        legal_instrument="Child, Youth and Family Services Act, 2017 (S.O. 2017, c. 14, Sched. 1), Part X; O. Reg. 191/18",
        official_source_url="https://www.ontario.ca/laws/statute/17c14",
        article_or_section="Part X (ss. 281-332): collection, use, disclosure, access and correction; breach notification and IPC oversight",
        effective_date=date(2020, 1, 1),
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        applicability_conditions={
            "establishments_any": ["CA-ON"],
            "organization_types_any": ["service_provider_child_welfare", "childrens_aid_society", "public", "nonprofit"],
            "involves_children": True,
            "counsel_review_note": "Verify Part X access-extension length and annual breach statistics deadline against current O. Reg. 191/18.",
        },
        organization_types=["childrens_aid_society", "licensed_service_provider", "nonprofit"],
        industry_sectors=["child_welfare", "youth_justice", "social_services"],
        data_subject_categories=["children", "youth", "families"],
        data_categories=["personal_information", "health", "child_welfare_records"],
        processing_activities=["collection", "use", "disclosure", "access_request_handling"],
        required_actions=[
            "Collect, use and disclose personal information only as permitted by Part X",
            "Respond to access requests within 30 days, subject to permitted extension",
            "Notify individuals at the first reasonable opportunity of theft, loss or unauthorized use/disclosure and report to the IPC",
            "Submit annual breach statistics to the IPC",
        ],
        required_assessments=["PIA_Recommended", "Breach_Reportability_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            breach_regulator_text="Report to the IPC at the first reasonable opportunity",
            breach_individual_text="At the first reasonable opportunity",
        ),
        notification_requirements=["IPC breach report", "Individual breach notice", "Annual breach statistics"],
        required_evidence=["Information practices statement", "Breach log", "Access request log"],
        competent_regulator=ipc,
        domain_category="children_privacy",
    ))

    regs.append(_reg(
        **on,
        regulation_id="CA-ON-ESA-WORKPLACE",
        legal_authority="Legislative Assembly of Ontario",
        legal_instrument=(
            "Employment Standards Act, 2000 (S.O. 2000, c. 41), Part XI.1 Written Policy on Electronic "
            "Monitoring (added by Working for Workers Act, 2022, S.O. 2022, c. 7)"
        ),
        official_source_url="https://www.ontario.ca/laws/statute/00e41",
        article_or_section="Part XI.1, ss. 41.1.1-41.1.2 written policy on electronic monitoring",
        effective_date=date(2022, 10, 11),
        applicability_conditions={
            "establishments_any": ["CA-ON"],
            "data_subject_categories_any": ["employees"],
            "employee_count_measured_on": "January 1 of each year (Ontario employees)",
        },
        thresholds=[
            StatutoryThreshold(
                metric="employee_count",
                operator=">=",
                value=25,
                logic_group="AND",
                description="Employers employing 25 or more employees in Ontario on January 1 must have a written electronic monitoring policy by March 1 of that year (s. 41.1.1(1)).",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CA-ON-ESA-EX-FWUB",
                exemption_type="entity_level",
                condition_field="is_federally_regulated_canada",
                condition_values=["True"],
                description="Federally regulated employers are governed by the Canada Labour Code, not the ESA.",
            ),
            ExemptionRule(
                exemption_id="CA-ON-ESA-EX-CROWN",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["crown"],
                description="The Crown, its agents and employees are excluded (s. 41.1.1(9)).",
            ),
        ],
        organization_types=["private", "nonprofit", "public"],
        industry_sectors=["all"],
        data_subject_categories=["employees"],
        data_categories=["employee_monitoring_data", "device_activity", "location"],
        processing_activities=["employee_monitoring"],
        required_actions=[
            "Maintain a written policy stating whether the employer electronically monitors employees, and if so how, in what circumstances and for what purposes (s. 41.1.1(2))",
            "Record the date the policy was prepared and the date of any changes",
            "Provide a copy to existing employees within 30 days of preparation or change; to new employees within 30 days of hire (s. 41.1.1(4)-(5))",
            "Retain a copy of each version for three years after it ceases to be in effect (s. 41.1.1(7))",
        ],
        required_assessments=["Employee_Monitoring_Policy_Review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            identity_verification_required=False,
            breach_regulator_text="Not applicable",
            breach_individual_text="Not applicable",
            record_retention_years=3,
        ),
        notification_requirements=["Policy copy to employees within 30 days of preparation, change or hire"],
        required_evidence=["Electronic monitoring policy (all versions)", "Proof of distribution to employees"],
        competent_regulator="Ontario Ministry of Labour, Immigration, Training and Skills Development (Employment Standards)",
        domain_category="privacy",
    ))

    return regs


# ---------------------------------------------------------------------------
# 4. ALBERTA (CA-AB) & BRITISH COLUMBIA (CA-BC)
# ---------------------------------------------------------------------------

def _alberta() -> List[CanonicalRegulation]:
    ab = _province("CA-AB", "Alberta")
    oipc = "Office of the Information and Privacy Commissioner of Alberta (OIPC-AB)"
    regs: List[CanonicalRegulation] = []

    regs.append(_reg(
        **ab,
        regulation_id="CA-AB-PIPA",
        legal_authority="Legislature of Alberta",
        legal_instrument="Personal Information Protection Act (S.A. 2003, c. P-6.5); Personal Information Protection Act Regulation (Alta. Reg. 366/2003)",
        official_source_url="https://www.canlii.org/en/ab/laws/stat/sa-2003-c-p-6.5/latest/",
        article_or_section=(
            "s. 6 policies and practices; s. 13.1 notice for service providers outside Canada; s. 28 "
            "45-day response; s. 31 extension; s. 34 safeguards; s. 34.1 breach notification to "
            "Commissioner; s. 37.1 Commissioner may require notice to individuals; Reg. ss. 19-19.1"
        ),
        effective_date=date(2004, 1, 1),
        applicability_conditions={
            "establishments_any": ["CA-AB"],
            "organization_types_any": ["private", "nonprofit_commercial_activity"],
            "employee_information_covered": True,
            "breach_provisions_in_force": "2010-05-01",
        },
        exemptions=[
            ExemptionRule(
                exemption_id="CA-AB-PIPA-EX-PUBLIC",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["public", "government_agency"],
                carve_out_statute="CA-AB-FOIP",
                description="Public bodies are governed by Alberta's ATIA / POPA.",
            ),
            ExemptionRule(
                exemption_id="CA-AB-PIPA-EX-HIA",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["health_information_under_hia"],
                carve_out_statute="CA-AB-HIA",
                description="Health information governed by the Health Information Act is excluded (s. 4(3)(f)).",
            ),
            ExemptionRule(
                exemption_id="CA-AB-PIPA-EX-NONPROFIT",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["nonprofit"],
                description="Non-profit organizations are covered only for information collected in connection with commercial activity (s. 56).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="CA-AB-PIPA-SUBSTANTIALLY-SIMILAR",
                preempts_or_yields="preempts",
                target_regulation_id="CA-FED-PIPEDA",
                scope_condition="intraprovincial activity in Alberta AND is_federally_regulated_canada == False",
                description="Organizations in the Province of Alberta Exemption Order (SOR/2004-219).",
            ),
        ],
        organization_types=["private", "nonprofit"],
        industry_sectors=["all_commercial"],
        data_subject_categories=["consumers", "customers", "employees"],
        data_categories=["personal_information", "personal_employee_information"],
        processing_activities=["collection", "use", "disclosure", "cross_border_transfer", "outsourcing"],
        required_actions=[
            "Develop and follow reasonable policies and practices; make information about them available (s. 6)",
            "Where using a service provider outside Canada, include in policies the countries involved and purposes, and notify individuals at collection of how to obtain that information (ss. 6(2), 13.1)",
            "Respond to access requests within 45 days (s. 28(1))",
            "Extend by up to 30 days (or longer with Commissioner permission) with notice (s. 31)",
            "Make reasonable security arrangements (s. 34)",
            "Notify the Commissioner without unreasonable delay of loss/unauthorized access or disclosure where a reasonable person would consider a real risk of significant harm exists (s. 34.1)",
            "Notify individuals directly as required by the Commissioner (s. 37.1; Reg. s. 19.1)",
        ],
        required_assessments=["RROSH_Assessment", "Service_Provider_Outside_Canada_Notice_Review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            rights_request_extension_days=30,
            breach_regulator_text="Without unreasonable delay where a real risk of significant harm exists (s. 34.1; Reg. s. 19)",
            breach_individual_text="Directly, as required by the Commissioner (s. 37.1; Reg. s. 19.1)",
        ),
        notification_requirements=["OIPC-AB breach notice (Reg. s. 19 content)", "Individual notice when required (Reg. s. 19.1)", "s. 13.1 notice of service providers outside Canada"],
        required_evidence=["Privacy policies listing foreign service provider countries", "Breach RROSH assessments", "Access request log"],
        competent_regulator=oipc,
        domain_category="privacy",
    ))

    regs.append(_reg(
        **ab,
        regulation_id="CA-AB-HIA",
        legal_authority="Legislature of Alberta",
        legal_instrument="Health Information Act (R.S.A. 2000, c. H-5)",
        official_source_url="https://www.canlii.org/en/ab/laws/stat/rsa-2000-c-h-5/latest/",
        article_or_section="s. 12 30-day response; s. 15 extension; s. 60 safeguards; s. 60.1 duty to notify; s. 64 PIA submitted to Commissioner; s. 66 information manager agreements",
        effective_date=date(2001, 4, 25),
        applicability_conditions={
            "establishments_any": ["CA-AB"],
            "organization_types_any": HEALTH_ORG_TYPES + ["information_manager"],
            "data_categories_any": HEALTH_DATA,
            "breach_provisions_in_force": "2018-08-31",
        },
        organization_types=HEALTH_ORG_TYPES + ["information_manager"],
        industry_sectors=["healthcare", "pharmacy", "digital_health"],
        data_subject_categories=["patients"],
        data_categories=HEALTH_DATA,
        processing_activities=["collection", "use", "disclosure", "electronic_health_records", "outsourcing"],
        required_actions=[
            "Respond to access requests within 30 days; extend up to 30 days (ss. 12, 15)",
            "Prepare a PIA and submit it to the Commissioner before implementing new administrative practices or information systems (s. 64)",
            "Enter into written agreements with information managers (s. 66)",
            "Notify the Commissioner, the Minister and affected individuals as soon as practicable of unauthorized access/disclosure where there is a risk of harm (s. 60.1)",
        ],
        required_assessments=["Alberta_HIA_PIA", "Risk_Of_Harm_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_extension_days=30,
            breach_regulator_text="As soon as practicable to the Commissioner and the Minister of Health where risk of harm (s. 60.1)",
            breach_individual_text="As soon as practicable (s. 60.1)",
        ),
        notification_requirements=["OIPC-AB and Minister breach notice", "Individual notice", "PIA submission to OIPC-AB"],
        required_evidence=["PIA acceptance letter from OIPC-AB", "Information manager agreements", "Breach risk-of-harm assessments"],
        approval_requirements=["PIA reviewed/accepted by OIPC-AB before go-live"],
        competent_regulator=oipc,
        domain_category="health_privacy",
    ))

    regs.append(_reg(
        **ab,
        regulation_id="CA-AB-FOIP",
        legal_authority="Legislature of Alberta",
        legal_instrument=(
            "Access to Information Act (S.A. 2024, c. A-1.4) and Protection of Privacy Act (S.A. 2024, "
            "c. P-28.5) — replacing the Freedom of Information and Protection of Privacy Act (R.S.A. 2000, c. F-25)"
        ),
        official_source_url="https://www.canlii.org/en/ab/laws/stat/sa-2024-c-p-28.5/latest/",
        article_or_section=(
            "ATIA: access requests and response deadlines; POPA: collection/use/disclosure, mandatory "
            "privacy breach notification (real risk of significant harm), privacy management programs, "
            "PIAs, prohibition on sale of personal information, data matching and non-personal data rules"
        ),
        effective_date=date(2025, 6, 11),
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        applicability_conditions={
            "establishments_any": ["CA-AB"],
            "organization_types_any": PUBLIC_SECTOR_ORG_TYPES + ["municipal", "school_board"],
            "predecessor": "FOIP Act (R.S.A. 2000, c. F-25), repealed on ATIA/POPA proclamation",
            "counsel_review_note": "Verify ATIA business-day response deadline and POPA breach-notification timing against current regulations.",
        },
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["municipal", "school_board"],
        industry_sectors=["provincial_government", "municipal", "education"],
        data_subject_categories=["citizens", "residents", "students"],
        data_categories=["personal_information", "non_personal_data", "government_records"],
        processing_activities=["collection", "use", "disclosure", "data_matching", "access_request_handling"],
        required_actions=[
            "Respond to access requests within 30 business days (ATIA)",
            "Notify the Commissioner, Minister and affected individuals of privacy breaches posing a real risk of significant harm (POPA)",
            "Establish a privacy management program and conduct PIAs where required (POPA)",
            "Do not sell personal information (POPA)",
        ],
        required_assessments=["Alberta_Public_Sector_PIA", "RROSH_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="business_days",
            rights_request_extension_days=30,
            breach_regulator_text="Without unreasonable delay where a real risk of significant harm exists (POPA)",
            breach_individual_text="Without unreasonable delay (POPA)",
        ),
        notification_requirements=["OIPC-AB and Minister breach notice", "Individual notice"],
        required_evidence=["Privacy management program", "PIA reports", "Breach log"],
        competent_regulator=oipc,
        domain_category="public_sector",
    ))

    return regs


def _british_columbia() -> List[CanonicalRegulation]:
    bc = _province("CA-BC", "British Columbia")
    oipc = "Office of the Information and Privacy Commissioner for British Columbia (OIPC-BC)"
    regs: List[CanonicalRegulation] = []

    regs.append(_reg(
        **bc,
        regulation_id="CA-BC-PIPA",
        legal_authority="Legislative Assembly of British Columbia",
        legal_instrument="Personal Information Protection Act (S.B.C. 2003, c. 63)",
        official_source_url="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/03063_01",
        article_or_section="s. 1 'day' excludes holidays and Saturdays; s. 4 privacy officer; s. 5 policies; s. 29 30-day response; s. 31 extension; s. 34 safeguards",
        effective_date=date(2004, 1, 1),
        applicability_conditions={
            "establishments_any": ["CA-BC"],
            "organization_types_any": ["private", "nonprofit"],
            "employee_information_covered": True,
            "mandatory_breach_notification": False,
            "note": "BC PIPA contains no mandatory breach notification; OIPC-BC recommends voluntary reporting.",
        },
        exemptions=[
            ExemptionRule(
                exemption_id="CA-BC-PIPA-EX-PUBLIC",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["public", "government_agency"],
                carve_out_statute="CA-BC-FOIPPA",
                description="Personal information to which FOIPPA applies is excluded (s. 3(2)).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="CA-BC-PIPA-SUBSTANTIALLY-SIMILAR",
                preempts_or_yields="preempts",
                target_regulation_id="CA-FED-PIPEDA",
                scope_condition="intraprovincial activity in British Columbia AND is_federally_regulated_canada == False",
                description="Organizations in the Province of British Columbia Exemption Order (SOR/2004-220).",
            ),
        ],
        organization_types=["private", "nonprofit"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "customers", "employees"],
        data_categories=["personal_information", "employee_personal_information"],
        processing_activities=["collection", "use", "disclosure"],
        required_actions=[
            "Designate one or more individuals responsible for compliance (s. 4(3))",
            "Develop and follow policies and a complaints process (s. 5)",
            "Respond to access requests within 30 days, where 'day' excludes Saturdays and holidays (ss. 1, 29)",
            "Extend by up to 30 days (or longer with Commissioner permission) with notice (s. 31)",
            "Make reasonable security arrangements (s. 34)",
        ],
        required_assessments=["PIA_Recommended", "Voluntary_Breach_Risk_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="business_days",
            rights_request_extension_days=30,
            breach_regulator_text="No statutory obligation; voluntary reporting to OIPC-BC recommended",
            breach_individual_text="No statutory obligation; notification recommended where risk of harm",
        ),
        required_evidence=["Privacy policy and complaints process", "Access request log"],
        competent_regulator=oipc,
        domain_category="privacy",
    ))

    regs.append(_reg(
        **bc,
        regulation_id="CA-BC-FOIPPA",
        legal_authority="Legislative Assembly of British Columbia",
        legal_instrument="Freedom of Information and Protection of Privacy Act (R.S.B.C. 1996, c. 165), as amended by S.B.C. 2021, c. 39 (Bill 22)",
        official_source_url="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96165_00",
        article_or_section=(
            "s. 7 30-day response (business days per Schedule 1 'day'); s. 10 extension; s. 30 "
            "security; s. 30.5 foreign demand notice; s. 33.1 disclosure outside Canada (per "
            "regulation/assessment); s. 36.2 privacy management program; s. 36.3 privacy breach "
            "notification; s. 69(5) PIA"
        ),
        effective_date=date(1993, 10, 4),
        applicability_conditions={
            "establishments_any": ["CA-BC"],
            "organization_types_any": PUBLIC_SECTOR_ORG_TYPES + ["health_authority", "municipal", "service_provider_to_public_body"],
            "data_residency_note": (
                "The former mandatory data-residency requirement (s. 30.1) was repealed in 2021; disclosure "
                "outside Canada is permitted subject to regulations, including a supplementary assessment "
                "for sensitive personal information."
            ),
            "breach_and_pmp_in_force": "2023-02-01",
        },
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["health_authority", "municipal", "service_provider_to_public_body"],
        industry_sectors=["provincial_government", "healthcare_public", "education", "municipal"],
        data_subject_categories=["citizens", "residents", "patients", "students"],
        data_categories=["personal_information", "sensitive_personal_information"],
        processing_activities=["collection", "use", "disclosure", "cross_border_transfer", "outsourcing", "access_request_handling"],
        required_actions=[
            "Respond to access requests within 30 days (business days); extend up to 30 days or longer with Commissioner permission (ss. 7, 10)",
            "Conduct a PIA for new or significantly modified enactments, systems, projects, programs or activities (s. 69(5))",
            "Conduct a supplementary assessment before storing or disclosing sensitive personal information outside Canada (s. 33.1 / regulations)",
            "Service providers and employees must report foreign demands for disclosure to the head of the public body (s. 30.5)",
            "Develop a privacy management program (s. 36.2)",
            "Notify affected individuals and the Commissioner without unreasonable delay of breaches reasonably expected to result in significant harm (s. 36.3)",
        ],
        required_assessments=["BC_FOIPPA_PIA", "Supplementary_Assessment_Sensitive_PI_Outside_Canada", "Significant_Harm_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="business_days",
            rights_request_extension_days=30,
            breach_regulator_text="Without unreasonable delay where the breach could reasonably be expected to result in significant harm (s. 36.3)",
            breach_individual_text="Without unreasonable delay (s. 36.3)",
        ),
        notification_requirements=["OIPC-BC breach notice", "Individual breach notice", "Foreign demand for disclosure report (s. 30.5)"],
        required_evidence=["PIA reports", "Supplementary assessments", "Privacy management program", "Breach log"],
        competent_regulator=oipc,
        domain_category="public_sector",
    ))

    regs.append(_reg(
        **bc,
        regulation_id="CA-BC-EHEALTH",
        legal_authority="Legislative Assembly of British Columbia",
        legal_instrument="E-Health (Personal Health Information Access and Protection of Privacy) Act (S.B.C. 2008, c. 38)",
        official_source_url="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/08038_01",
        article_or_section="Health information banks designated by ministerial order; disclosure directives; data stewardship committee; collection/use/disclosure limits",
        effective_date=date(2008, 5, 29),
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        applicability_conditions={
            "establishments_any": ["CA-BC"],
            "organization_types_any": ["health_authority", "government_agency", "health_information_bank_operator"],
            "data_categories_any": HEALTH_DATA,
            "counsel_review_note": "Verify in-force date and current designated health information banks.",
        },
        organization_types=["health_authority", "government_agency", "health_information_bank_operator"],
        industry_sectors=["healthcare", "digital_health"],
        data_subject_categories=["patients"],
        data_categories=HEALTH_DATA,
        processing_activities=["electronic_health_records", "health_information_bank_operations", "research"],
        required_actions=[
            "Collect, use and disclose personal health information in designated health information banks only for permitted purposes",
            "Honour disclosure directives made by individuals",
            "Obtain Data Stewardship Committee approval for secondary-use (e.g. research) disclosures",
        ],
        required_assessments=["BC_FOIPPA_PIA"],
        response_deadlines=ResponseDeadlineSpec(
            breach_regulator_text="Governed by FOIPPA s. 36.3 for public bodies",
            breach_individual_text="Governed by FOIPPA s. 36.3",
        ),
        required_evidence=["Ministerial designation orders", "Disclosure directive register", "Data Stewardship Committee approvals"],
        competent_regulator=oipc,
        subnational_regulators={"CA-BC-MOH": "BC Ministry of Health"},
        domain_category="health_privacy",
    ))

    return regs


# ---------------------------------------------------------------------------
# 5. OTHER PROVINCES (MB, NB, NL, NS, PE, SK)
# ---------------------------------------------------------------------------

def _public_sector_act(
    code: str, name: str, regulation_id: str, instrument: str, url: str, section: str,
    effective: date, regulator: str, initial: int, extension: int | None = None,
    day_type: str = "calendar_days", breach_regulator: str = "No statutory obligation; voluntary reporting recommended",
    breach_individual: str = "No statutory obligation; notification recommended where risk of harm",
    extra_actions: List[str] | None = None, extra_assessments: List[str] | None = None,
    territory: bool = False, review: LegalReviewStatus = LegalReviewStatus.VERIFIED,
    extra_conditions: Dict[str, Any] | None = None,
) -> CanonicalRegulation:
    conditions: Dict[str, Any] = {"establishments_any": [code], "organization_types_any": PUBLIC_SECTOR_ORG_TYPES}
    conditions.update(extra_conditions or {})
    ext_text = f"; extend up to {extension} {day_type.replace('_', ' ')}" if extension else ""
    return _reg(
        **_province(code, name, territory),
        regulation_id=regulation_id,
        legal_authority=f"Legislature of {name}",
        legal_instrument=instrument,
        official_source_url=url,
        article_or_section=section,
        effective_date=effective,
        legal_review_status=review,
        applicability_conditions=conditions,
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["municipal", "health_authority"],
        industry_sectors=["provincial_government" if not territory else "territorial_government", "education", "healthcare_public"],
        data_subject_categories=["citizens", "residents", "public_employees"],
        data_categories=["personal_information", "government_records"],
        processing_activities=["collection", "use", "disclosure", "access_request_handling"],
        required_actions=[
            f"Respond to access requests within {initial} {day_type.replace('_', ' ')}{ext_text}",
            "Collect, use and disclose personal information only as authorized by the Act",
            "Make reasonable security arrangements against unauthorized access, use or disclosure",
        ] + (extra_actions or []),
        required_assessments=(extra_assessments or ["PIA_Recommended"]),
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=initial,
            rights_request_day_type=day_type,
            rights_request_extension_days=extension,
            breach_regulator_text=breach_regulator,
            breach_individual_text=breach_individual,
        ),
        notification_requirements=["Extension notice to applicant"] + (["Commissioner breach notice", "Individual breach notice"] if "No statutory" not in breach_regulator else []),
        required_evidence=["Access request log", "Privacy breach protocol"],
        competent_regulator=regulator,
        domain_category="public_sector",
    )


def _health_act(
    code: str, name: str, regulation_id: str, instrument: str, url: str, section: str,
    effective: date, regulator: str, initial: int, extension: int | None,
    breach_regulator: str, breach_individual: str,
    extra_actions: List[str] | None = None, territory: bool = False,
    pipeda_order: str | None = None, review: LegalReviewStatus = LegalReviewStatus.VERIFIED,
    extra_conditions: Dict[str, Any] | None = None, deadlines: ResponseDeadlineSpec | None = None,
) -> CanonicalRegulation:
    conditions: Dict[str, Any] = {
        "establishments_any": [code],
        "organization_types_any": HEALTH_ORG_TYPES + ["trustee", "agent", "information_manager"],
        "data_categories_any": HEALTH_DATA,
    }
    conditions.update(extra_conditions or {})
    preemption = []
    if pipeda_order:
        preemption.append(PreemptionRule(
            rule_id=f"{regulation_id}-SUBSTANTIALLY-SIMILAR",
            preempts_or_yields="preempts",
            target_regulation_id="CA-FED-PIPEDA",
            scope_condition=f"organization_type == 'health_information_custodian' AND intraprovincial PHI handling in {name}",
            description=f"Health information custodians exempt from PIPEDA Part 1 for intraprovincial PHI ({pipeda_order}).",
        ))
    return _reg(
        **_province(code, name, territory),
        regulation_id=regulation_id,
        legal_authority=f"Legislature of {name}",
        legal_instrument=instrument,
        official_source_url=url,
        article_or_section=section,
        effective_date=effective,
        legal_review_status=review,
        applicability_conditions=conditions,
        preemption_rules=preemption,
        organization_types=HEALTH_ORG_TYPES + ["trustee", "agent", "information_manager"],
        industry_sectors=["healthcare", "pharmacy", "digital_health"],
        data_subject_categories=["patients"],
        data_categories=HEALTH_DATA,
        processing_activities=["collection", "use", "disclosure", "electronic_health_records", "research"],
        required_actions=[
            f"Respond to access requests within {initial} days" + (f"; extend up to {extension} days with notice" if extension else ""),
            "Collect, use and disclose personal health information only with consent or as authorized, limited to the minimum necessary",
            "Implement administrative, technical and physical safeguards",
            "Enter into written agreements with information managers / agents handling PHI",
        ] + (extra_actions or []),
        required_assessments=["Health_PIA", "Breach_Risk_Of_Harm_Assessment"],
        response_deadlines=deadlines or ResponseDeadlineSpec(
            rights_request_initial_days=initial,
            rights_request_extension_days=extension,
            breach_regulator_text=breach_regulator,
            breach_individual_text=breach_individual,
        ),
        notification_requirements=["Individual breach notice", "Commissioner breach notice (where required)"],
        required_evidence=["Information manager agreements", "Breach log", "Access request log", "PIA reports"],
        competent_regulator=regulator,
        domain_category="health_privacy",
    )


def _other_provinces() -> List[CanonicalRegulation]:
    regs: List[CanonicalRegulation] = []

    # --- Manitoba ---------------------------------------------------------
    mb_reg = "Manitoba Ombudsman (with Information and Privacy Adjudicator)"
    regs.append(_public_sector_act(
        "CA-MB", "Manitoba", "CA-MB-FIPPA",
        "Freedom of Information and Protection of Privacy Act (C.C.S.M. c. F175)",
        "https://web2.gov.mb.ca/laws/statutes/ccsm/f175e.php",
        "s. 11 30-day response; s. 15 extension; Part 3 protection of privacy (ss. 36-48)",
        date(1998, 5, 4), mb_reg, 30, 30,
    ))
    regs.append(_health_act(
        "CA-MB", "Manitoba", "CA-MB-PHIA",
        "The Personal Health Information Act (C.C.S.M. c. P33.5)",
        "https://web2.gov.mb.ca/laws/statutes/ccsm/p033-5e.php",
        "s. 6 response deadlines (30 days; 24h/72h for health care currently being provided by hospitals); s. 18 security; s. 19.0.1 notice of breach",
        date(1997, 12, 11), mb_reg, 30, None,
        breach_regulator="No statutory duty to notify the Ombudsman; Ombudsman guidance recommends reporting",
        breach_individual="As soon as reasonably practicable after theft, loss or unauthorized access/use/disclosure (s. 19.0.1)",
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_actions=[
            "Hospital trustees: respond within 24 hours where the individual is an in-patient and the request concerns care currently being provided, and within 72 hours for current care to a non-in-patient (s. 6(2))",
        ],
        extra_conditions={
            "accelerated_deadlines_hours": {"hospital_inpatient_current_care": 24, "hospital_current_care_non_inpatient": 72},
            "counsel_review_note": (
                "Confirm s. 6(2) accelerated-deadline mapping (24h in-patient vs 72h current care) against "
                "the current C.C.S.M. consolidation."
            ),
        },
    ))

    # --- New Brunswick ----------------------------------------------------
    nb_reg = "Office of the Ombud for New Brunswick (Access to Information and Privacy)"
    regs.append(_public_sector_act(
        "CA-NB", "New Brunswick", "CA-NB-RTIPPA",
        "Right to Information and Protection of Privacy Act (S.N.B. 2009, c. R-10.6)",
        "https://laws.gnb.ca/en/document/cs/R-10.6",
        "s. 11 30 business-day response; s. 11(3) extension; Part 3 protection of privacy; s. 49.1 breach notification",
        date(2010, 9, 1), nb_reg, 30, 30, day_type="business_days",
        breach_regulator="Notify the Commissioner/Ombud where it is reasonable to believe the breach creates a risk of significant harm (s. 49.1)",
        breach_individual="Notify affected individuals where risk of significant harm (s. 49.1)",
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={"counsel_review_note": "Verify breach notification section numbering and oversight body after 2019 ombud consolidation."},
    ))
    regs.append(_health_act(
        "CA-NB", "New Brunswick", "CA-NB-PHIPAA",
        "Personal Health Information Privacy and Access Act (S.N.B. 2009, c. P-7.05)",
        "https://laws.gnb.ca/en/document/cs/P-7.05",
        "s. 11 30-day response (+30); s. 49 notice of theft, loss or unauthorized use/disclosure; s. 50 information managers",
        date(2010, 9, 1), nb_reg, 30, 30,
        breach_regulator="At the first reasonable opportunity, notify the Commissioner/Ombud of theft, loss or unauthorized access, use or disclosure (s. 49(1)(c))",
        breach_individual="At the first reasonable opportunity (s. 49(1)(c))",
        pipeda_order="SOR/2011-265",
    ))

    # --- Newfoundland and Labrador ----------------------------------------
    nl_reg = "Office of the Information and Privacy Commissioner of Newfoundland and Labrador"
    regs.append(_public_sector_act(
        "CA-NL", "Newfoundland and Labrador", "CA-NL-ATIPPA",
        "Access to Information and Protection of Privacy Act, 2015 (S.N.L. 2015, c. A-1.2)",
        "https://www.assembly.nl.ca/legislation/sr/statutes/a01-2.htm",
        "s. 16 20 business-day response; s. 23 extension with Commissioner approval; s. 64 privacy breach notification; s. 72 PIA for common/integrated programs",
        date(2015, 6, 1), nl_reg, 20, None, day_type="business_days",
        breach_regulator="Notify the Commissioner of every privacy breach involving unauthorized collection, use or disclosure (s. 64(4))",
        breach_individual="Notify affected individuals unless there is no reasonable risk of significant harm (s. 64(3))",
        extra_actions=["Obtain Commissioner approval for any time extension (s. 23)", "Conduct PIA for common or integrated programs/services (s. 72)"],
        extra_assessments=["NL_ATIPPA_PIA"],
    ))
    regs.append(_health_act(
        "CA-NL", "Newfoundland and Labrador", "CA-NL-PHIA",
        "Personal Health Information Act (S.N.L. 2008, c. P-7.01)",
        "https://www.assembly.nl.ca/legislation/sr/statutes/p07-01.htm",
        "s. 15 breach notification; s. 55 60-day response; s. 56 extension",
        date(2011, 4, 1), nl_reg, 60, 30,
        breach_regulator="Notify the Commissioner of material breaches (s. 15(4); Reg. factors)",
        breach_individual="At the first reasonable opportunity unless no adverse impact reasonably expected (s. 15(3))",
        pipeda_order="SOR/2012-72",
    ))

    # --- Nova Scotia ------------------------------------------------------
    ns_reg = "Information and Privacy Commissioner for Nova Scotia"
    regs.append(_public_sector_act(
        "CA-NS", "Nova Scotia", "CA-NS-FOIPOP",
        "Freedom of Information and Protection of Privacy Act (S.N.S. 1993, c. 5)",
        "https://www.canlii.org/en/ns/laws/stat/sns-1993-c-5/latest/",
        "s. 7 30-day response; s. 9 extension; ss. 24-31 protection of privacy",
        date(1994, 7, 1), ns_reg, 30, 30,
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={"counsel_review_note": "Monitor Nova Scotia access/privacy modernization legislation that may replace FOIPOP."},
    ))
    regs.append(_reg(
        **_province("CA-NS", "Nova Scotia"),
        regulation_id="CA-NS-PIIDPA",
        legal_authority="Legislature of Nova Scotia",
        legal_instrument="Personal Information International Disclosure Protection Act (S.N.S. 2006, c. 3)",
        official_source_url="https://www.canlii.org/en/ns/laws/stat/sns-2006-c-3/latest/",
        article_or_section="s. 5 storage and access only in Canada; s. 5(2) head's exception for necessary operations; s. 6 foreign demand reporting; s. 8 annual report; s. 11 offences",
        effective_date=date(2006, 11, 15),
        applicability_conditions={
            "establishments_any": ["CA-NS"],
            "organization_types_any": PUBLIC_SECTOR_ORG_TYPES + ["municipal", "service_provider_to_public_body"],
            "involves_cross_border_transfer": True,
        },
        thresholds=[
            StatutoryThreshold(
                metric="offence_fine_max_cad_corporation",
                operator="<=",
                value=500000,
                currency="CAD",
                description="Fines up to CAD 500,000 for corporations; CAD 2,000 and possible imprisonment for individuals (s. 11).",
            ),
        ],
        organization_types=PUBLIC_SECTOR_ORG_TYPES + ["municipal", "service_provider_to_public_body"],
        industry_sectors=["provincial_government", "municipal", "healthcare_public", "education", "government_contracting"],
        data_subject_categories=["citizens", "residents"],
        data_categories=["personal_information"],
        processing_activities=["cloud_hosting", "outsourcing", "cross_border_transfer", "remote_access"],
        required_actions=[
            "Store personal information in public-body custody only in Canada and permit access only from Canada (s. 5(1))",
            "Obtain the head's documented decision that storage/access outside Canada meets the necessary requirements of operation, with conditions (s. 5(2))",
            "Service providers must report foreign demands for disclosure to the minister (s. 6)",
            "Report decisions allowing storage/access outside Canada in the annual report to the minister (s. 5(3))",
        ],
        required_assessments=["Data_Residency_Assessment", "Cross_Border_Transfer_Assessment"],
        response_deadlines=ResponseDeadlineSpec(
            breach_regulator_text="Report foreign demands for disclosure to the Minister of Justice without delay (s. 6)",
            breach_individual_text="Not specified",
            identity_verification_required=False,
        ),
        notification_requirements=["Foreign demand for disclosure report to Minister (s. 6)", "Annual report of s. 5(2) decisions"],
        required_evidence=["Data location attestations from service providers", "Head's s. 5(2) decision records"],
        approval_requirements=["Head of public body approval for any storage/access outside Canada"],
        competent_regulator="Nova Scotia Department of Justice (Information Access and Privacy Services); Information and Privacy Commissioner for Nova Scotia",
        domain_category="public_sector",
    ))
    regs.append(_health_act(
        "CA-NS", "Nova Scotia", "CA-NS-PHIA",
        "Personal Health Information Act (S.N.S. 2010, c. 41)",
        "https://www.canlii.org/en/ns/laws/stat/sns-2010-c-41/latest/",
        "s. 69 notification of breach to individual; s. 70 notice to Review Officer where no notification; s. 84 30-day response; s. 85 extension",
        date(2013, 6, 1), ns_reg, 30, 30,
        breach_regulator="Where the custodian decides not to notify individuals (no potential for harm or embarrassment), notify the Review Officer/Commissioner as soon as possible (s. 70)",
        breach_individual="At the first reasonable opportunity where there is potential for harm or embarrassment (s. 69)",
        pipeda_order="SOR/2016-62",
    ))

    # --- Prince Edward Island --------------------------------------------
    pe_reg = "Information and Privacy Commissioner of Prince Edward Island"
    regs.append(_public_sector_act(
        "CA-PE", "Prince Edward Island", "CA-PE-FOIPP",
        "Freedom of Information and Protection of Privacy Act (R.S.P.E.I. 1988, c. F-15.01)",
        "https://www.princeedwardisland.ca/sites/default/files/legislation/f-15-01-freedom_of_information_and_protection_of_privacy_act.pdf",
        "s. 9 30-day response; s. 12 extension; Part II protection of privacy",
        date(2002, 11, 1), pe_reg, 30, 30,
    ))
    regs.append(_health_act(
        "CA-PE", "Prince Edward Island", "CA-PE-HIA",
        "Health Information Act (R.S.P.E.I. 1988, c. H-1.41)",
        "https://www.princeedwardisland.ca/sites/default/files/legislation/h-01-41-health_information_act.pdf",
        "access 30 days (+30); breach notification to individual and Commissioner",
        date(2017, 7, 1), pe_reg, 30, 30,
        breach_regulator="At the first reasonable opportunity, notify the Commissioner of unauthorized access, use, disclosure or loss",
        breach_individual="At the first reasonable opportunity",
    ))

    # --- Saskatchewan -----------------------------------------------------
    sk_reg = "Office of the Saskatchewan Information and Privacy Commissioner"
    regs.append(_public_sector_act(
        "CA-SK", "Saskatchewan", "CA-SK-FOIP",
        "The Freedom of Information and Protection of Privacy Act (S.S. 1990-91, c. F-22.01); companion The Local Authority Freedom of Information and Protection of Privacy Act (S.S. 1990-91, c. L-27.1)",
        "https://www.canlii.org/en/sk/laws/stat/ss-1990-91-c-f-22.01/latest/",
        "s. 7 30-day response; s. 12 extension; s. 29.1 duty to notify of unauthorized collection/use/disclosure",
        date(1992, 4, 1), sk_reg, 30, 30,
        breach_regulator="No statutory duty to notify the Commissioner; IPC guidance recommends reporting",
        breach_individual="Notify the individual if it is reasonable to believe the incident creates a real risk of significant harm (s. 29.1)",
        extra_actions=["Notify individuals of unauthorized collection, use or disclosure creating a real risk of significant harm (s. 29.1)"],
    ))
    regs.append(_health_act(
        "CA-SK", "Saskatchewan", "CA-SK-HIPA",
        "The Health Information Protection Act (S.S. 1999, c. H-0.021)",
        "https://www.canlii.org/en/sk/laws/stat/ss-1999-c-h-0.021/latest/",
        "s. 16 safeguards; s. 18 information management service providers; s. 36 30-day response (+30)",
        date(2003, 9, 1), sk_reg, 30, 30,
        breach_regulator="IPC guidance recommends reporting; verify current statutory duty",
        breach_individual="Notify affected individuals of unauthorized use/disclosure where there is a risk of harm",
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={"counsel_review_note": "Verify HIPA breach-notification duty as amended (2017-2018 amendments)."},
    ))

    return regs


# ---------------------------------------------------------------------------
# 6. TERRITORIES (NT, NU, YT)
# ---------------------------------------------------------------------------

def _territories() -> List[CanonicalRegulation]:
    regs: List[CanonicalRegulation] = []

    nt_reg = "Information and Privacy Commissioner of the Northwest Territories"
    regs.append(_public_sector_act(
        "CA-NT", "Northwest Territories", "CA-NT-ATIPP",
        "Access to Information and Protection of Privacy Act (S.N.W.T. 1994, c. 20)",
        "https://www.canlii.org/en/nt/laws/stat/snwt-1994-c-20/latest/",
        "s. 8 response deadline (20 business days, as amended 2021); s. 11 extension; Part 2 protection of privacy; ss. 49.7-49.13 privacy breach notification; PIA requirements",
        date(1996, 12, 31), nt_reg, 20, 20, day_type="business_days", territory=True,
        breach_regulator="Notify the Commissioner of material breaches posing a real risk of significant harm",
        breach_individual="Notify affected individuals where real risk of significant harm",
        extra_assessments=["NWT_ATIPP_PIA"],
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={"counsel_review_note": "Verify 2019 amendment (in force 2021-07-30) business-day deadlines and breach provisions."},
    ))
    regs.append(_health_act(
        "CA-NT", "Northwest Territories", "CA-NT-HIA",
        "Health Information Act (S.N.W.T. 2014, c. 2)",
        "https://www.canlii.org/en/nt/laws/stat/snwt-2014-c-2/latest/",
        "Access 30 days (+30); breach notification to individual and Commissioner; PIA requirements",
        date(2015, 10, 1), nt_reg, 30, 30, territory=True,
        breach_regulator="Notify the Commissioner of breaches posing risk of harm",
        breach_individual="Notify affected individuals as soon as reasonably possible",
    ))

    nu_reg = "Information and Privacy Commissioner of Nunavut"
    regs.append(_public_sector_act(
        "CA-NU", "Nunavut", "CA-NU-ATIPP",
        "Access to Information and Protection of Privacy Act (S.N.W.T. (Nu) 1994, c. 20)",
        "https://www.canlii.org/en/nu/laws/stat/snwt-nu-1994-c-20/latest/",
        "s. 8 response deadline; s. 11 extension; Part 2 protection of privacy; ss. 49.7-49.13 privacy breach notification (2017 amendments); PIA for new programs/systems; health information handled under this Act (no standalone health statute)",
        date(1999, 4, 1), nu_reg, 25, 25, day_type="business_days", territory=True,
        breach_regulator="Notify the Commissioner of material privacy breaches",
        breach_individual="Notify affected individuals where real risk of significant harm",
        extra_actions=["Apply ATIPP privacy rules to personal health information held by the Department of Health (no standalone health statute)"],
        extra_assessments=["Nunavut_ATIPP_PIA"],
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={
            "data_categories_also_covered": HEALTH_DATA,
            "counsel_review_note": "Verify current response deadline (business days) and breach provisions following 2017 amendments.",
        },
    ))

    yt_reg = "Yukon Information and Privacy Commissioner"
    regs.append(_public_sector_act(
        "CA-YT", "Yukon", "CA-YT-ATIPP",
        "Access to Information and Protection of Privacy Act (S.Y. 2018, c. 9)",
        "https://laws.yukon.ca/cms/images/LEGISLATION/PRINCIPAL/2018/2018-0009/2018-0009.pdf",
        "Access requests (30 business days, with extensions); privacy impact assessments; privacy breach notification to individuals and Commissioner; data-linking and integrated services rules",
        date(2021, 4, 1), yt_reg, 30, 30, day_type="business_days", territory=True,
        breach_regulator="Notify the Commissioner where the breach creates a material risk of significant harm",
        breach_individual="Notify affected individuals where material risk of significant harm",
        extra_assessments=["Yukon_ATIPP_PIA"],
        review=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        extra_conditions={"counsel_review_note": "Verify response-deadline computation and breach threshold wording in S.Y. 2018, c. 9."},
    ))
    regs.append(_health_act(
        "CA-YT", "Yukon", "CA-YT-HIA",
        "Health Information Privacy and Management Act (HIPMA, S.Y. 2013, c. 16)",
        "https://laws.yukon.ca/cms/images/LEGISLATION/PRINCIPAL/2013/2013-0016/2013-0016.pdf",
        "Custodian duties; access 30 days (+30); breach notification to individual and Commissioner where risk of significant harm; agent and information manager agreements",
        date(2016, 8, 31), yt_reg, 30, 30, territory=True,
        breach_regulator="Notify the Commissioner as soon as reasonably possible where the breach creates a risk of significant harm",
        breach_individual="Notify affected individuals as soon as reasonably possible where risk of significant harm",
    ))

    return regs


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def get_canada_regulations() -> List[CanonicalRegulation]:
    """Return all Canadian federal, provincial and territorial canonical regulations."""
    regs = _federal() + _quebec() + _ontario() + _alberta() + _british_columbia() + _other_provinces() + _territories()
    ids = [r.regulation_id for r in regs]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ValueError(f"Duplicate Canadian regulation ids: {sorted(duplicates)}")
    return regs


__all__ = ["get_canada_regulations"]
