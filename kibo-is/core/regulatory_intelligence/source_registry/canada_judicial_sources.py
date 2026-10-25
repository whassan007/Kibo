"""
Canadian Court and Tribunal Decisions Source Registry (G09).

Covers authoritative judicial and appellate feeds for Canadian privacy,
data protection, Charter/Civil Code privacy rights, and PIPEDA / provincial
privacy judicial review:
- Supreme Court of Canada Judgments (decisions.scc-csc.ca)
- Federal Court of Canada & Federal Court of Appeal (decisions.fct-cf.gc.ca, decisions.fca-caf.gc.ca)
- Court of Appeal for Ontario (ontariocourts.ca)
- Cour d'appel du Québec & Cour du Québec (jugements.qc.ca)
- CanLII Authorized API (api.canlii.org) — strictly via authorized API key;
  automated HTML scraping is explicitly prohibited.
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.regulatory_intelligence import RegulatorySourceEntry, SourceHealthStatus


CANADA_JUDICIAL_SOURCES: List[RegulatorySourceEntry] = [
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-SCC-DECISIONS",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Supreme Court of Canada / Cour suprême du Canada",
        authority_type="court",
        official_domain="decisions.scc-csc.ca",
        discovery_endpoint="https://decisions.scc-csc.ca/scc-csc/en/rss/index.do",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) / Supreme Court of Canada Lexum Notice — non-commercial and commercial reproduction permitted with attribution and accuracy",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "constitutional_privacy", "civil_liability", "class_actions"],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en", "fr"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-FC-DECISIONS",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Federal Court of Canada / Cour fédérale du Canada",
        authority_type="court",
        official_domain="decisions.fct-cf.gc.ca",
        discovery_endpoint="https://decisions.fct-cf.gc.ca/fc-cf/en/rss/index.do",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — attribution and official neutral citation preservation required",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "pipeda_section_14_applications", "judicial_review", "access_to_information"],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en", "fr"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-FED-FCA-DECISIONS",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Federal Court of Appeal / Cour d'appel fédérale",
        authority_type="court",
        official_domain="decisions.fca-caf.gc.ca",
        discovery_endpoint="https://decisions.fca-caf.gc.ca/fca-caf/en/rss/index.do",
        feed_format="rss_atom",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Reproduction of Federal Law Order (SI/97-5) — attribution and official neutral citation preservation required",
        rate_limit_rpm=20,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "pipeda_appeals", "administrative_law", "cybersecurity"],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en", "fr"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-ON-ONCA-DECISIONS",
        jurisdiction_id="CA-ON",
        parent_jurisdiction="CA-FED",
        authority_name="Court of Appeal for Ontario",
        authority_type="court",
        official_domain="ontariocourts.ca",
        discovery_endpoint="https://www.ontariocourts.ca/coa/decisions_main/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="Court of Appeal for Ontario Official Decisions — public access judicial decisions; automated access via official RSS/structured index only",
        rate_limit_rpm=15,
        update_frequency="daily",
        publication_coverage=["privacy", "privacy_torts", "intrusion_upon_seclusion", "data_breach_class_actions", "phipa"],
        legal_instrument_types=["court_judgment"],
        source_priority=1,
        languages=["en", "fr"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-QC-SOQUIJ-JUGEMENTS",
        jurisdiction_id="CA-QC",
        parent_jurisdiction="CA-FED",
        authority_name="Cour d'appel du Québec & Cour du Québec (SOQUIJ)",
        authority_type="court",
        official_domain="jugements.qc.ca",
        discovery_endpoint="https://citoyens.soquij.qc.ca/",
        feed_format="html_structured",
        auth_requirements="public_unauthenticated",
        licensing_and_reuse="SOQUIJ / Tribunaux judiciaires du Québec — official public judgment repository; respect robots.txt and rate limits",
        rate_limit_rpm=15,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "quebec_law_25", "ccq_articles_35_41", "class_actions"],
        legal_instrument_types=["court_judgment", "administrative_tribunal_ruling"],
        source_priority=1,
        languages=["fr", "en"],
        health_status=SourceHealthStatus.HEALTHY,
    ),
    RegulatorySourceEntry(
        source_id="SRC-CA-CANLII-API",
        jurisdiction_id="CA-FED",
        parent_jurisdiction="CA-FED",
        authority_name="Canadian Legal Information Institute (CanLII)",
        authority_type="court",
        official_domain="api.canlii.org",
        discovery_endpoint="https://api.canlii.org/v1/caseBrowse/en/",
        feed_format="api_json",
        auth_requirements="api_key",
        licensing_and_reuse="CanLII Terms of Use & API License — automated web scraping of canlii.org is strictly prohibited; ONLY authorized API calls via api.canlii.org with a registered API key or direct court feeds are permitted",
        rate_limit_rpm=30,
        update_frequency="daily",
        publication_coverage=["privacy", "data_protection", "cybersecurity", "privacy_torts", "administrative_tribunals"],
        legal_instrument_types=["court_judgment", "administrative_tribunal_ruling"],
        source_priority=2,
        languages=["en", "fr"],
        health_status=SourceHealthStatus.REQUIRES_CREDENTIALS,
    ),
]


def get_canada_judicial_sources() -> List[RegulatorySourceEntry]:
    """Return a copy of the curated Canadian Court and Tribunal source registry entries."""
    return list(CANADA_JUDICIAL_SOURCES)


AUTHENTIC_CANADIAN_JUDICIAL_FIXTURES: List[Dict[str, Any]] = [
    {
        "decision_id": "DEC-CA-ONCA-2012-32",
        "document_id": "DOC-CA-ONCA-2012-32",
        "source_id": "SRC-CA-ON-ONCA-DECISIONS",
        "case_name": "Jones v. Tsige",
        "neutral_citation": "2012 ONCA 32",
        "official_citation": "108 O.R. (3d) 241",
        "docket_number": "C53311",
        "court_tribunal_or_regulator": "Court of Appeal for Ontario",
        "jurisdiction_id": "CA-ON",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2012-01-18",
        "official_source_url": "https://www.ontariocourts.ca/decisions/2012/2012ONCA0032.htm",
        "language": "en",
        "binding_status": "binding_precedent",
        "parties": ["Sandra Jones (Appellant)", "Winnie Tsige (Respondent)"],
        "material_facts": (
            "Winnie Tsige, a bank employee, used her workplace computer at Bank of Montreal to surreptitiously "
            "access the personal banking records and transaction history of fellow bank employee Sandra Jones at "
            "least 174 times over four years without authorization or legitimate business purpose."
        ),
        "legal_issues": [
            "Whether Ontario common law recognizes a right to bring a civil action for damages for invasion of personal privacy (intrusion upon seclusion).",
            "Whether the existence of federal and provincial privacy statutes (such as PIPEDA) forecloses the development of a common law privacy tort.",
            "What the elements and conventional damages range are for the tort of intrusion upon seclusion.",
        ],
        "statutory_provisions_considered": [
            "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5 (PIPEDA)",
            "Canadian Charter of Rights and Freedoms, s. 8",
            "Restatement (Second) of Torts (2010), § 652B",
        ],
        "legal_holdings": [
            "Ontario common law recognizes the tort of intrusion upon seclusion.",
            "The elements of intrusion upon seclusion are: (1) the defendant's conduct must be intentional or reckless; (2) the defendant must have invaded, without lawful justification, the plaintiff's private affairs or concerns; and (3) a reasonable person would regard the invasion as highly offensive causing distress, humiliation, or anguish.",
            "Proof of pecuniary loss is not an element of the cause of action; symbolic or moral damages for non-pecuniary harm are capped in a conventional range up to $20,000 absent aggravated or punitive circumstances.",
        ],
        "exact_source_excerpt": (
            "One who intentionally intrudes, physically or otherwise, upon the seclusion of another or his private "
            "affairs or concerns, is subject to liability to the other for invasion of his privacy, if the invasion "
            "would be highly offensive to a reasonable person."
        ),
        "source_section": "paras. 70-72",
        "remedies_and_penalties": [
            "Judgment granted in favour of the appellant Sandra Jones in the amount of $10,000 in damages for intrusion upon seclusion."
        ],
        "practical_privacy_program_implications": [
            "Organizations and insiders face civil tort liability for intentional or reckless unauthorized snooping into financial, health, biographical, or sensitive personal records.",
            "Role-based access controls (RBAC), employee audit logging, and proactive insider threat monitoring are essential to prevent unauthorized employee access.",
        ],
    },
    {
        "decision_id": "DEC-CA-ONCA-2022-813",
        "document_id": "DOC-CA-ONCA-2022-813",
        "source_id": "SRC-CA-ON-ONCA-DECISIONS",
        "case_name": "Owsianik v. Equifax Canada Co.",
        "neutral_citation": "2022 ONCA 813",
        "official_citation": "164 O.R. (3d) 497",
        "docket_number": "C69995 / C70160 / C70394",
        "court_tribunal_or_regulator": "Court of Appeal for Ontario",
        "jurisdiction_id": "CA-ON",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2022-11-25",
        "official_source_url": "https://www.ontariocourts.ca/decisions/2022/2022ONCA0813.htm",
        "language": "en",
        "binding_status": "binding_precedent",
        "parties": [
            "Motty Owsianik (Appellant)",
            "Equifax Canada Co. and Equifax Inc. (Respondents)",
        ],
        "material_facts": (
            "Companion appeals (Owsianik v. Equifax Canada Co., Obodo v. Trans Union of Canada, Inc., and Winder v. "
            "Marriott International, Inc.) arising from class actions where commercial database defendants stored "
            "personal information that was compromised by independent third-party criminal hackers."
        ),
        "legal_issues": [
            "Whether a commercial database custodian whose cybersecurity defences fail to prevent a third-party criminal cyberattack can be liable in tort for intrusion upon seclusion.",
            "Whether reckless failure to safeguard personal data satisfies the conduct element ('invaded, without lawful justification') when the actual intrusion is committed by an independent third-party hacker.",
        ],
        "statutory_provisions_considered": [
            "Class Proceedings Act, 1992, S.O. 1992, c. 6, s. 5(1)(a)",
            "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, Schedule 1, Principle 4.7 (Safeguards)",
        ],
        "legal_holdings": [
            "The tort of intrusion upon seclusion does not apply to 'database defendants' whose failure to maintain adequate security enables an independent third-party hacker to access plaintiffs' personal information.",
            "To be liable for intrusion upon seclusion, the defendant itself must commit the prohibited act of invading or intruding upon the plaintiff's privacy; a failure to prevent a third party's intrusion sounds in negligence or statutory breach, not the intentional tort of intrusion upon seclusion.",
            "Leave to appeal to the Supreme Court of Canada was subsequently dismissed on July 13, 2023 (SCC Docket Nos. 40575, 40577, 40590).",
        ],
        "exact_source_excerpt": (
            "Equifax's reckless storage of the plaintiffs' personal information cannot, at law, amount to an invasion "
            "of the plaintiffs' privacy by Equifax when third-party hackers access that information."
        ),
        "source_section": "paras. 54-63",
        "remedies_and_penalties": [
            "Appeals dismissed; certification of the intrusion upon seclusion claim against the database defendants refused (negligence claims requiring proof of compensable harm remain distinct)."
        ],
        "practical_privacy_program_implications": [
            "Clarifies class action exposure in Ontario data breaches: third-party hacker breaches Against database custodians are litigated under negligence and statutory frameworks rather than strict per se moral damages under intrusion upon seclusion.",
            "Does not diminish regulatory enforcement exposure under PIPEDA Principle 4.7 or Quebec Law 25 for inadequate security safeguards.",
        ],
    },
    {
        "decision_id": "DEC-CA-FCA-2024-140",
        "document_id": "DOC-CA-FCA-2024-140",
        "source_id": "SRC-CA-FED-FCA-DECISIONS",
        "case_name": "Canada (Privacy Commissioner) v. Facebook, Inc.",
        "neutral_citation": "2024 FCA 140",
        "official_citation": "2024 FCA 140",
        "docket_number": "A-129-23",
        "court_tribunal_or_regulator": "Federal Court of Appeal / Cour d'appel fédérale",
        "jurisdiction_id": "CA-FED",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2024-09-09",
        "official_source_url": "https://decisions.fca-caf.gc.ca/fca-caf/decisions/en/item/521614/index.do",
        "language": "en",
        "binding_status": "binding_precedent",
        "parties": [
            "Privacy Commissioner of Canada (Appellant)",
            "Facebook, Inc. (now Meta Platforms, Inc.) (Respondent)",
        ],
        "material_facts": (
            "Following the Cambridge Analytica investigation, the Privacy Commissioner of Canada brought an "
            "application under section 15 of PIPEDA alleging Facebook breached PIPEDA when third-party app "
            "'thisisyourdigitallife' (TYDL) accessed profile data of installing users and roughly 600,000 "
            "Canadian friends of installing users without meaningful consent or adequate safeguarding."
        ),
        "legal_issues": [
            "Whether Facebook obtained meaningful consent from users and friends of users under Clause 4.3 of Schedule 1 and section 6.1 of PIPEDA before disclosing personal information to third-party applications.",
            "Whether Facebook failed to adequately safeguard user personal information under Clause 4.7 of Schedule 1 to PIPEDA by relying on contractual terms without policing third-party app data governance practices.",
            "Whether the Federal Court erred by requiring expert or subjective user survey evidence to assess meaningful consent under an objective reasonable person standard.",
        ],
        "statutory_provisions_considered": [
            "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, s. 6.1",
            "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, s. 15",
            "Personal Information Protection and Electronic Documents Act, S.C. 2000, c. 5, Schedule 1, Clauses 4.3, 4.3.2, and 4.7",
        ],
        "legal_holdings": [
            "The Federal Court of Appeal reversed the Federal Court (2023 FC 533) and held that Facebook breached both its meaningful consent obligations (Clause 4.3 and s. 6.1) and its safeguarding obligations (Clause 4.7) under PIPEDA.",
            "Meaningful consent under PIPEDA is evaluated against an objective 'reasonable person' perspective; expert or empirical user evidence is not required for a court to determine whether lengthy, obscure, or bifurcated terms fail to provide meaningful notice.",
            "Friends of installing users had no opportunity to provide meaningful consent to the disclosure of their personal data to third-party apps.",
            "Contractual paper promises alone do not satisfy PIPEDA Principle 4.7 (Safeguards) when an organization grants third-party developers automated API access to millions of users' data without active oversight and technical enforcement.",
        ],
        "exact_source_excerpt": (
            "The perspective of the reasonable person is the lens through which a court determines whether "
            "an organization has obtained meaningful consent under PIPEDA."
        ),
        "source_section": "paras. 71-125",
        "remedies_and_penalties": [
            "Appeal allowed with costs; declaration issued that Facebook breached Clauses 4.3 and 4.7 of Schedule 1 and section 6.1 of PIPEDA between 2013 and 2015."
        ],
        "practical_privacy_program_implications": [
            "Bifurcated or buried privacy disclosures cannot establish meaningful consent under s. 6.1 and Principle 4.3 of PIPEDA; disclosures of third-party data sharing must be clear, upfront, and understandable to a reasonable person.",
            "Third-party API and vendor risk management under Principle 4.7 requires active technical monitoring and auditing of data recipients—relying solely on developer terms of service is legally insufficient.",
        ],
    },
    {
        "decision_id": "DEC-CA-SCC-2016-13",
        "document_id": "DOC-CA-SCC-2016-13",
        "source_id": "SRC-CA-FED-SCC-DECISIONS",
        "case_name": "Douez v. Facebook, Inc.",
        "neutral_citation": "2017 SCC 33",
        "official_citation": "[2017] 1 S.C.R. 751",
        "docket_number": "36616",
        "court_tribunal_or_regulator": "Supreme Court of Canada / Cour suprême du Canada",
        "jurisdiction_id": "CA-FED",
        "parent_jurisdictions": ["CA-FED"],
        "decision_date": "2017-06-23",
        "official_source_url": "https://decisions.scc-csc.ca/scc-csc/scc-csc/en/item/16700/index.do",
        "language": "en",
        "binding_status": "binding_precedent",
        "parties": [
            "Deborah Louise Douez (Appellant)",
            "Facebook, Inc. (Respondent)",
        ],
        "material_facts": (
            "A British Columbia resident brought a proposed class action under s. 3(2) of the British Columbia "
            "Privacy Act alleging Facebook used users' names and likenesses in 'Sponsored Stories' advertisements "
            "without consent. Facebook sought to stay the action based on a California forum selection clause in its "
            "online terms of use."
        ),
        "legal_issues": [
            "Whether a foreign forum selection clause in an online consumer contract of adhesion is enforceable to stay a statutory privacy tort class action brought under provincial privacy legislation.",
        ],
        "statutory_provisions_considered": [
            "Privacy Act, R.S.B.C. 1996, c. 373, s. 3(2), s. 4",
        ],
        "legal_holdings": [
            "Privacy rights have quasi-constitutional status in Canada; strong public policy considerations and gross inequality of bargaining power in consumer contracts of adhesion constitute 'strong cause' not to enforce a foreign forum selection clause against a statutory privacy claim.",
        ],
        "exact_source_excerpt": (
            "Privacy legislation has been accorded quasi-constitutional status in this Court's jurisprudence."
        ),
        "source_section": "paras. 50-63",
        "remedies_and_penalties": [
            "Appeal allowed; stay of proceedings set aside and BC statutory privacy class action permitted to proceed in British Columbia."
        ],
        "practical_privacy_program_implications": [
            "Global online platforms cannot rely on foreign forum selection clauses in standard consumer terms of service to oust Canadian courts' jurisdiction over Canadian statutory privacy rights.",
        ],
    },
]


__all__ = [
    "CANADA_JUDICIAL_SOURCES",
    "get_canada_judicial_sources",
    "AUTHENTIC_CANADIAN_JUDICIAL_FIXTURES",
]
