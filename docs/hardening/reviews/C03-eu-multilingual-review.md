# C03 Adversarial Review: EU GDPR, Member-State & Multilingual Annotation Architecture

- **Worker ID**: `C03` (EU GDPR, Member-State & Multilingual Annotation Reviewer)
- **Worktree**: `/tmp/kibo-hardening-worktrees/C03`
- **Branch**: `hardening/v2026.10.1/C03-eu-multilingual-review`
- **Review Date**: `2026-10-25`
- **Execution Provenance**: Local Claude CLI (`/Users/wael/.local/bin/claude` v2.1.310) was invoked first and returned exit code `1` with error message `You've hit your monthly spend limit`. In accordance with hardening orchestration failover protocol, this adversarial legal-engineering review was executed directly in the isolated `C03` Git worktree by the Antigravity C03 subagent against the live source registry and parser modules.

---

## 1. Executive Summary & Adversarial Findings Matrix

This review audited seven core EU regulatory intelligence and multilingual parsing modules:
1. `kibo-is/core/regulatory_intelligence/source_registry/eu_union_sources.py`
2. `kibo-is/core/regulatory_intelligence/source_registry/eu_member_states_1_9.py`
3. `kibo-is/core/regulatory_intelligence/source_registry/eu_member_states_10_18.py`
4. `kibo-is/core/regulatory_intelligence/source_registry/eu_member_states_19_27.py`
5. `kibo-is/core/regulatory_intelligence/source_registry/eu_edpb_edps_cjeu_sources.py`
6. `kibo-is/core/regulatory_intelligence/source_registry/eu_national_dpa_sources.py`
7. `kibo-is/core/regulatory_intelligence/parsers/multilingual_parser.py`

### Summary of Findings

| Finding ID | Severity | Scope / File | Summary |
| :--- | :--- | :--- | :--- |
| **C03-F01** | **MEDIUM** | `eu_union_sources.py:296-297` | **NIS2 CELEX Sector/Type Mismatch**: `DOC-EU-DIR-2022-2555` sets `"eli_or_celex_identifier": "CELEX:32022R2555"` (`R` = Regulation) while `"celex_id": "32022L2555"` (`L` = Directive). NIS2 is Directive (EU) 2022/2555 (`32022L2555`). |
| **C03-F02** | **MEDIUM** | `eu_union_sources.py:381-429` | **ePrivacy Directive 2009/136/EC Amendment Lineage (`32009L0136`)**: `DOC-EU-DIR-2002-58` sets `"document_version": "2.0.0-CONS-2009-12-19"` and quotes the post-2009 Article 5(3) consent text, but omits an explicit `version_history` / `rd_04_version_diff` entry referencing amending Directive `2009/136/EC` (`CELEX:32009L0136`) or consolidated CELEX `02002L0058-20091219`. |
| **C03-F03** | **LOW** | `eu_union_sources.py:148-150` | **GDPR Consolidated vs. Corrigendum CELEX Notation**: `_build_gdpr_corrigendum_diff()` tracks `CELEX:32016R0679R(02)` (23 May 2018 Corrigendum) and `consolidated_eli_uri` (`https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04`), but does not explicitly store the EUR-Lex Sector `0` consolidated CELEX string `02016R0679-20160504` as a separate lookup key. |
| **C03-F04** | **LOW** | `eu_member_states_10_18.py:591-905` vs `eu_national_dpa_sources.py:126-534` | **German Länder Jurisdiction Prefix & Source ID Drift**: The 16 German Länder use `DE-BW` .. `DE-TH` (with `parent_jurisdiction="EU-DE"`) rather than `EU-DE-BW` .. `EU-DE-TH`. Additionally, `eu_member_states_10_18.py` includes all 17 Länder DPAs (including Bavarian public-sector `SRC-DE-BY-BAYLFD`) and uses `SRC-DE-NI-LFD` / `SRC-DE-SN-SAECHSDSB`, whereas `eu_national_dpa_sources.py` includes 16 Länder DPAs (omitting `BayLfD`) and spells the IDs `SRC-DE-NI-LFDI` and `SRC-DE-SN-SAechSDSB`. |
| **C03-F05** | **LOW** | `multilingual_parser.py:628-667` | **Translation Status Vocabulary (`verified_translation` vs `official_translation`)**: `MultilingualLegalParser.align_bilingual_or_translated_passages()` emits `"official_bilingual_coauthoritative"`, `"verified_translation"`, and `"unverified_machine_translation"` (preserving `is_translation_authoritative=False` for both `verified_translation` and `unverified_machine_translation`). Downstream schemas expecting the literal token `"official_translation"` should map `"verified_translation"` / `"official_bilingual_coauthoritative"` accordingly. |

---

## 2. EUR-Lex ELI / CELEX Versioning & Corrigendum Tracking (`RD-04`)

### 2.1 Union-Wide Source Registry (`eu_union_sources.py`)
`EU_UNION_SOURCES` defines 4 primary Union-level authorities (`jurisdiction_id="EU"`, `source_priority=1`, `languages=["en", "fr", "de"]`):
- `SRC-EU-UNION-EURLEX-ELI` (`eur-lex.europa.eu`, `xml_akoma_ntoso`, ELI endpoint `https://eur-lex.europa.eu/eli/reg/2016/679/oj`)
- `SRC-EU-UNION-CELLAR-SPARQL` (`publications.europa.eu`, `cellar_rdf`, SPARQL endpoint `https://publications.europa.eu/webapi/rdf/sparql`)
- `SRC-EU-EC-ADEQUACY-SCC` (`commission.europa.eu`, Adequacy Decisions & Standard Contractual Clauses, cursor `EC-DG-JUST-SCC-2021-914-DPF-2023-1795`)
- `SRC-EU-AI-OFFICE` (`digital-strategy.ec.europa.eu`, European AI Office DG CNECT)

### 2.2 Audit of the 5 Core EU Instruments in `AUTHENTIC_EURLEX_FIXTURES`

| Instrument | Document ID | `eli_or_celex_identifier` | `celex_id` | `eli_path` | Version / Corrigendum Tracking (`RD-04`) | Audit Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDPR** (Reg. 2016/679) | `DOC-EU-REG-2016-679` | `CELEX:32016R0679` | `32016R0679` | `eli/reg/2016/679/oj` | Tracks `1.0.0-OJ-L119-20160504` (`CELEX:32016R0679`) -> `1.1.0-CORR-OJ-L127-20180523` (`CELEX:32016R0679R(02)`), `consolidated_eli_uri="https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04"`, plus `_build_gdpr_corrigendum_diff()` with SHA-256 hashes for the Art. 37(1)(c) `"and"` -> `"or"` Corrigendum. | **PASS** (Minor note **C03-F03**: add explicit `02016R0679-20160504` consolidated CELEX alias). |
| **EU AI Act** (Reg. 2024/1689) | `DOC-EU-REG-2024-1689` | `CELEX:32024R1689` | `32024R1689` | `eli/reg/2024/1689/oj` | `1.0.0-OJ-L-20240712` (Published `2024-07-12`, effective `2024-08-01`). Includes EN/FR/DE aligned passages for Art. 5(1)(a) prohibited subliminal/manipulative AI practices. | **PASS** |
| **NIS2 Directive** (Dir. 2022/2555) | `DOC-EU-DIR-2022-2555` | `CELEX:32022R2555` (**Defect**) | `32022L2555` | `eli/dir/2022/2555/oj` | `1.0.0-OJ-L333-20221227` (Published `2022-12-27`, effective `2024-10-18`). Includes EN/FR/DE aligned passages for Art. 23(4)(a) 24-hour CSIRT early warning. | **FINDING C03-F01**: Fix `eli_or_celex_identifier` from `CELEX:32022R2555` to `CELEX:32022L2555`. |
| **DORA** (Reg. 2022/2554) | `DOC-EU-REG-2022-2554` | `CELEX:32022R2554` | `32022R2554` | `eli/reg/2022/2554/oj` | `1.0.0-OJ-L333-20221227` (Published `2022-12-27`, effective `2025-01-17`). Includes EN/FR/DE aligned passages for Art. 5(1) ICT risk governance framework. | **PASS** |
| **ePrivacy Directive** (Dir. 2002/58/EC) | `DOC-EU-DIR-2002-58` | `CELEX:32002L0058` | `32002L0058` | `eli/dir/2002/58/oj` | `2.0.0-CONS-2009-12-19`. Quotes the post-2009 Article 5(3) prior-consent rule across EN/FR/DE, but does not explicitly list `CELEX:32009L0136` (Citizens' Rights Directive 2009/136/EC) in a `version_history` array. | **FINDING C03-F02**: Add explicit `version_history` & `rd_04_version_diff` linking `32002L0058` -> `32009L0136` (`02002L0058-20091219`). |

### 2.3 CJEU, EDPB, and EDPS Authority Distinction (`eu_edpb_edps_cjeu_sources.py`)
- **CJEU (`SRC-EU-CJEU-INFOCURIA` & `SRC-EU-CJEU-EURLEX-CASELAW`)**: Properly typed as `court_judgment` across all 24 official EU languages. Authentic fixtures cover *Schrems II* (`C-311/18`, `ECLI:EU:C:2020:559`, `CELEX:62018CJ0311`), *UI v Österreichische Post* (`C-300/21`, `ECLI:EU:C:2023:370`, `CELEX:62021CJ0300`), and *SCHUFA Holding* (`C-634/21`, `ECLI:EU:C:2023:957`, `CELEX:62021CJ0634`).
- **EDPB (`SRC-EU-EDPB-ART65-DECISIONS` vs `SRC-EU-EDPB-ART70-GUIDELINES`)**: Strictly separates binding Article 65 dispute-resolution decisions (`regulatory_enforcement_decision`, e.g., Binding Decision 1/2021 on WhatsApp Ireland) from non-legislative Article 70 guidelines/recommendations (`official_guidance`, e.g., Recommendations 01/2020 v2.0 on supplementary transfer measures).
- **EDPS (`SRC-EU-EDPS-OPINIONS-DECISIONS`)**: Covers Regulation (EU) 2018/1725 supervision of EU institutions (including Case 2021-0518 on European Commission use of Microsoft 365).

---

## 3. Member-State & German Subnational Coverage Audit

Programmatic verification confirmed **100% coverage of all 27 EU Member States (`EU-AT` through `EU-SE`)** across both national legislatures/official gazettes and national Data Protection Authorities (DPAs):

### 3.1 All 27 EU Member States (`EU-AT` .. `EU-SE`)
1. **Austria (`EU-AT`)**: RIS (`SRC-EU-AT-RIS-DSG`, *Datenschutzgesetz — DSG*) + DSB (`SRC-EU-AT-DSB`).
2. **Belgium (`EU-BE`)**: Justel / Moniteur Belge (`SRC-EU-BE-JUSTEL-LOI-2018`, *Loi du 30 juillet 2018*) + APD/GBA (`SRC-EU-BE-APD-GBA`, *Chambre Contentieuse*).
3. **Bulgaria (`EU-BG`)**: State Gazette (`SRC-EU-BG-DV-ZZLD`, *ЗЗЛД*) + CPDP/КЗЛД (`SRC-EU-BG-CPDP`).
4. **Croatia (`EU-HR`)**: Narodne novine (`SRC-EU-HR-NN-ZPOUZP`, NN 42/2018) + AZOP (`SRC-EU-HR-AZOP`).
5. **Cyprus (`EU-CY`)**: CyLaw (`SRC-EU-CY-CYLAW-125-I-2018`, Law 125(I)/2018) + Commissioner (`SRC-EU-CY-DATAPROTECTION`).
6. **Czechia (`EU-CZ`)**: e-Sbírka (`SRC-EU-CZ-ESBIRKA-110-2019`, Act No. 110/2019 Coll.) + ÚOOÚ (`SRC-EU-CZ-UOOU`).
7. **Denmark (`EU-DK`)**: Retsinformation (`SRC-EU-DK-RETSINFO-DBL-502`, *Databeskyttelsesloven* Lov nr. 502) + Datatilsynet (`SRC-EU-DK-DATATILSYNET`).
8. **Estonia (`EU-EE`)**: Riigi Teataja (`SRC-EU-EE-RIIGITEATAJA-IKS`, *Isikuandmete kaitse seadus*) + AKI (`SRC-EU-EE-AKI`).
9. **Finland (`EU-FI`)**: Finlex (`SRC-EU-FI-FINLEX-1050-2018`, *Tietosuojalaki* 1050/2018) + Office of the Data Protection Ombudsman (`SRC-EU-FI-TIETOSUOJA`).
10. **France (`EU-FR`)**: Légifrance (`SRC-EU-FR-LEGIFRANCE-LIL`, *Loi n° 78-17 Informatique et Libertés* & `SRC-EU-FR-LEGIFRANCE-CNIL`) + CNIL (`SRC-EU-FR-CNIL`, `SRC-EU-FR-CNIL-SANCTIONS`).
11. **Germany Federal (`EU-DE`)**: Gesetze im Internet (`SRC-EU-DE-GII-BDSG` for *BDSG* and `SRC-EU-DE-GII-TDDDG` for *TDDDG*) + BfDI (`SRC-EU-DE-BFDI`).
12. **Greece (`EU-GR`)**: National Printing House (`SRC-EU-GR-ET-LAW4624`, Law 4624/2019) + HDPA/ΑΠΔΠΧ (`SRC-EU-GR-HDPA`).
13. **Hungary (`EU-HU`)**: NJT (`SRC-EU-HU-NJT-INFOACT`, Act CXII of 2011) + NAIH (`SRC-EU-HU-NAIH`).
14. **Ireland (`EU-IE`)**: Electronic Irish Statute Book (`SRC-EU-IE-ISB-DPA2018`, Data Protection Act 2018) + DPC (`SRC-EU-IE-DPC`, `SRC-EU-IE-DPC-DECISIONS`).
15. **Italy (`EU-IT`)**: Normattiva (`SRC-EU-IT-NORMATTIVA-CODICE`, D.Lgs. 196/2003 & D.Lgs. 101/2018) + Garante Privacy (`SRC-EU-IT-GARANTE`, `SRC-EU-IT-GARANTE-PROVVEDIMENTI`).
16. **Latvia (`EU-LV`)**: Likumi.lv (`SRC-EU-LV-LIKUMI-FPDAL`, *FPDAL*) + DVI (`SRC-EU-LV-DVI`).
17. **Lithuania (`EU-LT`)**: e-TAR (`SRC-EU-LT-ETAR-ADKTAI`, *ADTAĮ* Nr. XIII-1426) + VDAI (`SRC-EU-LT-VDAI`).
18. **Luxembourg (`EU-LU`)**: Legilux (`SRC-EU-LU-LEGILUX-DPA2018`, *Loi du 1er août 2018*) + CNPD (`SRC-EU-LU-CNPD`).
19. **Malta (`EU-MT`)**: Legislation Malta (`SRC-EU-MT-LEGISLATION`, Cap. 586) + IDPC (`SRC-EU-MT-IDPC`).
20. **Netherlands (`EU-NL`)**: Wettenbank (`SRC-EU-NL-WETTEN`, *UAVG*) + Autoriteit Persoonsgegevens (`SRC-EU-NL-AP-BESLUITEN`).
21. **Poland (`EU-PL`)**: ISAP Sejm (`SRC-EU-PL-ISAP`, *Ustawa o ochronie danych osobowych*) + UODO (`SRC-EU-PL-UODO`).
22. **Portugal (`EU-PT`)**: Diário da República (`SRC-EU-PT-DRE`, *Lei n.º 58/2019*) + CNPD (`SRC-EU-PT-CNPD`).
23. **Romania (`EU-RO`)**: Portal Legislativ (`SRC-EU-RO-LEGISLATIE`, Law No. 190/2018) + ANSPDCP (`SRC-EU-RO-ANSPDCP`).
24. **Slovakia (`EU-SK`)**: Slov-Lex (`SRC-EU-SK-SLOVLEX`, Act No. 18/2018 Coll.) + ÚOOÚ SR (`SRC-EU-SK-UOOU`).
25. **Slovenia (`EU-SI`)**: PISRS (`SRC-EU-SI-PISRS`, *ZVOP-2*) + IP RS (`SRC-EU-SI-IPRS`).
26. **Spain (`EU-ES`)**: BOE (`SRC-EU-ES-BOE`, *LOPDGDD Ley Orgánica 3/2018*) + AEPD (`SRC-EU-ES-AEPD-RESOLUCIONES`).
27. **Sweden (`EU-SE`)**: Sveriges riksdag (`SRC-EU-SE-RIKSDAGEN`, *Lag 2018:218*) + IMY (`SRC-EU-SE-IMY`).

### 3.2 German Federal & 16 Länder Statutes + 17 Länder Supervisory Authorities
In `eu_member_states_10_18.py` (`_GERMAN_LAENDER_SPEC` and `_build_german_laender_sources()`), all **16 German Länder statutory laws** and **17 Länder DPAs** (plus federal `BfDI`, totaling 18 German supervisory authorities) are registered:

| Land Code | State Name | State Statute (`LDSG`) Source ID | Supervisory Authority (`DPA`) Source ID | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `DE-BW` | Baden-Württemberg | `SRC-DE-BW-LAW-LDSG-BW` | `SRC-DE-BW-LFDI` | LfDI BW |
| `DE-BY` | Bayern (Bavaria) | `SRC-DE-BY-LAW-BAYDSG` | `SRC-DE-BY-BAYLDA` (Private) & `SRC-DE-BY-BAYLFD` (Public) | Dual DPA structure modeled in `eu_member_states_10_18.py`; `BayLfD` omitted in `eu_national_dpa_sources.py` (**C03-F04**). |
| `DE-BE` | Berlin | `SRC-DE-BE-LAW-BLNDSG` | `SRC-DE-BE-BLNBDI` | BlnBDI |
| `DE-BB` | Brandenburg | `SRC-DE-BB-LAW-BBGDSG` | `SRC-DE-BB-LDA` | LDA Brandenburg |
| `DE-HB` | Bremen | `SRC-DE-HB-LAW-BREMDSGVOAG` | `SRC-DE-HB-LFDI` | LfDI Bremen |
| `DE-HH` | Hamburg | `SRC-DE-HH-LAW-HMBDSG` | `SRC-DE-HH-HMBBFDI` | HmbBfDI |
| `DE-HE` | Hessen | `SRC-DE-HE-LAW-HDSIG` | `SRC-DE-HE-HBDI` | HBDI |
| `DE-MV` | Mecklenburg-Vorpommern | `SRC-DE-MV-LAW-DSG-M-V` | `SRC-DE-MV-LFDI` | LfDI M-V |
| `DE-NI` | Niedersachsen | `SRC-DE-NI-LAW-NDSG` | `SRC-DE-NI-LFD` / `SRC-DE-NI-LFDI` | ID spelling differs between `10_18` (`LFD`) and `national_dpa` (`LFDI`) (**C03-F04**). |
| `DE-NW` | Nordrhein-Westfalen | `SRC-DE-NW-LAW-DSG-NRW` | `SRC-DE-NW-LDI` | LDI NRW |
| `DE-RP` | Rheinland-Pfalz | `SRC-DE-RP-LAW-LDSG-RP` | `SRC-DE-RP-LFDI` | LfDI RLP |
| `DE-SL` | Saarland | `SRC-DE-SL-LAW-SDSG` | `SRC-DE-SL-ULD` | ULD Saarland |
| `DE-SN` | Sachsen | `SRC-DE-SN-LAW-SAECHSDSDG` | `SRC-DE-SN-SAECHSDSB` / `SRC-DE-SN-SAechSDSB` | Case sensitivity differs (`SAECHSDSB` vs `SAechSDSB`) (**C03-F04**). |
| `DE-ST` | Sachsen-Anhalt | `SRC-DE-ST-LAW-DSG-LSA` | `SRC-DE-ST-LFD` | LfD Sachsen-Anhalt |
| `DE-SH` | Schleswig-Holstein | `SRC-DE-SH-LAW-LDSG-SH` | `SRC-DE-SH-ULD` | ULD Schleswig-Holstein |
| `DE-TH` | Thüringen | `SRC-DE-TH-LAW-THUERDSG` | `SRC-DE-TH-TLFDI` | TLfDI |

---

## 4. Multilingual Alignment & Translation Authority Governance (`RD-08`)

### 4.1 Verification of Authentic German (`BDSG §§ 26, 38`) and French (`LIL Art. 82`) Fixtures
Programmatic execution against `AUTHENTIC_FR_DE_MULTILINGUAL_FIXTURES` in `eu_member_states_10_18.py` and `MultilingualLegalParser` in `parsers/multilingual_parser.py` verified exact character-offset slicing (`full_provision_text_original[text_start_offset:text_end_offset] == exact_source_excerpt`) and deterministic SHA-256 hashing:

1. **`EU-DE-BDSG-S26` (`DOC-EU-DE-BDSG-2018-S26`) — Employee Data Processing (`§ 26 Abs. 1 Satz 1 BDSG`)**:
   - **Original Language**: `de` (`eli/bund/bgbl-1/2017/s2097/2026-01-01/1/deu`)
   - **Verified Character Offsets**: `70:358` (`len = 288`), exact match for *"Personenbezogene Daten von Beschäftigten dürfen für Zwecke des Beschäftigungsverhältnisses verarbeitet werden..."*
   - **Authoritative Status**: German original is primary (`authoritative_source_is_original=True`); English translation is marked `is_translation_authoritative=False`.
2. **`EU-DE-BDSG-S38` (`DOC-EU-DE-BDSG-2018-S38`) — DPO Designation 20-Employee Threshold (`§ 38 Abs. 1 Satz 1 BDSG`)**:
   - **Original Language**: `de` (`eli/bund/bgbl-1/2017/s2097/2026-01-01/1/deu`)
   - **Verified Character Offsets**: `58:388` (`len = 330`), exact match for *"Ergänzend zu Artikel 37 Absatz 1 Buchstabe b und c der Verordnung (EU) 2016/679 benennen der Verantwortliche und der Auftragsverarbeiter..."*
   - **Structured Threshold**: `{"automated_processing_employee_count_min": 20}`.
   - **Authoritative Status**: German original is primary (`authoritative_source_is_original=True`); English translation is marked `is_translation_authoritative=False`.
3. **`EU-FR-LIL-ART82` (`DOC-EU-FR-LIL-78-17-ART82`) — Cookies & Trackers Prior Consent (`Loi n° 78-17 Art. 82, alinéa 4`)**:
   - **Original Language**: `fr` (`eli/loi/1978/1/6/78-17/jo/article_82`)
   - **Verified Character Offsets**: `507:797` (`len = 290`), exact match for *"Ces accès ou inscriptions ne peuvent avoir lieu qu'à condition que l'abonné ou la personne utilisatrice ait exprimé..."*
   - **Structured Threshold**: `{"strictly_necessary_communication_exemption": True}`.
   - **Authoritative Status**: French original is primary (`authoritative_source_is_original=True`); English translation is marked `is_translation_authoritative=False`.

### 4.2 Parser Governance Check (`MultilingualLegalParser.align_bilingual_or_translated_passages`)
- **Unicode & Whitespace Normalization**: `normalize_document()` applies `unicodedata.normalize("NFC", raw_text)`, strips BOM/zero-width characters, normalizes horizontal whitespace per line while preserving `\n\n` paragraph breaks, and records both `raw_document_sha256` and `normalized_text_sha256`.
- **24 EU Official Languages Supported**: `SUPPORTED_EU_AND_GLOBAL_LANGUAGES` covers all 24 EU official languages (`en`, `fr`, `de`, `es`, `it`, `nl`, `pl`, `pt`, `sv`, `da`, `fi`, `el`, `cs`, `ro`, `hu`, `bg`, `sk`, `hr`, `lt`, `sl`, `lv`, `et`, `ga`, `mt`).
- **Translation Authority Safeguard (`RD-08`)**:
  - When `verified_translation=False` and `official_bilingual_coauthoritative=False` (default), the parser assigns `translation_status="unverified_machine_translation"`, `is_translation_authoritative=False`, and `requires_legal_review_for_translation=True`.
  - When `verified_translation=True`, the parser assigns `translation_status="verified_translation"`, `is_translation_authoritative=False`, and `requires_legal_review_for_translation=False`, ensuring that even counsel-verified or official ministry English translations of national statutes (`BDSG`, `LIL`) never displace the legally authoritative German or French text (`authoritative_source_is_original=True`).
  - Only when `official_bilingual_coauthoritative=True` (e.g., EUR-Lex Union acts in EN/FR/DE or Canadian federal statutes) does `is_translation_authoritative` evaluate to `True`.

---

## 5. Concrete Remediation Recommendations

1. **Fix NIS2 CELEX Identifier (`eu_union_sources.py:296`)**:
   Change `"eli_or_celex_identifier": "CELEX:32022R2555"` to `"eli_or_celex_identifier": "CELEX:32022L2555"` in `DOC-EU-DIR-2022-2555`.
2. **Add ePrivacy Directive `32009L0136` Version History (`eu_union_sources.py:399-430`)**:
   Populate `version_history` and `rd_04_version_diff` on `DOC-EU-DIR-2002-58` to record original Directive `2002/58/EC` (`CELEX:32002L0058`), amending Directive `2009/136/EC` (`CELEX:32009L0136`), and consolidated CELEX `02002L0058-20091219`.
3. **Add Explicit Consolidated CELEX Field on GDPR (`eu_union_sources.py:148-151`)**:
   Include `"consolidated_celex_id": "02016R0679-20160504"` alongside `"eli_or_celex_identifier": "CELEX:32016R0679R(02)"`.
4. **Harmonize German Länder Source IDs & `BayLfD` Across Registry Modules (`eu_member_states_10_18.py` & `eu_national_dpa_sources.py`)**:
   Unify `SRC-DE-NI-LFD` / `SRC-DE-NI-LFDI` and `SRC-DE-SN-SAECHSDSB` / `SRC-DE-SN-SAechSDSB`, add `SRC-DE-BY-BAYLFD` to `EU_NATIONAL_DPA_SOURCES`, and support `EU-DE-*` jurisdiction aliases alongside `DE-*`.
