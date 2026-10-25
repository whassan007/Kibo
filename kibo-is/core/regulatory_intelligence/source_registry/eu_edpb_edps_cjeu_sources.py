"""
KIBO Privacy OS — EU EDPB, EDPS & CJEU Source Registry and Authentic Decision Fixtures (Worker G14)

Covers:
1. Court of Justice of the European Union (CJEU / InfoCuria `curia.europa.eu`):
   - Binding judicial rulings (`court_judgment`), ECLI identifiers, preliminary rulings interpreting GDPR.
2. European Data Protection Board (EDPB `edpb.europa.eu`):
   - Article 65 GDPR binding dispute-resolution decisions (`regulatory_enforcement_decision`).
   - Article 70 GDPR guidelines, recommendations, and best practices (`official_guidance`).
   - Strictly distinguishes non-legislative EDPB guidance (`official_guidance`) from EU statutes/regulations
     (`statute` / `regulation`) and binding CJEU judicial judgments (`court_judgment`).
3. European Data Protection Supervisor (EDPS `edps.europa.eu`):
   - Supervisory opinions, formal comments, and enforcement/supervisory decisions for EU institutions
     under Regulation (EU) 2018/1725 (`official_guidance` and `regulatory_enforcement_decision`).
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.regulatory_intelligence import (
    DocumentClassType,
    RegulatorySourceEntry,
    SourceHealthStatus,
)


EU_EDPB_EDPS_CJEU_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-EU-CJEU-INFOCURIA",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="Court of Justice of the European Union (CJEU)",
        authority_type="court",
        official_domain="curia.europa.eu",
        discovery_endpoint="https://curia.europa.eu/juris/recherche.jsf?language=en",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="CJEU Official Case-Law Reuse Policy — free reproduction with ECLI attribution",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "fundamental_rights",
            "cross_border_transfers",
            "automated_decision_making",
            "non_material_damage",
        ],
        legal_instrument_types=[
            DocumentClassType.COURT_JUDGMENT.value,
        ],
        source_priority=1,
        languages=[
            "bg", "es", "cs", "da", "de", "et", "el", "en", "fr", "ga",
            "hr", "it", "lv", "lt", "hu", "mt", "nl", "pl", "pt", "ro",
            "sk", "sl", "fi", "sv",
        ],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-CJEU-EURLEX-CASELAW",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="Court of Justice of the European Union (EUR-Lex Sector 6 Case-Law / CELLAR)",
        authority_type="court",
        official_domain="eur-lex.europa.eu",
        discovery_endpoint="https://publications.europa.eu/webapi/rdf/sparql",
        feed_format="cellar_rdf",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="EU Decision 2011/833/EU — official ECLI & CELEX case-law metadata and texts",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "fundamental_rights",
            "electronic_communications",
        ],
        legal_instrument_types=[
            DocumentClassType.COURT_JUDGMENT.value,
        ],
        source_priority=1,
        languages=[
            "bg", "es", "cs", "da", "de", "et", "el", "en", "fr", "ga",
            "hr", "it", "lv", "lt", "hu", "mt", "nl", "pl", "pt", "ro",
            "sk", "sl", "fi", "sv",
        ],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-EDPB-ART65-DECISIONS",
        jurisdiction_id="EU",
        parent_jurisdiction="EU",
        authority_name="European Data Protection Board (EDPB)",
        authority_type="data_protection_authority",
        official_domain="edpb.europa.eu",
        discovery_endpoint="https://www.edpb.europa.eu/our-work-tools/consistency-findings/binding-decisions_en",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="EDPB Legal Notice — reproduction authorized with source acknowledgment",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "gdpr_consistency_mechanism",
            "cross_border_enforcement",
            "administrative_fines",
        ],
        legal_instrument_types=[
            DocumentClassType.REGULATORY_ENFORCEMENT_DECISION.value,
        ],
        source_priority=1,
        languages=["en", "fr", "de"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-EDPB-ART70-GUIDELINES",
        jurisdiction_id="EU",
        parent_jurisdiction="EU",
        authority_name="European Data Protection Board (EDPB)",
        authority_type="data_protection_authority",
        official_domain="edpb.europa.eu",
        discovery_endpoint="https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="EDPB Legal Notice — reproduction authorized with source acknowledgment",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "international_transfers",
            "supplementary_measures",
            "consent",
            "dark_patterns",
            "ai_data_protection",
        ],
        legal_instrument_types=[
            DocumentClassType.OFFICIAL_GUIDANCE.value,
            DocumentClassType.REGULATORY_CONSULTATION.value,
        ],
        source_priority=1,
        languages=[
            "bg", "es", "cs", "da", "de", "et", "el", "en", "fr", "ga",
            "hr", "it", "lv", "lt", "hu", "mt", "nl", "pl", "pt", "ro",
            "sk", "sl", "fi", "sv",
        ],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-EDPS-OPINIONS-DECISIONS",
        jurisdiction_id="EU",
        parent_jurisdiction="EU",
        authority_name="European Data Protection Supervisor (EDPS)",
        authority_type="data_protection_authority",
        official_domain="edps.europa.eu",
        discovery_endpoint="https://www.edps.europa.eu/data-protection/our-work/publications_en",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="EDPS Reuse Policy (Decision 2011/833/EU principles) — attribution required",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "eu_institutions_supervision",
            "legislative_opinions",
            "ai_supervision",
        ],
        legal_instrument_types=[
            DocumentClassType.OFFICIAL_GUIDANCE.value,
            DocumentClassType.REGULATORY_ENFORCEMENT_DECISION.value,
            DocumentClassType.OFFICIAL_POLICY_DIRECTIVE.value,
        ],
        source_priority=1,
        languages=["en", "fr", "de"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
]


AUTHENTIC_CJEU_EDPB_FIXTURES: List[Dict[str, Any]] = [
    {
        "document_id": "DOC-EU-CJEU-C-311-18",
        "source_id": "SRC-EU-CJEU-INFOCURIA",
        "document_type": DocumentClassType.COURT_JUDGMENT.value,
        "canonical_title": (
            "Judgment of the Court (Grand Chamber) of 16 July 2020, "
            "Data Protection Commissioner v Facebook Ireland Limited and Maximillian Schrems ('Schrems II')"
        ),
        "case_number": "C-311/18",
        "docket_or_case_number": "C-311/18",
        "ecli": "ECLI:EU:C:2020:559",
        "celex_id": "62018CJ0311",
        "eli_or_celex_identifier": "ECLI:EU:C:2020:559",
        "neutral_citation": "Case C-311/18, ECLI:EU:C:2020:559",
        "jurisdiction_id": "EU",
        "issuing_authority": "Court of Justice of the European Union (Grand Chamber)",
        "issuing_authority_type": "court",
        "official_source_url": "https://curia.europa.eu/juris/liste.jsf?num=C-311/18",
        "decision_date": "2020-07-16",
        "publication_date": "2020-07-16",
        "binding_status": "binding_precedent",
        "is_legislation": False,
        "is_binding_judicial_judgment": True,
        "is_edpb_guidance": False,
        "interpreted_provisions": [
            "GDPR Article 45",
            "GDPR Article 46(1)",
            "GDPR Article 46(2)(c)",
            "GDPR Article 58(2)(f)",
            "GDPR Article 58(2)(j)",
            "Charter of Fundamental Rights Articles 7, 8 and 47",
        ],
        "parties": [
            "Data Protection Commissioner",
            "Facebook Ireland Limited",
            "Maximillian Schrems",
        ],
        "legal_holdings": [
            (
                "Article 46(1) and 46(2)(c) GDPR must be interpreted as meaning that the appropriate safeguards, "
                "enforceable rights and effective legal remedies required by those provisions must ensure that "
                "data subjects whose personal data are transferred to a third country pursuant to standard data "
                "protection clauses are afforded a level of protection essentially equivalent to that guaranteed "
                "within the European Union by the GDPR, read in the light of the Charter."
            ),
            (
                "Commission Implementing Decision (EU) 2016/1250 of 12 July 2016 pursuant to Directive 95/46/EC "
                "of the European Parliament and of the Council on the adequacy of the protection provided by the "
                "EU-US Privacy Shield is invalid."
            ),
            (
                "Controllers and supervisory authorities are required to verify, on a case-by-case basis, whether "
                "the law of the destination third country ensures adequate protection under EU law for data "
                "transferred under Standard Contractual Clauses, and where needed provide supplementary measures "
                "or suspend/prohibit the transfer."
            ),
        ],
        "exact_source_excerpt": (
            "Article 46(1) and Article 46(2)(c) of Regulation 2016/679 must be interpreted as meaning that the "
            "appropriate safeguards, enforceable rights and effective legal remedies required by those provisions "
            "must ensure that data subjects whose personal data are transferred to a third country pursuant to "
            "standard data protection clauses are afforded a level of protection essentially equivalent to that "
            "guaranteed within the European Union by that regulation, read in the light of the Charter."
        ),
    },
    {
        "document_id": "DOC-EU-CJEU-C-300-21",
        "source_id": "SRC-EU-CJEU-INFOCURIA",
        "document_type": DocumentClassType.COURT_JUDGMENT.value,
        "canonical_title": (
            "Judgment of the Court (Third Chamber) of 4 May 2023, "
            "UI v Österreichische Post AG"
        ),
        "case_number": "C-300/21",
        "docket_or_case_number": "C-300/21",
        "ecli": "ECLI:EU:C:2023:370",
        "celex_id": "62021CJ0300",
        "eli_or_celex_identifier": "ECLI:EU:C:2023:370",
        "neutral_citation": "Case C-300/21, ECLI:EU:C:2023:370",
        "jurisdiction_id": "EU",
        "issuing_authority": "Court of Justice of the European Union (Third Chamber)",
        "issuing_authority_type": "court",
        "official_source_url": "https://curia.europa.eu/juris/liste.jsf?num=C-300/21",
        "decision_date": "2023-05-04",
        "publication_date": "2023-05-04",
        "binding_status": "binding_precedent",
        "is_legislation": False,
        "is_binding_judicial_judgment": True,
        "is_edpb_guidance": False,
        "interpreted_provisions": [
            "GDPR Article 82(1)",
        ],
        "parties": [
            "UI",
            "Österreichische Post AG",
        ],
        "legal_holdings": [
            (
                "Article 82(1) GDPR must be interpreted as meaning that the mere infringement of the provisions "
                "of that regulation is not sufficient to confer a right to compensation; the claimant must establish "
                "the existence of material or non-material damage, an infringement of the GDPR, and a causal link "
                "between that damage and that infringement."
            ),
            (
                "Article 82(1) GDPR must be interpreted as precluding a national rule or practice which makes "
                "compensation for non-material damage, within the meaning of that provision, subject to the "
                "condition that the damage suffered by the data subject has reached a certain degree of seriousness."
            ),
            (
                "National courts must apply domestic rules on the financial extent of compensation, provided "
                "the EU principles of equivalence and effectiveness are observed so that compensation is full "
                "and effective for the damage actually suffered."
            ),
        ],
        "exact_source_excerpt": (
            "Article 82(1) of Regulation (EU) 2016/679 of the European Parliament and of the Council of "
            "27 April 2016 on the protection of natural persons with regard to the processing of personal data "
            "and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection "
            "Regulation) must be interpreted as meaning that the mere infringement of the provisions of that "
            "regulation is not sufficient to confer a right to compensation."
        ),
    },
    {
        "document_id": "DOC-EU-CJEU-C-634-21",
        "source_id": "SRC-EU-CJEU-INFOCURIA",
        "document_type": DocumentClassType.COURT_JUDGMENT.value,
        "canonical_title": (
            "Judgment of the Court (First Chamber) of 7 December 2023, "
            "OQ v Land Hessen, joined party: SCHUFA Holding AG"
        ),
        "case_number": "C-634/21",
        "docket_or_case_number": "C-634/21",
        "ecli": "ECLI:EU:C:2023:957",
        "celex_id": "62021CJ0634",
        "eli_or_celex_identifier": "ECLI:EU:C:2023:957",
        "neutral_citation": "Case C-634/21, ECLI:EU:C:2023:957",
        "jurisdiction_id": "EU",
        "issuing_authority": "Court of Justice of the European Union (First Chamber)",
        "issuing_authority_type": "court",
        "official_source_url": "https://curia.europa.eu/juris/liste.jsf?num=C-634/21",
        "decision_date": "2023-12-07",
        "publication_date": "2023-12-07",
        "binding_status": "binding_precedent",
        "is_legislation": False,
        "is_binding_judicial_judgment": True,
        "is_edpb_guidance": False,
        "interpreted_provisions": [
            "GDPR Article 22(1)",
            "GDPR Article 4(4)",
        ],
        "parties": [
            "OQ",
            "Land Hessen",
            "SCHUFA Holding AG",
        ],
        "legal_holdings": [
            (
                "Article 22(1) GDPR must be interpreted as meaning that the automated establishment, by a credit "
                "information agency, of a probability value based on personal data relating to a person and "
                "concerning his or her ability to meet payment commitments in the future constitutes 'automated "
                "individual decision-making' within the meaning of that provision, where a third party, to which "
                "that probability value is transmitted, draws strongly on that probability value to establish, "
                "implement or terminate a contractual relationship with that person."
            ),
        ],
        "exact_source_excerpt": (
            "Article 22(1) of Regulation (EU) 2016/679 of the European Parliament and of the Council of "
            "27 April 2016 on the protection of natural persons with regard to the processing of personal data "
            "and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection "
            "Regulation) must be interpreted as meaning that the automated establishment, by a credit information "
            "agency, of a probability value based on personal data relating to a person and concerning his or her "
            "ability to meet payment commitments in the future constitutes 'automated individual decision-making' "
            "within the meaning of that provision, where a third party, to which that probability value is "
            "transmitted, draws strongly on that probability value to establish, implement or terminate a "
            "contractual relationship with that person."
        ),
    },
    {
        "document_id": "DOC-EU-EDPB-REC-01-2020",
        "source_id": "SRC-EU-EDPB-ART70-GUIDELINES",
        "document_type": DocumentClassType.OFFICIAL_GUIDANCE.value,
        "canonical_title": (
            "Recommendations 01/2020 on measures that supplement transfer tools to ensure compliance "
            "with the EU level of protection of personal data (Version 2.0)"
        ),
        "case_number": "Recommendations 01/2020",
        "docket_or_case_number": "EDPB Recommendations 01/2020 v2.0",
        "ecli": None,
        "celex_id": None,
        "eli_or_celex_identifier": None,
        "neutral_citation": "EDPB Recommendations 01/2020 (Version 2.0, adopted 18 June 2021)",
        "jurisdiction_id": "EU",
        "issuing_authority": "European Data Protection Board (EDPB)",
        "issuing_authority_type": "data_protection_authority",
        "official_source_url": (
            "https://www.edpb.europa.eu/our-work-tools/our-documents/recommendations/"
            "recommendations-012020-measures-supplement-transfer_en"
        ),
        "decision_date": "2021-06-18",
        "publication_date": "2021-06-18",
        "binding_status": "persuasive_guidance",
        "is_legislation": False,
        "is_binding_judicial_judgment": False,
        "is_edpb_guidance": True,
        "instrument_authority_distinction": (
            "Issued under Article 70(1)(e) GDPR as official supervisory board guidance (`official_guidance`); "
            "explicitly distinct from EU primary/secondary legislation (`statute` / `regulation`), "
            "CJEU judgments (`court_judgment`), and EDPB Article 65 binding dispute-resolution decisions "
            "(`regulatory_enforcement_decision`)."
        ),
        "interpreted_provisions": [
            "GDPR Article 44",
            "GDPR Article 46",
            "GDPR Article 70(1)(e)",
            "CJEU Case C-311/18 (Schrems II)",
        ],
        "parties": [],
        "legal_holdings": [
            (
                "Sets out a six-step transfer impact assessment (TIA) roadmap for data exporters: "
                "(1) know your transfers, (2) verify the transfer tool under Chapter V GDPR, "
                "(3) assess the law or practice of the third country affecting effectiveness of the transfer tool, "
                "(4) identify and adopt technical, contractual, and organizational supplementary measures, "
                "(5) take formal procedural steps, and (6) re-evaluate at appropriate intervals."
            ),
            (
                "Specifies technical supplementary measures (such as strong encryption with keys retained "
                "solely under the exporter's control in the EEA or adequate jurisdiction, or pseudonymisation "
                "with additional data held exclusively in the EEA) where third-country public authority "
                "access laws impinge on Article 46 transfer tools."
            ),
        ],
        "exact_source_excerpt": (
            "Consequently, the EDPB has decided to issue these recommendations to provide exporters with a "
            "series of steps to follow, potential sources of information, and some examples of supplementary "
            "measures that could be put in place."
        ),
    },
    {
        "document_id": "DOC-EU-EDPB-BINDING-01-2021",
        "source_id": "SRC-EU-EDPB-ART65-DECISIONS",
        "document_type": DocumentClassType.REGULATORY_ENFORCEMENT_DECISION.value,
        "canonical_title": (
            "Binding Decision 1/2021 on the dispute arisen on the draft decision of the Irish Supervisory "
            "Authority regarding WhatsApp Ireland under Article 65(1)(a) GDPR"
        ),
        "case_number": "Binding Decision 1/2021",
        "docket_or_case_number": "EDPB Binding Decision 1/2021 (Art. 65(1)(a) GDPR)",
        "ecli": None,
        "celex_id": None,
        "eli_or_celex_identifier": None,
        "neutral_citation": "EDPB Binding Decision 1/2021 (28 July 2021)",
        "jurisdiction_id": "EU",
        "issuing_authority": "European Data Protection Board (EDPB)",
        "issuing_authority_type": "data_protection_authority",
        "official_source_url": (
            "https://www.edpb.europa.eu/our-work-tools/our-documents/binding-decision-board-art-65/"
            "binding-decision-12021-dispute-arisen_en"
        ),
        "decision_date": "2021-07-28",
        "publication_date": "2021-07-28",
        "binding_status": "administrative_order",
        "is_legislation": False,
        "is_binding_judicial_judgment": False,
        "is_edpb_guidance": False,
        "instrument_authority_distinction": (
            "Issued under Article 65(1)(a) GDPR as a binding dispute-resolution decision addressed to "
            "supervisory authorities (`regulatory_enforcement_decision`), distinct from Article 70 non-binding "
            "`official_guidance` and distinct from CJEU `court_judgment`."
        ),
        "interpreted_provisions": [
            "GDPR Article 5(1)(a)",
            "GDPR Article 12",
            "GDPR Article 13",
            "GDPR Article 14",
            "GDPR Article 65(1)(a)",
            "GDPR Article 83",
        ],
        "parties": [
            "Irish Data Protection Commission (IE SA)",
            "WhatsApp Ireland Ltd.",
        ],
        "legal_holdings": [
            (
                "Instructs the Lead Supervisory Authority (Irish DPC) to amend its draft decision regarding "
                "transparency breaches under Articles 12, 13, and 14 GDPR and recalculate the administrative "
                "fine in accordance with Article 83 GDPR."
            ),
        ],
        "exact_source_excerpt": (
            "This binding decision is addressed to the IE SA, as the LSA, and to all the CSAs, and is "
            "binding on them pursuant to Article 65(2) GDPR."
        ),
    },
    {
        "document_id": "DOC-EU-EDPS-DECISION-2024-EC-M365",
        "source_id": "SRC-EU-EDPS-OPINIONS-DECISIONS",
        "document_type": DocumentClassType.REGULATORY_ENFORCEMENT_DECISION.value,
        "canonical_title": (
            "EDPS Decision of 8 March 2024 following its investigation into the European Commission's "
            "use of Microsoft 365 under Regulation (EU) 2018/1725 (Case 2021-0518)"
        ),
        "case_number": "Case 2021-0518",
        "docket_or_case_number": "EDPS Case 2021-0518",
        "ecli": None,
        "celex_id": None,
        "eli_or_celex_identifier": None,
        "neutral_citation": "EDPS Decision Case 2021-0518 (8 March 2024)",
        "jurisdiction_id": "EU",
        "issuing_authority": "European Data Protection Supervisor (EDPS)",
        "issuing_authority_type": "data_protection_authority",
        "official_source_url": (
            "https://www.edps.europa.eu/data-protection/our-work/publications/investigations/"
            "2024-03-08-edps-investigation-european-commissions-use-microsoft-365_en"
        ),
        "decision_date": "2024-03-08",
        "publication_date": "2024-03-11",
        "binding_status": "administrative_order",
        "is_legislation": False,
        "is_binding_judicial_judgment": False,
        "is_edpb_guidance": False,
        "interpreted_provisions": [
            "Regulation (EU) 2018/1725 Article 4(1)(b)",
            "Regulation (EU) 2018/1725 Article 29",
            "Regulation (EU) 2018/1725 Article 46",
            "Regulation (EU) 2018/1725 Article 48(1) and 48(2)(b)",
        ],
        "parties": [
            "European Data Protection Supervisor (EDPS)",
            "European Commission",
        ],
        "legal_holdings": [
            (
                "Finds that the European Commission infringed several provisions of Regulation (EU) 2018/1725, "
                "including those on purpose limitation, controller-processor agreements, and transfers of "
                "personal data outside the EU/EEA, in its use of Microsoft 365."
            ),
        ],
        "exact_source_excerpt": (
            "The EDPS has found that the European Commission (Commission) has infringed several key data "
            "protection rules when using Microsoft 365."
        ),
    },
]


def get_eu_edpb_edps_cjeu_sources() -> List[RegulatorySourceEntry]:
    """Return the curated registry of CJEU, EDPB, and EDPS official sources."""
    return list(EU_EDPB_EDPS_CJEU_SOURCES)
