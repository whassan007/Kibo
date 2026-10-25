"""
KIBO Privacy OS — European Union Regulatory Pack (Agent A3).

Canonical regulations for:
  1. EU-wide instruments (jurisdiction_id="EU"):
       EU-GDPR, EU-EPRIVACY, EU-AI-ACT, EU-NIS2, EU-DORA, EU-EUDPR-LED
  2. All 27 Member States (jurisdiction_id="EU-xx"):
       - one national GDPR implementing-act pack per Member State
       - one national ePrivacy (cookie / direct marketing) transposition pack per Member State
       - specialised sectoral packs for Germany (BDSG, patient/health data, TDDDG),
         France (Loi Informatique et Libertés + CNIL cookie doctrine + HDS) and
         Ireland (Data Protection Act 2018 + Health Research Regulations).

Conventions used in ``applicability_conditions`` (consumed by the JRAE evaluator):
  - ``nexus``: list of territorial connecting factors that can trigger the instrument.
    For the GDPR family this is ALWAYS an Art. 3 nexus (establishment, targeting,
    monitoring, or public-international-law). Nationality or residence of a data
    subject alone is never a trigger (``never_triggered_by``).
  - ``requires_regulation``: regulation_id that must itself be applicable before this
    pack is evaluated (national GDPR opening-clause laws require ``EU-GDPR``).
  - ``member_state_scope``: how the national pack attaches — establishment in the
    Member State, or targeting/monitoring of data subjects located in it.
  - ``trigger_facts``: field names of ``ProcessingActivityInput`` / ``OrganizationProfileInput``
    that make the instrument relevant (e.g. ``involves_targeted_advertising_or_cookies``).
  - ``phased_application``: ISO dates at which obligations start applying (AI Act, DORA).
  - ``citation_confidence``: "high" when every pinpoint citation has been cross-checked
    against the official consolidated text; "verify" when one or more national
    pinpoint citations (listed in ``citations_to_verify``) must be confirmed against the
    official gazette before production reliance. "verify" packs carry
    ``LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF``.

``source_document_hash`` is a deterministic SHA-256 fingerprint of the
(instrument, official URL, rule version) citation tuple. It identifies the citation
the rule was authored against; the ingestion pipeline replaces it with the hash of
the fetched official text when the document is archived.

Deadline conventions: GDPR "one month" (Art. 12(3)) is modelled as 30 calendar days,
and the "two further months" extension as 60 calendar days. Implementations should
compute the actual calendar-month date (CJEU / Regulation 1182/71 on time limits)
where precision matters.
"""

from __future__ import annotations

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

# Art. 3 GDPR nexus — shared by every GDPR-derived pack.
GDPR_ART3_NEXUS = ["establishment_in_eu", "targeting_goods_or_services_to_subjects_in_eu", "monitoring_behaviour_in_eu"]
GDPR_NEVER_TRIGGERED_BY = [
    "data_subject_nationality_alone",
    "data_subject_residence_without_art3_nexus",
    "eu_citizen_located_outside_eu_without_establishment_nexus",
]


def _fingerprint(*parts: str) -> str:
    return "sha256:" + hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _gdpr_deadlines(**overrides: Any) -> ResponseDeadlineSpec:
    base: Dict[str, Any] = dict(
        rights_request_initial_days=30,
        rights_request_day_type="calendar_days",
        rights_request_extension_days=60,
        rights_request_appeal_days=None,
        identity_verification_required=True,
        breach_regulator_hours=72,
        breach_regulator_text=(
            "Without undue delay and, where feasible, not later than 72 hours after becoming aware of "
            "the breach (GDPR Art. 33(1)); reasons for any delay must accompany the notification. "
            "Processor must notify the controller without undue delay (Art. 33(2))."
        ),
        breach_individual_text=(
            "Without undue delay where the breach is likely to result in a high risk to the rights and "
            "freedoms of natural persons (GDPR Art. 34(1)), unless an Art. 34(3) exception applies."
        ),
    )
    base.update(overrides)
    return ResponseDeadlineSpec(**base)


# ---------------------------------------------------------------------------
# 1. EU-WIDE INSTRUMENTS
# ---------------------------------------------------------------------------

def _eu_gdpr() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
    instrument = "Regulation (EU) 2016/679 — General Data Protection Regulation (GDPR)"
    return CanonicalRegulation(
        regulation_id="EU-GDPR",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union (Art. 16 TFEU)",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section=(
            "Arts. 3, 5-6, 8-9, 12-22, 24-28, 30, 32-39, 44-49, 56, 77-83"
        ),
        original_language="en",
        verified_translation="en",
        effective_date=date(2018, 5, 25),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "material_scope": (
                "Processing of personal data wholly or partly by automated means, or non-automated "
                "processing forming part of a filing system (Art. 2(1)); excludes purely personal/household "
                "activity (Art. 2(2)(c)), competent-authority criminal-law processing (LED, Art. 2(2)(d)) and "
                "EU institutions (EUDPR, Art. 2(3))."
            ),
            "nexus": GDPR_ART3_NEXUS + ["public_international_law_art3_3"],
            "art3_1_establishment": (
                "Applies to processing in the context of the activities of an establishment of a controller or "
                "processor in the Union, regardless of whether processing takes place in the Union. An "
                "establishment is any real and effective exercise of activity through stable arrangements "
                "(Recital 22; CJEU C-230/14 Weltimmo, C-131/12 Google Spain)."
            ),
            "art3_2_targeting_or_monitoring": (
                "Non-EU controller/processor is caught only where processing relates to (a) offering goods or "
                "services to data subjects who are in the Union (intent to target — Recital 23 factors: EU "
                "languages/currencies, EU delivery, EU-facing marketing), or (b) monitoring of their behaviour "
                "as far as that behaviour takes place within the Union (tracking/profiling — Recital 24). "
                "Location of the data subject at the time of the triggering activity governs (EDPB Guidelines 3/2018)."
            ),
            "never_triggered_by": GDPR_NEVER_TRIGGERED_BY,
            "trigger_facts": [
                "organization.establishments contains EU or EU-xx",
                "activity.subject_locations contains EU or EU-xx AND activity.targets_goods_or_services_to_subjects",
                "activity.subject_locations contains EU or EU-xx AND activity.monitors_subject_behavior",
            ],
            "art27_representative_required_when": "Art. 3(2) applies and no EU establishment exists",
            "one_stop_shop": (
                "Art. 56: where the controller/processor has a main establishment (Art. 4(16)) in the EU and "
                "engages in cross-border processing, the supervisory authority of the main establishment acts "
                "as Lead Supervisory Authority. Non-EU controllers relying solely on an Art. 27 representative "
                "do NOT benefit from the one-stop-shop and deal with every concerned authority."
            ),
            "child_consent_default_age": 16,
            "child_consent_member_state_floor": 13,
            "citation_confidence": "high",
        },
        thresholds=[
            StatutoryThreshold(
                metric="employee_count",
                operator="<",
                value=250,
                logic_group="AND",
                description=(
                    "Art. 30(5) RoPA derogation for organisations with fewer than 250 employees — available only "
                    "where processing is occasional, not likely to result in a risk, and does not include Art. 9(1) "
                    "special categories or Art. 10 criminal-offence data. In practice rarely available."
                ),
            ),
            StatutoryThreshold(
                metric="administrative_fine_upper_tier_eur",
                operator="==",
                value=20_000_000,
                currency="EUR",
                description="Art. 83(5): up to EUR 20m or 4% of total worldwide annual turnover of the undertaking, whichever is higher.",
            ),
            StatutoryThreshold(
                metric="administrative_fine_lower_tier_eur",
                operator="==",
                value=10_000_000,
                currency="EUR",
                description="Art. 83(4): up to EUR 10m or 2% of total worldwide annual turnover, whichever is higher.",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="GDPR-HOUSEHOLD",
                exemption_type="activity_level",
                condition_field="activity.purpose",
                condition_values=["purely_personal", "household_activity"],
                carve_out_statute="GDPR Art. 2(2)(c)",
                description="Purely personal or household activity by a natural person is outside material scope.",
            ),
            ExemptionRule(
                exemption_id="GDPR-LED-CARVEOUT",
                exemption_type="entity_level",
                condition_field="organization.organization_type",
                condition_values=["law_enforcement_competent_authority"],
                carve_out_statute="GDPR Art. 2(2)(d); Directive (EU) 2016/680",
                description="Processing by competent authorities for criminal-law purposes is governed by the LED (see EU-EUDPR-LED).",
            ),
            ExemptionRule(
                exemption_id="GDPR-EUI-CARVEOUT",
                exemption_type="entity_level",
                condition_field="organization.organization_type",
                condition_values=["eu_institution_body_office_agency"],
                carve_out_statute="GDPR Art. 2(3); Regulation (EU) 2018/1725",
                description="EU institutions, bodies, offices and agencies are governed by the EUDPR (see EU-EUDPR-LED).",
            ),
            ExemptionRule(
                exemption_id="GDPR-ANONYMOUS",
                exemption_type="data_level",
                condition_field="activity.data_categories",
                condition_values=["anonymous_data"],
                carve_out_statute="GDPR Recital 26; CJEU C-413/23 P EDPS v SRB",
                description=(
                    "Truly anonymous information is out of scope. Pseudonymised data remains personal data for any "
                    "party with means reasonably likely to re-identify (relative approach confirmed in C-413/23 P)."
                ),
            ),
            ExemptionRule(
                exemption_id="GDPR-ART27-OCCASIONAL",
                exemption_type="activity_level",
                condition_field="activity.processing_frequency",
                condition_values=["occasional_no_large_scale_special_categories_low_risk"],
                carve_out_statute="GDPR Art. 27(2)(a)",
                description="EU Representative not required for occasional, low-risk processing not involving large-scale Art. 9/10 data, or for public authorities.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="GDPR-OPENING-CLAUSES",
                preempts_or_yields="opening_clause_derogation",
                target_regulation_id="EU-xx national implementing acts",
                scope_condition="Arts. 6(2)-(3), 8(1), 9(4), 23, 85-91",
                description=(
                    "Regulation is directly applicable and preempts conflicting national law, but expressly permits "
                    "Member State specification in opening clauses (child consent age, employment Art. 88, "
                    "health/genetic/biometric Art. 9(4), restrictions Art. 23, national identifiers Art. 87, "
                    "journalism Art. 85, research Art. 89, professional secrecy Art. 90)."
                ),
            ),
            PreemptionRule(
                rule_id="GDPR-EPRIVACY-LEX-SPECIALIS",
                preempts_or_yields="yields_to",
                target_regulation_id="EU-EPRIVACY",
                scope_condition="Storage/access on terminal equipment; publicly available electronic communications services",
                description=(
                    "Art. 95 GDPR: no additional obligations on matters where the ePrivacy Directive imposes specific "
                    "obligations with the same objective. Cookie consent standard is nevertheless the GDPR Art. 4(11)/7 "
                    "standard (CJEU C-673/17 Planet49). Subsequent processing of data collected via cookies is GDPR."
                ),
            ),
        ],
        organization_types=["private", "public", "nonprofit", "healthcare_covered_entity", "financial_institution", "educational_institution", "government_agency"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "employees", "patients", "children", "job_applicants", "customers", "website_visitors", "research_participants"],
        data_categories=[
            "personal_data", "special_category_health", "special_category_genetic", "special_category_biometric",
            "special_category_racial_ethnic", "special_category_political", "special_category_religious",
            "special_category_trade_union", "special_category_sex_life_orientation", "criminal_offence_data",
            "online_identifiers", "location_data",
        ],
        processing_activities=["collection", "profiling", "automated_decision_making", "cross_border_transfer", "direct_marketing", "employee_monitoring", "research"],
        required_actions=[
            "Art. 5 / 24: Implement principles (lawfulness, fairness, transparency, purpose limitation, minimisation, accuracy, storage limitation, integrity/confidentiality) and demonstrate accountability.",
            "Art. 6: Document a lawful basis per purpose; Art. 6(1)(f) legitimate interests requires a three-part Legitimate Interests Assessment (purpose, necessity, balancing — EDPB Guidelines 1/2024; CJEU C-621/22 KNLTB).",
            "Art. 9: Identify an Art. 9(2) condition for special-category data, plus any national Art. 9(4) conditions for genetic/biometric/health data.",
            "Art. 8: Obtain parental authorisation for information-society services offered directly to a child below the applicable Member State age (13-16) where relying on consent; make reasonable verification efforts.",
            "Arts. 12-14: Provide concise, transparent privacy notices at collection (Art. 13) or within one month of indirect collection (Art. 14).",
            "Arts. 15-22: Operationalise access, rectification, erasure, restriction, portability, objection (absolute for direct marketing, Art. 21(3)) and Art. 22 safeguards for solely automated decisions with legal/similarly significant effects (CJEU C-634/21 SCHUFA; C-203/22 Dun & Bradstreet on explanation of logic).",
            "Art. 12(3): Respond to data-subject requests without undue delay and within one month; extendable by two further months for complex/numerous requests with notice to the data subject within the first month.",
            "Art. 25: Data protection by design and by default.",
            "Art. 26: Joint-controller arrangement where purposes and means are jointly determined.",
            "Art. 27: Designate in writing an EU Representative in a Member State where data subjects are located when Art. 3(2) applies.",
            "Art. 28: Execute an Art. 28(3)-compliant Data Processing Agreement with each processor (may use Commission SCCs, Decision (EU) 2021/915); flow down to sub-processors with prior authorisation.",
            "Art. 30: Maintain Records of Processing Activities (controller Art. 30(1); processor Art. 30(2)).",
            "Art. 32: Implement appropriate technical and organisational security measures (pseudonymisation, encryption, resilience, restoration, regular testing).",
            "Art. 33: Notify the competent/lead supervisory authority of a personal data breach within 72 hours unless unlikely to result in a risk; document every breach (Art. 33(5)).",
            "Art. 34: Communicate high-risk breaches to affected data subjects without undue delay.",
            "Art. 35: Conduct a DPIA before likely-high-risk processing (Art. 35(3) cases, national DPIA lists under Art. 35(4), EDPB WP248 nine criteria — two or more criteria normally require a DPIA).",
            "Art. 36: Prior consultation with the supervisory authority where residual high risk remains after DPIA.",
            "Arts. 37-39: Appoint a DPO where (a) public authority/body, (b) core activities involve regular and systematic monitoring on a large scale, or (c) core activities involve large-scale Art. 9/10 data; publish contact details and notify the SA; ensure independence and no conflict of interest (CJEU C-453/21 X-FAB).",
            "Arts. 44-49: Ground every restricted transfer on an adequacy decision (Art. 45), appropriate safeguards (Art. 46 — 2021 SCCs Decision (EU) 2021/914 plus a Transfer Impact Assessment per Schrems II C-311/18 and EDPB Recommendations 01/2020; BCRs Art. 47), or a narrow Art. 49 derogation.",
            "Art. 56: Identify the main establishment and Lead Supervisory Authority for cross-border processing; document the place of central administration / where decisions on purposes and means are taken.",
        ],
        required_assessments=[
            "Record of Processing Activities (Art. 30)",
            "Data Protection Impact Assessment (Art. 35)",
            "Legitimate Interests Assessment (Art. 6(1)(f))",
            "Transfer Impact Assessment (Arts. 44-46, Schrems II)",
            "Lead Supervisory Authority / Main Establishment Determination (Arts. 4(16), 56)",
            "DPO Designation Assessment (Art. 37)",
            "Art. 22 Automated Decision-Making Assessment",
            "Processor Due Diligence (Art. 28(1))",
        ],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=[
            "Supervisory authority: personal data breach within 72 hours of awareness (Art. 33).",
            "Data subjects: high-risk breach without undue delay (Art. 34).",
            "Supervisory authority: DPO contact details (Art. 37(7)).",
            "Supervisory authority: prior consultation where DPIA shows unmitigated high risk (Art. 36); SA responds within 8 weeks (+6 weeks).",
            "Data subjects: notification to recipients of rectification/erasure/restriction (Art. 19).",
        ],
        required_evidence=[
            "RoPA register", "DPIA reports and DPO advice", "LIA records", "Consent records (Art. 7(1))",
            "Signed Art. 28 DPAs and sub-processor list", "Breach register (Art. 33(5))",
            "Executed SCC modules + TIA per transfer", "DSAR log with timestamps and response evidence",
            "DPO appointment and SA notification", "Art. 27 Representative mandate",
            "Main-establishment determination memo",
        ],
        approval_requirements=[
            "DPO consultation on every DPIA (Art. 35(2))",
            "Human approval before any new restricted international transfer",
            "Human approval before Art. 33 regulator filing or deciding a breach is non-notifiable",
            "Human review gate for solely automated decisions with legal or similarly significant effects (Art. 22(3))",
        ],
        competent_regulator="National supervisory authorities (Art. 51) coordinated via the European Data Protection Board (EDPB); Lead Supervisory Authority under Art. 56",
        subnational_regulators={
            "EDPB": "https://www.edpb.europa.eu",
            "consistency_mechanism": "Arts. 60-66 (cooperation, dispute resolution, urgency procedure)",
        },
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.VERIFIED,
        rule_version=RULE_VERSION,
        domain_category="privacy",
    )


def _eu_eprivacy() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/dir/2002/58/oj"
    instrument = "Directive 2002/58/EC — Directive on privacy and electronic communications (ePrivacy Directive), as amended by Directive 2009/136/EC"
    return CanonicalRegulation(
        regulation_id="EU-EPRIVACY",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="Arts. 4, 5(1), 5(3), 6, 9, 13",
        effective_date=date(2003, 10, 31),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "instrument_nature": "Directive — obligations reach controllers through national transposing law (see EU-xx-EPRIVACY packs, EU-DE-TDDDG, EU-FR-LIL).",
            "nexus": ["terminal_equipment_of_users_located_in_eu", "publicly_available_ecs_provided_in_eu"],
            "art5_3_scope": (
                "Any storing of information, or gaining of access to information already stored, in the terminal "
                "equipment of a subscriber or user — cookies, local storage, SDKs, pixels, fingerprinting, device "
                "identifiers — irrespective of whether the information is personal data (CJEU C-673/17 Planet49; "
                "EDPB Guidelines 2/2023 on the technical scope of Art. 5(3))."
            ),
            "exempt_purposes": [
                "sole purpose of carrying out the transmission of a communication over an electronic communications network",
                "strictly necessary to provide an information society service explicitly requested by the subscriber or user",
            ],
            "trigger_facts": ["activity.involves_targeted_advertising_or_cookies", "activity.involves_electronic_marketing"],
            "legislative_note": "The proposed ePrivacy Regulation (COM(2017) 10) was withdrawn by the Commission in its 2025 work programme; the Directive and national transpositions remain the governing law.",
            "citation_confidence": "high",
        },
        exemptions=[
            ExemptionRule(
                exemption_id="EPD-5-3-STRICTLY-NECESSARY",
                exemption_type="activity_level",
                condition_field="activity.cookie_purpose",
                condition_values=["transmission", "strictly_necessary_requested_service", "security", "load_balancing", "shopping_cart", "consent_record"],
                carve_out_statute="Directive 2002/58/EC Art. 5(3) second sentence; WP29 Opinion 04/2012",
                description="No consent required for transmission or strictly necessary storage/access for a service explicitly requested by the user.",
            ),
            ExemptionRule(
                exemption_id="EPD-13-2-SOFT-OPT-IN",
                exemption_type="activity_level",
                condition_field="activity.marketing_relationship",
                condition_values=["existing_customer_similar_products_with_opt_out"],
                carve_out_statute="Directive 2002/58/EC Art. 13(2)",
                description="Email marketing to existing customers for own similar products/services where contact was obtained in a sale and an easy opt-out is offered at collection and in every message.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id="EPD-LEX-SPECIALIS-GDPR",
                preempts_or_yields="preempts",
                target_regulation_id="EU-GDPR",
                scope_condition="Storage/access on terminal equipment; traffic & location data of publicly available ECS",
                description="Art. 5(3) applies as lex specialis (GDPR Art. 95): Art. 6(1)(f) legitimate interest cannot replace required Art. 5(3) consent. Consent quality per GDPR Arts. 4(11) and 7.",
            ),
        ],
        organization_types=["private", "public", "nonprofit", "electronic_communications_provider"],
        industry_sectors=["all", "telecommunications", "digital_services", "adtech", "ecommerce", "media"],
        data_subject_categories=["website_visitors", "app_users", "subscribers", "consumers"],
        data_categories=["online_identifiers", "device_information", "traffic_data", "location_data", "communications_content"],
        processing_activities=["cookies_and_trackers", "targeted_advertising", "analytics", "direct_marketing", "electronic_communications"],
        required_actions=[
            "Art. 5(3): Obtain prior, freely given, specific, informed and unambiguous opt-in consent before setting/reading non-essential cookies or similar technologies; pre-ticked boxes and continued browsing are not consent (Planet49).",
            "Provide clear and comprehensive information on purposes, durations and third-party recipients of trackers before consent.",
            "Make refusing as easy as accepting and withdrawal as easy as giving consent (GDPR Art. 7(3); EDPB Cookie Banner Taskforce Report 2023).",
            "Art. 5(1): Protect confidentiality of communications and related traffic data; no interception or surveillance without user consent or legal authorisation.",
            "Arts. 6 and 9: Erase/anonymise traffic and location data when no longer needed for transmission; value-added services only with consent.",
            "Art. 13: Unsolicited electronic marketing (email, SMS, automated calls) requires prior consent, subject to the Art. 13(2) soft opt-in; disguised sender identity prohibited.",
            "Art. 4(3) + Commission Regulation (EU) No 611/2013: providers of publicly available electronic communications services must notify the competent national authority of personal data breaches within 24 hours of detection where feasible.",
        ],
        required_assessments=["Cookie & Tracker Audit / Consent Management Platform Configuration Review", "Direct Marketing Consent Audit"],
        response_deadlines=ResponseDeadlineSpec(
            breach_regulator_hours=24,
            breach_regulator_text="Providers of publicly available electronic communications services: notify the competent national authority within 24 hours after detection where feasible (Reg. (EU) 611/2013 Art. 2(2)).",
            breach_individual_text="Without undue delay where the breach is likely to adversely affect personal data or privacy of the subscriber or individual (Art. 4(3)).",
            identity_verification_required=False,
        ),
        notification_requirements=["Competent national authority: ECS-provider personal data breach within 24 hours (Reg. 611/2013)."],
        required_evidence=["CMP consent logs (timestamp, banner version, choices)", "Cookie inventory with categories and lifetimes", "Marketing consent and suppression lists"],
        approval_requirements=["Human approval before deploying any new third-party tracker or advertising SDK"],
        competent_regulator="National authorities designated in each Member State's transposition (DPA, telecom regulator or consumer authority — see EU-xx-EPRIVACY packs)",
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        rule_version=RULE_VERSION,
        domain_category="electronic_communications",
    )


def _eu_ai_act() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
    instrument = "Regulation (EU) 2024/1689 — Artificial Intelligence Act (EU AI Act)"
    return CanonicalRegulation(
        regulation_id="EU-AI-ACT",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union (Arts. 16 and 114 TFEU)",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="Arts. 2, 4, 5, 6, 9-17, 26, 27, 43, 49, 50, 51-55, 72-73, 99; Annexes I and III",
        effective_date=date(2024, 8, 1),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "nexus": [
                "provider_placing_on_market_or_putting_into_service_in_eu",
                "deployer_established_or_located_in_eu",
                "third_country_provider_or_deployer_where_ai_output_is_used_in_eu",
            ],
            "roles": ["provider", "deployer", "importer", "distributor", "authorised_representative", "product_manufacturer"],
            "phased_application": {
                "entry_into_force": "2024-08-01",
                "prohibitions_and_ai_literacy_arts_4_5": "2025-02-02",
                "gpai_obligations_governance_penalties": "2025-08-02",
                "general_application_incl_annex_iii_high_risk_and_art_50": "2026-08-02",
                "annex_i_product_safety_high_risk_art_6_1": "2027-08-02",
                "legacy_gpai_models_placed_before_2025_08_02": "2027-08-02",
            },
            "pending_amendment": (
                "Digital Omnibus on AI (Commission proposal COM(2025) 836, 19 Nov 2025) proposes linking the start of "
                "high-risk obligations to availability of harmonised standards with long-stop dates (Annex III: "
                "2 Dec 2027; Annex I: 2 Aug 2028). Confirm adoption status and Official Journal publication before "
                "relying on deferred dates; until then the 2026-08-02 date in the adopted text governs."
            ),
            "high_risk_annex_iii_areas": {
                "1_biometrics": "remote biometric identification (non-verification), biometric categorisation by sensitive attributes, emotion recognition",
                "2_critical_infrastructure": "safety components in critical digital infrastructure, road traffic, water, gas, heating, electricity",
                "3_education": "admission/access, evaluating learning outcomes, assessing appropriate level of education, proctoring",
                "4_employment": "recruitment/selection (targeted job ads, CV filtering, candidate evaluation); decisions on promotion, termination, task allocation, monitoring and evaluating performance",
                "5_essential_services": (
                    "(a) eligibility for public assistance benefits including healthcare services; (b) creditworthiness / credit "
                    "scoring (except fraud detection); (c) risk assessment and pricing in life and health insurance; (d) evaluating "
                    "and classifying emergency calls, emergency dispatch and emergency healthcare patient triage systems"
                ),
                "6_law_enforcement": "victim risk, polygraphs, evidence reliability, re-offending risk, profiling",
                "7_migration_asylum_border": "risk assessment, application examination, detection/identification",
                "8_justice_democracy": "assisting judicial authorities in researching/interpreting facts and law; influencing elections",
            },
            "healthcare_classification_note": (
                "Emergency patient triage is expressly Annex III 5(d). AI that is a medical device or safety component "
                "under the MDR (EU) 2017/745 / IVDR (EU) 2017/746 requiring notified-body assessment is high-risk via "
                "Art. 6(1) + Annex I. Administrative patient scheduling is NOT listed per se — classify as high-risk only "
                "where it determines access/eligibility to healthcare services (Annex III 5(a)) or forms part of triage; "
                "otherwise document a non-high-risk assessment under Art. 6(3)-(4) and register it (Art. 49(2))."
            ),
            "art6_3_derogation": "Annex III system is not high-risk where it does not pose a significant risk of harm (narrow procedural task, improving prior human activity, detecting decision patterns without replacing review, preparatory task) — never available where the system performs profiling of natural persons.",
            "trigger_facts": ["activity.involves_ai_or_admt", "activity.involves_biometrics"],
            "distinct_from_gdpr": "AI Act obligations are cumulative with — not a substitute for — GDPR Art. 22 / Art. 35 obligations (Art. 2(7)).",
            "citation_confidence": "high",
        },
        thresholds=[
            StatutoryThreshold(metric="administrative_fine_prohibited_practices_eur", operator="==", value=35_000_000, currency="EUR", description="Art. 99(3): prohibited practices — up to EUR 35m or 7% of worldwide annual turnover, whichever is higher (lower of the two for SMEs, Art. 99(6))."),
            StatutoryThreshold(metric="administrative_fine_operator_obligations_eur", operator="==", value=15_000_000, currency="EUR", description="Art. 99(4): other operator obligations — up to EUR 15m or 3%."),
            StatutoryThreshold(metric="administrative_fine_incorrect_information_eur", operator="==", value=7_500_000, currency="EUR", description="Art. 99(5): incorrect, incomplete or misleading information — up to EUR 7.5m or 1%."),
            StatutoryThreshold(metric="gpai_training_compute_flops", operator=">", value=1e25, description="Art. 51(2): GPAI model presumed to have systemic risk when cumulative training compute exceeds 10^25 FLOPs."),
        ],
        exemptions=[
            ExemptionRule(exemption_id="AIA-MILITARY", exemption_type="activity_level", condition_field="activity.purpose", condition_values=["military", "defence", "national_security"], carve_out_statute="AI Act Art. 2(3)", description="Systems exclusively for military, defence or national security purposes are excluded."),
            ExemptionRule(exemption_id="AIA-RESEARCH", exemption_type="activity_level", condition_field="activity.purpose", condition_values=["scientific_research_and_development_sole_purpose"], carve_out_statute="AI Act Art. 2(6)", description="AI developed and put into service for the sole purpose of scientific research and development is excluded."),
            ExemptionRule(exemption_id="AIA-PERSONAL-USE", exemption_type="entity_level", condition_field="organization.organization_type", condition_values=["natural_person_non_professional"], carve_out_statute="AI Act Art. 2(10)", description="Deployers who are natural persons using AI in a purely personal non-professional activity are excluded."),
            ExemptionRule(exemption_id="AIA-OPEN-SOURCE", exemption_type="activity_level", condition_field="activity.ai_licence", condition_values=["free_and_open_source_not_high_risk_not_art5_not_art50"], carve_out_statute="AI Act Art. 2(12)", description="Free and open-source AI components are excluded unless placed on the market as high-risk, prohibited, or Art. 50 systems."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="AIA-GDPR-CUMULATIVE", preempts_or_yields="concurrent_with", target_regulation_id="EU-GDPR", scope_condition="AI systems processing personal data", description="Art. 2(7): AI Act is without prejudice to the GDPR; DPIA (GDPR Art. 35) and FRIA (AI Act Art. 27) are both required where triggered; the FRIA may complement an existing DPIA (Art. 27(4))."),
            PreemptionRule(rule_id="AIA-MDR-SECTORAL", preempts_or_yields="concurrent_with", target_regulation_id="EU-MDR-IVDR", scope_condition="AI medical devices", description="Annex I Section A products (MDR/IVDR) undergo a single conformity assessment integrating AI Act requirements (Art. 43(3))."),
        ],
        organization_types=["private", "public", "government_agency", "healthcare_covered_entity", "financial_institution", "educational_institution"],
        industry_sectors=["all", "healthcare", "financial_services", "insurance", "education", "employment_hr", "public_sector", "critical_infrastructure", "law_enforcement"],
        data_subject_categories=["consumers", "patients", "employees", "job_applicants", "students", "credit_applicants", "insured_persons", "citizens"],
        data_categories=["personal_data", "special_category_biometric", "special_category_health", "behavioural_data", "financial_data"],
        processing_activities=["ai_system_deployment", "automated_decision_making", "profiling", "biometric_identification", "emotion_recognition", "generative_ai", "patient_triage", "credit_scoring", "recruitment_screening"],
        required_actions=[
            "Art. 4 (from 2 Feb 2025): Providers and deployers must take measures to ensure a sufficient level of AI literacy of staff and other persons operating AI on their behalf.",
            "Art. 5 (from 2 Feb 2025): Do not place on the market or use prohibited practices — subliminal/manipulative or deceptive techniques causing significant harm; exploiting vulnerabilities (age, disability, socio-economic situation); social scoring; predicting criminal offences solely on profiling/personality traits; untargeted scraping of facial images to build facial-recognition databases; emotion recognition in the workplace and education (save medical/safety); biometric categorisation inferring race, political opinions, trade-union membership, religion, sex life or sexual orientation; real-time remote biometric identification in public spaces for law enforcement save Art. 5(1)(h) exceptions.",
            "Art. 6 + Annex III: Classify every AI use case; document Art. 6(3) non-high-risk assessments and register them (Art. 49(2)).",
            "Providers of high-risk AI (Arts. 9-17): risk-management system, data governance (Art. 10, incl. bias examination with special-category data under Art. 10(5) safeguards), technical documentation (Annex IV), automatic logging, transparency/instructions for use, human oversight design, accuracy/robustness/cybersecurity, quality-management system, conformity assessment (Art. 43), EU declaration of conformity, CE marking, EU database registration (Art. 49).",
            "Deployers of high-risk AI (Art. 26): use per instructions, assign competent human oversight, ensure relevant and representative input data, monitor operation, keep logs at least 6 months, inform workers' representatives and affected workers before workplace use, inform natural persons subject to decisions, suspend use and inform provider/authority on serious incident.",
            "Art. 27 Fundamental Rights Impact Assessment: required before first use by deployers that are bodies governed by public law or private entities providing public services (e.g. hospitals, schools, public healthcare), and by any deployer of Annex III 5(b) credit-scoring or 5(c) life/health insurance pricing systems; notify the market surveillance authority of the results.",
            "Art. 86: Affected persons have a right to a clear and meaningful explanation of the role of a high-risk Annex III system in decisions with legal or similarly significant effects.",
            "Art. 50 (from 2 Aug 2026): inform persons they are interacting with an AI system; mark synthetic audio/image/video/text outputs in machine-readable form; deployers must disclose deep fakes and AI-generated text published on matters of public interest; inform persons exposed to emotion recognition or biometric categorisation.",
            "Arts. 53-55: GPAI model providers — technical documentation, downstream information, copyright policy and training-content summary; systemic-risk models additionally evaluations, adversarial testing, serious-incident reporting and cybersecurity (GPAI Code of Practice, July 2025).",
            "Art. 72-73: Post-market monitoring; report serious incidents to market surveillance authorities immediately after establishing a causal link and no later than 15 days; 2 days for widespread infringement or critical-infrastructure disruption; 10 days in the event of death.",
        ],
        required_assessments=[
            "AI System Inventory & Risk Classification (Art. 6 / Annex III)",
            "Prohibited Practices Screening (Art. 5)",
            "Fundamental Rights Impact Assessment (FRIA, Art. 27)",
            "Conformity Assessment (Art. 43) — providers of high-risk AI",
            "AI Literacy Programme Assessment (Art. 4)",
            "Transparency Obligation Mapping (Art. 50)",
            "GDPR DPIA for AI processing personal data (GDPR Art. 35 — cumulative)",
        ],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=None,
            identity_verification_required=False,
            breach_regulator_days=15,
            breach_regulator_text="Serious incident: report to market surveillance authority immediately after establishing a causal link, and not later than 15 days; 2 days for widespread infringement / critical-infrastructure disruption; 10 days where death occurred (Art. 73).",
            breach_individual_text="Deployers must inform affected natural persons of high-risk AI use in decisions concerning them (Art. 26(11)); explanation on request (Art. 86).",
            record_retention_years=10,
        ),
        notification_requirements=[
            "Market surveillance authority: serious incidents (Art. 73) — 15 / 10 / 2 day limits.",
            "Market surveillance authority: FRIA results via the AI Office template (Art. 27(3)).",
            "Workers' representatives and affected workers: before putting high-risk AI into service at the workplace (Art. 26(7)).",
            "AI Office: GPAI systemic-risk notification within 2 weeks of meeting the threshold (Art. 52(1)).",
        ],
        required_evidence=[
            "AI inventory with risk tier and role per system", "Art. 6(3) non-high-risk assessment records",
            "FRIA reports", "Technical documentation (Annex IV) and EU declaration of conformity", "Deployer logs (>= 6 months, Art. 26(6))",
            "AI literacy training records", "Human-oversight assignment records", "Serious-incident log",
            "Provider documentation retention 10 years after placing on market (Art. 18)",
        ],
        approval_requirements=[
            "Human sign-off before deploying any Annex III high-risk AI system",
            "FRIA approval before first use where Art. 27 applies",
            "Immediate escalation for any Art. 5 prohibited-practice hit — deployment blocked",
            "Human oversight assignment (Art. 14 / 26(2)) with authority to override or stop the system",
        ],
        competent_regulator="European AI Office (GPAI) & national market surveillance authorities and notifying authorities designated under Art. 70; European Artificial Intelligence Board (Art. 65)",
        subnational_regulators={"AI Office": "https://digital-strategy.ec.europa.eu/en/policies/ai-office"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        rule_version=RULE_VERSION,
        domain_category="ai_governance",
    )


def _eu_nis2() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/dir/2022/2555/oj"
    instrument = "Directive (EU) 2022/2555 — measures for a high common level of cybersecurity across the Union (NIS2 Directive)"
    return CanonicalRegulation(
        regulation_id="EU-NIS2",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="Arts. 2-3, 20, 21, 23, 26-27, 32-34; Annexes I and II",
        effective_date=date(2024, 10, 18),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "instrument_nature": "Directive — transposition deadline 17 Oct 2024; measures apply from 18 Oct 2024. Several Member States transposed late; check national law status for each establishment.",
            "nexus": ["establishment_in_member_state", "main_establishment_for_digital_infrastructure_and_digital_providers_art26"],
            "jurisdiction_rule": "Entities fall under the Member State where established (Art. 26(1)); DNS, TLD, cloud, data centre, CDN, MSP/MSSP, online marketplaces, search engines and social networks fall under the Member State of main establishment; non-EU such providers must designate a representative.",
            "annex_i_sectors_high_criticality": ["energy", "transport", "banking", "financial_market_infrastructure", "health", "drinking_water", "waste_water", "digital_infrastructure", "ict_service_management_b2b", "public_administration", "space"],
            "annex_ii_other_critical_sectors": ["postal_and_courier", "waste_management", "chemicals", "food", "manufacturing_medical_devices_computers_electronics_machinery_vehicles", "digital_providers", "research"],
            "health_sector_entities": "Healthcare providers; EU reference laboratories; entities carrying out R&D of medicinal products; manufacturers of basic pharmaceutical products; manufacturers of critical medical devices during a public health emergency.",
            "size_cap_rule": "Applies to medium-sized and large enterprises (Commission Recommendation 2003/361/EC) in Annex I/II sectors; certain entities (qualified trust service providers, TLD registries, DNS providers, public ECN/ECS providers, sole-provider/critical entities) regardless of size.",
            "essential_vs_important": "Essential: large Annex I entities, qualified TSPs, TLD/DNS, critical entities under CER Directive, central government; Important: other in-scope Annex I/II entities.",
            "trigger_facts": ["organization.industry", "organization.employee_count", "organization.annual_revenue_usd"],
            "citation_confidence": "high",
        },
        thresholds=[
            StatutoryThreshold(metric="employee_count", operator=">=", value=50, logic_group="OR", description="Medium-sized enterprise threshold (>= 50 staff) — Art. 2(1) size-cap."),
            StatutoryThreshold(metric="annual_turnover_eur", operator=">", value=10_000_000, currency="EUR", logic_group="OR", description="Medium-sized enterprise threshold: annual turnover and balance sheet > EUR 10m."),
            StatutoryThreshold(metric="employee_count", operator=">=", value=250, logic_group="ESSENTIAL_OR", description="Large enterprise (>= 250 staff) in Annex I sector => essential entity."),
            StatutoryThreshold(metric="annual_turnover_eur", operator=">", value=50_000_000, currency="EUR", logic_group="ESSENTIAL_AND", description="Large enterprise: turnover > EUR 50m AND balance sheet > EUR 43m => essential entity in Annex I."),
            StatutoryThreshold(metric="administrative_fine_essential_eur", operator="==", value=10_000_000, currency="EUR", description="Art. 34(4): essential entities — at least up to EUR 10m or 2% of worldwide annual turnover, whichever is higher."),
            StatutoryThreshold(metric="administrative_fine_important_eur", operator="==", value=7_000_000, currency="EUR", description="Art. 34(5): important entities — at least up to EUR 7m or 1.4% of worldwide annual turnover, whichever is higher."),
        ],
        exemptions=[
            ExemptionRule(exemption_id="NIS2-SMALL-MICRO", exemption_type="entity_level", condition_field="organization.employee_count", condition_values=["<50_and_turnover_<=10m"], carve_out_statute="NIS2 Art. 2(1)-(2)", description="Small and micro enterprises are out of scope unless listed in Art. 2(2) (size-independent categories)."),
            ExemptionRule(exemption_id="NIS2-NATSEC", exemption_type="entity_level", condition_field="organization.organization_type", condition_values=["national_security", "defence", "law_enforcement", "judiciary", "parliament", "central_bank"], carve_out_statute="NIS2 Art. 2(7)-(8)", description="Public administration entities carrying out activities in national security, defence, law enforcement, judiciary, parliaments and central banks are excluded."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="NIS2-DORA-LEX-SPECIALIS", preempts_or_yields="yields_to", target_regulation_id="EU-DORA", scope_condition="Financial entities within DORA Art. 2", description="NIS2 Art. 4: sector-specific Union acts with at least equivalent effect (DORA, Recital 28) displace NIS2 risk-management and reporting obligations for financial entities."),
            PreemptionRule(rule_id="NIS2-GDPR-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="EU-GDPR", scope_condition="Significant incidents that are also personal data breaches", description="NIS2 incident reporting does not replace GDPR Art. 33; competent authorities cooperate with DPAs (Art. 35). Run both clocks in parallel."),
        ],
        organization_types=["private", "public", "government_agency", "healthcare_covered_entity"],
        industry_sectors=["energy", "transport", "banking", "health", "digital_infrastructure", "ict_service_management", "public_administration", "manufacturing", "digital_providers", "postal", "chemicals", "food", "research", "water", "space", "waste"],
        data_subject_categories=["service_recipients"],
        data_categories=["network_and_information_systems"],
        processing_activities=["ict_operations", "incident_response", "supply_chain_management"],
        required_actions=[
            "Art. 20: Management bodies must approve cybersecurity risk-management measures, oversee implementation, follow training, and can be held liable.",
            "Art. 21(2): Implement all-hazards measures: risk analysis and IS policies; incident handling; business continuity, backup and crisis management; supply-chain security; secure acquisition/development incl. vulnerability handling; effectiveness assessment; cyber hygiene and training; cryptography/encryption; HR security, access control and asset management; MFA/continuous authentication and secured communications.",
            "Art. 23(4)(a): Submit an early warning to the CSIRT/competent authority within 24 hours of becoming aware of a significant incident (indicating suspected unlawful/malicious cause and cross-border impact).",
            "Art. 23(4)(b): Submit an incident notification within 72 hours of awareness with initial assessment of severity, impact and indicators of compromise.",
            "Art. 23(4)(c)-(d): Provide intermediate reports on request; submit a final report no later than one month after the incident notification (or a progress report if ongoing, with final report within one month of handling).",
            "Art. 23(1): Inform recipients of services, without undue delay, of significant incidents likely to adversely affect service provision; communicate measures and remedies for significant cyber threats (Art. 23(2)).",
            "Art. 3(4) / 27: Register with the national competent authority (entity list; digital infrastructure providers in the ENISA registry).",
            "Commission Implementing Regulation (EU) 2024/2690: apply detailed technical/methodological requirements and significance thresholds for digital infrastructure and digital providers.",
        ],
        required_assessments=["NIS2 Scope & Entity Classification (Essential/Important)", "Cybersecurity Risk Assessment (Art. 21)", "ICT Supply-Chain Risk Assessment", "Significant Incident Classification"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=None,
            identity_verification_required=False,
            breach_regulator_hours=24,
            breach_regulator_days=30,
            breach_regulator_text="Early warning within 24h of awareness; incident notification within 72h; final report within 1 month of the incident notification (Art. 23(4)).",
            breach_individual_text="Notify service recipients without undue delay where the significant incident is likely to adversely affect service provision (Art. 23(1)).",
        ),
        notification_requirements=[
            "CSIRT / competent authority: early warning 24h, notification 72h, final report 1 month (Art. 23).",
            "Service recipients: significant incidents and cyber threats (Art. 23(1)-(2)).",
            "Competent authority: registration of entity details and changes within 2 weeks (Art. 3(4), Art. 27).",
        ],
        required_evidence=["Board approval minutes for cybersecurity measures", "Management training records", "Incident register with timestamps", "Supplier security assessments", "Business continuity and backup test results"],
        approval_requirements=["Management-body approval of risk-management measures (Art. 20)", "Human approval of significance classification and regulatory filing"],
        competent_regulator="National competent authorities and CSIRTs designated per Member State (Art. 8, 10); NIS Cooperation Group; ENISA; EU-CyCLONe",
        subnational_regulators={"ENISA": "https://www.enisa.europa.eu"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        rule_version=RULE_VERSION,
        domain_category="cybersecurity",
    )


def _eu_dora() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/reg/2022/2554/oj"
    instrument = "Regulation (EU) 2022/2554 — Digital Operational Resilience Act (DORA)"
    return CanonicalRegulation(
        regulation_id="EU-DORA",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="Arts. 2, 5-16, 17-23, 24-27, 28-30, 31-44, 45",
        effective_date=date(2025, 1, 17),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "nexus": ["eu_authorised_financial_entity", "ict_third_party_provider_designated_critical"],
            "in_scope_entities_art2_1": [
                "credit_institutions", "payment_institutions", "account_information_service_providers", "electronic_money_institutions",
                "investment_firms", "crypto_asset_service_providers_and_art_issuers", "central_securities_depositories", "central_counterparties",
                "trading_venues", "trade_repositories", "aifms", "ucits_management_companies", "data_reporting_service_providers",
                "insurance_and_reinsurance_undertakings", "insurance_intermediaries", "iorps", "credit_rating_agencies",
                "critical_benchmark_administrators", "crowdfunding_service_providers", "securitisation_repositories", "ict_third_party_service_providers",
            ],
            "phased_application": {"entry_into_force": "2023-01-16", "application": "2025-01-17", "first_ctpp_designations": "2025-11-18"},
            "proportionality": "Art. 4 proportionality; Art. 16 simplified ICT risk-management framework for small/non-interconnected investment firms, exempt payment/e-money institutions and small IORPs; microenterprise relief in several articles.",
            "level_2_texts": [
                "Commission Delegated Regulation (EU) 2024/1774 (RTS ICT risk-management framework)",
                "Commission Delegated Regulation (EU) 2024/1772 (RTS incident classification)",
                "Commission Delegated Regulation (EU) 2025/301 (RTS incident reporting content and time limits)",
                "Commission Implementing Regulation (EU) 2025/302 (ITS incident reporting templates)",
                "Commission Implementing Regulation (EU) 2024/2956 (ITS register of information)",
                "Commission Delegated Regulation (EU) 2025/1190 (RTS threat-led penetration testing)",
            ],
            "trigger_facts": ["organization.organization_type == financial_institution", "organization.industry in financial_services/insurance/crypto"],
            "citation_confidence": "verify",
            "citations_to_verify": ["Delegated Regulation number for TLPT RTS (2025/1190)"],
        },
        exemptions=[
            ExemptionRule(exemption_id="DORA-ART2-3", exemption_type="entity_level", condition_field="organization.organization_type", condition_values=["aifm_under_art3_2_aifmd", "small_insurance_undertaking_art4_solvency_ii", "iorp_<=15_members", "microenterprise_insurance_intermediary", "post_office_giro"], carve_out_statute="DORA Art. 2(3)", description="Listed small/exempted entities are outside scope."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="DORA-LEX-SPECIALIS-NIS2", preempts_or_yields="preempts", target_regulation_id="EU-NIS2", scope_condition="Financial entities", description="DORA is lex specialis to NIS2 for ICT risk management, incident reporting, testing and information sharing (DORA Art. 1(2); NIS2 Art. 4)."),
            PreemptionRule(rule_id="DORA-GDPR-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="EU-GDPR", scope_condition="Major ICT incidents involving personal data", description="DORA incident reporting runs in parallel with GDPR Art. 33 notification."),
        ],
        organization_types=["financial_institution", "ict_third_party_service_provider"],
        industry_sectors=["banking", "payments", "investment_services", "insurance", "crypto_assets", "asset_management", "market_infrastructure"],
        data_subject_categories=["clients", "customers"],
        data_categories=["network_and_information_systems", "financial_data"],
        processing_activities=["ict_operations", "ict_outsourcing", "incident_response", "resilience_testing"],
        required_actions=[
            "Arts. 5-6: Management body defines, approves, oversees and is accountable for the ICT risk-management framework; documented digital operational resilience strategy.",
            "Arts. 7-16: Identify ICT assets and dependencies, protection & prevention, detection, response & recovery (ICT business continuity and backup policies), learning & evolving, crisis communication.",
            "Arts. 17-18: ICT-related incident management process; classify incidents using RTS (EU) 2024/1772 criteria (clients, duration, geographic spread, data losses, criticality of services, economic impact).",
            "Art. 19 + RTS (EU) 2025/301: Report major ICT-related incidents to the competent authority — initial notification within 4 hours of classification as major and no later than 24 hours from awareness; intermediate report within 72 hours of the initial notification; final report within 1 month of the latest intermediate report.",
            "Art. 19(3): Inform affected clients without undue delay of major ICT-related incidents affecting their financial interests.",
            "Arts. 24-27: Digital operational resilience testing programme; threat-led penetration testing (TLPT) at least every 3 years for entities identified by competent authorities.",
            "Art. 28: Manage ICT third-party risk; maintain and report the Register of Information on all ICT third-party contractual arrangements; pre-contract due diligence; exit strategies.",
            "Art. 30: Include mandatory contractual provisions in ICT service contracts (service description, data location, availability/integrity, audit and access rights, termination rights; enhanced terms for critical or important functions).",
            "Arts. 31-44: Cooperate with Lead Overseer oversight where an ICT provider is designated a critical ICT third-party service provider (CTPP).",
            "Art. 45: Optional cyber-threat information-sharing arrangements, notified to competent authorities.",
        ],
        required_assessments=["ICT Risk Assessment (Arts. 6-8)", "ICT Third-Party Concentration Risk Assessment (Art. 29)", "Major ICT Incident Classification (Art. 18)", "Digital Operational Resilience Testing / TLPT (Arts. 24-27)", "Register of Information (Art. 28(3))"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=None,
            identity_verification_required=False,
            breach_regulator_hours=4,
            breach_regulator_days=30,
            breach_regulator_text="Initial notification within 4h of classification as major and no later than 24h of awareness; intermediate report within 72h of initial notification; final report within 1 month of the latest intermediate report (RTS (EU) 2025/301).",
            breach_individual_text="Inform clients without undue delay where the major incident has an impact on their financial interests (Art. 19(3)).",
            record_retention_years=5,
        ),
        notification_requirements=[
            "Competent authority: major ICT-related incidents — 4h/24h initial, 72h intermediate, 1-month final.",
            "Competent authority: voluntary notification of significant cyber threats (Art. 19(2)).",
            "Competent authority: annual Register of Information submission (Art. 28(3)).",
            "Competent authority: planned contracts for ICT services supporting critical or important functions (Art. 28(3)).",
        ],
        required_evidence=["Management body ICT risk approvals", "ICT risk-management framework documentation", "Register of Information", "Incident classification and reports", "Testing and TLPT reports", "ICT contracts with Art. 30 clauses", "Exit plans"],
        approval_requirements=["Management-body approval of ICT risk-management framework and ICT third-party policy", "Human approval before engaging an ICT provider for critical or important functions", "Human approval of major-incident classification and filing"],
        competent_regulator="National competent authorities (Art. 46) — e.g. ECB/SSM, national central banks, financial supervisors; ESAs (EBA, EIOPA, ESMA) as Lead Overseers for CTPPs",
        subnational_regulators={"EBA": "https://www.eba.europa.eu", "EIOPA": "https://www.eiopa.europa.eu", "ESMA": "https://www.esma.europa.eu"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        rule_version=RULE_VERSION,
        domain_category="cybersecurity",
    )


def _eu_eudpr_led() -> CanonicalRegulation:
    url = "https://eur-lex.europa.eu/eli/reg/2018/1725/oj"
    instrument = (
        "Regulation (EU) 2018/1725 — protection of natural persons with regard to the processing of personal data by the "
        "Union institutions, bodies, offices and agencies (EUDPR); and Directive (EU) 2016/680 — Law Enforcement Directive (LED)"
    )
    return CanonicalRegulation(
        regulation_id="EU-EUDPR-LED",
        jurisdiction_id="EU",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        legal_authority="European Parliament and Council of the European Union",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, "https://eur-lex.europa.eu/eli/dir/2016/680/oj", RULE_VERSION),
        article_or_section="EUDPR Arts. 2-3, 14-24, 31, 34-35, 39, 43-45, 46-51; LED Arts. 1-2, 4, 8, 10, 12-18, 24-25, 27, 30-31, 32-34, 35-40",
        effective_date=date(2018, 12, 11),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "eudpr_scope": "All processing by EU institutions, bodies, offices and agencies (EUIs); Chapter IX for operational data of Europol/Eurojust/EPPO-type bodies subject to their founding acts.",
            "led_scope": "Processing by competent authorities for the prevention, investigation, detection or prosecution of criminal offences or execution of criminal penalties, including safeguarding against threats to public security. Transposition deadline 6 May 2018; obligations reach through national law.",
            "nexus": ["eu_institution_body_office_agency", "member_state_competent_authority_criminal_law_purpose", "processor_acting_for_eui_or_competent_authority"],
            "trigger_facts": ["organization.organization_type in (eu_institution_body_office_agency, law_enforcement_competent_authority, government_agency)", "organization.role == processor for an EUI or competent authority"],
            "led_effective_date": "2018-05-06",
            "citation_confidence": "high",
        },
        exemptions=[
            ExemptionRule(exemption_id="LED-NON-CRIMINAL-PURPOSE", exemption_type="activity_level", condition_field="activity.purpose", condition_values=["administrative", "commercial", "hr"], carve_out_statute="LED Art. 9(1)-(2)", description="Competent-authority processing for non-criminal purposes reverts to the GDPR."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="EUDPR-GDPR-PARALLEL", preempts_or_yields="preempts", target_regulation_id="EU-GDPR", scope_condition="EU institutions", description="GDPR Art. 2(3): EUDPR governs EUI processing; interpreted homogeneously with the GDPR (EUDPR Recital 5)."),
            PreemptionRule(rule_id="LED-GDPR-CARVEOUT", preempts_or_yields="preempts", target_regulation_id="EU-GDPR", scope_condition="Competent authorities, criminal-law purposes", description="GDPR Art. 2(2)(d): LED national law applies instead of the GDPR."),
        ],
        organization_types=["eu_institution_body_office_agency", "law_enforcement_competent_authority", "government_agency", "processor_to_public_body"],
        industry_sectors=["public_sector", "law_enforcement", "justice"],
        data_subject_categories=["staff", "citizens", "suspects", "convicted_persons", "victims", "witnesses"],
        data_categories=["personal_data", "criminal_offence_data", "special_category_biometric", "special_category_genetic"],
        processing_activities=["law_enforcement", "public_administration", "staff_management"],
        required_actions=[
            "EUDPR Art. 31: Maintain central register of records of processing (public).",
            "EUDPR Art. 34: Notify the EDPS of personal data breaches within 72 hours; Art. 35 communication to data subjects for high risk.",
            "EUDPR Arts. 39-40: DPIA and prior consultation of the EDPS.",
            "EUDPR Arts. 43-45: Mandatory DPO in every EUI.",
            "EUDPR Arts. 14-24: Data-subject rights within one month, extendable by two further months.",
            "EUDPR Chapter V (Arts. 46-51): international transfers on adequacy, appropriate safeguards or derogations.",
            "LED Art. 4/8: Processing necessary for a task carried out by a competent authority and based on Union or Member State law.",
            "LED Art. 6: Distinguish between categories of data subjects (suspects, convicted persons, victims, witnesses).",
            "LED Art. 10: Special categories only where strictly necessary, with appropriate safeguards, and authorised by law.",
            "LED Arts. 12-18: Information, access, rectification and erasure — rights may be restricted and exercised indirectly through the supervisory authority (Art. 17).",
            "LED Art. 25: Logging of collection, alteration, consultation, disclosure, combination and erasure in automated processing systems.",
            "LED Art. 27: DPIA for high-risk processing; Art. 28 prior consultation.",
            "LED Art. 30: Notify the supervisory authority of breaches within 72 hours; Art. 31 data-subject communication.",
            "LED Art. 32: Designate a DPO (courts acting in judicial capacity may be exempted).",
            "LED Arts. 35-40: Transfers to third countries only to competent authorities with adequacy, appropriate safeguards or specific derogations.",
        ],
        required_assessments=["EUDPR DPIA (Art. 39)", "LED DPIA (Art. 27)", "Logging Compliance Review (LED Art. 25)", "Data Subject Category Classification (LED Art. 6)"],
        response_deadlines=_gdpr_deadlines(
            breach_regulator_text="EUDPR Art. 34: notify EDPS within 72 hours; LED Art. 30: notify national supervisory authority within 72 hours.",
        ),
        notification_requirements=["EDPS: EUI breaches within 72h", "National supervisory authority: LED breaches within 72h", "EDPS / SA: prior consultation where DPIA shows high risk"],
        required_evidence=["Central register of records (EUDPR Art. 31)", "LED processing logs", "DPIA reports", "Breach register", "DPO designation"],
        approval_requirements=["DPO consultation on DPIA", "Legal-basis verification against Union or Member State law before any LED processing"],
        competent_regulator="European Data Protection Supervisor (EDPS) for EUIs; national supervisory authorities for LED (Art. 41 LED)",
        subnational_regulators={"EDPS": "https://www.edps.europa.eu"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        rule_version=RULE_VERSION,
        domain_category="public_sector",
    )


# ---------------------------------------------------------------------------
# 2. MEMBER STATE VARIATIONS (GDPR opening clauses + ePrivacy transpositions)
# ---------------------------------------------------------------------------

EU_MEMBER_STATE_VARIATIONS: Dict[str, Dict[str, Any]] = {
    "EU-AT": {
        "name": "Austria", "iso2": "AT", "original_language": "de", "pack_id": "EU-AT-DSG",
        "national_statute": "Datenschutzgesetz (DSG), BGBl. I Nr. 165/1999, as amended by the Datenschutz-Anpassungsgesetz 2018 (BGBl. I Nr. 120/2017) and the Datenschutz-Deregulierungs-Gesetz 2018 (BGBl. I Nr. 24/2018)",
        "statute_url": "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=10001597",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Österreichische Datenschutzbehörde (DSB)", "authority_url": "https://www.dsb.gv.at",
        "child_digital_consent_age": 14, "child_age_basis": "§ 4(4) DSG",
        "employment_rules": [
            "§§ 96(1) Z 3 and 96a ArbVG: control measures affecting human dignity and systems for automated processing of employee data require a works agreement (Betriebsvereinbarung); without a works council, individual employee consent (§ 10 AVRAG).",
            "GDPR Art. 88: no general employment-data statute; DSB and Supreme Court (OGH) case law on proportionality of monitoring.",
        ],
        "health_biometric_genetic_derogations": [
            "Gesundheitstelematikgesetz 2012 (GTelG 2012) — ELGA electronic health record with opt-out rights and access logging.",
            "Gentechnikgesetz (GTG) §§ 65-71: genetic analyses for medical purposes; prohibition on employers and insurers requesting or using genetic test results (§ 67 GTG).",
            "Forschungsorganisationsgesetz (FOG) § 2d: research processing safeguards under GDPR Art. 89.",
        ],
        "national_identifier_rules": "Area-specific personal identifiers (bPK) under the E-Government-Gesetz.",
        "notable_features": ["§ 1 DSG constitutional fundamental right to data protection, which also protects legal persons.", "DPIA blacklist/whitelist: DSFA-V and DSFA-AV regulations."],
        "eprivacy_cookie_law": "Telekommunikationsgesetz 2021 (TKG 2021), § 165(3) — storage/access on terminal equipment only with informed consent unless strictly necessary.",
        "eprivacy_cookie_authority": "Österreichische Datenschutzbehörde (DSB)",
        "direct_marketing_law": "TKG 2021 § 174 — prior consent for marketing calls, email and SMS; soft opt-in for existing customers (§ 174(4)); ECG-Liste (RTR opt-out list) for email.",
        "citation_confidence": "high",
    },
    "EU-BE": {
        "name": "Belgium", "iso2": "BE", "original_language": "fr/nl/de", "pack_id": "EU-BE-DPA2018",
        "national_statute": "Law of 30 July 2018 on the protection of natural persons with regard to the processing of personal data (Loi relative à la protection des personnes physiques à l'égard des traitements de données à caractère personnel); Law of 3 December 2017 establishing the Data Protection Authority",
        "statute_url": "https://www.ejustice.just.fgov.be/eli/loi/2018/07/30/2018040581/justel",
        "effective_date": date(2018, 9, 5),
        "supervisory_authority": "Autorité de protection des données / Gegevensbeschermingsautoriteit (APD/GBA)", "authority_url": "https://www.dataprotectionauthority.be",
        "child_digital_consent_age": 13, "child_age_basis": "Art. 7 Law of 30 July 2018",
        "employment_rules": [
            "Collective Labour Agreement (CCT/CAO) No. 81 of 26 April 2002: monitoring of online electronic communications — legitimate purposes, proportionality, prior information and individualisation procedure.",
            "CCT/CAO No. 68 of 16 June 1998: camera surveillance at the workplace.",
            "Law of 21 March 2007 regulating the installation and use of surveillance cameras.",
            "CCT/CAO No. 39: information and consultation on new technologies.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 9 Law of 30 July 2018: controllers processing genetic, biometric or health data must designate categories of persons with access, keep that list available to the APD/GBA, and bind those persons by confidentiality.",
            "Law of 22 August 2002 on patients' rights: patient access to the medical record.",
            "Law of 21 August 2008 establishing the eHealth platform; Information Security Committee (Comité de sécurité de l'information) deliberations for health-data exchange.",
        ],
        "national_identifier_rules": "National Register number use restricted to authorised entities (Law of 8 August 1983 on the National Register, Art. 8).",
        "notable_features": ["Art. 10 Law of 30 July 2018: criminal-offence data processing permitted in listed cases."],
        "eprivacy_cookie_law": "Law of 13 June 2005 on electronic communications, Art. 10/2 (formerly Art. 129) — prior consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Autorité de protection des données / Gegevensbeschermingsautoriteit (APD/GBA)",
        "direct_marketing_law": "Code of Economic Law Book XII, Art. XII.13 and Royal Decree of 4 April 2003 — opt-in for email marketing; 'Do Not Call Me' register for telemarketing.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Renumbering of the cookie provision from Art. 129 to Art. 10/2 of the Law of 13 June 2005"],
    },
    "EU-BG": {
        "name": "Bulgaria", "iso2": "BG", "original_language": "bg", "pack_id": "EU-BG-PDPA",
        "national_statute": "Personal Data Protection Act (Закон за защита на личните данни, ZZLD), as amended by State Gazette No. 17 of 26 February 2019",
        "statute_url": "https://www.cpdp.bg/en/index.php?p=element&aid=1194",
        "effective_date": date(2019, 3, 2),
        "supervisory_authority": "Commission for Personal Data Protection (CPDP)", "authority_url": "https://www.cpdp.bg",
        "child_digital_consent_age": 14, "child_age_basis": "Art. 25c PDPA",
        "employment_rules": [
            "PDPA Ch. 6 (Arts. 25g-25i): employer may copy identity documents only where required by law; must adopt rules and procedures for whistleblowing systems, restrictions on use of internal resources and access-control/working-time/labour-discipline systems, and inform employees.",
            "Labour Code: proportionality of employee monitoring.",
        ],
        "health_biometric_genetic_derogations": [
            "Health Act (Закон за здравето) Arts. 27-28: health information confidentiality and permitted disclosures.",
            "PDPA Art. 25e: rules for processing of national identification numbers (EGN) when publishing personal data.",
        ],
        "national_identifier_rules": "Unified Civil Number (EGN) — restricted public disclosure (PDPA Art. 25e).",
        "notable_features": ["PDPA Art. 25h: processing for journalism, academic, artistic and literary expression with balancing criteria."],
        "eprivacy_cookie_law": "Electronic Communications Act (Закон за електронните съобщения), Art. 4a — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Commission for Personal Data Protection (CPDP)",
        "direct_marketing_law": "Electronic Commerce Act Art. 6 — unsolicited commercial email; Commission for Consumer Protection register.",
        "citation_confidence": "verify",
        "citations_to_verify": ["PDPA Art. 25g-25i employer provisions numbering", "PDPA Art. 25e EGN publication rule", "E-Commerce Act Art. 6"],
    },
    "EU-HR": {
        "name": "Croatia", "iso2": "HR", "original_language": "hr", "pack_id": "EU-HR-GDPR-IMPL",
        "national_statute": "Act on the Implementation of the General Data Protection Regulation (Zakon o provedbi Opće uredbe o zaštiti podataka), Narodne novine 42/2018",
        "statute_url": "https://narodne-novine.nn.hr/clanci/sluzbeni/2018_05_42_805.html",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Croatian Personal Data Protection Agency (AZOP)", "authority_url": "https://azop.hr",
        "child_digital_consent_age": 16, "child_age_basis": "Art. 19 Implementation Act",
        "employment_rules": [
            "Implementation Act Arts. 25-32: video surveillance — workplace surveillance only where conditions of Art. 6 GDPR and the Act are met, with prior notice to employees and not in rest rooms, toilets or changing rooms.",
            "Implementation Act Art. 23: biometric data of employees may be processed for working-time records and entry/exit only with the employee's explicit consent.",
            "Labour Act (Zakon o radu) Art. 29: employee personal data only where necessary for labour-law purposes.",
        ],
        "health_biometric_genetic_derogations": [
            "Implementation Act Art. 20: processing of genetic data to calculate disease or other health risks in life-insurance contracts is prohibited.",
            "Implementation Act Arts. 21-22: biometric processing by public authorities only where provided by law; by private entities where prescribed by law or necessary for protection of persons, property, classified information or business secrets.",
        ],
        "national_identifier_rules": "Personal identification number (OIB) under the Personal Identification Number Act.",
        "notable_features": ["Art. 47: no administrative fines on public authorities."],
        "eprivacy_cookie_law": "Electronic Communications Act (Zakon o elektroničkim komunikacijama), Narodne novine 76/2022 — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Croatian Personal Data Protection Agency (AZOP) / Croatian Regulatory Authority for Network Industries (HAKOM)",
        "direct_marketing_law": "Electronic Communications Act (NN 76/2022) and Consumer Protection Act — opt-in for electronic marketing; soft opt-in for existing customers.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Cookie article number in ZEK NN 76/2022", "Authority split between AZOP and HAKOM for cookies"],
    },
    "EU-CY": {
        "name": "Cyprus", "iso2": "CY", "original_language": "el", "pack_id": "EU-CY-L125-2018",
        "national_statute": "Law providing for the Protection of Natural Persons with regard to the Processing of Personal Data and for the Free Movement of such Data, Law 125(I)/2018",
        "statute_url": "https://www.dataprotection.gov.cy",
        "effective_date": date(2018, 7, 31),
        "supervisory_authority": "Office of the Commissioner for Personal Data Protection", "authority_url": "https://www.dataprotection.gov.cy",
        "child_digital_consent_age": 14, "child_age_basis": "Art. 8 Law 125(I)/2018",
        "employment_rules": ["No specific employment statute; Commissioner guidance on employee monitoring and CCTV applies GDPR Art. 6/88 proportionality."],
        "health_biometric_genetic_derogations": [
            "Art. 9 Law 125(I)/2018: processing of genetic and biometric data for health and life insurance purposes is prohibited.",
            "Art. 10: DPIA plus prior consultation with the Commissioner for processing of special categories for public-interest research.",
        ],
        "national_identifier_rules": "Identity card number processing per Commissioner guidance.",
        "notable_features": ["Combination of filing systems by public authorities requires DPIA and prior consultation (Art. 10)."],
        "eprivacy_cookie_law": "Law 112(I)/2004 on the Regulation of Electronic Communications and Postal Services, Art. 99 — consent for cookies.",
        "eprivacy_cookie_authority": "Office of the Commissioner for Personal Data Protection",
        "direct_marketing_law": "Law 112(I)/2004 Art. 106 — opt-in for unsolicited electronic communications.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Law 112(I)/2004 Arts. 99 and 106 numbering", "Law 125(I)/2018 Art. 10 content"],
    },
    "EU-CZ": {
        "name": "Czechia", "iso2": "CZ", "original_language": "cs", "pack_id": "EU-CZ-ZZOU",
        "national_statute": "Act No. 110/2019 Coll., on Personal Data Processing (zákon o zpracování osobních údajů)",
        "statute_url": "https://www.zakonyprolidi.cz/cs/2019-110",
        "effective_date": date(2019, 4, 24),
        "supervisory_authority": "Office for Personal Data Protection (ÚOOÚ)", "authority_url": "https://www.uoou.cz",
        "child_digital_consent_age": 15, "child_age_basis": "§ 7 Act No. 110/2019 Coll.",
        "employment_rules": [
            "Labour Code (Act No. 262/2006 Coll.) § 316: employer may not intrude on employee privacy by open or hidden surveillance, interception or checking of correspondence without a serious reason arising from the nature of the employer's activity; employees must be directly informed of scope and methods.",
        ],
        "health_biometric_genetic_derogations": [
            "Act No. 372/2011 Coll. on Health Services: medical records content, retention and access.",
            "§ 66 Act No. 372/2011 Coll.: confidentiality of healthcare information.",
        ],
        "national_identifier_rules": "Birth number (rodné číslo) under Act No. 133/2000 Coll. on Population Register.",
        "notable_features": ["Public bodies are not subject to administrative fines (§ 62(5))."],
        "eprivacy_cookie_law": "Act No. 127/2005 Coll. on Electronic Communications, § 89(3) — opt-in consent for cookies since 1 January 2022 (previously opt-out).",
        "eprivacy_cookie_authority": "Office for Personal Data Protection (ÚOOÚ)",
        "direct_marketing_law": "Act No. 480/2004 Coll. on Certain Information Society Services, § 7 — prior consent for commercial communications by electronic means; soft opt-in for existing customers.",
        "citation_confidence": "high",
    },
    "EU-DK": {
        "name": "Denmark", "iso2": "DK", "original_language": "da", "pack_id": "EU-DK-DBL",
        "national_statute": "Databeskyttelsesloven — Act No. 502 of 23 May 2018 on supplementary provisions to the GDPR (Danish Data Protection Act)",
        "statute_url": "https://www.retsinformation.dk/eli/lta/2018/502",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Datatilsynet (Danish Data Protection Agency)", "authority_url": "https://www.datatilsynet.dk",
        "child_digital_consent_age": 13, "child_age_basis": "§ 6(2) Databeskyttelsesloven",
        "employment_rules": [
            "§ 12 Databeskyttelsesloven: processing of Art. 6/9 data in employment where necessary for labour-law obligations or rights, or based on consent under Art. 7.",
            "Danish employer-employee practice: collective agreements (e.g. DA/LO control-measures agreement) require prior notice of control measures (generally 6 weeks).",
        ],
        "health_biometric_genetic_derogations": [
            "§ 7 Databeskyttelsesloven: special categories processing under Art. 9(2) conditions, incl. public-authority tasks.",
            "§ 10: research and statistics on special categories where significant societal importance; disclosure only with Datatilsynet permission in certain cases.",
            "Sundhedsloven (Health Act) Ch. 9: patient confidentiality and access to health information.",
        ],
        "national_identifier_rules": "§ 11 Databeskyttelsesloven: CPR number processing by private controllers only where legally required, with consent, or under listed conditions; public authorities for unambiguous identification.",
        "notable_features": ["Datatilsynet cannot impose fines directly — fines are imposed by courts after police referral (§ 41)."],
        "eprivacy_cookie_law": "Executive Order No. 1148 of 9 December 2011 on information and consent required when storing or accessing information in end-user terminal equipment (Cookiebekendtgørelsen).",
        "eprivacy_cookie_authority": "Digitaliseringsstyrelsen (Agency for Digital Government) for the Cookie Order; Datatilsynet for GDPR-standard consent and subsequent processing",
        "direct_marketing_law": "Markedsføringsloven (Marketing Practices Act) § 10 — prior consent for electronic marketing; soft opt-in under § 10(2); CPR Robinson list.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Current competent authority for the Cookie Order (Digitaliseringsstyrelsen vs Erhvervsstyrelsen)"],
    },
    "EU-EE": {
        "name": "Estonia", "iso2": "EE", "original_language": "et", "pack_id": "EU-EE-IKS",
        "national_statute": "Personal Data Protection Act (Isikuandmete kaitse seadus), RT I, 04.01.2019, 11",
        "statute_url": "https://www.riigiteataja.ee/en/eli/523012019001/consolide",
        "effective_date": date(2019, 1, 15),
        "supervisory_authority": "Estonian Data Protection Inspectorate (Andmekaitse Inspektsioon, AKI)", "authority_url": "https://www.aki.ee",
        "child_digital_consent_age": 13, "child_age_basis": "§ 8 Personal Data Protection Act",
        "employment_rules": [
            "Employment Contracts Act § 28(2) item 11: employer must respect employee privacy and verify performance only in a manner that does not violate privacy.",
            "§ 11 Personal Data Protection Act: video surveillance and processing of data in public interest considerations.",
        ],
        "health_biometric_genetic_derogations": [
            "Health Services Organisation Act and Health Information System statutes: national e-health record.",
            "Human Genes Research Act: Estonian Biobank (gene donor consent and confidentiality).",
            "§ 6 Personal Data Protection Act: scientific and historical research safeguards incl. ethics committee approval.",
        ],
        "national_identifier_rules": "Personal identification code (isikukood) widely used; proportionality required for private-sector collection.",
        "notable_features": ["Administrative fines applied through misdemeanour procedure (Estonia's legal system, GDPR Recital 151)."],
        "eprivacy_cookie_law": "Electronic Communications Act (Elektroonilise side seadus) — transposition of ePrivacy Art. 5(3) for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Estonian Data Protection Inspectorate (AKI)",
        "direct_marketing_law": "Information Society Services Act § 6 — prior consent for commercial email; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Section number of Art. 5(3) transposition in the Electronic Communications Act", "ISSA § 6"],
    },
    "EU-FI": {
        "name": "Finland", "iso2": "FI", "original_language": "fi/sv", "pack_id": "EU-FI-TSL",
        "national_statute": "Data Protection Act (Tietosuojalaki 1050/2018)",
        "statute_url": "https://www.finlex.fi/fi/laki/ajantasa/2018/20181050",
        "effective_date": date(2019, 1, 1),
        "supervisory_authority": "Office of the Data Protection Ombudsman (Tietosuojavaltuutetun toimisto)", "authority_url": "https://tietosuoja.fi",
        "child_digital_consent_age": 13, "child_age_basis": "§ 5 Data Protection Act",
        "employment_rules": [
            "Act on the Protection of Privacy in Working Life (759/2004): necessity requirement (§ 3) — only data directly necessary for the employment relationship; rules on drug testing, camera surveillance, email retrieval and personality/aptitude testing.",
            "Act on Co-operation within Undertakings (1333/2021): co-operation negotiations before introducing technical monitoring.",
        ],
        "health_biometric_genetic_derogations": [
            "Act on the Secondary Use of Health and Social Data (552/2019): Findata permit authority for secondary use.",
            "Act on the Status and Rights of Patients (785/1992) and Act on Electronic Processing of Client Data in Healthcare and Social Welfare (784/2021, Kanta services).",
            "§ 6 Data Protection Act: Art. 9(2) derogations incl. insurance and healthcare providers.",
        ],
        "national_identifier_rules": "§ 29 Data Protection Act: personal identity code processing only with consent, legal basis, or where necessary for unambiguous identification in listed cases.",
        "notable_features": ["Sanctions Board (seuraamuskollegio) within the Ombudsman office imposes administrative fines; no fines on public authorities (§ 24)."],
        "eprivacy_cookie_law": "Act on Electronic Communications Services (Laki sähköisen viestinnän palveluista 917/2014), § 205 — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Finnish Transport and Communications Agency (Traficom)",
        "direct_marketing_law": "Act on Electronic Communications Services (917/2014) § 200 — opt-in for direct marketing to natural persons; soft opt-in; opt-out for legal persons.",
        "citation_confidence": "high",
    },
    "EU-FR": {
        "name": "France", "iso2": "FR", "original_language": "fr", "pack_id": "EU-FR-LIL",
        "national_statute": "Loi n° 78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés (Loi Informatique et Libertés), as amended by Loi n° 2018-493 du 20 juin 2018 and Ordonnance n° 2018-1125 du 12 décembre 2018",
        "statute_url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000886460",
        "effective_date": date(2019, 6, 1),
        "supervisory_authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)", "authority_url": "https://www.cnil.fr",
        "child_digital_consent_age": 15, "child_age_basis": "Art. 45 Loi Informatique et Libertés (below 15: joint consent of child and holder(s) of parental authority)",
        "employment_rules": [
            "Code du travail L.1121-1 (proportionality of restrictions on employee rights), L.1222-4 (no data collection by a device not previously brought to the employee's attention), L.2312-38 (CSE consultation on means of monitoring employee activity).",
            "CNIL référentiel on HR management (2019) and guidance on teleworking surveillance.",
        ],
        "health_biometric_genetic_derogations": [
            "Arts. 64-77 LIL: health data processing regime — reference methodologies (MR-001 to MR-006), CNIL authorisation, Health Data Hub / SNDS access.",
            "Code de la santé publique L.1111-8: certified health data hosting (HDS).",
            "Art. 6 III LIL and CNIL biometric workplace référentiel (2019): biometric access control limited to justified cases.",
            "Code civil Art. 16-10 and Code de la santé publique: genetic testing only for medical or research purposes with express consent.",
        ],
        "national_identifier_rules": "Décret n° 2019-341: NIR (social security number) processing restricted to listed purposes/controllers (Art. 30 LIL).",
        "notable_features": ["Art. 85 LIL: post-mortem directives on personal data.", "Simplified sanction procedure (Art. 22-1 LIL) for minor cases up to EUR 20,000."],
        "eprivacy_cookie_law": "Art. 82 Loi Informatique et Libertés; CNIL Délibérations n° 2020-091 (guidelines) and n° 2020-092 (recommendation) of 17 September 2020.",
        "eprivacy_cookie_authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        "direct_marketing_law": "Code des postes et des communications électroniques L.34-5 — opt-in for B2C email/SMS; soft opt-in; Bloctel opposition list for telephone canvassing (Code de la consommation L.223-1).",
        "specialized_packs": ["EU-FR-LIL"],
        "citation_confidence": "high",
    },
    "EU-DE": {
        "name": "Germany", "iso2": "DE", "original_language": "de", "pack_id": "EU-DE-BDSG",
        "national_statute": "Bundesdatenschutzgesetz (BDSG) of 30 June 2017 (BGBl. I S. 2097), as amended",
        "statute_url": "https://www.gesetze-im-internet.de/bdsg_2018/",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI) & 17 Länder authorities (§ 40 BDSG)", "authority_url": "https://www.bfdi.bund.de",
        "child_digital_consent_age": 16, "child_age_basis": "GDPR Art. 8(1) default (no German derogation)",
        "employment_rules": [
            "§ 26 BDSG: employment-related processing; consent in employment only where freely given (§ 26(2)); works agreements as legal basis (§ 26(4)).",
            "CJEU C-34/21 (30 March 2023): national rule identical to § 26(1) sentence 1 BDSG is not a 'more specific rule' under Art. 88 unless it meets Art. 88(2); controllers should rely on GDPR Art. 6(1)(b)/(c)/(f) directly.",
            "§ 87(1) No. 6 BetrVG: works council co-determination on technical devices capable of monitoring employee behaviour or performance.",
        ],
        "health_biometric_genetic_derogations": [
            "§ 22 BDSG: special-category processing for social security, preventive/occupational medicine, health care and public health with § 22(2) technical and organisational measures.",
            "§ 203 StGB: professional secrecy for physicians and other professionals.",
            "Gendiagnostikgesetz (GenDG): genetic testing restrictions, ban on insurers (§ 18 GenDG) and employers (§ 19 GenDG) requiring or using genetic tests.",
        ],
        "national_identifier_rules": "No general national ID number; tax ID (§ 139b AO) use restricted by purpose.",
        "notable_features": ["§ 38 BDSG DPO threshold (>= 20 persons).", "Federal/Länder split of supervisory competence."],
        "eprivacy_cookie_law": "Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz (TDDDG) § 25",
        "eprivacy_cookie_authority": "Länder DPAs (digital services) / BfDI (telecommunications providers)",
        "direct_marketing_law": "Gesetz gegen den unlauteren Wettbewerb (UWG) § 7 — unreasonable nuisance: prior express consent for telephone (B2C) and electronic mail advertising; soft opt-in § 7(3); consent documentation for telephone marketing § 7a UWG.",
        "specialized_packs": ["EU-DE-BDSG", "EU-DE-PATIENT-HEALTH", "EU-DE-TDDDG"],
        "citation_confidence": "high",
    },
    "EU-GR": {
        "name": "Greece", "iso2": "GR", "original_language": "el", "pack_id": "EU-GR-L4624-2019",
        "national_statute": "Law 4624/2019 — Hellenic Data Protection Authority, implementing measures of the GDPR and transposition of Directive (EU) 2016/680",
        "statute_url": "https://www.dpa.gr",
        "effective_date": date(2019, 8, 29),
        "supervisory_authority": "Hellenic Data Protection Authority (HDPA)", "authority_url": "https://www.dpa.gr",
        "child_digital_consent_age": 15, "child_age_basis": "Art. 21 Law 4624/2019",
        "employment_rules": [
            "Art. 27 Law 4624/2019: employment-context processing where necessary for the employment contract; consent assessed against dependency; CCTV in the workplace only where necessary for protection of persons and property.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 23 Law 4624/2019: processing of genetic data for health and life insurance purposes is prohibited.",
            "Art. 22: special categories processing for social security, preventive medicine, healthcare, public health with safeguards.",
        ],
        "national_identifier_rules": "AMKA (social security number) and AFM (tax ID) use subject to purpose limitation.",
        "notable_features": ["HDPA declared several provisions of Law 4624/2019 incompatible with the GDPR (Opinion 1/2020)."],
        "eprivacy_cookie_law": "Law 3471/2006 on protection of personal data and privacy in the electronic communications sector, Art. 4(5) — prior consent for cookies.",
        "eprivacy_cookie_authority": "Hellenic Data Protection Authority (HDPA)",
        "direct_marketing_law": "Law 3471/2006 Art. 11 — opt-in for unsolicited electronic communications; telephone opt-out registry (Art. 11 registry maintained by providers).",
        "citation_confidence": "high",
    },
    "EU-HU": {
        "name": "Hungary", "iso2": "HU", "original_language": "hu", "pack_id": "EU-HU-INFOTV",
        "national_statute": "Act CXII of 2011 on the Right of Informational Self-Determination and on Freedom of Information (Infotv.), as amended by Act XXXVIII of 2018",
        "statute_url": "https://njt.hu/jogszabaly/2011-112-00-00",
        "effective_date": date(2018, 7, 26),
        "supervisory_authority": "National Authority for Data Protection and Freedom of Information (NAIH)", "authority_url": "https://www.naih.hu",
        "child_digital_consent_age": 16, "child_age_basis": "GDPR Art. 8(1) default (no Hungarian derogation)",
        "employment_rules": [
            "Labour Code (Act I of 2012) §§ 9-11: employee personality rights; employer may monitor only work-related conduct, with prior information; §§ 11/A: monitoring of IT devices provided for work.",
        ],
        "health_biometric_genetic_derogations": [
            "Act XLVII of 1997 on the Processing and Protection of Health Care Data and Related Personal Data (Eüaktv.).",
            "Act XXI of 2008 on the protection of human genetic data and regulation of human genetic studies.",
        ],
        "national_identifier_rules": "Act XX of 1996: personal identification number use restricted; sector-specific identification codes (TAJ, tax ID).",
        "notable_features": ["Infotv. § 61: NAIH fines; data-protection procedures conducted under the General Administrative Procedures Act."],
        "eprivacy_cookie_law": "Act C of 2003 on Electronic Communications, § 155(4) — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "National Authority for Data Protection and Freedom of Information (NAIH)",
        "direct_marketing_law": "Act XLVIII of 2008 on Basic Requirements and Certain Restrictions of Commercial Advertising, § 6 — prior express consent for direct advertising.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Labour Code § 11/A numbering"],
    },
    "EU-IE": {
        "name": "Ireland", "iso2": "IE", "original_language": "en/ga", "pack_id": "EU-IE-DPA2018",
        "national_statute": "Data Protection Act 2018 (Number 7 of 2018)",
        "statute_url": "https://www.irishstatutebook.ie/eli/2018/act/7/enacted/en/html",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Data Protection Commission (DPC)", "authority_url": "https://www.dataprotection.ie",
        "child_digital_consent_age": 16, "child_age_basis": "Section 31 Data Protection Act 2018",
        "employment_rules": [
            "Section 46 DPA 2018: special-category processing necessary for employment and social-welfare law obligations or rights.",
            "No specific workplace-monitoring statute; DPC guidance on CCTV and employee monitoring; Workplace Relations Commission for employment disputes.",
        ],
        "health_biometric_genetic_derogations": [
            "Section 52 DPA 2018: processing for health purposes (preventive/occupational medicine, medical diagnosis, health/social care) by health practitioners or persons under equivalent confidentiality.",
            "Health Research Regulations 2018 (S.I. No. 314 of 2018), as amended by S.I. No. 18 of 2021: explicit consent for health research or a consent declaration from the Health Research Consent Declaration Committee (HRCDC).",
            "Disability Act 2005 Part 4: restrictions on genetic testing in employment and insurance.",
        ],
        "national_identifier_rules": "Personal Public Service Number (PPSN) use restricted to specified bodies (Social Welfare Consolidation Act 2005, s. 262).",
        "notable_features": ["DPC acts as Lead Supervisory Authority for many multinational technology companies with EU main establishment in Ireland.", "Section 141: fines on public bodies capped at EUR 1,000,000 unless acting as undertakings."],
        "eprivacy_cookie_law": "European Communities (Electronic Communications Networks and Services) (Privacy and Electronic Communications) Regulations 2011 (S.I. No. 336 of 2011), Regulation 5",
        "eprivacy_cookie_authority": "Data Protection Commission (DPC)",
        "direct_marketing_law": "S.I. No. 336 of 2011, Regulation 13 — opt-in for email/SMS marketing to individuals; soft opt-in limited to 12 months since last sale; National Directory Database opt-out for telephone.",
        "specialized_packs": ["EU-IE-DPA2018"],
        "citation_confidence": "high",
    },
    "EU-IT": {
        "name": "Italy", "iso2": "IT", "original_language": "it", "pack_id": "EU-IT-CODICE",
        "national_statute": "Codice in materia di protezione dei dati personali — D.Lgs. 30 giugno 2003, n. 196, as amended by D.Lgs. 10 agosto 2018, n. 101",
        "statute_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-06-30;196",
        "effective_date": date(2018, 9, 19),
        "supervisory_authority": "Garante per la protezione dei dati personali (Garante)", "authority_url": "https://www.garanteprivacy.it",
        "child_digital_consent_age": 14, "child_age_basis": "Art. 2-quinquies Codice",
        "employment_rules": [
            "Art. 4 Statuto dei Lavoratori (L. 300/1970), referenced by Art. 114 Codice: audiovisual and other remote-monitoring equipment only for organisational, production, safety or asset-protection needs, subject to union agreement or Labour Inspectorate authorisation; work tools exempt but adequate information required.",
            "Art. 113 Codice and Art. 8 Statuto: prohibition on inquiries into employee opinions and facts irrelevant to aptitude.",
            "Art. 88 Codice: processing in the employment context per Garante ethics rules.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 2-septies Codice: genetic, biometric and health data processed only in compliance with Garante safeguard measures (misure di garanzia); genetic data cannot be disseminated.",
            "Art. 2-sexies Codice: substantial public interest processing by public bodies.",
            "Arts. 110-110-bis Codice: medical/biomedical research and secondary use safeguards.",
        ],
        "national_identifier_rules": "Codice fiscale usage per sector rules.",
        "notable_features": [
            "Legge 23 settembre 2025, n. 132 (national AI law): parental consent required for minors under 14 to access AI technologies; sector rules for AI in healthcare and employment, complementing the EU AI Act.",
            "Art. 2-terdecies: post-mortem exercise of rights by heirs or persons with a legitimate interest.",
        ],
        "eprivacy_cookie_law": "Art. 122 Codice; Garante Guidelines on cookies and other tracking tools of 10 June 2021 (scrolling is not consent; banner 'X' closure means refusal; re-prompt no earlier than 6 months).",
        "eprivacy_cookie_authority": "Garante per la protezione dei dati personali (Garante)",
        "direct_marketing_law": "Art. 130 Codice — opt-in for automated calls, email, SMS; soft opt-in (Art. 130(4)); Registro Pubblico delle Opposizioni (extended to mobile numbers from 27 July 2022) for telemarketing.",
        "citation_confidence": "high",
    },
    "EU-LV": {
        "name": "Latvia", "iso2": "LV", "original_language": "lv", "pack_id": "EU-LV-FPDAL",
        "national_statute": "Personal Data Processing Law (Fizisko personu datu apstrādes likums), Latvijas Vēstnesis 132, 04.07.2018",
        "statute_url": "https://likumi.lv/ta/en/en/id/300099",
        "effective_date": date(2018, 7, 5),
        "supervisory_authority": "Data State Inspectorate (Datu valsts inspekcija, DVI)", "authority_url": "https://www.dvi.gov.lv",
        "child_digital_consent_age": 13, "child_age_basis": "Section 33 Personal Data Processing Law",
        "employment_rules": ["Labour Law Section 94: employer may request and process employee data only as necessary for the employment relationship."],
        "health_biometric_genetic_derogations": [
            "Law on the Rights of Patients: confidentiality and access to medical records.",
            "Human Genome Research Law: genome database and gene donor consent.",
        ],
        "national_identifier_rules": "Personal code (personas kods) processing per purpose limitation.",
        "notable_features": ["Section 25: research processing safeguards."],
        "eprivacy_cookie_law": "Law on Information Society Services, Section 7(2) — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Data State Inspectorate (DVI)",
        "direct_marketing_law": "Law on Information Society Services, Section 9 — prior consent for commercial communications by email; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Law on Information Society Services Sections 7 and 9", "Labour Law Section 94"],
    },
    "EU-LT": {
        "name": "Lithuania", "iso2": "LT", "original_language": "lt", "pack_id": "EU-LT-ADTAI",
        "national_statute": "Law on Legal Protection of Personal Data (Asmens duomenų teisinės apsaugos įstatymas, ADTAĮ), as amended by Law No. XIII-1426 of 30 June 2018",
        "statute_url": "https://e-seimas.lrs.lt",
        "effective_date": date(2018, 7, 16),
        "supervisory_authority": "State Data Protection Inspectorate (Valstybinė duomenų apsaugos inspekcija, VDAI)", "authority_url": "https://vdai.lrv.lt",
        "child_digital_consent_age": 14, "child_age_basis": "Art. 6 ADTAĮ",
        "employment_rules": [
            "Art. 4 ADTAĮ: processing of candidate/employee criminal-record data only as permitted by law; Art. 5: video and audio monitoring of employees at the workplace only with prior written information and under strict conditions; employees' homes and private spaces excluded.",
        ],
        "health_biometric_genetic_derogations": [
            "Law on the Rights of Patients and Compensation for Damage to Health: confidentiality of health information.",
            "Law on Ethics of Biomedical Research: research consent.",
        ],
        "national_identifier_rules": "Art. 3 ADTAĮ: personal code (asmens kodas) may not be made public; processing for direct marketing prohibited.",
        "notable_features": ["Inspectorate of Journalist Ethics supervises processing for journalistic purposes."],
        "eprivacy_cookie_law": "Law on Electronic Communications, Art. 61(3) — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "State Data Protection Inspectorate (VDAI)",
        "direct_marketing_law": "Law on Electronic Communications, Art. 69 — prior consent for electronic direct marketing; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Law on Electronic Communications Arts. 61(3) and 69 numbering"],
    },
    "EU-LU": {
        "name": "Luxembourg", "iso2": "LU", "original_language": "fr/de/lb", "pack_id": "EU-LU-LAW2018",
        "national_statute": "Law of 1 August 2018 on the organisation of the National Data Protection Commission and the general data protection framework",
        "statute_url": "https://legilux.public.lu/eli/etat/leg/loi/2018/08/01/a686/jo",
        "effective_date": date(2018, 8, 20),
        "supervisory_authority": "Commission Nationale pour la Protection des Données (CNPD)", "authority_url": "https://cnpd.public.lu",
        "child_digital_consent_age": 16, "child_age_basis": "GDPR Art. 8(1) default (no Luxembourg derogation)",
        "employment_rules": [
            "Labour Code Art. L.261-1: workplace surveillance only for listed purposes (safety/health, protection of company assets, production process control, temporary performance control, flexible working time); prior information to employees and staff delegation; co-decision for certain purposes (Art. L.211-8 / L.414-9).",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 64 Law of 1 August 2018: research and statistics processing with additional safeguards (DPO, pseudonymisation, access restrictions).",
            "Law of 24 July 2014 on patients' rights and obligations.",
        ],
        "national_identifier_rules": "National identification number under the Law of 19 June 2013.",
        "notable_features": ["CNPD is LSA for several large e-commerce and payments groups with EU main establishment in Luxembourg."],
        "eprivacy_cookie_law": "Law of 30 May 2005 on specific rules for the protection of privacy in the electronic communications sector, Art. 4(3)(e) — consent for cookies.",
        "eprivacy_cookie_authority": "Commission Nationale pour la Protection des Données (CNPD)",
        "direct_marketing_law": "Law of 30 May 2005, Art. 11 — opt-in for unsolicited communications; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Labour Code co-decision article references", "Law of 30 May 2005 Art. 11"],
    },
    "EU-MT": {
        "name": "Malta", "iso2": "MT", "original_language": "en/mt", "pack_id": "EU-MT-CAP586",
        "national_statute": "Data Protection Act, Chapter 586 of the Laws of Malta (2018) and subsidiary legislation (incl. S.L. 586.11 Processing of Child's Personal Data in relation to the Offer of Information Society Services Regulations)",
        "statute_url": "https://legislation.mt/eli/cap/586/eng",
        "effective_date": date(2018, 5, 28),
        "supervisory_authority": "Office of the Information and Data Protection Commissioner (IDPC)", "authority_url": "https://idpc.org.mt",
        "child_digital_consent_age": 13, "child_age_basis": "S.L. 586.11 (Processing of Child's Personal Data in relation to the Offer of Information Society Services Regulations)",
        "employment_rules": ["No specific workplace-monitoring statute; IDPC guidance on CCTV and employee monitoring; Employment and Industrial Relations Act."],
        "health_biometric_genetic_derogations": [
            "Health Act (Cap. 528) and subsidiary legislation govern processing of health data within the national health system.",
            "Art. 6 Data Protection Act: processing of special categories for substantial public interest by regulations.",
        ],
        "national_identifier_rules": "Art. 7 Data Protection Act: identity card number processing only where justified (with consent, legal basis or for identification).",
        "notable_features": ["Public authority fines capped at EUR 25,000 per violation (Art. 21 Cap. 586)."],
        "eprivacy_cookie_law": "Processing of Personal Data (Electronic Communications Sector) Regulations, S.L. 586.01, Regulation 5",
        "eprivacy_cookie_authority": "Office of the Information and Data Protection Commissioner (IDPC)",
        "direct_marketing_law": "S.L. 586.01 Regulation 9 — opt-in for unsolicited communications; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["Health Act (Cap. 528) subsidiary legislation on health data", "Cap. 586 Arts. 6, 7, 21 contents", "S.L. 586.01 Regs. 5 and 9"],
    },
    "EU-NL": {
        "name": "Netherlands", "iso2": "NL", "original_language": "nl", "pack_id": "EU-NL-UAVG",
        "national_statute": "Uitvoeringswet Algemene verordening gegevensbescherming (UAVG), Stb. 2018, 144",
        "statute_url": "https://wetten.overheid.nl/BWBR0040940",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Autoriteit Persoonsgegevens (AP)", "authority_url": "https://autoriteitpersoonsgegevens.nl",
        "child_digital_consent_age": 16, "child_age_basis": "Art. 5 UAVG",
        "employment_rules": [
            "Wet op de ondernemingsraden (WOR) Art. 27(1)(k)-(l): works council consent required for regulations on processing of employee personal data and on systems for monitoring attendance, behaviour or performance.",
            "AP guidance on employee monitoring and sickness-absence data (only company doctor/arbo service may process medical data).",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 29 UAVG: biometric data for unique identification only where necessary for authentication or security purposes.",
            "Art. 30 UAVG: health data processing by healthcare providers, insurers, schools, prisons, employers (reintegration) under conditions.",
            "Wet op de geneeskundige behandelingsovereenkomst (WGBO, Civil Code Book 7) — medical record retention 20 years.",
            "Wet aanvullende bepalingen verwerking persoonsgegevens in de zorg (Wabvpz): electronic exchange of health data requires explicit consent.",
        ],
        "national_identifier_rules": "Art. 46 UAVG: Burgerservicenummer (BSN) may only be processed where required by law.",
        "notable_features": ["Art. 23 UAVG: Art. 9 exemptions for data manifestly made public and for research."],
        "eprivacy_cookie_law": "Telecommunicatiewet Art. 11.7a — consent for cookies; limited exemption for analytics with little or no privacy impact.",
        "eprivacy_cookie_authority": "Autoriteit Consument & Markt (ACM) for Tw 11.7a; Autoriteit Persoonsgegevens (AP) for consent quality and personal-data processing",
        "direct_marketing_law": "Telecommunicatiewet Art. 11.7 — opt-in for email/SMS; soft opt-in; telephone marketing opt-in since 1 July 2021 (Bel-me-niet register abolished).",
        "citation_confidence": "high",
    },
    "EU-PL": {
        "name": "Poland", "iso2": "PL", "original_language": "pl", "pack_id": "EU-PL-UODO2018",
        "national_statute": "Act of 10 May 2018 on the Protection of Personal Data (Ustawa o ochronie danych osobowych), Dz.U. 2018 poz. 1000",
        "statute_url": "https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20180001000",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "President of the Personal Data Protection Office (UODO)", "authority_url": "https://uodo.gov.pl",
        "child_digital_consent_age": 16, "child_age_basis": "GDPR Art. 8(1) default (no Polish derogation)",
        "employment_rules": [
            "Labour Code Art. 22¹: closed list of data an employer may request from candidates/employees.",
            "Labour Code Art. 22¹b: biometric data of employees only with consent where necessary for access control to particularly important information or premises.",
            "Labour Code Arts. 22²-22³: video monitoring and email monitoring — purpose limitation, 3-month retention for recordings, prior notice (2 weeks before launch), inclusion in work regulations.",
        ],
        "health_biometric_genetic_derogations": [
            "Act of 6 November 2008 on Patients' Rights and the Patients' Rights Ombudsman: medical documentation.",
            "Act of 28 April 2011 on the Healthcare Information System.",
        ],
        "national_identifier_rules": "PESEL number processing per purpose limitation and statutory bases.",
        "notable_features": ["Art. 102: fines on public bodies capped at PLN 100,000 (PLN 10,000 for cultural institutions)."],
        "eprivacy_cookie_law": "Electronic Communications Law (Prawo komunikacji elektronicznej) of 12 July 2024, effective 10 November 2024 — consent for storage/access on terminal equipment (replacing Telecommunications Law Art. 173).",
        "eprivacy_cookie_authority": "President of the Office of Electronic Communications (UKE) / President of UODO for personal-data aspects",
        "direct_marketing_law": "Electronic Communications Law (2024) — prior consent for direct marketing via telecommunications terminal equipment and automated calling systems (replacing Telecommunications Law Art. 172 and Act on Electronic Services Art. 10).",
        "citation_confidence": "verify",
        "citations_to_verify": ["Article numbers of cookie and direct-marketing provisions in the 2024 Electronic Communications Law (Arts. 398-399 reported)"],
    },
    "EU-PT": {
        "name": "Portugal", "iso2": "PT", "original_language": "pt", "pack_id": "EU-PT-L58-2019",
        "national_statute": "Lei n.º 58/2019, de 8 de agosto — ensures the execution of the GDPR in the national legal order",
        "statute_url": "https://diariodarepublica.pt/dr/detalhe/lei/58-2019-123815982",
        "effective_date": date(2019, 8, 9),
        "supervisory_authority": "Comissão Nacional de Proteção de Dados (CNPD)", "authority_url": "https://www.cnpd.pt",
        "child_digital_consent_age": 13, "child_age_basis": "Art. 16 Lei n.º 58/2019",
        "employment_rules": [
            "Art. 28 Lei n.º 58/2019: employee consent is not a valid basis where processing gives a legal/economic advantage or is necessary for the contract; CCTV recordings usable in disciplinary proceedings only within criminal proceedings; biometric data only for attendance and access control.",
            "Código do Trabalho Arts. 20-21: remote surveillance only for protection and security of persons and property or where required by the activity.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 29 Lei n.º 58/2019: health and genetic data — access restricted to professionals bound by secrecy; electronic notification of access.",
            "Lei n.º 12/2005: personal genetic information and health information.",
        ],
        "national_identifier_rules": "Citizen card number per Lei n.º 7/2007.",
        "notable_features": ["CNPD Deliberation 2019/494: CNPD will disapply several Lei 58/2019 provisions it considers incompatible with the GDPR (e.g. Art. 2(1)-(2), Art. 20(1), Art. 23, Art. 28(3)(a), Art. 37(2), Art. 44(1), Art. 61(2))."],
        "eprivacy_cookie_law": "Lei n.º 41/2004, de 18 de agosto (as amended by Lei n.º 46/2012), Art. 5 — prior consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Comissão Nacional de Proteção de Dados (CNPD)",
        "direct_marketing_law": "Lei n.º 41/2004 Art. 13-A — prior consent for unsolicited communications to natural persons; DGC opt-out list for legal persons.",
        "citation_confidence": "high",
    },
    "EU-RO": {
        "name": "Romania", "iso2": "RO", "original_language": "ro", "pack_id": "EU-RO-L190-2018",
        "national_statute": "Law No. 190/2018 on measures implementing the GDPR",
        "statute_url": "https://www.dataprotection.ro",
        "effective_date": date(2018, 7, 31),
        "supervisory_authority": "National Supervisory Authority for Personal Data Processing (ANSPDCP)", "authority_url": "https://www.dataprotection.ro",
        "child_digital_consent_age": 16, "child_age_basis": "GDPR Art. 8(1) default (no Romanian derogation)",
        "employment_rules": [
            "Art. 5 Law 190/2018: monitoring of employees via electronic communication and/or video surveillance based on legitimate interest only if: interests justified and outweighing employee rights; prior mandatory, complete and explicit information; consultation of the trade union or employee representatives; less intrusive means proved ineffective; retention max 30 days unless legally required or justified.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 3 Law 190/2018: genetic, biometric or health data for automated decision-making or profiling only with explicit consent or where provided by law with appropriate safeguards.",
            "Law 46/2003 on patients' rights.",
        ],
        "national_identifier_rules": "Art. 4 Law 190/2018: national identification number (CNP) processing based on legitimate interest requires appropriate safeguards — TOMs, minimisation, retention limits, DPO appointment and staff training.",
        "notable_features": ["Art. 13-14: public authorities can receive warnings and remediation plans before fines (fines RON 10,000-200,000)."],
        "eprivacy_cookie_law": "Law No. 506/2004 on the processing of personal data and the protection of privacy in the electronic communications sector, Art. 4(5)",
        "eprivacy_cookie_authority": "National Supervisory Authority for Personal Data Processing (ANSPDCP)",
        "direct_marketing_law": "Law No. 506/2004 Art. 12 — prior express consent for commercial communications by automated calling, fax, email; soft opt-in.",
        "citation_confidence": "high",
    },
    "EU-SK": {
        "name": "Slovakia", "iso2": "SK", "original_language": "sk", "pack_id": "EU-SK-ACT18-2018",
        "national_statute": "Act No. 18/2018 Coll. on Personal Data Protection and on amendments to certain acts",
        "statute_url": "https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2018/18/",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Office for Personal Data Protection of the Slovak Republic (ÚOOÚ SR)", "authority_url": "https://dataprotection.gov.sk",
        "child_digital_consent_age": 16, "child_age_basis": "§ 15(1) Act No. 18/2018 Coll.",
        "employment_rules": [
            "Labour Code (Act No. 311/2001 Coll.) § 13(4): employer may not intrude on employee privacy without serious reasons related to the nature of its activity; must consult employee representatives on scope, method and duration of monitoring and inform employees in advance.",
            "§ 78(3) Act No. 18/2018: employer may publish/provide title, name, surname, position, workplace, phone, email where needed for the employee's work duties.",
        ],
        "health_biometric_genetic_derogations": [
            "Act No. 576/2004 Coll. on Healthcare: medical records and confidentiality.",
            "§ 78(5)-(7) Act No. 18/2018: genetic, biometric and health data processing only on basis of special law or international treaty.",
        ],
        "national_identifier_rules": "§ 78(4) Act No. 18/2018: birth number (rodné číslo) may be used for identification only where necessary for the purpose; publication prohibited.",
        "notable_features": ["Act No. 18/2018 also transposes the LED (Part Three)."],
        "eprivacy_cookie_law": "Act No. 452/2021 Coll. on Electronic Communications, § 109(8) — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Office for Personal Data Protection of the Slovak Republic (ÚOOÚ SR) / Regulatory Authority for Electronic Communications and Postal Services",
        "direct_marketing_law": "Act No. 452/2021 Coll. § 116 — prior consent for unsolicited communications; soft opt-in.",
        "citation_confidence": "verify",
        "citations_to_verify": ["§ 109(8) and § 116 Act No. 452/2021", "§ 78(5)-(7) Act No. 18/2018 content", "§ 15 child age article"],
    },
    "EU-SI": {
        "name": "Slovenia", "iso2": "SI", "original_language": "sl", "pack_id": "EU-SI-ZVOP2",
        "national_statute": "Personal Data Protection Act (Zakon o varstvu osebnih podatkov, ZVOP-2), Uradni list RS, št. 163/2022",
        "statute_url": "https://www.pisrs.si/pregledPredpisa?id=ZAKO7959",
        "effective_date": date(2023, 1, 26),
        "supervisory_authority": "Information Commissioner of the Republic of Slovenia (Informacijski pooblaščenec, IP RS)", "authority_url": "https://www.ip-rs.si",
        "child_digital_consent_age": 15, "child_age_basis": "Art. 8 ZVOP-2",
        "employment_rules": [
            "ZVOP-2 video-surveillance provisions: workplace video surveillance only in exceptional cases where necessary for safety of persons or property or protection of classified/business secrets, with prior written notice and consultation of the trade union/works council; prohibited in changing rooms, toilets, lifts and sanitary areas.",
            "Employment Relationships Act (ZDR-1) Art. 48: employee personal data processing only where required by law or connected with the employment relationship.",
        ],
        "health_biometric_genetic_derogations": [
            "ZVOP-2 biometrics provisions: biometric measures in the private sector only where strictly necessary for business operations, safety of persons/property or protection of secrets, with prior notice to the Information Commissioner.",
            "Patients' Rights Act (ZPacP) and Healthcare Databases Act (ZZPPZ).",
        ],
        "national_identifier_rules": "EMŠO (unique master citizen number) and tax number restrictions on linking filing systems.",
        "notable_features": ["ZVOP-2 also regulates direct-marketing processing and public-sector filing system connection."],
        "eprivacy_cookie_law": "Electronic Communications Act (ZEKom-2), Uradni list RS, št. 130/2022, Art. 225 — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Information Commissioner of the Republic of Slovenia (IP RS)",
        "direct_marketing_law": "ZEKom-2 Art. 226 — prior consent for unsolicited electronic communications; soft opt-in; ZVOP-2 direct-marketing provisions.",
        "citation_confidence": "verify",
        "citations_to_verify": ["ZEKom-2 Arts. 225-226 numbering", "ZVOP-2 article numbers for video surveillance and biometrics"],
    },
    "EU-ES": {
        "name": "Spain", "iso2": "ES", "original_language": "es", "pack_id": "EU-ES-LOPDGDD",
        "national_statute": "Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD)",
        "statute_url": "https://www.boe.es/eli/es/lo/2018/12/05/3/con",
        "effective_date": date(2018, 12, 7),
        "supervisory_authority": "Agencia Española de Protección de Datos (AEPD)", "authority_url": "https://www.aepd.es",
        "child_digital_consent_age": 14, "child_age_basis": "Art. 7 LOPDGDD",
        "employment_rules": [
            "Art. 87 LOPDGDD: employee privacy in the use of digital devices provided by the employer — criteria for use must be established with worker representatives.",
            "Art. 88 LOPDGDD: right to digital disconnection; internal policy required.",
            "Art. 89 LOPDGDD: video surveillance and sound recording at the workplace with prior express, clear and concise information.",
            "Art. 90 LOPDGDD: geolocation systems at work with prior information.",
            "Art. 91: collective agreements may set additional guarantees.",
        ],
        "health_biometric_genetic_derogations": [
            "Art. 9 LOPDGDD: consent alone cannot lift the Art. 9(1) prohibition where the main purpose is identifying ideology, union membership, religion, sexual orientation, beliefs or racial/ethnic origin.",
            "Disposición adicional decimoséptima LOPDGDD: health and research data — broad consent for research areas; pseudonymised reuse with ethics committee approval.",
            "Ley 41/2002 básica reguladora de la autonomía del paciente: clinical history retention minimum 5 years from discharge.",
        ],
        "national_identifier_rules": "Disposición adicional séptima LOPDGDD: publication of DNI/NIE numbers limited to four random digits.",
        "notable_features": [
            "Art. 34 LOPDGDD: list of entities required to appoint a DPO (e.g. schools, insurers, healthcare centres keeping patient records — except individual practitioners — telecom operators, private security firms, gaming operators).",
            "Art. 23 LOPDGDD: advertising exclusion systems (Lista Robinson).",
            "Title X (Arts. 79-97): digital rights (neutrality, digital education, right to be forgotten in search/social networks, digital testament).",
        ],
        "eprivacy_cookie_law": "Ley 34/2002 de servicios de la sociedad de la información y de comercio electrónico (LSSI), Art. 22.2; AEPD Guía sobre el uso de las cookies (updated July 2023, aligned with EDPB).",
        "eprivacy_cookie_authority": "Agencia Española de Protección de Datos (AEPD)",
        "direct_marketing_law": "LSSI Art. 21 — prior express consent for commercial electronic communications; soft opt-in; Ley 11/2022 General de Telecomunicaciones Art. 66 — right not to receive unsolicited marketing calls without prior consent.",
        "citation_confidence": "high",
    },
    "EU-SE": {
        "name": "Sweden", "iso2": "SE", "original_language": "sv", "pack_id": "EU-SE-DSL",
        "national_statute": "Lag (2018:218) med kompletterande bestämmelser till EU:s dataskyddsförordning (Dataskyddslagen)",
        "statute_url": "https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/lag-2018218-med-kompletterande-bestammelser_sfs-2018-218/",
        "effective_date": date(2018, 5, 25),
        "supervisory_authority": "Integritetsskyddsmyndigheten (IMY)", "authority_url": "https://www.imy.se",
        "child_digital_consent_age": 13, "child_age_basis": "Ch. 2 § 4 Dataskyddslagen",
        "employment_rules": [
            "Ch. 3 § 2 Dataskyddslagen: special categories processing necessary for labour-law, social-security and social-protection obligations.",
            "Lag (1976:580) om medbestämmande i arbetslivet (MBL) §§ 11 and 19: duty to negotiate and inform trade unions before introducing monitoring systems.",
            "Kamerabevakningslag (2018:1200): camera surveillance rules.",
        ],
        "health_biometric_genetic_derogations": [
            "Patientdatalag (2008:355): patient records, cohesive record-keeping and access logging.",
            "Lag (2003:460) om etikprövning av forskning: ethical review for research involving sensitive data.",
            "Lag (2006:351) om genetisk integritet: restrictions on genetic testing and use of genetic information by insurers and employers.",
        ],
        "national_identifier_rules": "Ch. 3 § 10 Dataskyddslagen: personal identity numbers (personnummer) only with consent or where clearly justified by purpose, importance of secure identification or other considerable reason.",
        "notable_features": ["Ch. 1 § 7: GDPR does not apply to the extent it would conflict with the Freedom of the Press Act and Fundamental Law on Freedom of Expression."],
        "eprivacy_cookie_law": "Lag (2022:482) om elektronisk kommunikation, Ch. 9 § 28 — consent for storage/access on terminal equipment.",
        "eprivacy_cookie_authority": "Post- och telestyrelsen (PTS)",
        "direct_marketing_law": "Marknadsföringslagen (2008:486) §§ 19-20 — prior consent for email/SMS/automated-call marketing to natural persons; soft opt-in; NIX telephone opt-out register.",
        "citation_confidence": "high",
    },
}


# ---------------------------------------------------------------------------
# 3. MEMBER-STATE PACK BUILDERS
# ---------------------------------------------------------------------------

def _review_status(v: Dict[str, Any]) -> LegalReviewStatus:
    return LegalReviewStatus.VERIFIED if v.get("citation_confidence") == "high" else LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF


def _deployment_status(v: Dict[str, Any]) -> DeploymentStatus:
    return DeploymentStatus.PRODUCTION_ENABLED if v.get("citation_confidence") == "high" else DeploymentStatus.TESTED


def _member_state_scope(code: str) -> Dict[str, Any]:
    return {
        "requires_regulation": "EU-GDPR",
        "nexus": GDPR_ART3_NEXUS,
        "member_state_scope": (
            f"Attaches where the controller/processor has an establishment in {code} (processing in the context of its "
            f"activities), or — for national rules protecting data subjects (e.g. Art. 8 child age) — where data subjects "
            f"located in {code} are targeted or monitored. Lead Supervisory Authority competence under Art. 56 does not "
            f"displace the substantive national law of the Member State whose rules apply."
        ),
        "never_triggered_by": GDPR_NEVER_TRIGGERED_BY,
        "trigger_facts": [
            f"organization.establishments contains {code}",
            f"activity.subject_locations contains {code} AND (targets_goods_or_services_to_subjects OR monitors_subject_behavior)",
        ],
    }


def _national_gdpr_pack(code: str, v: Dict[str, Any]) -> CanonicalRegulation:
    preemptions = [
        PreemptionRule(
            rule_id=f"{v['pack_id']}-GDPR-OPENING",
            preempts_or_yields="opening_clause_derogation",
            target_regulation_id="EU-GDPR",
            scope_condition="Arts. 8(1), 9(4), 23, 85-90 GDPR",
            description=f"{v['name']} national law specifies GDPR opening clauses; directly applicable GDPR prevails over inconsistent national provisions (primacy of EU law).",
        )
    ]
    conditions = _member_state_scope(code)
    conditions.update({
        "child_digital_consent_age": v["child_digital_consent_age"],
        "child_age_basis": v["child_age_basis"],
        "national_identifier_rules": v["national_identifier_rules"],
        "notable_features": v["notable_features"],
        "citation_confidence": v["citation_confidence"],
    })
    if v.get("citations_to_verify"):
        conditions["citations_to_verify"] = v["citations_to_verify"]

    return CanonicalRegulation(
        regulation_id=v["pack_id"],
        jurisdiction_id=code,
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country=v["iso2"],
        member_state=v["name"],
        legal_authority=f"Parliament of {v['name']}",
        legal_instrument=v["national_statute"],
        official_source_url=v["statute_url"],
        source_document_hash=_fingerprint(v["national_statute"], v["statute_url"], RULE_VERSION),
        article_or_section=f"National GDPR implementing act — child consent ({v['child_age_basis']}), Art. 88 employment, Art. 9(4) derogations, Art. 87 identifiers",
        original_language=v["original_language"],
        verified_translation="en",
        effective_date=v["effective_date"],
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions=conditions,
        thresholds=[
            StatutoryThreshold(
                metric="data_subject_age",
                operator="<",
                value=v["child_digital_consent_age"],
                description=f"GDPR Art. 8 as specified for {v['name']}: below {v['child_digital_consent_age']}, consent-based information-society services offered directly to a child require authorisation by the holder of parental responsibility.",
            )
        ],
        preemption_rules=preemptions,
        organization_types=["private", "public", "nonprofit", "healthcare_covered_entity", "financial_institution", "educational_institution"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "employees", "patients", "children", "job_applicants"],
        data_categories=["personal_data", "special_category_health", "special_category_genetic", "special_category_biometric", "national_identifier"],
        processing_activities=["employee_monitoring", "health_data_processing", "biometric_processing", "child_online_services", "research"],
        required_actions=(
            [f"Art. 8: Apply the {v['name']} digital consent age of {v['child_digital_consent_age']} ({v['child_age_basis']}) for consent-based information-society services offered directly to children."]
            + [f"Art. 88 employment: {r}" for r in v["employment_rules"]]
            + [f"Art. 9(4) health/biometric/genetic: {r}" for r in v["health_biometric_genetic_derogations"]]
            + [f"Art. 87 national identifier: {v['national_identifier_rules']}"]
            + [f"Notify personal data breaches to {v['supervisory_authority']} within 72 hours (GDPR Art. 33) using its national notification channel."]
        ),
        required_assessments=["National Opening-Clause Gap Assessment", "Employee Monitoring Proportionality Assessment", "DPIA per national Art. 35(4) list"],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=[f"{v['supervisory_authority']}: personal data breach within 72h (GDPR Art. 33)", f"{v['supervisory_authority']}: DPO contact details (GDPR Art. 37(7))"],
        required_evidence=["Age-assurance / parental consent records", "Works-council / employee-representative consultation records", "Special-category access lists and safeguards", "National DPIA list check"],
        approval_requirements=["Human approval before introducing any employee-monitoring technology", "Counsel sign-off on reliance on national Art. 9(4) derogations"],
        competent_regulator=v["supervisory_authority"],
        subnational_regulators={"authority_url": v["authority_url"]},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=_deployment_status(v),
        legal_review_status=_review_status(v),
        rule_version=RULE_VERSION,
        domain_category="privacy",
    )


def _national_eprivacy_pack(code: str, v: Dict[str, Any]) -> CanonicalRegulation:
    instrument = f"{v['name']} ePrivacy transposition — {v['eprivacy_cookie_law']}"
    conditions = {
        "requires_regulation": "EU-EPRIVACY",
        "nexus": ["terminal_equipment_of_users_located_in_member_state", "establishment_in_member_state"],
        "member_state_scope": f"Cookie/tracker deployment on terminal equipment of users in {v['name']}, and electronic marketing to recipients in {v['name']}.",
        "trigger_facts": ["activity.involves_targeted_advertising_or_cookies", f"activity.subject_locations contains {code}"],
        "direct_marketing_law": v["direct_marketing_law"],
        "citation_confidence": v["citation_confidence"],
    }
    if v.get("citations_to_verify"):
        conditions["citations_to_verify"] = v["citations_to_verify"]
    return CanonicalRegulation(
        regulation_id=f"{code}-EPRIVACY",
        jurisdiction_id=code,
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country=v["iso2"],
        member_state=v["name"],
        legal_authority=f"Parliament of {v['name']} (transposing Directive 2002/58/EC)",
        legal_instrument=instrument,
        official_source_url=v["authority_url"],
        source_document_hash=_fingerprint(instrument, v["authority_url"], RULE_VERSION),
        article_or_section=v["eprivacy_cookie_law"],
        original_language=v["original_language"],
        verified_translation="en",
        effective_date=v["effective_date"],
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions=conditions,
        exemptions=[
            ExemptionRule(
                exemption_id=f"{code}-EPRIVACY-STRICTLY-NECESSARY",
                exemption_type="activity_level",
                condition_field="activity.cookie_purpose",
                condition_values=["transmission", "strictly_necessary_requested_service"],
                carve_out_statute=v["eprivacy_cookie_law"],
                description="Strictly necessary storage/access and transmission-only cookies are exempt from consent (Art. 5(3) ePD transposition).",
            )
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id=f"{code}-EPRIVACY-LEX-SPECIALIS",
                preempts_or_yields="preempts",
                target_regulation_id="EU-GDPR",
                scope_condition="Terminal equipment access and electronic marketing",
                description="National ePrivacy rules apply as lex specialis (GDPR Art. 95); consent standard follows GDPR.",
            )
        ],
        organization_types=["private", "public", "nonprofit"],
        industry_sectors=["all", "digital_services", "ecommerce", "media", "adtech"],
        data_subject_categories=["website_visitors", "app_users", "consumers", "subscribers"],
        data_categories=["online_identifiers", "device_information"],
        processing_activities=["cookies_and_trackers", "targeted_advertising", "analytics", "direct_marketing"],
        required_actions=[
            f"Cookies/trackers: {v['eprivacy_cookie_law']}",
            "Obtain prior opt-in consent for non-essential cookies and similar technologies; equal-prominence reject option; record and honour withdrawal.",
            f"Direct marketing: {v['direct_marketing_law']}",
        ],
        required_assessments=["Cookie & Tracker Audit (national)", "Electronic Marketing Consent Audit (national)"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False),
        notification_requirements=[],
        required_evidence=["CMP consent logs", "Cookie inventory", "Marketing consent / suppression lists"],
        approval_requirements=["Human approval before deploying new third-party trackers"],
        competent_regulator=v["eprivacy_cookie_authority"],
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=_deployment_status(v),
        legal_review_status=_review_status(v),
        rule_version=RULE_VERSION,
        domain_category="electronic_communications",
    )


# ---------------------------------------------------------------------------
# 4. SPECIALISED SECTORAL PACKS — GERMANY, FRANCE, IRELAND
# ---------------------------------------------------------------------------

def _laender_regulators() -> Dict[str, str]:
    # Mirrors core.jrae.registry.GERMAN_LANDER_AUTHORITIES (17 authorities incl. Bavaria public/private split).
    return {
        "DE-FED": "Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI) — federal public bodies, telecommunications and postal services",
        "DE-BW": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg (LfDI BW)",
        "DE-BY-PRIV": "Bayerisches Landesamt für Datenschutzaufsicht (BayLDA) — private sector",
        "DE-BY-PUB": "Der Bayerische Landesbeauftragte für den Datenschutz (BayLfD) — public sector",
        "DE-BE": "Berliner Beauftragte für Datenschutz und Informationsfreiheit (BlnBDI)",
        "DE-BB": "Die Landesbeauftragte für den Datenschutz und für das Recht auf Akteneinsicht Brandenburg (LDA BB)",
        "DE-HB": "Die Landesbeauftragte für Datenschutz und Informationsfreiheit der Freien Hansestadt Bremen",
        "DE-HH": "Der Hamburgische Beauftragte für Datenschutz und Informationsfreiheit (HmbBfDI)",
        "DE-HE": "Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)",
        "DE-MV": "Der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern",
        "DE-NI": "Die Landesbeauftragte für den Datenschutz Niedersachsen (LfD NI)",
        "DE-NW": "Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW)",
        "DE-RP": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Rheinland-Pfalz",
        "DE-SL": "Unabhängiges Datenschutzzentrum Saarland",
        "DE-SN": "Sächsischer Datenschutz- und Transparenzbeauftragter",
        "DE-ST": "Landesbeauftragter für den Datenschutz Sachsen-Anhalt",
        "DE-SH": "Unabhängiges Landeszentrum für Datenschutz Schleswig-Holstein (ULD)",
        "DE-TH": "Thüringer Landesbeauftragter für den Datenschutz und die Informationsfreiheit (TLfDI)",
        "DSK": "Datenschutzkonferenz (DSK) — coordination body of federal and Länder authorities",
    }


def _de_bdsg() -> CanonicalRegulation:
    v = EU_MEMBER_STATE_VARIATIONS["EU-DE"]
    url = v["statute_url"]
    instrument = "Bundesdatenschutzgesetz (BDSG) — Federal Data Protection Act of 30 June 2017 (BGBl. I S. 2097)"
    conditions = _member_state_scope("EU-DE")
    conditions.update({
        "supervisory_competence": (
            "§ 40 BDSG: private-sector controllers are supervised by the Land authority where the establishment is located "
            "(e.g. BayLDA for Bavaria, BlnBDI for Berlin, LDI NRW for North Rhine-Westphalia); BfDI supervises federal public "
            "bodies (§ 9) and telecommunications/postal providers. Länder public bodies fall under Länder data protection acts "
            "(e.g. BayDSG, DSG NRW). § 19/§ 40(2): lead-authority coordination among Länder for multi-Land groups; BfDI is the "
            "single contact point to the EDPB (§ 17)."
        ),
        "subnational_region_field": "organization.subnational_regions (e.g. DE-BY, DE-BE, DE-NW)",
        "child_digital_consent_age": 16,
        "citation_confidence": "high",
    })
    return CanonicalRegulation(
        regulation_id="EU-DE-BDSG",
        jurisdiction_id="EU-DE",
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country="DE",
        member_state="Germany",
        legal_authority="Deutscher Bundestag / Bundesrat",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="§§ 4, 22, 26, 27, 31, 32-37, 38, 40, 42-43 BDSG",
        original_language="de",
        verified_translation="en",
        effective_date=date(2018, 5, 25),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions=conditions,
        thresholds=[
            StatutoryThreshold(
                metric="employees_constantly_engaged_in_automated_processing",
                operator=">=",
                value=20,
                logic_group="OR",
                description="§ 38(1) sentence 1 BDSG: controllers and processors must designate a DPO where, as a rule, at least 20 persons are constantly engaged in the automated processing of personal data.",
            ),
            StatutoryThreshold(
                metric="processing_requires_dpia_or_commercial_transfer_market_research",
                operator="==",
                value=True,
                logic_group="OR",
                description="§ 38(1) sentence 2 BDSG: DPO required regardless of headcount where processing is subject to a DPIA (Art. 35 GDPR) or personal data are processed commercially for transfer, anonymised transfer, or market/opinion research.",
            ),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="BDSG-38-BELOW-THRESHOLD",
                exemption_type="entity_level",
                condition_field="organization.employee_count",
                condition_values=["<20_automated_processing_staff_and_no_dpia_and_no_commercial_transfer"],
                carve_out_statute="§ 38(1) BDSG",
                description="No national DPO duty below the 20-person threshold absent DPIA/commercial-transfer triggers; GDPR Art. 37(1) criteria still apply independently.",
            ),
            ExemptionRule(
                exemption_id="BDSG-34-ACCESS-RESTRICTION",
                exemption_type="data_level",
                condition_field="activity.data_categories",
                condition_values=["statutory_retention_only_data", "backup_or_audit_only_data"],
                carve_out_statute="§ 34(1) BDSG",
                description="Right of access restricted for data stored only due to statutory retention or exclusively for data-security/audit purposes where access would require disproportionate effort and other processing is excluded by TOMs.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="BDSG-SUBSIDIARITY", preempts_or_yields="yields_to", target_regulation_id="Sector-specific federal data protection law (e.g. SGB X, TDDDG)", scope_condition="§ 1(2) BDSG", description="Specific federal data protection provisions take precedence over the BDSG."),
            PreemptionRule(rule_id="BDSG-GDPR-OPENING", preempts_or_yields="opening_clause_derogation", target_regulation_id="EU-GDPR", scope_condition="Arts. 6(2), 9(2)(b)/(h)/(i)/(j), 23, 37(4), 88", description="BDSG specifies GDPR opening clauses; CJEU C-34/21 limits § 26(1) sentence 1; CJEU C-634/21 casts doubt on § 31 BDSG scoring rules — apply GDPR directly where national rule is not a valid specification."),
        ],
        organization_types=["private", "public", "healthcare_covered_entity", "financial_institution"],
        industry_sectors=["all"],
        data_subject_categories=["employees", "job_applicants", "consumers", "patients"],
        data_categories=["personal_data", "special_category_health", "special_category_biometric", "employee_data", "credit_scoring_data"],
        processing_activities=["employee_monitoring", "hr_processing", "video_surveillance", "credit_scoring", "health_data_processing", "research"],
        required_actions=[
            "§ 26 BDSG: Limit employment-related processing to what is necessary for hiring, performance or termination; detecting criminal offences only on documented factual indications (§ 26(1) sentence 2); written/electronic consent with information on purpose and withdrawal (§ 26(2)); works agreements meeting Art. 88(2) GDPR.",
            "§ 87(1) No. 6 BetrVG: Obtain works council co-determination before introducing technical systems capable of monitoring employees (incl. Microsoft 365, AI tooling, telematics).",
            "§ 22 BDSG: For special-category (health) data, implement § 22(2) measures — access logging, staff awareness, pseudonymisation/encryption, restricted access, designated DPO, procedural rules.",
            "§ 38 BDSG: Designate a DPO where >= 20 persons are constantly engaged in automated processing, or where DPIA/commercial-transfer triggers apply; DPO dismissal protection (§ 38(2) with § 6(4)).",
            "§ 40 BDSG: Determine the competent Land supervisory authority from the establishment location (e.g. BayLDA, BlnBDI, LDI NRW) and the BfDI for federal bodies/telecom.",
            "§ 4 BDSG: Video surveillance of publicly accessible areas — necessity, signage and prompt deletion (note: applicability to private controllers limited after BVerwG 6 C 2.18 (2019); private controllers rely on Art. 6(1)(f) GDPR).",
            "§ 27 BDSG: Research processing of special categories permitted where necessary and controller interests substantially outweigh — with § 22(2) safeguards.",
            "§§ 32-37 BDSG: Apply national restrictions on information/access/erasure only within their narrow conditions; § 35: erasure replaced by restriction where non-automated processing makes erasure disproportionate.",
            "§§ 42-43 BDSG: Criminal liability for commercial unauthorised transfer/obtaining of non-public personal data (up to 3 years).",
        ],
        required_assessments=["DPO Requirement Assessment (§ 38 BDSG / Art. 37 GDPR)", "Works Council Co-determination Check (§ 87 BetrVG)", "Employee Data Processing Assessment (§ 26 BDSG / Art. 88 GDPR)", "Competent Land Authority Determination (§ 40 BDSG)", "DPIA per DSK Muss-Liste"],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=["Competent Land authority or BfDI: breach within 72h (Art. 33 GDPR)", "Competent authority: DPO contact details (Art. 37(7) GDPR)"],
        required_evidence=["DPO designation letter and authority notification", "Works agreements (Betriebsvereinbarungen)", "§ 22(2) TOM documentation", "Employee consent records (§ 26(2))", "Headcount record for § 38 threshold"],
        approval_requirements=["Works council agreement before employee-monitoring deployment", "DPO involvement in DPIA"],
        competent_regulator="BfDI (federal public bodies, telecom/postal) and the competent Land supervisory authority under § 40 BDSG",
        subnational_regulators=_laender_regulators(),
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.VERIFIED,
        rule_version=RULE_VERSION,
        domain_category="privacy",
    )


def _de_patient_health() -> CanonicalRegulation:
    url = "https://www.gesetze-im-internet.de/sgb_5/"
    instrument = (
        "German health-data framework — Patientendaten-Schutz-Gesetz (PDSG, BGBl. I 2020 S. 2115), Sozialgesetzbuch Fünftes Buch "
        "(SGB V) §§ 341-393 incl. Digital-Gesetz (DigiG, 2024) and Gesundheitsdatennutzungsgesetz (GDNG, 2024), SGB X §§ 67-85a, "
        "§ 203 Strafgesetzbuch (StGB), and Landeskrankenhausgesetze / Länder hospital data protection laws"
    )
    return CanonicalRegulation(
        regulation_id="EU-DE-PATIENT-HEALTH",
        jurisdiction_id="EU-DE",
        jurisdiction_type=JurisdictionType.SECTORAL,
        country="DE",
        member_state="Germany",
        legal_authority="Deutscher Bundestag / Bundesrat; Landtage (hospital laws)",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="SGB V §§ 341-342 (ePA), § 393 (cloud use); SGB X §§ 67-85a, § 80; StGB § 203; GDNG §§ 4-6; Länder hospital laws",
        original_language="de",
        verified_translation="en",
        effective_date=date(2020, 10, 20),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "requires_regulation": "EU-GDPR",
            "nexus": ["establishment_in_germany_as_healthcare_provider_or_payer", "processor_to_german_healthcare_provider_or_statutory_health_insurer"],
            "trigger_facts": [
                "organization.establishments contains EU-DE",
                "activity.data_categories contains special_category_health",
                "organization.industry == healthcare OR organization.organization_type == healthcare_covered_entity",
            ],
            "hosting_constraint": (
                "SGB V § 393: service providers and statutory health insurers may process health and social data using "
                "cloud services only where processing takes place in Germany, another EU/EEA state, Switzerland or an "
                "adequacy country (Art. 45 GDPR), with a current BSI C5 Type 2 attestation (Type 1 accepted only during "
                "the transition to 30 June 2025) and state-of-the-art TOMs. Social data commissioned processing outside "
                "the EU/EEA/adequacy countries is restricted (§ 80 SGB X)."
            ),
            "professional_secrecy": (
                "§ 203 StGB: physicians, pharmacists, psychologists and other professionals commit an offence by "
                "unauthorised disclosure of patient secrets. § 203(3) permits disclosure to 'contributing persons' (e.g. IT "
                "service providers) only where necessary and the contractor is bound to secrecy (§ 203(4) creates criminal "
                "liability for contractors)."
            ),
            "landeskrankenhausgesetze": (
                "Hospital data protection rules vary by Land (e.g. Bavaria Art. 27 BayKrG, Berlin LKG, NRW GDSG NW, "
                "Hamburg HmbKHG). Several Länder restrict commissioned processing of patient data to other hospitals or to "
                "processors meeting additional conditions, and some require processing within Germany/EU — verify the "
                "hospital's Land before onboarding any processor."
            ),
            "citation_confidence": "verify",
            "citations_to_verify": ["BayKrG Art. 27 sub-paragraph content", "Hamburg/Berlin hospital-law section numbers", "C5 Type 1 transition date in § 393 SGB V"],
        },
        exemptions=[
            ExemptionRule(
                exemption_id="DE-HEALTH-NON-PROVIDER",
                exemption_type="entity_level",
                condition_field="organization.organization_type",
                condition_values=["private", "non_healthcare"],
                carve_out_statute="SGB V scope",
                description="SGB V / SGB X duties apply to statutory-insurance service providers (Leistungserbringer), insurers and their processors; non-healthcare controllers remain subject to GDPR Art. 9 and § 22 BDSG only.",
            )
        ],
        preemption_rules=[
            PreemptionRule(rule_id="DE-HEALTH-LEX-SPECIALIS-BDSG", preempts_or_yields="preempts", target_regulation_id="EU-DE-BDSG", scope_condition="Social data and statutory health insurance data", description="SGB X/SGB V social-data rules take precedence over the BDSG (§ 1(2) BDSG; § 35 SGB I social secrecy)."),
            PreemptionRule(rule_id="DE-HEALTH-GDPR-9-4", preempts_or_yields="opening_clause_derogation", target_regulation_id="EU-GDPR", scope_condition="Health data", description="German health statutes are Art. 9(2)(h)-(i) and Art. 9(4) specifications."),
            PreemptionRule(rule_id="DE-HEALTH-EHDS", preempts_or_yields="concurrent_with", target_regulation_id="EU-EHDS", scope_condition="Electronic health records and secondary use", description="European Health Data Space Regulation (EU) 2025/327 phases in from 2027-2031; GDNG and ePA rules will be aligned."),
        ],
        organization_types=["healthcare_covered_entity", "health_information_custodian", "business_associate", "processor"],
        industry_sectors=["healthcare", "hospitals", "statutory_health_insurance", "pharmacy", "digital_health_apps", "health_research"],
        data_subject_categories=["patients", "insured_persons", "research_participants"],
        data_categories=["special_category_health", "special_category_genetic", "social_data", "electronic_patient_record"],
        processing_activities=["health_data_processing", "cloud_hosting", "electronic_patient_record", "secondary_use_research", "telemedicine"],
        required_actions=[
            "SGB V § 393: Host health/social data only in Germany, EU/EEA, Switzerland or adequacy countries with a current BSI C5 Type 2 attestation for the cloud service.",
            "§ 203 StGB: Bind every IT contractor and sub-contractor with access to patient secrets to confidentiality in writing; limit access to what is necessary.",
            "SGB X § 80: Commissioned processing of social data — prior notification to the supervisory authority and processing location limits.",
            "SGB V §§ 341-342: Support the opt-out electronic patient record (ePA für alle, from 15 January 2025) — patient access controls, objection rights and access logging.",
            "GDNG: Secondary use via the Health Research Data Centre (Forschungsdatenzentrum Gesundheit); § 6 GDNG permits provider-internal further use for quality, research and statistics with safeguards.",
            "Landeskrankenhausgesetz: Check the Land hospital law for restrictions on commissioned processing and data location before engaging any processor for hospital patient data.",
            "KRITIS/B3S: Hospitals above the KRITIS threshold must implement the B3S hospital security standard and § 8a BSIG measures (now aligned with NIS2 transposition).",
        ],
        required_assessments=["Health-Data Hosting Location & C5 Attestation Review (§ 393 SGB V)", "§ 203 StGB Confidentiality Chain Review", "Länder Hospital Law Applicability Check", "DPIA for health data (Art. 35(3)(b) GDPR)"],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=["Competent supervisory authority: breach within 72h (Art. 33 GDPR)", "BSI: significant IT incidents for KRITIS/NIS2-regulated hospitals"],
        required_evidence=["BSI C5 Type 2 attestation", "Data-location contractual clauses", "§ 203 StGB confidentiality undertakings", "Processor list with hosting locations"],
        approval_requirements=["Human approval for any non-EU sub-processor touching health data (blocked by default)", "Counsel sign-off on Land hospital-law compliance"],
        competent_regulator="Competent Land data protection authority (private hospitals/providers) or BfDI (federal statutory health insurers); Bundesamt für Soziale Sicherung; BSI for IT security",
        subnational_regulators=_laender_regulators(),
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.TESTED,
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        rule_version=RULE_VERSION,
        domain_category="health_privacy",
    )


def _de_tdddg() -> CanonicalRegulation:
    url = "https://www.gesetze-im-internet.de/ttdsg/"
    instrument = "Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz (TDDDG), formerly Telekommunikation-Telemedien-Datenschutz-Gesetz (TTDSG)"
    return CanonicalRegulation(
        regulation_id="EU-DE-TDDDG",
        jurisdiction_id="EU-DE",
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country="DE",
        member_state="Germany",
        legal_authority="Deutscher Bundestag / Bundesrat",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="§§ 25, 26, 28 TDDDG",
        original_language="de",
        verified_translation="en",
        effective_date=date(2021, 12, 1),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions={
            "requires_regulation": "EU-EPRIVACY",
            "nexus": ["terminal_equipment_of_users_in_germany", "establishment_in_germany"],
            "renaming": "TTDSG in force 1 Dec 2021; renamed TDDDG with effect from 14 May 2024 by the Digitale-Dienste-Gesetz (DDG) implementing the EU Digital Services Act.",
            "trigger_facts": ["activity.involves_targeted_advertising_or_cookies", "activity.subject_locations contains EU-DE"],
            "consent_management_services": "§ 26 TDDDG + Einwilligungsverwaltungsverordnung (EinwV, in force 1 April 2025): recognised consent management services may store user consent decisions; recognition by the BfDI.",
            "citation_confidence": "high",
        },
        thresholds=[StatutoryThreshold(metric="administrative_fine_eur", operator="==", value=300_000, currency="EUR", description="§ 28 TDDDG: fines up to EUR 300,000 for § 25 violations; GDPR fines apply separately to subsequent processing.")],
        exemptions=[
            ExemptionRule(exemption_id="TDDDG-25-2-1", exemption_type="activity_level", condition_field="activity.cookie_purpose", condition_values=["transmission"], carve_out_statute="§ 25(2) No. 1 TDDDG", description="Sole purpose of carrying out the transmission of a communication over a public telecommunications network."),
            ExemptionRule(exemption_id="TDDDG-25-2-2", exemption_type="activity_level", condition_field="activity.cookie_purpose", condition_values=["strictly_necessary_requested_service"], carve_out_statute="§ 25(2) No. 2 TDDDG", description="Absolutely necessary for the provider of a digital service to provide a service expressly requested by the user (DSK Orientierungshilfe Digitale Dienste 2024)."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="TDDDG-25-LEX-SPECIALIS", preempts_or_yields="preempts", target_regulation_id="EU-GDPR", scope_condition="Storage/access on terminal equipment", description="§ 25 TDDDG governs terminal-equipment access; subsequent processing of the obtained data requires a GDPR Art. 6 basis (DSK guidance)."),
        ],
        organization_types=["private", "public", "nonprofit"],
        industry_sectors=["all", "digital_services", "ecommerce", "media", "adtech", "telecommunications"],
        data_subject_categories=["website_visitors", "app_users", "end_users"],
        data_categories=["online_identifiers", "device_information", "terminal_equipment_information"],
        processing_activities=["cookies_and_trackers", "targeted_advertising", "analytics", "device_fingerprinting", "sdk_integration"],
        required_actions=[
            "§ 25(1) TDDDG: Obtain informed consent per GDPR before storing information in, or accessing information from, the end user's terminal equipment (cookies, local storage, pixels, fingerprinting, SDKs, connected devices).",
            "Provide a reject option on the first banner layer with equal prominence (DSK Orientierungshilfe; LG München I 33 O 14776/19; consistent court practice).",
            "Rely on § 25(2) only for transmission or absolutely necessary functions of an expressly requested service; analytics and marketing are not exempt.",
            "§ 26 TDDDG: Optionally integrate a recognised consent management service (EinwV) and honour stored decisions.",
            "UWG § 7: Prior express consent for email marketing and B2C telephone marketing; document telephone marketing consent (§ 7a UWG) and keep records for 5 years.",
        ],
        required_assessments=["Cookie & Tracker Audit (§ 25 TDDDG)", "Consent Banner Design Review (DSK Orientierungshilfe Digitale Dienste)"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False),
        required_evidence=["CMP consent logs", "Cookie/SDK inventory with § 25(2) justification", "UWG § 7a telephone-consent records (5 years)"],
        approval_requirements=["Human approval before adding non-essential trackers on German-facing properties"],
        competent_regulator="Competent Land data protection authority (digital services); BfDI (telecommunications providers and recognition of consent management services)",
        subnational_regulators=_laender_regulators(),
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.VERIFIED,
        rule_version=RULE_VERSION,
        domain_category="electronic_communications",
    )


def _fr_lil() -> CanonicalRegulation:
    v = EU_MEMBER_STATE_VARIATIONS["EU-FR"]
    url = v["statute_url"]
    instrument = "Loi n° 78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés (Loi Informatique et Libertés) & CNIL guidelines; Code de la santé publique Art. L.1111-8 (HDS)"
    conditions = _member_state_scope("EU-FR")
    conditions.update({
        "child_digital_consent_age": 15,
        "child_age_basis": "Art. 45 LIL — a minor may consent alone from age 15; below 15 consent must be given jointly by the minor and the holder(s) of parental authority.",
        "cookie_scope": "Art. 82 LIL applies to any reading/writing on terminal equipment of users located in France, regardless of the publisher's GDPR main establishment (CNIL competence confirmed by Conseil d'État, 28 January 2022, Google LLC, n° 449209) — the GDPR one-stop-shop does not apply to Art. 82.",
        "hds_scope": "Any person hosting personal health data collected in prevention, diagnosis, care or social/medico-social follow-up on behalf of the data subject or the producer (health professional/establishment) must be HDS-certified (L.1111-8 CSP; R.1111-8-8 et seq.).",
        "audience_measurement_exemption": (
            "CNIL criteria for consent-exempt analytics: strictly limited to audience measurement for the publisher's sole "
            "account; aggregate/anonymous statistics only; no cross-site tracking or combination with other processing; no "
            "transfer enabling re-identification; tracker lifetime max 13 months (not automatically extended on new visits); "
            "data retention max 25 months; users informed and able to object."
        ),
        "citation_confidence": "high",
    })
    return CanonicalRegulation(
        regulation_id="EU-FR-LIL",
        jurisdiction_id="EU-FR",
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country="FR",
        member_state="France",
        legal_authority="Parlement français; Commission Nationale de l'Informatique et des Libertés (CNIL)",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, RULE_VERSION),
        article_or_section="LIL Arts. 6, 30, 45, 64-77, 82, 85; CNIL Délibérations n° 2020-091 & 2020-092; CSP L.1111-8 & R.1111-8-8 et seq.; CPCE L.34-5",
        original_language="fr",
        verified_translation="en",
        effective_date=date(2019, 6, 1),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions=conditions,
        thresholds=[
            StatutoryThreshold(metric="data_subject_age", operator="<", value=15, description="Art. 45 LIL: joint consent of minor and parental authority below 15 for information-society services based on consent."),
            StatutoryThreshold(metric="analytics_cookie_lifetime_months", operator="<=", value=13, description="CNIL audience-measurement exemption: tracker lifetime max 13 months."),
            StatutoryThreshold(metric="analytics_data_retention_months", operator="<=", value=25, description="CNIL audience-measurement exemption: collected data retained max 25 months."),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="FR-82-AUDIENCE-MEASUREMENT",
                exemption_type="activity_level",
                condition_field="activity.cookie_purpose",
                condition_values=["audience_measurement_cnil_compliant"],
                carve_out_statute="Art. 82 LIL; CNIL Délibération n° 2020-091 Art. 5; CNIL list of configured exempt analytics solutions",
                description="Audience-measurement trackers meeting all CNIL criteria may be deposited without consent.",
            ),
            ExemptionRule(
                exemption_id="FR-82-STRICTLY-NECESSARY",
                exemption_type="activity_level",
                condition_field="activity.cookie_purpose",
                condition_values=["transmission", "strictly_necessary_requested_service", "consent_storage", "authentication", "load_balancing", "shopping_cart"],
                carve_out_statute="Art. 82 LIL al. 2",
                description="Trackers exclusively for transmission or strictly necessary for an online communication service expressly requested by the user.",
            ),
            ExemptionRule(
                exemption_id="FR-HDS-NON-HOSTING",
                exemption_type="activity_level",
                condition_field="activity.hosting_role",
                condition_values=["controller_self_hosted", "transient_processing_without_storage"],
                carve_out_statute="CSP L.1111-8",
                description="HDS applies to third-party hosting on behalf of the health professional/establishment or patient; a health establishment hosting its own data on its own infrastructure is not required to be certified.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="FR-LIL-GDPR-OPENING", preempts_or_yields="opening_clause_derogation", target_regulation_id="EU-GDPR", scope_condition="Arts. 8, 9(4), 23, 85, 87, 89 GDPR", description="LIL specifies GDPR opening clauses (child age 15, health data regime, NIR, post-mortem directives)."),
            PreemptionRule(rule_id="FR-82-NO-ONE-STOP-SHOP", preempts_or_yields="preempts", target_regulation_id="EU-GDPR", scope_condition="Cookies/trackers on French users' terminals", description="Art. 82 LIL (ePrivacy transposition) is outside the GDPR one-stop-shop; the CNIL is competent even where another SA is LSA (Conseil d'État 2022)."),
        ],
        organization_types=["private", "public", "healthcare_covered_entity", "health_information_custodian", "processor"],
        industry_sectors=["all", "healthcare", "digital_services", "ecommerce", "media", "adtech", "cloud_hosting"],
        data_subject_categories=["consumers", "website_visitors", "patients", "employees", "children"],
        data_categories=["personal_data", "online_identifiers", "special_category_health", "national_identifier_nir", "special_category_biometric"],
        processing_activities=["cookies_and_trackers", "targeted_advertising", "analytics", "health_data_hosting", "child_online_services", "direct_marketing"],
        required_actions=[
            "Art. 82 LIL: Obtain prior opt-in consent for all non-exempt trackers (advertising, social-media plugins, non-exempt analytics); consent must be free, specific, informed, unambiguous and given by a clear positive act.",
            "CNIL equal-prominence rule: Offer a 'Refuser tout' button on the first layer as visible and as easy as 'Accepter tout' (CNIL sanctions against Google and Facebook, December 2021 / January 2022); closing the banner without choice must not be treated as consent.",
            "CNIL recommendation: Retain users' refusal for a reasonable duration (CNIL suggests 6 months) before re-prompting; keep proof of consent; make withdrawal accessible at any time (e.g. persistent link/icon).",
            "Configure audience measurement to the CNIL exemption criteria (13-month tracker lifetime, 25-month retention, no cross-site tracking) or obtain consent.",
            "Art. 45 LIL: For users under 15, obtain joint consent of the minor and parental authority where consent is the lawful basis; provide age-appropriate information.",
            "CSP L.1111-8: Use only HDS-certified hosts for health data hosted on behalf of health professionals, establishments or patients; HDS referential v2 (2024) requires hosting within the EEA and transparency on any extra-EEA access risk.",
            "Arts. 64-77 LIL: Health research processing via CNIL reference methodologies (MR-001 to MR-006), CNIL authorisation, or SNDS/Health Data Hub access procedures.",
            "Art. 30 LIL / Décret n° 2019-341: Process the NIR only for authorised purposes and controllers.",
            "CPCE L.34-5: Opt-in for B2C email/SMS marketing; Code de la consommation L.223-1: screen telephone canvassing against Bloctel; Loi n° 2025-594 of 30 June 2025 moves telephone canvassing to prior consent (opt-in) from 11 August 2026.",
            "Code du travail L.1222-4 / L.2312-38: Inform employees and consult the CSE before introducing monitoring tools.",
        ],
        required_assessments=["Cookie & Tracker Audit (Art. 82 LIL / CNIL guidelines)", "Consent Banner Equal-Prominence Review", "HDS Certification Check for Health-Data Hosts", "DPIA per CNIL Art. 35(4) list", "Minor (<15) Consent Flow Review"],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=["CNIL: personal data breach within 72h (Art. 33 GDPR) via CNIL teleservice", "CNIL: DPO designation (Art. 37(7) GDPR)"],
        required_evidence=["CMP configuration and consent/refusal logs", "Analytics configuration meeting CNIL exemption", "HDS certificates of all health-data hosts", "Bloctel screening records", "CSE consultation minutes"],
        approval_requirements=["Human approval before onboarding any non-HDS host for French health data (blocked by default)", "Human approval before deploying advertising trackers on French-facing properties"],
        competent_regulator="Commission Nationale de l'Informatique et des Libertés (CNIL); Agence du Numérique en Santé (ANS) and accredited certification bodies for HDS",
        subnational_regulators={"CNIL": "https://www.cnil.fr", "ANS (HDS)": "https://esante.gouv.fr/produits-services/hds"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.VERIFIED,
        rule_version=RULE_VERSION,
        domain_category="privacy",
    )


def _ie_dpa2018() -> CanonicalRegulation:
    v = EU_MEMBER_STATE_VARIATIONS["EU-IE"]
    url = v["statute_url"]
    instrument = "Data Protection Act 2018 (Number 7 of 2018) & Data Protection Act 2018 (Section 36(2)) (Health Research) Regulations 2018 (S.I. No. 314 of 2018)"
    conditions = _member_state_scope("EU-IE")
    conditions.update({
        "child_digital_consent_age": 16,
        "child_age_basis": "Section 31 DPA 2018",
        "lead_supervisory_authority": (
            "Where the controller/processor's main establishment (Art. 4(16) GDPR — place of central administration in the "
            "EU, or where decisions on purposes and means are taken) is in Ireland, the DPC acts as Lead Supervisory "
            "Authority for cross-border processing (Art. 56 GDPR). A letterbox or sales-only Irish subsidiary does not "
            "confer main-establishment status (EDPB Guidelines 8/2022)."
        ),
        "lsa_trigger_fact": "organization.main_eu_establishment in (IE, EU-IE)",
        "citation_confidence": "high",
    })
    return CanonicalRegulation(
        regulation_id="EU-IE-DPA2018",
        jurisdiction_id="EU-IE",
        jurisdiction_type=JurisdictionType.MEMBER_STATE,
        country="IE",
        member_state="Ireland",
        legal_authority="Oireachtas (Houses of the Oireachtas); Minister for Health (Health Research Regulations)",
        legal_instrument=instrument,
        official_source_url=url,
        source_document_hash=_fingerprint(instrument, url, "https://www.irishstatutebook.ie/eli/2018/si/314/made/en/print", RULE_VERSION),
        article_or_section="DPA 2018 ss. 31, 36, 41, 45-54, 60, 117, 141-143; S.I. No. 314 of 2018 as amended by S.I. No. 18 of 2021",
        original_language="en",
        verified_translation="en",
        effective_date=date(2018, 5, 25),
        last_verified_at=LAST_VERIFIED_AT,
        applicability_conditions=conditions,
        thresholds=[
            StatutoryThreshold(metric="data_subject_age", operator="<", value=16, description="Section 31 DPA 2018: digital age of consent 16."),
            StatutoryThreshold(metric="public_body_fine_cap_eur", operator="<=", value=1_000_000, currency="EUR", description="Section 141(4): fines on public authorities/bodies not acting as undertakings capped at EUR 1,000,000."),
        ],
        exemptions=[
            ExemptionRule(
                exemption_id="IE-HRR-CONSENT-DECLARATION",
                exemption_type="activity_level",
                condition_field="activity.purpose",
                condition_values=["health_research_with_hrcdc_consent_declaration"],
                carve_out_statute="S.I. No. 314 of 2018, Reg. 5",
                description="Health research without explicit consent permitted only where the Health Research Consent Declaration Committee grants a consent declaration (public interest significantly outweighs need for consent).",
            ),
            ExemptionRule(
                exemption_id="IE-S60-RESTRICTIONS",
                exemption_type="activity_level",
                condition_field="activity.purpose",
                condition_values=["legal_proceedings", "criminal_investigation", "national_security"],
                carve_out_statute="DPA 2018 ss. 60-61 (Art. 23 GDPR restrictions)",
                description="Data-subject rights may be restricted to the extent necessary and proportionate for listed purposes, including legal privilege (s. 162).",
            ),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="IE-DPA-GDPR-OPENING", preempts_or_yields="opening_clause_derogation", target_regulation_id="EU-GDPR", scope_condition="Arts. 8, 9(2)(j), 9(4), 23, 36(5), 80, 82 GDPR", description="DPA 2018 gives further effect to the GDPR; Part 5 transposes the LED."),
            PreemptionRule(rule_id="IE-DPC-LSA", preempts_or_yields="concurrent_with", target_regulation_id="EU-GDPR", scope_condition="Cross-border processing with Irish main establishment", description="DPC is LSA (Art. 56) subject to the Art. 60 cooperation and Art. 65 EDPB dispute-resolution mechanisms."),
        ],
        organization_types=["private", "public", "healthcare_covered_entity", "health_information_custodian", "nonprofit"],
        industry_sectors=["all", "technology", "healthcare", "health_research", "pharma", "financial_services"],
        data_subject_categories=["consumers", "patients", "research_participants", "children", "employees"],
        data_categories=["personal_data", "special_category_health", "special_category_genetic", "national_identifier_ppsn"],
        processing_activities=["cross_border_processing", "health_research", "child_online_services", "health_data_processing"],
        required_actions=[
            "Art. 56 GDPR: Document the EU main establishment; where it is in Ireland, route cross-border regulatory engagement and breach notifications to the DPC as LSA.",
            "Section 31: Apply the digital age of consent of 16 for consent-based information-society services; s. 30 prohibits profiling/micro-targeting of children for direct marketing (provision not yet commenced — monitor commencement).",
            "Section 36 + S.I. 314/2018: For health research obtain explicit consent (or an HRCDC consent declaration), conduct a DPIA where high risk, put in place ethics approval, training, access controls and transparency arrangements.",
            "Section 52: Process health data for health purposes only by health practitioners or persons owing an equivalent duty of confidentiality.",
            "Section 46: Process special categories for employment/social-welfare purposes only with suitable and specific measures (s. 36).",
            "Section 117: Recognise the data subject's right to bring a 'data protection action' in the Circuit Court or High Court for infringement, including compensation for material and non-material damage, injunctions and declarations.",
            "Sections 142-143: DPC administrative fines are subject to court confirmation in uncontested cases and statutory appeal rights.",
            "Section 41: Further processing for compatible purposes (e.g. legal claims) within statutory bounds.",
        ],
        required_assessments=["Main Establishment & DPC LSA Determination (Art. 56)", "Health Research Regulations Compliance Assessment", "DPIA per DPC Art. 35(4) list", "Children's Data Fundamentals Review (DPC 'Fundamentals for a Child-Oriented Approach', 2021)"],
        response_deadlines=_gdpr_deadlines(),
        notification_requirements=["DPC: personal data breach within 72h (Art. 33 GDPR) via DPC breach webform", "DPC: DPO contact details"],
        required_evidence=["Main-establishment determination memo", "Health research explicit consent records or HRCDC declaration", "Ethics committee approvals", "Children's age-assurance and default-settings evidence"],
        approval_requirements=["Counsel sign-off on main-establishment / LSA position", "Research ethics committee approval before health research processing"],
        competent_regulator="Data Protection Commission (DPC)",
        subnational_regulators={"DPC": "https://www.dataprotection.ie", "HRCDC": "https://hrcdc.ie"},
        regulatory_status=RegulatoryStatus.EFFECTIVE,
        deployment_status=DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.VERIFIED,
        rule_version=RULE_VERSION,
        domain_category="privacy",
    )


# ---------------------------------------------------------------------------
# 5. PUBLIC API
# ---------------------------------------------------------------------------

_SPECIALISED_BUILDERS = {
    "EU-DE": [_de_bdsg, _de_patient_health, _de_tdddg],
    "EU-FR": [_fr_lil],
    "EU-IE": [_ie_dpa2018],
}

# Member States whose cookie rules are carried by a specialised pack rather than a generated -EPRIVACY pack.
_EPRIVACY_COVERED_BY_SPECIALISED = {"EU-DE", "EU-FR"}


def get_eu_regulations() -> List[CanonicalRegulation]:
    """Return every EU-wide and Member-State canonical regulation in this pack."""
    regulations: List[CanonicalRegulation] = [
        _eu_gdpr(),
        _eu_eprivacy(),
        _eu_ai_act(),
        _eu_nis2(),
        _eu_dora(),
        _eu_eudpr_led(),
    ]
    for code, variation in EU_MEMBER_STATE_VARIATIONS.items():
        builders = _SPECIALISED_BUILDERS.get(code)
        if builders:
            regulations.extend(build() for build in builders)
        else:
            regulations.append(_national_gdpr_pack(code, variation))
        if code not in _EPRIVACY_COVERED_BY_SPECIALISED:
            regulations.append(_national_eprivacy_pack(code, variation))
    return regulations


__all__ = ["get_eu_regulations", "EU_MEMBER_STATE_VARIATIONS"]
