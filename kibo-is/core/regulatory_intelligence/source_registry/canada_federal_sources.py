"""
KIBO Privacy OS — Canadian Federal Laws & Regulatory Amendment Discovery Registry (G06)

Authoritative bilingual (English `en` and French `fr`) Canadian federal legal sources:
- Department of Justice Canada Consolidated Acts & Regulations XML (`laws-lois.justice.gc.ca`)
  covering PIPEDA (`P-8.6.xml`), Privacy Act (`P-21.xml`), Access to Information Act (`A-1.xml`),
  and Canada's Anti-Spam Legislation / CASL (`E-1.6.xml`).
- Parliament of Canada LEGISinfo Federal Bills (`parl.ca`)
- Canada Gazette Part I & Part II Official Regulations (`gazette.gc.ca`)
- Treasury Board of Canada Secretariat (TBS) Privacy Directives & PIA Policy (`canada.ca`)
- Office of the Superintendent of Financial Institutions (OSFI) Guideline B-13 & Cyber/Third-Party Risk (`osfi-bsif.gc.ca`)

Includes co-authoritative English and French statutory passages (Section 18 of the Constitution Act, 1982
and Official Languages Act) for deterministic validation under RD-01 and RD-08.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    RegulatorySourceEntry,
    SourceHealthStatus,
)


CANADA_FEDERAL_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-JUSTICE-PIPEDA-EN",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice Canada — Consolidated Acts (PIPEDA, English)",
        authority_type="legislature",
        official_domain="laws-lois.justice.gc.ca",
        discovery_endpoint="https://laws-lois.justice.gc.ca/eng/XML/P-8.6.xml",
        feed_format="xml_justice_ca",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — Crown Copyright free reproduction with attribution",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "breach_notification",
            "commercial_electronic_processing",
            "cross_border_accountability",
        ],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="PIPEDA-S.C.2000-c.5-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-JUSTICE-PIPEDA-FR",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Ministère de la Justice Canada — Lois codifiées (LPRPDE, Français)",
        authority_type="legislature",
        official_domain="laws-lois.justice.gc.ca",
        discovery_endpoint="https://laws-lois.justice.gc.ca/fra/XML/P-8.6.xml",
        feed_format="xml_justice_ca",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Décret sur la reproduction de la législation fédérale (TR/97-5) — Droit d'auteur de la Couronne",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "breach_notification",
            "commercial_electronic_processing",
            "cross_border_accountability",
        ],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["fr", "en"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LPRPDE-L.C.2000-ch.5-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-JUSTICE-PRIVACY-ACT",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice Canada — Privacy Act / Loi sur la protection des renseignements personnels",
        authority_type="legislature",
        official_domain="laws-lois.justice.gc.ca",
        discovery_endpoint="https://laws-lois.justice.gc.ca/eng/XML/P-21.xml",
        feed_format="xml_justice_ca",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — Crown Copyright free reproduction with attribution",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "public_sector_data_protection",
            "personal_information_banks",
            "federal_government_institutions",
        ],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="PRIVACY-ACT-R.S.C.1985-c.P-21-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-JUSTICE-ATIA",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice Canada — Access to Information Act / Loi sur l'accès à l'information",
        authority_type="legislature",
        official_domain="laws-lois.justice.gc.ca",
        discovery_endpoint="https://laws-lois.justice.gc.ca/eng/XML/A-1.xml",
        feed_format="xml_justice_ca",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — Crown Copyright free reproduction with attribution",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "access_to_information",
            "privacy",
            "government_transparency",
            "personal_information_exemption",
        ],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ATIA-R.S.C.1985-c.A-1-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-JUSTICE-CASL",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice Canada — Canada's Anti-Spam Legislation (CASL)",
        authority_type="legislature",
        official_domain="laws-lois.justice.gc.ca",
        discovery_endpoint="https://laws-lois.justice.gc.ca/eng/XML/E-1.6.xml",
        feed_format="xml_justice_ca",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — Crown Copyright free reproduction with attribution",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "electronic_communications",
            "consent_management",
            "commercial_electronic_messages",
            "computer_program_installation",
            "privacy",
        ],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CASL-S.C.2010-c.23-E-1.6-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-PARL-LEGISINFO",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Parliament of Canada — LEGISinfo Federal Bills",
        authority_type="legislature",
        official_domain="parl.ca",
        discovery_endpoint="https://www.parl.ca/legisinfo/en/bills/json",
        feed_format="api_json",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Parliament of Canada Open Data Licence — attribution required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "artificial_intelligence",
            "cybersecurity",
            "legislative_amendments",
        ],
        legal_instrument_types=["legislative_bill"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="PARL-45-1-LEGISINFO-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-GAZETTE-P2",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="King's Printer for Canada — Canada Gazette Part I & Part II Official Regulations",
        authority_type="official_gazette",
        official_domain="gazette.gc.ca",
        discovery_endpoint="https://www.gazette.gc.ca/rss/p2-eng.xml",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Canada / Reproduction of Federal Law Order (SI/97-5)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "breach_of_security_safeguards_regulations",
            "data_protection",
            "cybersecurity",
            "orders_in_council",
        ],
        legal_instrument_types=["regulation", "regulatory_consultation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CG-P2-Vol160-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-TBS-PRIVACY-DIRECTIVES",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Treasury Board of Canada Secretariat (TBS) — Privacy Directives & PIA Policy",
        authority_type="sector_regulator",
        official_domain="canada.ca",
        discovery_endpoint="https://www.canada.ca/en/treasury-board-secretariat/services/access-information-privacy/privacy/privacy-policies-guidance.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Open Government Licence — Canada (OGL-Canada-2.0)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=[
            "privacy_impact_assessment",
            "directive_on_privacy_practices",
            "automated_decision_making",
            "government_privacy_governance",
        ],
        legal_instrument_types=["official_policy_directive", "official_guidance"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="TBS-DIRECTIVE-PRIVACY-PRACTICES-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-OSFI-B13-CYBER",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Superintendent of Financial Institutions (OSFI) — Guideline B-13 & B-10",
        authority_type="sector_regulator",
        official_domain="osfi-bsif.gc.ca",
        discovery_endpoint="https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/technology-cyber-risk-management-guideline-b-13",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Crown Copyright — Office of the Superintendent of Financial Institutions Canada",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=[
            "cybersecurity",
            "technology_risk_management",
            "third_party_risk_management",
            "financial_sector_data_governance",
        ],
        legal_instrument_types=["official_guidance", "official_policy_directive"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 0, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="OSFI-B13-B10-2026-10",
    ),
]


AUTHENTIC_CANADA_FEDERAL_FIXTURES: Dict[str, Dict[str, Any]] = {
    "PIPEDA-S10.1-BREACH-SAFEGUARDS": {
        "document_id": "DOC-CA-FED-PIPEDA-2000-C5-S10.1",
        "jurisdiction_id": "CA-FED",
        "official_citation_en": "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, s. 10.1",
        "official_citation_fr": "Loi sur la protection des renseignements personnels et les documents électroniques, L.C. 2000, ch. 5, art. 10.1",
        "source_id_en": "SRC-CA-FED-JUSTICE-PIPEDA-EN",
        "source_id_fr": "SRC-CA-FED-JUSTICE-PIPEDA-FR",
        "official_source_url_en": "https://laws-lois.justice.gc.ca/eng/XML/P-8.6.xml",
        "official_source_url_fr": "https://laws-lois.justice.gc.ca/fra/XML/P-8.6.xml",
        "translation_status": "official_bilingual_coauthoritative",
        "section": "10.1",
        "subsections": ["10.1(1)", "10.1(3)", "10.1(4)", "10.1(7)", "10.3(1)"],
        "Effective_date": "2018-11-01",
        "exact_text_en": (
            "10.1 (1) An organization shall report to the Commissioner any breach of security safeguards "
            "involving personal information under its control if it is reasonable in the circumstances to "
            "believe that the breach creates a real risk of significant harm to an individual.\n"
            "(2) The report shall contain the prescribed information and shall be made in the prescribed form "
            "and manner as soon as feasible after the organization determines that the breach has occurred.\n"
            "(3) Unless otherwise prohibited by law, an organization shall notify an individual of any breach "
            "of security safeguards involving the individual’s personal information under the organization’s "
            "control if it is reasonable in the circumstances to believe that the breach creates a real risk "
            "of significant harm to the individual.\n"
            "(7) In this section, significant harm includes bodily harm, humiliation, damage to reputation or "
            "relationships, loss of employment, business or professional opportunities, financial loss, "
            "identity theft, negative effects on the credit record and damage to or loss of property."
        ),
        "exact_text_fr": (
            "10.1 (1) L’organisation déclare au commissaire toute atteinte aux mesures de sécurité qui a "
            "trait à des renseignements personnels dont elle a la gestion s’il est raisonnable de croire, "
            "dans les circonstances, que l’atteinte présente un risque réel de préjudice grave à l’endroit "
            "d’un individu.\n"
            "(2) La déclaration contient les renseignements réglementaires et est faite en la forme et selon "
            "les modalités réglementaires le plus tôt possible après que l’organisation conclut qu’il y a eu "
            "atteinte.\n"
            "(3) Sauf règle de droit contraire, l’organisation avise un individu de toute atteinte aux mesures "
            "de sécurité qui a trait à des renseignements personnels le concernant et dont elle a la gestion "
            "s’il est raisonnable de croire, dans les circonstances, que l’atteinte présente un risque réel de "
            "préjudice grave à son endroit.\n"
            "(7) Au présent article, préjudice grave s’entend notamment de la lésion corporelle, de "
            "l’humiliation, du dommage à la réputation ou aux relations, de la perte de possibilités d’emploi "
            "ou d’occasions d’affaires ou d’activités professionnelles, de la perte financière, du vol "
            "d’identité, de l’effet négatif sur le dossier de crédit et du dommage aux biens ou de leur perte."
        ),
        "coauthoritative_alignment": {
            "real_risk_of_significant_harm": "risque réel de préjudice grave",
            "breach_of_security_safeguards": "atteinte aux mesures de sécurité",
            "as_soon_as_feasible": "le plus tôt possible",
            "under_its_control": "dont elle a la gestion",
        },
        "rd_validation_tags": ["RD-01", "RD-08"],
    },
    "PIPEDA-SCHEDULE1-PRINCIPLE-4.1.3-ACCOUNTABILITY": {
        "document_id": "DOC-CA-FED-PIPEDA-2000-C5-SCH1-4.1.3",
        "jurisdiction_id": "CA-FED",
        "official_citation_en": "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, Schedule 1, Clause 4.1.3",
        "official_citation_fr": "Loi sur la protection des renseignements personnels et les documents électroniques, L.C. 2000, ch. 5, Annexe 1, art. 4.1.3",
        "source_id_en": "SRC-CA-FED-JUSTICE-PIPEDA-EN",
        "source_id_fr": "SRC-CA-FED-JUSTICE-PIPEDA-FR",
        "official_source_url_en": "https://laws-lois.justice.gc.ca/eng/XML/P-8.6.xml",
        "official_source_url_fr": "https://laws-lois.justice.gc.ca/fra/XML/P-8.6.xml",
        "translation_status": "official_bilingual_coauthoritative",
        "section": "Schedule 1, Clause 4.1.3",
        "Effective_date": "2001-01-01",
        "exact_text_en": (
            "4.1.3 An organization is responsible for personal information in its possession or custody, "
            "including information that has been transferred to a third party for processing. The organization "
            "shall use contractual or other means to provide a comparable level of protection while the "
            "information is being processed by a third party."
        ),
        "exact_text_fr": (
            "4.1.3 Une organisation est responsable des renseignements personnels qu’elle a en sa possession "
            "ou sous sa garde, y compris les renseignements confiés à une tierce partie aux fins de "
            "traitement. L’organisation doit, par voie contractuelle ou autre, assurer un degré comparable "
            "de protection aux renseignements qui sont en cours de traitement par une tierce partie."
        ),
        "coauthoritative_alignment": {
            "transferred_to_a_third_party_for_processing": "confiés à une tierce partie aux fins de traitement",
            "comparable_level_of_protection": "degré comparable de protection",
            "contractual_or_other_means": "par voie contractuelle ou autre",
        },
        "rd_validation_tags": ["RD-01", "RD-08"],
    },
    "PRIVACY-ACT-RSC-1985-P21-S4-S8": {
        "document_id": "DOC-CA-FED-PRIVACY-ACT-1985-P21-S4-S8",
        "jurisdiction_id": "CA-FED",
        "official_citation_en": "Privacy Act, R.S.C., 1985, c. P-21, ss. 4, 7, 8",
        "official_citation_fr": "Loi sur la protection des renseignements personnels, L.R.C. (1985), ch. P-21, art. 4, 7, 8",
        "source_id_en": "SRC-CA-FED-JUSTICE-PRIVACY-ACT",
        "source_id_fr": "SRC-CA-FED-JUSTICE-PRIVACY-ACT",
        "official_source_url_en": "https://laws-lois.justice.gc.ca/eng/XML/P-21.xml",
        "official_source_url_fr": "https://laws-lois.justice.gc.ca/fra/XML/P-21.xml",
        "translation_status": "official_bilingual_coauthoritative",
        "section": "4, 7, 8",
        "Effective_date": "1983-07-01",
        "exact_text_en": (
            "4 No personal information shall be collected by a government institution unless it relates "
            "directly to an operating program or activity of the institution.\n"
            "7 Personal information under the control of a government institution shall not, without the "
            "consent of the individual to whom it relates, be used by the institution except\n"
            "(a) for the purpose for which the information was obtained or compiled by the institution or "
            "for a use consistent with that purpose; or\n"
            "(b) for a purpose for which the information may be disclosed to the institution under "
            "subsection 8(2).\n"
            "8 (1) Personal information under the control of a government institution shall not, without "
            "the consent of the individual to whom it relates, be disclosed by the institution except in "
            "accordance with this section."
        ),
        "exact_text_fr": (
            "4 Les seuls renseignements personnels que peut recueillir une institution fédérale sont ceux "
            "qui ont un lien direct avec ses programmes ou ses activités.\n"
            "7 À défaut de consentement de l’individu concerné, les renseignements personnels relevant d’une "
            "institution fédérale ne peuvent servir à celle-ci :\n"
            "a) qu’aux fins auxquelles ils ont été recueillis ou préparés par l’institution de même que "
            "pour les usages qui sont compatibles avec ces fins;\n"
            "b) qu’aux fins auxquelles ils peuvent lui être communiqués en vertu du paragraphe 8(2).\n"
            "8 (1) Les renseignements personnels qui relèvent d’une institution fédérale ne peuvent être "
            "communiqués, à défaut du consentement de l’individu qu’ils concernent, que conformément au "
            "présent article."
        ),
        "coauthoritative_alignment": {
            "government_institution": "institution fédérale",
            "relates_directly_to_an_operating_program_or_activity": "lien direct avec ses programmes ou ses activités",
            "use_consistent_with_that_purpose": "usages qui sont compatibles avec ces fins",
        },
        "rd_validation_tags": ["RD-01", "RD-08"],
    },
}


def get_canada_federal_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of all curated Canadian federal legal and regulatory sources."""
    return list(CANADA_FEDERAL_SOURCES)
