"""
KIBO Privacy OS — EU Member-State Legislative & Supervisory Source Registry (States 10–18)
Covers France (EU-FR), Germany Federal (EU-DE) + 16 German Länder legislative laws & 17 Länder supervisory authorities,
Greece (EU-GR), Hungary (EU-HU), Ireland (EU-IE), Italy (EU-IT), Latvia (EU-LV), Lithuania (EU-LT), and Luxembourg (EU-LU).
Also provides AUTHENTIC_FR_DE_MULTILINGUAL_FIXTURES for RD-08 multilingual passage-level citation verification.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import RegulatorySourceEntry, SourceHealthStatus


_DEFAULT_RETRIEVAL_TS = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)


# =============================================================================
# 1. Primary National Legislative & Supervisory Sources (Member States 10–18)
# =============================================================================

_NATIONAL_SOURCES: List[RegulatorySourceEntry] = [
    # -------------------------------------------------------------------------
    # 10. FRANCE (EU-FR)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-FR-LEGIFRANCE-LIL",
        jurisdiction_id="EU-FR",
        parent_jurisdiction="EU",
        authority_name="Secrétariat général du gouvernement — Légifrance (Parlement français)",
        authority_type="legislature",
        official_domain="legifrance.gouv.fr",
        discovery_endpoint="https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000886460",
        feed_format="api_json",
        auth_requirements="oauth2",
        licensing_and_reuse="Licence Ouverte / Open Licence 2.0 (Etalab) — République Française",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cookies_and_tracers",
            "health_data_processing",
            "algorithmic_transparency",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation", "official_policy_directive"],
        source_priority=1,
        languages=["fr"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LEGITEXT000006068624-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-FR-CNIL",
        jurisdiction_id="EU-FR",
        parent_jurisdiction="EU",
        authority_name="Commission Nationale de l'Informatique et des Libertés (CNIL)",
        authority_type="data_protection_authority",
        official_domain="cnil.fr",
        discovery_endpoint="https://www.cnil.fr/fr/rss.xml",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Licence Ouverte / Open Licence 2.0 (Etalab)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cookies_and_tracers",
            "ai_governance",
            "enforcement_sanctions",
        ],
        legal_instrument_types=[
            "official_guidance",
            "regulatory_enforcement_decision",
            "regulatory_consultation",
        ],
        source_priority=1,
        languages=["fr", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CNIL-SAN-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 11. GERMANY — FEDERAL (EU-DE)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-DE-GII-BDSG",
        jurisdiction_id="EU-DE",
        parent_jurisdiction="EU",
        authority_name="Bundesministerium der Justiz (BMJ) / Bundesamt für Justiz — Gesetze im Internet (BDSG)",
        authority_type="legislature",
        official_domain="gesetze-im-internet.de",
        discovery_endpoint="https://www.gesetze-im-internet.de/bdsg_2018/xml.zip",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="§ 5 UrhG Amtliche Werke — Public Domain (Germany Federal Statutes)",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "employee_data_protection",
            "data_protection_officer_designation",
            "video_surveillance",
            "credit_scoring_profiling",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["de", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="BJNR209710017-BDSG-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-DE-GII-TDDDG",
        jurisdiction_id="EU-DE",
        parent_jurisdiction="EU",
        authority_name="Bundesministerium der Justiz (BMJ) — Gesetze im Internet (TDDDG / Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz)",
        authority_type="legislature",
        official_domain="gesetze-im-internet.de",
        discovery_endpoint="https://www.gesetze-im-internet.de/ttdsg/xml.zip",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="§ 5 UrhG Amtliche Werke — Public Domain (Germany Federal Statutes)",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "telecommunications_secrecy",
            "terminal_equipment_storage_cookies",
            "consent_management_services_pims",
            "digital_services_privacy",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["de", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="BJNR198210021-TDDDG-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-DE-BFDI",
        jurisdiction_id="EU-DE",
        parent_jurisdiction="EU",
        authority_name="Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)",
        authority_type="data_protection_authority",
        official_domain="bfdi.bund.de",
        discovery_endpoint="https://www.bfdi.bund.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed_G1.xml",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="§ 5 UrhG Amtliche Werke / Bundesregierung Open Data",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "telecommunications_privacy",
            "federal_public_bodies",
            "dsk_resolutions",
        ],
        legal_instrument_types=[
            "official_guidance",
            "regulatory_enforcement_decision",
            "official_policy_directive",
        ],
        source_priority=1,
        languages=["de", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="BFDI-DSK-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 12. GREECE (EU-GR)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-GR-ET-LAW4624",
        jurisdiction_id="EU-GR",
        parent_jurisdiction="EU",
        authority_name="Εθνικό Τυπογραφείο (National Printing House of Greece) — Βουλή των Ελλήνων (Law 4624/2019)",
        authority_type="official_gazette",
        official_domain="et.gr",
        discovery_endpoint="https://www.et.gr/api/v1/laws/4624-2019",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Hellenic Republic Official Government Gazette (FEK A' 137/29.08.2019) — Public Reuse with Attribution",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "employee_data_processing",
            "special_category_genetic_biometric_data",
            "law_enforcement_directive_transposition",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["el"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="FEK-A-137-2019-L4624-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-GR-HDPA",
        jurisdiction_id="EU-GR",
        parent_jurisdiction="EU",
        authority_name="Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (Hellenic Data Protection Authority — HDPA)",
        authority_type="data_protection_authority",
        official_domain="dpa.gr",
        discovery_endpoint="https://www.dpa.gr/el/enimerwtiko/apofaseis",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Hellenic Republic Open Government Data — Attribution Required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "regulatory_decisions",
            "electronic_communications_privacy",
        ],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["el", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="HDPA-DEC-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 13. HUNGARY (EU-HU)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-HU-NJT-INFOACT",
        jurisdiction_id="EU-HU",
        parent_jurisdiction="EU",
        authority_name="Nemzeti Jogszabálytár (National Legislation Database — Országgyűlés, InfoAct CXII of 2011)",
        authority_type="legislature",
        official_domain="njt.hu",
        discovery_endpoint="https://njt.hu/jogszabaly/2011-112-00-00",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Hungarian Official Legislation Database (Magyar Közlöny / NJT) — Public Domain Statutory Text",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "informational_self_determination",
            "freedom_of_information",
            "mandatory_data_retention_derogations",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["hu"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NJT-2011-CXII-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-HU-NAIH",
        jurisdiction_id="EU-HU",
        parent_jurisdiction="EU",
        authority_name="Nemzeti Adatvédelmi és Információszabadság Hatóság (NAIH)",
        authority_type="data_protection_authority",
        official_domain="naih.hu",
        discovery_endpoint="https://www.naih.hu/hatarozatok-vegzesek",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="NAIH Official Public Register — Attribution Required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ai_facial_recognition_enforcement",
            "employee_monitoring",
        ],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["hu", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="NAIH-HAT-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 14. IRELAND (EU-IE)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-IE-ISB-DPA2018",
        jurisdiction_id="EU-IE",
        parent_jurisdiction="EU",
        authority_name="Office of the Attorney General — Electronic Irish Statute Book (Oireachtas — Data Protection Act 2018)",
        authority_type="legislature",
        official_domain="irishstatutebook.ie",
        discovery_endpoint="https://www.irishstatutebook.ie/eli/2018/act/7/enacted/en/html",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Government of Ireland PSI Licence / Creative Commons Attribution 4.0 International (CC BY 4.0)",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "dpc_investigative_and_corrective_powers",
            "digital_age_of_consent",
            "special_category_data_regulations",
            "cross_border_one_stop_shop_procedures",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["en", "ga"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ELI-IE-2018-ACT-7-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-IE-DPC",
        jurisdiction_id="EU-IE",
        parent_jurisdiction="EU",
        authority_name="Data Protection Commission (DPC — An Coimisiún um Chosaint Sonraí)",
        authority_type="data_protection_authority",
        official_domain="dataprotection.ie",
        discovery_endpoint="https://www.dataprotection.ie/en/dpc-guidance/law/decisions-made-under-data-protection-act-2018",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Government of Ireland PSI Licence (CC BY 4.0)",
        rate_limit_rpm=45,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "article_60_65_cross_border_decisions",
            "large_platform_enforcement",
            "international_data_transfers",
        ],
        legal_instrument_types=[
            "official_guidance",
            "regulatory_enforcement_decision",
            "regulatory_consultation",
        ],
        source_priority=1,
        languages=["en", "ga"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="IE-DPC-INQ-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 15. ITALY (EU-IT)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-IT-NORMATTIVA-CODICE",
        jurisdiction_id="EU-IT",
        parent_jurisdiction="EU",
        authority_name="Istituto Poligrafico e Zecca dello Stato — Normattiva (Codice in materia di protezione dei dati personali D.Lgs. 196/2003 & D.Lgs. 101/2018)",
        authority_type="legislature",
        official_domain="normattiva.it",
        discovery_endpoint="https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2003-06-30;196!vig=",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Italian Open Data Licence (IODL 2.0) / CC BY 4.0 — Presidenza del Consiglio dei Ministri",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "deontological_rules",
            "health_and_genetic_data_guarantees",
            "employee_remote_monitoring_statuto_lavoratori",
            "electronic_communications_telemarketing",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["it"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="URN-NIR-DLGS-2003-196-DLGS-2018-101-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-IT-GARANTE",
        jurisdiction_id="EU-IT",
        parent_jurisdiction="EU",
        authority_name="Garante per la protezione dei dati personali (Garante Privacy)",
        authority_type="data_protection_authority",
        official_domain="garanteprivacy.it",
        discovery_endpoint="https://www.garanteprivacy.it/home/provvedimenti-normativa",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="CC BY 4.0 — Garante per la protezione dei dati personali",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "generative_ai_enforcement",
            "telemarketing_registro_opposizioni",
            "workplace_biometrics",
        ],
        legal_instrument_types=[
            "official_guidance",
            "regulatory_enforcement_decision",
            "official_policy_directive",
        ],
        source_priority=1,
        languages=["it", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="GARANTE-PROVV-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 16. LATVIA (EU-LV)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-LV-LIKUMI-FPDAL",
        jurisdiction_id="EU-LV",
        parent_jurisdiction="EU",
        authority_name="VSIA Latvijas Vēstnesis — Likumi.lv (Saeima — Fizisko personu datu apstrādes likums / FPDAL)",
        authority_type="official_gazette",
        official_domain="likumi.lv",
        discovery_endpoint="https://likumi.lv/ta/id/300099-fizisko-personu-datu-apstrades-likums",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Latvijas Vēstnesis Official Publication — Public Domain Statutory Instrument",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "video_surveillance_notices",
            "national_identification_code_processing",
            "children_information_society_consent",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["lv", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LV-TA-300099-FPDAL-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-LV-DVI",
        jurisdiction_id="EU-LV",
        parent_jurisdiction="EU",
        authority_name="Datu valsts inspekcija (Data State Inspectorate of Latvia — DVI)",
        authority_type="data_protection_authority",
        official_domain="dvi.gov.lv",
        discovery_endpoint="https://www.dvi.gov.lv/lv/jaunumi",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Republic of Latvia Open Data Portal Terms (CC0 / CC BY 4.0)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "dvi_inspections_and_guidance"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["lv", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LV-DVI-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 17. LITHUANIA (EU-LT)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-LT-ETAR-ADKTAI",
        jurisdiction_id="EU-LT",
        parent_jurisdiction="EU",
        authority_name="Teisės aktų registras (TAR) — Lietuvos Respublikos Seimas (Asmens duomenų teisinės apsaugos įstatymas — ADTAĮ Nr. XIII-1426)",
        authority_type="official_gazette",
        official_domain="e-tar.lt",
        discovery_endpoint="https://www.e-tar.lt/portal/lt/legalAct/63401470846911e8ae2bfd1913d66d57/asr",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Republic of Lithuania Register of Legal Acts (TAR) — Official Public Domain Reuse",
        rate_limit_rpm=45,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "national_personal_identification_number_restrictions",
            "employment_candidate_screening_data",
            "creditworthiness_and_debt_databases",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["lt", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LT-TAR-XIII-1426-ADTAI-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-LT-VDAI",
        jurisdiction_id="EU-LT",
        parent_jurisdiction="EU",
        authority_name="Valstybinė duomenų apsaugos inspekcija (State Data Protection Inspectorate — VDAI)",
        authority_type="data_protection_authority",
        official_domain="vdai.lrv.lt",
        discovery_endpoint="https://vdai.lrv.lt/lt/naujienos/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Republic of Lithuania Government Open Data — Attribution Required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "fintech_and_mobility_privacy_enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["lt", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LT-VDAI-2026-10",
    ),
    # -------------------------------------------------------------------------
    # 18. LUXEMBOURG (EU-LU)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-EU-LU-LEGILUX-DPA2018",
        jurisdiction_id="EU-LU",
        parent_jurisdiction="EU",
        authority_name="Service central de législation — Legilux (Loi du 1er août 2018 portant organisation de la CNPD et du régime général sur la protection des données)",
        authority_type="official_gazette",
        official_domain="legilux.public.lu",
        discovery_endpoint="https://legilux.public.lu/eli/etat/leg/loi/2018/08/01/a686/jo",
        feed_format="cellar_rdf",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Grand Duchy of Luxembourg Open Data (CC0 1.0 Universal / ELI Standard)",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "workplace_surveillance_article_l261_1_code_du_travail",
            "cnpd_organisation_and_sanction_powers",
            "scientific_historical_statistical_research_derogations",
            "national_gdpr_derogations",
        ],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["fr", "de"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ELI-LU-LOI-2018-08-01-A686-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-LU-CNPD",
        jurisdiction_id="EU-LU",
        parent_jurisdiction="EU",
        authority_name="Commission Nationale pour la Protection des Données (CNPD — Luxembourg)",
        authority_type="data_protection_authority",
        official_domain="cnpd.public.lu",
        discovery_endpoint="https://cnpd.public.lu/fr/decisions-sanctions.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Grand Duchy of Luxembourg Public Portal — Attribution Required",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cross_border_lead_supervisory_authority_decisions",
            "dpo_compliance_audits",
            "gdpr_car_certification_criteria",
        ],
        legal_instrument_types=[
            "official_guidance",
            "regulatory_enforcement_decision",
            "regulatory_consultation",
        ],
        source_priority=1,
        languages=["fr", "de", "en"],
        last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="LU-CNPD-DELIB-2026-10",
    ),
]


# =============================================================================
# 2. German Subnational Sources: 16 Länder Data Protection Laws & 17 Länder DPAs
#    (Bavaria has two distinct supervisory authorities: BayLDA for non-public
#     entities and BayLfD for public bodies; all 16 Länder have state LDSGs)
# =============================================================================

_GERMAN_LAENDER_SPEC: List[Dict[str, Any]] = [
    {
        "code": "DE-BW",
        "state_name": "Baden-Württemberg",
        "law_abbrev": "LDSG BW",
        "law_title": "Landesdatenschutzgesetz Baden-Württemberg (LDSG BW)",
        "law_domain": "landesrecht-bw.de",
        "law_url": "https://www.landesrecht-bw.de/bsbw/document/jlr-DSGBW2018rahmen",
        "dpa_id": "SRC-DE-BW-LFDI",
        "dpa_name": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg (LfDI BW)",
        "dpa_domain": "baden-wuerttemberg.datenschutz.de",
        "dpa_url": "https://www.baden-wuerttemberg.datenschutz.de/feed/",
        "dpa_format": "rss_atom",
    },
    {
        "code": "DE-BY",
        "state_name": "Bayern (Bavaria)",
        "law_abbrev": "BayDSG",
        "law_title": "Bayerisches Datenschutzgesetz (BayDSG)",
        "law_domain": "gesetze-bayern.de",
        "law_url": "https://www.gesetze-bayern.de/Content/Document/BayDSG",
        "dpa_id": "SRC-DE-BY-BAYLDA",
        "dpa_name": "Bayerisches Landesamt für Datenschutzaufsicht (BayLDA — Private Sector Supervisory Authority)",
        "dpa_domain": "lda.bayern.de",
        "dpa_url": "https://www.lda.bayern.de/de/pressemitteilungen.html",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-BE",
        "state_name": "Berlin",
        "law_abbrev": "BlnDSG",
        "law_title": "Berliner Datenschutzgesetz (BlnDSG)",
        "law_domain": "gesetze.berlin.de",
        "law_url": "https://gesetze.berlin.de/bsbe/document/jlr-DSGBE2018rahmen",
        "dpa_id": "SRC-DE-BE-BLNBDI",
        "dpa_name": "Berliner Beauftragte für Datenschutz und Informationsfreiheit (BlnBDI)",
        "dpa_domain": "datenschutz-berlin.de",
        "dpa_url": "https://www.datenschutz-berlin.de/aktuelles/pressemitteilungen/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-BB",
        "state_name": "Brandenburg",
        "law_abbrev": "BbgDSG",
        "law_title": "Brandenburgisches Datenschutzgesetz (BbgDSG)",
        "law_domain": "bravors.brandenburg.de",
        "law_url": "https://bravors.brandenburg.de/gesetze/bbgdsg",
        "dpa_id": "SRC-DE-BB-LDA",
        "dpa_name": "Die Landesbeauftragte für den Datenschutz und für das Recht auf Akteneinsicht Brandenburg (LDA Brandenburg)",
        "dpa_domain": "lda.brandenburg.de",
        "dpa_url": "https://www.lda.brandenburg.de/lda/de/service/presseinformationen/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-HB",
        "state_name": "Bremen",
        "law_abbrev": "BremDSGVOAG",
        "law_title": "Bremisches Ausführungsgesetz zur EU-Datenschutz-Grundverordnung (BremDSGVOAG)",
        "law_domain": "transparenz.bremen.de",
        "law_url": "https://www.transparenz.bremen.de/metainformationen/bremisches-ausfuehrungsgesetz-zur-eu-datenschutz-grundverordnung-bremdsgvoag-vom-8-mai-2018-116890",
        "dpa_id": "SRC-DE-HB-LFDI",
        "dpa_name": "Die Landesbeauftragte für Datenschutz und Informationsfreiheit der Freien Hansestadt Bremen (LfDI Bremen)",
        "dpa_domain": "datenschutz.bremen.de",
        "dpa_url": "https://www.datenschutz.bremen.de/aktuelles-1467",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-HH",
        "state_name": "Hamburg",
        "law_abbrev": "HmbDSG",
        "law_title": "Hamburgisches Datenschutzgesetz (HmbDSG)",
        "law_domain": "landesrecht-hamburg.de",
        "law_url": "https://www.landesrecht-hamburg.de/bsha/document/jlr-DSGHA2018rahmen",
        "dpa_id": "SRC-DE-HH-HMBBFDI",
        "dpa_name": "Der Hamburgische Beauftragte für Datenschutz und Informationsfreiheit (HmbBfDI)",
        "dpa_domain": "datenschutz-hamburg.de",
        "dpa_url": "https://datenschutz-hamburg.de/pressemitteilungen/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-HE",
        "state_name": "Hessen (Hesse)",
        "law_abbrev": "HDSIG",
        "law_title": "Hessisches Datenschutz- und Informationsfreiheitsgesetz (HDSIG)",
        "law_domain": "rv.hessenrecht.hessen.de",
        "law_url": "https://www.rv.hessenrecht.hessen.de/bshe/document/jlr-DSIGHErahmen",
        "dpa_id": "SRC-DE-HE-HBDI",
        "dpa_name": "Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)",
        "dpa_domain": "datenschutz.hessen.de",
        "dpa_url": "https://datenschutz.hessen.de/presse",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-MV",
        "state_name": "Mecklenburg-Vorpommern",
        "law_abbrev": "DSG M-V",
        "law_title": "Landesdatenschutzgesetz Mecklenburg-Vorpommern (DSG M-V)",
        "law_domain": "landesrecht-mv.de",
        "law_url": "https://www.landesrecht-mv.de/bsmv/document/jlr-DSGMV2018rahmen",
        "dpa_id": "SRC-DE-MV-LFDI",
        "dpa_name": "Der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern (LfDI M-V)",
        "dpa_domain": "datenschutz-mv.de",
        "dpa_url": "https://www.datenschutz-mv.de/presse/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-NI",
        "state_name": "Niedersachsen (Lower Saxony)",
        "law_abbrev": "NDSG",
        "law_title": "Niedersächsisches Datenschutzgesetz (NDSG)",
        "law_domain": "voris.wolterskluwer-online.de",
        "law_url": "https://voris.wolterskluwer-online.de/browse/document/ceed6d75-78e6-3a35-942c-841d58c8256c",
        "dpa_id": "SRC-DE-NI-LFD",
        "dpa_name": "Die Landesbeauftragte für den Datenschutz Niedersachsen (LfD Niedersachsen)",
        "dpa_domain": "lfd.niedersachsen.de",
        "dpa_url": "https://www.lfd.niedersachsen.de/startseite/infothek/presseinformationen/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-NW",
        "state_name": "Nordrhein-Westfalen (North Rhine-Westphalia)",
        "law_abbrev": "DSG NRW",
        "law_title": "Datenschutzgesetz Nordrhein-Westfalen (DSG NRW)",
        "law_domain": "recht.nrw.de",
        "law_url": "https://recht.nrw.de/lmi/owa/br_bes_text?anw_nr=2&gld_nr=2&ugl_nr=2006&bes_id=38524",
        "dpa_id": "SRC-DE-NW-LDI",
        "dpa_name": "Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW)",
        "dpa_domain": "ldi.nrw.de",
        "dpa_url": "https://www.ldi.nrw.de/presse",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-RP",
        "state_name": "Rheinland-Pfalz (Rhineland-Palatinate)",
        "law_abbrev": "LDSG RP",
        "law_title": "Landesdatenschutzgesetz Rheinland-Pfalz (LDSG RP)",
        "law_domain": "landesrecht.rlp.de",
        "law_url": "https://landesrecht.rlp.de/bsrp/document/jlr-DSGRP2018rahmen",
        "dpa_id": "SRC-DE-RP-LFDI",
        "dpa_name": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Rheinland-Pfalz (LfDI RLP)",
        "dpa_domain": "datenschutz.rlp.de",
        "dpa_url": "https://www.datenschutz.rlp.de/de/aktuelles/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-SL",
        "state_name": "Saarland",
        "law_abbrev": "SDSG",
        "law_title": "Saarländisches Datenschutzgesetz (SDSG)",
        "law_domain": "recht.saarland.de",
        "law_url": "https://recht.saarland.de/bssl/document/jlr-DSGSL2018rahmen",
        "dpa_id": "SRC-DE-SL-ULD",
        "dpa_name": "Unabhängiges Datenschutzzentrum Saarland — Die Landesbeauftragte für Datenschutz und Informationsfreiheit",
        "dpa_domain": "datenschutz.saarland.de",
        "dpa_url": "https://www.datenschutz.saarland.de/aktuelles/pressemitteilungen",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-SN",
        "state_name": "Sachsen (Saxony)",
        "law_abbrev": "SächsDSDG",
        "law_title": "Sächsisches Datenschutzdurchführungsgesetz (SächsDSDG)",
        "law_domain": "revosax.sachsen.de",
        "law_url": "https://www.revosax.sachsen.de/vorschrift/17583-Saechsisches-Datenschutzdurchfuehrungsgesetz",
        "dpa_id": "SRC-DE-SN-SAECHSDSB",
        "dpa_name": "Die Sächsische Datenschutz- und Transparenzbeauftragte (SächsDSB)",
        "dpa_domain": "datenschutz.sachsen.de",
        "dpa_url": "https://www.datenschutz.sachsen.de/pressemitteilungen.html",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-ST",
        "state_name": "Sachsen-Anhalt (Saxony-Anhalt)",
        "law_abbrev": "DSG LSA",
        "law_title": "Datenschutz-Grundverordnungs-Ausfüllungsgesetz Sachsen-Anhalt (DSG LSA)",
        "law_domain": "landesrecht.sachsen-anhalt.de",
        "law_url": "https://www.landesrecht.sachsen-anhalt.de/bsst/document/jlr-DSGST2020rahmen",
        "dpa_id": "SRC-DE-ST-LFD",
        "dpa_name": "Landesbeauftragter für den Datenschutz Sachsen-Anhalt (LfD Sachsen-Anhalt)",
        "dpa_domain": "datenschutz.sachsen-anhalt.de",
        "dpa_url": "https://datenschutz.sachsen-anhalt.de/service/pressemitteilungen",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-SH",
        "state_name": "Schleswig-Holstein",
        "law_abbrev": "LDSG SH",
        "law_title": "Schleswig-Holsteinisches Gesetz zum Schutz personenbezogener Daten (Landesdatenschutzgesetz — LDSG SH)",
        "law_domain": "gesetze-rechtsprechung.sh.juris.de",
        "law_url": "https://www.gesetze-rechtsprechung.sh.juris.de/bssh/document/jlr-DSGSH2018rahmen",
        "dpa_id": "SRC-DE-SH-ULD",
        "dpa_name": "Unabhängiges Landeszentrum für Datenschutz Schleswig-Holstein (ULD)",
        "dpa_domain": "datenschutzzentrum.de",
        "dpa_url": "https://www.datenschutzzentrum.de/presse/",
        "dpa_format": "html_structured",
    },
    {
        "code": "DE-TH",
        "state_name": "Thüringen (Thuringia)",
        "law_abbrev": "ThürDSG",
        "law_title": "Thüringer Datenschutzgesetz (ThürDSG)",
        "law_domain": "landesrecht.thueringen.de",
        "law_url": "https://landesrecht.thueringen.de/bsth/document/jlr-DSGTH2018rahmen",
        "dpa_id": "SRC-DE-TH-TLFDI",
        "dpa_name": "Thüringer Landesbeauftragter für den Datenschutz und die Informationsfreiheit (TLfDI)",
        "dpa_domain": "tlfdi.de",
        "dpa_url": "https://www.tlfdi.de/presse/pressemitteilungen/",
        "dpa_format": "html_structured",
    },
]


def _build_german_laender_sources() -> List[RegulatorySourceEntry]:
    entries: List[RegulatorySourceEntry] = []
    for spec in _GERMAN_LAENDER_SPEC:
        code = spec["code"]
        abbrev_slug = spec["law_abbrev"].upper().replace(" ", "-").replace("Ä", "AE").replace("Ü", "UE")
        # 1. State Legislative Statute (LDSG)
        entries.append(
            RegulatorySourceEntry(
                source_id=f"SRC-{code}-LAW-{abbrev_slug}",
                jurisdiction_id=code,
                parent_jurisdiction="EU-DE",
                authority_name=f"Landtag {spec['state_name']} — {spec['law_title']}",
                authority_type="legislature",
                official_domain=spec["law_domain"],
                discovery_endpoint=spec["law_url"],
                feed_format="html_structured",
                auth_requirements="public_unauthenticated",
                licensing_and_reuse="§ 5 UrhG Amtliche Werke — Public Domain (German Land Legislation)",
                rate_limit_rpm=30,
                update_frequency="weekly",
                publication_coverage=[
                    "privacy",
                    "data_protection",
                    "public_sector_data_processing",
                    "state_specific_gdpr_derogations",
                    "employee_and_civil_servant_privacy",
                ],
                legal_instrument_types=["statute", "regulation"],
                source_priority=1,
                languages=["de"],
                last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
                health_status=SourceHealthStatus.HEALTHY,
                checkpoint_cursor=f"{code}-LAW-2026-10",
            )
        )
        # 2. State Supervisory Authority (Landesdatenschutzbehörde)
        entries.append(
            RegulatorySourceEntry(
                source_id=spec["dpa_id"],
                jurisdiction_id=code,
                parent_jurisdiction="EU-DE",
                authority_name=spec["dpa_name"],
                authority_type="data_protection_authority",
                official_domain=spec["dpa_domain"],
                discovery_endpoint=spec["dpa_url"],
                feed_format=spec["dpa_format"],
                auth_requirements="public_unauthenticated",
                licensing_and_reuse="§ 5 UrhG Amtliche Werke / Land Open Data Attribution",
                rate_limit_rpm=30,
                update_frequency="daily",
                publication_coverage=[
                    "privacy",
                    "data_protection",
                    "state_dpa_enforcement",
                    "cross_border_and_local_audits",
                ],
                legal_instrument_types=[
                    "official_guidance",
                    "regulatory_enforcement_decision",
                    "regulatory_consultation",
                ],
                source_priority=1,
                languages=["de"],
                last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
                health_status=SourceHealthStatus.HEALTHY,
                checkpoint_cursor=f"{code}-DPA-2026-10",
            )
        )

    # 17th German Land Supervisory Authority: Der Bayerische Landesbeauftragte für den Datenschutz (BayLfD)
    # (Bavaria splits public-sector supervision [BayLfD] and private-sector supervision [BayLDA])
    entries.append(
        RegulatorySourceEntry(
            source_id="SRC-DE-BY-BAYLFD",
            jurisdiction_id="DE-BY",
            parent_jurisdiction="EU-DE",
            authority_name="Der Bayerische Landesbeauftragte für den Datenschutz (BayLfD — Bavarian Public Sector Supervisory Authority)",
            authority_type="data_protection_authority",
            official_domain="datenschutz-bayern.de",
            discovery_endpoint="https://www.datenschutz-bayern.de/vorab/neu.html",
            feed_format="html_structured",
            auth_requirements="public_unauthenticated",
            licensing_and_reuse="§ 5 UrhG Amtliche Werke — Freistaat Bayern",
            rate_limit_rpm=30,
            update_frequency="weekly",
            publication_coverage=[
                "privacy",
                "data_protection",
                "bavarian_public_bodies_and_municipalities",
                "hospital_and_university_data_protection",
            ],
            legal_instrument_types=[
                "official_guidance",
                "regulatory_enforcement_decision",
            ],
            source_priority=1,
            languages=["de"],
            last_successful_retrieval=_DEFAULT_RETRIEVAL_TS,
            health_status=SourceHealthStatus.HEALTHY,
            checkpoint_cursor="DE-BY-BAYLFD-2026-10",
        )
    )
    return entries


EU_MEMBER_STATES_10_18_SOURCES: List[RegulatorySourceEntry] = (
    _NATIONAL_SOURCES + _build_german_laender_sources()
)


def get_eu_member_states_10_18_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of all curated EU Member-State (10–18) and German Länder sources."""
    return list(EU_MEMBER_STATES_10_18_SOURCES)


# =============================================================================
# 3. Authentic Multilingual Fixtures for RD-08 (Germany BDSG & France LIL)
#    Exact character offsets verified programmatically at module load.
# =============================================================================

_BDSG_S26_ORIGINAL_DE = (
    "§ 26 Datenverarbeitung für Zwecke des Beschäftigungsverhältnisses\n"
    "(1) Personenbezogene Daten von Beschäftigten dürfen für Zwecke des Beschäftigungsverhältnisses "
    "verarbeitet werden, wenn dies für die Entscheidung über die Begründung eines "
    "Beschäftigungsverhältnisses oder nach Begründung des Beschäftigungsverhältnisses für dessen "
    "Durchführung oder Beendigung oder zur Ausübung oder Erfüllung der sich aus einem Gesetz oder "
    "einem Tarifvertrag, einer Betriebs- oder Dienstvereinbarung (Kollektivvereinbarung) ergebenden "
    "Rechte und Pflichten der Interessenvertretung der Beschäftigten erforderlich ist. Zur Aufdeckung "
    "von Straftaten dürfen personenbezogene Daten von Beschäftigten nur dann verarbeitet werden, wenn "
    "zu dokumentierende tatsächliche Anhaltspunkte den Verdacht begründen, dass die betroffene Person "
    "im Beschäftigungsverhältnis eine Straftat begangen hat, die Verarbeitung zur Aufdeckung "
    "erforderlich ist und das schutzwürdige Interesse der oder des Beschäftigten an dem Ausschluss der "
    "Verarbeitung nicht überwiegt, insbesondere Art und Ausmaß im Hinblick auf den Anlass nicht "
    "unverhältnismäßig sind."
)

_BDSG_S26_EXCERPT_DE = (
    "Personenbezogene Daten von Beschäftigten dürfen für Zwecke des Beschäftigungsverhältnisses "
    "verarbeitet werden, wenn dies für die Entscheidung über die Begründung eines "
    "Beschäftigungsverhältnisses oder nach Begründung des Beschäftigungsverhältnisses für dessen "
    "Durchführung oder Beendigung"
)

_BDSG_S38_ORIGINAL_DE = (
    "§ 38 Datenschutzbeauftragte nichtöffentlicher Stellen\n"
    "(1) Ergänzend zu Artikel 37 Absatz 1 Buchstabe b und c der Verordnung (EU) 2016/679 benennen "
    "der Verantwortliche und der Auftragsverarbeiter eine Datenschutzbeauftragte oder einen "
    "Datenschutzbeauftragten, soweit sie in der Regel mindestens 20 Personen ständig mit der "
    "automatisierten Verarbeitung personenbezogener Daten beschäftigen. Nehmen der Verantwortliche "
    "oder der Auftragsverarbeiter Verarbeitungen vor, die einer Datenschutz-Folgenabschätzung nach "
    "Artikel 35 der Verordnung (EU) 2016/679 unterliegen, oder verarbeiten sie personenbezogene Daten "
    "geschäftsmäßig zum Zweck der Übermittlung, der anonymisierten Übermittlung oder für Zwecke der "
    "Markt- oder Meinungsforschung, haben sie unabhängig von der Anzahl der mit der Verarbeitung "
    "beschäftigten Personen eine Datenschutzbeauftragte oder einen Datenschutzbeauftragten zu benennen."
)

_BDSG_S38_EXCERPT_DE = (
    "Ergänzend zu Artikel 37 Absatz 1 Buchstabe b und c der Verordnung (EU) 2016/679 benennen "
    "der Verantwortliche und der Auftragsverarbeiter eine Datenschutzbeauftragte oder einen "
    "Datenschutzbeauftragten, soweit sie in der Regel mindestens 20 Personen ständig mit der "
    "automatisierten Verarbeitung personenbezogener Daten beschäftigen."
)

_LIL_ART82_ORIGINAL_FR = (
    "Article 82\n"
    "Tout abonné ou utilisateur d'un service de communications électroniques doit être informé de "
    "manière claire et complète, sauf s'il l'a été au préalable, par le responsable du traitement ou "
    "son représentant :\n"
    "1° De la finalité de toute action tendant à accéder, par voie de transmission électronique, à des "
    "informations déjà stockées dans son équipement terminal de communications électroniques, ou à "
    "inscrire des informations dans cet équipement ;\n"
    "2° Des moyens dont il dispose pour s'y opposer.\n"
    "Ces accès ou inscriptions ne peuvent avoir lieu qu'à condition que l'abonné ou la personne "
    "utilisatrice ait exprimé, après avoir reçu cette information, son accord qui peut résulter de "
    "paramètres appropriés de son dispositif de connexion ou de tout autre dispositif placé sous son "
    "contrôle.\n"
    "Ces dispositions ne sont pas applicables si l'accès aux informations stockées dans l'équipement "
    "terminal de l'utilisateur ou l'inscription d'informations dans l'équipement terminal de "
    "l'utilisateur :\n"
    "1° Soit a pour finalité exclusive de permettre ou faciliter la communication par voie "
    "électronique ;\n"
    "2° Soit est strictement nécessaire à la fourniture d'un service de communication en ligne à la "
    "demande expresse de l'utilisateur."
)

_LIL_ART82_EXCERPT_FR = (
    "Ces accès ou inscriptions ne peuvent avoir lieu qu'à condition que l'abonné ou la personne "
    "utilisatrice ait exprimé, après avoir reçu cette information, son accord qui peut résulter de "
    "paramètres appropriés de son dispositif de connexion ou de tout autre dispositif placé sous son "
    "contrôle."
)


AUTHENTIC_FR_DE_MULTILINGUAL_FIXTURES: Dict[str, Dict[str, Any]] = {
    "EU-DE-BDSG-S26": {
        "document_id": "DOC-EU-DE-BDSG-2018-S26",
        "source_id": "SRC-EU-DE-GII-BDSG",
        "jurisdiction_id": "EU-DE",
        "official_citation": "§ 26 Abs. 1 BDSG (BGBl. I S. 2097)",
        "eli_or_celex_identifier": "eli/bund/bgbl-1/2017/s2097/2026-01-01/1/deu",
        "source_section": "§ 26 Abs. 1 Satz 1",
        "article": "§ 26",
        "subsection": "(1)",
        "source_language": "de",
        "translation_status": "verified_translation",
        "full_provision_text_original": _BDSG_S26_ORIGINAL_DE,
        "exact_source_excerpt": _BDSG_S26_EXCERPT_DE,
        "text_start_offset": _BDSG_S26_ORIGINAL_DE.index(_BDSG_S26_EXCERPT_DE),
        "text_end_offset": _BDSG_S26_ORIGINAL_DE.index(_BDSG_S26_EXCERPT_DE) + len(_BDSG_S26_EXCERPT_DE),
        "english_translation": (
            "Personal data of employees may be processed for employment-related purposes where necessary "
            "for hiring decisions or, after establishment of the employment relationship, for carrying it "
            "out or terminating it, or to exercise or satisfy rights and obligations of employees' "
            "representation laid down by law or by collective agreements or works/service agreements."
        ),
        "normalized_legal_concept": "employee_data_processing_necessity_bdsg_s26",
        "thresholds": {},
    },
    "EU-DE-BDSG-S38": {
        "document_id": "DOC-EU-DE-BDSG-2018-S38",
        "source_id": "SRC-EU-DE-GII-BDSG",
        "jurisdiction_id": "EU-DE",
        "official_citation": "§ 38 Abs. 1 BDSG (BGBl. I S. 2097, geändert durch 2. DSAnpUG-EU)",
        "eli_or_celex_identifier": "eli/bund/bgbl-1/2017/s2097/2026-01-01/1/deu",
        "source_section": "§ 38 Abs. 1 Satz 1",
        "article": "§ 38",
        "subsection": "(1)",
        "source_language": "de",
        "translation_status": "verified_translation",
        "full_provision_text_original": _BDSG_S38_ORIGINAL_DE,
        "exact_source_excerpt": _BDSG_S38_EXCERPT_DE,
        "text_start_offset": _BDSG_S38_ORIGINAL_DE.index(_BDSG_S38_EXCERPT_DE),
        "text_end_offset": _BDSG_S38_ORIGINAL_DE.index(_BDSG_S38_EXCERPT_DE) + len(_BDSG_S38_EXCERPT_DE),
        "english_translation": (
            "In addition to Article 37(1)(b) and (c) of Regulation (EU) 2016/679, the controller and the "
            "processor shall designate a data protection officer if they normally constantly employ at "
            "least 20 persons dealing with the automated processing of personal data."
        ),
        "normalized_legal_concept": "mandatory_dpo_designation_20_employees_bdsg_s38",
        "thresholds": {"automated_processing_employee_count_min": 20},
    },
    "EU-FR-LIL-ART82": {
        "document_id": "DOC-EU-FR-LIL-78-17-ART82",
        "source_id": "SRC-EU-FR-LEGIFRANCE-LIL",
        "jurisdiction_id": "EU-FR",
        "official_citation": "Loi n° 78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés, Article 82",
        "eli_or_celex_identifier": "eli/loi/1978/1/6/78-17/jo/article_82",
        "source_section": "Article 82, alinéa 4",
        "article": "Article 82",
        "subsection": "alinéa 4",
        "source_language": "fr",
        "translation_status": "verified_translation",
        "full_provision_text_original": _LIL_ART82_ORIGINAL_FR,
        "exact_source_excerpt": _LIL_ART82_EXCERPT_FR,
        "text_start_offset": _LIL_ART82_ORIGINAL_FR.index(_LIL_ART82_EXCERPT_FR),
        "text_end_offset": _LIL_ART82_ORIGINAL_FR.index(_LIL_ART82_EXCERPT_FR) + len(_LIL_ART82_EXCERPT_FR),
        "english_translation": (
            "Such access or storage may take place only on condition that the subscriber or user has "
            "expressed, after having received this information, their agreement, which may result from "
            "appropriate settings of their connection device or any other device placed under their "
            "control."
        ),
        "normalized_legal_concept": "prior_informed_consent_cookies_and_tracers_lil_art82",
        "thresholds": {"strictly_necessary_communication_exemption": True},
    },
}


__all__ = [
    "EU_MEMBER_STATES_10_18_SOURCES",
    "get_eu_member_states_10_18_sources",
    "AUTHENTIC_FR_DE_MULTILINGUAL_FIXTURES",
]
