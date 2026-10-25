# Judicial, Tribunal & Regulator Decision Annotation Schema (`Section 6`)

## 1. Overview

KIBO Privacy OS enforces a strict, source-grounded schema for annotating statutory provisions ([`StatutoryProvisionAnnotator`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/annotations/statute_annotator.py)) and judicial/tribunal/regulator enforcement decisions ([`JudicialAndEnforcementAnnotator`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/annotations/decision_annotator.py)).

No annotation may invent facts, citations, or holdings outside the retrieved canonical document text. Every extracted rule or holding must carry exact character offsets (`text_start_offset`, `text_end_offset`) and a verbatim substring (`exact_source_excerpt`) verified against `CanonicalLegalDocument.normalized_text`.

---

## 2. Canonical Document Record (`CanonicalLegalDocument`)

Defined in [`kibo-is/core/regulatory_intelligence/__init__.py`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/__init__.py):

- `document_id`: Immutable canonical ID (e.g., `DOC-US-JUD-SCOTUS-TRANSUNION-2021`, `DOC-CA-OPC-PIPEDA-2021-001`, `DOC-EU-CJEU-C-634-21-SCHUFA`).
- `document_type`: `DocumentClassType` (`statute`, `regulation`, `regulatory_enforcement_decision`, `administrative_tribunal_ruling`, `court_judgment`, `consent_order_settlement`, `official_guidance`).
- `jurisdiction_id` & `parent_jurisdictions`: Canonical jurisdiction hierarchy (`US-FED`, `US-CA`, `CA-FED`, `CA-QC`, `CA-ON`, `EU`, `EU-DE`, `EU-FR`, etc.).
- `official_citation`, `neutral_citation`, `eli_or_celex_identifier`, `docket_or_case_number`.
- `raw_document_sha256` & `normalized_text_sha256`: Cryptographic SHA-256 hashes of raw bytes and NFC-normalized text.
- `language` & `translation_status`: Authoritative language metadata (`original_authoritative`, `official_bilingual_coauthoritative`, `official_translation`, `unverified_machine_translation`).
- `review_status`: `LegalPromotionState` (`DISCOVERED` -> `RETRIEVED` -> `VERIFIED_SOURCE` -> `ANNOTATED` -> `TECHNICALLY_VALIDATED` -> `LEGAL_REVIEW` -> `APPROVED` -> `ACTIVE`).

---

## 3. Statutory Provision Annotation (`LegalPassageAnnotation`)

Implemented by [`StatutoryProvisionAnnotator`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/annotations/statute_annotator.py):

- **Verbatim Grounding**: `source_section`, `exact_source_excerpt`, `text_start_offset`, `text_end_offset` where `normalized_text[text_start_offset:text_end_offset] == exact_source_excerpt`.
- **Deontic & Operational Classification**:
  - `normative_modality`: `obligation`, `prohibition`, `permission`, `right`, `exemption`, `definition`, `penalty_norm`.
  - `regulated_actors`: `controller`, `processor`, `business`, `service_provider`, `covered_entity`, `business_associate`, `health_information_custodian`, `public_body`, `credit_information_agency`, `employer`.
  - `protected_subjects`: `consumer`, `data_subject`, `employee`, `job_applicant`, `patient`, `child`, `minor`, `student`, `citizen`.
  - `regulated_data_categories`, `triggering_conditions`, `required_actions`, `prohibited_actions`, `statutory_deadlines`, `exemptions_and_thresholds`, `mapped_kibo_controls`.

---

## 4. Judicial & Enforcement Decision Annotation (`DecisionVerdictAnnotation`)

Implemented by [`JudicialAndEnforcementAnnotator`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/annotations/decision_annotator.py):

- **Holding vs. Obiter Dicta Separation (`RD-05`)**:
  - `legal_holdings`: Binding ratio decidendi / operative enforcement findings anchored to verbatim passages.
  - `obiter_dicta`: Non-binding judicial observations explicitly segregated so they are never promoted into mandatory compliance obligations.
- **Remedies, Sanctions & Corrective Orders (`RD-06`)**:
  - `monetary_penalties`: Fine amounts, currency, and statutory penalty basis.
  - `injunctive_or_corrective_orders`: Mandatory algorithmic disgorgement, opt-out honors, DPIA/EFVP orders, or retention deletion mandates.
  - `required_control_changes`: Mapped KIBO technical/organizational controls.
- **Precedential Weight & Appellate Reversal Tracking (`RD-07`)**:
  - `precedential_weight`: `binding_supreme_court`, `binding_appellate`, `binding_supranational_court`, `supervisory_enforcement_precedent`, `persuasive_authority`, `overturned_or_reversed`.
  - `appeal_status`: `final`, `affirmed`, `narrowed`, `reversed`, `overturned`.
  - `overturned_by_decision_id`: Explicit pointer when a lower-court decision (e.g., *Ramirez v. TransUnion LLC*, 951 F.3d 1008 (9th Cir. 2020)) is reversed by a higher court (*TransUnion LLC v. Ramirez*, 594 U.S. 413 (2021)), preventing overturned holdings from generating active compliance obligations.
