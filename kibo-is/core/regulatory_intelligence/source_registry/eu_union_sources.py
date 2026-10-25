"""
KIBO Privacy OS — EU-Wide EUR-Lex and Cellar Source Registry & Authentic Fixtures (G10)
Covers EUR-Lex Official Journal & ELI/CELEX Repository, EU Publications Office Cellar SPARQL & REST API,
European Commission Adequacy Decisions & Standard Contractual Clauses, and the European AI Office.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    RegulatorySourceEntry,
    SourceHealthStatus,
    compute_sha256_hex,
)

EU_UNION_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-EU-UNION-EURLEX-ELI",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="Publications Office of the European Union — EUR-Lex Official Journal & ELI/CELEX Repository",
        authority_type="official_gazette",
        official_domain="eur-lex.europa.eu",
        discovery_endpoint="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commission Decision 2011/833/EU on the reuse of Commission documents — attribution required",
        rate_limit_rpm=30,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "artificial_intelligence",
            "digital_operational_resilience",
            "electronic_communications",
        ],
        legal_instrument_types=["statute", "regulation", "official_policy_directive"],
        source_priority=1,
        languages=["en", "fr", "de"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ELI-2026-10-25-OJ-L-SERIES",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-UNION-CELLAR-SPARQL",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="Publications Office of the European Union — Cellar SPARQL & REST API",
        authority_type="official_gazette",
        official_domain="publications.europa.eu",
        discovery_endpoint="https://publications.europa.eu/webapi/rdf/sparql",
        feed_format="cellar_rdf",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commission Decision 2011/833/EU — Common Data Repository (CDM/FRBR/ELI RDF) open reuse",
        rate_limit_rpm=60,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "artificial_intelligence",
            "digital_operational_resilience",
            "cross_border_transfers",
        ],
        legal_instrument_types=["statute", "regulation", "official_guidance", "court_judgment"],
        source_priority=1,
        languages=["en", "fr", "de"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CELLAR-CDM-2026-10-25T12:00:00Z",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-EC-ADEQUACY-SCC",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="European Commission — DG Justice and Consumers (Adequacy Decisions & Standard Contractual Clauses)",
        authority_type="sector_regulator",
        official_domain="commission.europa.eu",
        discovery_endpoint="https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection_en",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commission Decision 2011/833/EU on the reuse of Commission documents — attribution required",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cross_border_transfers",
            "adequacy_decisions",
            "standard_contractual_clauses",
        ],
        legal_instrument_types=["regulation", "official_guidance", "official_policy_directive"],
        source_priority=1,
        languages=["en", "fr", "de"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="EC-DG-JUST-SCC-2021-914-DPF-2023-1795",
    ),
    RegulatorySourceEntry(
        source_id="SRC-EU-AI-OFFICE",
        jurisdiction_id="EU",
        parent_jurisdiction=None,
        authority_name="European Commission — European AI Office (DG CNECT)",
        authority_type="sector_regulator",
        official_domain="digital-strategy.ec.europa.eu",
        discovery_endpoint="https://digital-strategy.ec.europa.eu/en/policies/ai-office",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commission Decision 2011/833/EU on the reuse of Commission documents — attribution required",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "artificial_intelligence",
            "general_purpose_ai_governance",
            "high_risk_ai_systems",
            "algorithmic_transparency",
            "privacy",
        ],
        legal_instrument_types=["official_guidance", "regulatory_consultation", "official_policy_directive"],
        source_priority=1,
        languages=["en", "fr", "de"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="EU-AI-OFFICE-GPAI-CODE-2026-10",
    ),
]


def _build_gdpr_corrigendum_diff() -> Dict[str, Any]:
    prev_text = (
        "Article 37(1)(c): the core activities of the controller or the processor consist of processing "
        "on a large scale of special categories of data pursuant to Article 9 and personal data relating "
        "to criminal convictions and offences referred to in Article 10."
    )
    curr_text = (
        "Article 37(1)(c) [Corrigendum OJ L 127, 23.5.2018, p. 2]: the core activities of the controller "
        "or the processor consist of processing on a large scale of special categories of data pursuant "
        "to Article 9 or personal data relating to criminal convictions and offences referred to in Article 10."
    )
    return {
        "diff_id": "RD-04-EU-GDPR-2018-CORRIGENDUM-ART37",
        "rule_id": "RD-04",
        "document_id": "DOC-EU-REG-2016-679",
        "jurisdiction_id": "EU",
        "eli_or_celex_identifier": "CELEX:32016R0679R(02)",
        "eli_uri": "https://eur-lex.europa.eu/eli/reg/2016/679/corrigendum/2018-05-23/oj",
        "consolidated_eli_uri": "https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04",
        "provision_ref": "Article 37(1)(c) & Article 33(1)",
        "previous_version": "1.0.0-OJ-L119-20160504",
        "current_version": "1.1.0-CORR-OJ-L127-20180523",
        "previous_effective_date": "2018-05-25",
        "current_effective_date": "2018-05-25",
        "previous_text": prev_text,
        "current_text": curr_text,
        "previous_sha256": compute_sha256_hex(prev_text),
        "current_sha256": compute_sha256_hex(curr_text),
        "change_type": "substantive_amendment",
        "is_substantive": True,
        "changed_elements_summary": [
            "Replaced conjunctive 'and' with disjunctive 'or' in Article 37(1)(c) DPO designation threshold between Article 9 special category data and Article 10 criminal offence data (OJ L 127, 23.5.2018, p. 2).",
            "Clarified language alignment across EN/FR/DE authentic texts for Article 33(1) 72-hour supervisory authority breach notification and Article 42(7) certification validity.",
        ],
    }


AUTHENTIC_EURLEX_FIXTURES: List[Dict[str, Any]] = [
    {
        "document_id": "DOC-EU-REG-2016-679",
        "source_id": "SRC-EU-UNION-EURLEX-ELI",
        "cellar_source_id": "SRC-EU-UNION-CELLAR-SPARQL",
        "jurisdiction_id": "EU",
        "document_type": "regulation",
        "canonical_title": (
            "Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 "
            "on the protection of natural persons with regard to the processing of personal data and "
            "on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation)"
        ),
        "eli_or_celex_identifier": "CELEX:32016R0679",
        "celex_id": "32016R0679",
        "eli_path": "eli/reg/2016/679/oj",
        "official_source_url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "cellar_uri": "http://publications.europa.eu/resource/celex/32016R0679",
        "official_citation": "OJ L 119, 4.5.2016, p. 1–88",
        "publication_date": "2016-05-04",
        "effective_date": "2018-05-25",
        "document_version": "1.1.0-CORR-2018-05-23",
        "languages": ["en", "fr", "de"],
        "multilingual_titles": {
            "en": "Regulation (EU) 2016/679 (General Data Protection Regulation — GDPR)",
            "fr": "Règlement (UE) 2016/679 du Parlement européen et du Conseil du 27 avril 2016 (Règlement général sur la protection des données — RGPD)",
            "de": "Verordnung (EU) 2016/679 des Europäischen Parlaments und des Rates vom 27. April 2016 (Datenschutz-Grundverordnung — DSGVO)",
        },
        "multilingual_passages": {
            "en": (
                "Article 32(1): Taking into account the state of the art, the costs of implementation and the nature, "
                "scope, context and purposes of processing as well as the risk of varying likelihood and severity for "
                "the rights and freedoms of natural persons, the controller and the processor shall implement appropriate "
                "technical and organisational measures to ensure a level of security appropriate to the risk."
            ),
            "fr": (
                "Article 32, paragraphe 1: Compte tenu de l'état des connaissances, des coûts de mise en œuvre et de la "
                "nature, de la portée, du contexte et des finalités du traitement ainsi que des risques, dont le degré "
                "de probabilité et de gravité varie, pour les droits et libertés des personnes physiques, le responsable "
                "du traitement et le sous-traitant mettent en œuvre les mesures techniques et organisationnelles "
                "appropriées afin de garantir un niveau de sécurité adapté au risque."
            ),
            "de": (
                "Artikel 32 Absatz 1: Unter Berücksichtigung des Stands der Technik, der Implementierungskosten und der "
                "Art, des Umfangs, der Umstände und der Zwecke der Verarbeitung sowie der unterschiedlichen "
                "Eintrittswahrscheinlichkeit und Schwere des Risikos für die Rechte und Freiheiten natürlicher Personen "
                "treffen der Verantwortliche und der Auftragsverarbeiter geeignete technische und organisatorische "
                "Maßnahmen, um ein dem Risiko angemessenes Schutzniveau zu gewährleisten."
            ),
        },
        "version_history": [
            {
                "version": "1.0.0-OJ-L119-20160504",
                "eli_or_celex_identifier": "CELEX:32016R0679",
                "eli_path": "eli/reg/2016/679/oj",
                "publication_date": "2016-05-04",
                "description": "Original Official Journal publication OJ L 119, 4.5.2016, p. 1–88",
            },
            {
                "version": "1.1.0-CORR-OJ-L127-20180523",
                "eli_or_celex_identifier": "CELEX:32016R0679R(02)",
                "eli_path": "eli/reg/2016/679/corrigendum/2018-05-23/oj",
                "publication_date": "2018-05-23",
                "description": "Corrigendum to Regulation (EU) 2016/679 (OJ L 127, 23.5.2018, p. 2–5)",
            },
        ],
        "rd_04_version_diff": _build_gdpr_corrigendum_diff(),
    },
    {
        "document_id": "DOC-EU-REG-2024-1689",
        "source_id": "SRC-EU-UNION-EURLEX-ELI",
        "cellar_source_id": "SRC-EU-UNION-CELLAR-SPARQL",
        "ai_office_source_id": "SRC-EU-AI-OFFICE",
        "jurisdiction_id": "EU",
        "document_type": "regulation",
        "canonical_title": (
            "Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 "
            "laying down harmonised rules on artificial intelligence and amending Regulations (EC) No 300/2008, "
            "(EU) No 167/2013, (EU) No 168/2013, (EU) 2018/858, (EU) 2018/1139 and (EU) 2019/2144 and "
            "Directives 2014/90/EU, (EU) 2016/797 and (EU) 2020/1828 (Artificial Intelligence Act)"
        ),
        "eli_or_celex_identifier": "CELEX:32024R1689",
        "celex_id": "32024R1689",
        "eli_path": "eli/reg/2024/1689/oj",
        "official_source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "cellar_uri": "http://publications.europa.eu/resource/celex/32024R1689",
        "official_citation": "OJ L, 2024/1689, 12.7.2024",
        "publication_date": "2024-07-12",
        "effective_date": "2024-08-01",
        "document_version": "1.0.0-OJ-L-20240712",
        "languages": ["en", "fr", "de"],
        "multilingual_titles": {
            "en": "Regulation (EU) 2024/1689 (Artificial Intelligence Act — EU AI Act)",
            "fr": "Règlement (UE) 2024/1689 établissant des règles harmonisées concernant l'intelligence artificielle (Loi sur l'intelligence artificielle)",
            "de": "Verordnung (EU) 2024/1689 zur Festlegung harmonisierter Vorschriften für künstliche Intelligenz (Gesetz über künstliche Intelligenz — KI-Verordnung)",
        },
        "multilingual_passages": {
            "en": (
                "Article 5(1)(a): The placing on the market, the putting into service or the use of an AI system "
                "that deploys subliminal techniques beyond a person's consciousness or purposefully manipulative "
                "or deceptive techniques, with the objective, or the effect of materially distorting the behaviour "
                "of a person or a group of persons, shall be prohibited."
            ),
            "fr": (
                "Article 5, paragraphe 1, point a): Est interdite la mise sur le marché, la mise en service ou "
                "l'utilisation d'un système d'IA qui recourt à des techniques subliminales au-delà de la conscience "
                "d'une personne ou à des techniques délibérément manipulatrices ou trompeuses ayant pour objectif "
                "ou pour effet d'altérer substantiellement le comportement d'une personne ou d'un groupe de personnes."
            ),
            "de": (
                "Artikel 5 Absatz 1 Buchstabe a: Das Inverkehrbringen, die Inbetriebnahme oder die Verwendung eines "
                "KI-Systems, das unterschwellige Techniken außerhalb des Bewusstseins einer Person oder absichtlich "
                "manipulative oder täuschende Techniken einsetzt, mit dem Ziel oder der Wirkung, das Verhalten "
                "einer Person oder einer Gruppe von Personen wesentlich zu beeinflussen, ist verboten."
            ),
        },
    },
    {
        "document_id": "DOC-EU-DIR-2022-2555",
        "source_id": "SRC-EU-UNION-EURLEX-ELI",
        "cellar_source_id": "SRC-EU-UNION-CELLAR-SPARQL",
        "jurisdiction_id": "EU",
        "document_type": "official_policy_directive",
        "canonical_title": (
            "Directive (EU) 2022/2555 of the European Parliament and of the Council of 14 December 2022 "
            "on measures for a high common level of cybersecurity across the Union, amending Regulation "
            "(EU) No 910/2014 and Directive (EU) 2018/1972, and repealing Directive (EU) 2016/1148 (NIS 2 Directive)"
        ),
        "eli_or_celex_identifier": "CELEX:32022L2555",
        "celex_id": "32022L2555",
        "eli_path": "eli/dir/2022/2555/oj",
        "official_source_url": "https://eur-lex.europa.eu/eli/dir/2022/2555/oj",
        "cellar_uri": "http://publications.europa.eu/resource/celex/32022L2555",
        "official_citation": "OJ L 333, 27.12.2022, p. 80–152",
        "publication_date": "2022-12-27",
        "effective_date": "2024-10-18",
        "document_version": "1.0.0-OJ-L333-20221227",
        "languages": ["en", "fr", "de"],
        "multilingual_titles": {
            "en": "Directive (EU) 2022/2555 on measures for a high common level of cybersecurity across the Union (NIS 2)",
            "fr": "Directive (UE) 2022/2555 concernant des mesures destinées à assurer un niveau élevé commun de cybersécurité dans l'ensemble de l'Union (Directive SRI 2 / NIS 2)",
            "de": "Richtlinie (EU) 2022/2555 über Maßnahmen für ein hohes gemeinsames Cybersicherheitsniveau in der Union (NIS-2-Richtlinie)",
        },
        "multilingual_passages": {
            "en": (
                "Article 23(4)(a): Essential and important entities shall submit to the CSIRT or, where applicable, "
                "the competent authority without undue delay and in any event within 24 hours of becoming aware of "
                "the significant incident, an early warning, which, where applicable, shall indicate whether the "
                "significant incident is suspected of being caused by unlawful or malicious acts or could have a "
                "cross-border impact."
            ),
            "fr": (
                "Article 23, paragraphe 4, point a): Les entités essentielles et importantes notifient au CSIRT ou, "
                "le cas échéant, à l'autorité compétente, sans retard injustifié et en tout état de cause dans un "
                "délai de 24 heures après avoir eu connaissance de l'incident significatif, une alerte précoce "
                "indiquant, le cas échéant, s'il est suspecté que l'incident significatif a été causé par des actes "
                "illicites ou malveillants ou pourrait avoir un impact transfrontière."
            ),
            "de": (
                "Artikel 23 Absatz 4 Buchstabe a: Wesentliche und wichtige Einrichtungen übermitteln dem CSIRT oder "
                "gegebenenfalls der zuständigen Behörde unverzüglich, in jedem Fall aber innerhalb von 24 Stunden, "
                "nachdem sie von dem erheblichen Sicherheitsvorfall Kenntnis erlangt haben, eine Frühwarnung, in "
                "der gegebenenfalls angegeben wird, ob der Verdacht besteht, dass der erhebliche Sicherheitsvorfall "
                "auf rechtswidrige oder böswillige Handlungen zurückzuführen ist oder grenzüberschreitende "
                "Auswirkungen haben könnte."
            ),
        },
    },
    {
        "document_id": "DOC-EU-REG-2022-2554",
        "source_id": "SRC-EU-UNION-EURLEX-ELI",
        "cellar_source_id": "SRC-EU-UNION-CELLAR-SPARQL",
        "jurisdiction_id": "EU",
        "document_type": "regulation",
        "canonical_title": (
            "Regulation (EU) 2022/2554 of the European Parliament and of the Council of 14 December 2022 "
            "on digital operational resilience for the financial sector and amending Regulations (EC) No 1060/2009, "
            "(EU) No 648/2012, (EU) No 600/2014, (EU) No 909/2014 and (EU) 2016/1011 (DORA)"
        ),
        "eli_or_celex_identifier": "CELEX:32022R2554",
        "celex_id": "32022R2554",
        "eli_path": "eli/reg/2022/2554/oj",
        "official_source_url": "https://eur-lex.europa.eu/eli/reg/2022/2554/oj",
        "cellar_uri": "http://publications.europa.eu/resource/celex/32022R2554",
        "official_citation": "OJ L 333, 27.12.2022, p. 1–79",
        "publication_date": "2022-12-27",
        "effective_date": "2025-01-17",
        "document_version": "1.0.0-OJ-L333-20221227",
        "languages": ["en", "fr", "de"],
        "multilingual_titles": {
            "en": "Regulation (EU) 2022/2554 on digital operational resilience for the financial sector (DORA)",
            "fr": "Règlement (UE) 2022/2554 sur la résilience opérationnelle numérique du secteur financier (DORA)",
            "de": "Verordnung (EU) 2022/2554 über die digitale operationale Resilienz im Finanzsektor (DORA)",
        },
        "multilingual_passages": {
            "en": (
                "Article 5(1): Financial entities shall have in place an internal governance and control framework "
                "that ensures an effective and prudent management of ICT risk, in accordance with Chapter II, in "
                "order to achieve a high level of digital operational resilience."
            ),
            "fr": (
                "Article 5, paragraphe 1: Les entités financières mettent en place un cadre de gouvernance et de "
                "contrôle internes qui assure une gestion efficace et prudente du risque lié aux TIC, conformément "
                "au chapitre II, afin d'atteindre un niveau élevé de résilience opérationnelle numérique."
            ),
            "de": (
                "Artikel 5 Absatz 1: Finanzunternehmen verfügen über einen internen Governance- und Kontrollrahmen, "
                "der ein wirksames und umsichtiges Management des IKT-Risikos im Einklang mit Kapitel II "
                "gewährleistet, um ein hohes Niveau an digitaler operationaler Resilienz zu erreichen."
            ),
        },
    },
    {
        "document_id": "DOC-EU-DIR-2002-58",
        "source_id": "SRC-EU-UNION-EURLEX-ELI",
        "cellar_source_id": "SRC-EU-UNION-CELLAR-SPARQL",
        "jurisdiction_id": "EU",
        "document_type": "official_policy_directive",
        "canonical_title": (
            "Directive 2002/58/EC of the European Parliament and of the Council of 12 July 2002 "
            "concerning the processing of personal data and the protection of privacy in the electronic "
            "communications sector (Directive on privacy and electronic communications — ePrivacy Directive)"
        ),
        "eli_or_celex_identifier": "CELEX:32002L0058",
        "celex_id": "32002L0058",
        "consolidated_celex_id": "02002L0058-20091219",
        "amending_celex_ids": ["32009L0136"],
        "eli_path": "eli/dir/2002/58/oj",
        "official_source_url": "https://eur-lex.europa.eu/eli/dir/2002/58/oj",
        "cellar_uri": "http://publications.europa.eu/resource/celex/32002L0058",
        "official_citation": "OJ L 201, 31.7.2002, p. 37–47",
        "publication_date": "2002-07-31",
        "effective_date": "2003-10-31",
        "document_version": "2.0.0-CONS-2009-12-19",
        "languages": ["en", "fr", "de"],
        "multilingual_titles": {
            "en": "Directive 2002/58/EC on privacy and electronic communications (ePrivacy Directive)",
            "fr": "Directive 2002/58/CE concernant le traitement des données à caractère personnel et la protection de la vie privée dans le secteur des communications électroniques (Directive vie privée et communications électroniques)",
            "de": "Richtlinie 2002/58/EG über die Verarbeitung personenbezogener Daten und den Schutz der Privatsphäre in der elektronischen Kommunikation (Datenschutzrichtlinie für elektronische Kommunikation)",
        },
        "multilingual_passages": {
            "en": (
                "Article 5(3): Member States shall ensure that the storing of information, or the gaining of access "
                "to information already stored, in the terminal equipment of a subscriber or user is only allowed "
                "on condition that the subscriber or user concerned has given his or her consent, having been "
                "provided with clear and comprehensive information, in accordance with Directive 95/46/EC, inter "
                "alia, about the purposes of the processing."
            ),
            "fr": (
                "Article 5, paragraphe 3: Les États membres garantissent que le stockage d'informations, ou l'obtention "
                "de l'accès à des informations déjà stockées, dans l'équipement terminal d'un abonné ou d'un "
                "utilisateur n'est permis qu'à condition que l'abonné ou l'utilisateur ait donné son accord, après "
                "avoir reçu, dans le respect de la directive 95/46/CE, une information claire et complète, "
                "notamment sur les finalités du traitement."
            ),
            "de": (
                "Artikel 5 Absatz 3: Die Mitgliedstaaten stellen sicher, dass die Speicherung von Informationen oder "
                "der Zugriff auf Informationen, die bereits im Endgerät eines Teilnehmers oder Nutzers gespeichert "
                "sind, nur gestattet ist, wenn der betreffende Teilnehmer oder Nutzer auf der Grundlage von klaren "
                "und umfassenden Informationen, die er gemäß der Richtlinie 95/46/EG u. a. über die Zwecke der "
                "Verarbeitung erhält, seine Einwilligung gegeben hat."
            ),
        },
    },
]


def get_eu_union_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of the curated EU-wide regulatory intelligence sources."""
    return list(EU_UNION_SOURCES)


__all__ = [
    "EU_UNION_SOURCES",
    "AUTHENTIC_EURLEX_FIXTURES",
    "get_eu_union_sources",
]
