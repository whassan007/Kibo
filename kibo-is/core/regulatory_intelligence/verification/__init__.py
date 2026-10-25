"""
KIBO Privacy OS — Independent Verification & Authoritative Promotion Guard (Worker G19)
Implements Section 6.4, RD-06, RD-10, and RD-14:
- Enforces that no LLM-proposed regulatory rule, statutory obligation, enforcement decision,
  or case-law holding can self-promote into the authoritative registry without a
  cryptographically and structurally verified `CitationVerificationResult(valid=True)`.
- Verifies all 7 mandatory citation provenance dimensions (`document_identity_verified`,
  `citation_accuracy_verified`, `section_existence_verified`, `passage_consistency_verified`,
  `version_applicability_verified`, `authority_identity_verified`, and
  `effective_date_relevance_verified`).
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    CitationVerificationResult,
    DecisionVerdictAnnotation,
    DiscoveryStatusCode,
    LegalPassageAnnotation,
    LegalPromotionState,
    VerificationStatus,
)
from core.regulatory_intelligence.citations.verifier import (
    CitationVerificationService,
    FABRICATED_NEGATIVE_TEST_FIXTURES,
)


class CandidatePromotionVerificationReport(BaseModel):
    """Structured result returned by `AuthoritativePromotionGuard.verify_candidate_record`."""
    candidate_id: str
    allowed: bool
    valid: bool
    status: DiscoveryStatusCode
    promotion_state: LegalPromotionState
    citation_verification: Optional[CitationVerificationResult] = None
    rejection_reasons: List[str] = Field(default_factory=list)
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class AuthoritativePromotionGuard:
    """
    RD-10 Authoritative Promotion Guard.

    Blocks any LLM-generated or unverified candidate regulatory obligation, rule,
    annotation, or decision from entering the authoritative registry unless:
    1. It includes or resolves to a verified `CitationVerificationResult` with `valid=True`
       and `status == DiscoveryStatusCode.OK`.
    2. All 7 mandatory provenance dimensions are `True`.
    3. If a `CanonicalLegalDocument` or citation query/excerpt is provided, re-verification
       by `CitationVerificationService.verify_citation(...)` succeeds deterministically.
    4. Unverified machine translations (`unverified_machine_translation`) are routed to
       `REQUIRES_LEGAL_REVIEW` rather than promoted as authoritative law (RD-08).
    """

    def __init__(
        self,
        citation_verifier: Optional[CitationVerificationService] = None,
    ) -> None:
        self.verifier = citation_verifier or CitationVerificationService()

    @staticmethod
    def _all_seven_dimensions_true(res: CitationVerificationResult) -> bool:
        return bool(
            res.valid
            and res.status == DiscoveryStatusCode.OK
            and res.document_identity_verified
            and res.citation_accuracy_verified
            and res.section_existence_verified
            and res.passage_consistency_verified
            and res.version_applicability_verified
            and res.authority_identity_verified
            and res.effective_date_relevance_verified
        )

    def verify_candidate_record(
        self,
        candidate_record: Union[Dict[str, Any], LegalPassageAnnotation, DecisionVerdictAnnotation, BaseModel],
        citation_result: Optional[CitationVerificationResult] = None,
        *,
        document: Optional[CanonicalLegalDocument] = None,
        as_of_date: Optional[date] = None,
        raise_on_failure: bool = False,
    ) -> CandidatePromotionVerificationReport:
        """
        Verifies whether a candidate regulatory rule, annotation, or decision record is
        eligible for promotion into the authoritative registry (`RD-10`).

        Any LLM-proposed regulatory decision or rule lacking a verified
        `CitationVerificationResult(valid=True)` is deterministically blocked (`allowed=False`,
        `valid=False`, `status=DiscoveryStatusCode.UNVERIFIED`, `promotion_state=REJECTED`).
        """
        if isinstance(candidate_record, BaseModel):
            record_dict = candidate_record.model_dump()
        elif isinstance(candidate_record, dict):
            record_dict = dict(candidate_record)
        else:
            record_dict = {}

        candidate_id = str(
            record_dict.get("annotation_id")
            or record_dict.get("decision_id")
            or record_dict.get("rule_id")
            or record_dict.get("document_id")
            or record_dict.get("id")
            or "CANDIDATE-UNKNOWN"
        )

        rejection_reasons: List[str] = []

        # Extract embedded CitationVerificationResult if passed inside the candidate dict
        embedded_cv = record_dict.get("citation_verification") or record_dict.get("verification_result")
        if citation_result is None and embedded_cv is not None:
            if isinstance(embedded_cv, CitationVerificationResult):
                citation_result = embedded_cv
            elif isinstance(embedded_cv, dict):
                try:
                    citation_result = CitationVerificationResult(**embedded_cv)
                except Exception as exc:
                    rejection_reasons.append(f"RD-10 violation: malformed citation_verification payload ({exc}).")

        # Extract citation fields from candidate record to perform or corroborate verification
        citation_query = str(
            record_dict.get("citation_query")
            or record_dict.get("official_citation")
            or record_dict.get("neutral_citation_or_id")
            or record_dict.get("neutral_citation")
            or record_dict.get("source_section")
            or record_dict.get("document_id")
            or ""
        ).strip()

        claimed_excerpt = str(
            record_dict.get("exact_source_excerpt")
            or record_dict.get("claimed_excerpt")
            or record_dict.get("verbatim_excerpt")
            or (
                record_dict["legal_holdings"][0]
                if isinstance(record_dict.get("legal_holdings"), list) and record_dict["legal_holdings"]
                else ""
            )
            or ""
        ).strip()

        claimed_section = (
            record_dict.get("claimed_section")
            or record_dict.get("source_section")
            or record_dict.get("article")
        )
        claimed_authority = (
            record_dict.get("claimed_authority")
            or record_dict.get("regulatory_authority")
            or record_dict.get("court_tribunal_or_regulator")
            or record_dict.get("issuing_authority")
        )
        claimed_version = record_dict.get("claimed_version") or record_dict.get("document_version")

        target_doc = document
        if target_doc is None and record_dict.get("document_id"):
            target_doc = self.verifier.get_canonical_document(str(record_dict["document_id"]))

        # If no pre-computed citation_result was supplied, check if we have enough data to run verify_citation
        # However, if the candidate explicitly marks itself as an unverified LLM proposal without citation_result
        # and lacks verifiable excerpt/citation, block immediately.
        if citation_result is None:
            if citation_query and claimed_excerpt:
                citation_result = self.verifier.verify_citation(
                    citation_query=citation_query,
                    claimed_excerpt=claimed_excerpt,
                    document=target_doc,
                    claimed_section=str(claimed_section) if claimed_section else None,
                    claimed_authority=str(claimed_authority) if claimed_authority else None,
                    claimed_version=str(claimed_version) if claimed_version else None,
                    as_of_date=as_of_date,
                )
            else:
                rejection_reasons.append(
                    "RD-10 violation: candidate regulatory record lacks a CitationVerificationResult(valid=True) and has no verifiable source citation/excerpt."
                )

        if citation_result is None:
            report = CandidatePromotionVerificationReport(
                candidate_id=candidate_id,
                allowed=False,
                valid=False,
                status=DiscoveryStatusCode.UNVERIFIED,
                promotion_state=LegalPromotionState.REJECTED,
                citation_verification=None,
                rejection_reasons=rejection_reasons,
            )
            if raise_on_failure:
                raise PermissionError("; ".join(rejection_reasons))
            return report

        # Even if a caller passed `citation_result`, verify that all 7 dimensions are True
        if not self._all_seven_dimensions_true(citation_result):
            rejection_reasons.extend(citation_result.rejection_reasons)
            rejection_reasons.append(
                "RD-10 violation: CitationVerificationResult is not valid across all 7 mandatory provenance dimensions."
            )

        # If citation_result claims valid=True, also cross-check against CitationVerificationService when excerpt & query or document exist
        if (
            self._all_seven_dimensions_true(citation_result)
            and (citation_query or citation_result.citation_query)
            and (claimed_excerpt or citation_result.matched_excerpt)
        ):
            recheck_doc = target_doc or (
                self.verifier.get_canonical_document(citation_result.document_id)
                if citation_result.document_id
                else None
            )
            recheck = self.verifier.verify_citation(
                citation_query=citation_result.citation_query or citation_query,
                claimed_excerpt=claimed_excerpt or (citation_result.matched_excerpt or ""),
                document=recheck_doc,
                claimed_section=str(claimed_section) if claimed_section else None,
                claimed_authority=str(claimed_authority) if claimed_authority else None,
                claimed_version=str(claimed_version) if claimed_version else None,
                as_of_date=as_of_date,
            )
            if not self._all_seven_dimensions_true(recheck):
                citation_result = recheck
                rejection_reasons.extend(recheck.rejection_reasons)
                rejection_reasons.append(
                    "RD-10 violation: independent re-verification of candidate citation failed."
                )
            else:
                citation_result = recheck

        # Check RD-08 translation governance: unverified machine translations cannot self-promote to authoritative law
        translation_status = str(record_dict.get("translation_status") or "").lower()
        if target_doc is not None and not translation_status:
            translation_status = (target_doc.translation_status or "").lower()
        if translation_status == "unverified_machine_translation":
            rejection_reasons.append(
                "RD-08 / RD-10 violation: unverified_machine_translation cannot be promoted as authoritative law without human legal review."
            )
            report = CandidatePromotionVerificationReport(
                candidate_id=candidate_id,
                allowed=False,
                valid=False,
                status=DiscoveryStatusCode.REQUIRES_LEGAL_REVIEW,
                promotion_state=LegalPromotionState.REQUIRES_LEGAL_REVIEW,
                citation_verification=citation_result,
                rejection_reasons=rejection_reasons,
            )
            if raise_on_failure:
                raise PermissionError("; ".join(rejection_reasons))
            return report

        allowed = len(rejection_reasons) == 0 and self._all_seven_dimensions_true(citation_result)
        report = CandidatePromotionVerificationReport(
            candidate_id=candidate_id,
            allowed=allowed,
            valid=allowed,
            status=DiscoveryStatusCode.OK if allowed else DiscoveryStatusCode.UNVERIFIED,
            promotion_state=(
                LegalPromotionState.TECHNICALLY_VALIDATED
                if allowed
                else LegalPromotionState.REJECTED
            ),
            citation_verification=citation_result,
            rejection_reasons=rejection_reasons,
        )
        if not allowed and raise_on_failure:
            raise PermissionError("; ".join(rejection_reasons))
        return report


__all__ = [
    "AuthoritativePromotionGuard",
    "CandidatePromotionVerificationReport",
    "CitationVerificationService",
    "FABRICATED_NEGATIVE_TEST_FIXTURES",
    "VerificationStatus",
]
