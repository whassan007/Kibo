"""
KIBO Privacy OS — US State, DC & Territory Regulatory Pack.

Covers:
- A data breach notification CanonicalRegulation (``US-{ST}-BREACH``) for all 50 states,
  the District of Columbia, Puerto Rico, Guam and the U.S. Virgin Islands, generated from
  ``US_STATE_BREACH_RULES``.
- Comprehensive consumer privacy statutes (CA, CO, CT, VA, TX, UT, OR, MT, DE, IA, NE, NH,
  NJ, TN, MN, MD, IN, KY, RI, FL).
- Sectoral packs: CA CMIA / ADMT / Delete Act / AI transparency, CO AI Act, TX CUBI & HB 300,
  WA My Health My Data, IL BIPA, NY SHIELD & NYDFS 23 NYCRR 500.

``applicability_conditions`` keys follow the convention documented in us_federal.py.

US_STATE_BREACH_RULES schema (per jurisdiction code):
    statute                     citation of the breach notification statute
    individual_days             hard outer deadline for resident notice (None = no fixed day count)
    individual_text             statutory timing language for resident notice
    regulator_threshold         minimum affected residents triggering regulator notice
                                (1 = any breach requiring resident notice; None = no regulator notice duty)
    regulator_days              hard outer deadline for regulator notice (None = no fixed day count)
    regulator_text              statutory timing language for regulator notice
    regulator                   authority that receives notice
    cra_threshold               residents triggering notice to nationwide consumer reporting agencies (None = none)
    identity_protection_months  mandatory free credit monitoring/identity theft protection (None = not mandated)
    notes                       additional state-specific rules
    requires_counsel_signoff    True where a recent amendment should be re-verified before production reliance
    effective_date              operative date of the current statutory version where tracked, else _BREACH_BASELINE_DATE

StatutoryThreshold.logic_group convention for multi-prong tests:
    "OR"          independent prong; any one OR prong satisfies the test
    "OR_B"        members of a single compound prong that must ALL be met together (that compound prong is OR'd with the others)
    "AND"         mandatory gate that must be met in addition to the OR prongs
    "AND_OR", "AND_OR_B"  alternative prongs (simple / compound) evaluated only once all "AND" gates are met
    "CLASS_A"     classification prong (not an applicability gate)
"""

import hashlib
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from core.jrae.registry import US_STATES_METADATA, US_TERRITORIES_METADATA
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
LAST_VERIFIED_AT = datetime(2026, 10, 25)

_WUD = "Without unreasonable delay"
# By July 1, 2018 every state had a breach statute in force (Alabama eff. June 1, 2018; South Dakota eff. July 1, 2018).
# Used as effective_date where the operative date of the current statutory version is not separately tracked.
_BREACH_BASELINE_DATE = date(2018, 7, 1)
_MEX = "In the most expedient time possible and without unreasonable delay"


def _source_hash(regulation_id: str, instrument: str, section: str, url: str) -> str:
    payload = "|".join([regulation_id, instrument, section, url, RULE_VERSION])
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


_JURISDICTION_META: Dict[str, Dict[str, str]] = {
    code: {"name": name, "regulator": regulator, "url": url}
    for code, name, _, regulator, url in US_STATES_METADATA + US_TERRITORIES_METADATA
}
_TERRITORIES = {code for code, *_ in US_TERRITORIES_METADATA}


def _state(**kwargs) -> CanonicalRegulation:
    """Builds a state/territory CanonicalRegulation with shared defaults and citation fingerprint."""
    code = kwargs["jurisdiction_id"]
    meta = _JURISDICTION_META[code]
    kwargs.setdefault("jurisdiction_type", JurisdictionType.TERRITORY if code in _TERRITORIES else JurisdictionType.STATE)
    kwargs.setdefault("country", "US")
    kwargs.setdefault("state_or_province", meta["name"])
    kwargs.setdefault("competent_regulator", meta["regulator"])
    kwargs.setdefault("official_source_url", meta["url"])
    kwargs.setdefault("rule_version", RULE_VERSION)
    kwargs.setdefault("last_verified_at", LAST_VERIFIED_AT)
    kwargs["source_document_hash"] = _source_hash(
        kwargs["regulation_id"], kwargs["legal_instrument"], kwargs["article_or_section"], kwargs["official_source_url"]
    )
    return CanonicalRegulation(**kwargs)


def _br(
    statute: str,
    individual_days: Optional[int] = None,
    individual_text: str = _MEX,
    regulator_threshold: Optional[int] = None,
    regulator_days: Optional[int] = None,
    regulator_text: str = "No state regulator notification required",
    regulator: Optional[str] = None,
    cra_threshold: Optional[int] = 1001,
    identity_protection_months: Optional[int] = None,
    notes: str = "",
    requires_counsel_signoff: bool = False,
    effective_date: date = _BREACH_BASELINE_DATE,
) -> Dict[str, Any]:
    return {
        "statute": statute,
        "individual_days": individual_days,
        "individual_text": individual_text,
        "regulator_threshold": regulator_threshold,
        "regulator_days": regulator_days,
        "regulator_text": regulator_text,
        "regulator": regulator,
        "cra_threshold": cra_threshold,
        "identity_protection_months": identity_protection_months,
        "notes": notes,
        "requires_counsel_signoff": requires_counsel_signoff,
        "effective_date": effective_date,
    }


# ---------------------------------------------------------------------------
# 1. STATE DATA BREACH NOTIFICATION RULES (50 states + DC + PR/GU/VI)
# ---------------------------------------------------------------------------

US_STATE_BREACH_RULES: Dict[str, Dict[str, Any]] = {
    "US-AL": _br("Ala. Code §§ 8-38-1 to 8-38-12 (Alabama Data Breach Notification Act of 2018)",
                 45, "As expeditiously as possible and without unreasonable delay, no later than 45 days after determination of breach and likely substantial harm",
                 1001, 45, "Attorney General within 45 days if more than 1,000 Alabama residents are notified", "Alabama Attorney General",
                 notes="Third-party agents must notify the covered entity within 10 days of determination.", effective_date=date(2018, 6, 1)),
    "US-AK": _br("Alaska Stat. §§ 45.48.010-45.48.090 (Alaska Personal Information Protection Act)",
                 None, _MEX, 1, None, "Written notice to the Attorney General when the entity determines no notice to residents is required (no reasonable likelihood of harm)",
                 "Alaska Department of Law (Attorney General)",
                 notes="Regulator notice is tied to a no-harm determination rather than a headcount."),
    "US-AZ": _br("Ariz. Rev. Stat. §§ 18-551, 18-552",
                 45, "Within 45 days after determination of the breach",
                 1001, 45, "Attorney General and the three largest nationwide CRAs within 45 days if more than 1,000 Arizona residents are notified",
                 "Arizona Attorney General", cra_threshold=1001),
    "US-AR": _br("Ark. Code Ann. §§ 4-110-101 to 4-110-108 (Personal Information Protection Act), as amended by Act 1030 of 2019",
                 None, _MEX, 1001, 45, "Attorney General at the same time residents are notified or within 45 days after determination of breach, whichever is first, if more than 1,000 individuals affected",
                 "Arkansas Attorney General",
                 notes="Breach determination records must be retained for 5 years.", cra_threshold=None),
    "US-CA": _br("Cal. Civ. Code §§ 1798.29 (agencies), 1798.82 (businesses), as amended by SB 446 (2025); Cal. Health & Safety Code § 1280.15",
                 30, "In the most expedient time possible and without unreasonable delay, and within 30 calendar days of discovery or notification of the breach (SB 446, operative Jan 1, 2026), subject to law-enforcement delay",
                 501, 15, "Attorney General (sample notice via online form) within 15 calendar days of notifying affected residents when more than 500 California residents are notified",
                 "California Attorney General (Privacy Enforcement Unit)", cra_threshold=None, identity_protection_months=12,
                 notes=("Notice must use the statutory 'Notice of Data Breach' format and headings. If SSN/DL/ID numbers were exposed and the "
                        "business was the source, offer 12 months of identity theft prevention and mitigation services at no cost. Licensed "
                        "clinics/health facilities: notify CDPH and the patient within 15 business days of detecting unauthorized access to "
                        "medical information (H&S Code § 1280.15). Private right of action for security breaches under CCPA § 1798.150."),
                 requires_counsel_signoff=True, effective_date=date(2026, 1, 1)),
    "US-CO": _br("Colo. Rev. Stat. §§ 6-1-716 (business), 24-73-103 (government)",
                 30, "In the most expedient time possible and without unreasonable delay, no later than 30 days after determination that a security breach occurred",
                 500, 30, "Attorney General no later than 30 days after determination if 500 or more Colorado residents are affected",
                 "Colorado Attorney General",
                 notes="Written information security and secure disposal policies required (§§ 6-1-713, 6-1-713.5); covered entities must require third-party service providers to maintain security."),
    "US-CT": _br("Conn. Gen. Stat. § 36a-701b",
                 60, "Without unreasonable delay but not later than 60 days after discovery of the breach",
                 1, 60, "Attorney General not later than the time notice is provided to residents (online form)",
                 "Connecticut Attorney General", identity_protection_months=24,
                 notes="If SSN or ITIN exposed, offer at least 24 months of identity theft prevention/mitigation services at no cost. Ongoing supplemental notice to residents if further information discovered.", effective_date=date(2021, 10, 1), cra_threshold=None),
    "US-DE": _br("Del. Code Ann. tit. 6, §§ 12B-101 to 12B-104",
                 60, "Without unreasonable delay but not later than 60 days after determination of the breach",
                 501, 60, "Attorney General not later than the time notice is provided to residents if more than 500 Delaware residents are affected",
                 "Delaware Department of Justice", identity_protection_months=12,
                 notes="If SSN exposed, offer 1 year of credit monitoring at no cost. Reasonable security procedures required (§ 12B-100).", cra_threshold=None),
    "US-DC": _br("D.C. Code §§ 28-3851 to 28-3853 (as amended by the Security Breach Protection Amendment Act of 2020)",
                 None, _MEX, 50, None, "Office of the Attorney General promptly, and in no event later than when notice is provided to residents, if 50 or more District residents are affected",
                 "Office of the Attorney General for the District of Columbia", identity_protection_months=18,
                 notes="If SSN or TIN exposed, offer 18 months of identity theft protection services at no cost. Reasonable security safeguards required (§ 28-3852a)."),
    "US-FL": _br("Fla. Stat. § 501.171 (Florida Information Protection Act of 2014)",
                 30, "As expeditiously as practicable and without unreasonable delay, but no later than 30 days after determination of the breach (15-day extension with good cause provided in writing to the Department within 30 days)",
                 500, 30, "Department of Legal Affairs (Attorney General) as expeditiously as practicable, no later than 30 days after determination if 500 or more Floridians are affected",
                 "Florida Department of Legal Affairs (Attorney General)",
                 notes="Third-party agents must notify the covered entity within 10 days. On request, provide the Department a police report, forensic report, and breach policies. Reasonable security measures required."),
    "US-GA": _br("O.C.G.A. §§ 10-1-910 to 10-1-912",
                 None, _MEX, None, cra_threshold=10001,
                 notes=("No regulator notice. If more than 10,000 residents are notified at one time, notify all nationwide CRAs without unreasonable delay. "
                        "Data collectors maintaining data on behalf of an information broker must notify the broker within 24 hours of discovery.")),
    "US-HI": _br("Haw. Rev. Stat. §§ 487N-1 to 487N-7",
                 None, _WUD, 1001, None, "Office of Consumer Protection without unreasonable delay if more than 1,000 persons are notified at one time",
                 "Hawaii Department of Commerce and Consumer Affairs — Office of Consumer Protection", cra_threshold=1001),
    "US-ID": _br("Idaho Code §§ 28-51-104 to 28-51-107",
                 None, _MEX, None,
                 notes="State agencies must notify the Office of the Attorney General within 24 hours of discovery; no private-sector regulator notice.", cra_threshold=None),
    "US-IL": _br("815 ILCS 530/1 et seq. (Personal Information Protection Act)",
                 None, _MEX, 501, None, "Attorney General in the most expedient time possible and not later than when residents are notified if more than 500 Illinois residents are affected",
                 "Illinois Attorney General", cra_threshold=None,
                 notes="HIPAA-covered entities that notify HHS must also provide the Attorney General a copy within 5 business days of notifying HHS (815 ILCS 530/50)."),
    "US-IN": _br("Ind. Code §§ 24-4.9-1 to 24-4.9-5 (as amended by HEA 1351-2022)",
                 45, "Without unreasonable delay, but not more than 45 days after discovery of the breach",
                 1, 45, "Attorney General (any number of Indiana residents), using the AG's breach notification form",
                 "Indiana Office of the Attorney General", effective_date=date(2022, 7, 1)),
    "US-IA": _br("Iowa Code §§ 715C.1-715C.2",
                 None, _MEX, 501, 5, "Director of the Consumer Protection Division of the Attorney General's office within 5 business days after notifying consumers if more than 500 Iowa residents are affected",
                 "Iowa Attorney General — Consumer Protection Division", cra_threshold=None,
                 notes="Regulator deadline counts business days after resident notice."),
    "US-KS": _br("Kan. Stat. Ann. §§ 50-7a01 to 50-7a04",
                 None, _MEX, None, cra_threshold=1001),
    "US-KY": _br("Ky. Rev. Stat. § 365.732",
                 None, _MEX, None, cra_threshold=1001,
                 notes="Public agencies are governed separately by KRS 61.931-61.934 (notice to Commonwealth Office of Technology and others within 72 hours)."),
    "US-LA": _br("La. Rev. Stat. §§ 51:3071-51:3077; La. Admin. Code tit. 16, pt. III, § 701",
                 60, "In the most expedient time possible and without unreasonable delay, but not later than 60 days from discovery of the breach",
                 1, 10, "Consumer Protection Section of the Attorney General within 10 days of distribution of notice to Louisiana residents (any number)",
                 "Louisiana Department of Justice — Consumer Protection Section", cra_threshold=None,
                 notes="Failure to timely notify the AG carries fines of up to $5,000 per day."),
    "US-ME": _br("Me. Rev. Stat. tit. 10, §§ 1346-1350-B",
                 30, "As expediently as possible and without unreasonable delay, no more than 30 days after becoming aware of the breach and identifying its scope",
                 1, None, "Attorney General (or Department of Professional and Financial Regulation for regulated entities) when residents are notified",
                 "Office of the Maine Attorney General"),
    "US-MD": _br("Md. Code Ann., Com. Law §§ 14-3501 to 14-3508 (as amended 2022)",
                 45, "As soon as reasonably practicable, but not later than 45 days after the business concludes its investigation / discovers the breach",
                 1, None, "Office of the Attorney General prior to giving notice to individuals",
                 "Maryland Office of the Attorney General",
                 notes="Third-party maintainers must notify the owner/licensee within 10 days of discovery.", effective_date=date(2022, 10, 1), cra_threshold=1000),
    "US-MA": _br("Mass. Gen. Laws ch. 93H, §§ 1-6; 201 CMR 17.00 (Standards for the Protection of Personal Information)",
                 None, "As soon as practicable and without unreasonable delay",
                 1, None, "Attorney General and Director of the Office of Consumer Affairs and Business Regulation (OCABR) as soon as practicable (online form)",
                 "Massachusetts Attorney General & Office of Consumer Affairs and Business Regulation", cra_threshold=None, identity_protection_months=18,
                 notes=("Resident notice may not disclose the nature of the breach or number affected. If SSN exposed, offer 18 months of credit "
                        "monitoring at no cost (42 months for consumer reporting agencies). 201 CMR 17.00 requires a Written Information "
                        "Security Program (WISP), encryption of PI on laptops/portable devices and in transit over public networks, and "
                        "service provider oversight.")),
    "US-MI": _br("Mich. Comp. Laws §§ 445.63, 445.72 (Identity Theft Protection Act)",
                 None, _WUD, None, cra_threshold=1001),
    "US-MN": _br("Minn. Stat. § 325E.61",
                 None, _MEX, None,
                 notes="If more than 500 persons are notified at one time, notify nationwide CRAs within 48 hours.", cra_threshold=501),
    "US-MS": _br("Miss. Code Ann. § 75-24-29",
                 None, _WUD, None, cra_threshold=None),
    "US-MO": _br("Mo. Rev. Stat. § 407.1500",
                 None, _WUD, 1001, None, "Attorney General and nationwide CRAs without unreasonable delay if more than 1,000 Missouri residents are notified at one time",
                 "Missouri Attorney General", cra_threshold=1001),
    "US-MT": _br("Mont. Code Ann. §§ 30-14-1704, 2-6-1503",
                 None, _WUD, 1, None, "Attorney General's Office of Consumer Protection simultaneously with resident notice (electronic copy of notice and statement of number affected)",
                 "Montana Department of Justice — Office of Consumer Protection", cra_threshold=None),
    "US-NE": _br("Neb. Rev. Stat. §§ 87-801 to 87-808",
                 None, _MEX, 1, None, "Attorney General not later than the time notice is provided to Nebraska residents",
                 "Nebraska Attorney General", cra_threshold=None),
    "US-NV": _br("Nev. Rev. Stat. §§ 603A.010-603A.290",
                 None, _MEX, None, cra_threshold=1001,
                 notes="Data collectors must encrypt PI transmitted outside the secure system and comply with PCI DSS when accepting payment cards (NRS 603A.215)."),
    "US-NH": _br("N.H. Rev. Stat. Ann. §§ 359-C:19 to 359-C:21",
                 None, "As soon as possible",
                 1, None, "Attorney General (or primary regulator for regulated entities) as soon as possible",
                 "New Hampshire Department of Justice (Attorney General)"),
    "US-NJ": _br("N.J. Stat. Ann. §§ 56:8-161 to 56:8-166",
                 None, _MEX, 1, None, "Division of State Police in the Department of Law and Public Safety, in advance of disclosure to customers",
                 "New Jersey Division of State Police",
                 notes="Regulator (State Police) notice must precede resident notice."),
    "US-NM": _br("N.M. Stat. Ann. §§ 57-12C-1 to 57-12C-12 (Data Breach Notification Act)",
                 45, "In the most expedient time possible, but not later than 45 calendar days following discovery",
                 1001, 45, "Office of the Attorney General and major CRAs within 45 calendar days if more than 1,000 New Mexico residents are notified",
                 "New Mexico Department of Justice", cra_threshold=1001),
    "US-NY": _br("N.Y. Gen. Bus. Law § 899-aa (as amended by S2659-B/A8872-A, Dec. 2024) and § 899-bb (SHIELD Act); 23 NYCRR 500.17",
                 30, "In the most expedient time possible and without unreasonable delay, and no later than 30 days after discovery of the breach",
                 1, None, "Attorney General, Department of State, Division of State Police and (since March 2025) the Department of Financial Services as to timing, content, distribution and approximate number affected",
                 "New York State Office of the Attorney General, Department of State, Division of State Police & NYDFS", cra_threshold=5001,
                 notes=("NYDFS-regulated covered entities must separately notify NYDFS within 72 hours of determining a reportable cybersecurity "
                        "incident (23 NYCRR 500.17; see US-NY-NYDFS-500). HIPAA covered entities must also provide a copy of HHS breach "
                        "reports to the Attorney General within 5 business days. CRA notice if more than 5,000 residents are notified."),
                 requires_counsel_signoff=True, effective_date=date(2024, 12, 21)),
    "US-NC": _br("N.C. Gen. Stat. §§ 75-61, 75-65",
                 None, _WUD, 1, None, "Consumer Protection Division of the Attorney General's Office without unreasonable delay (online form)",
                 "North Carolina Department of Justice — Consumer Protection Division"),
    "US-ND": _br("N.D. Cent. Code §§ 51-30-01 to 51-30-07",
                 None, _MEX, 251, None, "Attorney General in the most expedient time possible and without unreasonable delay if more than 250 North Dakota residents are affected",
                 "North Dakota Office of Attorney General", cra_threshold=None),
    "US-OH": _br("Ohio Rev. Code §§ 1349.19, 1349.191, 1349.192; § 1354.01-1354.05 (cybersecurity safe harbor)",
                 45, "In the most expedient time possible, but not later than 45 days following discovery or notification of the breach",
                 None, cra_threshold=1001,
                 notes="Ohio Data Protection Act (R.C. Ch. 1354) affords an affirmative defense to tort claims for entities maintaining a cybersecurity program conforming to an industry framework (NIST CSF, ISO 27001, etc.)."),
    "US-OK": _br("Okla. Stat. tit. 24, §§ 161-166 (Security Breach Notification Act), as amended by SB 626 (2025)",
                 None, _WUD, 500, 60, "Attorney General within 60 days after notifying affected residents if 500 or more Oklahoma residents (1,000 or more for credit bureaus) are affected (operative Jan 1, 2026)",
                 "Oklahoma Office of the Attorney General",
                 notes="SB 626 also introduced an affirmative defense for entities using reasonable safeguards and prompt notice.",
                 requires_counsel_signoff=True, effective_date=date(2026, 1, 1)),
    "US-OR": _br("Or. Rev. Stat. §§ 646A.600-646A.628 (Oregon Consumer Information Protection Act)",
                 45, "In the most expeditious manner possible, without unreasonable delay, but not later than 45 days after discovery or notification of the breach",
                 251, None, "Attorney General if more than 250 Oregon consumers are affected (online form)",
                 "Oregon Department of Justice (Attorney General)",
                 notes="Vendors must notify the covered entity within 10 days and the AG if more than 250 consumers are affected and the covered entity has not."),
    "US-PA": _br("73 Pa. Stat. §§ 2301-2330 (Breach of Personal Information Notification Act), as amended by Act 33 of 2024",
                 None, _WUD, 501, None, "Office of Attorney General concurrently with notice to residents if more than 500 Pennsylvania residents are affected",
                 "Pennsylvania Office of Attorney General", identity_protection_months=12,
                 notes="If SSN, bank account number or driver's license/state ID number exposed, offer 12 months of credit monitoring and one independent credit report at no cost (Act 33 of 2024, effective Sept. 26, 2024).", effective_date=date(2024, 9, 26)),
    "US-RI": _br("R.I. Gen. Laws §§ 11-49.3-1 to 11-49.3-6 (Identity Theft Protection Act of 2015)",
                 45, "In the most expedient time possible, but no later than 45 calendar days after confirmation of the breach",
                 501, None, "Attorney General and major CRAs if more than 500 Rhode Island residents are affected",
                 "Rhode Island Office of the Attorney General", cra_threshold=501, identity_protection_months=12,
                 notes="Notice must include availability of credit monitoring (12 months is customary under AG guidance)."),
    "US-SC": _br("S.C. Code Ann. § 39-1-90; S.C. Code § 38-99-10 et seq. (Insurance Data Security Act)",
                 None, _MEX, 1001, None, "Department of Consumer Affairs (Consumer Protection Division) and nationwide CRAs without unreasonable delay if more than 1,000 persons are notified at one time",
                 "South Carolina Department of Consumer Affairs", cra_threshold=1001),
    "US-SD": _br("S.D. Codified Laws §§ 22-40-19 to 22-40-26",
                 60, "Not later than 60 days from discovery or notification of the breach",
                 251, None, "Attorney General if more than 250 South Dakota residents are affected",
                 "South Dakota Office of Attorney General", cra_threshold=1, effective_date=date(2018, 7, 1)),
    "US-TN": _br("Tenn. Code Ann. § 47-18-2107",
                 45, "Immediately, but no later than 45 days from discovery or notification of the breach",
                 None, cra_threshold=1001),
    "US-TX": _br("Tex. Bus. & Com. Code §§ 521.002, 521.053 (as amended by SB 768, 2023)",
                 60, "Without unreasonable delay and not later than the 60th day after determination of the breach",
                 250, 30, "Attorney General as soon as practicable and not later than the 30th day after determination if 250 or more Texas residents are affected (AG online form; AG posts list publicly)",
                 "Texas Office of the Attorney General", cra_threshold=10001,
                 notes="CRA notice if more than 10,000 persons are notified at one time. Civil penalties up to $100 per individual per day of delay (max $250,000 per breach).", effective_date=date(2023, 9, 1)),
    "US-UT": _br("Utah Code Ann. §§ 13-44-101 to 13-44-301 (Protection of Personal Information Act), as amended 2024",
                 None, _MEX, 500, None, "Attorney General's Office and the Utah Cyber Center if 500 or more Utah residents are affected",
                 "Utah Office of the Attorney General & Utah Cyber Center", cra_threshold=1001, effective_date=date(2024, 5, 1)),
    "US-VT": _br("Vt. Stat. Ann. tit. 9, §§ 2430, 2435",
                 45, "In the most expedient time possible and without unreasonable delay, but not later than 45 days after discovery or notification",
                 1, 14, "Preliminary notice to the Attorney General (or Department of Financial Regulation for regulated entities) within 14 business days of discovery, and a copy of resident notice when sent",
                 "Vermont Office of the Attorney General",
                 notes="Preliminary regulator notice is measured in business days and precedes resident notice."),
    "US-VA": _br("Va. Code Ann. §§ 18.2-186.6 (personal information), 32.1-127.1:05 (medical information), 58.1-341.2 (tax information)",
                 None, _WUD, 1, None, "Office of the Attorney General without unreasonable delay (any number); employer breaches of tax information require notice to the AG",
                 "Office of the Attorney General of Virginia", cra_threshold=1001),
    "US-WA": _br("Rev. Code Wash. §§ 19.255.005-19.255.040 (as amended by HB 1071, 2019)",
                 30, "In the most expedient time possible, without unreasonable delay, and no more than 30 calendar days after discovery of the breach",
                 501, 30, "Attorney General no more than 30 calendar days after discovery if more than 500 Washington residents are affected; updates required",
                 "Washington State Office of the Attorney General", cra_threshold=None, effective_date=date(2020, 3, 1)),
    "US-WV": _br("W. Va. Code §§ 46A-2A-101 to 46A-2A-105",
                 None, _WUD, None, cra_threshold=1001),
    "US-WI": _br("Wis. Stat. § 134.98",
                 45, "Within a reasonable time, not to exceed 45 days after learning of the breach",
                 None, cra_threshold=1001),
    "US-WY": _br("Wyo. Stat. Ann. §§ 40-12-501 to 40-12-509",
                 None, _MEX, None, cra_threshold=None),
    "US-PR": _br("P.R. Laws Ann. tit. 10, §§ 4051-4055 (Act No. 111 of 2005, Citizen Information on Data Banks Security Act)",
                 None, "As expeditiously as possible, taking into account law enforcement needs",
                 1, 10, "Department of Consumer Affairs (DACO) within 10 days of detecting the breach; DACO makes a public announcement within 24 hours of receipt",
                 "Puerto Rico Department of Consumer Affairs (DACO)", cra_threshold=None),
    "US-GU": _br("9 Guam Code Ann. §§ 48.10-48.80 (Notification of Breaches of Personal Information)",
                 None, _WUD, None, cra_threshold=None),
    "US-VI": _br("V.I. Code Ann. tit. 14, §§ 2208-2212 (Identity Theft Prevention Act)",
                 None, _MEX, None, cra_threshold=None),
}

def _breach_regulation(code: str, rule: Dict[str, Any]) -> CanonicalRegulation:
    meta = _JURISDICTION_META[code]
    st = code.split("-")[1]
    reg_threshold = rule["regulator_threshold"]
    notifications = [f"Affected residents: {rule['individual_text']}"]
    if reg_threshold is not None:
        notifications.append(f"Regulator ({rule['regulator']}): {rule['regulator_text']}")
    else:
        notifications.append("No state regulator/Attorney General notification mandated by statute")
    if rule["cra_threshold"]:
        notifications.append(
            "Nationwide consumer reporting agencies: required for any notified breach"
            if rule["cra_threshold"] == 1
            else f"Nationwide consumer reporting agencies: required when {rule['cra_threshold']:,} or more residents are notified"
        )
    if rule["identity_protection_months"]:
        notifications.append(f"Offer {rule['identity_protection_months']} months of free credit monitoring/identity theft protection where statutory trigger met")
    if rule["notes"]:
        notifications.append(rule["notes"])

    actions = [
        "Investigate and document breach determination (scope, data elements, residents affected, harm analysis where permitted)",
        "Notify affected residents with statutorily required content and method (written, electronic or substitute notice)",
        "Third-party maintainers: notify data owner/licensee promptly upon discovery",
        "Honor law-enforcement delay requests and document them",
    ]
    if reg_threshold is not None:
        actions.append(f"Notify {rule['regulator']} per statutory threshold and timing")
    if rule["cra_threshold"]:
        actions.append("Notify nationwide consumer reporting agencies when CRA threshold is met")
    if rule["identity_protection_months"]:
        actions.append(f"Offer {rule['identity_protection_months']} months of credit monitoring/identity theft protection at no cost")

    signoff = rule["requires_counsel_signoff"]
    return _state(
        regulation_id=f"US-{st}-BREACH",
        jurisdiction_id=code,
        legal_authority=f"{meta['name']} legislature; enforced by {rule['regulator'] or meta['regulator']}",
        legal_instrument=f"{meta['name']} Data Breach Notification Law",
        article_or_section=rule["statute"],
        effective_date=rule["effective_date"],
        applicability_conditions={
            "subject_locations_any": [code],
            "data_categories_any": ["personal_information", "ssn", "drivers_license", "financial_account", "payment_card", "credentials", "health_information", "biometric_data"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to persons/businesses that own, license or maintain computerized personal information of residents "
                f"of {meta['name']}, regardless of where the entity is located. Encrypted data is generally exempt unless the key is also compromised. "
                "Most states deem compliance with GLBA/HIPAA/primary-regulator notice procedures sufficient for resident notice, but regulator notice may still apply."
            ),
        },
        thresholds=(
            [StatutoryThreshold(metric="affected_residents_count", operator=">=", value=reg_threshold, logic_group="AND",
                                description=f"Regulator notification threshold: {rule['regulator_text']}")]
            if reg_threshold is not None else []
        ),
        exemptions=[
            ExemptionRule(
                exemption_id=f"{st}-BREACH-ENCRYPTION",
                exemption_type="data_level",
                condition_field="data_categories",
                condition_values=["encrypted_key_not_compromised", "redacted"],
                carve_out_statute=rule["statute"],
                description="Encrypted or redacted personal information is outside the definition of a breach unless the decryption key/credentials were also acquired.",
            ),
            ExemptionRule(
                exemption_id=f"{st}-BREACH-FEDERAL-REGULATED",
                exemption_type="entity_level",
                condition_field="organization_type",
                condition_values=["healthcare_covered_entity", "business_associate", "financial_institution"],
                carve_out_statute=rule["statute"],
                description="Entities complying with HIPAA/GLBA or primary functional regulator notification procedures are generally deemed compliant for resident notice; regulator/AG copy requirements may still apply.",
            ),
        ],
        preemption_rules=[
            PreemptionRule(
                rule_id=f"{st}-BREACH-FED-CONCURRENT",
                preempts_or_yields="concurrent_with",
                target_regulation_id="US-FED-HIPAA-BREACH",
                scope_condition="Entity subject to HIPAA, GLBA, HBNR or NYDFS-style sectoral breach rules",
                description="No federal law generally preempts state breach statutes; apply the shortest applicable deadline across regimes.",
            ),
        ],
        organization_types=["private", "public", "nonprofit", "government_agency", "financial_institution", "healthcare_covered_entity", "business_associate", "educational_institution"],
        industry_sectors=["all"],
        data_subject_categories=["residents", "consumers", "employees"],
        data_categories=["personal_information", "ssn", "drivers_license", "financial_account", "payment_card", "credentials"],
        processing_activities=["breach_response", "incident_response"],
        required_actions=actions,
        required_assessments=["State breach notification applicability & harm analysis"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_days=rule["regulator_days"],
            breach_regulator_text=rule["regulator_text"],
            breach_attorney_general_threshold_individuals=reg_threshold,
            breach_individual_notification_days=rule["individual_days"],
            breach_individual_text=rule["individual_text"],
        ),
        notification_requirements=notifications,
        required_evidence=["Incident investigation report", "Breach determination memo with discovery date", "Copies of resident/regulator/CRA notices", "Mailing/distribution proof", "Law-enforcement delay documentation (if any)"],
        approval_requirements=["Counsel approval of breach determination and notice content", "Executive approval prior to external notification"],
        competent_regulator=rule["regulator"] or meta["regulator"],
        deployment_status=DeploymentStatus.TESTED if signoff else DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF if signoff else LegalReviewStatus.VERIFIED,
        domain_category="breach_notification",
    )


# ---------------------------------------------------------------------------
# 2. COMPREHENSIVE CONSUMER PRIVACY STATUTES — shared builders
# ---------------------------------------------------------------------------

_CONSUMER_RIGHTS = [
    "Honor right to confirm processing and access personal data",
    "Honor right to correct inaccurate personal data",
    "Honor right to delete personal data",
    "Honor right to data portability",
    "Honor opt-out of targeted advertising, sale of personal data, and profiling in furtherance of decisions producing legal or similarly significant effects",
    "Provide a clear and meaningful privacy notice",
    "Practice data minimization and purpose limitation",
    "Obtain opt-in consent before processing sensitive data (and COPPA-compliant consent for known children under 13)",
    "Execute controller-processor contracts with statutorily required terms",
    "Conduct data protection assessments for targeted advertising, sale, sensitive data, and risky profiling",
    "Provide an appeal process and Attorney General contact information on denial",
    "Do not discriminate against consumers for exercising rights",
    "Maintain reasonable administrative, technical and physical data security practices",
]

_UOOM_ACTION = "Honor universal opt-out mechanisms / Global Privacy Control signals as valid opt-out of sale and targeted advertising"


def _thr(*items) -> List[StatutoryThreshold]:
    out = []
    for metric, op, value, group, desc in items:
        out.append(StatutoryThreshold(metric=metric, operator=op, value=value, logic_group=group, description=desc,
                                      currency="USD" if "revenue_usd" in metric else None))
    return out


def _std_exemptions(st: str, glba: str, hipaa: str, nonprofit_exempt: bool, higher_ed_exempt: bool) -> List[ExemptionRule]:
    ex = [
        ExemptionRule(
            exemption_id=f"{st}-GLBA",
            exemption_type="entity_level" if glba == "entity" else "data_level",
            condition_field="organization_type" if glba == "entity" else "data_categories",
            condition_values=["financial_institution"] if glba == "entity" else ["nonpublic_personal_information"],
            carve_out_statute="Gramm-Leach-Bliley Act, 15 U.S.C. § 6801 et seq.",
            description=f"GLBA {'financial institutions are exempt at the entity level' if glba == 'entity' else 'covered data is exempt (data-level only)'}.",
        ),
        ExemptionRule(
            exemption_id=f"{st}-HIPAA",
            exemption_type="entity_level" if hipaa == "entity" else "data_level",
            condition_field="hipaa_status" if hipaa == "entity" else "data_categories",
            condition_values=["covered_entity", "business_associate"] if hipaa == "entity" else ["phi"],
            carve_out_statute="HIPAA, 45 CFR Parts 160 and 164",
            description=f"HIPAA {'covered entities and business associates are exempt at the entity level' if hipaa == 'entity' else 'protected health information is exempt (data-level only)'}.",
        ),
        ExemptionRule(
            exemption_id=f"{st}-FCRA-FERPA-DPPA-COPPA",
            exemption_type="data_level",
            condition_field="data_categories",
            condition_values=["consumer_report_data", "ferpa_education_records", "dppa_motor_vehicle_records", "farm_credit_act_data"],
            carve_out_statute="FCRA 15 U.S.C. § 1681; FERPA 20 U.S.C. § 1232g; DPPA 18 U.S.C. § 2721",
            description="Data regulated by FCRA (to the extent of regulated activity), FERPA, DPPA and similar federal regimes is exempt; COPPA-compliant parental consent satisfies child consent obligations.",
        ),
        ExemptionRule(
            exemption_id=f"{st}-EMPLOYEE-B2B",
            exemption_type="data_level",
            condition_field="data_subject_categories",
            condition_values=["employees", "job_applicants", "b2b_contacts"],
            carve_out_statute="Definition of 'consumer'",
            description="Individuals acting in a commercial or employment context are excluded from 'consumer'.",
        ),
        ExemptionRule(
            exemption_id=f"{st}-GOVERNMENT",
            exemption_type="entity_level",
            condition_field="organization_type",
            condition_values=["government_agency"],
            carve_out_statute="Statutory exemption for state bodies and political subdivisions",
            description="State agencies and political subdivisions are exempt.",
        ),
    ]
    if nonprofit_exempt:
        ex.append(ExemptionRule(exemption_id=f"{st}-NONPROFIT", exemption_type="entity_level", condition_field="organization_type",
                                condition_values=["nonprofit"], carve_out_statute="Statutory nonprofit exemption",
                                description="Nonprofit organizations are exempt."))
    if higher_ed_exempt:
        ex.append(ExemptionRule(exemption_id=f"{st}-HIGHER-ED", exemption_type="entity_level", condition_field="organization_type",
                                condition_values=["educational_institution"], carve_out_statute="Statutory institution of higher education exemption",
                                description="Institutions of higher education are exempt."))
    return ex


def _comprehensive(
    reg_id: str,
    code: str,
    instrument: str,
    section: str,
    url: str,
    effective: date,
    thresholds: List[StatutoryThreshold],
    exemptions: List[ExemptionRule],
    *,
    initial_days: int = 45,
    extension_days: Optional[int] = 45,
    appeal_days: Optional[int] = 60,
    cure_days: Optional[int] = None,
    cure_note: str = "",
    extra_actions: Optional[List[str]] = None,
    extra_assessments: Optional[List[str]] = None,
    notes: str = "",
    regulator: Optional[str] = None,
    uoom: bool = False,
    status: RegulatoryStatus = RegulatoryStatus.EFFECTIVE,
    counsel_signoff: bool = False,
    data_categories: Optional[List[str]] = None,
    transition_end: Optional[date] = None,
) -> CanonicalRegulation:
    actions = list(_CONSUMER_RIGHTS) + ([_UOOM_ACTION] if uoom else []) + (extra_actions or [])
    deadlines_text = [
        f"Consumer rights requests: respond within {initial_days} days" + (f", extendable once by {extension_days} days when reasonably necessary with notice" if extension_days else ""),
    ]
    if appeal_days:
        deadlines_text.append(f"Appeals: decide within {appeal_days} days of receipt")
    if cure_note:
        deadlines_text.append(cure_note)
    return _state(
        regulation_id=reg_id,
        jurisdiction_id=code,
        legal_authority=f"{_JURISDICTION_META[code]['name']} legislature; enforced by {regulator or _JURISDICTION_META[code]['regulator']}",
        legal_instrument=instrument,
        official_source_url=url,
        article_or_section=section,
        effective_date=effective,
        transition_period_end=transition_end,
        applicability_conditions={
            "subject_locations_any": [code],
            "gate_logic": "thresholds",
            "notes": notes or "Applies to persons conducting business in the state or producing products/services targeted to state residents that meet the statutory thresholds.",
        },
        thresholds=thresholds,
        exemptions=exemptions,
        preemption_rules=[
            PreemptionRule(
                rule_id=f"{reg_id}-FED-YIELD",
                preempts_or_yields="yields_to",
                target_regulation_id="US-FED-HIPAA-PRIVACY",
                scope_condition="Data or entities regulated by HIPAA/GLBA/FCRA/FERPA/COPPA per exemption list",
                description="Comprehensive state law yields to sector-specific federal regimes to the extent of statutory exemptions; no general federal preemption.",
            ),
        ],
        organization_types=["private", "controller", "processor"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "children", "teens"],
        data_categories=data_categories or ["personal_data", "sensitive_data", "precise_geolocation", "biometric_data", "health_data", "children_data"],
        processing_activities=["targeted_advertising", "sale_of_personal_data", "profiling", "sensitive_data_processing", "ai_or_admt"],
        required_actions=actions,
        required_assessments=["Data Protection Assessment (DPA)"] + (extra_assessments or []),
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=initial_days,
            rights_request_extension_days=extension_days,
            rights_request_appeal_days=appeal_days,
            cure_period_days=cure_days,
            breach_regulator_text=f"See US-{code.split('-')[1]}-BREACH",
            breach_individual_text=f"See US-{code.split('-')[1]}-BREACH",
        ),
        notification_requirements=deadlines_text,
        required_evidence=["Published privacy notice", "DSAR log with response timestamps", "Appeal decisions", "Data protection assessments", "Processor contracts", "Sensitive data consent records", "Opt-out signal handling logs"],
        approval_requirements=["Privacy lead approval of data protection assessments", "Counsel approval for sale of sensitive data or high-risk profiling"],
        competent_regulator=regulator or _JURISDICTION_META[code]["regulator"],
        regulatory_status=status,
        deployment_status=DeploymentStatus.TESTED if counsel_signoff else DeploymentStatus.PRODUCTION_ENABLED,
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF if counsel_signoff else LegalReviewStatus.VERIFIED,
        domain_category="privacy",
    )


_T100K = ("consumer_records_count", ">=", 100000, "OR", "Controls or processes personal data of at least 100,000 state consumers in a calendar year (excluding data processed solely to complete a payment transaction)")


def _t_sale(count: int, pct: int, desc_pct: str):
    return [
        ("consumer_records_count", ">=", count, "OR_B", f"Controls or processes personal data of at least {count:,} consumers AND ..."),
        ("data_broker_revenue_pct", ">", pct, "OR_B", f"... {desc_pct} of gross revenue from the sale of personal data"),
    ]


# ---------------------------------------------------------------------------
# 3. CALIFORNIA
# ---------------------------------------------------------------------------

def _california() -> List[CanonicalRegulation]:
    regs: List[CanonicalRegulation] = []

    regs.append(_state(
        regulation_id="US-CA-CCPA-CPRA",
        jurisdiction_id="US-CA",
        legal_authority="California Privacy Protection Agency (CalPrivacy) and California Attorney General",
        legal_instrument="California Consumer Privacy Act of 2018, as amended by the California Privacy Rights Act of 2020, and CCPA Regulations",
        official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?division=3.&part=4.&lawCode=CIV&title=1.81.5",
        article_or_section="Cal. Civ. Code §§ 1798.100-1798.199.100; Cal. Code Regs. tit. 11, §§ 7000-7304",
        effective_date=date(2020, 1, 1),
        applicability_conditions={
            "subject_locations_any": ["US-CA"],
            "gate_logic": "thresholds",
            "notes": (
                "Applies to for-profit businesses doing business in California that collect consumers' personal information "
                "and meet any one threshold. 'Consumer' includes employees, job applicants, contractors and B2B contacts "
                "(exemptions expired Jan 1, 2023). CPRA amendments operative Jan 1, 2023; regulations amended (ADMT, risk "
                "assessment, cybersecurity audit) effective Jan 1, 2026. Revenue threshold CPI-adjusted to $26,625,000 "
                "effective Jan 1, 2025."
            ),
        },
        thresholds=_thr(
            ("annual_revenue_usd", ">", 26625000, "OR", "Annual gross revenues in excess of $26,625,000 in the preceding calendar year (CPI-adjusted, § 1798.140(d)(1)(A))"),
            ("consumer_records_count", ">=", 100000, "OR", "Alone or in combination, annually buys, sells, or shares the personal information of 100,000 or more consumers or households (§ 1798.140(d)(1)(B))"),
            ("data_broker_revenue_pct", ">=", 50, "OR", "Derives 50% or more of annual revenues from selling or sharing consumers' personal information (§ 1798.140(d)(1)(C))"),
        ),
        exemptions=[
            ExemptionRule(exemption_id="CA-HIPAA-CMIA-PHI", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["phi", "cmia_medical_information"], carve_out_statute="Cal. Civ. Code § 1798.146(a)",
                          description="PHI collected by HIPAA covered entities/business associates and medical information governed by CMIA are exempt; providers/CEs are exempt to the extent they treat other patient information like PHI. De-identified patient information must meet § 1798.146(a)(4) and contract terms (§ 1798.148)."),
            ExemptionRule(exemption_id="CA-GLBA-FCRA", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["nonpublic_personal_information", "consumer_report_data"], carve_out_statute="Cal. Civ. Code § 1798.145(e), (d)",
                          description="Data subject to GLBA/CalFIPA and FCRA-regulated activity is exempt (data-level; the § 1798.150 breach private right of action still applies)."),
            ExemptionRule(exemption_id="CA-CLINICAL-TRIALS", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["common_rule_research_data", "ich_gcp_clinical_trial_data"], carve_out_statute="Cal. Civ. Code § 1798.146(a)(3)",
                          description="Information collected in clinical trials subject to the Common Rule/ICH GCP/FDA protections."),
            ExemptionRule(exemption_id="CA-NONPROFIT", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["nonprofit", "government_agency"], carve_out_statute="Cal. Civ. Code § 1798.140(d)",
                          description="Only for-profit 'businesses' are covered; nonprofits and government agencies are outside scope (unless controlled by/sharing branding with a covered business)."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="CCPA-1798.175", preempts_or_yields="concurrent_with", target_regulation_id="US-CA-CMIA",
                           scope_condition="Conflicting California laws", description="Where CCPA conflicts with other California law, the law affording the greatest privacy protection controls (§ 1798.175)."),
            PreemptionRule(rule_id="CCPA-1798.180", preempts_or_yields="preempts", target_regulation_id="US-CA-LOCAL",
                           scope_condition="Local ordinances on collection/sale of consumer PI", description="CCPA preempts city/county privacy ordinances (§ 1798.180)."),
        ],
        organization_types=["private", "business", "service_provider", "contractor", "third_party"],
        industry_sectors=["all"],
        data_subject_categories=["consumers", "households", "employees", "job_applicants", "contractors", "b2b_contacts", "children", "teens"],
        data_categories=["personal_information", "sensitive_personal_information", "precise_geolocation", "biometric_data", "health_data", "neural_data", "children_data"],
        processing_activities=["sale", "sharing_for_cross_context_behavioral_advertising", "sensitive_pi_use", "profiling", "ai_or_admt", "employee_monitoring"],
        required_actions=[
            "Provide Notice at Collection and a comprehensive privacy policy updated at least every 12 months (§ 1798.100, § 1798.130(a)(5))",
            "Honor rights to know/access, delete, correct, and data portability (§§ 1798.100-1798.110, 1798.106)",
            "Provide 'Do Not Sell or Share My Personal Information' link and honor opt-out within 15 business days (§ 1798.120, § 1798.135; Regs § 7026)",
            "Provide 'Limit the Use of My Sensitive Personal Information' link where sensitive PI is used beyond § 7027(m) purposes (§ 1798.121)",
            "Honor opt-out preference signals (Global Privacy Control) as a valid request to opt out (Regs § 7025)",
            "Obtain opt-in consent before selling/sharing PI of consumers under 16 (parental consent under 13) (§ 1798.120(c))",
            "Acknowledge rights requests within 10 business days (Regs § 7021)",
            "Execute service provider/contractor/third-party contracts with § 1798.100(d) and Regs § 7051/§ 7053 terms",
            "Apply data minimization and purpose limitation reasonably necessary and proportionate (§ 1798.100(c); Regs § 7002)",
            "Avoid dark patterns; symmetry in choice for consent (Regs § 7004)",
            "Maintain reasonable security procedures (§ 1798.100(e), § 1798.150)",
            "Maintain records of consumer requests for 24 months (Regs § 7101); businesses handling PI of 10M+ consumers must publish request metrics (§ 7102)",
            "Conduct risk assessments for significant-risk processing (selling/sharing, sensitive PI, ADMT for significant decisions, AI training) per Regs §§ 7150-7157",
            "Complete annual independent cybersecurity audit when meeting § 7120 thresholds, phased certification deadlines April 1, 2028-2030",
            "Train personnel handling consumer inquiries (Regs § 7100)",
        ],
        required_assessments=["CCPA Risk Assessment (Regs §§ 7150-7157)", "Cybersecurity Audit (Regs §§ 7120-7124)", "Financial incentive valuation (Regs § 7016)"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            rights_request_day_type="calendar_days",
            rights_request_extension_days=45,
            identity_verification_required=True,
            breach_regulator_text="See US-CA-BREACH",
            breach_individual_text="See US-CA-BREACH",
            cure_period_days=None,
            record_retention_years=2,
        ),
        notification_requirements=[
            "Rights to know/delete/correct: respond within 45 calendar days, one 45-day extension with notice (90 total) (§ 1798.130(a)(2))",
            "Acknowledgement: within 10 business days (Regs § 7021(a))",
            "Opt-out of sale/sharing & limit requests: comply within 15 business days (Regs §§ 7026(f), 7027(g))",
            "Risk assessment attestation and summary submission to CalPrivacy beginning April 1, 2028 for assessments conducted in 2026-2027",
            "No statutory cure period since CPRA (administrative discretion only); fines up to $2,663 per violation / $7,988 intentional or minors (CPI-adjusted 2025)",
            "Private right of action for data breaches resulting from failure to maintain reasonable security: $107-$799 per consumer per incident (CPI-adjusted) with 30-day cure notice (§ 1798.150)",
        ],
        required_evidence=["Privacy policy (12-month review)", "Notice at collection", "DSAR and opt-out request logs (24 months)", "GPC signal handling evidence", "Service provider contracts", "Risk assessments", "Cybersecurity audit reports", "Training records"],
        approval_requirements=["Executive/board review of risk assessments (signed by highest-ranking executive responsible)", "Counsel approval of financial incentive programs"],
        competent_regulator="California Privacy Protection Agency (CalPrivacy) & California Attorney General",
        domain_category="privacy",
    ))

    regs.append(_state(
        regulation_id="US-CA-CMIA",
        jurisdiction_id="US-CA",
        legal_authority="California legislature; enforced by Attorney General, district attorneys, CDPH and private plaintiffs",
        legal_instrument="Confidentiality of Medical Information Act",
        official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=CIV&division=1.&title=&part=2.6.",
        article_or_section="Cal. Civ. Code §§ 56-56.37; Cal. Health & Safety Code § 1280.15",
        effective_date=date(1981, 1, 1),
        applicability_conditions={
            "subject_locations_any": ["US-CA"],
            "organization_types_any": ["healthcare_covered_entity", "business_associate", "health_information_custodian", "private"],
            "data_categories_any": ["medical_information", "health_information", "phi", "reproductive_health_data", "mental_health_app_data"],
            "gate_logic": "org_or_data",
            "notes": (
                "Applies to providers of health care, health care service plans, contractors, employers receiving medical "
                "information, and businesses offering software/hardware (incl. mental health and reproductive/sexual health "
                "digital services) designed to maintain medical information for the consumer's management or diagnosis "
                "(§ 56.06, as amended by AB 2089 (2022) and AB 254 (2023)). AB 352 (2024) requires segregation and access "
                "controls for sensitive services data in EHRs (compliance July 1, 2024 / Jan 1, 2026 for certain EHR features)."
            ),
        },
        exemptions=[
            ExemptionRule(exemption_id="CMIA-PERMITTED-DISCLOSURES", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["treatment", "payment", "court_order", "public_health_reporting"], carve_out_statute="Cal. Civ. Code § 56.10(b)-(c)",
                          description="Compelled and permitted disclosures without authorization."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="CMIA-HIPAA-MORE-STRINGENT", preempts_or_yields="concurrent_with", target_regulation_id="US-FED-HIPAA-PRIVACY",
                           scope_condition="CMIA more stringent than HIPAA", description="CMIA survives HIPAA preemption as more stringent state law (45 CFR § 160.203(b))."),
        ],
        organization_types=["healthcare_covered_entity", "business_associate", "private"],
        industry_sectors=["healthcare", "digital_health", "health_apps", "employers"],
        data_subject_categories=["patients", "consumers", "employees"],
        data_categories=["medical_information", "reproductive_health_data", "gender_affirming_care_data", "mental_health_data"],
        processing_activities=["disclosure", "marketing", "app_based_health_services", "ehr_management"],
        required_actions=[
            "Obtain written authorization meeting § 56.11 requirements before disclosing medical information except as permitted by § 56.10",
            "Do not use medical information for marketing without authorization (§ 56.10(d))",
            "Maintain, store and dispose of medical information in a manner preserving confidentiality (§ 56.101)",
            "Employers: establish procedures to protect confidentiality of employee medical information (§ 56.20)",
            "Restrict disclosure of reproductive/abortion and gender-affirming care information to out-of-state law enforcement and subpoenas (§ 56.108, § 56.109)",
            "Licensed clinics/health facilities: report unauthorized access/use/disclosure to CDPH and the affected patient within 15 business days of detection (H&S Code § 1280.15)",
        ],
        required_assessments=["CMIA applicability review for digital health services", "Sensitive services EHR segmentation review (AB 352)"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=True,
            breach_regulator_days=15,
            breach_regulator_text="Licensed clinics/health facilities: CDPH within 15 business days after detection of unlawful or unauthorized access, use or disclosure (H&S Code § 1280.15)",
            breach_individual_notification_days=15,
            breach_individual_text="Affected patient or representative within 15 business days after detection (H&S Code § 1280.15)",
        ),
        notification_requirements=["CDPH + patient: 15 business days (H&S § 1280.15)", "Nominal damages $1,000 per patient without proof of actual damages (§ 56.36(b)); administrative fines up to $25,000 per violation (§ 56.36(c))"],
        required_evidence=["Signed authorizations", "Disclosure logs", "Access audit trails", "CDPH incident reports"],
        approval_requirements=["Privacy Officer approval of non-routine disclosures"],
        competent_regulator="California Attorney General; California Department of Public Health (H&S § 1280.15); local district attorneys",
        domain_category="health_privacy",
    ))

    regs.append(_state(
        regulation_id="US-CA-ADMT",
        jurisdiction_id="US-CA",
        legal_authority="California Privacy Protection Agency (CalPrivacy) under Cal. Civ. Code § 1798.185(a)(15)-(16)",
        legal_instrument="CCPA Regulations on Automated Decisionmaking Technology, Risk Assessments and Cybersecurity Audits",
        official_source_url="https://cppa.ca.gov/regulations/ccpa_updates.html",
        article_or_section="Cal. Code Regs. tit. 11, §§ 7200-7222 (ADMT), §§ 7150-7157 (risk assessment), §§ 7120-7124 (cybersecurity audit)",
        effective_date=date(2026, 1, 1),
        transition_period_end=date(2027, 1, 1),
        applicability_conditions={
            "subject_locations_any": ["US-CA"],
            "activity_flags_any": ["involves_ai_or_admt"],
            "gate_logic": "org_and_data",
            "notes": (
                "Applies to CCPA 'businesses' using ADMT to make a significant decision concerning a consumer (financial or "
                "lending services, housing, education enrollment/opportunity, employment or independent-contracting "
                "opportunities/compensation, or healthcare services). Regulations approved by OAL Sept. 23, 2025 and "
                "effective Jan 1, 2026; businesses using ADMT for significant decisions before Jan 1, 2027 must comply with "
                "ADMT requirements by Jan 1, 2027. Risk assessment requirements apply to processing from Jan 1, 2026, with "
                "attestations/summaries due to CalPrivacy by April 1, 2028."
            ),
        },
        thresholds=[],
        exemptions=[
            ExemptionRule(exemption_id="CA-ADMT-HUMAN-INVOLVEMENT", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["human_reviewer_with_authority_and_understanding"], carve_out_statute="Cal. Code Regs. tit. 11, § 7001 (definition of ADMT)",
                          description="Technology is not ADMT where it does not replace or substantially replace human decisionmaking (qualified human reviewer who knows how to interpret output, reviews it and other info, and has authority to change the decision)."),
            ExemptionRule(exemption_id="CA-ADMT-OPT-OUT-EXCEPTIONS", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["human_appeal_offered", "admission_acceptance_hiring_with_accuracy_safeguards", "work_allocation_with_safeguards"], carve_out_statute="Cal. Code Regs. tit. 11, § 7221(b)",
                          description="Opt-out need not be offered where a human appeal right is provided or for certain admission/hiring/allocation uses with non-discrimination safeguards."),
        ],
        preemption_rules=[],
        organization_types=["private", "business"],
        industry_sectors=["financial_services", "housing", "education", "employment", "healthcare", "hr_tech"],
        data_subject_categories=["consumers", "employees", "job_applicants", "students"],
        data_categories=["personal_information", "sensitive_personal_information"],
        processing_activities=["ai_or_admt", "significant_decision", "automated_employment_decision", "ai_model_training", "profiling"],
        required_actions=[
            "Provide a Pre-use Notice describing the ADMT's purpose, logic, outputs, and consumer rights before use for a significant decision (§ 7220)",
            "Offer a right to opt out of ADMT for significant decisions unless an exception applies (§ 7221)",
            "Honor ADMT access requests explaining purpose, logic and how output was used (§ 7222)",
            "Conduct and document a risk assessment before initiating significant-risk processing; review at least every 3 years and update within 45 days of material change (§§ 7150-7155)",
            "Submit risk assessment information and executive attestation to CalPrivacy (first due April 1, 2028) (§ 7157)",
            "Provide service providers/contractors with facts necessary to complete risk assessments (§ 7153)",
        ],
        required_assessments=["CCPA Risk Assessment for ADMT/significant-risk processing (§ 7152)", "ADMT pre-use notice review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            rights_request_extension_days=45,
            identity_verification_required=True,
            breach_regulator_text="See US-CA-BREACH",
            breach_individual_text="See US-CA-BREACH",
            record_retention_years=5,
        ),
        notification_requirements=["Pre-use notice prior to processing", "ADMT opt-out processed within 15 business days", "Risk assessments retained for duration of processing or 5 years after completion, whichever is longer"],
        required_evidence=["Pre-use notice", "Opt-out request log", "Risk assessment documents with executive sign-off", "ADMT access response templates", "CalPrivacy submissions"],
        approval_requirements=["Highest-ranking executive responsible for risk assessment compliance attests under penalty of perjury", "Human review of ADMT significant decisions where relying on human appeal exception"],
        competent_regulator="California Privacy Protection Agency (CalPrivacy)",
        domain_category="ai_governance",
    ))

    regs.append(_state(
        regulation_id="US-CA-DELETE-ACT",
        jurisdiction_id="US-CA",
        legal_authority="California Privacy Protection Agency (CalPrivacy)",
        legal_instrument="California Delete Act (SB 362) — Data Broker Registration and Delete Request and Opt-out Platform (DROP)",
        official_source_url="https://cppa.ca.gov/data_brokers/",
        article_or_section="Cal. Civ. Code §§ 1798.99.80-1798.99.89; Cal. Code Regs. tit. 11, §§ 7600-7604 (registration), §§ 7610-7616 (DROP)",
        effective_date=date(2024, 1, 1),
        applicability_conditions={
            "subject_locations_any": ["US-CA"],
            "industry_sectors_any": ["data_broker", "adtech", "people_search", "marketing_data"],
            "gate_logic": "org_only",
            "notes": (
                "Applies to data brokers: businesses that knowingly collect and sell to third parties the personal information "
                "of consumers with whom they do not have a direct relationship (§ 1798.99.80(c)). Registration annually by "
                "Jan 31. Consumers may submit DROP deletion requests from Jan 1, 2026; brokers must access DROP and process "
                "deletion requests beginning Aug 1, 2026 and at least every 45 days thereafter. Independent compliance audits "
                "every 3 years starting Jan 1, 2028."
            ),
        },
        thresholds=[],
        exemptions=[
            ExemptionRule(exemption_id="CA-DELETE-ACT-DIRECT-RELATIONSHIP", exemption_type="entity_level", condition_field="processing_activities",
                          condition_values=["first_party_direct_relationship_only"], carve_out_statute="Cal. Civ. Code § 1798.99.80(c)",
                          description="Entities selling only data of consumers with whom they have a direct relationship are not data brokers."),
            ExemptionRule(exemption_id="CA-DELETE-ACT-FCRA-GLBA-HIPAA", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["consumer_reporting_agency", "financial_institution", "healthcare_covered_entity"], carve_out_statute="Cal. Civ. Code § 1798.99.80(c)(1)-(3)",
                          description="Entities to the extent covered by FCRA, GLBA, or the Insurance Information and Privacy Protection Act are excluded."),
        ],
        preemption_rules=[],
        organization_types=["private", "data_broker"],
        industry_sectors=["data_broker"],
        data_subject_categories=["consumers"],
        data_categories=["personal_information", "precise_geolocation", "reproductive_health_data", "minors_data"],
        processing_activities=["data_brokering", "sale_of_personal_data"],
        required_actions=[
            "Register with CalPrivacy annually between Jan 1 and Jan 31 and pay the registration fee; disclose whether data of minors, precise geolocation, reproductive health data is collected (§ 1798.99.82)",
            "Access the DROP at least once every 45 days and process all consumer deletion requests, deleting all non-exempt PI (§ 1798.99.86(c))",
            "After deletion, do not sell or share new PI of the consumer and direct service providers/contractors to delete (§ 1798.99.86(c)(1)(B))",
            "Report DROP processing status to CalPrivacy",
            "Undergo an independent audit every 3 years starting Jan 1, 2028 and submit report on request (§ 1798.99.86(e))",
            "Publish annual metrics on CCPA requests received/complied with in privacy policy (§ 1798.99.85)",
        ],
        required_assessments=["Data broker status determination", "Triennial independent compliance audit"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            identity_verification_required=False,
            breach_regulator_text="See US-CA-BREACH",
            breach_individual_text="See US-CA-BREACH",
            record_retention_years=3,
        ),
        notification_requirements=["Annual registration Jan 1-31", "DROP polling every 45 days from Aug 1, 2026", "Administrative fines $200 per day for failure to register; $200 per deletion request per day for failure to delete"],
        required_evidence=["CalPrivacy registration receipt", "DROP processing logs", "Deletion confirmations from service providers", "Audit reports"],
        approval_requirements=["Counsel approval of data broker status determination"],
        competent_regulator="California Privacy Protection Agency (CalPrivacy)",
        domain_category="privacy",
    ))

    regs.append(_state(
        regulation_id="US-CA-AI-TRANSPARENCY",
        jurisdiction_id="US-CA",
        legal_authority="California legislature; enforced by Attorney General, city attorneys and county counsel",
        legal_instrument="California Generative AI Training Data Transparency Act (AB 2013) & California AI Transparency Act (SB 942, as amended by AB 853)",
        official_source_url="https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB942",
        article_or_section="Cal. Civ. Code §§ 3110-3111 (AB 2013); Cal. Bus. & Prof. Code §§ 22757-22757.6 (SB 942 / AB 853)",
        effective_date=date(2026, 1, 1),
        applicability_conditions={
            "subject_locations_any": ["US-CA"],
            "activity_flags_any": ["involves_ai_or_admt"],
            "industry_sectors_any": ["ai_developer", "generative_ai", "technology"],
            "gate_logic": "org_and_data",
            "notes": (
                "AB 2013: developers of generative AI systems or services released on or after Jan 1, 2022 and made available "
                "to Californians must publish high-level training data documentation on or before Jan 1, 2026 and before each "
                "new release/substantial modification. SB 942: 'covered providers' (GenAI systems with over 1,000,000 monthly "
                "visitors/users publicly accessible in California) must provide a free AI detection tool and offer manifest "
                "and embed latent disclosures in AI-generated image, video and audio content; operative date delayed to "
                "Aug 2, 2026 by AB 853, which also adds obligations for large online platforms (Jan 1, 2027) and capture "
                "device manufacturers (Jan 1, 2028)."
            ),
        },
        thresholds=_thr(
            ("monthly_active_users", ">", 1000000, "OR", "SB 942 covered provider: generative AI system with over 1,000,000 monthly visitors or users publicly accessible within California"),
        ),
        exemptions=[
            ExemptionRule(exemption_id="CA-AB2013-SECURITY-DEFENSE", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["security_and_integrity_only", "aircraft_operation", "national_security_federal_only"], carve_out_statute="Cal. Civ. Code § 3111(b)",
                          description="AB 2013 documentation not required for GenAI systems solely for security/integrity, aircraft operation in national airspace, or national security/defense made available only to federal entities."),
            ExemptionRule(exemption_id="CA-SB942-NON-USER-GENERATED", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["video_game_or_tv_or_streaming_non_user_generated"], carve_out_statute="Cal. Bus. & Prof. Code § 22757.6",
                          description="SB 942 does not apply to products that exclusively provide non-user-generated video game, television, streaming, movie or interactive experiences."),
        ],
        preemption_rules=[],
        organization_types=["private", "ai_developer"],
        industry_sectors=["generative_ai", "technology"],
        data_subject_categories=["consumers"],
        data_categories=["training_data", "personal_information", "synthetic_media"],
        processing_activities=["ai_model_training", "generative_ai_output", "ai_or_admt"],
        required_actions=[
            "Publish training data documentation: sources/owners, dataset purpose, number of data points, data types, IP/copyright status, whether personal information or aggregate consumer information is included, licensing/purchase, cleaning/processing, collection time period, synthetic data use (Civ. Code § 3111(a))",
            "Update documentation before each new release or substantial modification",
            "Covered providers: make available a free, publicly accessible AI detection tool (B&P § 22757.2)",
            "Covered providers: offer users the option to include a manifest disclosure and embed latent disclosures (provider name, system name/version, creation timestamp, unique identifier) in AI-generated image, video and audio content (B&P § 22757.3)",
            "Contractually require licensees to maintain latent disclosure capability; revoke license within 96 hours of discovering removal (B&P § 22757.3(c))",
        ],
        required_assessments=["Training data provenance and PI inclusion review", "Content provenance (C2PA/latent disclosure) implementation review"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False, breach_regulator_text="Not applicable", breach_individual_text="Not applicable"),
        notification_requirements=["SB 942 civil penalty $5,000 per violation per day", "License revocation within 96 hours on discovery of disclosure removal"],
        required_evidence=["Published training data documentation", "AI detection tool availability", "Latent disclosure implementation evidence", "Licensee contracts"],
        approval_requirements=["Counsel review of training data disclosure prior to publication"],
        competent_regulator="California Attorney General; city attorneys; county counsel",
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        deployment_status=DeploymentStatus.TESTED,
        domain_category="ai_governance",
    ))
    return regs


# ---------------------------------------------------------------------------
# 4. COLORADO (CPA + AI Act)
# ---------------------------------------------------------------------------

def _colorado() -> List[CanonicalRegulation]:
    cpa = _comprehensive(
        "US-CO-CPA", "US-CO",
        "Colorado Privacy Act & Colorado Privacy Act Rules",
        "Colo. Rev. Stat. §§ 6-1-1301 to 6-1-1314; 4 CCR 904-3",
        "https://coag.gov/resources/colorado-privacy-act/",
        date(2023, 7, 1),
        _thr(
            ("consumer_records_count", ">=", 100000, "OR", "Controls or processes personal data of 100,000 or more Colorado consumers during a calendar year"),
            ("consumer_records_count", ">=", 25000, "OR_B", "Controls or processes personal data of 25,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 0, "OR_B", "... derives revenue or receives a discount on goods/services from the sale of personal data"),
        ),
        _std_exemptions("CO", glba="entity", hipaa="data", nonprofit_exempt=False, higher_ed_exempt=False),
        appeal_days=45, cure_days=None, uoom=True,
        cure_note="60-day cure period expired Jan 1, 2025; appeals decided within 45 days (+60-day extension)",
        extra_actions=[
            "Obtain opt-in consent per Rule 7 (refresh consent annually for sensitive data inferences where required)",
            "Biometric identifiers (HB 24-1130, effective July 1, 2025): adopt written retention/deletion policy, incident response protocol, and obtain consent — applies to any controller processing biometrics regardless of volume thresholds",
            "Minors (SB 24-041, effective Oct 1, 2025): heightened duty of care; consent before targeted advertising, sale or profiling of known minors under 18; no precise geolocation without consent",
            "Maintain data protection assessments for 3 years after processing ends (Rule 8.08)",
        ],
        notes="Applies to controllers conducting business in Colorado or targeting Colorado residents. Nonprofits are covered. Universal opt-out mechanism (GPC) mandatory since July 1, 2024.",
    )
    ai_act = _state(
        regulation_id="US-CO-AI-ACT",
        jurisdiction_id="US-CO",
        legal_authority="Colorado legislature; exclusive enforcement by Colorado Attorney General",
        legal_instrument="Colorado Artificial Intelligence Act — Consumer Protections for Interactions with Artificial Intelligence Systems (SB 24-205, as amended by SB 25B-004)",
        official_source_url="https://leg.colorado.gov/bills/sb24-205",
        article_or_section="Colo. Rev. Stat. §§ 6-1-1701 to 6-1-1707",
        effective_date=date(2026, 6, 30),
        applicability_conditions={
            "subject_locations_any": ["US-CO"],
            "activity_flags_any": ["involves_ai_or_admt"],
            "gate_logic": "org_and_data",
            "notes": (
                "Applies to developers and deployers of 'high-risk AI systems' that make, or are a substantial factor in "
                "making, consequential decisions (education, employment, financial/lending, essential government services, "
                "healthcare, housing, insurance, legal services). Original Feb 1, 2026 operative date was delayed to "
                "June 30, 2026 by SB 25B-004 (Aug. 2025 special session). The 2026 regular session considered further "
                "amendment/replacement — counsel must confirm the operative date and current text before relying on this "
                "pack as a live obligation. Until confirmed, treat as preparation obligations."
            ),
        },
        thresholds=_thr(
            ("employee_count", "<", 50, "AND", "Deployer small-business relief (§ 6-1-1703(6)): fewer than 50 FTEs, does not train the system with its own data, uses system for disclosed intended uses, and makes developer impact assessment available — exempt from risk management program, impact assessment and website notice duties"),
        ),
        exemptions=[
            ExemptionRule(exemption_id="CO-AI-HIPAA-NONHIGH-RISK", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["hipaa_covered_entity_ai_recommendation_requiring_provider_action"], carve_out_statute="Colo. Rev. Stat. § 6-1-1705(4)",
                          description="HIPAA covered entities providing AI-generated healthcare recommendations that require a provider to take action are exempt."),
            ExemptionRule(exemption_id="CO-AI-FED-APPROVED", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["fda_faa_approved_system", "federal_standard_equivalent"], carve_out_statute="Colo. Rev. Stat. § 6-1-1705(2)",
                          description="Systems approved by federal agencies (e.g., FDA, FAA) or compliant with equivalent/stricter federal standards."),
            ExemptionRule(exemption_id="CO-AI-REGULATED-FI-INSURERS", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["financial_institution", "insurer_subject_to_crs_10-3-1104.9"], carve_out_statute="Colo. Rev. Stat. § 6-1-1705(5)-(6)",
                          description="Banks/credit unions subject to substantially equivalent prudential AI guidance and insurers subject to C.R.S. § 10-3-1104.9 are deemed compliant."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="CO-AI-CPA-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="US-CO-CPA",
                           scope_condition="Profiling in furtherance of decisions producing legal or similarly significant effects",
                           description="CPA profiling opt-out and data protection assessment duties apply now; AI Act obligations layer on top once operative."),
        ],
        organization_types=["private", "ai_developer", "ai_deployer"],
        industry_sectors=["employment", "financial_services", "insurance", "healthcare", "housing", "education", "legal_services", "government_services"],
        data_subject_categories=["consumers", "job_applicants", "employees"],
        data_categories=["personal_data", "sensitive_data"],
        processing_activities=["ai_or_admt", "consequential_decision", "high_risk_ai_system"],
        required_actions=[
            "Developers and deployers: use reasonable care to protect consumers from known or reasonably foreseeable risks of algorithmic discrimination (§§ 6-1-1702(1), 6-1-1703(1))",
            "Developers: provide deployers documentation on intended uses, training data, limitations, evaluation and mitigation; publish a public statement of high-risk systems (§ 6-1-1702(2)-(4))",
            "Developers: disclose known or reasonably foreseeable algorithmic discrimination risks to the AG and known deployers within 90 days of discovery (§ 6-1-1702(5))",
            "Deployers: implement a risk management policy and program aligned to NIST AI RMF / ISO/IEC 42001 (§ 6-1-1703(2))",
            "Deployers: complete an impact assessment before deployment, annually, and within 90 days of intentional and substantial modification (§ 6-1-1703(3))",
            "Deployers: notify consumers before a consequential decision; provide statement of reasons, correction opportunity and appeal with human review for adverse decisions (§ 6-1-1703(4))",
            "Deployers: publish website statement of high-risk systems deployed and risk management (§ 6-1-1703(5))",
            "Deployers: notify AG within 90 days of discovering algorithmic discrimination (§ 6-1-1703(7))",
            "Any person deploying consumer-facing AI: disclose to consumers they are interacting with AI unless obvious (§ 6-1-1704)",
            "Preparation (now): inventory AI systems used in consequential decisions; map to CPA profiling DPAs; adopt NIST AI RMF for affirmative defense (§ 6-1-1706(3))",
        ],
        required_assessments=["Colorado High-Risk AI Impact Assessment (§ 6-1-1703(3))", "Algorithmic discrimination testing", "CPA Data Protection Assessment for profiling"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_appeal_days=None,
            identity_verification_required=False,
            breach_regulator_days=90,
            breach_regulator_text="Attorney General within 90 days after discovery of algorithmic discrimination caused by a high-risk AI system",
            breach_individual_text="Not applicable (consequential decision notices required pre-decision and on adverse outcome)",
            record_retention_years=3,
        ),
        notification_requirements=["AG notice of algorithmic discrimination: 90 days", "Impact assessments retained for at least 3 years after final deployment", "Violations are deceptive trade practices under the Colorado Consumer Protection Act (AG enforcement only; no private right of action)"],
        required_evidence=["AI system inventory", "Risk management policy", "Impact assessments", "Consumer notices and adverse-decision explanations", "Developer documentation packages", "NIST AI RMF / ISO 42001 alignment evidence"],
        approval_requirements=["Executive approval of risk management program", "Counsel confirmation of operative date and current statutory text"],
        competent_regulator="Colorado Attorney General",
        regulatory_status=RegulatoryStatus.ENACTED_NOT_EFFECTIVE,
        deployment_status=DeploymentStatus.TESTED,
        legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
        domain_category="ai_governance",
    )
    return [cpa, ai_act]


# ---------------------------------------------------------------------------
# 5. TEXAS (TDPSA, CUBI, HB 300)
# ---------------------------------------------------------------------------

def _texas() -> List[CanonicalRegulation]:
    tdpsa = _comprehensive(
        "US-TX-TDPSA", "US-TX",
        "Texas Data Privacy and Security Act",
        "Tex. Bus. & Com. Code ch. 541 (§§ 541.001-541.205)",
        "https://statutes.capitol.texas.gov/Docs/BC/htm/BC.541.htm",
        date(2024, 7, 1),
        _thr(
            ("conducts_business_in_state", "==", True, "AND", "Conducts business in Texas or produces products/services consumed by Texas residents"),
            ("processes_or_sells_personal_data", "==", True, "AND", "Processes or engages in the sale of personal data"),
            ("is_sba_small_business", "==", False, "AND", "Is not a small business as defined by the U.S. SBA (small businesses must still obtain consent before selling sensitive data, § 541.107)"),
        ),
        _std_exemptions("TX", glba="entity", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=True),
        cure_days=30, uoom=True,
        cure_note="30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
        extra_actions=[
            "Post the notice 'NOTICE: We may sell your sensitive personal data.' and/or 'NOTICE: We may sell your biometric personal data.' where applicable (§ 541.102(b)-(c))",
            "Honor universal opt-out mechanisms beginning Jan 1, 2025 (§ 541.055(e))",
            "Data brokers: register with the Texas Secretary of State under Tex. Bus. & Com. Code ch. 509",
        ],
        notes="No revenue or volume threshold; applies to any non-small business conducting business in Texas. Small-business exemption does not cover sale of sensitive data without consent.",
    )
    cubi = _state(
        regulation_id="US-TX-CUBI",
        jurisdiction_id="US-TX",
        legal_authority="Texas legislature; exclusive enforcement by Texas Attorney General",
        legal_instrument="Capture or Use of Biometric Identifier Act",
        official_source_url="https://statutes.capitol.texas.gov/Docs/BC/htm/BC.503.htm",
        article_or_section="Tex. Bus. & Com. Code § 503.001",
        effective_date=date(2009, 9, 1),
        applicability_conditions={
            "subject_locations_any": ["US-TX"],
            "activity_flags_any": ["involves_biometrics"],
            "data_categories_any": ["biometric_data", "retina_scan", "iris_scan", "fingerprint", "voiceprint", "face_geometry"],
            "gate_logic": "data_only",
            "notes": "Applies to any person capturing biometric identifiers of individuals for a commercial purpose. Texas AG secured a $1.4B settlement with Meta (2024) and $1.375B with Google (2025) under CUBI/DTPA.",
        },
        exemptions=[
            ExemptionRule(exemption_id="TX-CUBI-NON-COMMERCIAL", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["non_commercial_purpose", "ai_training_not_used_to_identify"], carve_out_statute="Tex. Bus. & Com. Code § 503.001(e) (as amended by HB 149, 2025)",
                          description="Capture not for a commercial purpose is outside scope; HB 149 (TRAIGA, eff. Jan 1, 2026) excludes training/development of AI systems unless used to uniquely identify individuals."),
        ],
        preemption_rules=[],
        organization_types=["private"],
        industry_sectors=["all"],
        data_subject_categories=["individuals", "employees", "consumers"],
        data_categories=["biometric_data"],
        processing_activities=["biometric_capture", "facial_recognition", "voice_identification"],
        required_actions=[
            "Inform the individual before capturing a biometric identifier and obtain consent (§ 503.001(b))",
            "Do not sell, lease or otherwise disclose biometric identifiers except for identification in disappearance/death, completing a financial transaction the individual authorized, as required by law, or to law enforcement under warrant (§ 503.001(c)(1))",
            "Store, transmit and protect biometric identifiers using reasonable care, at least as protective as other confidential information (§ 503.001(c)(2))",
            "Destroy biometric identifiers within a reasonable time, but not later than the first anniversary of the date the purpose for collection expires (employment: upon termination of employment relationship) (§ 503.001(c)(3))",
        ],
        required_assessments=["Biometric data inventory and retention review"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False, breach_regulator_text="See US-TX-BREACH", breach_individual_text="See US-TX-BREACH", record_retention_years=1),
        notification_requirements=["Civil penalty up to $25,000 per violation (AG enforcement only; no private right of action)"],
        required_evidence=["Pre-capture notice", "Consent records", "Biometric retention/destruction schedule and destruction logs"],
        approval_requirements=["Counsel approval before deploying facial recognition or voiceprint features"],
        competent_regulator="Texas Office of the Attorney General",
        domain_category="biometric_privacy",
    )
    hb300 = _state(
        regulation_id="US-TX-HB300-TMRPA",
        jurisdiction_id="US-TX",
        legal_authority="Texas legislature (HB 300, 2011); enforced by Texas Attorney General and state licensing agencies",
        legal_instrument="Texas Medical Records Privacy Act (as amended by HB 300)",
        official_source_url="https://statutes.capitol.texas.gov/Docs/HS/htm/HS.181.htm",
        article_or_section="Tex. Health & Safety Code ch. 181 (§§ 181.001-181.207); Tex. Bus. & Com. Code § 521.053",
        effective_date=date(2012, 9, 1),
        applicability_conditions={
            "subject_locations_any": ["US-TX"],
            "data_categories_any": ["phi", "health_information", "medical_records", "ehr"],
            "gate_logic": "data_only",
            "notes": (
                "'Covered entity' is broader than HIPAA: any person who assembles, collects, analyzes, uses, evaluates, "
                "stores or transmits PHI for commercial, financial or professional gain, including business associates, "
                "health information exchanges, health care practitioners, schools, and employees/agents (§ 181.001(b)(2)). "
                "Applies regardless of HIPAA status."
            ),
        },
        exemptions=[
            ExemptionRule(exemption_id="TX-HB300-HIPAA-COMPLIANCE", exemption_type="activity_level", condition_field="processing_activities",
                          condition_values=["hipaa_permitted_tpo_disclosure"], carve_out_statute="Tex. Health & Safety Code § 181.154(c)",
                          description="Electronic disclosure authorization not required for disclosures for treatment, payment, health care operations, insurance/HMO functions, or as otherwise authorized/required by law."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="TX-HB300-MORE-STRINGENT", preempts_or_yields="concurrent_with", target_regulation_id="US-FED-HIPAA-PRIVACY",
                           scope_condition="Texas requirements more stringent than HIPAA", description="Applies concurrently with HIPAA as more stringent state law (shorter EHR access, mandatory training, sale prohibition)."),
        ],
        organization_types=["healthcare_covered_entity", "business_associate", "private", "educational_institution"],
        industry_sectors=["healthcare", "health_it", "health_insurance", "digital_health"],
        data_subject_categories=["patients"],
        data_categories=["phi", "ehr", "medical_records"],
        processing_activities=["ehr_access", "electronic_disclosure", "sale_of_phi", "marketing", "workforce_training"],
        required_actions=[
            "Provide electronic health records to the patient in electronic form not later than the 15th business day after receiving a written request (§ 181.102)",
            "Train employees on state and federal law concerning PHI, tailored to their scope of employment, within 90 days of hire and as necessary when laws change; obtain signed acknowledgment of training and retain (§ 181.101)",
            "Do not sell PHI (§ 181.153) and do not use or disclose PHI for marketing without authorization (§ 181.152)",
            "Provide notice to individuals that PHI is subject to electronic disclosure (posting or written notice) and obtain authorization for electronic disclosures outside TPO/insurance/legal purposes (§ 181.154)",
            "Notify Texas residents of breaches of sensitive personal information (incl. health info) within 60 days and the AG within 30 days if 250+ residents affected (Tex. Bus. & Com. Code § 521.053)",
        ],
        required_assessments=["Texas covered-entity status determination", "Workforce training compliance audit"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=15,
            rights_request_day_type="business_days",
            identity_verification_required=True,
            breach_regulator_days=30,
            breach_regulator_text="Texas Attorney General within 30 days if 250 or more Texas residents affected (Tex. Bus. & Com. Code § 521.053(i))",
            breach_attorney_general_threshold_individuals=250,
            breach_individual_notification_days=60,
            breach_individual_text="Without unreasonable delay and not later than 60 days after determination (Tex. Bus. & Com. Code § 521.053(b))",
            record_retention_years=6,
        ),
        notification_requirements=["EHR access: 15 business days", "Civil penalties from $5,000 (negligent) up to $250,000 (intentional, for financial gain) per violation, capped at $1.5M annually for pattern of violations (§ 181.201)", "Licensing agency disciplinary action and exclusion from state programs possible (§ 181.202-.203)"],
        required_evidence=["EHR request log with response dates", "Training completion records and signed acknowledgments", "Electronic disclosure notice", "Authorizations"],
        approval_requirements=["Privacy Officer approval of electronic disclosures outside TPO"],
        competent_regulator="Texas Office of the Attorney General; Texas Health and Human Services Commission; state licensing boards",
        domain_category="health_privacy",
    )
    return [tdpsa, cubi, hb300]


# ---------------------------------------------------------------------------
# 6. WASHINGTON (MHMDA)
# ---------------------------------------------------------------------------

def _washington() -> List[CanonicalRegulation]:
    return [_state(
        regulation_id="US-WA-MHMDA",
        jurisdiction_id="US-WA",
        legal_authority="Washington legislature; enforced by Washington Attorney General and private plaintiffs under the Consumer Protection Act",
        legal_instrument="Washington My Health My Data Act",
        official_source_url="https://app.leg.wa.gov/RCW/default.aspx?cite=19.373",
        article_or_section="Rev. Code Wash. ch. 19.373 (§§ 19.373.005-19.373.900)",
        effective_date=date(2024, 3, 31),
        applicability_conditions={
            "subject_locations_any": ["US-WA"],
            "data_categories_any": ["consumer_health_data", "health_information", "reproductive_health_data", "gender_affirming_care_data", "biometric_data", "precise_geolocation", "health_inferences"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to any 'regulated entity' (conducts business in WA or targets WA consumers and determines purposes of "
                "processing consumer health data) with no revenue or volume threshold; small businesses (< 100,000 consumers "
                "or < 25,000 + > 50% revenue from consumer health data) had until June 30, 2024. 'Consumer' includes WA "
                "residents and any natural person whose consumer health data is collected in Washington. Covers inferences "
                "derived from non-health data. Private right of action via the Washington CPA (RCW 19.86)."
            ),
        },
        thresholds=[],
        exemptions=[
            ExemptionRule(exemption_id="WA-MHMDA-HIPAA-PHI", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["phi", "hipaa_deidentified_data"], carve_out_statute="RCW 19.373.100",
                          description="PHI under HIPAA and information treated like PHI by covered entities/business associates is exempt (data-level only)."),
            ExemptionRule(exemption_id="WA-MHMDA-GLBA-FCRA-FERPA", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["nonpublic_personal_information", "consumer_report_data", "ferpa_education_records", "part2_sud_records"], carve_out_statute="RCW 19.373.100",
                          description="Data governed by GLBA, FCRA, FERPA, 42 CFR Part 2 and Washington health care information laws."),
            ExemptionRule(exemption_id="WA-MHMDA-GOV", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["government_agency"], carve_out_statute="RCW 19.373.010",
                          description="Government agencies, tribal nations and their contracted service providers processing on their behalf."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="WA-MHMDA-HBNR-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="US-FED-FTC-HBNR",
                           scope_condition="Non-HIPAA consumer health apps", description="Applies concurrently with the FTC Health Breach Notification Rule and FTC Act § 5."),
        ],
        organization_types=["private", "nonprofit", "regulated_entity", "processor"],
        industry_sectors=["digital_health", "health_apps", "wearables", "fitness", "retail_pharmacy", "adtech", "reproductive_health"],
        data_subject_categories=["consumers"],
        data_categories=["consumer_health_data", "reproductive_health_data", "gender_affirming_care_data", "biometric_data", "precise_geolocation"],
        processing_activities=["health_data_collection", "health_data_sharing", "sale_of_health_data", "geofencing", "targeted_advertising"],
        required_actions=[
            "Maintain a separate, prominently linked Consumer Health Data Privacy Policy (RCW 19.373.020)",
            "Obtain separate, affirmative opt-in consent to collect consumer health data beyond what is necessary to provide the requested product/service (RCW 19.373.030(1)(a))",
            "Obtain a separate opt-in consent, distinct from collection consent, to share consumer health data (RCW 19.373.030(1)(b))",
            "Obtain a signed, written, time-limited (1-year) valid authorization before selling consumer health data; retain for 6 years (RCW 19.373.070)",
            "Do not implement a geofence around an entity that provides in-person health care services within 2,000 feet to identify/track consumers, collect consumer health data, or send health-related notifications/ads (RCW 19.373.080)",
            "Honor rights to confirm/access (including list of third parties and affiliates), withdraw consent, and delete (including from archives/backups within 6 months) (RCW 19.373.040)",
            "Notify processors and third parties of deletion requests (RCW 19.373.040(1)(c))",
            "Restrict access to consumer health data to employees/processors necessary for the purpose; maintain reasonable security (RCW 19.373.050)",
            "Bind processors by contract; processors may only process per binding instructions (RCW 19.373.060)",
        ],
        required_assessments=["Consumer health data inventory incl. health inferences", "Geofencing and location-based advertising review"],
        response_deadlines=ResponseDeadlineSpec(
            rights_request_initial_days=45,
            rights_request_extension_days=45,
            rights_request_appeal_days=45,
            identity_verification_required=True,
            breach_regulator_text="See US-WA-BREACH",
            breach_individual_text="See US-WA-BREACH",
            record_retention_years=6,
        ),
        notification_requirements=["Rights requests: 45 days, one 45-day extension", "Appeals: 45 days, with AG contact information on denial", "Deletion from archives/backups within 6 months", "Sale authorizations retained 6 years", "Violations are per se CPA violations with private right of action"],
        required_evidence=["Consumer Health Data Privacy Policy", "Separate collection and sharing consent records", "Valid sale authorizations", "Geofence configuration audits", "Rights request logs", "Processor contracts"],
        approval_requirements=["Counsel approval before sharing or selling consumer health data", "Marketing approval gate for any location-based health advertising"],
        competent_regulator="Washington State Office of the Attorney General",
        domain_category="health_privacy",
    )]


# ---------------------------------------------------------------------------
# 7. ILLINOIS (BIPA)
# ---------------------------------------------------------------------------

def _illinois() -> List[CanonicalRegulation]:
    return [_state(
        regulation_id="US-IL-BIPA",
        jurisdiction_id="US-IL",
        legal_authority="Illinois General Assembly; enforced through private right of action",
        legal_instrument="Biometric Information Privacy Act",
        official_source_url="https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=3004&ChapterID=57",
        article_or_section="740 ILCS 14/1-14/99 (as amended by Public Act 103-0769, effective Aug. 2, 2024)",
        effective_date=date(2008, 10, 3),
        applicability_conditions={
            "subject_locations_any": ["US-IL"],
            "activity_flags_any": ["involves_biometrics"],
            "data_categories_any": ["biometric_data", "retina_scan", "iris_scan", "fingerprint", "voiceprint", "face_geometry", "hand_geometry"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to private entities in possession of biometric identifiers or biometric information of individuals "
                "in Illinois, including employers (timekeeping), retailers and technology vendors. No volume or revenue "
                "threshold. Private right of action without proof of actual harm (Rosenbach v. Six Flags, 2019); claims "
                "accrue per scan but P.A. 103-0769 limits recovery to one violation per person per collection method, and "
                "permits electronic signatures for written release."
            ),
        },
        thresholds=[],
        exemptions=[
            ExemptionRule(exemption_id="IL-BIPA-HEALTHCARE", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["phi", "healthcare_treatment_biometrics"], carve_out_statute="740 ILCS 14/10 (definition of biometric identifier)",
                          description="Information captured from a patient in a health care setting or collected for treatment, payment or operations under HIPAA is excluded (Mosby v. Ingalls, 2023 extends to health care workers' biometrics used for TPO)."),
            ExemptionRule(exemption_id="IL-BIPA-GLBA", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["financial_institution"], carve_out_statute="740 ILCS 14/25(c)",
                          description="Financial institutions subject to Title V of GLBA are exempt."),
            ExemptionRule(exemption_id="IL-BIPA-GOV", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["government_agency"], carve_out_statute="740 ILCS 14/25(e)",
                          description="State/local government agencies and contractors/subcontractors working for them are exempt."),
            ExemptionRule(exemption_id="IL-BIPA-EXCLUDED-ITEMS", exemption_type="data_level", condition_field="data_categories",
                          condition_values=["photographs", "writing_samples", "signatures", "physical_descriptions", "donated_organs", "xray_mri"], carve_out_statute="740 ILCS 14/10",
                          description="Enumerated items excluded from 'biometric identifier'."),
        ],
        preemption_rules=[],
        organization_types=["private", "employer"],
        industry_sectors=["all"],
        data_subject_categories=["employees", "consumers", "customers"],
        data_categories=["biometric_data"],
        processing_activities=["biometric_capture", "facial_recognition", "biometric_timekeeping", "voice_identification", "ai_model_training"],
        required_actions=[
            "Develop and make publicly available a written policy establishing a retention schedule and guidelines for permanent destruction (14/15(a))",
            "Permanently destroy biometric identifiers/information when the initial purpose has been satisfied or within 3 years of the individual's last interaction with the entity, whichever occurs first (14/15(a))",
            "Before collection, inform the subject in writing that biometrics are being collected/stored, the specific purpose and length of term, and obtain a written release (electronic signature permitted) (14/15(b))",
            "Do not sell, lease, trade or otherwise profit from biometric identifiers/information (14/15(c))",
            "Do not disclose or disseminate without consent or other statutory exception (14/15(d))",
            "Store, transmit and protect biometrics using the reasonable standard of care within the industry, at least as protective as other confidential and sensitive information (14/15(e))",
        ],
        required_assessments=["Biometric data inventory and retention schedule review", "Vendor biometric processing assessment"],
        response_deadlines=ResponseDeadlineSpec(identity_verification_required=False, breach_regulator_text="See US-IL-BREACH", breach_individual_text="See US-IL-BREACH", record_retention_years=3),
        notification_requirements=["Liquidated damages: $1,000 per negligent violation or $5,000 per intentional/reckless violation, or actual damages if greater, plus attorneys' fees (14/20)", "Statute of limitations 5 years (Tims v. Black Horse Carriers, 2023)"],
        required_evidence=["Public biometric retention and destruction policy", "Signed written releases (pre-collection)", "Destruction logs", "Vendor contracts prohibiting sale/dissemination"],
        approval_requirements=["Counsel approval before deploying any biometric feature touching Illinois individuals"],
        competent_regulator="Illinois circuit courts (private right of action); Illinois Attorney General (general consumer protection)",
        domain_category="biometric_privacy",
    )]


# ---------------------------------------------------------------------------
# 8. NEW YORK (SHIELD + NYDFS 23 NYCRR 500)
# ---------------------------------------------------------------------------

def _new_york() -> List[CanonicalRegulation]:
    shield = _state(
        regulation_id="US-NY-SHIELD",
        jurisdiction_id="US-NY",
        legal_authority="New York legislature; enforced by New York Attorney General",
        legal_instrument="Stop Hacks and Improve Electronic Data Security (SHIELD) Act",
        official_source_url="https://www.nysenate.gov/legislation/laws/GBS/899-BB",
        article_or_section="N.Y. Gen. Bus. Law §§ 899-aa (breach notification), 899-bb (data security protections)",
        effective_date=date(2020, 3, 21),
        applicability_conditions={
            "subject_locations_any": ["US-NY"],
            "data_categories_any": ["private_information", "personal_information", "biometric_data", "credentials", "ssn", "financial_account"],
            "gate_logic": "data_only",
            "notes": (
                "Applies to any person or business that owns or licenses computerized private information of New York "
                "residents, regardless of whether it conducts business in New York. Small businesses (< 50 employees, "
                "< $3M gross annual revenue in each of last 3 fiscal years, or < $5M year-end total assets) may scale "
                "safeguards to size and complexity. Breach notice amended Dec. 2024: 30-day outer deadline and NYDFS added "
                "as notified agency."
            ),
        },
        thresholds=[],
        exemptions=[
            ExemptionRule(exemption_id="NY-SHIELD-COMPLIANT-REGULATED", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["healthcare_covered_entity", "business_associate", "financial_institution", "nydfs_covered_entity"], carve_out_statute="N.Y. Gen. Bus. Law § 899-bb(1)",
                          description="Entities compliant with GLBA, HIPAA/HITECH, 23 NYCRR 500, or other applicable federal/NY data security rules are deemed compliant with § 899-bb safeguards."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="NY-SHIELD-NYDFS-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="US-NY-NYDFS-500",
                           scope_condition="NYDFS-licensed entity", description="NYDFS 72-hour cybersecurity incident notice applies in addition to GBL § 899-aa resident notice."),
        ],
        organization_types=["private", "nonprofit"],
        industry_sectors=["all"],
        data_subject_categories=["residents", "consumers", "employees"],
        data_categories=["private_information", "biometric_data", "credentials"],
        processing_activities=["data_security", "breach_response"],
        required_actions=[
            "Implement a data security program with reasonable administrative safeguards: designate coordinator(s), identify reasonably foreseeable risks, assess safeguards, train employees, select capable service providers bound by contract, adjust program (§ 899-bb(2)(b)(ii)(A))",
            "Implement reasonable technical safeguards: assess network/software design risks, detect/prevent/respond to attacks, regularly test and monitor key controls (§ 899-bb(2)(b)(ii)(B))",
            "Implement reasonable physical safeguards: assess storage/disposal risks, detect/prevent intrusions, protect against unauthorized access during collection, transport and disposal, dispose within reasonable time (§ 899-bb(2)(b)(ii)(C))",
            "Notify affected NY residents within 30 days of discovering a breach of private information (§ 899-aa(2))",
            "Notify the Attorney General, Department of State, Division of State Police and NYDFS of timing, content, distribution and approximate number of affected persons (§ 899-aa(8)(a))",
            "Document 'inadvertent disclosure' no-harm determinations in writing, retain 5 years, and provide to AG within 10 days if > 500 residents (§ 899-aa(2)(a))",
        ],
        required_assessments=["SHIELD reasonable safeguards risk assessment"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_text="AG, Department of State, State Police and NYDFS — concurrently with resident notice",
            breach_attorney_general_threshold_individuals=1,
            breach_individual_notification_days=30,
            breach_individual_text="In the most expedient time possible and without unreasonable delay, no later than 30 days after discovery",
            record_retention_years=5,
        ),
        notification_requirements=["Residents: <= 30 days", "State agencies (AG, DOS, State Police, DFS): at time of resident notice", "CRAs: if > 5,000 residents notified", "Civil penalties up to $5,000 per violation for safeguards failures; up to $20 per failed notification, max $250,000"],
        required_evidence=["Written information security program", "Risk assessments", "Employee training records", "Service provider contracts", "Breach notices and no-harm determinations"],
        approval_requirements=["Designated security coordinator sign-off"],
        competent_regulator="New York State Office of the Attorney General",
        domain_category="cybersecurity",
    )
    nydfs = _state(
        regulation_id="US-NY-NYDFS-500",
        jurisdiction_id="US-NY",
        legal_authority="New York State Department of Financial Services (NYDFS)",
        legal_instrument="Cybersecurity Requirements for Financial Services Companies (as amended by the Second Amendment, Nov. 1, 2023)",
        official_source_url="https://www.dfs.ny.gov/industry_guidance/cybersecurity",
        article_or_section="23 NYCRR Part 500 (§§ 500.0-500.24)",
        effective_date=date(2017, 3, 1),
        applicability_conditions={
            "subject_locations_any": ["US-NY"],
            "organization_types_any": ["financial_institution", "nydfs_covered_entity"],
            "industry_sectors_any": ["banking", "insurance", "financial_services", "mortgage", "money_transmission", "virtual_currency", "check_cashing"],
            "gate_logic": "org_only",
            "notes": (
                "Applies to any person operating under or required to operate under a license, registration, charter, "
                "certificate, permit or similar authorization under NY Banking, Insurance or Financial Services Law. "
                "Class A companies: >= $20M gross NY revenue and either > 2,000 employees or > $1B gross revenue (incl. "
                "affiliates). Second Amendment phased obligations completed Nov. 1, 2025 (universal MFA, asset inventory)."
            ),
        },
        thresholds=_thr(
            ("employee_count", "<", 20, "OR", "Limited exemption § 500.19(a)(1): fewer than 20 employees and independent contractors (incl. affiliates)"),
            ("annual_revenue_usd", "<", 7500000, "OR", "Limited exemption § 500.19(a)(2): less than $7.5M gross annual revenue from NY business operations in each of last 3 fiscal years"),
            ("total_assets_usd", "<", 15000000, "OR", "Limited exemption § 500.19(a)(3): less than $15M year-end total assets"),
            ("annual_revenue_usd", ">=", 20000000, "CLASS_A", "Class A company: at least $20M gross annual revenue from NY business AND (> 2,000 employees OR > $1B gross annual revenue) — § 500.1(d)"),
        ),
        exemptions=[
            ExemptionRule(exemption_id="NYDFS-500.19-LIMITED", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["small_covered_entity_500_19a"], carve_out_statute="23 NYCRR § 500.19(a)",
                          description="Limited exemption entities must still maintain a cybersecurity program, policy, risk assessment, access privileges, third-party policy, MFA, asset inventory, incident notification and annual compliance filing; file Notice of Exemption within 30 days."),
            ExemptionRule(exemption_id="NYDFS-500.19-EMPLOYEE-OF-CE", exemption_type="entity_level", condition_field="organization_type",
                          condition_values=["employee_or_agent_covered_by_parent_program"], carve_out_statute="23 NYCRR § 500.19(b)",
                          description="Employees/agents covered by the cybersecurity program of their covered entity."),
        ],
        preemption_rules=[
            PreemptionRule(rule_id="NYDFS-GLBA-CONCURRENT", preempts_or_yields="concurrent_with", target_regulation_id="US-FED-GLBA-PRIVACY",
                           scope_condition="NY-licensed financial institutions", description="More stringent state cybersecurity regime applied in addition to GLBA Safeguards (15 U.S.C. § 6807)."),
        ],
        organization_types=["financial_institution", "nydfs_covered_entity"],
        industry_sectors=["banking", "insurance", "financial_services", "virtual_currency"],
        data_subject_categories=["customers", "consumers", "employees"],
        data_categories=["nonpublic_information", "financial_data", "credentials"],
        processing_activities=["cybersecurity_program", "incident_response", "third_party_service_provider_management", "ransom_payment"],
        required_actions=[
            "Maintain a cybersecurity program based on the risk assessment (§ 500.2); Class A: independent audit of the program",
            "Maintain board-approved written cybersecurity policies reviewed at least annually (§ 500.3)",
            "Designate a qualified CISO responsible for the program; CISO reports in writing at least annually to the senior governing body and timely on material issues (§ 500.4)",
            "Senior governing body must have sufficient understanding of cybersecurity and exercise oversight (§ 500.4(d))",
            "Conduct annual penetration testing and automated vulnerability scans with timely remediation (§ 500.5)",
            "Maintain audit trails to reconstruct material financial transactions (5 years) and detect/respond to cybersecurity events (3 years) (§ 500.6)",
            "Limit and annually review access privileges, including privileged accounts; Class A: privileged access management and password controls (§ 500.7)",
            "Implement written application security procedures (§ 500.8) and annual risk assessment (§ 500.9)",
            "Use qualified cybersecurity personnel and provide training (§ 500.10)",
            "Implement a written Third-Party Service Provider security policy: identification and risk assessment, minimum practices, due diligence, periodic assessment, contractual MFA/encryption/notice obligations (§ 500.11)",
            "Implement multi-factor authentication for any individual accessing any information system (§ 500.12, effective Nov. 1, 2025)",
            "Maintain a complete, documented asset inventory (§ 500.13(a), effective Nov. 1, 2025) and data retention/disposal policies (§ 500.13(b))",
            "Implement monitoring and annual cybersecurity awareness training incl. social engineering (§ 500.14); Class A: EDR and centralized logging",
            "Encrypt nonpublic information in transit over external networks and at rest, or CISO-approved compensating controls reviewed annually (§ 500.15)",
            "Maintain written incident response and business continuity/disaster recovery plans, tested at least annually (§ 500.16)",
            "Notify NYDFS within 72 hours of determining a cybersecurity incident has occurred; provide requested information and updates (§ 500.17(a))",
            "Report extortion payments within 24 hours and a written description within 30 days (§ 500.17(c))",
            "Submit annual Certification of Material Compliance or Acknowledgment of Noncompliance by April 15, signed by highest-ranking executive and CISO (§ 500.17(b))",
        ],
        required_assessments=["NYDFS Cybersecurity Risk Assessment (§ 500.9)", "Third-Party Service Provider risk assessment (§ 500.11)", "Class A independent audit (§ 500.2(c))", "Annual penetration test (§ 500.5)"],
        response_deadlines=ResponseDeadlineSpec(
            identity_verification_required=False,
            breach_regulator_hours=72,
            breach_regulator_text="NYDFS within 72 hours of determining a cybersecurity incident occurred at the covered entity, its affiliates or a third-party service provider; extortion payment notice within 24 hours and written justification within 30 days",
            breach_attorney_general_threshold_individuals=1,
            breach_individual_text="See US-NY-BREACH (GBL § 899-aa: 30 days)",
            record_retention_years=5,
        ),
        notification_requirements=["NYDFS cybersecurity incident: 72 hours via DFS Portal", "Extortion payment: 24 hours + written explanation within 30 days", "Annual certification/acknowledgment: April 15", "Notice of Exemption: within 30 days of qualifying"],
        required_evidence=["Board-approved cybersecurity policy", "CISO annual report to board", "Risk assessment", "Penetration test and vulnerability scan results", "Asset inventory", "MFA coverage evidence", "TPSP policy and due diligence files", "IR/BCDR plans and test results", "Annual certification and supporting documentation (retained 5 years)"],
        approval_requirements=["Senior governing body approval of cybersecurity policy", "CEO (highest-ranking executive) and CISO sign annual certification", "CISO approval of compensating controls in lieu of encryption"],
        competent_regulator="New York State Department of Financial Services (NYDFS)",
        domain_category="cybersecurity",
    )
    return [shield, nydfs]


# ---------------------------------------------------------------------------
# 9. OTHER COMPREHENSIVE STATE PRIVACY LAWS
# ---------------------------------------------------------------------------

def _other_comprehensive() -> List[CanonicalRegulation]:
    regs: List[CanonicalRegulation] = []

    regs.append(_comprehensive(
        "US-VA-VCDPA", "US-VA", "Virginia Consumer Data Protection Act", "Va. Code Ann. §§ 59.1-575 to 59.1-585",
        "https://law.lis.virginia.gov/vacodefull/title59.1/chapter53/",
        date(2023, 1, 1),
        _thr(_T100K, *_t_sale(25000, 50, "derives over 50%")),
        _std_exemptions("VA", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=30,
        cure_note="30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
        extra_actions=["Social media platforms: verify age and limit minors under 16 to one hour per day absent parental consent (SB 854, operative Jan 1, 2026 — subject to litigation)"],
        notes="Applies to persons conducting business in Virginia or targeting Virginia residents that meet thresholds. AG exclusive enforcement.",
    ))

    regs.append(_comprehensive(
        "US-CT-CTDPA", "US-CT", "Connecticut Data Privacy Act (incl. Consumer Health Data and Minors amendments)",
        "Conn. Gen. Stat. §§ 42-515 to 42-526 (P.A. 22-15, as amended by P.A. 23-56 and P.A. 25-113 / SB 1295)",
        "https://portal.ct.gov/ag/sections/privacy/the-connecticut-data-privacy-act",
        date(2023, 7, 1),
        _thr(
            ("consumer_records_count", ">=", 35000, "OR", "Controls or processes personal data of at least 35,000 Connecticut consumers (SB 1295, effective July 1, 2026; previously 100,000)"),
            ("processes_sensitive_data", "==", True, "OR", "Controls or processes consumers' sensitive data (other than solely for payment) (SB 1295, effective July 1, 2026)"),
            ("sells_personal_data", "==", True, "OR", "Offers consumers' personal data for sale in trade or commerce (SB 1295, effective July 1, 2026)"),
        ),
        _std_exemptions("CT", glba="data", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=None, uoom=True,
        cure_note="Mandatory 60-day cure period expired Dec 31, 2024; AG may grant cure at discretion",
        extra_actions=[
            "Consumer health data (P.A. 23-56): any person (regardless of thresholds) must obtain consent before selling consumer health data and may not geofence within 1,750 feet of mental, reproductive or sexual health facilities",
            "Minors (P.A. 23-56, effective Oct 1, 2024): online services with actual knowledge or wilful disregard of users under 18 must avoid heightened risk of harm, conduct impact assessments, and not process for targeted advertising/sale/profiling without consent",
            "Impact assessments for profiling in furtherance of decisions producing legal or similarly significant effects and right to contest such decisions (SB 1295, effective July 1, 2026)",
            "Disclose whether personal data is used to train large language models (SB 1295)",
        ],
        extra_assessments=["Minors heightened-risk impact assessment", "Profiling impact assessment (SB 1295)"],
        notes="Thresholds lowered and scope expanded by SB 1295 effective July 1, 2026. Consumer health data provisions apply to all persons regardless of thresholds.",
        counsel_signoff=True,
    ))

    regs.append(_comprehensive(
        "US-UT-UCPA", "US-UT", "Utah Consumer Privacy Act", "Utah Code Ann. §§ 13-61-101 to 13-61-404",
        "https://le.utah.gov/xcode/Title13/Chapter61/13-61.html",
        date(2023, 12, 31),
        _thr(
            ("annual_revenue_usd", ">=", 25000000, "AND", "Annual revenue of $25,000,000 or more AND one of the following"),
            ("consumer_records_count", ">=", 100000, "AND_OR", "Controls or processes personal data of 100,000 or more Utah consumers in a calendar year; OR"),
            ("consumer_records_count", ">=", 25000, "AND_OR_B", "controls or processes personal data of 25,000 or more consumers AND derives over 50% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("UT", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=None, cure_days=30,
        cure_note="No statutory appeal right; 30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
        extra_actions=["Provide notice and opportunity to opt out before processing sensitive data (opt-out rather than opt-in model)", "Social media / AI disclosure: comply with Utah AI Policy Act (Utah Code § 13-75) disclosure duties for generative AI interactions"],
        notes="Business-friendly model: no data protection assessments mandated, no right to correct until 2025 amendment (SB 13 adds correction effective May 7, 2025). Enforcement: Division of Consumer Protection investigates, AG enforces.",
    ))

    regs.append(_comprehensive(
        "US-OR-OCPA", "US-OR", "Oregon Consumer Privacy Act", "Or. Rev. Stat. §§ 646A.570-646A.589",
        "https://www.doj.state.or.us/consumer-protection/id-theft-data-breaches/privacy/",
        date(2024, 7, 1),
        _thr(
            ("consumer_records_count", ">=", 100000, "OR", "Controls or processes personal data of 100,000 or more Oregon consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 25000, "OR_B", "Controls or processes personal data of 25,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">=", 25, "OR_B", "... derives 25% or more of annual gross revenue from selling personal data"),
        ),
        _std_exemptions("OR", glba="data", hipaa="data", nonprofit_exempt=False, higher_ed_exempt=False),
        appeal_days=45, cure_days=None, uoom=True,
        cure_note="30-day cure period expired Jan 1, 2026; appeals decided within 45 days (+60-day extension)",
        extra_actions=[
            "Provide on request a list of specific third parties to which personal data was disclosed",
            "Do not sell precise geolocation data or personal data of consumers under 16 (HB 2008, effective Jan 1, 2026)",
            "Motor vehicle manufacturers processing vehicle data are covered regardless of thresholds (HB 3875)",
        ],
        notes="Nonprofits covered from July 1, 2025. Sensitive data includes transgender/non-binary status and crime-victim status.",
    ))

    regs.append(_comprehensive(
        "US-MT-MCDPA", "US-MT", "Montana Consumer Data Privacy Act", "Mont. Code Ann. §§ 30-14-2801 to 30-14-2817 (as amended by SB 297, 2025)",
        "https://dojmt.gov/office-of-consumer-protection/",
        date(2024, 10, 1),
        _thr(
            ("consumer_records_count", ">=", 25000, "OR", "Controls or processes personal data of 25,000 or more Montana consumers (excluding payment-only data) (SB 297, effective Oct 1, 2025; previously 50,000)"),
            ("consumer_records_count", ">=", 15000, "OR_B", "Controls or processes personal data of 15,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 25, "OR_B", "... derives more than 25% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("MT", glba="data", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=None, uoom=True,
        cure_note="Cure period eliminated by SB 297 (effective Oct 1, 2025)",
        extra_actions=["Minors: heightened protections and impact assessments for online services directed to consumers under 18 (SB 297)"],
        counsel_signoff=True,
    ))

    regs.append(_comprehensive(
        "US-DE-DPDPA", "US-DE", "Delaware Personal Data Privacy Act", "Del. Code Ann. tit. 6, §§ 12D-101 to 12D-111",
        "https://attorneygeneral.delaware.gov/fraud/personal-data-privacy-portal/",
        date(2025, 1, 1),
        _thr(
            ("consumer_records_count", ">=", 35000, "OR", "Controls or processes personal data of 35,000 or more Delaware consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 10000, "OR_B", "Controls or processes personal data of 10,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 20, "OR_B", "... derives more than 20% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("DE", glba="data", hipaa="data", nonprofit_exempt=False, higher_ed_exempt=False),
        appeal_days=60, cure_days=None, uoom=True,
        cure_note="60-day cure period expired Dec 31, 2025",
        extra_actions=["Obtain consent before targeted advertising or sale of data of consumers under 18 (known or wilfully disregarded)"],
        notes="Nonprofits covered (except those dedicated to preventing insurance crime). Sensitive data includes pregnancy status and transgender/non-binary status.",
    ))

    regs.append(_comprehensive(
        "US-IA-ICDPA", "US-IA", "Iowa Consumer Data Protection Act", "Iowa Code ch. 715D",
        "https://www.legis.iowa.gov/docs/code/715D.pdf",
        date(2025, 1, 1),
        _thr(_T100K, *_t_sale(25000, 50, "derives over 50%")),
        _std_exemptions("IA", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        initial_days=90, extension_days=45, appeal_days=60, cure_days=90,
        cure_note="90-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
        extra_actions=["Provide notice and opportunity to opt out of sensitive data processing (opt-out model)"],
        notes="No right to correct, no profiling opt-out, and no data protection assessment requirement.",
    ))

    regs.append(_comprehensive(
        "US-NE-NDPA", "US-NE", "Nebraska Data Privacy Act", "Neb. Rev. Stat. §§ 87-1101 to 87-1130",
        "https://ago.nebraska.gov/data-privacy",
        date(2025, 1, 1),
        _thr(
            ("conducts_business_in_state", "==", True, "AND", "Conducts business in Nebraska or produces products/services consumed by Nebraska residents"),
            ("processes_or_sells_personal_data", "==", True, "AND", "Processes or engages in the sale of personal data"),
            ("is_sba_small_business", "==", False, "AND", "Is not a small business as defined by the U.S. SBA (small businesses still need consent to sell sensitive data)"),
        ),
        _std_exemptions("NE", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=30, uoom=True,
        cure_note="30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
        notes="Texas-model statute with no numeric thresholds.",
    ))

    regs.append(_comprehensive(
        "US-NH-NHPA", "US-NH", "New Hampshire Privacy Act", "N.H. Rev. Stat. Ann. ch. 507-H",
        "https://www.doj.nh.gov/bureaus/consumer-protection-and-antitrust-bureau/data-privacy",
        date(2025, 1, 1),
        _thr(
            ("consumer_records_count", ">=", 35000, "OR", "Controls or processes personal data of 35,000 or more New Hampshire consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 10000, "OR_B", "Controls or processes personal data of 10,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 25, "OR_B", "... derives more than 25% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("NH", glba="entity", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=None, uoom=True,
        cure_note="60-day cure period expired Dec 31, 2025",
        notes="Applies to persons conducting business in NH or targeting NH residents. AG exclusive enforcement.",
    ))

    regs.append(_comprehensive(
        "US-NJ-NJDPA", "US-NJ", "New Jersey Data Privacy Act", "N.J. Stat. Ann. §§ 56:8-166.4 to 56:8-166.19; N.J.A.C. 13:45L (proposed/adopted rules)",
        "https://www.njconsumeraffairs.gov/",
        date(2025, 1, 15),
        _thr(
            ("consumer_records_count", ">=", 100000, "OR", "Controls or processes personal data of 100,000 or more New Jersey consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 25000, "OR_B", "Controls or processes personal data of 25,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 0, "OR_B", "... derives revenue or receives a discount from the sale of personal data"),
        ),
        _std_exemptions("NJ", glba="entity", hipaa="data", nonprofit_exempt=False, higher_ed_exempt=False),
        appeal_days=45, cure_days=None, uoom=True,
        cure_note="30-day cure period available until July 1, 2026 (expired)",
        extra_actions=["Consent required before processing data of known teens (13-17) for targeted advertising, sale or profiling", "Conduct data protection assessments before high-risk processing"],
        notes="Enforced by NJ Attorney General / Division of Consumer Affairs. Sensitive data includes financial account data and transgender/non-binary status. Nonprofits covered.",
        regulator="New Jersey Office of the Attorney General — Division of Consumer Affairs",
    ))

    regs.append(_comprehensive(
        "US-TN-TIPA", "US-TN", "Tennessee Information Protection Act", "Tenn. Code Ann. §§ 47-18-3201 to 47-18-3214",
        "https://www.tn.gov/attorneygeneral/working-for-tennessee/consumer-protection.html",
        date(2025, 7, 1),
        _thr(
            ("annual_revenue_usd", ">", 25000000, "AND", "Revenue exceeding $25,000,000 AND one of the following"),
            ("consumer_records_count", ">=", 175000, "AND_OR", "Controls or processes personal data of at least 175,000 Tennessee consumers during a calendar year; OR"),
            ("consumer_records_count", ">=", 25000, "AND_OR_B", "controls or processes personal data of at least 25,000 consumers AND derives more than 50% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("TN", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=60,
        cure_note="60-day cure period after AG notice (permanent); treble damages for wilful/knowing violations; civil penalty up to $7,500 per violation",
        extra_actions=["Maintain a written privacy program reasonably conforming to the NIST Privacy Framework to qualify for the statutory affirmative defense (§ 47-18-3213)"],
        notes="Insurance licensees exempt. NIST Privacy Framework affirmative defense.",
    ))

    regs.append(_comprehensive(
        "US-MN-MCDPA", "US-MN", "Minnesota Consumer Data Privacy Act", "Minn. Stat. ch. 325M (§§ 325M.10-325M.21)",
        "https://www.revisor.mn.gov/statutes/cite/325M",
        date(2025, 7, 31),
        _thr(
            ("consumer_records_count", ">=", 100000, "OR", "Controls or processes personal data of 100,000 or more Minnesota consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 25000, "OR_B", "Controls or processes personal data of 25,000 or more consumers AND ..."),
            ("data_broker_revenue_pct", ">", 25, "OR_B", "... derives over 25% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("MN", glba="data", hipaa="data", nonprofit_exempt=False, higher_ed_exempt=False),
        appeal_days=45, cure_days=None, uoom=True,
        cure_note="30-day cure period expired Jan 31, 2026",
        extra_actions=[
            "Right to question the result of a profiling decision, be informed of the reason and actions to achieve a different result, and review the data used (§ 325M.14 subd. 1(g))",
            "Maintain a data inventory (§ 325M.16 subd. 1(a)(4))",
            "Document and maintain description of policies and procedures to comply (§ 325M.17)",
            "Provide on request a list of specific third parties to which data was disclosed",
            "SBA small businesses exempt except must obtain consent before selling sensitive data",
        ],
        notes="Postsecondary institutions covered from July 31, 2029. Nonprofits covered.",
    ))

    regs.append(_comprehensive(
        "US-MD-MODPA", "US-MD", "Maryland Online Data Privacy Act of 2024", "Md. Code Ann., Com. Law §§ 14-4601 to 14-4613",
        "https://www.marylandattorneygeneral.gov/Pages/CPD/OnlineDataPrivacyAct.aspx",
        date(2025, 10, 1),
        _thr(
            ("consumer_records_count", ">=", 35000, "OR", "Controls or processes personal data of at least 35,000 Maryland consumers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 10000, "OR_B", "Controls or processes personal data of at least 10,000 consumers AND ..."),
            ("data_broker_revenue_pct", ">", 20, "OR_B", "... derives more than 20% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("MD", glba="entity", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=False),
        appeal_days=60, cure_days=60,
        cure_note="60-day cure period at AG discretion until April 1, 2027",
        uoom=True,
        extra_actions=[
            "Limit collection of personal data to what is reasonably necessary and proportionate to provide the requested product/service (§ 14-4607(a)(1))",
            "Collect/process sensitive data only when strictly necessary to provide or maintain a specifically requested product/service (§ 14-4607(a)(2))",
            "Do not sell sensitive data under any circumstances (§ 14-4607(a)(3))",
            "Do not process personal data for targeted advertising or sell data where the controller knew or should have known the consumer is under 18 (§ 14-4607(a)(7))",
            "Conduct data protection assessments for each algorithm used in high-risk processing (§ 14-4610)",
        ],
        extra_assessments=["Algorithm-level data protection assessment"],
        notes="Effective Oct 1, 2025; does not apply to personal data processing activities before April 1, 2026. Strictest data-minimization standard among US comprehensive laws.",
        transition_end=date(2026, 4, 1),
    ))

    regs.append(_comprehensive(
        "US-IN-ICDPA", "US-IN", "Indiana Consumer Data Protection Act", "Ind. Code art. 24-15",
        "https://www.in.gov/attorneygeneral/consumer-protection-division/",
        date(2026, 1, 1),
        _thr(_T100K, *_t_sale(25000, 50, "derives more than 50%")),
        _std_exemptions("IN", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=30,
        cure_note="30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
    ))

    regs.append(_comprehensive(
        "US-KY-KCDPA", "US-KY", "Kentucky Consumer Data Protection Act", "Ky. Rev. Stat. §§ 367.3611-367.3629",
        "https://www.ag.ky.gov/Priorities/Protecting-Kentuckians/Consumers/Pages/default.aspx",
        date(2026, 1, 1),
        _thr(_T100K, *_t_sale(25000, 50, "derives over 50%")),
        _std_exemptions("KY", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=30,
        cure_note="30-day cure period after AG notice (permanent); civil penalty up to $7,500 per violation",
    ))

    regs.append(_comprehensive(
        "US-RI-RIDTPPA", "US-RI", "Rhode Island Data Transparency and Privacy Protection Act", "R.I. Gen. Laws §§ 6-48.1-1 to 6-48.1-10",
        "https://webserver.rilegislature.gov/Statutes/TITLE6/6-48.1/INDEX.htm",
        date(2026, 1, 1),
        _thr(
            ("consumer_records_count", ">=", 35000, "OR", "Controls or processes personal data of at least 35,000 Rhode Island customers (excluding payment-only data)"),
            ("consumer_records_count", ">=", 10000, "OR_B", "Controls or processes personal data of at least 10,000 customers AND ..."),
            ("data_broker_revenue_pct", ">", 20, "OR_B", "... derives more than 20% of gross revenue from the sale of personal data"),
        ),
        _std_exemptions("RI", glba="entity", hipaa="data", nonprofit_exempt=True, higher_ed_exempt=True),
        appeal_days=60, cure_days=None,
        cure_note="No cure period; civil penalty up to $10,000 per violation",
        extra_actions=["Any commercial website or internet service provider that collects, stores and sells customers' personally identifiable information must identify in its privacy notice all categories of data and third parties to whom data may be sold — regardless of thresholds (§ 6-48.1-3)"],
        notes="Website privacy-notice duties apply to all commercial websites/ISPs serving RI customers regardless of thresholds. No universal opt-out mechanism requirement.",
    ))

    regs.append(_comprehensive(
        "US-FL-FDBR", "US-FL", "Florida Digital Bill of Rights", "Fla. Stat. §§ 501.701-501.722",
        "https://www.myfloridalegal.com/",
        date(2024, 7, 1),
        _thr(
            ("annual_revenue_usd", ">", 1000000000, "AND", "Global gross annual revenues in excess of $1 billion AND one of the following"),
            ("online_ad_revenue_pct", ">=", 50, "AND_OR", "Derives 50% or more of global gross annual revenues from the sale of advertisements online, including targeted advertising; OR"),
            ("operates_smart_speaker_voice_assistant", "==", True, "AND_OR", "Operates a consumer smart speaker and voice command component service with integrated virtual assistant connected to a cloud computing service using hands-free verbal activation; OR"),
            ("operates_app_store_250k_apps", "==", True, "AND_OR", "Operates an app store or digital distribution platform offering at least 250,000 different software applications"),
        ),
        _std_exemptions("FL", glba="entity", hipaa="entity", nonprofit_exempt=True, higher_ed_exempt=True),
        initial_days=45, extension_days=15, appeal_days=60, cure_days=45,
        cure_note="45-day cure period at AG discretion; civil penalties up to $50,000 per violation, tripled for violations involving known children under 18",
        extra_actions=[
            "Any for-profit entity doing business in Florida (regardless of the $1B threshold) that sells sensitive data must post 'NOTICE: This website may sell your sensitive personal data.' and obtain consent before selling sensitive data (§ 501.71(5); § 501.715)",
            "Retention: maintain and publish a data retention schedule; delete personal data within 2 years after the purpose is satisfied unless otherwise required (§ 501.711)",
            "Search engines: disclose prioritization of political/ideological factors (§ 501.708)",
            "Online platforms primarily accessed by children: do not process children's data that may cause substantial harm (§ 501.7155)",
        ],
        notes="Comprehensive obligations apply only to very large 'controllers' meeting the $1B revenue test plus one prong; certain sensitive-data sale provisions apply to all for-profit businesses.",
        regulator="Florida Department of Legal Affairs (Attorney General)",
    ))
    return regs


# ---------------------------------------------------------------------------
# 10. PUBLIC ENTRYPOINT
# ---------------------------------------------------------------------------

def get_us_state_breach_regulations() -> List[CanonicalRegulation]:
    return [_breach_regulation(code, rule) for code, rule in US_STATE_BREACH_RULES.items()]


def get_us_state_regulations() -> List[CanonicalRegulation]:
    regs: List[CanonicalRegulation] = []
    regs.extend(get_us_state_breach_regulations())
    regs.extend(_california())
    regs.extend(_colorado())
    regs.extend(_texas())
    regs.extend(_washington())
    regs.extend(_illinois())
    regs.extend(_new_york())
    regs.extend(_other_comprehensive())
    return regs
