# C01 — US Regulatory Interpretation & Annotation Quality Adversarial Review

## 1. Execution Provenance & Provider Status

| Attribute | Value |
| :--- | :--- |
| **Worker ID** | `C01` (US Regulatory Interpretation & Annotation Quality Reviewer) |
| **Isolated Git Worktree** | `/tmp/kibo-hardening-worktrees/C01` |
| **Git Branch** | `hardening/v2026.10.1/C01-us-annotation-review` |
| **Primary Provider Invoked** | Local Claude CLI (`/Users/wael/.local/bin/claude`, v2.1.310) |
| **Primary Provider Exit Status** | Exit code `1` — `You've hit your monthly spend limit` |
| **Failover Execution** | Executed in-worktree by Antigravity C01 Subagent with full Python runtime verification against `kibo-is/core/regulatory_intelligence` |
| **Review Timestamp** | `2026-10-25T20:26:00Z` |

> **Honest Provenance Disclosure:** Local `/Users/wael/.local/bin/claude` CLI returned exit code `1` (`You've hit your monthly spend limit`) when invoked for the C01 adversarial review pass. In accordance with hardening governance rules, no simulated Claude output is claimed; this review was executed directly by the Antigravity C01 reviewer subagent using deterministic Python inspection and execution against the codebase in `/tmp/kibo-hardening-worktrees/C01`.

---

## 2. Executive Summary & Quantitative Verification Matrix

An adversarial code and runtime verification was conducted across the US regulatory source registries (`us_federal_sources.py`, `us_states_a_m_sources.py`, `us_states_n_w_dc_sources.py`, `us_enforcement_sources.py`, `us_judicial_sources.py`) and the deterministic annotation engines (`annotations/statute_annotator.py` and `annotations/decision_annotator.py`).

### Verified Artifact & Source Counts

| Registry / Module | Verified Count | Scope / Details |
| :--- | :---: | :--- |
| **`US_FEDERAL_SOURCES`** | **5** | `SRC-US-FED-FR`, `SRC-US-FED-ECFR`, `SRC-US-FED-GOVINFO`, `SRC-US-FED-CONGRESS`, `SRC-US-FED-NIST` (`US-FED`) |
| **`AUTHENTIC_US_FEDERAL_FIXTURES`** | **7** | `45_CFR_164_404`, `45_CFR_164_408`, `16_CFR_312_5`, `15_USC_45`, `15_USC_6802`, `34_CFR_99_30`, `5_USC_552A` |
| **`US_STATES_A_M_SOURCES`** | **53** | Covers **26** US states (`US-AL` through `US-MT`; 2 sources per state + 3 for `US-CA`) |
| **`US_STATES_N_W_DC_SOURCES`** | **40** | Covers **24** US states (`US-NE` through `US-WY`) + `US-DC` + **3** US territories (`US-PR`, `US-GU`, `US-VI`) = **28** jurisdictions |
| **Total US State + DC + Territory Sources** | **93** | Covers all **50 US states + DC + 3 territories = 54 distinct sub-federal jurisdictions** |
| **`AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES`** | **4** | Provision-level `ProvisionDiffRecord` fixtures (`RD-03`) for CA CCPA/CPRA/ADMT and CO CPA/AI Act |
| **`US_ENFORCEMENT_SOURCES`** | **12** | FTC, HHS OCR (Breach + Agreements), CalPrivacy/CPPA, CA OAG, NYDFS, TX OAG, CO OAG, CFPB, SEC, OCC, FRB |
| **`AUTHENTIC_US_ENFORCEMENT_FIXTURES`** | **6** | FTC GoodRx, FTC BetterHelp, CA OAG Sephora, CalPrivacy Advisory 2024-01, HHS OCR Montefiore, NYDFS Genesis |
| **`US_JUDICIAL_SOURCES`** | **5** | SCOTUS, GovInfo USCOURTS, CourtListener REST v4, CA Courts, IL Courts |
| **`AUTHENTIC_US_JUDICIAL_FIXTURES`** | **5** | *TransUnion v. Ramirez* (SCOTUS), *Ramirez v. TransUnion* (9th Cir.), *Rosenbach*, *Cothron*, *CPPA v. Superior Court* |

### Summary of Adversarial Findings

1. **[HIGH — Runtime `NameError` Defect in `statute_annotator.py`]:** In `kibo-is/core/regulatory_intelligence/annotations/statute_annotator.py` lines 699, 700, and 711 (inside `_match_concept_profile` Profile 7 generic fallback), the code references undefined variable `source_section` instead of `sec_lower` (or passing `source_section: str` into `_match_concept_profile`). When `StatutoryProvisionAnnotator().annotate_document()` is executed on `16_CFR_312_5` (COPPA), `15_USC_45` (FTC Act § 5), `15_USC_6802` (GLBA), `34_CFR_99_30` (FERPA), or `5_USC_552A` (Privacy Act), it raises `NameError: name 'source_section' is not defined`.
2. **[MEDIUM — HIPAA § 164.408 Concept Misclassification in `statute_annotator.py`]:** Profile 1 in `_match_concept_profile` matches `"unsecured protected health information" in text_lower and ("breach" in text_lower or "notify" in text_lower)` before distinguishing between `45 CFR § 164.404` (Notification to Individuals, 60-day deadline) and `45 CFR § 164.408` (Notification to the Secretary, 500-individual contemporaneous threshold vs. <500 annual log within 60 days of calendar year-end). As a result, `45_CFR_164_408` is mislabeled with `normalized_legal_concept="breach_notification_to_individuals_hipaa"` and omits the `500`-individual threshold in `thresholds`.
3. **[MEDIUM — Missing Authentic Judicial Fixtures for *Spokeo*, *Carpenter*, *Patel v. Facebook*, and *Dittman v. UPMC* & CalPrivacy *Honda* Enforcement Fixture]:**
   - While *Spokeo, Inc. v. Robins*, 578 U.S. 330 (2016) is cited inside the `normalized_text` of *TransUnion LLC v. Ramirez* (`us_judicial_sources.py:211`), neither *Spokeo*, *Carpenter v. United States* (585 U.S. 296 (2018)), *Patel v. Facebook, Inc.* (932 F.3d 1264 (9th Cir. 2019)), nor *Dittman v. UPMC* (649 Pa. 496, 196 A.3d 1036 (2018)) are present as standalone entries in `AUTHENTIC_US_JUDICIAL_FIXTURES`.
   - Similarly, in `AUTHENTIC_US_ENFORCEMENT_FIXTURES`, CalPrivacy is represented by `DEC-US-CA-CPPA-ADVISORY-2024-01` (Enforcement Advisory No. 2024-01 on Data Minimization) and CA OAG by `DEC-US-CA-OAG-SEPHORA-2022`, rather than the 2025 CalPrivacy *American Honda Motor Co.* stipulated final order.
4. **[MEDIUM — Overly Strict Exact-String Authority Matching in `decision_annotator.py`]:** `KNOWN_AUTHORITY_BINDING_MAP` in `decision_annotator.py:50-71` checks `if authority_key in KNOWN_AUTHORITY_BINDING_MAP:` using exact lowercase string equality before falling back to substring checks only when `doc.binding_status == "binding_precedent"` or `"administrative_order"`. Furthermore:
   - Typo in key `"departement of health and human services office for civil rights"` (`departement` vs. `department`), and the fixture uses `"U.S. Department of Health and Human Services — Office for Civil Rights (HHS OCR)"`.
   - Missing courts/regulators in `KNOWN_AUTHORITY_BINDING_MAP`: `"Supreme Court of Illinois"`, `"California Court of Appeal, Third Appellate District"`, `"New York State Department of Financial Services (NYDFS)"`, and `"California Department of Justice (Attorney General)"`. Consequently, *Rosenbach*, *Cothron*, *CPPA v. Superior Court*, and all 6 US enforcement fixtures default to `binding_vs_persuasive_status="requires_legal_review"` unless `binding_vs_persuasive_status` is explicitly passed in the fixture dict.
5. **[LOW — Case-Sensitivity Typos in Fixture Field Names]:**
   - `us_federal_sources.py:136` uses `"Statutory_deadline": "60 calendar days"` (capital `S`).
   - `us_states_a_m_sources.py:868` passes `Previous_sha256=prev_sha` (capital `P`) to `ProvisionDiffRecord`, which relies on Pydantic extra/default handling or field aliasing instead of lowercase `previous_sha256`.

---

## 3. US Federal (`US-FED`) & 50-State + DC + Territory Coverage Verification

### 3.1 US Federal (`US-FED`) Coverage (`us_federal_sources.py`)

- **Source Registry Entries (`US_FEDERAL_SOURCES` — 5 sources):**
  1. `SRC-US-FED-FR`: NARA Office of the Federal Register (`federalregister.gov`, `api_json`, 60 RPM, `every_6_hours`).
  2. `SRC-US-FED-ECFR`: GPO/OFR Electronic Code of Federal Regulations (`ecfr.gov`, `api_json`, covers 45 CFR Parts 160/164 HIPAA, 16 CFR Parts 312/313/314 COPPA/GLBA, 34 CFR Part 99 FERPA, 12 CFR Part 1016 Reg P).
  3. `SRC-US-FED-GOVINFO`: GPO GovInfo Bulk Data & USLM Statutes (`govinfo.gov`, `xml_akoma_ntoso`, covers HIPAA/HITECH, GLBA, FTC Act § 5, FCRA, Privacy Act of 1974, E-Government Act § 208, CIRCIA).
  4. `SRC-US-FED-CONGRESS`: Library of Congress `api.congress.gov` (`api_json`, federal legislative bills and amendments).
  5. `SRC-US-FED-NIST`: NIST Computer Security Resource Center (`csrc.nist.gov`, `rss_atom`, AI RMF, NIST Privacy Framework, SP 800-53).

- **Verbatim Statutory & Regulatory Fixtures (`AUTHENTIC_US_FEDERAL_FIXTURES` — 7 fixtures):**
  - All 7 fixtures (`45_CFR_164_404`, `45_CFR_164_408`, `16_CFR_312_5`, `15_USC_45`, `15_USC_6802`, `34_CFR_99_30`, `5_USC_552A`) contain authentic verbatim text from the U.S. Code / eCFR and deterministic SHA-256 digests (`compute_sha256_hex`).
  - **Adversarial Runtime Finding on `StatutoryProvisionAnnotator`:**
    - When `StatutoryProvisionAnnotator().annotate_document(doc)` is run across the 7 `AUTHENTIC_US_FEDERAL_FIXTURES`:
      - `45_CFR_164_404` succeeds (`1` annotation, `breach_notification_to_individuals_hipaa`, `VERIFIED`, `thresholds={'max_notification_delay_calendar_days': 60, 'statutory_timeframe_days': 60}`).
      - `45_CFR_164_408` succeeds syntactically (`1` annotation) but **misclassifies** Notification to the Secretary (`§ 164.408`) under the individual notification profile (`breach_notification_to_individuals_hipaa`) because `"unsecured protected health information"` and `"notify"` trigger Profile 1 (`statute_annotator.py:277`). It fails to extract the 500-individual threshold (`500 or more individuals` vs. `less than 500 individuals`) because `_extract_thresholds` (`statute_annotator.py:746`) requires comma-formatted numbers (`r"\b(\d{1,3}(?:,\d{3})+)\s+..."`), missing 3-digit numbers like `500`.
      - `16_CFR_312_5`, `15_USC_45`, `15_USC_6802`, `34_CFR_99_30`, and `5_USC_552A` **crash with `NameError: name 'source_section' is not defined`** at `statute_annotator.py:699` because they fall through to Profile 7 (generic statutory fallback), where `source_section` is referenced in the f-strings on lines 699, 700, and 711, even though the method parameter is named `sec_lower: str`.

### 3.2 US 50 States + DC + Territories Coverage (`us_states_a_m_sources.py` & `us_states_n_w_dc_sources.py`)

- **States A–M (`us_states_a_m_sources.py`):**
  - Verified **26** distinct state jurisdictions: `US-AL`, `US-AK`, `US-AZ`, `US-AR`, `US-CA`, `US-CO`, `US-CT`, `US-DE`, `US-FL`, `US-GA`, `US-HI`, `US-ID`, `US-IL`, `US-IN`, `US-IA`, `US-KS`, `US-KY`, `US-LA`, `US-ME`, `US-MD`, `US-MA`, `US-MI`, `US-MN`, `US-MS`, `US-MO`, `US-MT`.
  - Total sources: **53** (each state has both a primary legislature source and an Attorney General / administrative rule source; `US-CA` has 3: `SRC-US-CA-LEGINFO`, `SRC-US-CA-CPPA`, and `SRC-US-CA-OAG`).
- **States N–W + DC + Territories (`us_states_n_w_dc_sources.py`):**
  - Verified **24** distinct state jurisdictions (`US-NE`, `US-NV`, `US-NH`, `US-NJ`, `US-NM`, `US-NY`, `US-NC`, `US-ND`, `US-OH`, `US-OK`, `US-OR`, `US-PA`, `US-RI`, `US-SC`, `US-SD`, `US-TN`, `US-TX`, `US-UT`, `US-VT`, `US-VA`, `US-WA`, `US-WV`, `US-WI`, `US-WY`), plus **District of Columbia (`US-DC`)** and **3 US Territories (`US-PR`, `US-GU`, `US-VI`)** = **28** jurisdictions.
  - Total sources: **40**.
  - Specifically verified territory coverage:
    - `US-PR`: `SRC-US-PR-OGP-LAW111` (Puerto Rico Citizen Information on Data Banks Security Act, Law No. 111-2005, 10 L.P.R.A. § 4051 et seq., bilingual `["es", "en"]`).
    - `US-GU`: `SRC-US-GU-COMPILERS-9GCA48` (Guam Notification of Breaches of Personal Information Act, 9 GCA §§ 48-10 to 48-80).
    - `US-VI`: `SRC-US-VI-LEGISLATURE-14VIC2208` (U.S. Virgin Islands Breach of Security Law, 14 V.I.C. § 2208 et seq. & 11 V.I.C. § 1001).
- **Combined Jurisdictional Completeness:** `26 + 28 = 54` distinct sub-federal jurisdictions (`50` states + `1` federal district + `3` territories), all linked to `parent_jurisdiction="US-FED"` with `SourceHealthStatus.HEALTHY`.

---

## 4. Judicial Opinions: Holding vs. Dicta Separation (`RD-05`) & Appellate Reversal Tracking (`RD-07`)

### 4.1 *TransUnion LLC v. Ramirez*, 594 U.S. 413 (2021) Reversing *Ramirez v. TransUnion LLC*, 951 F.3d 1008 (9th Cir. 2020)

- **Fixture & Annotator Verification (`us_judicial_sources.py:165-311`, `decision_annotator.py`):**
  - **SCOTUS Decision (`DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413` / `DEC-US-FED-SCOTUS-2021-TRANSUNION`):**
    - Accurately models the class bifurcation: **1,853** class members whose credit reports with misleading OFAC alerts were disseminated to third-party creditors suffered concrete Article III reputational harm analogous to defamation, whereas the remaining **6,332** class members whose internal credit files were never disseminated lacked Article III standing ("No concrete harm, no standing").
    - Accurately captures the 15 U.S.C. § 1681g disclosure formatting holding (absent class members lacked concrete informational injury without evidence of opening mailings or confusion).
    - **Holding vs. Dicta Separation (`RD-05`):** Strictly separates the 4 binding Article III / FCRA holdings (`legal_holdings`) from the 2 non-binding observations (`dicta_and_commentary`): (1) Footnote 6 hypothetical regarding third-party printing vendor publication not preserved at trial, and (2) general observation contrasting forward-looking injunctive relief for imminent risk with retrospective damages claims.
    - **Passage Annotation Verification:** `JudicialAndEnforcementAnnotator.annotate_decision()` produces `LegalPassageAnnotation` records with `annotation_type="judicial_holding"`, `"judicial_dicta"` (explicitly prefixed `"Non-binding dicta/commentary (not an enforceable requirement): ..."` and `evidence_strength="non_binding_dicta_or_commentary"`), and `"remedy_order"`.
  - **Ninth Circuit Reversed Decision (`DOC-US-FED-CA9-2020-RAMIREZ-951-F3D-1008` / `DEC-US-FED-CA9-2020-RAMIREZ`):**
    - Preserved in `AUTHENTIC_US_JUDICIAL_FIXTURES` (never deleted).
    - Marked with `appeal_status="reversed"`, `binding_status="superseded_or_reversed_precedent"`, `subsequent_appeals=["TransUnion LLC v. Ramirez, 594 U.S. 413 (2021) (DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413)"]`, and `is_amended_by=["DOC-US-FED-SCOTUS-2021-TRANSUNION-594-US-413"]`.
    - When passed through `JudicialAndEnforcementAnnotator.annotate_decision()`, `_resolve_review_status` (`decision_annotator.py:805-809`) detects `doc.appeal_status == "reversed"` and `"Reversed"` in `reversals_or_modifications`, automatically setting `review_status = LegalPromotionState.REQUIRES_LEGAL_REVIEW`.
    - Furthermore, `mark_decision_reversed_or_modified(earlier_decision, appellate_decision)` (`decision_annotator.py:312-386`) deterministically cross-links both records and forces `earlier_decision.binding_vs_persuasive_status = "requires_legal_review"` and `earlier_decision.review_status = LegalPromotionState.REQUIRES_LEGAL_REVIEW`.
    - **Minor Quirk:** In `annotate_decision()` alone (prior to calling `mark_decision_reversed_or_modified`), `DEC-US-FED-CA9-2020-RAMIREZ` resolves `binding_vs_persuasive_status = "binding_precedent"` because `_resolve_binding_status` (`decision_annotator.py:744`) checks `if authority_key in KNOWN_AUTHORITY_BINDING_MAP:` *before* checking whether `doc.binding_status == "superseded_or_reversed_precedent"` or `doc.appeal_status == "reversed"`. Although `review_status` is properly gated as `REQUIRES_LEGAL_REVIEW`, `_resolve_binding_status` should check `doc.appeal_status in ("reversed", "vacated")` and `doc.binding_status == "superseded_or_reversed_precedent"` first.

### 4.2 Other Judicial Decisions in Registry (*Rosenbach*, *Cothron*, *CPPA v. Superior Court*) vs. Missing Landmark Cases (*Spokeo*, *Carpenter*, *Patel v. Facebook*, *Dittman v. UPMC*)

- **Present & Verified in `us_judicial_sources.py`:**
  1. ***Rosenbach v. Six Flags Entertainment Corp.*, 2019 IL 123186, 129 N.E.3d 1197 (`DEC-US-IL-SC-2019-ROSENBACH`):** Accurately separates the holding (violation of 740 ILCS 14/15 suffices to make a person "aggrieved" under 740 ILCS 14/20 without pleading actual downstream injury) from legislative-intent commentary on biometric uniqueness.
  2. ***Cothron v. White Castle System, Inc.*, 2023 IL 128004, 216 N.E.3d 918 (`DEC-US-IL-SC-2023-COTHRON`):** Exemplary `RD-05` and `RD-07` modeling: separates the per-scan/per-transmission accrual holding under pre-2024 statutory text from the Court's dicta that trial court damages under § 20 ("may recover") are discretionary, and explicitly tracks the prospective statutory modification by **Illinois Public Act 103-0769 (SB 2979, effective August 2, 2024)**.
  3. ***California Privacy Protection Agency v. Superior Court*, 99 Cal.App.5th 705 (2024) (`DEC-US-CA-APP3-2024-CPPA`):** Accurately separates the holding vacating the Sacramento Superior Court's 12-month enforcement stay under Cal. Civ. Code § 1798.185(d) from dicta regarding individualized equitable defenses in future enforcement actions.
- **Missing Standalone Fixtures Identified by Adversarial Audit:**
  - ***Spokeo, Inc. v. Robins*, 578 U.S. 330 (2016):** Cited inside the *TransUnion* excerpt (`us_judicial_sources.py:211`), but not included as a standalone fixture in `AUTHENTIC_US_JUDICIAL_FIXTURES`.
  - ***Carpenter v. United States*, 585 U.S. 296 (2018):** Fourth Amendment reasonable expectation of privacy in historical cell-site location information (CSLI) — not present in `AUTHENTIC_US_JUDICIAL_FIXTURES`.
  - ***Patel v. Facebook, Inc.*, 932 F.3d 1264 (9th Cir. 2019):** Article III standing for Illinois BIPA facial-recognition template claims in federal court — not present in `AUTHENTIC_US_JUDICIAL_FIXTURES`.
  - ***Dittman v. UPMC*, 649 Pa. 496, 196 A.3d 1036 (2018):** Pennsylvania Supreme Court recognition of an employer's common-law duty of reasonable care to safeguard employees' sensitive personal data stored on internet-accessible computer systems — not present in `AUTHENTIC_US_JUDICIAL_FIXTURES`.

---

## 5. US Regulatory Enforcement Annotations (`RD-06`)

### 5.1 Source Registry & Fixture Verification (`us_enforcement_sources.py`)

`US_ENFORCEMENT_SOURCES` provides **12** authoritative federal and state enforcement feeds (`SRC-US-FED-FTC-CASES`, `SRC-US-FED-HHS-OCR-BREACH`, `SRC-US-FED-HHS-OCR-AGREEMENTS`, `SRC-US-CA-CPPA-ENFORCEMENT`, `SRC-US-CA-OAG-CCPA-ENFORCEMENT`, `SRC-US-NY-DFS-ENFORCEMENT`, `SRC-US-TX-OAG-PRIVACY`, `SRC-US-CO-OAG-CPA`, `SRC-US-FED-CFPB-ENFORCEMENT`, `SRC-US-FED-SEC-CYBER-ENFORCEMENT`, `SRC-US-FED-OCC-ENFORCEMENT`, `SRC-US-FED-FRB-ENFORCEMENT`).

`AUTHENTIC_US_ENFORCEMENT_FIXTURES` contains **6** detailed enforcement fixtures:
1. **FTC — *United States v. GoodRx Holdings, Inc.* (`DEC-US-FTC-GOODRX-2023`, File No. 202-3090, 2023-02-01):**
   - Accurately cites 15 U.S.C. § 45(a) (FTC Act § 5) and 16 C.F.R. Part 318 (Health Breach Notification Rule — HBNR).
   - Accurately distinguishes the legal findings (unauthorized sharing of prescription/health condition data via tracking pixels/SDKs without affirmative express consent + failure to notify under HBNR) from operative orders (permanent ban on sharing health data for advertising, mandatory affirmative express consent, third-party data deletion, $1.5M civil penalty).
2. **FTC — *In the Matter of BetterHelp, Inc.* (`DEC-US-FTC-BETTERHELP-2023`, Docket No. C-4796, 2023-07-14):**
   - Accurately cites 15 U.S.C. § 45(a) and captures the holdings on deceptive privacy assurances for mental health intake questionnaires and failure to contractually limit third-party advertising uses, plus the $7.8M monetary relief and 20-year biennial assessment order.
3. **CA OAG — *People v. Sephora USA, Inc.* (`DEC-US-CA-OAG-SEPHORA-2022`, Case No. CGC-22-601380, 2022-08-24):**
   - Accurately cites Cal. Civ. Code §§ 1798.115, 1798.120, 1798.135, and 11 CCR § 7026(c) regarding third-party tracker "sales" and mandatory honoring of Global Privacy Control (GPC) signals, plus the $1.2M settlement penalty.
4. **CalPrivacy (CPPA) — *Enforcement Advisory No. 2024-01* (`DEC-US-CA-CPPA-ADVISORY-2024-01`, 2024-04-02):**
   - Accurately cites Cal. Civ. Code § 1798.100(c) and 11 CCR §§ 7002, 7060 on data minimization in consumer request verification.
   - **Coverage Gap Note (CalPrivacy *Honda* Action):** The task specification references CalPrivacy (*Honda*) — i.e., *In the Matter of American Honda Motor Co., Inc.* (CalPrivacy Stipulated Final Order, March 2025, $632,500 fine for excessive verification data on opt-out/limit requests, asymmetrical cookie consent banners, and missing service provider contracts). Currently, `us_enforcement_sources.py` includes CalPrivacy Enforcement Advisory No. 2024-01 (which established the exact data minimization principles later enforced against Honda) and the CA OAG *Sephora* action, but does not include a separate fixture for the *Honda* stipulated order.
5. **HHS OCR — *In the Matter of Montefiore Medical Center* (`DEC-US-HHS-OCR-MONTEFIORE-2024`, Ref. No. 15-210483, 2024-02-06):**
   - Accurately cites the HIPAA Security Rule provisions: 45 C.F.R. § 164.308(a)(1)(ii)(A) (Risk Analysis), § 164.308(a)(1)(ii)(D) (Information System Activity Review), and § 164.312(b) (Technical Audit Controls), along with the $4,750,000 settlement and 2-year Corrective Action Plan (CAP).
6. **NYDFS — *In the Matter of Genesis Global Trading, Inc.* (`DEC-US-NY-DFS-ENFORCEMENT` / `DEC-US-NY-DFS-GENESIS-2024`, 2024-01-12):**
   - Accurately cites 23 NYCRR §§ 500.02 (Cybersecurity Program), 500.03 (Cybersecurity Policy), 500.09 (Risk Assessment), and 500.14 (Training and Monitoring), and captures the BitLicense surrender and $8,000,000 civil monetary penalty.

### 5.2 Adversarial Finding on Enforcement Fixture Annotation (`decision_annotator.py`)

When the 6 `AUTHENTIC_US_ENFORCEMENT_FIXTURES` are annotated via `JudicialAndEnforcementAnnotator.annotate_decision(doc, ef)`:
- None of the 6 fixtures in `us_enforcement_sources.py` define a `"binding_vs_persuasive_status"` key or a `"remedies_and_penalties"` key (monetary penalties are instead listed as the last bullet inside `"operative_orders"`).
- Because `ef["court_tribunal_or_regulator"]` contains parenthetical acronyms or combined names (e.g., `"Federal Trade Commission (FTC) / U.S. District Court..."`, `"Federal Trade Commission (FTC)"`, `"U.S. Department of Health and Human Services — Office for Civil Rights (HHS OCR)"`, `"New York State Department of Financial Services (NYDFS)"`), exact lookup in `KNOWN_AUTHORITY_BINDING_MAP` (`decision_annotator.py:744`) misses every single one unless `doc.binding_status == "administrative_order"` is explicitly set on the `CanonicalLegalDocument`.

---

## 6. Statutory Amendment Diff Accuracy (`RD-03`)

In `us_states_a_m_sources.py:882-1050`, `AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES` defines **4** `ProvisionDiffRecord` fixtures:

1. **`DIFF-US-CA-CIV-1798-100-CPRA` (`Cal. Civ. Code § 1798.100` — CCPA AB 375 [2020-01-01] $\rightarrow$ CPRA Prop. 24 / AB 1008 [2023-01-01]):**
   - **Substantive Accuracy:** Accurately captures the shift from CCPA's general collection notice to CPRA's 3-prong notice at collection (`§ 1798.100(a)(1)-(3)`): (1) categories of PI and whether sold or shared, (2) categories of Sensitive Personal Information (SPI) and whether sold or shared, (3) retention period or criteria for each category, plus the overarching data minimization and purpose limitation mandate (`§ 1798.100(c)` — "reasonably necessary and proportionate").
   - **Cryptographic Integrity:** `previous_sha256` and `current_sha256` are deterministically computed via `compute_sha256_hex`.
2. **`DIFF-US-CA-CIV-1798-185-A15-A16-ADMT` (`Cal. Civ. Code § 1798.185(a)(15)-(16)` — CCPA [2020-01-01] $\rightarrow$ CPRA / 2026 CalPrivacy ADMT, Risk Assessment & Cybersecurity Audit Regulations `11 CCR §§ 7150-7222` [2026-01-01]):**
   - **Substantive Accuracy:** Accurately captures the statutory rulemaking mandate transferred from the Attorney General to CalPrivacy (CPPA) for (A) annual independent cybersecurity audits, (B) regular risk assessment submissions weighing consumer privacy risks against benefits, and (16) access and opt-out rights for Automated Decisionmaking Technology (ADMT) and profiling, including logic and likely outcome disclosures.
3. **`DIFF-US-CO-CRS-6-1-1306-UOOM` (`C.R.S. § 6-1-1306` — Colorado Privacy Act SB 21-190 [2023-07-01] $\rightarrow$ Mandatory Universal Opt-Out Mechanism Phase & HB 24-1130 / SB 24-041 Amendments [2025-07-01]):**
   - **Substantive Accuracy:** Accurately captures the transition from `C.R.S. § 6-1-1306(1)(a)(IV)(A)` ("Prior to July 1, 2024, a controller *may allow*...") to `(IV)(B)` ("Effective July 1, 2024, a controller... *shall allow* consumers to exercise the right to opt out... through a user-selected universal opt-out mechanism"), plus the 45-day denial justification and AG appeal notice under `§ 6-1-1306(3)`.
4. **`DIFF-US-CO-CRS-6-1-1703-AI-ACT` (`C.R.S. § 6-1-1703` — Colorado AI Act SB 24-205 [enacted May 17, 2024, original operative date 2026-02-01] $\rightarrow$ SB 25B-004 Operative Date Extension [2026-06-30]):**
   - **Substantive Accuracy:** Accurately reflects the special-session amendment (`SB 25B-004`) extending the deployer compliance date from **February 1, 2026** to **June 30, 2026**, alongside the substantive requirements for NIST AI RMF / ISO/IEC 42001 risk management alignment (`§ 6-1-1703(2)(a)`), pre-deployment/annual/90-day post-modification impact assessments (`§ 6-1-1703(3)(a)`), adverse consequential decision statements and human appeal (`§ 6-1-1703(4)(b)`), and 90-day Attorney General notification of discovered algorithmic discrimination (`§ 6-1-1703(7)`).

- **Schema Parameter Defect in `_build_diff_fixture` (`us_states_a_m_sources.py:868`):**
  - Line 868 passes `Previous_sha256=prev_sha` (capital `P`) to `ProvisionDiffRecord(...)`. While `ProvisionDiffRecord` in `core/regulatory_intelligence/__init__.py` defaults `previous_sha256: str = ""` so validation does not raise an exception, `record.model_dump()["previous_sha256"]` evaluates to `""` (empty string) instead of `prev_sha`! Let us verify this exact runtime behavior below:
    - Confirmed: Because `ProvisionDiffRecord` defines `previous_sha256: str = ""`, passing `Previous_sha256=prev_sha` leaves `previous_sha256` empty (`""`) on all 4 amendment diff fixtures.

---

## 7. Actionable Remediation Recommendations for Hardening Fix Pass

| Priority | File & Line(s) | Defect Summary | Recommended Fix |
| :---: | :--- | :--- | :--- |
| **P0 (High)** | `annotations/statute_annotator.py:699-711` | `NameError: name 'source_section' is not defined` in `_match_concept_profile` Profile 7 fallback when annotating COPPA, FTC Act § 5, GLBA, FERPA, and Privacy Act fixtures. | Pass `source_section: str` into `_match_concept_profile` or replace `source_section` with `sec_lower` on lines 699, 700, and 711; add explicit concept profiles for `45_CFR_164_408`, `16_CFR_312_5`, `15_USC_45`, `15_USC_6802`, `34_CFR_99_30`, and `5_USC_552A`. |
| **P1 (High)** | `source_registry/us_states_a_m_sources.py:868` | Typo `Previous_sha256=prev_sha` (capital `P`) in `_build_diff_fixture` causes `ProvisionDiffRecord.previous_sha256` to default to `""`. | Change `Previous_sha256=prev_sha` to `previous_sha256=prev_sha`. (Also change `"Statutory_deadline"` to `"statutory_deadline"` in `us_federal_sources.py:136`). |
| **P1 (Medium)** | `annotations/statute_annotator.py:274-333, 746` | `45 CFR § 164.408` (Notification to the Secretary, 500-individual threshold) matches Profile 1 (`164.404` Notification to Individuals) and misses un-comma-formatted `500 individuals`. | Add a dedicated profile for `45 CFR § 164.408` before Profile 1 and support `500 or more individuals` in `_extract_thresholds`. |
| **P2 (Medium)** | `annotations/decision_annotator.py:50-71, 741-765` | `KNOWN_AUTHORITY_BINDING_MAP` uses exact string matching, has typo `"departement"`, and omits IL Supreme Court, CA Court of Appeal, NYDFS, and CA OAG; also checks authority map before checking `appeal_status == "reversed"`. | Check `appeal_status` / `superseded_or_reversed_precedent` first in `_resolve_binding_status`; fix `"department"` typo; add substring matching and entries for IL Supreme Court, CA Court of Appeal, NYDFS, and state AGs. |
| **P2 (Medium)** | `source_registry/us_judicial_sources.py` & `us_enforcement_sources.py` | Missing standalone judicial fixtures for *Spokeo*, *Carpenter*, *Patel v. Facebook*, and *Dittman v. UPMC*, and CalPrivacy *Honda* enforcement fixture. | Add verbatim fixtures for *Spokeo* (578 U.S. 330), *Carpenter* (585 U.S. 296), *Patel v. Facebook* (932 F.3d 1264), *Dittman v. UPMC* (196 A.3d 1036), and CalPrivacy *American Honda Motor Co.* (2025). |
