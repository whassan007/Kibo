# Legislative Versioning, Amendment Diffing & Temporal Knowledge Graph (`RD-03`, `RD-04`, `RD-12`)

## 1. Structural Provision Diff Engine ([`versioning/__init__.py`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/versioning/__init__.py))

Implemented by [`StructuralVersionDiffEngine`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/versioning/__init__.py):

- **Content-Hash First**: Computes both `raw_sha256` and `normalized_sha256` for the prior and current provision text. Never infers a statutory change solely from a changed URL or retrieval timestamp.
- **Substantive vs. Editorial Classification**:
  - **Editorial Only (`EDITORIAL_ONLY`)**: Whitespace normalization, punctuation/hyphenation adjustments, capitalization fixes, or minor typographical corrigenda where normalized legal tokens and deontic modalities remain unchanged.
  - **Substantive Amendments (`SUBSTANTIVE_AMENDMENT`, `NEW_OBLIGATION`, `SCOPE_EXPANSION`, `DEADLINE_OR_THRESHOLD_CHANGE`, `REPEAL`)**: Detects changes in deontic modality (`shall`, `must`, `may not`), statutory deadlines (e.g., `60 calendar days`, `72 hours`, `45 days`), numerical/revenue thresholds, regulated roles, or newly added statutory rights/assessments.

---

## 2. Tracked Multi-Jurisdiction Amendment Chains

### 2.1 United States State Amendments (`RD-03`)
- **California (`US-CA`)**:
  - `v2020.1-CCPA` (eff. `2020-01-01`) -> `v2023.1-CPRA` (eff. `2023-01-01`, adding sensitive personal information, contractor/third-party DPA mandates under `Cal. Civ. Code § 1798.100(d)`, and CalPrivacy enforcement) -> `v2026.1-CPPA-ADMT-AUDIT` (eff. `2026-01-01`, adding mandatory Automated Decisionmaking Technology (ADMT) pre-use notices, opt-out rights, and annual cybersecurity audit / risk assessment mandates under `Cal. Civ. Code § 1798.185(a)(15)-(16)`).
- **Colorado (`US-CO`)**:
  - Colorado Privacy Act (`C.R.S. § 6-1-1301 et seq.`, eff. `2023-07-01`) -> Biometric/Neural Data & Minor Privacy Amendments + Colorado AI Act (`C.R.S. § 6-1-1701 et seq.`, eff. `2026-02-01`).

### 2.2 European Union EUR-Lex ELI/CELEX Versioning (`RD-04`)
- **GDPR (`32016R0679`)**:
  - Original OJ L 119 (`2016-05-04`, eff. `2018-05-25`, ELI `http://data.europa.eu/eli/reg/2016/679/oj`) vs. Consolidated Corrigendum (`02016R0679-20160504` / `2018-05-23`), preserving ELI, CELEX, and historical text without overwriting prior versions.
- **ePrivacy Directive (`32002L0058` -> `32009L0136`)**:
  - Tracks the Citizens' Rights Directive `2009/136/EC` amendment to Article 5(3) transforming terminal equipment storage from opt-out to prior informed consent (`02002L0058-20091219`).

---

## 3. Temporal Regulatory Knowledge Graph ([`legal_relations/__init__.py`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/legal_relations/__init__.py))

[`TemporalRegulatoryKnowledgeGraph`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/legal_relations/__init__.py) extends KIBO's SQLAlchemy ontology (`ontology_store.py`) with temporal version tables (`kg_laws`, `kg_provisions`, `kg_amendments`, `kg_decisions`, `kg_obligations`, `kg_controls`, `kg_edges`) and supports all 6 mandatory `RD-12` queries:

1. **`query_law_as_of(processing_activity_or_law_id, as_of_date)`**: Resolves the exact version governing a processing activity on `2025-03-01` (`v2023.1-CPRA`) vs. `2026-01-01` (`v2026.1-CPPA-ADMT-AUDIT`).
2. **`query_decisions_affecting_sector("CA-ON", "healthcare")`**: Returns IPC Ontario `PHIPA Decision 175` and `PHIPA Decision 110` governing Ontario hospitals (`Health Information Custodians`).
3. **`query_decisions_interpreting_provision("EU-DE", "Art. 22")`**: Returns German rulings (`CJEU Case C-634/21 / VG Wiesbaden SCHUFA Holding AG` and `BAG 9 AZR 383/19 / C-453/21 X-Fab Dresden`) interpreting GDPR Articles 22, 35, and 38.
4. **`query_regulations_effective_in_year("US-CA", 2026)`**: Returns California CPPA ADMT, Risk Assessment, and Cybersecurity Audit regulations taking effect in 2026.
5. **`query_organizations_affected_by_amendment(amendment_id)`**: Traverses `Amendment -> Provision -> Obligation -> ProcessingActivity -> Organization` to return affected tenants, controls, and triggered assessments.
6. **`query_overturned_or_reversed_decisions()`**: Returns appellate reversal chains (*Ramirez v. TransUnion LLC*, 951 F.3d 1008 (9th Cir. 2020) reversed by *TransUnion LLC v. Ramirez*, 594 U.S. 413 (2021)).
