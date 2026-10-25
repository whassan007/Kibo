# Deterministic Citation Verification & Provenance Architecture (`RD-06`, `RD-10`)

## 1. Zero-Hallucination Design Principle

KIBO Privacy OS treats every LLM or automated annotation as an **untrusted candidate** until it passes deterministic verification in [`CitationVerificationService`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/citations/verifier.py) and [`AuthoritativePromotionGuard`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/verification/__init__.py).

---

## 2. Seven Mandatory Verification Dimensions

Every call to `CitationVerificationService.verify_citation(...)` evaluates all 7 dimensions against the SHA-256-indexed canonical corpus (`58` multi-jurisdictional canonical statutes, regulations, enforcement actions, and judicial opinions):

1. **`document_identity_verified`**: The target `CanonicalLegalDocument` exists in the authoritative document store with a valid 64-character SHA-256 hash (`raw_document_sha256` and `normalized_text_sha256`) and contains no fabricated markers.
2. **`citation_accuracy_verified`**: The supplied `citation_query` matches the document's `official_citation`, `neutral_citation`, `eli_or_celex_identifier`, or `docket_or_case_number`.
3. **`section_existence_verified`**: The claimed article, section, subsection, or paragraph token exists within the canonical document text.
4. **`passage_consistency_verified`**: The NFC-normalized `claimed_excerpt` is verified as an exact substring of `document.normalized_text`, returning deterministic `matched_offset_start` and `matched_offset_end`.
5. **`version_applicability_verified`**: The document version is active (not `SUPERSEDED`, `reversed`, or `overturned` without explicit historical query context).
6. **`authority_identity_verified`**: The claimed issuing authority matches the canonical legislature, regulator, DPA, commissioner, or court for that jurisdiction.
7. **`effective_date_relevance_verified`**: The document's `effective_date` and `repeal_or_expiry_date` are valid for the requested `as_of_date`.

If **any** of the 7 dimensions fails, `CitationVerificationResult.valid` is set to `False`, `status` is set to `DiscoveryStatusCode.UNVERIFIED`, and detailed `rejection_reasons` are recorded.

---

## 3. Negative Fixture Rejection Benchmark (`FABRICATED_NEGATIVE_TEST_FIXTURES`)

`CitationVerificationService.run_negative_fixture_suite()` continuously tests 10 adversarial negative fixtures covering every failure mode:

| Fixture ID | Failure Category | Expected Outcome | Verified Result |
|---|---|---|---|
| `NEG-01-NONEXISTENT-STATUTE` | Fabricated US Federal AI Privacy Act citation | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-02-HALLUCINATED-GDPR-ARTICLE` | Nonexistent GDPR Article 99a | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-03-ALTERED-STATUTORY-QUOTE` | Altered HIPAA breach notification deadline (`180 days` vs `60 days`) | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-04-WRONG-AUTHORITY-ATTRIBUTION` | Attributing California CCPA to FTC | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-05-OVERTURNED-PRECEDENT-AS-ACTIVE` | Citing reversed 9th Cir. *Ramirez v. TransUnion* holding as active binding law | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-06-SUPERSEDED-VERSION-MISMATCH` | Citing superseded version identifier | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-07-PRE-EFFECTIVE-DATE-CLAIM` | Claiming a future-effective statute was binding before its effective date | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-08-FAKE-CANADIAN-OPC-VERDICT` | Fabricated `verdict-auto-*` OPC decision | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-09-MISMATCHED-CELEX-IDENTIFIER` | Spoofed EUR-Lex CELEX number | `UNVERIFIED` (`valid=False`) | **100% Rejected** |
| `NEG-10-FABRICATED-CJEU-CASE` | Fictional CJEU docket number | `UNVERIFIED` (`valid=False`) | **100% Rejected** |

---

## 4. Authoritative Promotion Guard (`RD-10`, `RD-16`)

[`AuthoritativePromotionGuard.verify_candidate_record(...)`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/verification/__init__.py) enforces that:
- No candidate obligation, statutory annotation, or case-law holding can transition to `TECHNICALLY_VALIDATED`, `APPROVED`, or `ACTIVE` without all 7 citation dimensions passing (`valid=True`).
- Unverified machine translations (`unverified_machine_translation`) are automatically routed to `REQUIRES_LEGAL_REVIEW` (`RD-08`).
- Promotion to `APPROVED` / `ACTIVE` additionally requires human sign-off from an authorized role (`CPO`, `DPO`, `LEGAL`, `PRIVACY_COUNSEL`).
