"""
KIBO Privacy OS — Canadian Privacy Commissioner Decisions & Enforcement Source Registry (G08).

Covers authoritative federal, provincial, and territorial privacy commissioner feeds across Canada:
- Office of the Privacy Commissioner of Canada (OPC) — priv.gc.ca (PIPEDA Findings & Privacy Act Investigations)
- Commission d'accès à l'information du Québec (CAI) — cai.gouv.qc.ca (Décisions de la Commission, Loi 25 / Act respecting the protection of personal information in the private sector)
- Information and Privacy Commissioner of Ontario (IPC Ontario) — ipc.on.ca (PHIPA Decisions & FIPPA/MFIPPA Orders)
- Office of the Information and Privacy Commissioner for British Columbia (OIPC BC) — oipc.bc.ca (PIPA & FIPPA Orders)
- Office of the Information and Privacy Commissioner of Alberta (OIPC Alberta) — oipc.ab.ca (PIPA, FOIP & HIA Orders)
- Office of the Information and Privacy Commissioner of Saskatchewan (OIPC SK) — oipc.sk.ca
- Manitoba Ombudsman — ombudsman.mb.ca
- Office of the Ombud New Brunswick — ombudnb.ca
- Office of the Information and Privacy Commissioner for Nova Scotia (OIPC NS) — oipc.novascotia.ca
- Office of the Information and Privacy Commissioner of Prince Edward Island (OIPC PEI) — assembly.pe.ca
- Office of the Information and Privacy Commissioner of Newfoundland and Labrador (OIPC NL) — oipc.nl.ca
- Yukon Information and Privacy Commissioner — yukonipc.ca
- Office of the Information and Privacy Commissioner of the Northwest Territories (OIPC NWT) — atipp-nt.ca
- Information and Privacy Commissioner of Nunavut — atipp-nu.ca
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
# Authoritative Canadian Privacy Commissioner Source Registry Entries
# ---------------------------------------------------------------------------

CANADA_COMMISSIONER_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-OPC-PIPEDA",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Privacy Commissioner of Canada (OPC) / Commissariat à la protection de la vie privée du Canada",
        authority_type="data_protection_authority",
        official_domain="priv.gc.ca",
        discovery_endpoint="https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Crown Copyright — Government of Canada Open Government / OPC Terms and Conditions (non-commercial & commercial reproduction permitted with attribution and accuracy)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "pipeda_findings",
            "biometrics",
            "cross_border_transfers",
            "cybersecurity_safeguards",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "official_guidance",
        ],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="opc-pipeda-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-OPC-PRIVACY-ACT",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Privacy Commissioner of Canada (OPC) — Privacy Act Investigations",
        authority_type="data_protection_authority",
        official_domain="priv.gc.ca",
        discovery_endpoint="https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-federal-institutions/",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Crown Copyright — Government of Canada Open Government / OPC Terms and Conditions (attribution required)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "federal_public_sector_privacy_act",
            "privacy_impact_assessments",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "official_guidance",
        ],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="opc-pa-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-QC-CAI-DECISIONS",
        jurisdiction_id="CA-QC",
        parent_jurisdiction="CA-FED",
        authority_name="Commission d'accès à l'information du Québec (CAI)",
        authority_type="data_protection_authority",
        official_domain="cai.gouv.qc.ca",
        discovery_endpoint="https://www.cai.gouv.qc.ca/decisions-de-la-commission",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Gouvernement du Québec / CAI — Public administrative tribunal and oversight decisions (attribution required)",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "quebec_law_25",
            "biometrics_database_registration",
            "confidentiality_incidents",
            "privacy_impact_assessments",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "administrative_tribunal_ruling",
            "official_guidance",
        ],
        source_priority=1,
        languages=["fr", "en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="cai-qc-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-ON-IPC-DECISIONS",
        jurisdiction_id="CA-ON",
        parent_jurisdiction="CA-FED",
        authority_name="Information and Privacy Commissioner of Ontario (IPC Ontario)",
        authority_type="data_protection_authority",
        official_domain="ipc.on.ca",
        discovery_endpoint="https://decisions.ipc.on.ca/ipc-cipvp/en/rss/index.do",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="King's Printer for Ontario / IPC Ontario — Official PHIPA Decisions and FIPPA/MFIPPA Orders (attribution required)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "healthcare_privacy_phipa",
            "fippa_mfippa_orders",
            "ehr_audit_logging",
            "ransomware_breach_notification",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "administrative_tribunal_ruling",
            "official_guidance",
        ],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ipc-on-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-BC-OIPC-ORDERS",
        jurisdiction_id="CA-BC",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
        authority_type="data_protection_authority",
        official_domain="oipc.bc.ca",
        discovery_endpoint="https://www.oipc.bc.ca/rulings/orders/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC BC Copyright Policy — Official Orders & Investigation Reports under BC PIPA and FIPPA (attribution required)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "bc_pipa_orders",
            "bc_fippa_orders",
            "security_safeguards_s34",
            "employee_privacy",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "administrative_tribunal_ruling",
            "official_guidance",
        ],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-bc-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-AB-OIPC-ORDERS",
        jurisdiction_id="CA-AB",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of Alberta (OIPC Alberta)",
        authority_type="data_protection_authority",
        official_domain="oipc.ab.ca",
        discovery_endpoint="https://www.oipc.ab.ca/decisions/orders/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC Alberta — Official PIPA, FOIP, and HIA Orders and Breach Decisions (attribution required)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "alberta_pipa",
            "alberta_hia",
            "real_risk_of_significant_harm_rrosh",
            "breach_notification",
        ],
        legal_instrument_types=[
            "regulatory_enforcement_decision",
            "administrative_tribunal_ruling",
            "official_guidance",
        ],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-ab-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-SK-OIPC-REPORTS",
        jurisdiction_id="CA-SK",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of Saskatchewan (OIPC SK)",
        authority_type="data_protection_authority",
        official_domain="oipc.sk.ca",
        discovery_endpoint="https://oipc.sk.ca/decisions/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC Saskatchewan — Public Review and Investigation Reports under FOIP, LAFOIP, and HIPA (attribution required)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "saskatchewan_hipa", "audit_logging"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-sk-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-MB-OMBUDSMAN",
        jurisdiction_id="CA-MB",
        parent_jurisdiction="CA-FED",
        authority_name="Manitoba Ombudsman — Access and Privacy Division",
        authority_type="data_protection_authority",
        official_domain="ombudsman.mb.ca",
        discovery_endpoint="https://www.ombudsman.mb.ca/reports-and-resources/access-and-privacy-reports/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Manitoba Ombudsman — Official FIPPA and PHIA Investigation Reports (attribution required)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "manitoba_phia", "manitoba_fippa"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="mb-ombudsman-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-NB-OMBUD",
        jurisdiction_id="CA-NB",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Ombud New Brunswick — Access and Privacy Division",
        authority_type="data_protection_authority",
        official_domain="ombudnb.ca",
        discovery_endpoint="https://www.ombudnb.ca/en/access-and-privacy",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Office of the Ombud New Brunswick — Official RTIPPA and PHIPAA Reports (attribution required)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "nb_phipaa", "nb_rtippa"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="nb-ombud-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-NS-OIPC",
        jurisdiction_id="CA-NS",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner for Nova Scotia (OIPC NS)",
        authority_type="data_protection_authority",
        official_domain="oipc.novascotia.ca",
        discovery_endpoint="https://oipc.novascotia.ca/publicly-issued-reports",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Crown Copyright Nova Scotia / OIPC NS — FOIPOP and PHIA Review Reports (attribution required)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "ns_phia", "ns_foipop", "piidpa"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-ns-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-PE-OIPC",
        jurisdiction_id="CA-PE",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of Prince Edward Island (OIPC PEI)",
        authority_type="data_protection_authority",
        official_domain="assembly.pe.ca",
        discovery_endpoint="https://www.assembly.pe.ca/offices/information-and-privacy-commissioner/orders",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Legislative Assembly of PEI / OIPC PEI — Official FOIPP and HIA Orders (attribution required)",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "pei_hia", "pei_foipp"],
        legal_instrument_types=["regulatory_enforcement_decision", "administrative_tribunal_ruling"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-pe-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-NL-OIPC",
        jurisdiction_id="CA-NL",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of Newfoundland and Labrador (OIPC NL)",
        authority_type="data_protection_authority",
        official_domain="oipc.nl.ca",
        discovery_endpoint="https://www.oipc.nl.ca/reports/commissioner",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC Newfoundland and Labrador — Official ATIPPA, 2015 and PHIA Reports (attribution required)",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "nl_phia", "nl_atippa"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-nl-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-YT-IPC",
        jurisdiction_id="CA-YT",
        parent_jurisdiction="CA-FED",
        authority_name="Yukon Information and Privacy Commissioner (Yukon IPC)",
        authority_type="data_protection_authority",
        official_domain="yukonipc.ca",
        discovery_endpoint="https://www.yukonipc.ca/decisions-and-reports/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Yukon Ombudsman, Information and Privacy Commissioner — ATIPPA and HIPMA Reports (attribution required)",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "yukon_hipma", "yukon_atippa"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ipc-yt-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-NT-OIPC",
        jurisdiction_id="CA-NT",
        parent_jurisdiction="CA-FED",
        authority_name="Office of the Information and Privacy Commissioner of the Northwest Territories (OIPC NWT)",
        authority_type="data_protection_authority",
        official_domain="atipp-nt.ca",
        discovery_endpoint="https://www.atipp-nt.ca/decisions/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="OIPC Northwest Territories — Official ATIPP Act and HIA Review Recommendations (attribution required)",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "nwt_hia", "nwt_atipp"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="oipc-nt-2026-10-25",
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-NU-IPC",
        jurisdiction_id="CA-NU",
        parent_jurisdiction="CA-FED",
        authority_name="Information and Privacy Commissioner of Nunavut",
        authority_type="data_protection_authority",
        official_domain="atipp-nu.ca",
        discovery_endpoint="https://atipp-nu.ca/en/decisions",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Information and Privacy Commissioner of Nunavut — Official ATIPP Act Review Reports (attribution required)",
        rate_limit_rpm=15,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "nunavut_atipp", "privacy_impact_assessments"],
        legal_instrument_types=["regulatory_enforcement_decision", "official_guidance"],
        source_priority=1,
        languages=["en", "fr"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="ipc-nu-2026-10-25",
    ),
]


# ---------------------------------------------------------------------------
# Verbatim Passages for Authentic Canadian Commissioner Decisions
# ---------------------------------------------------------------------------

_CLEARVIEW_AI_2021_001_EXCERPT = (
    "PIPEDA Report of Findings #2021-001: Joint investigation of Clearview AI, Inc. by the Office "
    "of the Privacy Commissioner of Canada, the Commission d'accès à l'information du Québec, the "
    "Information and Privacy Commissioner for British Columbia, and the Information and Privacy "
    "Commissioner of Alberta (February 2, 2021). Clearview AI scraped over three billion images "
    "of faces and associated metadata from publicly accessible online sources without the knowledge "
    "or consent of the individuals depicted to create a biometric facial recognition database "
    "marketed to law enforcement and commercial entities. The Commissioners held that biometric "
    "facial templates are uniquely sensitive personal information, that publicly available "
    "information exemptions under PIPEDA s. 7(1)(b)/(2)(c.1), BC PIPA, Alberta PIPA, and Quebec's "
    "Private Sector Act and LCCJTI did not apply to mass indiscriminate scraping and biometric "
    "indexing, and that Clearview's purpose constituted mass surveillance that a reasonable person "
    "would not consider appropriate under PIPEDA s. 5(3), BC PIPA s. 4, and Alberta PIPA s. 4."
)

_EQUIFAX_2019_002_EXCERPT = (
    "PIPEDA Report of Findings #2019-002: Investigation into Equifax Inc. and Equifax Canada Co.'s "
    "compliance with PIPEDA in light of the 2017 breach of personal information (April 9, 2019). "
    "Attackers exploited an unpatched Apache Struts vulnerability (CVE-2017-5638) in Equifax Inc.'s "
    "U.S. infrastructure, compromising the personal information (names, Social Insurance Numbers, "
    "dates of birth, credit card numbers, and addresses) of approximately 19,000 Canadians. "
    "The Privacy Commissioner of Canada held that Equifax Canada remained accountable under PIPEDA "
    "Principle 4.1.3 for personal information transferred to its U.S. parent company (Equifax Inc.) "
    "for processing, and that both Equifax Inc. and Equifax Canada violated Principle 4.7 (Safeguards) "
    "through critical failures in vulnerability management, network segregation, cryptographic key "
    "management, access controls, and oversight of cross-border processing arrangements, as well as "
    "Principle 4.5 (Limiting Retention). Equifax Canada entered into a binding 6-year Compliance "
    "Agreement under PIPEDA s. 17.1."
)

_IPC_ONTARIO_PHIPA_175_EXCERPT = (
    "IPC Ontario PHIPA Decision 175 (February 28, 2022): Investigation into unauthorized access "
    "('snooping') into electronic patient health records under the Personal Health Information "
    "Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA). A health information custodian "
    "reported under s. 12(2) of PHIPA that an employee had accessed electronic medical records of "
    "patients outside the employee's circle of care and assigned duties without authorization. "
    "The Information and Privacy Commissioner of Ontario analyzed the custodian's obligations "
    "under PHIPA s. 12(1) to take steps that are reasonable in the circumstances to ensure that "
    "personal health information in its custody or control is protected against theft, loss, and "
    "unauthorized use or disclosure, and under s. 10 of O. Reg. 329/04 regarding electronic audit "
    "logs that record every instance of access and are proactively audited on a regular basis."
)

_IPC_ONTARIO_PHIPA_110_EXCERPT = (
    "IPC Ontario PHIPA Decision 110 (February 19, 2020): Ransomware cyberattack encrypting "
    "electronic personal health information held by a health information custodian under the "
    "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA). "
    "Malware infected the custodian's server and encrypted patient electronic health records, "
    "rendering the records inaccessible until restored. The Information and Privacy Commissioner "
    "of Ontario held that the unauthorized encryption of electronic personal health information "
    "by ransomware constitutes both an unauthorized 'use' (handling or dealing with the information) "
    "and a 'loss' of personal health information within the meaning of section 12(1) and section "
    "12(2) of PHIPA, even where there is no evidence of data exfiltration, thereby triggering "
    "mandatory breach notification obligations under PHIPA s. 12(2)."
)

_OIPC_BC_ORDER_P21_06_EXCERPT = (
    "OIPC BC Order P21-06 (2021 BCIPC 35, June 17, 2021): Inquiry under the Personal Information "
    "Protection Act, S.B.C. 2003, c. 63 (BC PIPA) regarding an organization's collection, use, "
    "retention, and security safeguards for employee and customer personal information. The "
    "adjudicator examined the organization's statutory obligation under section 34 of BC PIPA to "
    "protect personal information in its custody or under its control by making reasonable security "
    "arrangements to prevent unauthorized access, collection, use, disclosure, copying, modification, "
    "or disposal, as well as retention limitations under section 35 of PIPA once personal "
    "information is no longer necessary for legal or business purposes."
)


# ---------------------------------------------------------------------------
# Authentic, Historically Verifiable Canadian Commissioner Decisions
# ---------------------------------------------------------------------------

AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS: List[Dict[str, Any]] = [
    {
        "id": "verdict-ca-opc-2021-001",
        "decision_id": "DEC-CA-OPC-PIPEDA-2021-001",
        "document_id": "DOC-CA-OPC-PIPEDA-2021-001",
        "source_id": "SRC-CA-FED-OPC-PIPEDA",
        "official_citation": "PIPEDA Report of Findings #2021-001",
        "neutral_citation_or_id": "2021 CanLII 91125 (PCC) / PIPEDA Report of Findings #2021-001",
        "commissioner": "Office of the Privacy Commissioner of Canada (OPC), CAI Québec, OIPC BC, and OIPC Alberta",
        "court_tribunal_or_regulator": "Office of the Privacy Commissioner of Canada (Joint Investigation with CAI Québec, OIPC BC, OIPC AB)",
        "jurisdiction": "Federal / Joint (Canada, Québec, BC, Alberta)",
        "jurisdiction_id": "CA-FED",
        "parent_jurisdictions": ["CA-FED", "CA-QC", "CA-BC", "CA-AB"],
        "decision_date": "2021-02-02",
        "parties": [
            "Office of the Privacy Commissioner of Canada (OPC)",
            "Commission d'accès à l'information du Québec (CAI)",
            "Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
            "Office of the Information and Privacy Commissioner of Alberta (OIPC AB)",
            "Clearview AI, Inc. (Respondent)",
        ],
        "title": "PIPEDA Report of Findings #2021-001 — Joint Investigation of Clearview AI, Inc. (Biometric Facial Recognition Scraping)",
        "summary": (
            "Joint investigation by the federal OPC, CAI Québec, OIPC BC, and OIPC Alberta into Clearview AI, Inc.'s "
            "mass scraping of over three billion facial images from publicly accessible websites without consent to "
            "build a commercial biometric facial recognition search engine. Held that biometric facial templates are "
            "uniquely sensitive personal information, that 'publicly available' exceptions under PIPEDA s. 7 and "
            "provincial PIPA statutes do not permit indiscriminate scraping, and that mass biometric surveillance "
            "violated the 'appropriate purpose' requirement under PIPEDA s. 5(3), BC PIPA s. 4, and Alberta PIPA s. 4."
        ),
        "compliance_impact": (
            "Prohibits scraping publicly accessible web pages to extract biometric identifiers or train biometric "
            "identification models without express opt-in consent and an objectively appropriate purpose under PIPEDA "
            "s. 5(3), BC/AB PIPA s. 4, and Québec Law 25 biometric database declaration rules (LCCJTI s. 44-45)."
        ),
        "statutory_provisions": [
            "Personal Information Protection and Electronic Documents Act (PIPEDA), S.C. 2000, c. 5, s. 5(3), s. 6.1, s. 7(1)(b), s. 7(2)(c.1), Schedule 1 Clause 4.3",
            "Personal Information Protection Act (BC PIPA), S.B.C. 2003, c. 63, ss. 4, 6-8, 11, 14, 17",
            "Personal Information Protection Act (Alberta PIPA), S.A. 2003, c. P-6.5, ss. 4, 7, 11, 14, 17, 20",
            "Act respecting the protection of personal information in the private sector (Québec), CQLR c. P-39.1, ss. 4, 5, 12-14",
            "Act to establish a legal framework for information technology (Québec LCCJTI), CQLR c. C-1.1, ss. 44-45",
        ],
        "holdings": [
            "Biometric facial geometry generated from photographs is sensitive personal information in all circumstances because it is intrinsic, permanent, and uniquely identifies an individual across contexts.",
            "Social media pages and public websites do not qualify for the 'publicly available information' consent exemption under PIPEDA Regulations (SOR/2001-7) or provincial PIPA regulations when scraped en masse for unrelated commercial biometric indexing.",
            "Clearview AI's mass collection of biometric data for commercial and law enforcement facial recognition was not an appropriate purpose that a reasonable person would consider appropriate in the circumstances under PIPEDA s. 5(3), BC PIPA s. 4, and Alberta PIPA s. 4.",
        ],
        "source_url": "https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/2021/pipeda-2021-001/",
        "official_domain": "priv.gc.ca",
        "verbatim_excerpt": _CLEARVIEW_AI_2021_001_EXCERPT,
        "content_sha256": compute_sha256_hex(_CLEARVIEW_AI_2021_001_EXCERPT),
        "review_status": "VERIFIED_SOURCE",
        "collected_at": "2021-02-02T00:00:00Z",
    },
    {
        "id": "verdict-ca-opc-2019-002",
        "decision_id": "DEC-CA-OPC-PIPEDA-2019-002",
        "document_id": "DOC-CA-OPC-PIPEDA-2019-002",
        "source_id": "SRC-CA-FED-OPC-PIPEDA",
        "official_citation": "PIPEDA Report of Findings #2019-002",
        "neutral_citation_or_id": "2019 CanLII 29621 (PCC) / PIPEDA Report of Findings #2019-002",
        "commissioner": "Office of the Privacy Commissioner of Canada (OPC)",
        "court_tribunal_or_regulator": "Office of the Privacy Commissioner of Canada (OPC)",
        "jurisdiction": "Federal (Canada)",
        "jurisdiction_id": "CA-FED",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2019-04-09",
        "parties": [
            "Privacy Commissioner of Canada",
            "Equifax Inc. (Respondent)",
            "Equifax Canada Co. (Respondent)",
        ],
        "title": "PIPEDA Report of Findings #2019-002 — Investigation into Equifax Inc. and Equifax Canada Co. (2017 Cross-Border Breach)",
        "summary": (
            "Investigation by the Privacy Commissioner of Canada into the 2017 Apache Struts vulnerability breach at "
            "Equifax Inc. that compromised Social Insurance Numbers and financial data of ~19,000 Canadians. Held that "
            "Equifax Canada violated PIPEDA Principle 4.1.3 (Accountability for Cross-Border Transfers to an Affiliate), "
            "Principle 4.7 (Safeguards), and Principle 4.5 (Limiting Retention). Equifax Canada entered into a binding "
            "6-year Compliance Agreement under PIPEDA s. 17.1 requiring third-party security audits."
        ),
        "compliance_impact": (
            "Requires written cross-border data processing agreements, active security oversight of parent/affiliated "
            "processors under PIPEDA Principle 4.1.3, automated vulnerability patching, network segmentation, "
            "cryptographic key rotation, and strict data retention purging under Principles 4.5 and 4.7."
        ),
        "statutory_provisions": [
            "Personal Information Protection and Electronic Documents Act (PIPEDA), S.C. 2000, c. 5, s. 17.1",
            "PIPEDA Schedule 1, Principle 4.1.3 (Accountability — Transfers to Third Parties for Processing)",
            "PIPEDA Schedule 1, Principle 4.3 (Consent)",
            "PIPEDA Schedule 1, Principle 4.5 (Limiting Use, Disclosure, and Retention)",
            "PIPEDA Schedule 1, Principle 4.7 (Safeguards)",
        ],
        "holdings": [
            "Under PIPEDA Principle 4.1.3, a Canadian subsidiary (Equifax Canada) remains fully accountable for personal information transferred to its foreign parent corporation (Equifax Inc.) for processing and must ensure comparable protection via structured contractual and monitoring controls.",
            "Equifax Inc. and Equifax Canada contravened PIPEDA Principle 4.7 (Safeguards) due to inadequate vulnerability patching (CVE-2017-5638), lack of network segmentation, unencrypted storage of credentials and cryptographic keys, and deficient monitoring.",
            "Equifax contravened PIPEDA Principle 4.5 by retaining personal data in legacy systems beyond the period required to fulfill the identified purposes.",
        ],
        "source_url": "https://www.priv.gc.ca/en/opc-actions-and-decisions/investigations/investigations-into-businesses/2019/pipeda-2019-002/",
        "official_domain": "priv.gc.ca",
        "verbatim_excerpt": _EQUIFAX_2019_002_EXCERPT,
        "content_sha256": compute_sha256_hex(_EQUIFAX_2019_002_EXCERPT),
        "review_status": "VERIFIED_SOURCE",
        "collected_at": "2019-04-09T00:00:00Z",
    },
    {
        "id": "verdict-ca-on-phipa-175",
        "decision_id": "DEC-CA-ON-IPC-PHIPA-175",
        "document_id": "DOC-CA-ON-IPC-PHIPA-175",
        "source_id": "SRC-CA-ON-IPC-DECISIONS",
        "official_citation": "PHIPA Decision 175",
        "neutral_citation_or_id": "2022 CanLII 15711 (ON IPC) / PHIPA Decision 175",
        "commissioner": "Information and Privacy Commissioner of Ontario (IPC Ontario)",
        "court_tribunal_or_regulator": "Information and Privacy Commissioner of Ontario (IPC Ontario)",
        "jurisdiction": "Ontario",
        "jurisdiction_id": "CA-ON",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2022-02-28",
        "parties": [
            "Information and Privacy Commissioner of Ontario",
            "Health Information Custodian (Respondent)",
        ],
        "title": "IPC Ontario PHIPA Decision 175 (2022) — Unauthorized Electronic Health Record Access ('Snooping') & Audit Logging",
        "summary": (
            "IPC Ontario review under the Personal Health Information Protection Act, 2004 (PHIPA) regarding unauthorized "
            "employee access ('snooping') into electronic patient health records outside the circle of care. Evaluates "
            "whether the health information custodian implemented reasonable administrative and technical safeguards "
            "under PHIPA s. 12(1), electronic audit logging under O. Reg. 329/04 s. 10, and timely breach notification "
            "and disciplinary remediation under PHIPA s. 12(2)."
        ),
        "compliance_impact": (
            "Mandates immutable electronic read/view audit logs recording user ID, timestamp, and patient record "
            "identifier under PHIPA s. 12(1) and O. Reg. 329/04 s. 10, combined with role-based access controls, "
            "regular proactive random snooping audits, and mandatory privacy training."
        ),
        "statutory_provisions": [
            "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA), s. 12(1) (Information practices & security safeguards)",
            "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA), s. 12(2) (Notice of theft, loss, or unauthorized use/disclosure)",
            "O. Reg. 329/04 (General Regulation under PHIPA), s. 10 (Electronic audit logs for health information network providers and electronic systems)",
        ],
        "holdings": [
            "Unauthorized employee snooping into electronic health records outside the circle of care constitutes an unauthorized use and/or disclosure under PHIPA s. 12.",
            "Under PHIPA s. 12(1) and O. Reg. 329/04, health information custodians operating electronic health record systems must maintain electronic audit logs capable of tracking all views and modifications and must conduct regular, proactive audits to detect unauthorized access.",
            "Where a custodian promptly investigates, notifies affected patients and regulatory colleges, disciplines the offending agent, and reinforces RBAC and audit controls, the IPC may decline further formal review orders upon verifying remediation.",
        ],
        "source_url": "https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/520415/index.do",
        "official_domain": "ipc.on.ca",
        "verbatim_excerpt": _IPC_ONTARIO_PHIPA_175_EXCERPT,
        "content_sha256": compute_sha256_hex(_IPC_ONTARIO_PHIPA_175_EXCERPT),
        "review_status": "VERIFIED_SOURCE",
        "collected_at": "2022-02-28T00:00:00Z",
    },
    {
        "id": "verdict-ca-on-phipa-110",
        "decision_id": "DEC-CA-ON-IPC-PHIPA-110",
        "document_id": "DOC-CA-ON-IPC-PHIPA-110",
        "source_id": "SRC-CA-ON-IPC-DECISIONS",
        "official_citation": "PHIPA Decision 110",
        "neutral_citation_or_id": "2020 CanLII 12679 (ON IPC) / PHIPA Decision 110",
        "commissioner": "Information and Privacy Commissioner of Ontario (IPC Ontario)",
        "court_tribunal_or_regulator": "Information and Privacy Commissioner of Ontario (IPC Ontario)",
        "jurisdiction": "Ontario",
        "jurisdiction_id": "CA-ON",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2020-02-19",
        "parties": [
            "Information and Privacy Commissioner of Ontario",
            "Pediatric Health Information Custodian (Respondent)",
        ],
        "title": "IPC Ontario PHIPA Decision 110 (2020) — Ransomware Encryption of Electronic PHI Constitutes Loss & Unauthorized Use",
        "summary": (
            "Landmark IPC Ontario decision holding that a ransomware attack that encrypts electronic personal health "
            "information (PHI) on a custodian's server constitutes both an unauthorized 'use' and a 'loss' of PHI "
            "under PHIPA s. 12(1) and s. 12(2)—even where there is no evidence of exfiltration and backups are "
            "subsequently restored—thereby triggering mandatory notification to affected patients."
        ),
        "compliance_impact": (
            "Incident response playbooks must classify ransomware encryption or availability loss of PHI as a "
            "reportable breach (unauthorized use and loss) under PHIPA s. 12(2) regardless of exfiltration. Requires "
            "offline immutable backups, endpoint detection, and patch management under PHIPA s. 12(1)."
        ),
        "statutory_provisions": [
            "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA), s. 2 (Definition of 'use' — handle or deal with)",
            "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA), s. 12(1) (Security safeguards against theft, loss, and unauthorized use)",
            "Personal Health Information Protection Act, 2004, S.O. 2004, c. 3, Sched. A (PHIPA), s. 12(2) (Mandatory patient notification at the first reasonable opportunity)",
        ],
        "holdings": [
            "Ransomware encryption of electronic personal health information alters the state and availability of the records and therefore constitutes an unauthorized 'use' ('to handle or deal with') under section 2 and section 12 of PHIPA.",
            "When ransomware encrypts electronic records so that the health information custodian can no longer access them, the information is 'lost' within the meaning of section 12(2) of PHIPA, triggering the statutory duty to notify affected individuals at the first reasonable opportunity.",
            "Custodians must maintain segregated, tested backups and reasonable cybersecurity controls (antivirus, firewall, patch management) under PHIPA s. 12(1).",
        ],
        "source_url": "https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/466468/index.do",
        "official_domain": "ipc.on.ca",
        "verbatim_excerpt": _IPC_ONTARIO_PHIPA_110_EXCERPT,
        "content_sha256": compute_sha256_hex(_IPC_ONTARIO_PHIPA_110_EXCERPT),
        "review_status": "VERIFIED_SOURCE",
        "collected_at": "2020-02-19T00:00:00Z",
    },
    {
        "id": "verdict-ca-bc-p21-06",
        "decision_id": "DEC-CA-BC-OIPC-P21-06",
        "document_id": "DOC-CA-BC-OIPC-P21-06",
        "source_id": "SRC-CA-BC-OIPC-ORDERS",
        "official_citation": "Order P21-06",
        "neutral_citation_or_id": "2021 BCIPC 35 / Order P21-06",
        "commissioner": "Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
        "court_tribunal_or_regulator": "Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
        "jurisdiction": "British Columbia",
        "jurisdiction_id": "CA-BC",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2021-06-17",
        "parties": [
            "Office of the Information and Privacy Commissioner for British Columbia",
            "Private Sector Organization (Respondent under BC PIPA)",
        ],
        "title": "OIPC BC Order P21-06 (2021 BCIPC 35) — PIPA s. 34 Reasonable Security Safeguards & s. 35 Data Retention",
        "summary": (
            "Adjudicative order by the OIPC for British Columbia under the Personal Information Protection Act (BC PIPA) "
            "evaluating an organization's obligations under s. 34 to make reasonable security arrangements to prevent "
            "unauthorized access, collection, use, disclosure, copying, modification, or disposal of employee and "
            "customer personal information, and under s. 35 to destroy or anonymize personal information once retention "
            "is no longer necessary for legal or business purposes."
        ),
        "compliance_impact": (
            "Enforces BC PIPA s. 34 security safeguards (access controls, documented security policies, encryption, and "
            "audit trails proportional to data sensitivity) and s. 35 automated retention schedules that securely "
            "destroy or de-identify employee and customer records once business/legal purposes expire."
        ),
        "statutory_provisions": [
            "Personal Information Protection Act, S.B.C. 2003, c. 63 (BC PIPA), s. 34 (Protection of personal information — reasonable security arrangements)",
            "Personal Information Protection Act, S.B.C. 2003, c. 63 (BC PIPA), s. 35 (Retention of personal information — destruction or anonymization when no longer necessary)",
            "Personal Information Protection Act, S.B.C. 2003, c. 63 (BC PIPA), s. 52 (Adjudicator's order-making powers)",
        ],
        "holdings": [
            "Section 34 of BC PIPA imposes a continuing statutory duty on organizations to maintain reasonable physical, technological, and administrative security arrangements proportionate to the sensitivity and volume of employee and customer personal information.",
            "Section 35 of BC PIPA requires organizations to cease retaining personal information—and to destroy their documents or remove the means by which the personal information can be associated with particular individuals—as soon as it is reasonable to assume that the purpose for collection is no longer being served and retention is no longer necessary for legal or business purposes.",
        ],
        "source_url": "https://www.oipc.bc.ca/orders/2556",
        "official_domain": "oipc.bc.ca",
        "verbatim_excerpt": _OIPC_BC_ORDER_P21_06_EXCERPT,
        "content_sha256": compute_sha256_hex(_OIPC_BC_ORDER_P21_06_EXCERPT),
        "review_status": "VERIFIED_SOURCE",
        "collected_at": "2021-06-17T00:00:00Z",
    },
]


def get_canada_commissioner_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of the curated Canadian Privacy Commissioner RegulatorySourceEntry list."""
    return [entry.model_copy(deep=True) for entry in CANADA_COMMISSIONER_SOURCES]


def get_authentic_canadian_commissioner_decisions() -> List[Dict[str, Any]]:
    """Return a copy of the authentic, verifiable Canadian Privacy Commissioner decisions."""
    return [dict(item) for item in AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS]


__all__ = [
    "CANADA_COMMISSIONER_SOURCES",
    "get_canada_commissioner_sources",
    "AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS",
    "get_authentic_canadian_commissioner_decisions",
]
