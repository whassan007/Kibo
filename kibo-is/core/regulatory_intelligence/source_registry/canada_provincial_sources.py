"""
KIBO Privacy OS — Canadian Provincial & Territorial Regulatory Source Registry (G07)
Covers all 10 Canadian provinces (CA-AB, CA-BC, CA-MB, CA-NB, CA-NL, CA-NS, CA-ON, CA-PE, CA-QC, CA-SK)
and all 3 Canadian territories (CA-NT, CA-NU, CA-YT), including bilingual French/English support for
Quebec Law 25 (CQLR c. P-39.1) and authentic statutory fixtures for RD-08 verification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    RegulatorySourceEntry,
    SourceHealthStatus,
    compute_sha256_hex,
)

LAST_RETRIEVAL_TS = datetime(2026, 10, 25, 19, 30, 0, tzinfo=timezone.utc)

CANADA_PROVINCIAL_SOURCES: List[RegulatorySourceEntry] = [
    # =========================================================================
    # QUEBEC (CA-QC) — LégisQuébec & Commission d'accès à l'information (CAI)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-QC-LEGISQUEBEC-LAW25-FR",
        jurisdiction_id="CA-QC",
        parent_jurisdiction="CA-FED",
        authority_name="Éditeur officiel du Québec — LégisQuébec (RLRQ c. P-39.1 / Loi 25)",
        authority_type="legislature",
        official_domain="legisquebec.gouv.qc.ca",
        discovery_endpoint="https://www.legisquebec.gouv.qc.ca/fr/document/lc/P-39.1",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Droits d'auteur du Québec — Reproduction autorisée avec mention de la source",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "biometrics",
            "automated_decision_making",
            "confidentiality_incidents",
            "privacy_impact_assessment",
            "data_portability",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["fr", "en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="RLRQ-c-P-39.1-Loi25-2024-09-22-FR",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-QC-LEGISQUEBEC-LAW25-EN",
        jurisdiction_id="CA-QC",
        parent_jurisdiction="CA-FED",
        authority_name="Official Publisher of Québec — LégisQuébec (CQLR c. P-39.1 / Law 25 & Public Sector Act c. A-2.1)",
        authority_type="legislature",
        official_domain="legisquebec.gouv.qc.ca",
        discovery_endpoint="https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Gouvernement du Québec Copyright — Official Bilingual Co-Authoritative Consolidation",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "public_sector_access",
            "confidentiality_incidents",
            "cross_border_transfers",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CQLR-c-P-39.1-Law25-2024-09-22-EN",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-QC-CAI-DECISIONS",
        jurisdiction_id="CA-QC",
        parent_jurisdiction="CA-FED",
        authority_name="Commission d'accès à l'information du Québec (CAI)",
        authority_type="data_protection_authority",
        official_domain="cai.gouv.qc.ca",
        discovery_endpoint="https://www.cai.gouv.qc.ca/decisions-de-la-commission/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Gouvernement du Québec — Public Regulatory Guidance and Decisions",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "enforcement", "biometrics_registry"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "administrative_tribunal_ruling"],
        source_priority=1,
        languages=["fr", "en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CAI-QC-2026-10",
    ),

    # =========================================================================
    # ONTARIO (CA-ON) — Ontario e-Laws & IPC Ontario
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-ON-ELAWS-PHIPA-FIPPA",
        jurisdiction_id="CA-ON",
        parent_jurisdiction="CA-FED",
        authority_name="King's Printer for Ontario — e-Laws (PHIPA S.O. 2004, c. 3, Sched. A; FIPPA R.S.O. 1990, c. F.31; MFIPPA R.S.O. 1990, c. M.56; Bill 194)",
        authority_type="legislature",
        official_domain="ontario.ca",
        discovery_endpoint="https://www.ontario.ca/laws/statute/04p03",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Ontario Open Government Licence — attribution required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "health_information",
            "public_sector_privacy",
            "municipal_privacy",
            "cybersecurity",
            "ai_governance_public_sector",
        ],
        legal_instrument_types=["statute", "regulation", "legislative_bill"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ON-ELAWS-SO-2004-c3-SchedA-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-ON-IPC-DECISIONS",
        jurisdiction_id="CA-ON",
        parent_jurisdiction="CA-FED",
        authority_name="Information and Privacy Commissioner of Ontario (IPC)",
        authority_type="data_protection_authority",
        official_domain="ipc.on.ca",
        discovery_endpoint="https://decisions.ipc.on.ca/ipc-cipvp/en/nav.do",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Information and Privacy Commissioner of Ontario — Open Access Orders & Guidance",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "administrative_penalties", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "administrative_tribunal_ruling"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="IPC-ON-PHIPA-DECISIONS-2026-10",
    ),

    # =========================================================================
    # BRITISH COLUMBIA (CA-BC) — BCLaws & OIPC BC
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-BC-BCLAWS-PIPA-FOIPPA",
        jurisdiction_id="CA-BC",
        parent_jurisdiction="CA-FED",
        authority_name="King's Printer for British Columbia — BCLaws (PIPA SBC 2003, c. 63 & FOIPPA RSBC 1996, c. 165)",
        authority_type="legislature",
        official_domain="bclaws.gov.bc.ca",
        discovery_endpoint="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/03063_01",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer Quickscribe / B.C. Crown Copyright Open Licence",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "employee_privacy", "public_sector_privacy", "data_residency"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="BC-PIPA-SBC-2003-c63-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-BC-OIPC-ORDERS",
        jurisdiction_id="CA-BC",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
        authority_type="data_protection_authority",
        official_domain="oipc.bc.ca",
        discovery_endpoint="https://www.oipc.bc.ca/decisions/orders/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC BC Public Access Terms",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "enforcement", "employee_surveillance"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="OIPC-BC-ORDERS-2026-10",
    ),

    # =========================================================================
    # ALBERTA (CA-AB) — Alberta King's Printer & OIPC Alberta
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-AB-KINGS-PRINTER-PIPA-HIA",
        jurisdiction_id="CA-AB",
        parent_jurisdiction="CA-FED",
        authority_name="Alberta King's Printer (Alberta PIPA SA 2003, c. P-6.5; HIA RSA 2000, c. H-5; FOIP RSA 2000, c. F-25)",
        authority_type="legislature",
        official_domain="kings-printer.alberta.ca",
        discovery_endpoint="https://kings-printer.alberta.ca/570.cfm?frm_isbn=9780779842209&search_by=link",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Alberta Open Government Licence — King's Printer for Alberta",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "health_information",
            "breach_notification",
            "service_provider_notice",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="AB-PIPA-SA-2003-cP6.5-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-AB-OIPC-DECISIONS",
        jurisdiction_id="CA-AB",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of Alberta (OIPC AB)",
        authority_type="data_protection_authority",
        official_domain="oipc.ab.ca",
        discovery_endpoint="https://oipc.ab.ca/decisions/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC Alberta Open Publication Policy",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "breach_decisions", "health_information"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="OIPC-AB-2026-10",
    ),

    # =========================================================================
    # MANITOBA (CA-MB) — Manitoba Laws (FIPPA & PHIA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-MB-LAWS-FIPPA-PHIA",
        jurisdiction_id="CA-MB",
        parent_jurisdiction="CA-FED",
        authority_name="Legislative Counsel / Statutory Publications Manitoba (FIPPA C.C.S.M. c. F175 & PHIA C.C.S.M. c. P33.5)",
        authority_type="legislature",
        official_domain="web2.gov.mb.ca",
        discovery_endpoint="https://web2.gov.mb.ca/laws/statutes/ccsm/p033-5.php",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Manitoba — Open Legislative Access",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="MB-CCSM-P33.5-F175-2026-10",
    ),

    # =========================================================================
    # NEW BRUNSWICK (CA-NB) — New Brunswick Acts and Regulations (RTIPPA & PHIPAA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-NB-LAWS-RTIPPA-PHIPAA",
        jurisdiction_id="CA-NB",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Attorney General of New Brunswick (RTIPPA S.N.B. 2009, c. R-10.6 & PHIPAA S.N.B. 2009, c. P-7.05)",
        authority_type="legislature",
        official_domain="laws.gnb.ca",
        discovery_endpoint="https://laws.gnb.ca/en/showdoc/cs/P-7.05",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for New Brunswick — Official Bilingual Consolidation",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NB-PHIPAA-RTIPPA-2026-10",
    ),

    # =========================================================================
    # NEWFOUNDLAND AND LABRADOR (CA-NL) — House of Assembly (ATIPPA 2015 & PHIA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-NL-ASSEMBLY-ATIPPA-PHIA",
        jurisdiction_id="CA-NL",
        parent_jurisdiction="CA-FED",
        authority_name="Newfoundland and Labrador House of Assembly (ATIPPA, 2015 SNL 2015, c. A-1.2 & PHIA SNL 2008, c. P-7.01)",
        authority_type="legislature",
        official_domain="assembly.nl.ca",
        discovery_endpoint="https://www.assembly.nl.ca/Legislation/sr/statutes/a01-2.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Newfoundland and Labrador Crown Copyright",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NL-ATIPPA2015-PHIA-2026-10",
    ),

    # =========================================================================
    # NOVA SCOTIA (CA-NS) — Nova Scotia Legislature (FOIPOP, PIIDPA, PHIA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-NS-LEGISLATURE-PIIDPA-PHIA",
        jurisdiction_id="CA-NS",
        parent_jurisdiction="CA-FED",
        authority_name="Nova Scotia House of Assembly — Office of the Legislative Counsel (PIIDPA S.N.S. 2006, c. 3; PHIA S.N.S. 2010, c. 41; FOIPOP S.N.S. 1993, c. 5)",
        authority_type="legislature",
        official_domain="nslegislature.ca",
        discovery_endpoint="https://nslegislature.ca/sites/default/files/legc/statutes/personal%20health%20information.pdf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Crown Copyright Province of Nova Scotia",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "international_disclosure_restrictions", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NS-PIIDPA-PHIA-FOIPOP-2026-10",
    ),

    # =========================================================================
    # PRINCE EDWARD ISLAND (CA-PE) — PEI Legislation (FOIPP & HIA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-PE-LEGISLATION-FOIPP-HIA",
        jurisdiction_id="CA-PE",
        parent_jurisdiction="CA-FED",
        authority_name="King's Printer for Prince Edward Island (FOIPP Act R.S.P.E.I. 1988, c. F-15.01 & Health Information Act R.S.P.E.I. 1988, c. H-1.41)",
        authority_type="legislature",
        official_domain="princeedwardisland.ca",
        discovery_endpoint="https://www.princeedwardisland.ca/en/legislation/all/all/a",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Government of Prince Edward Island Open Legislation Terms",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="PE-FOIPP-HIA-2026-10",
    ),

    # =========================================================================
    # SASKATCHEWAN (CA-SK) — Publications Saskatchewan (FOIP, LAFOIP, HIPA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-SK-PUBLICATIONS-FOIP-HIPA",
        jurisdiction_id="CA-SK",
        parent_jurisdiction="CA-FED",
        authority_name="King's Printer for Saskatchewan — Publications Saskatchewan (FOIP S.S. 1990-91, c. F-22.01; LAFOIP S.S. 1990-91, c. L-27.1; HIPA S.S. 1999, c. H-0.021)",
        authority_type="legislature",
        official_domain="publications.saskatchewan.ca",
        discovery_endpoint="https://publications.saskatchewan.ca/api/v1/products/485",
        feed_format="api_json",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Saskatchewan Crown Copyright",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="SK-FOIP-LAFOIP-HIPA-2026-10",
    ),

    # =========================================================================
    # NORTHWEST TERRITORIES (CA-NT) — NWT Department of Justice (ATIPP & HIA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-NT-JUSTICE-ATIPP-HIA",
        jurisdiction_id="CA-NT",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice — Government of the Northwest Territories (ATIPP Act S.N.W.T. 1994, c. 20 & Health Information Act S.N.W.T. 2014, c. 2)",
        authority_type="legislature",
        official_domain="justice.gov.nt.ca",
        discovery_endpoint="https://www.justice.gov.nt.ca/en/legislation/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Government of the Northwest Territories Territorial Legislation License",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "health_information", "public_sector_privacy"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NT-ATIPP-HIA-2026-10",
    ),

    # =========================================================================
    # NUNAVUT (CA-NU) — Nunavut Legislation Division (ATIPP Act)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-NU-LEGISLATION-ATIPP",
        jurisdiction_id="CA-NU",
        parent_jurisdiction="CA-FED",
        authority_name="Department of Justice of Nunavut — Legislation Division (Access to Information and Protection of Privacy Act, S.Nu. 1994, c. 20)",
        authority_type="legislature",
        official_domain="nunavutlegislation.ca",
        discovery_endpoint="https://www.nunavutlegislation.ca/en/consolidated-law/access-information-and-protection-privacy-act-consolidated",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Territorial Printer for Nunavut — Official Consolidation",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "public_sector_privacy", "data_protection"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NU-ATIPP-2026-10",
    ),

    # =========================================================================
    # YUKON (CA-YT) — Yukon Legislation (ATIPP Act & HIPMA)
    # =========================================================================
    RegulatorySourceEntry(
        source_id="SRC-CA-YT-LAWS-ATIPP-HIPMA",
        jurisdiction_id="CA-YT",
        parent_jurisdiction="CA-FED",
        authority_name="Government of Yukon — Legislative Counsel Office (ATIPP Act S.Y. 2018, c. 9 & Health Information Privacy and Management Act S.Y. 2013, c. 16)",
        authority_type="legislature",
        official_domain="laws.yukon.ca",
        discovery_endpoint="https://laws.yukon.ca/cms/images/LEGISLATION/PRINCIPAL/2018/2018-0009/2018-0009_1.pdf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Yukon — Open Government Licence",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "health_information", "public_sector_privacy", "breach_notification"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=LAST_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="YT-ATIPP2018-HIPMA2013-2026-10",
    ),
]


# =============================================================================
# AUTHENTIC CANADIAN PROVINCIAL FIXTURES (RD-08)
# =============================================================================
# Real statutory text from:
# 1. Quebec Law 25 / Act respecting the protection of personal information in the
#    private sector (RLRQ c. P-39.1 / CQLR c. P-39.1) — arts. 3.1, 3.3, 3.5, 12.1, 17, 18.3
#    in both authentic French (original authoritative) and official English co-authoritative text.
# 2. Ontario Personal Health Information Protection Act, 2004 (S.O. 2004, c. 3, Sched. A)
#    — ss. 12(1), 12(2), 17.1.
# =============================================================================

_QC_LAW25_FR_TEXT = (
    "RLRQ c. P-39.1 — Loi sur la protection des renseignements personnels dans le secteur privé (modifiée par la Loi 25, L.Q. 2021, c. 25)\n"
    "Article 3.1 : Toute personne qui exploite une entreprise est responsable de la protection des renseignements personnels qu'elle détient. "
    "Au sein de l'entreprise, la personne ayant la plus haute autorité veille à assurer le respect et la mise en oeuvre de la présente loi. "
    "Elle exerce la fonction de responsable de la protection des renseignements personnels; elle peut déléguer cette fonction, en tout ou en partie, par écrit, à toute personne. "
    "Le titre et les coordonnées du responsable de la protection des renseignements personnels sont publiés sur le site Internet de l'entreprise ou, si elle n'a pas de site, rendus accessibles par tout autre moyen approprié.\n"
    "Article 3.3 : La personne qui exploite une entreprise doit procéder à une évaluation des facteurs relatifs à la vie privée de tout projet d'acquisition, de développement et de refonte de système d'information ou de prestation électronique de services impliquant la collecte, l'utilisation, la communication, la conservation ou la destruction de renseignements personnels.\n"
    "Article 3.5 : Toute personne qui exploite une entreprise et qui a des motifs de croire que s'est produit un incident de confidentialité impliquant un renseignement personnel qu'elle détient doit prendre les mesures raisonnables pour diminuer les risques qu'un préjudice soit causé et éviter que de nouveaux incidents de même nature ne se produisent. "
    "Si l'incident présente un risque qu'un préjudice sérieux soit causé, elle doit, avec diligence, en aviser la Commission d'accès à l'information. Elle doit également en aviser toute personne dont un renseignement personnel est concerné par l'incident, à défaut de quoi la Commission peut lui ordonner de le faire.\n"
    "Article 12.1 : Toute personne qui exploite une entreprise qui utilise des renseignements personnels afin que soit rendue une décision fondée exclusivement sur un traitement automatisé de tels renseignements doit, au plus tard au moment où elle informe la personne concernée de cette décision, l'informer aussi de l'utilisation de tels renseignements, des raisons ainsi que des principaux facteurs et paramètres ayant mené à la décision, et de son droit de faire présenter ses observations à un membre du personnel de l'entreprise en mesure de réviser la décision.\n"
    "Article 17 : Avant de communiquer à l'extérieur du Québec un renseignement personnel, la personne qui exploite une entreprise doit procéder à une évaluation des facteurs relatifs à la vie privée. Elle doit notamment tenir compte de la sensibilité du renseignement, de la finalité de son utilisation, des mesures de protection, incluant celles qui sont contractuelles, dont le renseignement bénéficierait, et du régime juridique applicable dans l'État où ce renseignement serait communiqué.\n"
    "Article 18.3 : Toute personne qui exploite une entreprise doit, à la demande de la personne concernée, lui communiquer dans un format technologique structuré et couramment utilisé un renseignement personnel informatisé recueilli auprès d'elle, ou le communiquer à toute personne ou à tout organisme autorisé par la loi à recueillir un tel renseignement."
)

_QC_LAW25_EN_TEXT = (
    "CQLR c. P-39.1 — Act respecting the protection of personal information in the private sector (as amended by Law 25, S.Q. 2021, c. 25)\n"
    "Section 3.1: Any person carrying on an enterprise is responsible for the protection of the personal information held by the person. "
    "Within the enterprise, the person exercising the highest authority shall see to ensuring that this Act is respected and implemented. "
    "That person exercises the function of person in charge of the protection of personal information; the person may delegate that function in writing, in whole or in part, to any person. "
    "The title and contact information of the person in charge of the protection of personal information must be published on the enterprise's website or, if the enterprise does not have a website, be made accessible by any other appropriate means.\n"
    "Section 3.3: A person carrying on an enterprise must conduct an assessment of the privacy-related factors of any project to acquire, develop or overhaul an information system or electronic service delivery system involving the collection, use, communication, keeping or destruction of personal information.\n"
    "Section 3.5: Any person carrying on an enterprise who has cause to believe that a confidentiality incident involving personal information the person holds has occurred must take reasonable measures to reduce the risk of injury and to prevent new incidents of the same nature. "
    "If the incident presents a risk of serious injury, the person must promptly notify the Commission d'accès à l'information. The person must also notify any person whose personal information is concerned by the incident, failing which the Commission may order the person to do so.\n"
    "Section 12.1: Any person carrying on an enterprise who uses personal information to render a decision based exclusively on an automated processing of such information must, at the time of or before informing the person concerned of the decision, also inform the person concerned of the use of such information, of the reasons and the principal factors and parameters that led to the decision, and of the right of the person concerned to submit observations to a member of the enterprise's personnel who is in a position to review the decision.\n"
    "Section 17: Before communicating personal information outside Québec, a person carrying on an enterprise must conduct a privacy impact assessment. The person must, in particular, take into account the sensitivity of the information, the purposes for which it is to be used, the protection measures, including those that are contractual, that would apply to it, and the legal framework applicable in the State in which the information would be communicated.\n"
    "Section 18.3: Unless doing so raises serious practical difficulties, computerized personal information collected from the applicant must, at the applicant's request, be communicated to the applicant in a structured, commonly used technological format, or be communicated to any person or body authorized by law to collect such information."
)

_ON_PHIPA_TEXT = (
    "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A\n"
    "Section 12(1) Security: A health information custodian shall take steps that are reasonable in the circumstances to ensure that personal health information in the custodian's custody or control is protected against theft, loss and unauthorized use or disclosure and to ensure that the records containing the information are protected against unauthorized copying, modification or disposal.\n"
    "Section 12(2) Notice of theft, loss, etc.: Subject to the exceptions and additional requirements, if any, that are prescribed, if personal health information about an individual that is in the custody or control of a health information custodian is stolen or lost or if it is used or disclosed without authority, the health information custodian shall, "
    "(a) notify the individual at the first reasonable opportunity of the theft or loss or of the unauthorized use or disclosure; and "
    "(b) include in the notice a statement that the individual is entitled to make a complaint to the Commissioner under Part VI.\n"
    "Section 17.1 Notice to Commissioner: In the prescribed circumstances, a health information custodian shall notify the Commissioner with respect to personal health information that is stolen or lost or that is used or disclosed without authority, and shall provide an annual report to the Commissioner setting out the number of times in the previous calendar year that personal health information was stolen, lost, used without authority or disclosed without authority."
)

AUTHENTIC_CANADA_PROVINCIAL_FIXTURES: Dict[str, Dict[str, Any]] = {
    "CA-QC-LAW25-RLRQ-P-39.1-FR": {
        "document_id": "DOC-CA-QC-RLRQ-P-39.1-FR",
        "source_id": "SRC-CA-QC-LEGISQUEBEC-LAW25-FR",
        "jurisdiction_id": "CA-QC",
        "parent_jurisdiction": "CA-FED",
        "official_citation": "RLRQ c. P-39.1 (mod. L.Q. 2021, c. 25 / Loi 25)",
        "canonical_title": "Loi sur la protection des renseignements personnels dans le secteur privé",
        "issuing_authority": "Assemblée nationale du Québec / Éditeur officiel du Québec",
        "official_source_url": "https://www.legisquebec.gouv.qc.ca/fr/document/lc/P-39.1",
        "language": "fr",
        "translation_status": "original_authoritative",
        "effective_date": "2024-09-22",
        "raw_document_sha256": compute_sha256_hex(_QC_LAW25_FR_TEXT),
        "normalized_text_sha256": compute_sha256_hex(_QC_LAW25_FR_TEXT.strip()),
        "normalized_text": _QC_LAW25_FR_TEXT,
        "provisions": {
            "art. 3.1": (
                "Toute personne qui exploite une entreprise est responsable de la protection des renseignements personnels qu'elle détient. "
                "Au sein de l'entreprise, la personne ayant la plus haute autorité veille à assurer le respect et la mise en oeuvre de la présente loi. "
                "Elle exerce la fonction de responsable de la protection des renseignements personnels; elle peut déléguer cette fonction, en tout ou en partie, par écrit, à toute personne. "
                "Le titre et les coordonnées du responsable de la protection des renseignements personnels sont publiés sur le site Internet de l'entreprise ou, si elle n'a pas de site, rendus accessibles par tout autre moyen approprié."
            ),
            "art. 3.3": (
                "La personne qui exploite une entreprise doit procéder à une évaluation des facteurs relatifs à la vie privée de tout projet d'acquisition, "
                "de développement et de refonte de système d'information ou de prestation électronique de services impliquant la collecte, l'utilisation, la communication, la conservation ou la destruction de renseignements personnels."
            ),
            "art. 3.5": (
                "Toute personne qui exploite une entreprise et qui a des motifs de croire que s'est produit un incident de confidentialité impliquant un renseignement personnel qu'elle détient "
                "doit prendre les mesures raisonnables pour diminuer les risques qu'un préjudice soit causé et éviter que de nouveaux incidents de même nature ne se produisent. "
                "Si l'incident présente un risque qu'un préjudice sérieux soit causé, elle doit, avec diligence, en aviser la Commission d'accès à l'information. "
                "Elle doit également en aviser toute personne dont un renseignement personnel est concerné par l'incident, à défaut de quoi la Commission peut lui ordonner de le faire."
            ),
            "art. 12.1": (
                "Toute personne qui exploite une entreprise qui utilise des renseignements personnels afin que soit rendue une décision fondée exclusivement sur un traitement automatisé "
                "de tels renseignements doit, au plus tard au moment où elle informe la personne concernée de cette décision, l'informer aussi de l'utilisation de tels renseignements, "
                "des raisons ainsi que des principaux facteurs et paramètres ayant mené à la décision, et de son droit de faire présenter ses observations à un membre du personnel de l'entreprise en mesure de réviser la décision."
            ),
            "art. 17": (
                "Avant de communiquer à l'extérieur du Québec un renseignement personnel, la personne qui exploite une entreprise doit procéder à une évaluation des facteurs relatifs à la vie privée. "
                "Elle doit notamment tenir compte de la sensibilité du renseignement, de la finalité de son utilisation, des mesures de protection, incluant celles qui sont contractuelles, dont le renseignement bénéficierait, "
                "et du régime juridique applicable dans l'État où ce renseignement serait communiqué."
            ),
            "art. 18.3": (
                "Toute personne qui exploite une entreprise doit, à la demande de la personne concernée, lui communiquer dans un format technologique structuré et couramment utilisé un renseignement personnel informatisé recueilli auprès d'elle, "
                "ou le communiquer à toute personne ou à tout organisme autorisé par la loi à recueillir un tel renseignement."
            ),
        },
    },
    "CA-QC-LAW25-CQLR-P-39.1-EN": {
        "document_id": "DOC-CA-QC-CQLR-P-39.1-EN",
        "source_id": "SRC-CA-QC-LEGISQUEBEC-LAW25-EN",
        "jurisdiction_id": "CA-QC",
        "parent_jurisdiction": "CA-FED",
        "official_citation": "CQLR c. P-39.1 (as am. by S.Q. 2021, c. 25 / Law 25)",
        "canonical_title": "Act respecting the protection of personal information in the private sector",
        "issuing_authority": "National Assembly of Québec / Official Publisher of Québec",
        "official_source_url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1",
        "language": "en",
        "translation_status": "official_bilingual_coauthoritative",
        "effective_date": "2024-09-22",
        "raw_document_sha256": compute_sha256_hex(_QC_LAW25_EN_TEXT),
        "normalized_text_sha256": compute_sha256_hex(_QC_LAW25_EN_TEXT.strip()),
        "normalized_text": _QC_LAW25_EN_TEXT,
        "provisions": {
            "art. 3.1": (
                "Any person carrying on an enterprise is responsible for the protection of the personal information held by the person. "
                "Within the enterprise, the person exercising the highest authority shall see to ensuring that this Act is respected and implemented. "
                "That person exercises the function of person in charge of the protection of personal information; the person may delegate that function in writing, in whole or in part, to any person. "
                "The title and contact information of the person in charge of the protection of personal information must be published on the enterprise's website or, if the enterprise does not have a website, be made accessible by any other appropriate means."
            ),
            "art. 3.3": (
                "A person carrying on an enterprise must conduct an assessment of the privacy-related factors of any project to acquire, develop or overhaul "
                "an information system or electronic service delivery system involving the collection, use, communication, keeping or destruction of personal information."
            ),
            "art. 3.5": (
                "Any person carrying on an enterprise who has cause to believe that a confidentiality incident involving personal information the person holds has occurred "
                "must take reasonable measures to reduce the risk of injury and to prevent new incidents of the same nature. "
                "If the incident presents a risk of serious injury, the person must promptly notify the Commission d'accès à l'information. "
                "The person must also notify any person whose personal information is concerned by the incident, failing which the Commission may order the person to do so."
            ),
            "art. 12.1": (
                "Any person carrying on an enterprise who uses personal information to render a decision based exclusively on an automated processing of such information must, "
                "at the time of or before informing the person concerned of the decision, also inform the person concerned of the use of such information, of the reasons and the principal factors and parameters that led to the decision, "
                "and of the right of the person concerned to submit observations to a member of the enterprise's personnel who is in a position to review the decision."
            ),
            "art. 17": (
                "Before communicating personal information outside Québec, a person carrying on an enterprise must conduct a privacy impact assessment. "
                "The person must, in particular, take into account the sensitivity of the information, the purposes for which it is to be used, the protection measures, including those that are contractual, that would apply to it, "
                "and the legal framework applicable in the State in which the information would be communicated."
            ),
            "art. 18.3": (
                "Unless doing so raises serious practical difficulties, computerized personal information collected from the applicant must, at the applicant's request, "
                "be communicated to the applicant in a structured, commonly used technological format, or be communicated to any person or body authorized by law to collect such information."
            ),
        },
    },
    "CA-ON-PHIPA-SO-2004-c3-SchedA": {
        "document_id": "DOC-CA-ON-PHIPA-2004-c3-SchedA",
        "source_id": "SRC-CA-ON-ELAWS-PHIPA-FIPPA",
        "jurisdiction_id": "CA-ON",
        "parent_jurisdiction": "CA-FED",
        "official_citation": "S.O. 2004, c. 3, Sched. A",
        "canonical_title": "Personal Health Information Protection Act, 2004",
        "issuing_authority": "Legislative Assembly of Ontario / King's Printer for Ontario",
        "official_source_url": "https://www.ontario.ca/laws/statute/04p03",
        "language": "en",
        "translation_status": "original_authoritative",
        "effective_date": "2004-11-01",
        "raw_document_sha256": compute_sha256_hex(_ON_PHIPA_TEXT),
        "normalized_text_sha256": compute_sha256_hex(_ON_PHIPA_TEXT.strip()),
        "normalized_text": _ON_PHIPA_TEXT,
        "provisions": {
            "s. 12(1)": (
                "A health information custodian shall take steps that are reasonable in the circumstances to ensure that personal health information "
                "in the custodian's custody or control is protected against theft, loss and unauthorized use or disclosure and to ensure that the records "
                "containing the information are protected against unauthorized copying, modification or disposal."
            ),
            "s. 12(2)": (
                "Subject to the exceptions and additional requirements, if any, that are prescribed, if personal health information about an individual "
                "that is in the custody or control of a health information custodian is stolen or lost or if it is used or disclosed without authority, "
                "the health information custodian shall, (a) notify the individual at the first reasonable opportunity of the theft or loss or of the unauthorized use or disclosure; "
                "and (b) include in the notice a statement that the individual is entitled to make a complaint to the Commissioner under Part VI."
            ),
            "s. 17.1": (
                "In the prescribed circumstances, a health information custodian shall notify the Commissioner with respect to personal health information "
                "that is stolen or lost or that is used or disclosed without authority, and shall provide an annual report to the Commissioner setting out "
                "the number of times in the previous calendar year that personal health information was stolen, lost, used without authority or disclosed without authority."
            ),
        },
    },
}


def get_canada_provincial_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of all curated Canadian provincial and territorial regulatory sources."""
    return list(CANADA_PROVINCIAL_SOURCES)
