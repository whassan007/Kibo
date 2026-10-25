"""
KIBO Privacy OS — US Federal Regulatory Pack (US-FED).

Canonical, versioned representations of the principal US federal privacy,
health-privacy, financial-privacy, children's-privacy, education, consumer-
reporting, public-sector and critical-infrastructure cyber-reporting regimes.

Conventions for ``applicability_conditions`` (shared with us_states.py):
    organization_types_any   -> OrganizationProfileInput.organization_type values
    hipaa_status_any         -> OrganizationProfileInput.hipaa_status values
    industry_sectors_any     -> OrganizationProfileInput.industry values
    data_categories_any      -> ProcessingActivityInput.data_categories values
    activity_flags_any       -> ProcessingActivityInput boolean flags (e.g. involves_children)
    subject_locations_any    -> ProcessingActivityInput.subject_locations codes
    gate_logic               -> how the gates combine ("org_or_data", "org_and_data", "org_only", "data_only", "any_us_commerce")
    notes                    -> free-text applicability guidance for reviewers

``source_document_hash`` is a SHA-256 fingerprint of the canonical citation
(regulation id, instrument, section, source URL, rule version). It identifies the
pinned citation, not a byte-level hash of the retrieved official text.
"""

import hashlib
from datetime import date, datetime
from typing import List

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
LAST_VERIFIED_AT = datetime(2026, 10, 25)


def _source_hash(regulation_id: str, instrument: str, section: str, url: str) -> str:
    payload = "|".join([regulation_id, instrument, section, url, RULE_VERSION])
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _fed(**kwargs) -> CanonicalRegulation:
    """Builds a US-FED CanonicalRegulation with shared defaults and citation fingerprint."""
    kwargs.setdefault("jurisdiction_id", "US-FED")
    kwargs.setdefault("jurisdiction_type", JurisdictionType.FEDERAL)
    kwargs.setdefault("country", "US")
    kwargs.setdefault("rule_version", RULE_VERSION)
    kwargs.setdefault("last_verified_at", LAST_VERIFIED_AT)
    kwargs["source_document_hash"] = _source_hash(
        kwargs["regulation_id"],
        kwargs["legal_instrument"],
        kwargs["article_or_section"],
        kwargs["official_source_url"],
    )
    return CanonicalRegulation(**kwargs)


# ---------------------------------------------------------------------------
# HIPAA (Privacy, Security, Breach Notification)
# ---------------------------------------------------------------------------

_HIPAA_ORG_TYPES = ["healthcare_covered_entity", "business_associate"]
_HIPAA_STATUS = ["covered_entity", "business_associate", "hybrid_entity"]
_HIPAA_DATA = ["health_information", "phi", "ephi", "medical_records"]

_HIPAA_STATE_PREEMPTION = PreemptionRule(
    rule_id="HIPAA-160-203",
    preempts_or_yields="preempts",
    target_regulation_id="US-STATE-HEALTH-PRIVACY",
    scope_condition="Contrary state law that is less stringent than HIPAA (45 CFR § 160.203)",
    description=(
        "HIPAA preempts contrary state law, except state law that is 'more stringent' (more privacy-protective), "
        "public-health reporting laws, health-plan reporting laws, and laws granted an HHS exception. More stringent "
        "state laws (e.g., CA CMIA, TX HB 300) apply concurrently."
    ),
)


def _hipaa_privacy() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-HIPAA-PRIVACY",
        legal_authority="U.S. Department of Health and Human Services (HHS) under HIPAA, Pub. L. 104-191 § 264, as amended by HITECH Act (Pub. L. 111-5)",
        legal_instrument="HIPAA Privacy Rule — Standards for Privacy of Individually Identifiable Health Information",
        official_source_url="https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E",
        article_or_section="45 CFR Part 160 and Part 164, Subparts A and E (§§ 164.500-164.534)",
        effective_date=date(2003, 4, 14),
        applicability_conditions={
            "organization_types_any": _HIPAA_ORG_TYPES,
            "hipaa_status_any": _HIPAA_STATUS,
            "data_categories_any": _HIPAA_DATA,
            "gate_logic": "org_and_data",
            "notes": (
                "Applies to covered entities (health plans, health care clearinghouses, health care providers that "
                "conduct standard electronic transactions) and, directly for specified provisions, business associates. "
                "Small health plans (< $5M receipts) had a delayed 2004 compliance date. The 2024 Reproductive Health "
                "Care Privacy amendments were vacated nationwide (Purl v. HHS, N.D. Tex., June 18, 2025) except the "
                "Notice of Privacy Practices updates tied to 42 CFR Part 2 (compliance Feb 16, 2026)."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="HIPAA-DEIDENTIFIED",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["deidentified_safe_harbor", "deidentified_expert_determination"],
                carve_out_statute="45 CFR § 164.514(a)-(b)",
                description="Health information de-identified via Safe Harbor (18 identifiers removed) or Expert Determination is not PHI.",
            ),
            ExemptionRule(
                exemption_id="HIPAA-EMPLOYMENT-RECORDS",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["employment_records", "ferpa_education_records"],
                carve_out_statute="45 CFR § 160.103 (definition of 'protected health information')",
                description="Employment records held by a covered entity as employer and FERPA education records are excluded from PHI.",
            ),
            ExemptionRule(
                exemption_id="HIPAA-NON-COVERED-ENTITY",
                exemption_type="entity_level",
                condition_field="hipaa_status",
                condition_values=["non_hipaa"],
                carve_out_statute="45 CFR § 160.102",
                description="Consumer health apps and other entities that are neither covered entities nor business associates fall outside HIPAA (see US-FED-FTC-HBNR and state consumer health data laws).",
            ),
        ],
        preemption_rules=[_HIPAA_STATE_PREEMPTION],
        organization_types=_HIPAA_ORG_TYPES,
        industry_sectors=["healthcare", "health_insurance", "pharmacy", "health_it", "life_sciences"],
        data_subject_categories=["patients", "health_plan_members", "consumers"],
        data_categories=_HIPAA_DATA,
        processing_activities=["treatment", "payment", "health_care_operations", "research", "marketing", "sale_of_phi", "disclosure_to_business_associates"],
        required_actions=[
            "Designate a Privacy Official and a contact person for complaints (§ 164.530(a))",
            "Publish and distribute a Notice of Privacy Practices (§ 164.520)",
            "Apply the minimum necessary standard to uses, disclosures and requests (§ 164.502(b), § 164.514(d))",
            "Obtain valid HIPAA authorization for uses/disclosures not otherwise permitted, including marketing and sale of PHI (§ 164.508)",
            "Execute Business Associate Agreements before disclosing PHI to business associates (§ 164.502(e), § 164.504(e))",
            "Honor individual rights: access (§ 164.524), amendment (§ 164.526), accounting of disclosures (§ 164.528), restriction requests (§ 164.522(a)), confidential communications (§ 164.522(b))",
            "Train workforce on privacy policies and apply sanctions (§ 164.530(b), (e))",
            "Implement administrative, technical and physical safeguards for PHI (§ 164.530(c))",
            "Mitigate harmful effects of impermissible uses or disclosures (§ 164.530(f))",
            "Prohibit retaliation and waiver of rights (§ 164.530(g)-(h))",
        ],
        required_assessments=["HIPAA Privacy Rule gap assessment", "Minimum necessary review", "Business associate inventory review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="calendar_days",
            rights_request_extension_days=30,
            identity_verification_required=True,
            breach_regulator_text="See US-FED-HIPAA-BREACH",
            breach_individual_text="See US-FED-HIPAA-BREACH",
            record_retention_years=6,
        ),
        notification_requirements=[
            "Access requests: act within 30 calendar days; one 30-day extension with written notice of reasons (§ 164.524(b)(2))",
            "Amendment requests: act within 60 calendar days; one 30-day extension (§ 164.526(b)(2))",
            "Accounting of disclosures: act within 60 calendar days; one 30-day extension (§ 164.528(c))",
        ],
        required_evidence=[
            "Notice of Privacy Practices (current version and distribution/acknowledgement records)",
            "Executed Business Associate Agreements",
            "Privacy policies and procedures (retained 6 years from creation or last effective date)",
            "Workforce training records",
            "Access/amendment/accounting request logs",
            "Signed HIPAA authorizations",
        ],
        approval_requirements=["Privacy Official approval of policies", "Counsel review of marketing and sale-of-PHI uses"],
        competent_regulator="HHS Office for Civil Rights (OCR); State Attorneys General (HITECH § 13410(e) civil actions)",
        subnational_regulators={"state_attorneys_general": "Parens patriae civil enforcement under 42 U.S.C. § 1320d-5(d)"},
        domain_category="health_privacy",
    )


def _hipaa_security() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-HIPAA-SECURITY",
        legal_authority="U.S. Department of Health and Human Services (HHS) under HIPAA § 262 and HITECH Act § 13401",
        legal_instrument="HIPAA Security Rule — Security Standards for the Protection of Electronic Protected Health Information",
        official_source_url="https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C",
        article_or_section="45 CFR Part 164, Subpart C (§§ 164.302-164.318)",
        effective_date=date(2005, 4, 20),
        applicability_conditions={
            "organization_types_any": _HIPAA_ORG_TYPES,
            "hipaa_status_any": _HIPAA_STATUS,
            "data_categories_any": ["ephi", "phi", "health_information"],
            "gate_logic": "org_and_data",
            "notes": (
                "Applies to electronic PHI created, received, maintained or transmitted by covered entities and business "
                "associates (BAs directly liable since HITECH). HHS published an NPRM on Jan 6, 2025 proposing mandatory "
                "(no 'addressable') specifications, asset inventory, MFA, encryption and 72-hour restoration; it is not a "
                "final rule — track separately."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="HIPAA-SEC-PAPER-ONLY",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["paper_phi", "oral_phi"],
                carve_out_statute="45 CFR § 164.302",
                description="Security Rule applies only to ePHI; paper/oral PHI is governed by Privacy Rule safeguards (§ 164.530(c)).",
            ),
        ],
        preemption_rules=[_HIPAA_STATE_PREEMPTION],
        organization_types=_HIPAA_ORG_TYPES,
        industry_sectors=["healthcare", "health_insurance", "health_it", "cloud_services"],
        data_subject_categories=["patients", "health_plan_members"],
        data_categories=["ephi"],
        processing_activities=["storage", "transmission", "cloud_hosting", "remote_access", "ai_model_training_on_ephi"],
        required_actions=[
            "Conduct an accurate and thorough enterprise-wide risk analysis (§ 164.308(a)(1)(ii)(A))",
            "Implement risk management to reduce risks to a reasonable and appropriate level (§ 164.308(a)(1)(ii)(B))",
            "Designate a Security Official (§ 164.308(a)(2))",
            "Implement workforce security, information access management and security awareness training (§ 164.308(a)(3)-(5))",
            "Maintain security incident procedures and contingency plan incl. data backup and disaster recovery (§ 164.308(a)(6)-(7))",
            "Perform periodic technical and non-technical evaluation (§ 164.308(a)(8))",
            "Implement facility access, workstation and device/media controls (§ 164.310)",
            "Implement access control, audit controls, integrity, person/entity authentication and transmission security (§ 164.312)",
            "Address encryption at rest and in transit (addressable: implement or document equivalent alternative) (§ 164.312(a)(2)(iv), (e)(2)(ii))",
            "Flow down Security Rule obligations to subcontractors via BAAs (§ 164.314)",
        ],
        required_assessments=["HIPAA Security Risk Analysis (SRA)", "Periodic security evaluation (§ 164.308(a)(8))"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_text="See US-FED-HIPAA-BREACH",
            breach_individual_text="See US-FED-HIPAA-BREACH",
            record_retention_years=6,
        ),
        notification_requirements=["Security incidents must be identified, responded to, mitigated and documented (§ 164.308(a)(6)(ii)); BAs must report security incidents to the covered entity per the BAA (§ 164.314(a)(2)(i)(C))"],
        required_evidence=[
            "Documented risk analysis and risk management plan",
            "Security policies and procedures (retained 6 years, § 164.316(b))",
            "Audit log review records",
            "Security awareness training records",
            "Contingency/backup test results",
            "Encryption decision documentation for addressable specifications",
        ],
        approval_requirements=["Security Official sign-off on risk analysis", "Executive acceptance of residual risk"],
        competent_regulator="HHS Office for Civil Rights (OCR)",
        subnational_regulators={"state_attorneys_general": "Parens patriae civil enforcement under 42 U.S.C. § 1320d-5(d)"},
        domain_category="cybersecurity",
    )


def _hipaa_breach() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-HIPAA-BREACH",
        legal_authority="HHS under HITECH Act § 13402 (42 U.S.C. § 17932)",
        legal_instrument="HIPAA Breach Notification Rule",
        official_source_url="https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-D",
        article_or_section="45 CFR §§ 164.400-164.414 (Part 164, Subpart D)",
        effective_date=date(2009, 9, 23),
        applicability_conditions={
            "organization_types_any": _HIPAA_ORG_TYPES,
            "hipaa_status_any": _HIPAA_STATUS,
            "data_categories_any": ["phi", "ephi", "health_information"],
            "gate_logic": "org_and_data",
            "notes": (
                "Triggered by acquisition, access, use or disclosure of unsecured PHI not permitted by the Privacy Rule. "
                "An impermissible use/disclosure is presumed a breach unless a documented 4-factor risk assessment shows a "
                "low probability that PHI has been compromised (§ 164.402(2)). Discovery = first day known, or by exercising "
                "reasonable diligence would have been known, to any workforce member or agent (§ 164.404(a)(2))."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="HIPAA-BREACH-SECURED-PHI",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["encrypted_per_hhs_guidance", "destroyed_per_hhs_guidance"],
                carve_out_statute="45 CFR § 164.402 ('unsecured PHI'); HHS Guidance to Render Unsecured PHI Unusable (74 FR 42740)",
                description="PHI encrypted per NIST-consistent HHS guidance (key not compromised) or destroyed is 'secured' and outside the notification duty.",
            ),
            ExemptionRule(
                exemption_id="HIPAA-BREACH-STATUTORY-EXCEPTIONS",
                exemption_type="activity_level",
                condition_field="processing_activities",
                condition_values=["unintentional_good_faith_workforce_access", "inadvertent_internal_disclosure_between_authorized_persons", "recipient_unable_to_retain"],
                carve_out_statute="45 CFR § 164.402(1)(i)-(iii)",
                description="Three statutory exceptions to the definition of breach.",
            ),
        ],
        preemption_rules=[
            _HIPAA_STATE_PREEMPTION,
            PreemptionRule(
                rule_id="HIPAA-BREACH-STATE-CONCURRENT",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-{ST}-BREACH",
                scope_condition="State breach statutes with HIPAA-compliance safe harbors or shorter deadlines",
                description="Many state breach laws deem HIPAA-compliant notice sufficient; others (e.g., CA H&S Code § 1280.15 15-business-day rule, TX AG notice) impose additional or shorter duties that apply concurrently.",
            ),
        ],
        organization_types=_HIPAA_ORG_TYPES,
        industry_sectors=["healthcare", "health_insurance", "health_it"],
        data_subject_categories=["patients", "health_plan_members"],
        data_categories=["phi", "ephi"],
        processing_activities=["breach_response", "incident_response"],
        required_actions=[
            "Perform and document the 4-factor risk assessment: (1) nature/extent of PHI incl. identifiers and re-identification likelihood; (2) unauthorized person who used/received the PHI; (3) whether PHI was actually acquired or viewed; (4) extent risk has been mitigated (§ 164.402(2))",
            "Notify affected individuals without unreasonable delay and no later than 60 calendar days after discovery by first-class mail or e-mail if agreed (§ 164.404)",
            "Provide substitute notice (website posting 90 days or major media + toll-free number active 90 days) when contact info is insufficient for 10+ individuals (§ 164.404(d)(2))",
            "Notify prominent media outlets serving a State/jurisdiction when > 500 residents of that State/jurisdiction are affected, within 60 days (§ 164.406)",
            "Notify HHS Secretary contemporaneously with individual notice (within 60 days) for breaches affecting 500+ individuals (§ 164.408(b))",
            "Log breaches affecting < 500 individuals and report to HHS within 60 days after the end of each calendar year (§ 164.408(c))",
            "Business associates notify the covered entity without unreasonable delay and no later than 60 days after discovery, identifying each individual (§ 164.410)",
            "Honor law-enforcement delay requests (§ 164.412)",
        ],
        required_assessments=["HIPAA 4-factor breach risk assessment (45 CFR § 164.402(2))"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_days=60,
            breach_regulator_text=(
                "HHS OCR: >= 500 individuals — contemporaneously with individual notice and no later than 60 calendar days "
                "after discovery; < 500 individuals — annual log submission within 60 days after end of calendar year"
            ),
            breach_attorney_general_threshold_individuals=500,
            breach_individual_notification_days=60,
            breach_individual_text="Without unreasonable delay and in no case later than 60 calendar days after discovery",
            record_retention_years=6,
        ),
        notification_requirements=[
            "Individuals: <= 60 calendar days after discovery (§ 164.404(b))",
            "HHS OCR (>= 500): contemporaneous with individuals, <= 60 days, via OCR breach portal (§ 164.408(b))",
            "HHS OCR (< 500): annual, within 60 days after calendar year-end (§ 164.408(c))",
            "Media: > 500 residents of a State/jurisdiction, <= 60 days (§ 164.406)",
            "Business associate -> covered entity: <= 60 days after discovery (§ 164.410)",
        ],
        required_evidence=[
            "Documented 4-factor risk assessment (burden of proof on CE/BA, § 164.414(b))",
            "Copies of individual, media and HHS notifications",
            "Breach log for < 500 incidents",
            "Discovery date determination record",
        ],
        approval_requirements=["Privacy Official and counsel sign-off on 'low probability of compromise' determinations", "Executive approval of external notifications"],
        competent_regulator="HHS Office for Civil Rights (OCR)",
        subnational_regulators={"state_attorneys_general": "Parens patriae civil enforcement under 42 U.S.C. § 1320d-5(d)"},
        domain_category="breach_notification",
    )


# ---------------------------------------------------------------------------
# GLBA (Privacy, Safeguards, FTC breach notice) + Bank Incident Notification
# ---------------------------------------------------------------------------

def _glba() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-GLBA-PRIVACY",
        legal_authority="Gramm-Leach-Bliley Act Title V, Subtitle A; CFPB (Regulation P), FTC (Safeguards Rule), federal banking agencies, SEC and state insurance regulators",
        legal_instrument="Gramm-Leach-Bliley Act Privacy Rule (Regulation P) & FTC Standards for Safeguarding Customer Information (Safeguards Rule); Interagency Computer-Security Incident Notification Rule",
        official_source_url="https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-314",
        article_or_section="15 U.S.C. §§ 6801-6809; 12 CFR Part 1016 (Reg. P); 16 CFR Part 314 (Safeguards Rule, incl. § 314.4(j) and § 314.5); 12 CFR Part 53 (OCC), 12 CFR Part 225 Subpart N (FRB), 12 CFR Part 304 Subpart C (FDIC)",
        effective_date=date(2001, 7, 1),
        applicability_conditions={
            "organization_types_any": ["financial_institution"],
            "industry_sectors_any": ["banking", "insurance", "financial_services", "fintech", "lending", "mortgage", "securities", "payments", "credit_union", "tax_preparation", "auto_dealer_financing"],
            "data_categories_any": ["nonpublic_personal_information", "financial_data", "customer_financial_information"],
            "gate_logic": "org_or_data",
            "notes": (
                "Applies to 'financial institutions' — businesses significantly engaged in financial activities under "
                "12 U.S.C. § 1843(k). The FTC Safeguards Rule covers non-bank financial institutions; banks follow the "
                "Interagency Guidelines (12 CFR Part 30 App. B etc.); insurers are regulated by state insurance law "
                "(NAIC Model 668 where adopted). Safeguards Rule amendments: core 2021 amendments compliance June 9, 2023; "
                "FTC breach notice § 314.4(j) effective May 13, 2024. Bank Computer-Security Incident Notification Rule "
                "effective April 1, 2022 (compliance May 1, 2022). SEC Regulation S-P amendments (17 CFR 248.30) require "
                "customer notice within 30 days; compliance Dec 3, 2025 (larger entities) / June 3, 2026 (smaller)."
            ),
        },
        thresholds=[
            StatutoryThreshold(
                metric="consumer_records_count",
                operator="<",
                value=5000,
                logic_group="AND",
                description="Safeguards Rule § 314.6: institutions maintaining customer information on fewer than 5,000 consumers are exempt from § 314.4(b)(1), (d)(2), (h) and (i) (written risk assessment, pen/vuln testing cadence, written IRP, annual board report).",
            ),
            StatutoryThreshold(
                metric="affected_consumers_count",
                operator=">=",
                value=500,
                logic_group="AND",
                description="FTC Safeguards Rule § 314.4(j): notification event involving unencrypted customer information of >= 500 consumers triggers FTC notice.",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="GLBA-CONSUMER-REPORTING-FCRA",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["consumer_report_data"],
                carve_out_statute="15 U.S.C. § 6806; FCRA 15 U.S.C. § 1681",
                description="Consumer report sharing among affiliates is governed by FCRA rather than GLBA notice/opt-out.",
            ),
            ExemptionRule(
                exemption_id="GLBA-NOTICE-EXCEPTIONS",
                exemption_type="activity_level",
                condition_field="processing_activities",
                condition_values=["service_provider_joint_marketing", "processing_servicing_transactions", "fraud_prevention", "legal_compliance"],
                carve_out_statute="15 U.S.C. § 6802(b)(2), (e); 12 CFR §§ 1016.13-1016.15",
                description="Opt-out is not required for disclosures under §§ 13-15 exceptions (service providers/joint marketing with contract, transaction processing, fraud, legal process).",
            ),
            ExemptionRule(
                exemption_id="GLBA-ANNUAL-NOTICE-FAST-ACT",
                exemption_type="activity_level",
                condition_field="processing_activities",
                condition_values=["no_sharing_beyond_exceptions_and_policy_unchanged"],
                carve_out_statute="15 U.S.C. § 6803(f) (FAST Act 2015); 12 CFR § 1016.5(e)",
                description="Annual privacy notice not required if sharing is limited to exceptions and policies have not changed.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="GLBA-6807-STATE-FLOOR",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-STATE-FINANCIAL-PRIVACY",
                scope_condition="State law affording greater consumer protection (15 U.S.C. § 6807)",
                description="GLBA is a floor; more protective state laws (e.g., CA Financial Information Privacy Act, NYDFS 23 NYCRR 500) apply. Most comprehensive state privacy laws exempt GLBA entities or GLBA-covered data.",
            ),
        ],
        organization_types=["financial_institution"],
        industry_sectors=["banking", "insurance", "financial_services", "fintech", "securities", "lending", "payments"],
        data_subject_categories=["consumers", "customers"],
        data_categories=["nonpublic_personal_information", "financial_data", "account_numbers", "ssn"],
        processing_activities=["sharing_with_nonaffiliated_third_parties", "affiliate_sharing", "marketing", "service_provider_processing"],
        required_actions=[
            "Deliver initial privacy notice to customers at relationship inception and annual notice unless FAST Act exception applies (12 CFR §§ 1016.4-1016.5)",
            "Provide opt-out notice and reasonable opt-out method before sharing NPI with nonaffiliated third parties (12 CFR §§ 1016.7-1016.10)",
            "Do not disclose account numbers to nonaffiliated third parties for marketing (15 U.S.C. § 6802(d); 12 CFR § 1016.12)",
            "Designate a Qualified Individual to oversee the information security program (16 CFR § 314.4(a))",
            "Maintain a written information security program based on a written risk assessment (§ 314.4(b))",
            "Implement access controls, data inventory, encryption in transit and at rest, secure development, MFA for any individual accessing information systems, secure disposal within 2 years of last use, change management, and activity monitoring (§ 314.4(c))",
            "Conduct continuous monitoring or annual penetration testing and vulnerability assessments every 6 months (§ 314.4(d)(2))",
            "Oversee service providers by selection, contract and periodic assessment (§ 314.4(f))",
            "Maintain a written incident response plan (§ 314.4(h))",
            "Qualified Individual reports in writing at least annually to the board (§ 314.4(i))",
            "Notify the FTC of notification events involving >= 500 consumers (§ 314.4(j))",
            "Banking organizations: notify primary federal regulator of 'notification incidents' within 36 hours; bank service providers notify bank customers as soon as possible when an incident disrupts services for >= 4 hours (12 CFR Part 53 / 225 Subpart N / 304 Subpart C)",
        ],
        required_assessments=["GLBA Safeguards written risk assessment (16 CFR § 314.4(b))", "Service provider risk assessment", "Annual penetration test / semi-annual vulnerability assessment"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=True,
            breach_regulator_hours=36,
            breach_regulator_days=30,
            breach_regulator_text=(
                "FTC (non-bank FIs): as soon as possible and no later than 30 days after discovery of a notification event "
                "involving unencrypted customer information of >= 500 consumers (16 CFR § 314.4(j)). Banking organizations: "
                "primary federal regulator (OCC/FDIC/FRB) as soon as possible and no later than 36 hours after determining a "
                "computer-security 'notification incident' occurred (12 CFR § 53.3)."
            ),
            breach_attorney_general_threshold_individuals=500,
            breach_individual_text=(
                "Banks: as soon as possible under Interagency Guidance on Response Programs (12 CFR Part 30 App. B Supp. A); "
                "SEC-registered broker-dealers/investment advisers: no later than 30 days (Reg. S-P § 248.30(a)(4)); "
                "otherwise per applicable state breach law"
            ),
            record_retention_years=5,
        ),
        notification_requirements=[
            "FTC: <= 30 days after discovery for >= 500 consumers (16 CFR § 314.4(j)); notice is published by the FTC",
            "OCC/FDIC/FRB: <= 36 hours after determination of a notification incident (12 CFR Part 53; Part 225 Subpart N; Part 304 Subpart C)",
            "Bank service provider -> bank customer: as soon as possible when incident materially disrupts services for >= 4 hours",
            "SEC Reg. S-P: affected individuals <= 30 days; service providers notify covered institution <= 72 hours",
            "State insurance regulators: per state adoption of NAIC Insurance Data Security Model Law (#668), commonly 72 hours",
        ],
        required_evidence=[
            "Initial and annual privacy notices (Reg. P model form)",
            "Opt-out records",
            "Written information security program",
            "Written risk assessment",
            "Annual Qualified Individual report to the board",
            "Penetration test and vulnerability scan reports",
            "Service provider contracts and oversight records",
            "Incident response plan and FTC/regulator notification records",
        ],
        approval_requirements=["Board of directors (or senior officer) receives annual Qualified Individual report", "Counsel approval of sharing outside § 6802(e) exceptions"],
        competent_regulator="Federal Trade Commission (non-bank FIs); Consumer Financial Protection Bureau (Reg. P); OCC / FDIC / Federal Reserve / NCUA (banks & credit unions); SEC (broker-dealers, advisers); state insurance regulators",
        subnational_regulators={"state_insurance_departments": "GLBA § 6805(a)(6) functional regulation of insurers", "NYDFS": "23 NYCRR 500 for NY-licensed entities"},
        domain_category="financial_privacy",
    )


# ---------------------------------------------------------------------------
# FTC Act Section 5 & FTC Health Breach Notification Rule
# ---------------------------------------------------------------------------

def _ftc_act_sec5() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-FTC-ACT-SEC5",
        legal_authority="Federal Trade Commission under the FTC Act of 1914, as amended",
        legal_instrument="Federal Trade Commission Act, Section 5 — Unfair or Deceptive Acts or Practices",
        official_source_url="https://www.law.cornell.edu/uscode/text/15/45",
        article_or_section="15 U.S.C. § 45(a), (n) (unfairness standard); 15 U.S.C. § 57b (civil redress)",
        effective_date=date(1938, 3, 21),
        applicability_conditions={
            "gate_logic": "any_us_commerce",
            "notes": (
                "Applies to persons, partnerships and corporations in or affecting commerce, excluding banks, savings and "
                "loans, federal credit unions, common carriers subject to the Communications Act, air carriers, and "
                "non-profits (§ 45(a)(2); § 44). Privacy/security deception (statements in privacy policies, UIs, AI "
                "marketing claims) and unfairness (substantial injury not reasonably avoidable and not outweighed by "
                "benefits, § 45(n)) — incl. inadequate data security, unfair use of AI/facial recognition (Rite Aid, 2023), "
                "deceptive AI capability claims (Operation AI Comply, 2024), dark patterns, and sale of sensitive "
                "location data. Remedies include algorithmic/model disgorgement."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="FTC-JURISDICTIONAL-CARVEOUTS",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["bank", "savings_and_loan", "federal_credit_union", "common_carrier", "air_carrier", "nonprofit"],
                carve_out_statute="15 U.S.C. § 44, § 45(a)(2)",
                description="Entities outside FTC Section 5 jurisdiction (subject to their own prudential/sectoral regulators; nonprofits outside 'corporation' definition unless operating for members' profit).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="FTC5-STATE-UDAP-CONCURRENT",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-STATE-UDAP",
                scope_condition="State 'mini-FTC Acts' (UDAP statutes)",
                description="Section 5 does not preempt state UDAP statutes, which are enforced concurrently by State Attorneys General.",
            ),
        ],
        organization_types=["private", "public"],
        industry_sectors=["all"],
        data_subject_categories=["consumers"],
        data_categories=["personal_information", "sensitive_data", "precise_geolocation", "health_information", "biometric_data", "children_data"],
        processing_activities=["privacy_notices", "data_security", "ai_or_admt", "facial_recognition", "targeted_advertising", "data_brokering", "dark_patterns", "ai_marketing_claims"],
        required_actions=[
            "Ensure privacy notices, consent flows and AI capability claims are truthful, not misleading, and substantiated",
            "Implement reasonable data security proportionate to data sensitivity and size",
            "Avoid dark patterns that subvert consumer choice",
            "Obtain affirmative express consent before material retroactive changes to data practices",
            "Assess and mitigate foreseeable consumer harm from AI/biometric systems (bias testing, accuracy, monitoring)",
            "Do not sell or share sensitive location/health data without affirmative express consent",
            "Maintain substantiation for AI performance claims",
        ],
        required_assessments=["Privacy representation/claims substantiation review", "Algorithmic fairness and accuracy assessment for consumer-facing AI", "Data security program review"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False, breach_regulator_text="No standalone breach notification duty; see US-FED-FTC-HBNR, US-FED-GLBA-PRIVACY and state breach laws"),
        notification_requirements=["Compliance with FTC consent orders (typically 20-year duration) including biennial independent assessments and incident reporting to FTC within specified days"],
        required_evidence=["Claim substantiation files", "Consent records", "Data security program documentation", "AI testing/validation reports"],
        approval_requirements=["Legal/marketing review of privacy and AI claims before publication"],
        competent_regulator="Federal Trade Commission (Bureau of Consumer Protection)",
        subnational_regulators={"state_attorneys_general": "Concurrent enforcement under state UDAP statutes"},
        domain_category="privacy",
    )


def _ftc_hbnr() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-FTC-HBNR",
        legal_authority="Federal Trade Commission under HITECH Act § 13407 (42 U.S.C. § 17937)",
        legal_instrument="FTC Health Breach Notification Rule",
        official_source_url="https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-318",
        article_or_section="16 CFR Part 318 (§§ 318.1-318.9), as amended 89 FR 47028 (effective July 29, 2024)",
        effective_date=date(2009, 9, 24),
        applicability_conditions={
            "hipaa_status_any": ["non_hipaa"],
            "industry_sectors_any": ["digital_health", "health_apps", "wearables", "fitness", "consumer_health"],
            "data_categories_any": ["health_information", "personal_health_record", "consumer_health_data", "fitness_data"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to vendors of personal health records (PHR), PHR related entities and third-party service providers "
                "that are NOT HIPAA covered entities or business associates. A PHR is an electronic record of identifiable "
                "health information that can be drawn from multiple sources (2024 amendment clarifies apps that draw from "
                "device APIs + user input qualify). A 'breach of security' includes unauthorized disclosures (e.g., sharing "
                "with ad platforms without authorization), not only cybersecurity intrusions (GoodRx, BetterHelp, Easy Healthcare)."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="HBNR-HIPAA-ENTITIES",
                exemption_type="entity_level",
                condition_field="hipaa_status",
                condition_values=["covered_entity", "business_associate"],
                carve_out_statute="16 CFR § 318.1(a)",
                description="HIPAA covered entities and business associates (acting as such) are governed by 45 CFR §§ 164.400-414 instead.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="HBNR-YIELDS-HIPAA",
                preempts_or_yields="yields_to",
                target_regulation_id="US-FED-HIPAA-BREACH",
                scope_condition="Entity is a HIPAA covered entity or business associate",
                description="HBNR does not apply where HIPAA Breach Notification Rule governs.",
            ),
            PreemptionRule(
                rule_id="HBNR-STATE-CONCURRENT",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-WA-MHMDA",
                scope_condition="Consumer health data of WA/NV/CT consumers",
                description="State consumer health data laws apply concurrently.",
            ),
        ],
        organization_types=["private"],
        industry_sectors=["digital_health", "health_apps", "wearables", "consumer_health"],
        data_subject_categories=["consumers", "app_users"],
        data_categories=["personal_health_record", "health_information"],
        processing_activities=["health_app_operation", "advertising_disclosure", "analytics_sdk_sharing", "breach_response"],
        required_actions=[
            "Notify each affected US individual without unreasonable delay and within 60 calendar days after discovery (§ 318.4(a)) with the content required by § 318.6 (incl. identity of third parties that acquired data)",
            "Notify the FTC: >= 500 individuals — contemporaneously with individual notice and within 60 calendar days; < 500 — log and report within 60 calendar days following the end of the calendar year (§ 318.5(c))",
            "Notify prominent media outlets when > 500 residents of a State/territory are affected (§ 318.5(b))",
            "Third-party service providers notify the PHR vendor/related entity within 60 days of discovery (§ 318.3(b))",
            "Obtain affirmative express authorization before disclosing PHR identifiable health information to third parties (e.g., advertising platforms)",
        ],
        required_assessments=["PHR vendor status determination", "Third-party SDK/pixel data flow assessment"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_days=60,
            breach_regulator_text="FTC: >= 500 individuals contemporaneously with individual notice and within 60 calendar days of discovery; < 500 annually within 60 days after calendar year-end",
            breach_attorney_general_threshold_individuals=500,
            breach_individual_notification_days=60,
            breach_individual_text="Without unreasonable delay and in no case later than 60 calendar days after discovery (email + in-app/text permitted under 2024 amendments)",
        ),
        notification_requirements=[
            "Individuals: <= 60 calendar days",
            "FTC: >= 500 within 60 days via FTC form; < 500 annual log",
            "Media: > 500 residents of a State",
            "Civil penalties per violation (inflation-adjusted, > $50,000 per violation) under 15 U.S.C. § 45(m)",
        ],
        required_evidence=["Breach determination memo", "Notification copies and FTC submission", "Third-party disclosure authorization records", "SDK/pixel inventory"],
        approval_requirements=["Counsel sign-off on PHR vendor/HIPAA status determination"],
        competent_regulator="Federal Trade Commission",
        domain_category="breach_notification",
    )


# ---------------------------------------------------------------------------
# COPPA, FERPA, FCRA
# ---------------------------------------------------------------------------

def _coppa() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-COPPA",
        legal_authority="Federal Trade Commission under the Children's Online Privacy Protection Act of 1998",
        legal_instrument="Children's Online Privacy Protection Act & COPPA Rule",
        official_source_url="https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312",
        article_or_section="15 U.S.C. §§ 6501-6506; 16 CFR Part 312 (as amended 90 FR 16918, effective June 23, 2025; compliance April 22, 2026)",
        effective_date=date(2000, 4, 21),
        applicability_conditions={
            "activity_flags_any": ["involves_children"],
            "data_subject_categories_any": ["children_under_13", "children"],
            "data_categories_any": ["children_data"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to operators of commercial websites/online services (incl. apps, IoT, ed-tech) directed to children "
                "under 13, or with actual knowledge they collect personal information from a child under 13, and to "
                "operators with actual knowledge they collect from users of a child-directed service (e.g., ad networks, "
                "plug-ins). 2025 amendments (compliance April 22, 2026): separate verifiable parental consent for "
                "third-party disclosures incl. targeted advertising, written children's information security program, "
                "written data retention policy (no indefinite retention), biometric identifiers added to 'personal "
                "information', expanded Safe Harbor transparency."
            ),
        },
        thresholds=[
            StatutoryThreshold(metric="data_subject_age", operator="<", value=13, logic_group="AND", description="Child = individual under the age of 13 (15 U.S.C. § 6501(1))."),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="COPPA-NONPROFIT",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["nonprofit", "government_agency"],
                carve_out_statute="15 U.S.C. § 6501(2)(B) (operator definition tied to FTC Act § 5 jurisdiction)",
                description="Nonprofits outside FTC Act jurisdiction and government entities are not 'operators'.",
            ),
            ExemptionRule(
                exemption_id="COPPA-CONSENT-EXCEPTIONS",
                exemption_type="activity_level",
                condition_field="processing_activities",
                condition_values=["support_for_internal_operations", "one_time_response", "parental_contact_for_consent", "child_safety", "school_authorized_edtech"],
                carve_out_statute="16 CFR § 312.5(c)",
                description="Enumerated exceptions to prior verifiable parental consent (e.g., persistent identifiers solely for internal operations).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="COPPA-6502-STATE-INCONSISTENT",
                preempts_or_yields="preempts",
                target_regulation_id="US-STATE-CHILDREN-PRIVACY",
                scope_condition="State law imposing liability inconsistent with COPPA treatment of activities in interstate commerce (15 U.S.C. § 6502(d))",
                description="COPPA expressly preempts inconsistent state requirements for under-13 online data; consistent state laws and teen (13-17) protections (e.g., CT, CO, MD, OR minors provisions) apply.",
            ),
        ],
        organization_types=["private"],
        industry_sectors=["gaming", "edtech", "social_media", "media", "toys", "adtech", "streaming"],
        data_subject_categories=["children_under_13", "parents"],
        data_categories=["children_data", "persistent_identifiers", "geolocation", "photos_video_audio", "biometric_data"],
        processing_activities=["online_collection_from_children", "targeted_advertising", "third_party_disclosure", "ai_training"],
        required_actions=[
            "Post a clear, complete online privacy notice describing children's data practices (§ 312.4(d))",
            "Provide direct notice to parents and obtain verifiable parental consent before collection, use or disclosure (§ 312.4(b)-(c), § 312.5)",
            "Obtain separate verifiable parental consent for disclosure to third parties, incl. for targeted advertising, unless integral to the service (§ 312.5(a)(2), 2025 amendment)",
            "Give parents the right to review, delete and refuse further collection/use (§ 312.6)",
            "Do not condition participation on collecting more personal information than reasonably necessary (§ 312.7)",
            "Establish and maintain a written children's personal information security program with annual assessment (§ 312.8)",
            "Establish and publish a written data retention policy; retain only as long as reasonably necessary and never indefinitely (§ 312.10)",
            "Ensure service providers/third parties maintain confidentiality, security and integrity (§ 312.8)",
        ],
        required_assessments=["Child-directed / mixed-audience status determination", "Annual children's information security risk assessment (§ 312.8)", "Age assurance / neutral age-screen review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=None,
            identity_verification_required=True,
            breach_regulator_text="No standalone breach-notice clock; state breach laws apply. Security program must address incidents.",
        ),
        notification_requirements=["Material changes to practices require new parental notice and consent", "Civil penalties per violation (inflation-adjusted, > $50,000) under 15 U.S.C. § 45(m)"],
        required_evidence=["Verifiable parental consent records (method and timestamp)", "Direct notice copies", "Written information security program", "Data retention policy", "Third-party disclosure inventory", "Safe Harbor certification (if applicable)"],
        approval_requirements=["Counsel review of child-directed determination", "Product/legal approval before enabling third-party ad SDKs on child-directed surfaces"],
        competent_regulator="Federal Trade Commission",
        subnational_regulators={"state_attorneys_general": "Civil actions as parens patriae (15 U.S.C. § 6504)"},
        domain_category="children_privacy",
    )


def _ferpa() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-FERPA",
        legal_authority="U.S. Department of Education, Student Privacy Policy Office (SPPO)",
        legal_instrument="Family Educational Rights and Privacy Act of 1974",
        official_source_url="https://www.ecfr.gov/current/title-34/subtitle-A/part-99",
        article_or_section="20 U.S.C. § 1232g; 34 CFR Part 99",
        effective_date=date(1974, 11, 19),
        applicability_conditions={
            "organization_types_any": ["educational_institution"],
            "industry_sectors_any": ["education", "higher_education", "k12", "edtech"],
            "data_categories_any": ["education_records", "student_data"],
            "gate_logic": "org_or_data",
            "notes": (
                "Applies to educational agencies and institutions receiving funds under any program administered by the "
                "Department of Education. Ed-tech vendors are bound indirectly as 'school officials' with legitimate "
                "educational interest under direct control of the institution (§ 99.31(a)(1)(i)(B)). Rights transfer to "
                "the student at age 18 or upon attending postsecondary institution ('eligible student')."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="FERPA-DIRECTORY-INFO",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["directory_information"],
                carve_out_statute="34 CFR § 99.31(a)(11), § 99.37",
                description="Directory information may be disclosed without consent after public notice and opportunity to opt out.",
            ),
            ExemptionRule(
                exemption_id="FERPA-EXCLUDED-RECORDS",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["sole_possession_records", "law_enforcement_unit_records", "employment_records", "treatment_records_eligible_students", "alumni_records"],
                carve_out_statute="34 CFR § 99.3 ('education records' exclusions)",
                description="Records excluded from the definition of education records.",
            ),
            ExemptionRule(
                exemption_id="FERPA-HIPAA-BOUNDARY",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["ferpa_education_records"],
                carve_out_statute="45 CFR § 160.103",
                description="Student health records that are education records are governed by FERPA, not HIPAA.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="FERPA-STATE-STUDENT-PRIVACY",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-STATE-STUDENT-PRIVACY",
                scope_condition="State student data privacy laws (e.g., CA SOPIPA, NY Educ. Law § 2-d)",
                description="State student privacy laws impose additional vendor contract, security and breach duties.",
            ),
        ],
        organization_types=["educational_institution", "government_agency"],
        industry_sectors=["education", "edtech"],
        data_subject_categories=["students", "eligible_students", "parents"],
        data_categories=["education_records", "student_data", "pii_from_education_records"],
        processing_activities=["disclosure_to_school_officials", "studies_and_audits", "edtech_processing", "directory_disclosure"],
        required_actions=[
            "Provide annual notification of FERPA rights to parents/eligible students (§ 99.7)",
            "Grant access to education records within 45 days of request (§ 99.10(b))",
            "Provide opportunity to seek amendment and a hearing (§§ 99.20-99.22)",
            "Obtain signed, dated written consent before disclosing PII from education records unless an exception applies (§ 99.30-99.31)",
            "Use reasonable methods to ensure school officials access only records with legitimate educational interest (§ 99.31(a)(1)(ii))",
            "Maintain a record of each request and disclosure with the education record (§ 99.32)",
            "Enter written agreements for studies and audit/evaluation disclosures (§ 99.31(a)(6), § 99.35)",
            "Impose redisclosure limitations on recipients (§ 99.33)",
        ],
        required_assessments=["Ed-tech vendor 'school official' qualification review", "Directory information policy review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            rights_request_day_type="calendar_days",
            identity_verification_required=True,
            breach_regulator_text="No federal breach-notice clock; Department of Education may require reporting under program agreements; state breach and student privacy laws apply",
        ),
        notification_requirements=["Annual FERPA rights notification", "Directory information public notice with opt-out window"],
        required_evidence=["Annual notification", "Record of disclosures (§ 99.32)", "Written consents", "Vendor agreements designating school officials", "Study/audit written agreements"],
        approval_requirements=["Registrar/FERPA compliance officer approval of non-consensual disclosures"],
        competent_regulator="U.S. Department of Education — Student Privacy Policy Office (SPPO)",
        domain_category="privacy",
    )


def _fcra() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-FCRA",
        legal_authority="Consumer Financial Protection Bureau (Regulation V) and Federal Trade Commission",
        legal_instrument="Fair Credit Reporting Act",
        official_source_url="https://www.law.cornell.edu/uscode/text/15/chapter-41/subchapter-III",
        article_or_section="15 U.S.C. § 1681 et seq.; 12 CFR Part 1022 (Regulation V); 16 CFR Part 681 (Red Flags Rule); 16 CFR Part 682 (Disposal Rule)",
        effective_date=date(1971, 4, 25),
        applicability_conditions={
            "data_categories_any": ["consumer_report_data", "credit_data", "background_check_data", "tenant_screening_data"],
            "industry_sectors_any": ["consumer_reporting", "lending", "banking", "employment_screening", "tenant_screening", "insurance", "data_broker"],
            "processing_activities_any": ["eligibility_decisions", "employment_screening", "credit_underwriting", "ai_or_admt"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to consumer reporting agencies (CRAs), users of consumer reports (permissible purpose, adverse "
                "action), and furnishers. Data brokers and AI/ADMT vendors assembling consumer information used for "
                "credit, employment, insurance or housing eligibility may be CRAs. CFPB's Dec 2024 proposed data broker "
                "rule was withdrawn in 2025."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="FCRA-FIRST-PARTY-EXPERIENCE",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["first_party_transaction_experience"],
                carve_out_statute="15 U.S.C. § 1681a(d)(2)(A)(i)",
                description="Reports solely of transactions or experiences between the consumer and the person making the report are not consumer reports.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="FCRA-1681T",
                preempts_or_yields="preempts",
                target_regulation_id="US-STATE-CONSUMER-REPORTING",
                scope_condition="Subject matter enumerated in 15 U.S.C. § 1681t(b) (e.g., prescreening, dispute timing, adverse action duties, affiliate sharing)",
                description="FCRA preempts state laws on enumerated subjects; otherwise state laws apply if not inconsistent (§ 1681t(a)). State comprehensive privacy laws exempt FCRA-regulated activity.",
            ),
        ],
        organization_types=["private", "financial_institution"],
        industry_sectors=["consumer_reporting", "lending", "employment_screening", "tenant_screening", "insurance"],
        data_subject_categories=["consumers", "job_applicants", "employees", "tenants"],
        data_categories=["consumer_report_data", "credit_data", "background_check_data"],
        processing_activities=["consumer_reporting", "eligibility_decisions", "employment_screening", "adverse_action", "furnishing"],
        required_actions=[
            "Obtain/report consumer reports only for a permissible purpose (§ 1681b)",
            "Employment: provide standalone written disclosure and obtain written authorization before procuring a report; pre-adverse action notice with copy of report and summary of rights (§ 1681b(b))",
            "Provide adverse action notices incl. credit score disclosure where used (§ 1681m)",
            "CRAs: follow reasonable procedures to assure maximum possible accuracy (§ 1681e(b))",
            "CRAs: reinvestigate disputes within 30 days (extendable 15 days) (§ 1681i)",
            "Furnishers: conduct reasonable investigations of direct and indirect disputes (§ 1681s-2)",
            "Implement an Identity Theft Prevention (Red Flags) Program for covered accounts (16 CFR Part 681)",
            "Properly dispose of consumer report information (16 CFR Part 682)",
        ],
        required_assessments=["Permissible purpose review", "AI/ADMT model adverse-action reason code explainability review", "Red Flags covered-account risk assessment"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=30,
            rights_request_day_type="calendar_days",
            rights_request_extension_days=15,
            identity_verification_required=True,
            breach_regulator_text="No FCRA breach-notice clock; GLBA and state breach laws apply",
            record_retention_years=2,
        ),
        notification_requirements=["Adverse action notices", "Summary of Consumer Rights", "Identity theft block within 4 business days (§ 1681c-2)"],
        required_evidence=["Permissible purpose certifications", "Employment disclosure and authorization forms", "Adverse action notice templates and logs", "Dispute investigation records", "Red Flags program and board approval"],
        approval_requirements=["Board (or senior management) approval of initial Red Flags program (16 CFR § 681.1(e))"],
        competent_regulator="Consumer Financial Protection Bureau; Federal Trade Commission",
        subnational_regulators={"state_attorneys_general": "Enforcement under 15 U.S.C. § 1681s(c)"},
        domain_category="financial_privacy",
    )


# ---------------------------------------------------------------------------
# Public sector: Privacy Act of 1974 + E-Government Act § 208
# ---------------------------------------------------------------------------

def _privacy_act_1974() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-PRIVACY-ACT-1974",
        legal_authority="U.S. Congress; implemented by OMB Circulars A-108 and A-130 and agency regulations",
        legal_instrument="Privacy Act of 1974 & E-Government Act of 2002, Section 208",
        official_source_url="https://www.law.cornell.edu/uscode/text/5/552a",
        article_or_section="5 U.S.C. § 552a; E-Government Act of 2002, Pub. L. 107-347 § 208 (44 U.S.C. § 3501 note); OMB M-03-22; OMB Circular A-108; OMB M-17-12",
        effective_date=date(1975, 9, 27),
        applicability_conditions={
            "organization_types_any": ["government_agency"],
            "industry_sectors_any": ["federal_government", "federal_contractor"],
            "data_categories_any": ["federal_system_of_records"],
            "gate_logic": "org_or_data",
            "notes": (
                "Applies to federal executive-branch agencies maintaining systems of records retrieved by an individual's "
                "name or identifier, and to government contractors operating such systems on an agency's behalf "
                "(§ 552a(m)). Protects US citizens and lawful permanent residents (Judicial Redress Act of 2015 extends "
                "certain rights to covered-country citizens). E-Gov Act § 208 requires a PIA before developing or procuring "
                "IT that collects identifiable information or initiating a new electronic collection from 10+ persons."
            ),
        },
        exemptions=[
            ExemptionRule(
                exemption_id="PA-GENERAL-SPECIFIC-EXEMPTIONS",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["cia_records", "criminal_law_enforcement_records", "classified_records", "investigatory_records"],
                carve_out_statute="5 U.S.C. § 552a(j)-(k)",
                description="Agencies may promulgate rules exempting systems from certain provisions.",
            ),
            ExemptionRule(
                exemption_id="PA-STATE-LOCAL-PRIVATE",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["private", "state_agency", "local_government"],
                carve_out_statute="5 U.S.C. § 552(f) via § 552a(a)(1)",
                description="Does not apply to state/local governments or private entities unless operating a system of records under federal contract.",
            ),
        ],
        preemption_rules=[],
        organization_types=["government_agency", "federal_contractor"],
        industry_sectors=["federal_government", "public_sector"],
        data_subject_categories=["us_citizens", "lawful_permanent_residents", "federal_employees", "beneficiaries"],
        data_categories=["federal_system_of_records", "ssn", "pii"],
        processing_activities=["system_of_records_maintenance", "computer_matching", "routine_use_disclosure", "new_it_system_procurement"],
        required_actions=[
            "Publish a System of Records Notice (SORN) in the Federal Register; new/modified routine uses require 30-day public comment (§ 552a(e)(4), (e)(11))",
            "Report new/altered systems to OMB and Congress (§ 552a(r); OMB A-108)",
            "Provide Privacy Act (e)(3) statement at point of collection",
            "Disclose records only with written consent or under § 552a(b) exceptions; keep an accounting of disclosures for 5 years or life of record (§ 552a(c))",
            "Grant access and amendment rights; acknowledge amendment requests within 10 working days (§ 552a(d))",
            "Establish appropriate administrative, technical and physical safeguards (§ 552a(e)(10))",
            "Conduct a Privacy Impact Assessment and make it publicly available where practicable (E-Gov Act § 208(b))",
            "Execute Computer Matching Agreements and Data Integrity Board review (§ 552a(o)-(u))",
            "Report incidents involving PII to CISA within 1 hour and maintain a breach response plan (OMB M-17-12)",
            "Designate a Senior Agency Official for Privacy (OMB A-130)",
        ],
        required_assessments=["E-Government Act § 208 Privacy Impact Assessment (PIA)", "Privacy Threshold Analysis (PTA)", "SORN review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=10,
            rights_request_day_type="business_days",
            identity_verification_required=True,
            breach_regulator_hours=1,
            breach_regulator_text="Report suspected or confirmed breaches/incidents to CISA (US-CERT) within 1 hour of discovery (OMB M-17-12 / FISMA); major incidents to Congress within 7 days",
            breach_individual_text="Per agency breach response plan (OMB M-17-12) following risk-of-harm assessment",
            record_retention_years=5,
        ),
        notification_requirements=["SORN Federal Register publication (30-day comment for routine uses)", "Matching program notice (30 days prior)", "CISA incident report within 1 hour"],
        required_evidence=["Published SORNs", "PIAs and PTAs", "Accounting of disclosures", "Breach response plan", "Computer Matching Agreements"],
        approval_requirements=["Senior Agency Official for Privacy approval of PIAs/SORNs", "Data Integrity Board approval of matching programs"],
        competent_regulator="Office of Management and Budget (OMB) oversight; agency Senior Agency Officials for Privacy; federal courts (civil remedies § 552a(g))",
        domain_category="public_sector",
    )


# ---------------------------------------------------------------------------
# CIRCIA
# ---------------------------------------------------------------------------

def _circia() -> CanonicalRegulation:
    return _fed(
        regulation_id="US-FED-CIRCIA",
        legal_authority="Cybersecurity and Infrastructure Security Agency (CISA), Department of Homeland Security",
        legal_instrument="Cyber Incident Reporting for Critical Infrastructure Act of 2022",
        official_source_url="https://www.cisa.gov/topics/cyber-threats-and-advisories/information-sharing/cyber-incident-reporting-critical-infrastructure-act-2022-circia",
        article_or_section="6 U.S.C. §§ 681-681g (Division Y of the Consolidated Appropriations Act, 2022, Pub. L. 117-103); proposed 6 CFR Part 226 (89 FR 23644, April 4, 2024)",
        effective_date=date(2022, 3, 15),
        applicability_conditions={
            "industry_sectors_any": [
                "chemical", "commercial_facilities", "communications", "critical_manufacturing", "dams", "defense_industrial_base",
                "emergency_services", "energy", "financial_services", "food_and_agriculture", "government_facilities",
                "healthcare", "information_technology", "nuclear", "transportation", "water",
            ],
            "gate_logic": "org_only",
            "notes": (
                "Statute enacted March 15, 2022; reporting obligations commence only on the effective date of CISA's final "
                "rule (6 U.S.C. § 681b(b)). CISA's NPRM (April 2024) proposed covering entities in the 16 critical "
                "infrastructure sectors that exceed SBA small-business size standards or meet sector-based criteria. CISA "
                "announced the final rule would slip to 2026; confirm Federal Register publication and effective date "
                "before treating reporting clocks as live."
            ),
        },
        thresholds=[
            StatutoryThreshold(metric="employee_count_or_revenue", operator=">", value="SBA small business size standard", logic_group="OR", description="Proposed size-based criterion: entities exceeding SBA size standard for their NAICS code, OR meeting any sector-based criterion (proposed 6 CFR § 226.2)."),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="CIRCIA-SUBSTANTIALLY-SIMILAR",
                exemption_type="activity_level",
                condition_field="processing_activities",
                condition_values=["reported_under_substantially_similar_federal_requirement_with_cisa_agreement"],
                carve_out_statute="6 U.S.C. § 681b(a)(5)(B)",
                description="Covered entity need not submit a CIRCIA report if it reports substantially similar information to another federal agency under a CISA information-sharing agreement.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="CIRCIA-CONCURRENT-SECTORAL",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-FED-GLBA-PRIVACY",
                scope_condition="Sector-specific incident reporting (bank 36-hour rule, TSA, NERC CIP, SEC Form 8-K Item 1.05, HIPAA)",
                description="CIRCIA operates alongside sectoral reporting regimes, subject to the substantially-similar-reporting exception.",
            ),
        ],
        organization_types=["private", "public", "critical_infrastructure_entity"],
        industry_sectors=["energy", "healthcare", "financial_services", "communications", "information_technology", "transportation", "water"],
        data_subject_categories=[],
        data_categories=["cyber_incident_data", "ransomware_payment_data"],
        processing_activities=["incident_response", "ransom_payment"],
        required_actions=[
            "Report covered cyber incidents to CISA no later than 72 hours after reasonable belief one occurred (6 U.S.C. § 681b(a)(1))",
            "Report ransom payments made as the result of a ransomware attack no later than 24 hours after payment (§ 681b(a)(2))",
            "Submit supplemental reports promptly when substantial new or different information becomes available (§ 681b(a)(3))",
            "Preserve data relevant to the incident or ransom payment (proposed 2-year retention, § 681b(a)(4))",
            "Third parties (e.g., IR firms, insurers) may submit on behalf of the covered entity (§ 681b(d))",
        ],
        required_assessments=["Covered-entity determination under final CIRCIA rule", "Substantial cyber incident severity assessment"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_hours=72,
            breach_regulator_text="CISA: covered cyber incident within 72 hours of reasonable belief; ransom payment within 24 hours of payment; supplemental reports promptly",
            breach_individual_text="Not applicable (regulator reporting regime)",
            record_retention_years=2,
        ),
        notification_requirements=["CISA covered cyber incident report: 72 hours", "CISA ransom payment report: 24 hours", "Supplemental reports: promptly"],
        required_evidence=["Incident timeline establishing 'reasonable belief' time", "CISA submission confirmations", "Preserved incident data"],
        approval_requirements=["CISO/General Counsel approval of covered-incident determinations", "Executive approval of any ransom payment (OFAC sanctions screening)"],
        competent_regulator="Cybersecurity and Infrastructure Security Agency (CISA)",
        regulatory_status=RegulatoryStatus.ENACTED_NOT_EFFECTIVE,
        deployment_status=DeploymentStatus.TESTED,
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        domain_category="cybersecurity",
    )


def get_us_federal_regulations() -> List[CanonicalRegulation]:
    return [
        _hipaa_privacy(),
        _hipaa_security(),
        _hipaa_breach(),
        _glba(),
        _ftc_act_sec5(),
        _ftc_hbnr(),
        _coppa(),
        _ferpa(),
        _fcra(),
        _privacy_act_1974(),
        _circia(),
    ]
