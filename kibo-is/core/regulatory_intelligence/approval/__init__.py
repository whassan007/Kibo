"""
KIBO Privacy OS — Legal Promotion Workflow Engine & Human-in-the-Loop Governance (Worker G21)
Implements RD-16 & Section 10:
- Manages the full state machine for `LegalPromotionState`:
  `DISCOVERED -> RETRIEVED -> VERIFIED_SOURCE -> ANNOTATED -> TECHNICALLY_VALIDATED -> LEGAL_REVIEW -> APPROVED -> ACTIVE`,
  plus `REJECTED`, `SUPERSEDED`, `SUSPENDED`, `REQUIRES_LEGAL_REVIEW`.
- Uses `AuthoritativePromotionGuard` (`core.regulatory_intelligence.verification`) so no
  candidate obligation or rule can transition to `APPROVED` or `ACTIVE` without:
  1. `CitationVerificationResult.status == VerificationStatus.VERIFIED` (i.e., `DiscoveryStatusCode.OK` / `valid=True`)
  2. Non-empty `source_hash` and `verbatim_quote`
  3. Explicit human reviewer sign-off (`reviewer_id`, `reviewer_role` in
     `{"CPO", "DPO", "LEGAL", "PRIVACY_COUNSEL"}`, `review_notes`, `timestamp`).
- Records an immutable, cryptographically hash-chained audit trail of every state transition
  (`PromotionTransitionAuditRecord`) and supports rejection (`REJECTED`), supersession
  (`SUPERSEDED`), and emergency suspension (`SUSPENDED`).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    CitationVerificationResult,
    DecisionAnnotation,
    DecisionVerdictAnnotation,
    DiscoveryStatusCode,
    LegalPassageAnnotation,
    LegalPromotionState,
    PromotionTransitionAuditRecord,
    ProvisionDiffRecord,
    StatutoryAnnotation,
    VerificationStatus,
    compute_sha256_hex,
)
from core.regulatory_intelligence.applicability import Obligation
from core.regulatory_intelligence.verification import (
    AuthoritativePromotionGuard,
    CandidatePromotionVerificationReport,
)


AUTHORIZED_HUMAN_REVIEWER_ROLES: Set[str] = {
    "CPO",
    "DPO",
    "LEGAL",
    "PRIVACY_COUNSEL",
}

LINEAR_PROMOTION_PIPELINE: Tuple[LegalPromotionState, ...] = (
    LegalPromotionState.DISCOVERED,
    LegalPromotionState.RETRIEVED,
    LegalPromotionState.VERIFIED_SOURCE,
    LegalPromotionState.ANNOTATED,
    LegalPromotionState.TECHNICALLY_VALIDATED,
    LegalPromotionState.LEGAL_REVIEW,
    LegalPromotionState.APPROVED,
    LegalPromotionState.ACTIVE,
)

ALLOWED_STATE_TRANSITIONS: Dict[LegalPromotionState, Set[LegalPromotionState]] = {
    LegalPromotionState.DISCOVERED: {
        LegalPromotionState.RETRIEVED,
        LegalPromotionState.REJECTED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.RETRIEVED: {
        LegalPromotionState.VERIFIED_SOURCE,
        LegalPromotionState.REJECTED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.VERIFIED_SOURCE: {
        LegalPromotionState.ANNOTATED,
        LegalPromotionState.REJECTED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.ANNOTATED: {
        LegalPromotionState.TECHNICALLY_VALIDATED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.REJECTED,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.TECHNICALLY_VALIDATED: {
        LegalPromotionState.LEGAL_REVIEW,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.APPROVED,
        LegalPromotionState.REJECTED,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.REQUIRES_LEGAL_REVIEW: {
        LegalPromotionState.LEGAL_REVIEW,
        LegalPromotionState.APPROVED,
        LegalPromotionState.REJECTED,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.LEGAL_REVIEW: {
        LegalPromotionState.APPROVED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.REJECTED,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
    },
    LegalPromotionState.APPROVED: {
        LegalPromotionState.ACTIVE,
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
        LegalPromotionState.REJECTED,
    },
    LegalPromotionState.ACTIVE: {
        LegalPromotionState.SUPERSEDED,
        LegalPromotionState.SUSPENDED,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
    },
    LegalPromotionState.SUSPENDED: {
        LegalPromotionState.LEGAL_REVIEW,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
        LegalPromotionState.REJECTED,
        LegalPromotionState.SUPERSEDED,
    },
    LegalPromotionState.REJECTED: {
        LegalPromotionState.LEGAL_REVIEW,
        LegalPromotionState.REQUIRES_LEGAL_REVIEW,
    },
    LegalPromotionState.SUPERSEDED: set(),
}


class HumanReviewSignOff(BaseModel):
    """Explicit human reviewer sign-off required by RD-16 before APPROVED / ACTIVE promotion."""
    reviewer_id: str
    reviewer_role: str = Field(..., description="Must be in {'CPO', 'DPO', 'LEGAL', 'PRIVACY_COUNSEL'}")
    review_notes: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ManagedPromotionItem(BaseModel):
    """State container tracked by `LegalPromotionWorkflowEngine`."""
    candidate_id: str
    state: LegalPromotionState = LegalPromotionState.DISCOVERED
    source_hash: str = ""
    verbatim_quote: str = ""
    citation_verification: Optional[CitationVerificationResult] = None
    human_signoff: Optional[HumanReviewSignOff] = None
    superseded_by_id: Optional[str] = None
    suspension_reason: Optional[str] = None
    rejection_reasons: List[str] = Field(default_factory=list)
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class LegalPromotionWorkflowEngine:
    """
    RD-16 & Section 10 — Human-in-the-Loop Legal Promotion Workflow Engine.

    Enforces:
    1. Complete state machine:
       `DISCOVERED -> RETRIEVED -> VERIFIED_SOURCE -> ANNOTATED -> TECHNICALLY_VALIDATED -> LEGAL_REVIEW -> APPROVED -> ACTIVE`,
       plus `REJECTED`, `SUPERSEDED`, `SUSPENDED`, `REQUIRES_LEGAL_REVIEW`.
    2. Integration with `AuthoritativePromotionGuard` (`core.regulatory_intelligence.verification`).
    3. Hard promotion gate for `APPROVED` and `ACTIVE`:
       - `CitationVerificationResult.status == VerificationStatus.VERIFIED` (`DiscoveryStatusCode.OK`) and `valid == True`
       - Non-empty `source_hash` and `verbatim_quote`
       - Explicit human reviewer sign-off (`reviewer_id`, `reviewer_role` in `{"CPO", "DPO", "LEGAL", "PRIVACY_COUNSEL"}`, `review_notes`, `timestamp`).
    4. Immutable hash-chained `PromotionTransitionAuditRecord` log for every transition.
    """

    def __init__(
        self,
        promotion_guard: Optional[AuthoritativePromotionGuard] = None,
    ) -> None:
        self.promotion_guard = promotion_guard or AuthoritativePromotionGuard()
        self._items: Dict[str, ManagedPromotionItem] = {}
        self._audit_log: List[PromotionTransitionAuditRecord] = []

    # ------------------------------------------------------------------
    # Registration & State Inspection
    # ------------------------------------------------------------------
    def register_candidate(
        self,
        candidate: Union[
            Dict[str, Any],
            StatutoryAnnotation,
            DecisionAnnotation,
            ProvisionDiffRecord,
            Obligation,
            CanonicalLegalDocument,
            str,
        ],
        *,
        initial_state: LegalPromotionState = LegalPromotionState.DISCOVERED,
        source_hash: Optional[str] = None,
        verbatim_quote: Optional[str] = None,
        citation_verification: Optional[CitationVerificationResult] = None,
        actor_id: str = "kibo-discovery-scheduler",
        actor_role: str = "SYSTEM",
        notes: str = "Initial candidate registration",
    ) -> ManagedPromotionItem:
        """Registers a candidate rule/obligation/annotation in the workflow engine."""
        cand_id, payload, inferred_hash, inferred_quote, inferred_cv = self._extract_candidate_fields(candidate)
        final_hash = (source_hash if source_hash is not None else inferred_hash).strip()
        final_quote = (verbatim_quote if verbatim_quote is not None else inferred_quote).strip()
        final_cv = citation_verification or inferred_cv

        item = ManagedPromotionItem(
            candidate_id=cand_id,
            state=initial_state,
            source_hash=final_hash,
            verbatim_quote=final_quote,
            citation_verification=final_cv,
            payload=payload,
        )
        self._items[cand_id] = item
        self._append_audit_record(
            candidate_id=cand_id,
            from_state=None,
            to_state=initial_state,
            actor_id=actor_id,
            actor_role=actor_role,
            review_notes=notes,
            source_hash=final_hash,
            verbatim_quote=final_quote,
            citation_verification=final_cv,
        )
        return item

    def get_candidate(self, candidate_id: str) -> ManagedPromotionItem:
        if candidate_id not in self._items:
            raise KeyError(f"Unknown candidate_id in promotion workflow: {candidate_id!r}")
        return self._items[candidate_id]

    def get_state(self, candidate_id: str) -> LegalPromotionState:
        return self.get_candidate(candidate_id).state

    def get_audit_trail(self, candidate_id: Optional[str] = None) -> List[PromotionTransitionAuditRecord]:
        """Returns an immutable copy of the transition audit log (filtered by `candidate_id` if provided)."""
        if candidate_id is None:
            return [rec.model_copy(deep=True) for rec in self._audit_log]
        return [rec.model_copy(deep=True) for rec in self._audit_log if rec.candidate_id == candidate_id]

    # ------------------------------------------------------------------
    # State Transitions & Promotion Gate Enforcement (RD-16)
    # ------------------------------------------------------------------
    def transition(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        target_state: Union[LegalPromotionState, str],
        *,
        citation_verification: Optional[CitationVerificationResult] = None,
        source_hash: Optional[str] = None,
        verbatim_quote: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        reviewer_role: Optional[str] = None,
        review_notes: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        superseded_by_id: Optional[str] = None,
        emergency_reason: Optional[str] = None,
        document: Optional[CanonicalLegalDocument] = None,
        auto_advance_intermediate: bool = False,
    ) -> ManagedPromotionItem:
        """
        Transitions a candidate to `target_state`, enforcing all RD-10 and RD-16 guards
        and recording an immutable `PromotionTransitionAuditRecord`.
        """
        to_state = (
            target_state
            if isinstance(target_state, LegalPromotionState)
            else LegalPromotionState(str(target_state).upper())
        )

        item = self._ensure_registered(
            candidate_or_id,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            citation_verification=citation_verification,
        )

        # Update item metadata if supplied on this transition call
        if source_hash is not None:
            item.source_hash = source_hash.strip()
        if verbatim_quote is not None:
            item.verbatim_quote = verbatim_quote.strip()
        if citation_verification is not None:
            item.citation_verification = citation_verification

        # Optionally advance through intermediate states when requested
        if auto_advance_intermediate and item.state != to_state:
            self._auto_advance_up_to_predecessor(item, to_state)

        from_state = item.state
        if from_state != to_state:
            allowed_next = ALLOWED_STATE_TRANSITIONS.get(from_state, set())
            if to_state not in allowed_next:
                raise ValueError(
                    f"Invalid LegalPromotionState transition for {item.candidate_id}: "
                    f"{from_state.value} -> {to_state.value}. Allowed from {from_state.value}: "
                    f"{sorted(s.value for s in allowed_next)}"
                )

        # Gate 1: VERIFIED_SOURCE requires non-empty source_hash
        if to_state == LegalPromotionState.VERIFIED_SOURCE:
            if not item.source_hash:
                raise PermissionError(
                    f"RD-16 violation: cannot transition {item.candidate_id} to VERIFIED_SOURCE without a non-empty source_hash."
                )

        # Gate 2: ANNOTATED requires non-empty verbatim_quote
        if to_state == LegalPromotionState.ANNOTATED:
            if not item.verbatim_quote:
                raise PermissionError(
                    f"RD-16 violation: cannot transition {item.candidate_id} to ANNOTATED without a non-empty verbatim_quote."
                )

        # Gate 3: TECHNICALLY_VALIDATED runs AuthoritativePromotionGuard
        if to_state == LegalPromotionState.TECHNICALLY_VALIDATED:
            self._enforce_technical_validation_gate(item, document=document)

        # Gate 4: APPROVED and ACTIVE require full RD-16 verification + human reviewer sign-off
        if to_state in (LegalPromotionState.APPROVED, LegalPromotionState.ACTIVE):
            self._enforce_human_promotion_gate(
                item=item,
                target_state=to_state,
                reviewer_id=reviewer_id,
                reviewer_role=reviewer_role,
                review_notes=review_notes,
                timestamp=timestamp,
                document=document,
            )

        if to_state == LegalPromotionState.SUPERSEDED and superseded_by_id:
            item.superseded_by_id = superseded_by_id
        if to_state == LegalPromotionState.SUSPENDED and emergency_reason:
            item.suspension_reason = emergency_reason

        actor = (
            reviewer_id
            or (item.human_signoff.reviewer_id if item.human_signoff else None)
            or "kibo-workflow-engine"
        )
        role = (
            reviewer_role
            or (item.human_signoff.reviewer_role if item.human_signoff else None)
            or "SYSTEM"
        )
        notes = (
            review_notes
            or emergency_reason
            or (item.human_signoff.review_notes if item.human_signoff else None)
            or f"State transition {from_state.value} -> {to_state.value}"
        )

        item.state = to_state
        item.updated_at = timestamp or datetime.now(timezone.utc)
        self._items[item.candidate_id] = item

        self._append_audit_record(
            candidate_id=item.candidate_id,
            from_state=from_state,
            to_state=to_state,
            actor_id=str(actor),
            actor_role=str(role).upper(),
            review_notes=str(notes),
            source_hash=item.source_hash,
            verbatim_quote=item.verbatim_quote,
            citation_verification=item.citation_verification,
            superseded_by_id=superseded_by_id,
            emergency_reason=emergency_reason,
            transitioned_at=timestamp,
        )
        return item

    # ------------------------------------------------------------------
    # High-Level Lifecycle Operations (Approve, Activate, Reject, Supersede, Suspend)
    # ------------------------------------------------------------------
    def approve(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        reviewer_id: str,
        reviewer_role: str,
        review_notes: str,
        timestamp: Optional[datetime] = None,
        citation_verification: Optional[CitationVerificationResult] = None,
        source_hash: Optional[str] = None,
        verbatim_quote: Optional[str] = None,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> ManagedPromotionItem:
        """
        Promotes a candidate to `LegalPromotionState.APPROVED` after verifying all RD-10 and
        RD-16 requirements (`CitationVerificationResult.status == VerificationStatus.VERIFIED`,
        non-empty `source_hash` and `verbatim_quote`, and authorized human reviewer sign-off).
        """
        return self.transition(
            candidate_or_id,
            LegalPromotionState.APPROVED,
            citation_verification=citation_verification,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            review_notes=review_notes,
            timestamp=timestamp,
            document=document,
            auto_advance_intermediate=True,
        )

    def activate(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        reviewer_id: Optional[str] = None,
        reviewer_role: Optional[str] = None,
        review_notes: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        citation_verification: Optional[CitationVerificationResult] = None,
        source_hash: Optional[str] = None,
        verbatim_quote: Optional[str] = None,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> ManagedPromotionItem:
        """
        Promotes an `APPROVED` candidate (or auto-advances a verified candidate with human
        sign-off) to `LegalPromotionState.ACTIVE`.
        """
        item = self._ensure_registered(
            candidate_or_id,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            citation_verification=citation_verification,
        )
        if item.state != LegalPromotionState.APPROVED:
            self.approve(
                item.candidate_id,
                reviewer_id=reviewer_id or (item.human_signoff.reviewer_id if item.human_signoff else ""),
                reviewer_role=reviewer_role or (item.human_signoff.reviewer_role if item.human_signoff else ""),
                review_notes=review_notes or (item.human_signoff.review_notes if item.human_signoff else ""),
                timestamp=timestamp,
                citation_verification=citation_verification,
                source_hash=source_hash,
                verbatim_quote=verbatim_quote,
                document=document,
            )
        return self.transition(
            item.candidate_id,
            LegalPromotionState.ACTIVE,
            citation_verification=citation_verification,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            review_notes=review_notes or "Activated in authoritative production JRAE registry",
            timestamp=timestamp,
            document=document,
        )

    def reject(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        reviewer_id: str = "legal-review-gate",
        reviewer_role: str = "LEGAL",
        review_notes: str = "Rejected during legal or citation verification review",
        rejection_reasons: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> ManagedPromotionItem:
        """Transitions a candidate to `LegalPromotionState.REJECTED` and logs the audit record."""
        item = self._ensure_registered(candidate_or_id)
        if rejection_reasons:
            item.rejection_reasons.extend(rejection_reasons)
        elif review_notes:
            item.rejection_reasons.append(review_notes)
        return self.transition(
            item.candidate_id,
            LegalPromotionState.REJECTED,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            review_notes=review_notes,
            timestamp=timestamp,
        )

    def supersede(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        superseded_by_id: str,
        reviewer_id: str = "legal-counsel",
        reviewer_role: str = "LEGAL",
        review_notes: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> ManagedPromotionItem:
        """
        Transitions an obligation/rule to `LegalPromotionState.SUPERSEDED` while preserving
        its historical record and linking `superseded_by_id`.
        """
        item = self._ensure_registered(candidate_or_id)
        if not superseded_by_id or not superseded_by_id.strip():
            raise ValueError("superseded_by_id must be non-empty when superseding a regulatory record.")
        notes = review_notes or f"Superseded by {superseded_by_id}"
        return self.transition(
            item.candidate_id,
            LegalPromotionState.SUPERSEDED,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            review_notes=notes,
            superseded_by_id=superseded_by_id.strip(),
            timestamp=timestamp,
        )

    def suspend(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        emergency_reason: str,
        reviewer_id: str = "emergency-legal-response",
        reviewer_role: str = "CPO",
        timestamp: Optional[datetime] = None,
    ) -> ManagedPromotionItem:
        """
        Emergency suspension (`LegalPromotionState.SUSPENDED`) when a regulation or judicial
        decision is stayed, enjoined, reversed on appeal, or flagged for urgent review.
        """
        item = self._ensure_registered(candidate_or_id)
        if not emergency_reason or not emergency_reason.strip():
            raise ValueError("emergency_reason must be non-empty for emergency suspension.")
        return self.transition(
            item.candidate_id,
            LegalPromotionState.SUSPENDED,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            review_notes=f"EMERGENCY SUSPENSION: {emergency_reason.strip()}",
            emergency_reason=emergency_reason.strip(),
            timestamp=timestamp,
        )

    # ------------------------------------------------------------------
    # Gate Validation Helpers
    # ------------------------------------------------------------------
    def _enforce_technical_validation_gate(
        self,
        item: ManagedPromotionItem,
        document: Optional[CanonicalLegalDocument] = None,
    ) -> None:
        if not item.source_hash or not item.source_hash.strip():
            raise PermissionError(
                f"RD-16 violation: candidate {item.candidate_id} lacks a non-empty source_hash."
            )
        if not item.verbatim_quote or not item.verbatim_quote.strip():
            raise PermissionError(
                f"RD-16 violation: candidate {item.candidate_id} lacks a non-empty verbatim_quote."
            )

        cv = item.citation_verification
        if cv is None:
            # Attempt verification through AuthoritativePromotionGuard
            guard_report = self.promotion_guard.verify_candidate_record(
                item.payload or {"id": item.candidate_id, "exact_source_excerpt": item.verbatim_quote},
                citation_result=None,
                document=document,
                raise_on_failure=False,
            )
            if not guard_report.allowed or guard_report.citation_verification is None:
                raise PermissionError(
                    f"RD-10 / RD-16 violation: candidate {item.candidate_id} failed AuthoritativePromotionGuard: "
                    f"{'; '.join(guard_report.rejection_reasons)}"
                )
            item.citation_verification = guard_report.citation_verification
            cv = item.citation_verification

        if not (
            cv.valid
            and cv.status == VerificationStatus.VERIFIED
            and AuthoritativePromotionGuard._all_seven_dimensions_true(cv)
        ):
            raise PermissionError(
                f"RD-10 / RD-16 violation: CitationVerificationResult for {item.candidate_id} is not VERIFIED "
                f"(status={cv.status}, valid={cv.valid}, reasons={cv.rejection_reasons})."
            )

    def _enforce_human_promotion_gate(
        self,
        item: ManagedPromotionItem,
        target_state: LegalPromotionState,
        reviewer_id: Optional[str],
        reviewer_role: Optional[str],
        review_notes: Optional[str],
        timestamp: Optional[datetime],
        document: Optional[CanonicalLegalDocument] = None,
    ) -> None:
        """
        Enforces RD-16 hard requirements before transitioning to `APPROVED` or `ACTIVE`:
        1. `CitationVerificationResult.status == VerificationStatus.VERIFIED` (`DiscoveryStatusCode.OK`) and all 7 provenance flags True
        2. Non-empty `source_hash` and `verbatim_quote`
        3. Explicit human reviewer sign-off (`reviewer_id`, `reviewer_role` in `{"CPO", "DPO", "LEGAL", "PRIVACY_COUNSEL"}`, `review_notes`, `timestamp`).
        """
        # 1 & 2: Verify citation and source_hash + verbatim_quote
        self._enforce_technical_validation_gate(item, document=document)

        # Also run AuthoritativePromotionGuard to ensure RD-08/RD-10 compliance
        if item.payload.get("translation_status") == "unverified_machine_translation":
            raise PermissionError(
                f"RD-08 / RD-16 violation: candidate {item.candidate_id} has unverified_machine_translation and cannot be promoted to {target_state.value}."
            )

        # 3: Verify human reviewer sign-off
        eff_reviewer_id = (reviewer_id if reviewer_id is not None else (item.human_signoff.reviewer_id if item.human_signoff else "")).strip()
        eff_reviewer_role = (reviewer_role if reviewer_role is not None else (item.human_signoff.reviewer_role if item.human_signoff else "")).strip().upper()
        eff_review_notes = (review_notes if review_notes is not None else (item.human_signoff.review_notes if item.human_signoff else "")).strip()
        eff_timestamp = timestamp or (item.human_signoff.timestamp if item.human_signoff else datetime.now(timezone.utc))

        if not eff_reviewer_id or eff_reviewer_id.lower() in {"system", "llm", "auto", "bot", "ai", "none"}:
            raise PermissionError(
                f"RD-16 violation: cannot promote {item.candidate_id} to {target_state.value} without an explicit human reviewer_id (got {eff_reviewer_id!r})."
            )
        if eff_reviewer_role not in AUTHORIZED_HUMAN_REVIEWER_ROLES:
            raise PermissionError(
                f"RD-16 violation: reviewer_role {eff_reviewer_role!r} is not authorized to promote {item.candidate_id} to {target_state.value}. "
                f"Must be one of {sorted(AUTHORIZED_HUMAN_REVIEWER_ROLES)}."
            )
        if not eff_review_notes:
            raise PermissionError(
                f"RD-16 violation: non-empty review_notes are required from human reviewer {eff_reviewer_id} ({eff_reviewer_role}) before promoting {item.candidate_id} to {target_state.value}."
            )

        item.human_signoff = HumanReviewSignOff(
            reviewer_id=eff_reviewer_id,
            reviewer_role=eff_reviewer_role,
            review_notes=eff_review_notes,
            timestamp=eff_timestamp,
        )

    def _auto_advance_up_to_predecessor(
        self,
        item: ManagedPromotionItem,
        final_target: LegalPromotionState,
    ) -> None:
        if final_target not in LINEAR_PROMOTION_PIPELINE:
            return
        target_idx = LINEAR_PROMOTION_PIPELINE.index(final_target)
        if item.state in LINEAR_PROMOTION_PIPELINE:
            curr_idx = LINEAR_PROMOTION_PIPELINE.index(item.state)
            for idx in range(curr_idx + 1, target_idx):
                step_state = LINEAR_PROMOTION_PIPELINE[idx]
                self.transition(item.candidate_id, step_state, auto_advance_intermediate=False)
        elif item.state == LegalPromotionState.REQUIRES_LEGAL_REVIEW and final_target in (
            LegalPromotionState.APPROVED,
            LegalPromotionState.ACTIVE,
        ):
            self.transition(item.candidate_id, LegalPromotionState.LEGAL_REVIEW, auto_advance_intermediate=False)

    def _ensure_registered(
        self,
        candidate_or_id: Union[str, ManagedPromotionItem, Dict[str, Any], BaseModel],
        *,
        source_hash: Optional[str] = None,
        verbatim_quote: Optional[str] = None,
        citation_verification: Optional[CitationVerificationResult] = None,
    ) -> ManagedPromotionItem:
        if isinstance(candidate_or_id, str):
            if candidate_or_id in self._items:
                return self._items[candidate_or_id]
            return self.register_candidate(
                candidate_or_id,
                source_hash=source_hash,
                verbatim_quote=verbatim_quote,
                citation_verification=citation_verification,
            )
        if isinstance(candidate_or_id, ManagedPromotionItem):
            if candidate_or_id.candidate_id not in self._items:
                self._items[candidate_or_id.candidate_id] = candidate_or_id
            return self._items[candidate_or_id.candidate_id]
        cand_id, _, _, _, _ = self._extract_candidate_fields(candidate_or_id)
        if cand_id in self._items:
            return self._items[cand_id]
        return self.register_candidate(
            candidate_or_id,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            citation_verification=citation_verification,
        )

    @staticmethod
    def _extract_candidate_fields(
        candidate: Any,
    ) -> Tuple[str, Dict[str, Any], str, str, Optional[CitationVerificationResult]]:
        if isinstance(candidate, str):
            return candidate, {"id": candidate}, "", "", None

        if isinstance(candidate, BaseModel):
            d = candidate.model_dump()
        elif isinstance(candidate, dict):
            d = dict(candidate)
        else:
            d = {"id": str(candidate)}

        cand_id = str(
            d.get("candidate_id")
            or d.get("obligation_id")
            or d.get("annotation_id")
            or d.get("decision_id")
            or d.get("diff_id")
            or d.get("document_id")
            or d.get("id")
            or "CANDIDATE-001"
        )
        source_hash = str(
            d.get("source_hash")
            or d.get("source_document_hash")
            or d.get("normalized_text_sha256")
            or d.get("raw_document_sha256")
            or d.get("current_sha256")
            or ""
        )
        verbatim_quote = str(
            d.get("verbatim_quote")
            or d.get("exact_source_excerpt")
            or d.get("current_text")
            or d.get("normalized_text")
            or (
                d["legal_holdings"][0]
                if isinstance(d.get("legal_holdings"), list) and d["legal_holdings"]
                else ""
            )
            or ""
        )
        if not source_hash and isinstance(candidate, LegalPassageAnnotation) and verbatim_quote:
            source_hash = compute_sha256_hex(verbatim_quote)

        cv: Optional[CitationVerificationResult] = None
        raw_cv = d.get("citation_verification") or getattr(candidate, "citation_verification", None)
        if isinstance(raw_cv, CitationVerificationResult):
            cv = raw_cv
        elif isinstance(raw_cv, dict):
            try:
                cv = CitationVerificationResult(**raw_cv)
            except Exception:
                cv = None

        return cand_id, d, source_hash, verbatim_quote, cv

    def _append_audit_record(
        self,
        *,
        candidate_id: str,
        from_state: Optional[LegalPromotionState],
        to_state: LegalPromotionState,
        actor_id: str,
        actor_role: str,
        review_notes: str,
        source_hash: str,
        verbatim_quote: str,
        citation_verification: Optional[CitationVerificationResult],
        superseded_by_id: Optional[str] = None,
        emergency_reason: Optional[str] = None,
        transitioned_at: Optional[datetime] = None,
    ) -> PromotionTransitionAuditRecord:
        ts = transitioned_at or datetime.now(timezone.utc)
        prev_hash = self._audit_log[-1].record_sha256 if self._audit_log else "GENESIS"
        seq_num = len(self._audit_log) + 1
        cv_status = citation_verification.status.value if citation_verification else None
        cv_valid = bool(
            citation_verification
            and citation_verification.valid
            and citation_verification.status == VerificationStatus.VERIFIED
        )

        digest_payload = (
            f"{seq_num}:{candidate_id}:{from_state.value if from_state else 'NONE'}->{to_state.value}:"
            f"{ts.isoformat()}:{actor_id}:{actor_role}:{source_hash}:{cv_status}:{prev_hash}"
        )
        record_sha256 = compute_sha256_hex(digest_payload)
        audit_id = f"PROMO-AUDIT-{seq_num:04d}-{record_sha256[:12].upper()}"

        record = PromotionTransitionAuditRecord(
            audit_id=audit_id,
            candidate_id=candidate_id,
            from_state=from_state,
            to_state=to_state,
            transitioned_at=ts,
            actor_id=actor_id,
            actor_role=actor_role,
            review_notes=review_notes,
            source_hash=source_hash,
            verbatim_quote=verbatim_quote,
            citation_verification_status=cv_status,
            citation_verified=cv_valid,
            superseded_by_id=superseded_by_id,
            emergency_reason=emergency_reason,
            previous_audit_hash=prev_hash,
            record_sha256=record_sha256,
        )
        self._audit_log.append(record)
        return record


__all__ = [
    "ALLOWED_STATE_TRANSITIONS",
    "AUTHORIZED_HUMAN_REVIEWER_ROLES",
    "HumanReviewSignOff",
    "LINEAR_PROMOTION_PIPELINE",
    "LegalPromotionWorkflowEngine",
    "ManagedPromotionItem",
    "PromotionTransitionAuditRecord",
]
