"""
KIBO Privacy OS — US State Legislation and Administrative Rules Source Registry (States A–M)
Covers all 26 US states alphabetically from Alabama (US-AL) through Montana (US-MT):
US-AL, US-AK, US-AZ, US-AR, US-CA, US-CO, US-CT, US-DE, US-FL, US-GA, US-HI, US-ID,
US-IL, US-IN, US-IA, US-KS, US-KY, US-LA, US-ME, US-MD, US-MA, US-MI, US-MN, US-MS,
US-MO, US-MT.

Also exports AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES containing real statutory text
for California CCPA/CPRA (Cal. Civ. Code § 1798.100 & § 1798.185(a)(15)-(16)) and
Colorado CPA / AI Act (C.R.S. § 6-1-1306 & § 6-1-1703) for provision-level diff testing (RD-03).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    ProvisionDiffRecord,
    RegulatorySourceEntry,
    SourceHealthStatus,
    compute_sha256_hex,
)

# Canonical list of the 26 US state jurisdiction codes (Alabama through Montana)
US_STATES_A_M_JURISDICTIONS: List[str] = [
    "US-AL",
    "US-AK",
    "US-AZ",
    "US-AR",
    "US-CA",
    "US-CO",
    "US-CT",
    "US-DE",
    "US-FL",
    "US-GA",
    "US-HI",
    "US-ID",
    "US-IL",
    "US-IN",
    "US-IA",
    "US-KS",
    "US-KY",
    "US-LA",
    "US-ME",
    "US-MD",
    "US-MA",
    "US-MI",
    "US-MN",
    "US-MS",
    "US-MO",
    "US-MT",
]

_DEFAULT_LICENSE = "US State Government Public Record / Statutory Publication — Public Domain / Attribution Required"


def _src(
    source_id: str,
    jurisdiction_id: str,
    authority_name: str,
    authority_type: str,
    official_domain: str,
    discovery_endpoint: str,
    feed_format: str = "html_structured",
    *,
    rate_limit_rpm: int = 30,
    update_frequency: str = "daily",
    publication_coverage: List[str] | None = None,
    legal_instrument_types: List[str] | None = None,
    source_priority: int = 1,
) -> RegulatorySourceEntry:
    return RegulatorySourceEntry(
        source_id=source_id,
        jurisdiction_id=jurisdiction_id,
        parent_jurisdiction="US-FED",
        authority_name=authority_name,
        authority_type=authority_type,
        official_domain=official_domain,
        discovery_endpoint=discovery_endpoint,
        feed_format=feed_format,
        auth_requirements="public_unauthenticated",
        licensing_and_reuse=_DEFAULT_LICENSE,
        rate_limit_rpm=rate_limit_rpm,
        update_frequency=update_frequency,
        publication_coverage=publication_coverage
        or ["privacy", "data_protection", "cybersecurity", "breach_notification"],
        legal_instrument_types=legal_instrument_types
        or ["statute", "regulation", "legislative_bill", "official_guidance"],
        source_priority=source_priority,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor=f"ckpt-{source_id.lower()}-2026-10-25",
    )


US_STATES_A_M_SOURCES: List[RegulatorySourceEntry] = [
    # -------------------------------------------------------------------------
    # 1. ALABAMA (US-AL) — Ala. Code §§ 8-38-1 to 8-38-12 (Breach Notification Act)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-AL-ALISON-LEG",
        "US-AL",
        "Alabama Legislature (Legislative Services Agency — Code of Alabama)",
        "legislature",
        "alison.legislature.state.al.us",
        "https://alison.legislature.state.al.us/code-of-alabama",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "cybersecurity", "consumer_protection"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-AL-AG-ADMIN",
        "US-AL",
        "Office of the Alabama Attorney General & Alabama Administrative Monthly",
        "attorney_general",
        "alabamaag.gov",
        "https://www.alabamaag.gov/consumer-complaint/",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 2. ALASKA (US-AK) — Alaska Stat. §§ 45.48.010-45.48.090 (PIPA)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-AK-AKLEG",
        "US-AK",
        "Alaska State Legislature — Basis & Alaska Statutes (Title 45 Ch. 48 PIPA)",
        "legislature",
        "akleg.gov",
        "https://www.akleg.gov/basis/statutes.asp#45.48.010",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "credit_monitoring", "identity_theft"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-AK-LAW-ADMIN",
        "US-AK",
        "Alaska Department of Law (Attorney General Consumer Protection Unit)",
        "attorney_general",
        "law.alaska.gov",
        "https://law.alaska.gov/department/civil/consumer/cp_index.html",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 3. ARIZONA (US-AZ) — Ariz. Rev. Stat. §§ 18-551, 18-552; Health Info §§ 36-3801 et seq.
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-AZ-AZLEG",
        "US-AZ",
        "Arizona State Legislature — Arizona Revised Statutes (Title 18 Ch. 5 & Title 36)",
        "legislature",
        "azleg.gov",
        "https://www.azleg.gov/arsDetail/?title=18",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "health_privacy", "cybersecurity"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-AZ-AG-AAR",
        "US-AZ",
        "Arizona Attorney General's Office & Arizona Administrative Register",
        "attorney_general",
        "azag.gov",
        "https://www.azag.gov/consumer/data-breach",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection", "privacy"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 4. ARKANSAS (US-AR) — Ark. Code Ann. §§ 4-110-101 to 4-110-108 (PIPA) & Biometric/Health
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-AR-ARKLEG",
        "US-AR",
        "Arkansas General Assembly — Arkansas Code & Legislative Acts (Title 4 Ch. 110 PIPA)",
        "legislature",
        "arkleg.state.ar.us",
        "https://www.arkleg.state.ar.us/Acts/Search",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "biometric_privacy", "children_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-AR-AG-ADMIN",
        "US-AR",
        "Arkansas Attorney General — Consumer Protection & Administrative Rules",
        "attorney_general",
        "arkansasag.gov",
        "https://arkansasag.gov/consumer-protection/",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 5. CALIFORNIA (US-CA) — CCPA/CPRA, Delete Act, CMIA, ADMT, AI Transparency, Breach
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-CA-LEGINFO",
        "US-CA",
        "California Legislative Information — Civil Code §§ 1798.100–1798.199.100 (CCPA/CPRA), CMIA (§ 56), Delete Act & AI Acts",
        "legislature",
        "leginfo.legislature.ca.gov",
        "https://leginfo.legislature.ca.gov/faces/codes_displayexpandedbranch.xhtml?tocCode=CIV&division=3.&part=4.&title=1.81.5.",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ai_governance",
            "health_privacy",
            "biometric_privacy",
            "breach_notification",
            "data_broker",
            "children_privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-CA-CPPA",
        "US-CA",
        "California Privacy Protection Agency (CalPrivacy) — 11 CCR §§ 7000–7616 (CCPA, ADMT, Risk Assessments, DROP Rules)",
        "data_protection_authority",
        "cppa.ca.gov",
        "https://cppa.ca.gov/regulations/",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ai_governance",
            "admt",
            "risk_assessments",
            "data_broker",
            "cybersecurity_audits",
        ],
        legal_instrument_types=[
            "regulation",
            "official_guidance",
            "regulatory_enforcement_decision",
            "regulatory_consultation",
        ],
    ),
    _src(
        "SRC-US-CA-OAG",
        "US-CA",
        "California Office of the Attorney General — Privacy Enforcement & Data Breach Repository",
        "attorney_general",
        "oag.ca.gov",
        "https://oag.ca.gov/privacy",
        "html_structured",
        publication_coverage=["privacy", "breach_notification", "health_privacy", "ai_governance"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "consent_order_settlement"],
    ),
    # -------------------------------------------------------------------------
    # 6. COLORADO (US-CO) — CPA (C.R.S. §§ 6-1-1301 to 1314), Colorado AI Act (SB 24-205, §§ 6-1-1701 to 1707), Biometrics (HB 24-1130)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-CO-LEG",
        "US-CO",
        "Colorado General Assembly — C.R.S. Title 6 Art. 1 Pt. 13 (CPA), Pt. 17 (Colorado AI Act SB 24-205) & Pt. 7 (Breach)",
        "legislature",
        "leg.colorado.gov",
        "https://leg.colorado.gov/bills/sb24-205",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ai_governance",
            "biometric_privacy",
            "breach_notification",
            "children_privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-CO-COAG",
        "US-CO",
        "Colorado Office of the Attorney General — Colorado Privacy Act Rules (4 CCR 904-3) & AI Governance",
        "attorney_general",
        "coag.gov",
        "https://coag.gov/resources/colorado-privacy-act/",
        "html_structured",
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "ai_governance", "biometric_privacy", "breach_notification"],
        legal_instrument_types=[
            "regulation",
            "official_guidance",
            "regulatory_enforcement_decision",
            "regulatory_consultation",
        ],
    ),
    # -------------------------------------------------------------------------
    # 7. CONNECTICUT (US-CT) — CTDPA (Conn. Gen. Stat. §§ 42-515 to 42-526, P.A. 22-15, P.A. 23-56 Consumer Health, SB 1295), Breach (§ 36a-701b)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-CT-CGA",
        "US-CT",
        "Connecticut General Assembly — Conn. Gen. Stat. §§ 42-515 to 42-526 (CTDPA, Consumer Health Data & Minors) & § 36a-701b",
        "legislature",
        "cga.ct.gov",
        "https://www.cga.ct.gov/current/pub/chap_743jj.htm",
        "html_structured",
        publication_coverage=[
            "privacy",
            "data_protection",
            "health_privacy",
            "children_privacy",
            "ai_governance",
            "breach_notification",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-CT-AG",
        "US-CT",
        "Connecticut Office of the Attorney General — Privacy & Data Security Section",
        "attorney_general",
        "portal.ct.gov",
        "https://portal.ct.gov/ag/sections/privacy/the-connecticut-data-privacy-act",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "health_privacy", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 8. DELAWARE (US-DE) — DPDPA (Del. Code Ann. tit. 6, §§ 12D-101 to 12D-111), Breach (§§ 12B-101 to 12B-104)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-DE-LEGIS",
        "US-DE",
        "Delaware General Assembly — Del. Code Ann. Title 6 Ch. 12D (DPDPA) & Ch. 12B (Data Breach)",
        "legislature",
        "legis.delaware.gov",
        "https://delcode.delaware.gov/title6/c012d/index.html",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification", "children_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-DE-DOJ",
        "US-DE",
        "Delaware Department of Justice — Consumer Protection Unit & Personal Data Privacy Portal",
        "attorney_general",
        "attorneygeneral.delaware.gov",
        "https://attorneygeneral.delaware.gov/fraud/personal-data-privacy-portal/",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 9. FLORIDA (US-FL) — Florida Digital Bill of Rights (Fla. Stat. §§ 501.701-501.722) & FIPA (§ 501.171)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-FL-LEG",
        "US-FL",
        "Florida Legislature — Online Sunshine Florida Statutes Ch. 501 Pt. V (FDBR) & § 501.171 (FIPA)",
        "legislature",
        "leg.state.fl.us",
        "http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0500-0599/0501/0501PARTVContentsIndex.html",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification", "children_privacy", "biometric_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-FL-DLA-ADMIN",
        "US-FL",
        "Florida Department of Legal Affairs (Attorney General) & Florida Administrative Register (F.A.C. 2-30)",
        "attorney_general",
        "myfloridalegal.com",
        "https://www.myfloridalegal.com/consumer-protection",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["regulation", "official_guidance", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 10. GEORGIA (US-GA) — O.C.G.A. §§ 10-1-910 to 10-1-912 (Personal Identity Protection Act)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-GA-LEGIS",
        "US-GA",
        "Georgia General Assembly — Official Code of Georgia Annotated (O.C.G.A. Title 10 Ch. 1 Art. 34)",
        "legislature",
        "legis.ga.gov",
        "https://www.legis.ga.gov/legislation/all",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "cybersecurity", "children_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-GA-LAW-CPD",
        "US-GA",
        "Office of the Attorney General of Georgia — Consumer Protection Division",
        "attorney_general",
        "law.georgia.gov",
        "https://law.georgia.gov/key-issues/consumer-protection",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 11. HAWAII (US-HI) — Haw. Rev. Stat. §§ 487N-1 to 487N-7 (Security Breach of Personal Information) & Ch. 487J/487R
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-HI-CAPITOL",
        "US-HI",
        "Hawaii State Legislature — Hawaii Revised Statutes Ch. 487N, 487J & 487R (Personal Information & Destruction)",
        "legislature",
        "capitol.hawaii.gov",
        "https://www.capitol.hawaii.gov/hrscurrent/Vol11_Ch0476-0490/HRS0487N/",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "data_disposal", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-HI-DCCA-OCP",
        "US-HI",
        "Hawaii Department of Commerce and Consumer Affairs — Office of Consumer Protection & AG",
        "sector_regulator",
        "cca.hawaii.gov",
        "https://cca.hawaii.gov/ocp/security-breach-notices/",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection", "privacy"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 12. IDAHO (US-ID) — Idaho Code §§ 28-51-104 to 28-51-107 (Identity Theft & Security Breach)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-ID-LEGISLATURE",
        "US-ID",
        "Idaho Legislature — Idaho Statutes Title 28 Ch. 51 (Identity Theft & Security Breach Notification)",
        "legislature",
        "legislature.idaho.gov",
        "https://legislature.idaho.gov/statutesrules/idstat/Title28/T28CH51/",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "identity_theft", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-ID-AG",
        "US-ID",
        "Office of the Attorney General of Idaho — Consumer Protection Division",
        "attorney_general",
        "ag.idaho.gov",
        "https://www.ag.idaho.gov/consumer-protection/",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 13. ILLINOIS (US-IL) — BIPA (740 ILCS 14), PIPA (815 ILCS 530), AI Video Interview Act (820 ILCS 42), Genetic Info (410 ILCS 513)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-IL-ILGA",
        "US-IL",
        "Illinois General Assembly — 740 ILCS 14 (BIPA), 815 ILCS 530 (PIPA), 410 ILCS 513 (GIPA) & 820 ILCS 42 (AI Video Interview Act)",
        "legislature",
        "ilga.gov",
        "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=3004&ChapterID=57",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "biometric_privacy",
            "breach_notification",
            "ai_governance",
            "health_privacy",
            "genetic_privacy",
            "privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-IL-AG",
        "US-IL",
        "Illinois Attorney General — Privacy Unit & Data Breach Notification Portal",
        "attorney_general",
        "illinoisattorneygeneral.gov",
        "https://illinoisattorneygeneral.gov/Consumer-Protection/Identity-Theft/",
        "html_structured",
        publication_coverage=["biometric_privacy", "breach_notification", "privacy", "health_privacy"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 14. INDIANA (US-IN) — ICDPA (Ind. Code art. 24-15) & Breach (Ind. Code §§ 24-4.9-1 to 24-4.9-5)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-IN-IGA",
        "US-IN",
        "Indiana General Assembly — Indiana Code Title 24 Art. 15 (ICDPA) & Art. 4.9 (Disclosure of Security Breach)",
        "legislature",
        "iga.in.gov",
        "https://iga.in.gov/laws/2026/ic/titles/24#24-15",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-IN-AG",
        "US-IN",
        "Indiana Office of the Attorney General — Data Privacy & Identity Theft Unit",
        "attorney_general",
        "in.gov",
        "https://www.in.gov/attorneygeneral/consumer-protection-division/id-theft-prevention/",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 15. IOWA (US-IA) — ICDPA (Iowa Code ch. 715D) & Breach (Iowa Code ch. 715C)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-IA-LEGIS",
        "US-IA",
        "Iowa Legislature — Iowa Code Ch. 715D (Consumer Data Protection) & Ch. 715C (Personal Information Security Breach)",
        "legislature",
        "legis.iowa.gov",
        "https://www.legis.iowa.gov/docs/code/715D.pdf",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-IA-AG",
        "US-IA",
        "Office of the Attorney General of Iowa — Consumer Protection Division",
        "attorney_general",
        "iowaattorneygeneral.gov",
        "https://www.iowaattorneygeneral.gov/for-consumers/security-breach-notifications",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 16. KANSAS (US-KS) — Kan. Stat. Ann. §§ 50-7a01 to 50-7a04 (Wayne Owen Act / Security Breach)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-KS-KSLEGISLATURE",
        "US-KS",
        "Kansas Legislature — Kansas Statutes Annotated Ch. 50 Art. 7a (Protection of Consumer Information)",
        "legislature",
        "kslegislature.gov",
        "https://www.kslegislature.gov/li/b2025_26/statute/050_000_0000_chapter/050_007a_0000_article/",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "data_disposal", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-KS-AG",
        "US-KS",
        "Kansas Office of the Attorney General — Consumer Protection Division",
        "attorney_general",
        "ag.ks.gov",
        "https://ag.ks.gov/consumer-protection",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 17. KENTUCKY (US-KY) — KCDPA (Ky. Rev. Stat. §§ 367.3611-367.3629) & Breach (KRS § 365.732, §§ 61.931-61.934)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-KY-LEGISLATURE",
        "US-KY",
        "Kentucky General Assembly — Kentucky Revised Statutes Ch. 367 (KCDPA) & § 365.732 (Breach Notification)",
        "legislature",
        "legislature.ky.gov",
        "https://apps.legislature.ky.gov/law/statutes/chapter.aspx?id=39105",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification", "biometric_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-KY-AG",
        "US-KY",
        "Kentucky Office of the Attorney General — Office of Consumer Protection",
        "attorney_general",
        "ag.ky.gov",
        "https://www.ag.ky.gov/Priorities/Protecting-Kentuckians/Consumers/Pages/default.aspx",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 18. LOUISIANA (US-LA) — La. Rev. Stat. §§ 51:3071-51:3077 (Database Security Breach Notification Law) & LAC 16:III.701
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-LA-LEGIS",
        "US-LA",
        "Louisiana State Legislature — La. Rev. Stat. Title 51 Ch. 51 (Database Security Breach Notification Law)",
        "legislature",
        "legis.la.gov",
        "https://www.legis.la.gov/legis/Laws_Toc.aspx?folder=75&level=Parent",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "children_privacy", "cybersecurity"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-LA-AG-ADMIN",
        "US-LA",
        "Louisiana Department of Justice (Attorney General) & Louisiana Administrative Code (LAC 16:III.701)",
        "attorney_general",
        "ag.state.la.us",
        "https://www.ag.state.la.us/Page/ConsumerProtection",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "consumer_protection"],
        legal_instrument_types=["regulation", "official_guidance", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 19. MAINE (US-ME) — Me. Rev. Stat. tit. 10, §§ 1346-1350-B (Breach), tit. 35-A § 9301 (ISP Broadband Privacy) & Health Privacy
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-ME-LEGISLATURE",
        "US-ME",
        "Maine State Legislature — 10 M.R.S. Ch. 210-B (Notice of Risk to Personal Data) & 35-A M.R.S. § 9301 (Broadband ISP Privacy)",
        "legislature",
        "legislature.maine.gov",
        "https://legislature.maine.gov/statutes/10/title10ch210-Bsec0.html",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "isp_privacy", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-ME-AG",
        "US-ME",
        "Office of the Maine Attorney General — Consumer Protection Division & Data Breach Portal",
        "attorney_general",
        "maine.gov",
        "https://www.maine.gov/ag/consumer/identity_theft/index.shtml",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 20. MARYLAND (US-MD) — MODPA (Md. Code Ann., Com. Law §§ 14-4601 to 14-4613), Kids Code, PIPA (§§ 14-3501 to 14-3508) & AI Facial Recognition
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MD-MGALEG",
        "US-MD",
        "Maryland General Assembly — Commercial Law Title 14 Subt. 46 (MODPA), Subt. 35 (PIPA) & Labor/Biometric Statutes",
        "legislature",
        "mgaleg.maryland.gov",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gcl&section=14-4601",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "breach_notification",
            "children_privacy",
            "biometric_privacy",
            "ai_governance",
            "health_privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MD-AG",
        "US-MD",
        "Maryland Office of the Attorney General — Consumer Protection Division & Online Data Privacy Act Enforcement",
        "attorney_general",
        "marylandattorneygeneral.gov",
        "https://www.marylandattorneygeneral.gov/Pages/CPD/OnlineDataPrivacyAct.aspx",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification", "health_privacy"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 21. MASSACHUSETTS (US-MA) — Mass. Gen. Laws ch. 93H & 201 CMR 17.00 (Standards for Protection of Personal Information / WISP)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MA-MALECISLATURE",
        "US-MA",
        "The General Court of the Commonwealth of Massachusetts — M.G.L. ch. 93H (Security Breaches) & ch. 93I (Data Disposal)",
        "legislature",
        "malegislature.gov",
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXV/Chapter93H",
        "html_structured",
        publication_coverage=["breach_notification", "cybersecurity", "privacy", "data_disposal", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MA-OCABR-AG",
        "US-MA",
        "Massachusetts Office of Consumer Affairs and Business Regulation (OCABR) & AG — 201 CMR 17.00 WISP Regulations",
        "sector_regulator",
        "mass.gov",
        "https://www.mass.gov/regulations/201-CMR-1700-standards-for-the-protection-of-personal-information-of-residents-of-the-commonwealth",
        "html_structured",
        publication_coverage=["cybersecurity", "breach_notification", "privacy"],
        legal_instrument_types=["regulation", "official_guidance", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 22. MICHIGAN (US-MI) — Mich. Comp. Laws §§ 445.61-445.79d (Identity Theft Protection Act) & Insurance Data Security
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MI-LEGISLATURE",
        "US-MI",
        "Michigan Legislature — Michigan Compiled Laws Ch. 445 (Identity Theft Protection Act §§ 445.63, 445.72)",
        "legislature",
        "legislature.mi.gov",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-Act-452-of-2004",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "cybersecurity", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MI-AG",
        "US-MI",
        "Michigan Department of Attorney General — Consumer Protection & Privacy",
        "attorney_general",
        "michigan.gov",
        "https://www.michigan.gov/ag/consumer-protection",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection", "privacy"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 23. MINNESOTA (US-MN) — MCDPA (Minn. Stat. ch. 325M, §§ 325M.10-325M.21), Breach (§ 325E.61), Health Records (§ 144.291)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MN-REVISOR",
        "US-MN",
        "Minnesota Office of the Revisor of Statutes — Minn. Stat. Ch. 325M (MCDPA), § 325E.61 (Breach) & § 144.291 (Health Records)",
        "legislature",
        "revisor.mn.gov",
        "https://www.revisor.mn.gov/statutes/cite/325M",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ai_governance",
            "breach_notification",
            "health_privacy",
            "isp_privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MN-AG",
        "US-MN",
        "Office of the Minnesota Attorney General — Data Privacy Enforcement",
        "attorney_general",
        "ag.state.mn.us",
        "https://www.ag.state.mn.us/Consumer/IdentityTheft/",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
    # -------------------------------------------------------------------------
    # 24. MISSISSIPPI (US-MS) — Miss. Code Ann. § 75-24-29 (Breach Notification) & Insurance Data Security
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MS-LEGISLATURE",
        "US-MS",
        "Mississippi Legislature — Mississippi Code Title 75 Ch. 24 § 75-24-29 (Notice of Breach of Security)",
        "legislature",
        "billstatus.ls.state.ms.us",
        "http://billstatus.ls.state.ms.us/",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "cybersecurity"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MS-AGO",
        "US-MS",
        "Office of the Attorney General of Mississippi — Consumer Protection Division",
        "attorney_general",
        "ago.state.ms.us",
        "https://www.ago.state.ms.us/divisions/consumer-protection/",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 25. MISSOURI (US-MO) — Mo. Rev. Stat. § 407.1500 (Breach Notification) & Biometric/Health Laws
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MO-REVISOR",
        "US-MO",
        "Missouri Revisor of Statutes — Mo. Rev. Stat. § 407.1500 (Personal Information Breach Notification)",
        "legislature",
        "revisor.mo.gov",
        "https://revisor.mo.gov/main/OneSection.aspx?section=407.1500",
        "html_structured",
        publication_coverage=["breach_notification", "privacy", "health_privacy"],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MO-AGO",
        "US-MO",
        "Missouri Attorney General's Office — Consumer Protection & Data Breach Unit",
        "attorney_general",
        "ago.mo.gov",
        "https://ago.mo.gov/civil-division/consumer/",
        "html_structured",
        publication_coverage=["breach_notification", "consumer_protection", "privacy"],
        legal_instrument_types=["official_guidance", "regulation", "regulatory_enforcement_decision"],
    ),
    # -------------------------------------------------------------------------
    # 26. MONTANA (US-MT) — MCDPA (Mont. Code Ann. §§ 30-14-2801 to 30-14-2817, as amended by SB 297), Breach (§ 30-14-1704), Genetic (§ 30-14-2901)
    # -------------------------------------------------------------------------
    _src(
        "SRC-US-MT-LEGMT",
        "US-MT",
        "Montana Legislature — Mont. Code Ann. Title 30 Ch. 14 Pt. 28 (MCDPA, SB 384 / SB 297), Pt. 17 (Breach) & Pt. 29 (Genetic Privacy)",
        "legislature",
        "legmt.gov",
        "https://legmt.gov/laws/",
        "html_structured",
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "breach_notification",
            "children_privacy",
            "genetic_privacy",
            "biometric_privacy",
        ],
        legal_instrument_types=["statute", "legislative_bill"],
    ),
    _src(
        "SRC-US-MT-DOJ-OCP",
        "US-MT",
        "Montana Department of Justice — Office of Consumer Protection",
        "attorney_general",
        "dojmt.gov",
        "https://dojmt.gov/office-of-consumer-protection/",
        "html_structured",
        publication_coverage=["privacy", "data_protection", "breach_notification"],
        legal_instrument_types=["official_guidance", "regulatory_enforcement_decision", "regulation"],
    ),
]


def _build_diff_fixture(
    diff_id: str,
    document_id: str,
    jurisdiction_id: str,
    provision_ref: str,
    previous_version: str,
    current_version: str,
    previous_effective_date: date,
    current_effective_date: date,
    previous_text: str,
    current_text: str,
    change_type: str,
    changed_elements_summary: List[str],
) -> Dict[str, Any]:
    prev_sha = compute_sha256_hex(previous_text)
    curr_sha = compute_sha256_hex(current_text)
    record = ProvisionDiffRecord(
        diff_id=diff_id,
        document_id=document_id,
        jurisdiction_id=jurisdiction_id,
        provision_ref=provision_ref,
        previous_version=previous_version,
        current_version=current_version,
        previous_effective_date=previous_effective_date,
        current_effective_date=current_effective_date,
        previous_text=previous_text,
        current_text=current_text,
        previous_sha256=prev_sha,
        current_sha256=curr_sha,
        change_type=change_type,
        is_substantive=True,
        changed_elements_summary=changed_elements_summary,
        detected_at=datetime(2026, 10, 25, 12, 0, 0),
    )
    return record.model_dump()


# ---------------------------------------------------------------------------
# Authentic US State A–M Statutory Amendment Fixtures (RD-03 Provision Diffs)
# ---------------------------------------------------------------------------

AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES: List[Dict[str, Any]] = [
    # 1. California CCPA -> CPRA (Cal. Civ. Code § 1798.100: Right to Know / Collection Notice & Retention/Minimization)
    _build_diff_fixture(
        diff_id="DIFF-US-CA-CIV-1798-100-CPRA",
        document_id="DOC-US-CA-CCPA-CPRA",
        jurisdiction_id="US-CA",
        provision_ref="Cal. Civ. Code § 1798.100",
        previous_version="2020.1 (CCPA AB 375)",
        current_version="2023.1 (CPRA Prop. 24 / AB 1008)",
        previous_effective_date=date(2020, 1, 1),
        current_effective_date=date(2023, 1, 1),
        previous_text=(
            "1798.100. (a) A consumer shall have the right to request that a business that collects a consumer's "
            "personal information disclose to that consumer the categories and specific pieces of personal information "
            "the business has collected. (b) A business that collects a consumer's personal information shall, at or "
            "before the point of collection, inform consumers as to the categories of personal information to be "
            "collected and the purposes for which the categories of personal information shall be used. A business "
            "shall not collect additional categories of personal information or use personal information collected "
            "for additional purposes without providing the consumer with notice consistent with this section."
        ),
        current_text=(
            "1798.100. (a) A business that controls the collection of a consumer's personal information shall, at or "
            "before the point of collection, inform consumers as to: (1) The categories of personal information to be "
            "collected and the purposes for which the categories of personal information are collected or used and "
            "whether that information is sold or shared. (2) If the business collects sensitive personal information, "
            "the categories of sensitive personal information to be collected and the purposes for which the categories "
            "of sensitive personal information are collected or used, and whether that information is sold or shared. "
            "(3) The length of time the business intends to retain each category of personal information, including "
            "sensitive personal information, or if that is not possible, the criteria used to determine that period, "
            "provided that a business shall not retain a consumer's personal information or sensitive personal "
            "information for each disclosed purpose for which the personal information was collected for longer than is "
            "reasonably necessary for that disclosed purpose. (c) A business' collection, use, retention, and sharing "
            "of a consumer's personal information shall be reasonably necessary and proportionate to achieve the "
            "purposes for which the personal information was collected or processed, or for another disclosed purpose "
            "that is compatible with the context in which the personal information was collected, and not further "
            "processed in a manner that is incompatible with those purposes."
        ),
        change_type="substantive_amendment",
        changed_elements_summary=[
            "Added explicit notice of sensitive personal information categories and whether data is sold or shared (§ 1798.100(a)(1)-(2))",
            "Added mandatory retention period or retention criteria disclosure and prohibition on retaining personal information longer than reasonably necessary (§ 1798.100(a)(3))",
            "Added statutory data minimization and purpose limitation requirement ('reasonably necessary and proportionate') (§ 1798.100(c))",
        ],
    ),
    # 2. California CCPA/CPRA Rulemaking Mandate for Cybersecurity Audits, Risk Assessments & ADMT (Cal. Civ. Code § 1798.185(a)(15)-(16))
    _build_diff_fixture(
        diff_id="DIFF-US-CA-CIV-1798-185-A15-A16-ADMT",
        document_id="DOC-US-CA-CCPA-CPRA",
        jurisdiction_id="US-CA",
        provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16)",
        previous_version="2020.1 (CCPA AB 375)",
        current_version="2026.1 (CPRA / CalPrivacy ADMT & Risk Assessment Regulations 11 CCR §§ 7150-7222)",
        previous_effective_date=date(2020, 1, 1),
        current_effective_date=date(2026, 1, 1),
        previous_text=(
            "1798.185. (a) On or before July 1, 2020, the Attorney General shall solicit broad public participation "
            "and adopt regulations to further the purposes of this title, including establishing rules and procedures "
            "for the submission of verified consumer requests to know and to delete and for business compliance with "
            "a consumer's opt-out request under Section 1798.120."
        ),
        current_text=(
            "1798.185. (a)(15) Issuing regulations requiring businesses whose processing of consumers' personal "
            "information presents significant risk to consumers' privacy or security, to: (A) Perform a cybersecurity "
            "audit on an annual basis, including defining the scope of the audit and establishing a process to ensure "
            "that audits are thorough and independent. (B) Submit to the California Privacy Protection Agency on a "
            "regular basis a risk assessment with respect to their processing of personal information, including "
            "whether the processing involves sensitive personal information, and identifying and weighing the benefits "
            "resulting from the processing to the business, the consumer, other stakeholders, and the public, against "
            "the potential risks to the rights of the consumer associated with that processing, with the goal of "
            "restricting or prohibiting the processing if the risks to privacy of the consumer outweigh the benefits "
            "resulting from processing to the consumer, the business, other stakeholders, and the public. "
            "(16) Issuing regulations governing access and opt-out rights with respect to businesses' use of automated "
            "decisionmaking technology, including profiling and requiring businesses' response to access requests to "
            "include meaningful information about the logic involved in those decisionmaking processes, as well as a "
            "description of the likely outcome of the process with respect to the consumer."
        ),
        change_type="substantive_amendment",
        changed_elements_summary=[
            "Transferred rulemaking authority to the California Privacy Protection Agency (CalPrivacy)",
            "Mandated annual independent cybersecurity audits and regular risk assessment submissions for significant-risk processing (§ 1798.185(a)(15))",
            "Mandated access and opt-out rights for automated decisionmaking technology (ADMT) and profiling, including logic and outcome disclosures (§ 1798.185(a)(16))",
        ],
    ),
    # 3. Colorado Privacy Act — Consumer Rights, Universal Opt-Out & Biometric Identifiers (C.R.S. § 6-1-1306)
    _build_diff_fixture(
        diff_id="DIFF-US-CO-CRS-6-1-1306-UOOM",
        document_id="DOC-US-CO-CPA",
        jurisdiction_id="US-CO",
        provision_ref="C.R.S. § 6-1-1306",
        previous_version="2023.1 (SB 21-190 Initial Operative Text)",
        current_version="2025.1 (CPA Universal Opt-Out Mandatory Phase & HB 24-1130 / SB 24-041 Amendments)",
        previous_effective_date=date(2023, 7, 1),
        current_effective_date=date(2025, 7, 1),
        previous_text=(
            "6-1-1306. Consumer personal data — rights — repeal. (1)(a)(I) A consumer has the right to opt out of the "
            "processing of personal data concerning the consumer for purposes of: (A) Targeted advertising; (B) The "
            "sale of personal data; or (C) Profiling in furtherance of decisions that produce legal or similarly "
            "significant effects concerning a consumer. (IV)(A) Prior to July 1, 2024, a controller may allow "
            "consumers to exercise the right to opt out of the processing of personal data for purposes of targeted "
            "advertising or the sale of personal data through a user-selected universal opt-out mechanism that meets "
            "the technical specifications established by the attorney general pursuant to section 6-1-1313."
        ),
        current_text=(
            "6-1-1306. Consumer personal data — rights. (1)(a)(I) A consumer has the right to opt out of the "
            "processing of personal data concerning the consumer for purposes of: (A) Targeted advertising; (B) The "
            "sale of personal data; or (C) Profiling in furtherance of decisions that produce legal or similarly "
            "significant effects concerning a consumer. (IV)(B) Effective July 1, 2024, a controller that processes "
            "personal data for purposes of targeted advertising or the sale of personal data shall allow consumers to "
            "exercise the right to opt out of the processing of personal data for purposes of targeted advertising or "
            "the sale of personal data through a user-selected universal opt-out mechanism that meets the technical "
            "specifications established by the attorney general pursuant to section 6-1-1313. (3) If a controller "
            "denies a consumer's request under this section, the controller shall inform the consumer within "
            "forty-five days after receipt of the request of the justification for declining to take action and "
            "instructions for how to appeal the decision pursuant to subsection (3) of this section, and if the "
            "appeal is denied, inform the consumer of the consumer's ability to contact the attorney general."
        ),
        change_type="deadline_change",
        changed_elements_summary=[
            "Transitioned universal opt-out mechanism (Global Privacy Control / UOOM) from permissive ('may allow') to mandatory ('shall allow') under C.R.S. § 6-1-1306(1)(a)(IV)(B)",
            "Enforced 45-day response deadline with mandatory appeal workflow and Attorney General referral notice",
        ],
    ),
    # 4. Colorado Artificial Intelligence Act — Deployer Obligations for High-Risk AI Systems (C.R.S. § 6-1-1703)
    _build_diff_fixture(
        diff_id="DIFF-US-CO-CRS-6-1-1703-AI-ACT",
        document_id="DOC-US-CO-AI-ACT",
        jurisdiction_id="US-CO",
        provision_ref="C.R.S. § 6-1-1703",
        previous_version="2024.1 (SB 24-205 as enacted May 17, 2024)",
        current_version="2025.2 (SB 24-205 as amended by SB 25B-004 operative date extension)",
        previous_effective_date=date(2026, 2, 1),
        current_effective_date=date(2026, 6, 30),
        previous_text=(
            "6-1-1703. Deployer duty to avoid algorithmic discrimination — risk management policy and program. "
            "(1) On and after February 1, 2026, a deployer of a high-risk artificial intelligence system shall use "
            "reasonable care to protect consumers from any known or reasonably foreseeable risks of algorithmic "
            "discrimination. (2)(a) On and after February 1, 2026, and except as provided in subsection (6) of this "
            "section, a deployer of a high-risk artificial intelligence system shall implement a risk management "
            "policy and program to govern the deployer's deployment of the high-risk artificial intelligence system. "
            "(3)(a) On and after February 1, 2026, and except as provided in subsection (6) of this section, a "
            "deployer, or a third party contracted by the deployer, that deploys a high-risk artificial intelligence "
            "system shall complete an impact assessment for the high-risk artificial intelligence system."
        ),
        current_text=(
            "6-1-1703. Deployer duty to avoid algorithmic discrimination — risk management policy and program — "
            "impact assessment — consumer notices — reporting. (1) On and after June 30, 2026, a deployer of a "
            "high-risk artificial intelligence system shall use reasonable care to protect consumers from any known "
            "or reasonably foreseeable risks of algorithmic discrimination. (2)(a) On and after June 30, 2026, and "
            "except as provided in subsection (6) of this section, a deployer of a high-risk artificial intelligence "
            "system shall implement a risk management policy and program to govern the deployer's deployment of the "
            "high-risk artificial intelligence system, aligned with the latest version of the 'Artificial Intelligence "
            "Risk Management Framework' published by the National Institute of Standards and Technology or ISO/IEC "
            "42001. (3)(a) On and after June 30, 2026, a deployer shall complete an impact assessment prior to "
            "deploying a high-risk artificial intelligence system, annually thereafter, and within ninety days after "
            "any intentional and substantial modification. (4)(b) If a deployer deploys a high-risk artificial "
            "intelligence system to make, or be a substantial factor in making, a consequential decision that is "
            "adverse to a consumer, the deployer shall provide to the consumer a statement disclosing the principal "
            "reasons for the consequential decision, an opportunity to correct any incorrect personal data, and an "
            "opportunity to appeal an adverse consequential decision for human review if technically feasible. "
            "(7) A deployer shall notify the attorney general within ninety days after discovering that the high-risk "
            "artificial intelligence system has caused algorithmic discrimination."
        ),
        change_type="deadline_change",
        changed_elements_summary=[
            "Amended operative date of C.R.S. § 6-1-1703 from February 1, 2026 to June 30, 2026 pursuant to SB 25B-004",
            "Detailed deployer obligations for NIST AI RMF / ISO/IEC 42001 risk management alignment, annual and 90-day post-modification impact assessments, adverse consequential decision explanations/human appeal, and 90-day Attorney General algorithmic discrimination reporting",
        ],
    ),
]


def get_us_states_a_m_sources() -> List[RegulatorySourceEntry]:
    """Return all curated official legislative and administrative sources for US states A–M (26 states)."""
    return list(US_STATES_A_M_SOURCES)


def get_us_states_a_m_amendment_fixtures() -> List[Dict[str, Any]]:
    """Return authentic statutory amendment fixtures for California CCPA/CPRA and Colorado CPA / AI Act."""
    return list(AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES)


__all__ = [
    "AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES",
    "US_STATES_A_M_JURISDICTIONS",
    "US_STATES_A_M_SOURCES",
    "get_us_states_a_m_amendment_fixtures",
    "get_us_states_a_m_sources",
]
