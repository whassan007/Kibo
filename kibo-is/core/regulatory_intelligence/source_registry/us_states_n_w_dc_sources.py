"""
US State Legislation and Administrative Rules (States N-W, Washington DC, and US Territories).

Covers authoritative legislative, administrative code, attorney general, and sector-specific
regulatory sources across all 24 US states from Nebraska (US-NE) through Wyoming (US-WY),
plus the District of Columbia (US-DC) and US Territories (US-PR, US-GU, US-VI):
- US-NE (Nebraska): Nebraska Data Privacy Act (NDPA, LB 1074) & Nebraska Unicameral Legislature
- US-NV (Nevada): NRS Chapter 603A (SB 220 / SB 260 / SB 370 Consumer Health Data)
- US-NH (New Hampshire): New Hampshire Privacy Act (NHPA, SB 255, RSA 507-H)
- US-NJ (New Jersey): New Jersey Data Privacy Act (NJDPA, S332) & Division of Consumer Affairs
- US-NM (New Mexico): New Mexico Consumer Information Privacy & Data Breach Notification Act
- US-NY (New York): NY SHIELD Act (GBL § 899-aa/bb) & NYDFS 23 NYCRR Part 500 Cybersecurity Regulation
- US-NC (North Carolina): NC Identity Theft Protection Act (N.C. Gen. Stat. § 75-60 et seq.)
- US-ND (North Dakota): North Dakota Century Code Ch. 51-30 & Financial Data Protection
- US-OH (Ohio): Ohio Data Protection Act (ORC § 1354.01 et seq.) & Personal Privacy Act
- US-OK (Oklahoma): Oklahoma Security Breach Notification Act (24 O.S. § 161 et seq.)
- US-OR (Oregon): Oregon Consumer Privacy Act (OCPA, ORS 646A.570 et seq., SB 619)
- US-PA (Pennsylvania): Breach of Personal Information Notification Act (73 P.S. § 2301 et seq.)
- US-RI (Rhode Island): Rhode Island Data Transparency and Privacy Protection Act (RIDTPPA, S2500 / H7787)
- US-SC (South Carolina): South Carolina Insurance Data Security Act & Financial Identity Fraud Act
- US-SD (South Dakota): South Dakota Codified Laws Ch. 22-40 (Breach Notification & Consumer Protection)
- US-TN (Tennessee): Tennessee Information Protection Act (TIPA, T.C.A. § 47-18-3201 et seq.)
- US-TX (Texas): Texas Data Privacy and Security Act (TDPSA, Bus. & Com. Code Ch. 541) & CUBI (Ch. 503)
- US-UT (Utah): Utah Consumer Privacy Act (UCPA, Utah Code § 13-61-101 et seq.)
- US-VT (Vermont): Vermont Data Broker Regulation (9 V.S.A. § 2430 et seq.) & Age-Appropriate Design
- US-VA (Virginia): Virginia Consumer Data Protection Act (VCDPA, Va. Code § 59.1-575 et seq.)
- US-WA (Washington): Washington My Health My Data Act (WMHMDA, RCW 19.373) & Biometric Identifiers (RCW 19.375)
- US-WV (West Virginia): West Virginia Consumer Credit and Protection Act (W. Va. Code § 46A-2A-101 et seq.)
- US-WI (Wisconsin): Wisconsin Data Privacy & Notice of Unauthorized Acquisition (Wis. Stat. § 134.98)
- US-WY (Wyoming): Wyoming Consumer Protection & Data Breach Statutes (Wyo. Stat. § 40-12-501 et seq.)
- US-DC (District of Columbia): DC Consumer Protection Procedures Act & Security Breach Protection Amendment Act
- US-PR (Puerto Rico): Citizen Information on Data Banks Security Act (Law No. 111-2005, 10 L.P.R.A. § 4051)
- US-GU (Guam): Guam Notification of Breaches of Personal Information Act (9 GCA § 48-10 et seq.)
- US-VI (U.S. Virgin Islands): USVI Data Breach Notification Law (14 V.I.C. § 2208 et seq.)
"""

from __future__ import annotations

from typing import List

from core.regulatory_intelligence import RegulatorySourceEntry, SourceHealthStatus


US_STATES_N_W_DC_SOURCES: List[RegulatorySourceEntry] = [
    # -------------------------------------------------------------------------
    # Nebraska (US-NE)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NE-LEGISLATURE-NDPA",
        jurisdiction_id="US-NE",
        parent_jurisdiction="US-FED",
        authority_name="Nebraska Unicameral Legislature",
        authority_type="legislature",
        official_domain="nebraskalegislature.gov",
        discovery_endpoint="https://nebraskalegislature.gov/laws/browse-chapters.php?chapter=87",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Nebraska Public Domain — Nebraska Revised Statutes Ch. 87 (NDPA LB 1074)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "consumer_protection", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-NE-AG-CONSUMER",
        jurisdiction_id="US-NE",
        parent_jurisdiction="US-FED",
        authority_name="Nebraska Attorney General — Consumer Protection Division",
        authority_type="attorney_general",
        official_domain="ago.nebraska.gov",
        discovery_endpoint="https://ago.nebraska.gov/consumer-protection",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Nebraska Public Domain — Official AG Enforcement & Guidance",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Nevada (US-NV)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NV-LEGISLATURE-NRS603A",
        jurisdiction_id="US-NV",
        parent_jurisdiction="US-FED",
        authority_name="Nevada Legislature — Legislative Counsel Bureau",
        authority_type="legislature",
        official_domain="leg.state.nv.us",
        discovery_endpoint="https://www.leg.state.nv.us/NRS/NRS-603A.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Nevada Public Domain — NRS Chapter 603A & SB 370 Health Data Privacy",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "health_data", "data_brokers", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # New Hampshire (US-NH)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NH-GENCOURT-NHPA",
        jurisdiction_id="US-NH",
        parent_jurisdiction="US-FED",
        authority_name="New Hampshire General Court",
        authority_type="legislature",
        official_domain="gencourt.state.nh.us",
        discovery_endpoint="https://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-LII-507-H.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New Hampshire Public Domain — RSA 507-H (New Hampshire Privacy Act, SB 255) & RSA 359-C",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "consumer_rights", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-NH-DOJ-PRIVACY",
        jurisdiction_id="US-NH",
        parent_jurisdiction="US-FED",
        authority_name="New Hampshire Department of Justice — Office of the Attorney General Data Privacy Unit",
        authority_type="attorney_general",
        official_domain="doj.nh.gov",
        discovery_endpoint="https://www.doj.nh.gov/citizens/consumer-protection-antitrust-bureau/data-privacy",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New Hampshire Public Domain — Official AG Guidance",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # New Jersey (US-NJ)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NJ-LEGISLATURE-NJDPA",
        jurisdiction_id="US-NJ",
        parent_jurisdiction="US-FED",
        authority_name="New Jersey Legislature — Office of Legislative Services",
        authority_type="legislature",
        official_domain="njleg.state.nj.us",
        discovery_endpoint="https://pub.njleg.state.nj.us/Bills/2022/S0500/332_R6.HTM",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New Jersey Public Domain — New Jersey Data Privacy Act (S332 / P.L. 2023, c.266, N.J.S.A. 56:8-166.4 et seq.)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "universal_opt_out", "data_protection_assessments"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-NJ-DCA-RULES",
        jurisdiction_id="US-NJ",
        parent_jurisdiction="US-FED",
        authority_name="New Jersey Division of Consumer Affairs — Office of the Attorney General",
        authority_type="attorney_general",
        official_domain="njconsumeraffairs.gov",
        discovery_endpoint="https://www.njconsumeraffairs.gov/Statutes-and-Rules",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New Jersey Public Domain — NJDPA Implementing Rules & Enforcement",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "rulemaking", "enforcement"],
        legal_instrument_types=["regulation", "official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # New Mexico (US-NM)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NM-LEGISLATURE-NMSA",
        jurisdiction_id="US-NM",
        parent_jurisdiction="US-FED",
        authority_name="New Mexico Legislature",
        authority_type="legislature",
        official_domain="nmlegis.gov",
        discovery_endpoint="https://www.nmlegis.gov/Legislation/Legislation_List",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New Mexico Public Domain — NMSA 1978 Chapter 57, Article 12C (Data Breach Notification Act)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "data_security"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # New York (US-NY)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NY-SENATE-SHIELD",
        jurisdiction_id="US-NY",
        parent_jurisdiction="US-FED",
        authority_name="New York State Senate — Open Legislation API",
        authority_type="legislature",
        official_domain="nysenate.gov",
        discovery_endpoint="https://legislation.nysenate.gov/api/3/laws/GBS/A39-F",
        feed_format="api_json",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New York Public Domain — NY General Business Law Art. 39-F (SHIELD Act §§ 899-aa, 899-bb) & NY Child Data Protection Act",
        rate_limit_rpm=60,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "cybersecurity", "breach_notification", "children_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-NY-NYDFS-23NYCRR500",
        jurisdiction_id="US-NY",
        parent_jurisdiction="US-FED",
        authority_name="New York State Department of Financial Services (NYDFS)",
        authority_type="sector_regulator",
        official_domain="dfs.ny.gov",
        discovery_endpoint="https://www.dfs.ny.gov/industry_guidance/cybersecurity",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of New York Public Domain — 23 NYCRR Part 500 Cybersecurity Requirements for Financial Services Companies & Enforcement Consent Orders",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["cybersecurity", "financial_privacy", "incident_reporting", "governance", "enforcement"],
        legal_instrument_types=["regulation", "official_guidance", "regulatory_enforcement_decision", "consent_order_settlement"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # North Carolina (US-NC)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-NC-GA-GS75",
        jurisdiction_id="US-NC",
        parent_jurisdiction="US-FED",
        authority_name="North Carolina General Assembly",
        authority_type="legislature",
        official_domain="ncleg.gov",
        discovery_endpoint="https://www.ncleg.gov/Laws/GeneralStatuteSections/Chapter75",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of North Carolina Public Domain — N.C. Gen. Stat. Ch. 75 Art. 2A (Identity Theft Protection Act)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "identity_theft", "breach_notification", "data_security"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # North Dakota (US-ND)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-ND-LEGISLATURE-NDCC51",
        jurisdiction_id="US-ND",
        parent_jurisdiction="US-FED",
        authority_name="North Dakota Legislative Branch",
        authority_type="legislature",
        official_domain="ndlegis.gov",
        discovery_endpoint="https://ndlegis.gov/cencode/t51c30.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of North Dakota Public Domain — N.D.C.C. Ch. 51-30 (Notice of Security Breach for Personal Information) & Ch. 26.1-02.2",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "financial_data_security"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Ohio (US-OH)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-OH-LEGISLATURE-ORC1354",
        jurisdiction_id="US-OH",
        parent_jurisdiction="US-FED",
        authority_name="Ohio General Assembly — Legislative Service Commission",
        authority_type="legislature",
        official_domain="codes.ohio.gov",
        discovery_endpoint="https://codes.ohio.gov/ohio-revised-code/chapter-1354",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Ohio Public Domain — ORC Ch. 1354 (Ohio Data Protection Act Safe Harbor) & ORC § 1349.19",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "cybersecurity", "safe_harbor", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Oklahoma (US-OK)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-OK-LEGISLATURE-OS24",
        jurisdiction_id="US-OK",
        parent_jurisdiction="US-FED",
        authority_name="Oklahoma State Legislature",
        authority_type="legislature",
        official_domain="oklegislature.gov",
        discovery_endpoint="https://www.oklegislature.gov/ok_statutes/CompleteTitles/os24.rtf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Oklahoma Public Domain — 24 O.S. § 161 et seq. (Security Breach Notification Act)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "data_security"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Oregon (US-OR)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-OR-LEGISLATURE-OCPA",
        jurisdiction_id="US-OR",
        parent_jurisdiction="US-FED",
        authority_name="Oregon Legislative Assembly",
        authority_type="legislature",
        official_domain="oregonlegislature.gov",
        discovery_endpoint="https://www.oregonlegislature.gov/bills_laws/ors/ors646A.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Oregon Public Domain — ORS 646A.570 to 646A.589 (Oregon Consumer Privacy Act, SB 619) & ORS 646A.600 (Consumer Information Protection Act)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "consumer_rights", "data_brokers", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-OR-DOJ-PRIVACY",
        jurisdiction_id="US-OR",
        parent_jurisdiction="US-FED",
        authority_name="Oregon Department of Justice — Office of the Attorney General Privacy Unit",
        authority_type="attorney_general",
        official_domain="doj.state.or.us",
        discovery_endpoint="https://www.doj.state.or.us/consumer-protection/id-theft-data-breaches/oregon-consumer-privacy-act/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Oregon Public Domain — OCPA Guidance & Enforcement",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Pennsylvania (US-PA)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-PA-GA-BPINA",
        jurisdiction_id="US-PA",
        parent_jurisdiction="US-FED",
        authority_name="Pennsylvania General Assembly",
        authority_type="legislature",
        official_domain="palegis.us",
        discovery_endpoint="https://www.palegis.us/statutes/unconsolidated/law-information?sessYr=2005&sessInd=0&actNum=94",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commonwealth of Pennsylvania Public Domain — 73 P.S. § 2301 et seq. (Breach of Personal Information Notification Act, Act 151 / SB 824 Amendments)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "data_security", "credit_monitoring"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Rhode Island (US-RI)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-RI-LEGISLATURE-RIDTPPA",
        jurisdiction_id="US-RI",
        parent_jurisdiction="US-FED",
        authority_name="Rhode Island General Assembly",
        authority_type="legislature",
        official_domain="rilegislature.gov",
        discovery_endpoint="http://webserver.rilegislature.gov/Statutes/TITLE6/6-48.1/INDEX.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Rhode Island Public Domain — R.I. Gen. Laws Ch. 6-48.1 (Rhode Island Data Transparency and Privacy Protection Act, S2500/H7787) & Ch. 11-49.3",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "third_party_disclosure", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # South Carolina (US-SC)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-SC-STATEHOUSE-TITLE39",
        jurisdiction_id="US-SC",
        parent_jurisdiction="US-FED",
        authority_name="South Carolina General Assembly",
        authority_type="legislature",
        official_domain="scstatehouse.gov",
        discovery_endpoint="https://www.scstatehouse.gov/code/t39c001.php",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of South Carolina Public Domain — S.C. Code Ann. § 39-1-90 (Breach Notification) & Title 38 Ch. 99 (Insurance Data Security Act)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "cybersecurity", "insurance_data_security", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # South Dakota (US-SD)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-SD-LEGISLATURE-SDCL22",
        jurisdiction_id="US-SD",
        parent_jurisdiction="US-FED",
        authority_name="South Dakota Legislature — Legislative Research Council",
        authority_type="legislature",
        official_domain="sdlegislature.gov",
        discovery_endpoint="https://sdlegislature.gov/Statutes/22-40",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of South Dakota Public Domain — SDCL Ch. 22-40 (Identity Crimes & Breach of System Security Notification §§ 22-40-19 to 22-40-26)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "identity_theft"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Tennessee (US-TN)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-TN-CAPITOL-TIPA",
        jurisdiction_id="US-TN",
        parent_jurisdiction="US-FED",
        authority_name="Tennessee General Assembly",
        authority_type="legislature",
        official_domain="capitol.tn.gov",
        discovery_endpoint="https://wapp.capitol.tn.gov/apps/BillInfo/Default.aspx?BillNumber=HB1181&GA=113",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Tennessee Public Domain — Tennessee Information Protection Act (TIPA, T.C.A. § 47-18-3201 et seq., Public Chapter 408) & T.C.A. § 47-18-2107",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "nist_privacy_framework_safe_harbor", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-TN-AG-PRIVACY",
        jurisdiction_id="US-TN",
        parent_jurisdiction="US-FED",
        authority_name="Tennessee Attorney General and Reporter — Division of Consumer Affairs",
        authority_type="attorney_general",
        official_domain="tn.gov",
        discovery_endpoint="https://www.tn.gov/attorneygeneral/working-for-tennessee/consumer-affairs.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Tennessee Public Domain — TIPA Enforcement & Guidance",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Texas (US-TX)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-TX-STATUTES-TDPSA",
        jurisdiction_id="US-TX",
        parent_jurisdiction="US-FED",
        authority_name="Texas Legislature — Texas Legislative Council",
        authority_type="legislature",
        official_domain="statutes.capitol.texas.gov",
        discovery_endpoint="https://statutes.capitol.texas.gov/Docs/BC/htm/BC.541.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Texas Public Domain — Tex. Bus. & Com. Code Ch. 541 (Texas Data Privacy and Security Act, TDPSA, HB 4)",
        rate_limit_rpm=40,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "universal_opt_out", "sensitive_data", "data_protection_assessments"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-TX-STATUTES-CUBI",
        jurisdiction_id="US-TX",
        parent_jurisdiction="US-FED",
        authority_name="Texas Legislature — Texas Legislative Council",
        authority_type="legislature",
        official_domain="statutes.capitol.texas.gov",
        discovery_endpoint="https://statutes.capitol.texas.gov/Docs/BC/htm/BC.503.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Texas Public Domain — Tex. Bus. & Com. Code Ch. 503 (Capture or Use of Biometric Identifier Act, CUBI) & Ch. 521 (Identity Theft Enforcement and Protection Act)",
        rate_limit_rpm=40,
        update_frequency="daily",
        publication_coverage=["biometric_privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-TX-OAG-PRIVACY",
        jurisdiction_id="US-TX",
        parent_jurisdiction="US-FED",
        authority_name="Office of the Texas Attorney General — Data Privacy and Security Enforcement Team",
        authority_type="attorney_general",
        official_domain="texasattorneygeneral.gov",
        discovery_endpoint="https://www.texasattorneygeneral.gov/consumer-protection/file-consumer-complaint/consumer-privacy-rights/texas-data-privacy-and-security-act",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Texas Public Domain — OAG TDPSA & CUBI Enforcement Actions and Guidance",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "biometric_privacy", "data_brokers", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "consent_order_settlement"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Utah (US-UT)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-UT-LEGISLATURE-UCPA",
        jurisdiction_id="US-UT",
        parent_jurisdiction="US-FED",
        authority_name="Utah State Legislature",
        authority_type="legislature",
        official_domain="le.utah.gov",
        discovery_endpoint="https://le.utah.gov/xcode/Title13/Chapter61/13-61.html",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Utah Public Domain — Utah Code Title 13, Ch. 61 (Utah Consumer Privacy Act, UCPA) & Title 13, Ch. 44 (Protection of Personal Information Act)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "consumer_rights", "artificial_intelligence", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-UT-DCP-ODPP",
        jurisdiction_id="US-UT",
        parent_jurisdiction="US-FED",
        authority_name="Utah Department of Commerce — Office of Data Privacy & Division of Consumer Protection",
        authority_type="data_protection_authority",
        official_domain="dcp.utah.gov",
        discovery_endpoint="https://dcp.utah.gov/ucpa/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Utah Public Domain — UCPA Guidance & AI Policy Reports",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "artificial_intelligence", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Vermont (US-VT)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-VT-LEGISLATURE-TITLE9",
        jurisdiction_id="US-VT",
        parent_jurisdiction="US-FED",
        authority_name="Vermont General Assembly",
        authority_type="legislature",
        official_domain="legislature.vermont.gov",
        discovery_endpoint="https://legislature.vermont.gov/statutes/chapter/09/062",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Vermont Public Domain — 9 V.S.A. Ch. 62 (Protection of Personal Information & Data Broker Regulation §§ 2430-2447)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_brokers", "breach_notification", "data_security"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Virginia (US-VA)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-VA-LIS-VCDPA",
        jurisdiction_id="US-VA",
        parent_jurisdiction="US-FED",
        authority_name="Virginia General Assembly — Legislative Information System (LIS)",
        authority_type="legislature",
        official_domain="law.lis.virginia.gov",
        discovery_endpoint="https://law.lis.virginia.gov/vacodepopularnames/consumer-data-protection-act/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commonwealth of Virginia Public Domain — Va. Code Title 59.1, Ch. 53 (§§ 59.1-575 to 59.1-585, Virginia Consumer Data Protection Act, VCDPA) & § 18.2-186.6",
        rate_limit_rpm=40,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "children_privacy", "data_protection_assessments", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-VA-OAG-VCDPA",
        jurisdiction_id="US-VA",
        parent_jurisdiction="US-FED",
        authority_name="Office of the Attorney General of Virginia — Consumer Protection Section",
        authority_type="attorney_general",
        official_domain="oag.state.va.us",
        discovery_endpoint="https://www.oag.state.va.us/consumer-protection/index.php/virginia-consumer-data-protection-act",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commonwealth of Virginia Public Domain — VCDPA Enforcement & Official Guidance",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Washington (US-WA)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-WA-LEGISLATURE-MHMDA",
        jurisdiction_id="US-WA",
        parent_jurisdiction="US-FED",
        authority_name="Washington State Legislature — Statute Law Committee",
        authority_type="legislature",
        official_domain="app.leg.wa.gov",
        discovery_endpoint="https://app.leg.wa.gov/RCW/default.aspx?cite=19.373",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Washington Public Domain — RCW 19.373 (Washington My Health My Data Act, HB 1155), RCW 19.375 (Biometric Identifiers), & RCW 19.255",
        rate_limit_rpm=40,
        update_frequency="daily",
        publication_coverage=["health_data_privacy", "biometric_privacy", "geofencing", "consumer_consent", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-WA-ATG-MHMDA",
        jurisdiction_id="US-WA",
        parent_jurisdiction="US-FED",
        authority_name="Washington State Office of the Attorney General",
        authority_type="attorney_general",
        official_domain="atg.wa.gov",
        discovery_endpoint="https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Washington Public Domain — My Health My Data Act Guidance & Data Breach Reports",
        rate_limit_rpm=25,
        update_frequency="weekly",
        publication_coverage=["health_data_privacy", "privacy", "breach_notification", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # West Virginia (US-WV)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-WV-LEGISLATURE-WVCODE46A",
        jurisdiction_id="US-WV",
        parent_jurisdiction="US-FED",
        authority_name="West Virginia Legislature",
        authority_type="legislature",
        official_domain="wvlegislature.gov",
        discovery_endpoint="https://code.wvlegislature.gov/46A-2A/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of West Virginia Public Domain — W. Va. Code Ch. 46A, Art. 2A (Breach of Security of Consumer Information)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "consumer_protection"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Wisconsin (US-WI)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-WI-LEGISLATURE-STAT134",
        jurisdiction_id="US-WI",
        parent_jurisdiction="US-FED",
        authority_name="Wisconsin State Legislature — Legislative Reference Bureau",
        authority_type="legislature",
        official_domain="docs.legis.wisconsin.gov",
        discovery_endpoint="https://docs.legis.wisconsin.gov/statutes/statutes/134/98",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Wisconsin Public Domain — Wis. Stat. § 134.98 (Notice of Unauthorized Acquisition of Personal Information) & § 995.50 (Right of Privacy)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "data_protection"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Wyoming (US-WY)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-WY-LEGISLATURE-TITLE40",
        jurisdiction_id="US-WY",
        parent_jurisdiction="US-FED",
        authority_name="Wyoming Legislature — Legislative Service Office",
        authority_type="legislature",
        official_domain="wyoleg.gov",
        discovery_endpoint="https://wyoleg.gov/statutes/compress/title40.pdf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="State of Wyoming Public Domain — Wyo. Stat. §§ 40-12-501 to 40-12-509 (Personal Identifying Information & Security Breach Notification)",
        rate_limit_rpm=25,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "digital_assets_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # District of Columbia (US-DC)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-DC-COUNCIL-CODE28",
        jurisdiction_id="US-DC",
        parent_jurisdiction="US-FED",
        authority_name="Council of the District of Columbia",
        authority_type="legislature",
        official_domain="code.dccouncil.gov",
        discovery_endpoint="https://code.dccouncil.gov/us/dc/council/code/titles/28/chapters/38/subchapters/II",
        feed_format="xml_akoma_ntoso",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="District of Columbia CC0 / Public Domain — D.C. Official Code Title 28, Ch. 38, Subch. II (Consumer Security Breach Notification §§ 28-3851 et seq.) & Stop Discrimination by Algorithms",
        rate_limit_rpm=40,
        update_frequency="daily",
        publication_coverage=["privacy", "breach_notification", "consumer_protection", "algorithmic_accountability"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-DC-OAG-PRIVACY",
        jurisdiction_id="US-DC",
        parent_jurisdiction="US-FED",
        authority_name="Office of the Attorney General for the District of Columbia",
        authority_type="attorney_general",
        official_domain="oag.dc.gov",
        discovery_endpoint="https://oag.dc.gov/consumer-protection/security-breaches",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="District of Columbia Public Domain — DC OAG Privacy Enforcement & Consent Orders",
        rate_limit_rpm=25,
        update_frequency="weekly",
        publication_coverage=["privacy", "data_protection", "enforcement"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "consent_order_settlement"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Puerto Rico (US-PR)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-PR-OGP-LAW111",
        jurisdiction_id="US-PR",
        parent_jurisdiction="US-FED",
        authority_name="Oficina de Gerencia y Presupuesto de Puerto Rico (Biblioteca Virtual OGP) & DACO",
        authority_type="legislature",
        official_domain="bvirtualogp.pr.gov",
        discovery_endpoint="https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/Protecci%C3%B3n%20al%20Consumidor/111-2005/111-2005.pdf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Commonwealth of Puerto Rico Public Domain — Act No. 111-2005 (Citizen Information on Data Banks Security Act, 10 L.P.R.A. § 4051 et seq.) & Act No. 39-2012",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "breach_notification", "consumer_protection"],
        legal_instrument_types=["statute", "regulation"],
        source_priority=1,
        languages=["es", "en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # Guam (US-GU)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-GU-COMPILERS-9GCA48",
        jurisdiction_id="US-GU",
        parent_jurisdiction="US-FED",
        authority_name="Office of the Compiler of Laws of Guam — Guam Legislature",
        authority_type="legislature",
        official_domain="guamcourts.org",
        discovery_endpoint="https://www.guamcourts.org/CompilerofLaws/GCA/09gca/9gc048.pdf",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Territory of Guam Public Domain — 9 GCA Ch. 48 (Notification of Breaches of Personal Information §§ 48-10 to 48-80)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "breach_notification"],
        legal_instrument_types=["statute"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),

    # -------------------------------------------------------------------------
    # U.S. Virgin Islands (US-VI)
    # -------------------------------------------------------------------------
    RegulatorySourceEntry(
        source_id="SRC-US-VI-LEGISLATURE-14VIC2208",
        jurisdiction_id="US-VI",
        parent_jurisdiction="US-FED",
        authority_name="Legislature of the Virgin Islands & Lieutenant Governor Consumer Affairs Division",
        authority_type="legislature",
        official_domain="legvi.org",
        discovery_endpoint="https://www.legvi.org/billtracking/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Territory of the U.S. Virgin Islands Public Domain — 14 V.I.C. § 2208 et seq. & 11 V.I.C. § 1001 (Disclosure of Breach of Security)",
        rate_limit_rpm=20,
        update_frequency="weekly",
        publication_coverage=["privacy", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
        source_priority=1,
        languages=["en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
]


def get_us_states_n_w_dc_sources() -> List[RegulatorySourceEntry]:
    """Return all authoritative regulatory sources for US states N-W, Washington DC, and US territories."""
    return list(US_STATES_N_W_DC_SOURCES)
