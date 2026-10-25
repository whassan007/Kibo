"""
US Federal & State Judicial Opinion Source Registry & Authentic Fixtures (G05).

Provides curated, machine-readable source registry entries for official United States
federal and state appellate judicial opinion repositories, together with deterministic,
verbatim judicial opinion fixtures (including appellate modification/reversal chains
for RD-05 and holding vs. dicta separation for RD-07).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from core.regulatory_intelligence import (
    RegulatorySourceEntry,
    SourceHealthStatus,
)

US_JUDICIAL_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-US-FED-SCOTUS-OPINIONS",
        jurisdiction_id="US-FED",
        parent_jurisdiction="US-FED",
        authority_name="Supreme Court of the United States",
        authority_type="court",
        official_domain="supremecourt.gov",
        discovery_endpoint="https://www.supremecourt.gov/opinions/slipopinion/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="US Government Work (17 U.S.C. § 105) — Public Domain",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "constitutional_standing",
            "fourth_amendment",
            "administrative_law",
            "statutory_interpretation",
        ],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="SCOTUS-OT2025-SLIP-001",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-GOVINFO-USCOURTS",
        jurisdiction_id="US-FED",
        parent_jurisdiction="US-FED",
        authority_name="United States Federal Courts (U.S. Government Publishing Office / GovInfo USCOURTS)",
        authority_type="court",
        official_domain="api.govinfo.gov",
        discovery_endpoint="https://api.govinfo.gov/collections/USCOURTS/2026-01-01T00:00:00Z",
        feed_format="api_json",
        auth_requirements="api_key",
        licensing_and_reuse="US Government Work (17 U.S.C. § 105) — Public Domain (MODS/PREMIS XML & PDF)",
        rate_limit_rpm=60,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "class_action_litigation",
            "consumer_protection",
            "administrative_law",
        ],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="USCOURTS-2026-10-25T00:00:00Z",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-FED-COURTLISTENER-OPINIONS",
        jurisdiction_id="US-FED",
        parent_jurisdiction="US-FED",
        authority_name="Free Law Project / CourtListener Official Opinion & RECAP Repository",
        authority_type="court",
        official_domain="courtlistener.com",
        discovery_endpoint="https://www.courtlistener.com/api/rest/v4/opinions/",
        feed_format="api_json",
        auth_requirements="api_key",
        licensing_and_reuse="Public Domain Judicial Opinions / Free Law Project Bulk & REST API v4 Terms",
        rate_limit_rpm=60,
        update_frequency="every_6_hours",
        publication_coverage=[
            "privacy",
            "data_protection",
            "cybersecurity",
            "biometric_privacy",
            "wiretap_cipa",
            "vpba",
            "fcra",
        ],
        legal_instrument_types=["court_judgment", "consent_order_settlement"],
        source_priority=2,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CL-V4-OPINION-CURSOR-9941200",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-CA-COURTS-OPINIONS",
        jurisdiction_id="US-CA",
        parent_jurisdiction="US-FED",
        authority_name="Supreme Court of California & California Courts of Appeal",
        authority_type="court",
        official_domain="courts.ca.gov",
        discovery_endpoint="https://www.courts.ca.gov/opinions-slip.htm",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Public Domain under California Law (Cal. Civ. Code § 22.2 / Official Judicial Opinions)",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "data_protection",
            "ccpa_cpra",
            "cipa_wiretap",
            "constitutional_privacy",
            "administrative_mandamus",
        ],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="CA-SLIP-2026-10",
    ),
    RegulatorySourceEntry(
        source_id="SRC-US-IL-COURTS-OPINIONS",
        jurisdiction_id="US-IL",
        parent_jurisdiction="US-FED",
        authority_name="Supreme Court of Illinois & Illinois Appellate Court",
        authority_type="court",
        official_domain="illinoiscourts.gov",
        discovery_endpoint="https://www.illinoiscourts.gov/top-level-opinions/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Public Domain Official Judicial Opinions — State of Illinois Judicial Branch",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=[
            "privacy",
            "biometric_privacy",
            "bipa_740_ilcs_14",
            "genetic_information_privacy",
            "data_protection",
        ],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en"],
        last_successful_retrieval=datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc),
        health_status=SourceHealthStatus.HEALTHY,
        checkpoint_cursor="IL-OPINIONS-2026-10",
    ),
]


AUTHENTIC_US_JUDICIAL_FIXTURES: List[Dict[str, Any]] = [
    {
        "document_id": "DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413",
        "decision_id": "DEC-US-FED-SCOTUS-2021-TRANSUNION",
        "source_id": "SRC-US-FED-SCOTUS-OPINIONS",
        "document_type": "court_judgment",
        "canonical_title": "TransUnion LLC v. Ramirez, 594 U.S. 413 (2021)",
        "case_name": "TransUnion LLC v. Ramirez",
        "jurisdiction_id": "US-FED",
        "parent_jurisdictions": [],
        "issuing_authority": "Supreme Court of the United States",
        "issuing_authority_type": "court",
        "official_source_url": "https://www.supremecourt.gov/opinions/20pdf/20-297_4g25.pdf",
        "official_citation": "594 U.S. 413 (2021)",
        "neutral_citation": "594 U.S. 413",
        "docket_or_case_number": "No. 20-297",
        "decision_date": "2021-06-25",
        "publication_date": "2021-06-25",
        "effective_date": "2021-06-25",
        "appeal_status": "reversed_and_remanded",
        "binding_status": "binding_precedent",
        "parties": ["TransUnion LLC", "Sergio L. Ramirez"],
        "statutory_provisions_considered": [
            "U.S. Const. art. III, § 2",
            "15 U.S.C. § 1681e(b)",
            "15 U.S.C. § 1681g(a)(1)",
            "15 U.S.C. § 1681g(c)(2)",
            "15 U.S.C. § 1681n(a)",
        ],
        "material_facts": (
            "A class of 8,185 individuals had OFAC terrorist/narcotics alerts placed in their "
            "TransUnion credit files using name-only matching. For 1,853 class members, TransUnion "
            "disseminated misleading credit reports containing the OFAC alert to third-party creditors "
            "during the class period; for the remaining 6,332 class members, their internal credit files "
            "contained the misleading alert but were never disseminated to any third party."
        ),
        "legal_issues": [
            "Whether Article III permits a class of consumers to recover statutory damages in federal court under the Fair Credit Reporting Act (15 U.S.C. § 1681n(a)) when inaccurate OFAC alerts in their credit files were never disseminated to third-party creditors.",
            "Whether formatting defects in disclosures mailed directly to consumers under 15 U.S.C. § 1681g without evidence of downstream confusion or reliance satisfy Article III concrete injury-in-fact.",
        ],
        "normalized_text": (
            "JUSTICE KAVANAUGH delivered the opinion of the Court. "
            "To have Article III standing to sue in federal court, plaintiffs must demonstrate, "
            "among other things, that they suffered a concrete harm. No concrete harm, no standing. "
            "Central to assessing concreteness is whether the asserted harm has a 'close relationship' "
            "to a harm traditionally recognized as providing a basis for a lawsuit in American courts—"
            "such as physical harm, monetary harm, or various intangible harms including (as relevant here) "
            "reputational harm. Spokeo, Inc. v. Robins, 578 U. S. 330, 340–341 (2016). "
            "The 1,853 class members whose reports were disseminated to third-party businesses suffered "
            "a concrete harm in the form of reputational injury analogous to the tort of defamation. "
            "By contrast, the remaining 6,332 class members whose internal credit files were not provided "
            "to third-party businesses did not suffer a concrete harm. The mere presence of an inaccuracy "
            "in an internal credit file, if it is not disclosed to a third party, causes no concrete harm. "
            "In footprints of history and tradition, Congress's creation of a statutory prohibition or "
            "obligation and a cause of action does not relieve courts of their responsibility to "
            "independently decide whether a plaintiff has suffered a concrete harm under Article III."
        ),
        "legal_holdings": [
            "Only plaintiffs concretely harmed by a defendant's statutory violation have Article III standing to seek damages against that private defendant in federal court ('No concrete harm, no standing').",
            "The 1,853 class members whose credit reports bearing misleading OFAC alerts were disseminated to third-party businesses suffered a concrete injury-in-fact under Article III analogous to the traditional tort of defamation.",
            "The 6,332 class members whose internal credit files contained misleading OFAC alerts that were never disseminated to third parties lacked Article III standing because an uncommunicated internal file inaccuracy causes no concrete reputational harm and unmaterialized risk of future disclosure cannot independently support a suit for retrospective damages.",
            "On the disclosure formatting claims under 15 U.S.C. § 1681g, all class members other than named plaintiff Ramirez failed to demonstrate concrete informational injury where the record contained no evidence they opened the mailings or were confused or prevented from correcting their files.",
        ],
        "dicta_and_commentary": [
            "In footnote 6 and surrounding discussion, the Court noted hypothetical scenarios involving whether printing errors by a third-party mailing vendor could ever constitute 'publication' in a defamation sense, observing that plaintiffs had not advanced a serious theory of intracompany or vendor publication on the trial record.",
            "The Court observed in general commentary that a person exposed to a sufficiently imminent and substantial risk of future harm may pursue forward-looking injunctive relief to prevent the harm from occurring, while distinguishing retrospective damages claims.",
        ],
        "operative_orders": [
            "The judgment of the U.S. Court of Appeals for the Ninth Circuit is reversed, and the case is remanded for further proceedings consistent with this opinion, including consideration of whether class certification remains appropriate."
        ],
        "remedies_and_penalties": [
            "Vacatur of classwide statutory and punitive damages judgment as to the 6,332 class members lacking third-party dissemination on the § 1681e(b) claim and all absent class members on the § 1681g formatting claims."
        ],
        "subsequent_appeals": [],
        "reversals_or_modifications": [
            "Reverses Ramirez v. TransUnion LLC, 951 F.3d 1008 (9th Cir. 2020) (DOC-US-FED-CA9-2020-RAMIREZ-951-F3D-1008)."
        ],
        "supersedes": "DOC-US-FED-CA9-2020-RAMIREZ-951-F3D-1008",
        "practical_privacy_program_implications": [
            "Federal court class-action exposure for statutory privacy and accuracy violations hinges on demonstrable third-party disclosure, unauthorized external transmission, or tangible downstream harm, whereas state courts applying state standing doctrines (such as Illinois BIPA) are not bound by federal Article III constraints.",
            "Data accuracy and sanctions-screening pipelines must enforce multi-identifier verification rather than name-only fuzzy matching before generating external credit or compliance alerts.",
        ],
    },
    {
        "document_id": "DOC-US-FED-CA9-2020-RAMIREZ-951-F3D-1008",
        "decision_id": "DEC-US-FED-CA9-2020-RAMIREZ",
        "source_id": "SRC-US-FED-GOVINFO-USCOURTS",
        "document_type": "court_judgment",
        "canonical_title": "Ramirez v. TransUnion LLC, 951 F.3d 1008 (9th Cir. 2020) (Reversed by 594 U.S. 413)",
        "case_name": "Ramirez v. TransUnion LLC",
        "jurisdiction_id": "US-FED",
        "parent_jurisdictions": [],
        "issuing_authority": "United States Court of Appeals for the Ninth Circuit",
        "issuing_authority_type": "court",
        "official_source_url": "https://api.govinfo.gov/packages/USCOURTS-ca9-17-17244/summary",
        "official_citation": "951 F.3d 1008 (9th Cir. 2020)",
        "neutral_citation": "951 F.3d 1008",
        "docket_or_case_number": "No. 17-17244",
        "decision_date": "2020-02-27",
        "publication_date": "2020-02-27",
        "effective_date": "2020-02-27",
        "appeal_status": "reversed",
        "binding_status": "superseded_or_reversed_precedent",
        "parties": ["Sergio L. Ramirez", "TransUnion LLC"],
        "statutory_provisions_considered": [
            "U.S. Const. art. III, § 2",
            "15 U.S.C. § 1681e(b)",
            "15 U.S.C. § 1681g",
        ],
        "material_facts": (
            "Ninth Circuit panel review of the Northern District of California jury verdict awarding "
            "statutory and punitive damages to all 8,185 class members under the FCRA."
        ),
        "legal_issues": [
            "Whether every member of a Rule 23 class must satisfy Article III standing at the final judgment stage and whether a material risk of dissemination of inaccurate OFAC alerts suffices for all 8,185 class members."
        ],
        "normalized_text": (
            "Holding by the Ninth Circuit majority (subsequently reversed by the U.S. Supreme Court in "
            "TransUnion LLC v. Ramirez, 594 U.S. 413 (2021)): Every member of a class certified under "
            "Federal Rule of Civil Procedure 23 must satisfy the basic requirements of Article III "
            "standing at the final stage of a money damages suit. However, the Ninth Circuit panel held "
            "that all 8,185 class members suffered a material risk of harm sufficient to confer Article "
            "III standing on both the reasonable-procedures and disclosure claims because their credit "
            "files were available for immediate dissemination to third-party creditors upon request."
        ),
        "legal_holdings": [
            "[REVERSED BY 594 U.S. 413 (2021)] Held that a real risk of harm from maintaining inaccurate OFAC terrorist alerts in internal credit files available upon third-party request sufficed for Article III standing for all 8,185 class members even without proof of actual third-party dissemination."
        ],
        "dicta_and_commentary": [
            "Discussion of punitive-to-statutory damages ratio reduction from 6.45:1 to 4:1 under BMW of North America, Inc. v. Gore."
        ],
        "operative_orders": [
            "Affirmed district court judgment on liability and statutory damages; reduced punitive damages award. [Subsequently reversed and remanded by 594 U.S. 413 (2021)]."
        ],
        "remedies_and_penalties": [
            "Statutory damages of $984.22 per class member and reduced punitive damages of $3,936.88 per class member (subsequently vacated by U.S. Supreme Court)."
        ],
        "subsequent_appeals": [
            "TransUnion LLC v. Ramirez, 594 U.S. 413 (2021) (DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413)"
        ],
        "reversals_or_modifications": [
            "Reversed and remanded by the Supreme Court of the United States in TransUnion LLC v. Ramirez, 594 U.S. 413 (2021)."
        ],
        "is_amended_by": ["DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413"],
        "practical_privacy_program_implications": [
            "Tracked in the RD-05 appellate reversal chain to ensure downstream reasoning engines never cite the reversed Ninth Circuit 'material risk of credit file dissemination' holding as active binding law."
        ],
    },
    {
        "document_id": "DOC-US-IL-SC-2019-ROSENBACH-123186",
        "decision_id": "DEC-US-IL-SC-2019-ROSENBACH",
        "source_id": "SRC-US-IL-COURTS-OPINIONS",
        "document_type": "court_judgment",
        "canonical_title": "Rosenbach v. Six Flags Entertainment Corp., 2019 IL 123186, 129 N.E.3d 1197",
        "case_name": "Rosenbach v. Six Flags Entertainment Corp.",
        "jurisdiction_id": "US-IL",
        "parent_jurisdictions": ["US-FED"],
        "issuing_authority": "Supreme Court of Illinois",
        "issuing_authority_type": "court",
        "official_source_url": "https://www.illinoiscourts.gov/Resources/212233ca-1f60-4f08-899c-132f7f1f0c41/123186.pdf",
        "official_citation": "2019 IL 123186, 129 N.E.3d 1197",
        "neutral_citation": "2019 IL 123186",
        "docket_or_case_number": "Docket No. 123186",
        "decision_date": "2019-01-25",
        "publication_date": "2019-01-25",
        "effective_date": "2019-01-25",
        "appeal_status": "affirmed_as_binding_state_supreme_court_precedent",
        "binding_status": "binding_precedent",
        "parties": [
            "Stacy Rosenbach, as Mother and Next Friend of Alexander Rosenbach",
            "Six Flags Entertainment Corporation",
            "Great America LLC",
        ],
        "statutory_provisions_considered": [
            "740 ILCS 14/15(b)",
            "740 ILCS 14/20",
        ],
        "material_facts": (
            "Six Flags fingerprinted a 14-year-old theme park season-pass holder during enrollment "
            "without obtaining written informed consent or providing written disclosures regarding "
            "the specific purpose and length of term for which his biometric identifier was being "
            "collected, stored, and used under section 15(b) of the Illinois Biometric Information "
            "Privacy Act (BIPA)."
        ),
        "legal_issues": [
            "Whether an individual must plead and prove an actual injury or adverse consequence beyond a violation of statutory rights under the Illinois Biometric Information Privacy Act (740 ILCS 14/1 et seq.) in order to qualify as an 'aggrieved' person entitled to seek liquidated damages and injunctive relief under 740 ILCS 14/20."
        ],
        "normalized_text": (
            "CHIEF JUSTICE KARMEIER delivered the judgment of the court, with opinion. "
            "Through the Act, our General Assembly has codified that individuals possess a right to "
            "privacy in and control over their biometric identifiers and biometric information. "
            "The duties imposed on private entities by section 15 of the Act (740 ILCS 14/15) "
            "regarding the collection, retention, disclosure, and destruction of a person's or "
            "customer's biometric identifiers or biometric information define the contours of that "
            "statutory right. Accordingly, when a private entity fails to comply with one of section "
            "15's requirements, that violation constitutes an invasion, impairment, or denial of the "
            "statutory rights of any person or customer whose biometric identifier or biometric "
            "information is subject to the breach. Consistent with the authority cited above, such a "
            "person or customer would clearly be 'aggrieved' within the meaning of section 20 of the "
            "Act (740 ILCS 14/20) and entitled to seek recovery under that provision. No additional "
            "consequences need be pleaded or proved. The violation, in itself, is sufficient to "
            "support the individual's or customer's statutory cause of action."
        ),
        "legal_holdings": [
            "An individual need not allege or prove some actual injury or adverse effect, beyond violation of his or her rights under the Illinois Biometric Information Privacy Act (740 ILCS 14/15), in order to qualify as an 'aggrieved' person entitled to seek liquidated damages, attorneys' fees, and injunctive relief under 740 ILCS 14/20.",
            "A private entity's failure to comply with section 15's notice, written release, or retention-schedule requirements in itself constitutes an invasion, impairment, or denial of the statutory right to biometric privacy.",
        ],
        "dicta_and_commentary": [
            "The Court observed the General Assembly's legislative findings that biometrics are biologically unique and, unlike Social Security numbers, cannot be changed once compromised, noting that requiring plaintiffs to wait until a data breach or identity theft occurs before suing would be completely antithetical to BIPA's preventive and deterrent design."
        ],
        "operative_orders": [
            "Certified question answered in the negative; the judgment of the Illinois Appellate Court, Second District, is reversed, and the cause is remanded to the circuit court of Lake County for further proceedings."
        ],
        "remedies_and_penalties": [
            "Statutory standing established to pursue liquidated damages of $1,000 per negligent violation or $5,000 per intentional or reckless violation, plus reasonable attorneys' fees, costs, and injunctive relief under 740 ILCS 14/20."
        ],
        "subsequent_appeals": [],
        "reversals_or_modifications": [
            "Reverses Rosenbach v. Six Flags Entertainment Corp., 2017 IL App (2d) 170317."
        ],
        "practical_privacy_program_implications": [
            "Any collection of biometric identifiers or biometric information in Illinois without prior written informed consent and a publicly available retention/destruction schedule creates immediate statutory liability under 740 ILCS 14/20 without requiring plaintiffs to show downstream data compromise."
        ],
    },
    {
        "document_id": "DOC-US-IL-SC-2023-COTHRON-128004",
        "decision_id": "DEC-US-IL-SC-2023-COTHRON",
        "source_id": "SRC-US-IL-COURTS-OPINIONS",
        "document_type": "court_judgment",
        "canonical_title": "Cothron v. White Castle System, Inc., 2023 IL 128004, 216 N.E.3d 918",
        "case_name": "Cothron v. White Castle System, Inc.",
        "jurisdiction_id": "US-IL",
        "parent_jurisdictions": ["US-FED"],
        "issuing_authority": "Supreme Court of Illinois",
        "issuing_authority_type": "court",
        "official_source_url": "https://www.illinoiscourts.gov/Resources/08764f10-5782-4536-b623-07036d2d2952/128004.pdf",
        "official_citation": "2023 IL 128004, 216 N.E.3d 918",
        "neutral_citation": "2023 IL 128004",
        "docket_or_case_number": "Docket No. 128004",
        "decision_date": "2023-02-17",
        "publication_date": "2023-02-17",
        "effective_date": "2023-02-17",
        "appeal_status": "modified_by_subsequent_statute_pa_103_0769",
        "binding_status": "binding_precedent",
        "parties": [
            "Latrina Cothron",
            "White Castle System, Inc.",
        ],
        "statutory_provisions_considered": [
            "740 ILCS 14/15(b)",
            "740 ILCS 14/15(d)",
            "740 ILCS 14/20",
        ],
        "material_facts": (
            "On certified question from the U.S. Court of Appeals for the Seventh Circuit, a White "
            "Castle restaurant manager alleged that her employer required employees to scan their "
            "fingerprints to access pay stubs and computers and transmitted each scan to a third-party "
            "vendor without obtaining prior BIPA consent."
        ),
        "legal_issues": [
            "Whether claims under section 15(b) and 15(d) of the Illinois Biometric Information Privacy Act (740 ILCS 14/15(b), (d)) accrue only once upon the initial collection or disclosure of a person's biometric identifier, or each time a private entity scans or transmits the biometric identifier."
        ],
        "normalized_text": (
            "JUSTICE ROCHFORD delivered the judgment of the court, with opinion. "
            "We hold that the plain language of section 15(b) and 15(d) demonstrates that such "
            "violations occur with every scan or transmission. The party's policy-based concerns "
            "about potentially excessive damage awards under the Act are best addressed by the "
            "legislature. It also appears that the General Assembly chose to make damages "
            "discretionary rather than mandatory under the Act. Look to the language of section 20: "
            "'A prevailing party may recover for each violation' (emphasis added) (740 ILCS 14/20). "
            "There is no language in the Act suggesting legislative intent to authorize a damages "
            "award that would result in the financial destruction of a business."
        ),
        "legal_holdings": [
            "Under the plain text of 740 ILCS 14/15(b) and 14/15(d) as enacted prior to Public Act 103-0769, a separate claim accrues each time a private entity scans a person's biometric identifier or transmits such a scan to a third party without prior informed consent, rather than only upon the first scan or first transmission."
        ],
        "dicta_and_commentary": [
            "The Court observed in commentary that damages under 740 ILCS 14/20 ('may recover') appear to be discretionary rather than mandatory, noting that trial courts presiding over class actions possess equitable discretion to fashion awards that fairly compensate class members and deter future violations without destroying the defendant's business, and invited the Illinois General Assembly to explicitly address accrual and damages caps."
        ],
        "operative_orders": [
            "Certified question from the United States Court of Appeals for the Seventh Circuit answered in the affirmative (per-scan accrual under pre-amendment statutory text)."
        ],
        "remedies_and_penalties": [
            "Per-scan and per-transmission claim accrual under pre-2024 statutory text, subject to discretionary trial court damages assessment and subsequent prospective legislative modification under Illinois Public Act 103-0769 (effective August 2, 2024, limiting identical-method electronic collection or disclosure of the same biometric identifier to a single violation)."
        ],
        "subsequent_appeals": [],
        "reversals_or_modifications": [
            "Prospectively modified by statutory amendment in Illinois Public Act 103-0769 (SB 2979, amending 740 ILCS 14/20 effective August 2, 2024, to specify that repeated collection or electronic disclosure of the same biometric identifier using the same method constitutes a single violation)."
        ],
        "practical_privacy_program_implications": [
            "Distinguishes binding statutory construction holdings from judicial dicta regarding discretionary damages and links judicial interpretation directly to subsequent legislative amendment tracking (P.A. 103-0769)."
        ],
    },
    {
        "document_id": "DOC-US-CA-APP3-2024-CPPA-SUPERIOR-CT-C099130",
        "decision_id": "DEC-US-CA-APP3-2024-CPPA",
        "source_id": "SRC-US-CA-COURTS-OPINIONS",
        "document_type": "court_judgment",
        "canonical_title": "California Privacy Protection Agency v. Superior Court (California Chamber of Commerce), 99 Cal.App.5th 705 (2024)",
        "case_name": "California Privacy Protection Agency v. Superior Court",
        "jurisdiction_id": "US-CA",
        "parent_jurisdictions": ["US-FED"],
        "issuing_authority": "California Court of Appeal, Third Appellate District",
        "issuing_authority_type": "court",
        "official_source_url": "https://www.courts.ca.gov/opinions/archive/C099130.PDF",
        "official_citation": "99 Cal.App.5th 705 (2024)",
        "neutral_citation": "99 Cal.App.5th 705",
        "docket_or_case_number": "No. C099130",
        "decision_date": "2024-02-09",
        "publication_date": "2024-02-09",
        "effective_date": "2024-02-09",
        "appeal_status": "final_writ_granted_reversing_superior_court_injunction",
        "binding_status": "binding_precedent",
        "parties": [
            "California Privacy Protection Agency",
            "Rob Bonta, as Attorney General",
            "Superior Court of Sacramento County",
            "California Chamber of Commerce (Real Party in Interest)",
        ],
        "statutory_provisions_considered": [
            "Cal. Civ. Code § 1798.185(d)",
            "Proposition 24 (California Privacy Rights Act of 2020)",
        ],
        "material_facts": (
            "After the California Privacy Protection Agency (CPPA) adopted final CPRA regulations on "
            "March 29, 2023—nearly nine months after the July 1, 2022 statutory rulemaking deadline in "
            "Civil Code section 1798.185(d)—the Sacramento County Superior Court granted a writ of "
            "mandate Staying enforcement of any CPPA regulation for 12 months following the date that "
            "individual regulation is finalized."
        ),
        "legal_issues": [
            "Whether Civil Code section 1798.185(d) imposes a mandatory 12-month grace period between the CPPA's adoption of final CPRA regulations and the commencement of agency enforcement, despite containing no explicit text linking the July 1, 2022 rulemaking date to the July 1, 2023 enforcement date."
        ],
        "normalized_text": (
            "BOULWARE EURIE, J. The California Privacy Protection Agency (Agency) petitions for "
            "extraordinary writ relief from a trial court order effectively delaying for one year the "
            "Agency's ability to enforce regulations adopted nearly nine months after the July 1, 2022 "
            "deadline set forth in Civil Code section 1798.185, subdivision (d). Because the unambiguous "
            "language of the statute does not link the enforcement date of July 1, 2023, to the "
            "Agency's compliance with the July 1, 2022 rulemaking deadline, we will grant the petition "
            "and direct the trial court to vacate its order and judgment staying enforcement for 12 "
            "months after final regulations are adopted."
        ),
        "legal_holdings": [
            "Civil Code section 1798.185(d) does not require a 12-month delay between the CPPA's adoption of final CPRA regulations and the commencement of enforcement; the statute unambiguously set July 1, 2023 as the enforcement commencement date without conditioning enforcement on timely completion of rulemaking by July 1, 2022.",
            "Final CPPA regulations take effect upon approval by the Office of Administrative Law (OAL) and filing with the Secretary of State under the California Administrative Procedure Act, without any judicial 12-month enforcement stay.",
        ],
        "dicta_and_commentary": [
            "The Court noted in dicta that regulated entities remain free in individual enforcement proceedings to raise equitable defenses if a newly promulgated regulation imposes complex technical obligations with insufficient lead time, but such individualized equities cannot justify a facial 12-month blanket stay across all CPPA rulemakings."
        ],
        "operative_orders": [
            "Let a peremptory writ of mandate issue directing the respondent Superior Court of Sacramento County to vacate its June 30, 2023 order and judgment and to enter a new order denying the California Chamber of Commerce's petition for writ of mandate."
        ],
        "remedies_and_penalties": [
            "Immediate restoration of CPPA and California Attorney General authority to enforce finalized CPRA regulations upon OAL approval."
        ],
        "subsequent_appeals": [
            "Petition for review and request for depublication denied by the Supreme Court of California on May 1, 2024 (Case No. S284103)."
        ],
        "reversals_or_modifications": [
            "Vacates Sacramento County Superior Court order in California Chamber of Commerce v. California Privacy Protection Agency (Case No. 34-2023-80004106)."
        ],
        "practical_privacy_program_implications": [
            "Organizations subject to the CCPA/CPRA cannot rely on a 12-month grace period after new CPPA rules (including cybersecurity audits, risk assessments, and automated decision-making technology regulations) are approved by the Office of Administrative Law."
        ],
    },
]


def get_us_judicial_sources() -> List[RegulatorySourceEntry]:
    """Return the canonical list of official US federal and state judicial opinion sources."""
    return list(US_JUDICIAL_SOURCES)
