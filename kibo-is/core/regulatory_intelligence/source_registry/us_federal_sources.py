"""
KIBO Privacy OS — US Federal Legislative & Regulatory Source Discovery Registry (G01)
Curated, authoritative RegulatorySourceEntry records and verbatim statutory/regulatory
fixtures for deterministic discovery, SHA-256 verification, and passage extraction.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    RegulatorySourceEntry,
    SourceHealthStatus,
    compute_sha256_hex,
)

# ---------------------------------------------------------------------------
# Verbatim Official Statutory & Regulatory Text Fixtures (RD-01 Deterministic)
# ---------------------------------------------------------------------------

_HIPAA_45_CFR_164_404_TEXT = (
    "§ 164.404 Notification to individuals.\n"
    "(a) Standard—(1) General rule. A covered entity shall, following the discovery of a "
    "breach of unsecured protected health information, notify each individual whose "
    "unsecured protected health information has been, or is reasonably believed by the "
    "covered entity to have been, accessed, acquired, used, or disclosed as a result of "
    "such breach.\n"
    "(b) Implementation specifications: Timeliness of notification. Except as provided in "
    "§ 164.412, a covered entity shall provide the notification required by paragraph (a) "
    "of this section without unreasonable delay and in no case later than 60 calendar days "
    "after discovery of a breach."
)

_HIPAA_45_CFR_164_408_TEXT = (
    "§ 164.408 Notification to the Secretary.\n"
    "(a) Standard. A covered entity shall, following the discovery of a breach of unsecured "
    "protected health information, notify the Secretary.\n"
    "(b) Implementation specifications: Breaches involving 500 or more individuals. For "
    "breaches of unsecured protected health information involving 500 or more individuals, "
    "a covered entity shall, except as provided in § 164.412, provide the notification "
    "required by paragraph (a) of this section contemporaneously with the notice required "
    "by § 164.404(a) and in the manner specified on the HHS Web site.\n"
    "(c) Implementation specifications: Breaches involving less than 500 individuals. For "
    "breaches of unsecured protected health information involving less than 500 individuals, "
    "a covered entity shall maintain a log or other documentation of such breaches and, not "
    "later than 60 days after the end of each calendar year, provide the notification "
    "required by paragraph (a) of this section for breaches discovered during the preceding "
    "calendar year, in the manner specified on the HHS Web site."
)

_COPPA_16_CFR_312_5_TEXT = (
    "§ 312.5 Parental consent.\n"
    "(a) General requirements. (1) An operator is required to obtain verifiable parental "
    "consent before any collection, use, or disclosure of personal information from "
    "children, including consent to any material change in the collection, use, or "
    "disclosure practices to which the parent has previously consented.\n"
    "(2) An operator must give the parent the option to consent to the collection and use "
    "of the child's personal information without consenting to disclosure of his or her "
    "personal information to third parties."
)

_FTC_ACT_15_USC_45_TEXT = (
    "15 U.S.C. § 45 - Unfair methods of competition unlawful; prevention by Commission\n"
    "(a) Declaration of unlawfulness; power to prohibit unfair practices; inapplicability "
    "to foreign trade\n"
    "(1) Unfair methods of competition in or affecting commerce, and unfair or deceptive "
    "acts or practices in or affecting commerce, are hereby declared unlawful.\n"
    "(2) The Commission is hereby empowered and directed to prevent persons, partnerships, "
    "or corporations, except banks, savings and loan institutions described in section "
    "57a(f)(3) of this title, Federal credit unions described in section 57a(f)(4) of this "
    "title, common carriers subject to the Acts to regulate commerce, air carriers and "
    "foreign air carriers subject to part A of subtitle VII of title 49, and persons, "
    "partnerships, or corporations insofar as they are subject to the Packers and "
    "Stockyards Act, 1921, as amended, except as provided in section 406(b) of said Act, "
    "from using unfair methods of competition in or affecting commerce and unfair or "
    "deceptive acts or practices in or affecting commerce."
)

_GLBA_15_USC_6802_TEXT = (
    "15 U.S.C. § 6802 - Obligations with respect to disclosures of personal information\n"
    "(a) Notice requirements\n"
    "Except as otherwise provided in this subchapter, a financial institution may not, "
    "directly or through any affiliate, disclose to a nonaffiliated third party any "
    "nonpublic personal information, unless such financial institution provides or has "
    "provided to the consumer a notice that complies with section 6803 of this title.\n"
    "(b) Opt out\n"
    "(1) In general\n"
    "A financial institution may not disclose nonpublic personal information to a "
    "nonaffiliated third party unless—\n"
    "(A) such financial institution clearly and conspicuously discloses to the consumer, "
    "in writing or in electronic form or other form permitted by the regulations "
    "prescribed under section 6804 of this title, that such information may be disclosed "
    "to such third party;\n"
    "(B) the consumer is given the opportunity, before the time that such information is "
    "initially disclosed, to direct that such information not be disclosed to such third "
    "party; and\n"
    "(C) the consumer is given an explanation of how the consumer can exercise that "
    "nondisclosure option."
)

_FERPA_34_CFR_99_30_TEXT = (
    "§ 99.30 Under what conditions is prior consent required to disclose information?\n"
    "(a) The parent or eligible student shall provide a signed and dated written consent "
    "before an educational agency or institution discloses personally identifiable "
    "information from the student's education records, except as provided in § 99.31.\n"
    "(b) The written consent must:\n"
    "(1) Specify the records that may be disclosed;\n"
    "(2) State the purpose of the disclosure; and\n"
    "(3) Identify the party or class of parties to whom the disclosure may be made."
)

_PRIVACY_ACT_5_USC_552A_TEXT = (
    "5 U.S.C. § 552a - Records maintained on individuals\n"
    "(b) Conditions of Disclosure.—No agency shall disclose any record which is contained "
    "in a system of records by any means of communication to any person, or to another "
    "agency, except pursuant to a written request by, or with the prior written consent "
    "of, the individual to whom the record pertains, unless disclosure of the record "
    "would be—\n"
    "(1) to those officers and employees of the agency which maintains the record who "
    "have a need for the record in the performance of their duties;"
)


AUTHENTIC_US_FEDERAL_FIXTURES: Dict[str, Dict[str, Any]] = {
    "45_CFR_164_404": {
        "document_id": "DOC-US-FED-ECFR-45-164-404",
        "source_id": "SRC-US-FED-ECFR",
        "jurisdiction_id": "US-FED",
        "official_citation": "45 CFR § 164.404",
        "canonical_title": "HIPAA Breach Notification Rule — Notification to Individuals (45 CFR § 164.404)",
        "issuing_authority": "U.S. Department of Health and Human Services (HHS)",
        "official_source_url": "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-D/section-164.404",
        "document_type": "regulation",
        "effective_date": "2009-09-23",
        "Statutory_deadline": "60 calendar days",
        "verbatim_text": _HIPAA_45_CFR_164_404_TEXT,
        "sha256": compute_sha256_hex(_HIPAA_45_CFR_164_404_TEXT),
    },
    "45_CFR_164_408": {
        "document_id": "DOC-US-FED-ECFR-45-164-408",
        "source_id": "SRC-US-FED-ECFR",
        "jurisdiction_id": "US-FED",
        "official_citation": "45 CFR § 164.408",
        "canonical_title": "HIPAA Breach Notification Rule — Notification to the Secretary (45 CFR § 164.408)",
        "issuing_authority": "U.S. Department of Health and Human Services (HHS)",
        "official_source_url": "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-D/section-164.408",
        "document_type": "regulation",
        "effective_date": "2009-09-23",
        "thresholds": {"contemporaneous_secretary_notice_individuals": 500},
        "verbatim_text": _HIPAA_45_CFR_164_408_TEXT,
        "sha256": compute_sha256_hex(_HIPAA_45_CFR_164_408_TEXT),
    },
    "16_CFR_312_5": {
        "document_id": "DOC-US-FED-ECFR-16-312-5",
        "source_id": "SRC-US-FED-ECFR",
        "jurisdiction_id": "US-FED",
        "official_citation": "16 CFR § 312.5",
        "canonical_title": "Children's Online Privacy Protection Rule — Parental Consent (16 CFR § 312.5)",
        "issuing_authority": "Federal Trade Commission (FTC)",
        "official_source_url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312/section-312.5",
        "document_type": "regulation",
        "effective_date": "2013-07-01",
        "verbatim_text": _COPPA_16_CFR_312_5_TEXT,
        "sha256": compute_sha256_hex(_COPPA_16_CFR_312_5_TEXT),
    },
    "15_USC_45": {
        "document_id": "DOC-US-FED-GOVINFO-15-USC-45",
        "source_id": "SRC-US-FED-GOVINFO",
        "jurisdiction_id": "US-FED",
        "official_citation": "15 U.S.C. § 45",
        "canonical_title": "Federal Trade Commission Act Section 5 — Unfair or Deceptive Acts or Practices (15 U.S.C. § 45)",
        "issuing_authority": "United States Congress",
        "official_source_url": "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap2-subchapI-sec45",
        "document_type": "statute",
        "effective_date": "1914-09-26",
        "verbatim_text": _FTC_ACT_15_USC_45_TEXT,
        "sha256": compute_sha256_hex(_FTC_ACT_15_USC_45_TEXT),
    },
    "15_USC_6802": {
        "document_id": "DOC-US-FED-GOVINFO-15-USC-6802",
        "source_id": "SRC-US-FED-GOVINFO",
        "jurisdiction_id": "US-FED",
        "official_citation": "15 U.S.C. § 6802",
        "canonical_title": "Gramm-Leach-Bliley Act — Obligations with Respect to Disclosures of Personal Information (15 U.S.C. § 6802)",
        "issuing_authority": "United States Congress",
        "official_source_url": "https://www.govinfo.gov/app/details/USCODE-2023-title15/USCODE-2023-title15-chap94-subchapI-sec6802",
        "document_type": "statute",
        "effective_date": "1999-11-12",
        "verbatim_text": _GLBA_15_USC_6802_TEXT,
        "sha256": compute_sha256_hex(_GLBA_15_USC_6802_TEXT),
    },
    "34_CFR_99_30": {
        "document_id": "DOC-US-FED-ECFR-34-99-30",
        "source_id": "SRC-US-FED-ECFR",
        "jurisdiction_id": "US-FED",
        "official_citation": "34 CFR § 99.30",
        "canonical_title": "Family Educational Rights and Privacy Act (FERPA) — Prior Consent Conditions (34 CFR § 99.30)",
        "issuing_authority": "U.S. Department of Education",
        "official_source_url": "https://www.ecfr.gov/current/title-34/subtitle-A/part-99/subpart-D/section-99.30",
        "document_type": "regulation",
        "effective_date": "1988-04-11",
        "verbatim_text": _FERPA_34_CFR_99_30_TEXT,
        "sha256": compute_sha256_hex(_FERPA_34_CFR_99_30_TEXT),
    },
    "5_USC_552A": {
        "document_id": "DOC-US-FED-GOVINFO-5-USC-552A",
        "source_id": "SRC-US-FED-GOVINFO",
        "jurisdiction_id": "US-FED",
        "official_citation": "5 U.S.C. § 552a",
        "canonical_title": "Privacy Act of 1974 — Records Maintained on Individuals (5 U.S.C. § 552a)",
        "issuing_authority": "United States Congress",
        "official_source_url": "https://www.govinfo.gov/app/details/USCODE-2023-title5/USCODE-2023-title5-partI-chap5-subchapII-sec552a",
        "document_type": "statute",
        "effective_date": "1974-12-31",
        "verbatim_text": _PRIVACY_ACT_5_USC_552A_TEXT,
        "sha256": compute_sha256_hex(_PRIVACY_ACT_5_USC_552A_TEXT),
    },
}


# ---------------------------------------------------------------------------
# Authoritative US Federal Regulatory Source Entries
# ---------------------------------------------------------------------------

US_FEDERAL_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-US-FED-FR",
        jurisdiction_id="US-FED",
        parent_jurisdiction=None,
        authority_name="National Archives and Records Administration (NARA) — Office of the Federal Register",
        authority_type="official_gazette",
        official_domain="federalregister.gov",
        discovery_endpoint="https://www.federalregister.gov/api/v1/documents.json",
        feed_format="api_json",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="17 U.S.C. § 105 — US Government Works in the Public Domain",
        rate_limit_rpm=60,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "healthcare_privacy",
            "financial_privacy",
            "children_privacy",
            "ai_governance",
            "telecommunications_privacy",
        ],
        legal_instrument_types=[
            "regulation",
            "official_guidance",
            "regulatory_consultation",
            "official_policy_directive",
        ],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="fr-2026-10-25-v1",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-ECFR",
        jurisdiction_id="US-FED",
        parent_jurisdiction=None,
        authority_name=(
            "Government Publishing Office (GPO) & Office of the Federal Register — "
            "Electronic Code of Federal Regulations (45 CFR Parts 160/164 HIPAA, "
            "16 CFR Parts 312/313/314 COPPA/GLBA, 34 CFR Part 99 FERPA, 12 CFR Part 1016 Reg P)"
        ),
        authority_type="official_gazette",
        official_domain="ecfr.gov",
        discovery_endpoint="https://www.ecfr.gov/api/versioner/v1/titles.json",
        feed_format="api_json",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="17 U.S.C. § 105 — US Government Works in the Public Domain",
        rate_limit_rpm=60,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "hipaa_45_cfr_160_164",
            "coppa_16_cfr_312",
            "glba_16_cfr_313_314",
            "ferpa_34_cfr_99",
            "reg_p_12_cfr_1016",
        ],
        legal_instrument_types=["regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ecfr-titles-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-GOVINFO",
        jurisdiction_id="US-FED",
        parent_jurisdiction=None,
        authority_name=(
            "U.S. Government Publishing Office (GPO) — GovInfo Bulk Data & USLM Statutes "
            "(HIPAA/HITECH, GLBA, FTC Act § 5, FCRA, Privacy Act of 1974, E-Government Act § 208, CIRCIA)"
        ),
        authority_type="legislature",
        official_domain="govinfo.gov",
        discovery_endpoint="https://api.govinfo.gov/collections",
        feed_format="xml_akoma_ntoso",
        auth_requirements="api_key",
        licensing_and_reuse="17 U.S.C. § 105 — US Government Works in the Public Domain",
        rate_limit_rpm=40,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "hipaa_hitech",
            "glba",
            "ftc_act_section_5",
            "fcra",
            "privacy_act_1974",
            "e_government_act_208",
            "circia",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="govinfo-uscode-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-CONGRESS",
        jurisdiction_id="US-FED",
        parent_jurisdiction=None,
        authority_name="Library of Congress — Congress.gov Legislative Bills & Amendments",
        authority_type="legislature",
        official_domain="api.congress.gov",
        discovery_endpoint="https://api.congress.gov/v3/bill",
        feed_format="api_json",
        auth_requirements="api_key",
        licensing_and_reuse="17 U.S.C. § 105 — US Government Works in the Public Domain",
        rate_limit_rpm=40,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "ai_governance",
            "federal_legislative_bills",
        ],
        legal_instrument_types=["legislative_bill", "statute"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="congress-119-bills-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-NIST",
        jurisdiction_id="US-FED",
        parent_jurisdiction=None,
        authority_name="National Institute of Standards and Technology (NIST) — AI RMF & Privacy Framework",
        authority_type="sector_regulator",
        official_domain="csrc.nist.gov",
        discovery_endpoint="https://csrc.nist.gov/publications/rss",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="17 U.S.C. § 105 — US Government Works in the Public Domain",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "ai_risk_management_framework",
            "nist_privacy_framework",
            "sp_800_53",
        ],
        legal_instrument_types=["official_guidance", "official_policy_directive"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="nist-csrc-rss-2026-10-25",
    ),
]


def get_us_federal_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of the curated US Federal legislative and regulatory sources."""
    return [entry.model_copy(deep=True) for entry in US_FEDERAL_SOURCES]


def get_authentic_us_federal_fixtures() -> Dict[str, Dict[str, Any]]:
    """Return verbatim US Federal statutory and regulatory fixtures with SHA-256 hashes."""
    return dict(AUTHENTIC_US_FEDERAL_FIXTURES)
