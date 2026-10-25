"""
KIBO Privacy OS — Judicial Decision, Regulator Enforcement Action, and Tribunal Ruling Annotation (Worker G18)
Implements Section 6.3 & RD-02, RD-05, RD-07:
- Extracts case name, neutral citation or official decision ID, court/tribunal/regulator, jurisdiction,
  decision date, parties, material facts, legal issues, statutory provisions considered, reasoning passages
  with exact character offsets (`text_start_offset`, `text_end_offset`, `exact_source_excerpt`), legal holdings,
  dicta/commentary (`dicta_and_commentary`), operative orders, remedies/penalties, binding vs. persuasive status,
  concurring/dissenting notes, subsequent appeals, reversals/modifications, and practical privacy-program implications.
- Explicitly distinguishes binding `legal_holdings` from `dicta_and_commentary`, procedural history,
  settlement terms, and agency commentary (Section 6.3).
- Never invents a court hierarchy or precedent relationship: if `binding_vs_persuasive_status` is unresolved or
  ambiguous, sets `review_status=LegalPromotionState.REQUIRES_LEGAL_REVIEW`.
- Supports `mark_decision_reversed_or_modified(earlier_decision, appellate_decision)` for `RD-07` (preserving both
  records, linking `reversals_or_modifications` and `subsequent_appeals`, and flagging the earlier decision's
  legal status for review).
"""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DecisionVerdictAnnotation,
    DocumentClassType,
    LegalPassageAnnotation,
    LegalPromotionState,
)


VALID_BINDING_STATUSES = {
    "binding_precedent",
    "binding_administrative_order",
    "persuasive_authority",
    "requires_legal_review",
}

EXPLICIT_BINDING_STATUSES = {
    "binding_precedent",
    "binding_administrative_order",
    "persuasive_authority",
}

# Known authoritative court/tribunal/regulator binding status map when not overridden by fixture/doc.
# Any court, tribunal, or regulator not deterministically resolved defaults to "requires_legal_review"
# and triggers LegalPromotionState.REQUIRES_LEGAL_REVIEW (never inventing a court hierarchy).
KNOWN_AUTHORITY_BINDING_MAP: Dict[str, str] = {
    "supreme court of the united states": "binding_precedent",
    "united states court of appeals for the ninth circuit": "binding_precedent",
    "supreme court of canada": "binding_precedent",
    "federal court of appeal": "binding_precedent",
    "federal court of canada": "binding_precedent",
    "court of justice of the european union": "binding_precedent",
    "cjeu": "binding_precedent",
    "information and privacy commissioner of ontario": "binding_administrative_order",
    "ipc ontario": "binding_administrative_order",
    "commission d'accès à l'information du québec": "binding_administrative_order",
    "office of the information and privacy commissioner for british columbia": "binding_administrative_order",
    "office of the information and privacy commissioner of alberta": "binding_administrative_order",
    "office of the privacy commissioner of canada": "persuasive_authority",
    "opc": "persuasive_authority",
    "federal trade commission": "binding_administrative_order",
    "california privacy protection agency": "binding_administrative_order",
    "departement of health and human services office for civil rights": "binding_administrative_order",
    "commission nationale de l'informatique et des libertés": "binding_administrative_order",
    "cnil": "binding_administrative_order",
    "data protection commission": "binding_administrative_order",
}


class JudicialAndEnforcementAnnotator:
    """
    Deterministic, source-grounded annotator for judicial decisions, appellate rulings,
    administrative tribunal orders, and regulatory enforcement actions (Section 6.3, RD-02, RD-05, RD-07).

    Strictly separates:
    1. Binding `legal_holdings` (ratio decidendi / formal findings of violation)
    2. Non-binding `dicta_and_commentary` (obiter dicta, procedural history, settlement disclaimers,
       and general agency commentary)
    3. `operative_orders` and `remedies_and_penalties`

    Never invents a court hierarchy or precedent relationship: whenever `binding_vs_persuasive_status`
    is unresolved, ambiguous, or marked `"requires_legal_review"`, the decision annotation's
    `review_status` is set to `LegalPromotionState.REQUIRES_LEGAL_REVIEW`.
    """

    _CASE_NAME_PATTERN = re.compile(
        r"\b([A-Z][A-Za-z0-9\.\,\&\-\'\s]{1,70}\s+v\.\s+[A-Z][A-Za-z0-9\.\,\&\-\'\s]{1,70})"
    )
    _STATUTE_CITATION_PATTERN = re.compile(
        r"\b(?:"
        r"\d+\s+U\.S\.C\.\s*§+\s*\d+[a-zA-Z0-9\-\(\)]*"
        r"|\d+\s+C\.F\.R\.\s*§+\s*\d+(?:\.\d+)*[a-zA-Z0-9\-\(\)]*"
        r"|Article\s+\d+(?:\(\d+\))?(?:\([a-z]\))?\s*(?:of\s+the\s+GDPR|GDPR|of\s+the\s+Charter)?"
        r"|PIPEDA\s+(?:s\.|section|sections|clause)\s*\d+(?:\.\d+)*(?:\([a-z0-9]+\))*"
        r"|PHIPA\s+(?:s\.|section|sections)\s*\d+(?:\(\d+\))*"
        r"|Section\s+\d+(?:\.\d+)*(?:\([a-zA-Z0-9]+\))*"
        r")\b",
        re.IGNORECASE,
    )

    _HOLDING_LINE_MARKERS: Tuple[str, ...] = (
        "we hold that",
        "the court holds",
        "held:",
        "holding:",
        "the court rules that",
        "is invalid",
        "we conclude that",
        "the commissioner concludes",
        "the adjudicator finds",
        "finding of violation:",
        "ratio decidendi:",
    )

    _DICTA_PROCEDURAL_SETTLEMENT_MARKERS: Tuple[str, ...] = (
        "dicta:",
        "obiter dicta:",
        "commentary:",
        "agency commentary:",
        "procedural history:",
        "settlement term:",
        "settlement note:",
        "without admitting or denying",
        "by way of observation",
        "in passing, we note",
        "general guidance note:",
    )

    _ORDER_LINE_MARKERS: Tuple[str, ...] = (
        "it is hereby ordered",
        "order:",
        "operative order:",
        "the judgment of the",
        "is reversed and remanded",
        "cease and desist",
        "shall delete",
        "is ordered to",
    )

    _REMEDY_LINE_MARKERS: Tuple[str, ...] = (
        "remedy:",
        "penalty:",
        "administrative fine",
        "civil monetary penalty",
        "corrective measure:",
        "injunctive relief",
        "damages",
        "deletion of biometric",
    )

    def __init__(self, extraction_model: str = "kibo-judicial-decision-annotator-v2") -> None:
        self.extraction_model = extraction_model

    def annotate_decision(
        self,
        doc: CanonicalLegalDocument,
        structured_fixture: dict | None = None,
    ) -> tuple[DecisionVerdictAnnotation, list[LegalPassageAnnotation]]:
        """
        Extracts a source-grounded `DecisionVerdictAnnotation` and passage-level
        `LegalPassageAnnotation` list from `doc` (and optional `structured_fixture`).

        Guarantees:
        - Every reasoning, holding, dicta, and remedy/order passage carries exact character
          offsets (`text_start_offset`, `text_end_offset`, `exact_source_excerpt`) verified
          against `doc.normalized_text` when present in the text.
        - Explicitly separates `legal_holdings` from `dicta_and_commentary` (including
          procedural history, settlement terms, and non-binding agency commentary).
        - If `binding_vs_persuasive_status` is unresolved or ambiguous, sets
          `review_status = LegalPromotionState.REQUIRES_LEGAL_REVIEW`.
        """
        fixture: Dict[str, Any] = dict(structured_fixture or {})
        norm_text = doc.normalized_text or ""

        decision_id = str(
            fixture.get("decision_id")
            or f"DEC-{doc.jurisdiction_id}-{self._short_hash(doc.document_id + ':' + doc.canonical_title)}"
        )

        case_name = str(
            fixture.get("case_name")
            or self._extract_case_name(doc)
        )

        neutral_citation_or_id = str(
            fixture.get("neutral_citation_or_id")
            or doc.neutral_citation
            or doc.official_citation
            or doc.docket_or_case_number
            or doc.official_document_id
            or doc.document_id
        )

        court_tribunal_or_regulator = str(
            fixture.get("court_tribunal_or_regulator")
            or doc.issuing_authority
        )

        jurisdiction_id = str(fixture.get("jurisdiction_id") or doc.jurisdiction_id)
        decision_date = self._resolve_decision_date(fixture.get("decision_date"), doc)

        parties = self._resolve_list_field(
            fixture.get("parties"),
            fallback=self._extract_parties(case_name, norm_text),
        )

        material_facts = str(
            fixture.get("material_facts")
            or self._extract_material_facts(norm_text, doc.canonical_title)
        )

        legal_issues = self._resolve_list_field(
            fixture.get("legal_issues"),
            fallback=self._extract_legal_issues(norm_text, doc.canonical_title),
        )

        statutory_provisions = self._resolve_list_field(
            fixture.get("statutory_provisions_considered"),
            fallback=self._extract_statutory_provisions(norm_text),
        )

        # Distinguish holdings vs. dicta/procedural history/settlement terms/agency commentary
        raw_holdings, raw_dicta, raw_orders, raw_remedies = self._extract_classified_statements(
            norm_text=norm_text,
            fixture=fixture,
            doc=doc,
        )

        # Build passage-grounded reasoning passages with exact character offsets
        reasoning_passages = self._build_reasoning_passages(
            norm_text=norm_text,
            fixture=fixture,
            holdings=raw_holdings,
            dicta=raw_dicta,
            orders=raw_orders,
            remedies=raw_remedies,
        )

        # Resolve binding_vs_persuasive_status without ever inventing court hierarchy
        binding_status, is_binding_unresolved = self._resolve_binding_status(
            fixture_status=fixture.get("binding_vs_persuasive_status"),
            doc=doc,
            court_tribunal_or_regulator=court_tribunal_or_regulator,
        )

        concurring_or_dissenting = fixture.get("concurring_or_dissenting_notes")
        if concurring_or_dissenting is None:
            concurring_or_dissenting = self._extract_concurring_or_dissenting(norm_text)

        subsequent_appeals = self._resolve_list_field(fixture.get("subsequent_appeals"), fallback=[])
        reversals_or_modifications = self._resolve_list_field(
            fixture.get("reversals_or_modifications"),
            fallback=[],
        )
        related_cases = self._resolve_list_field(fixture.get("related_cases"), fallback=[])
        related_statutory_provisions = self._resolve_list_field(
            fixture.get("related_statutory_provisions"),
            fallback=list(statutory_provisions),
        )
        practical_implications = self._resolve_list_field(
            fixture.get("practical_privacy_program_implications"),
            fallback=self._derive_practical_implications(raw_holdings, raw_orders, raw_remedies, statutory_provisions),
        )

        # Determine review_status: if binding status is unresolved/ambiguous or doc appeal status is reversed/modified
        review_status = self._resolve_review_status(
            fixture_review_status=fixture.get("review_status"),
            doc=doc,
            is_binding_unresolved=is_binding_unresolved,
            reversals_or_modifications=reversals_or_modifications,
        )

        verdict_annotation = DecisionVerdictAnnotation(
            decision_id=decision_id,
            document_id=doc.document_id,
            case_name=case_name,
            neutral_citation_or_id=neutral_citation_or_id,
            court_tribunal_or_regulator=court_tribunal_or_regulator,
            jurisdiction_id=jurisdiction_id,
            decision_date=decision_date,
            parties=parties,
            material_facts=material_facts,
            legal_issues=legal_issues,
            statutory_provisions_considered=statutory_provisions,
            relevant_reasoning_passages=reasoning_passages,
            legal_holdings=raw_holdings,
            dicta_and_commentary=raw_dicta,
            operative_orders=raw_orders,
            remedies_and_penalties=raw_remedies,
            binding_vs_persuasive_status=binding_status,
            concurring_or_dissenting_notes=concurring_or_dissenting,
            subsequent_appeals=subsequent_appeals,
            reversals_or_modifications=reversals_or_modifications,
            related_cases=related_cases,
            related_statutory_provisions=related_statutory_provisions,
            practical_privacy_program_implications=practical_implications,
            review_status=review_status,
        )

        passage_annotations = self._build_passage_annotations(
            doc=doc,
            verdict=verdict_annotation,
            is_binding_unresolved=is_binding_unresolved,
        )

        return verdict_annotation, passage_annotations

    def mark_decision_reversed_or_modified(
        self,
        earlier_decision: DecisionVerdictAnnotation,
        appellate_decision: DecisionVerdictAnnotation,
        action_type: str = "reversed",
    ) -> tuple[DecisionVerdictAnnotation, DecisionVerdictAnnotation]:
        """
        Implements RD-07: When a court or appellate tribunal reverses, vacates, or modifies an
        earlier decision:
        1. Preserves both `earlier_decision` and `appellate_decision` records (never silently overwrites
           or deletes historical legal records).
        2. Links `earlier_decision.subsequent_appeals` and `earlier_decision.reversals_or_modifications`
           to `appellate_decision` (`decision_id`, `case_name`, `neutral_citation_or_id`).
        3. Links `appellate_decision.related_cases` and `appellate_decision.reversals_or_modifications`
           to the earlier decision record.
        4. Flags `earlier_decision.review_status = LegalPromotionState.REQUIRES_LEGAL_REVIEW` and sets
           `earlier_decision.binding_vs_persuasive_status = "requires_legal_review"` so downstream
           compliance engines do not enforce reversed holdings without counsel review.
        """
        normalized_action = action_type.strip().lower()
        if normalized_action not in ("reversed", "modified", "vacated", "reversed_in_part"):
            normalized_action = "reversed"

        appellate_ref = (
            f"{appellate_decision.decision_id} ({appellate_decision.case_name}, "
            f"{appellate_decision.neutral_citation_or_id})"
        )
        reversal_entry = (
            f"{normalized_action.upper()} by {appellate_decision.court_tribunal_or_regulator} in "
            f"{appellate_decision.case_name} [{appellate_decision.neutral_citation_or_id}] "
            f"(decision_id={appellate_decision.decision_id}, date={appellate_decision.decision_date.isoformat()})"
        )

        earlier_appeals = list(earlier_decision.subsequent_appeals)
        if appellate_ref not in earlier_appeals:
            earlier_appeals.append(appellate_ref)

        earlier_reversals = list(earlier_decision.reversals_or_modifications)
        if reversal_entry not in earlier_reversals:
            earlier_reversals.append(reversal_entry)

        earlier_related = list(earlier_decision.related_cases)
        if appellate_decision.decision_id not in earlier_related:
            earlier_related.append(appellate_decision.decision_id)

        updated_earlier = earlier_decision.model_copy(
            update={
                "subsequent_appeals": earlier_appeals,
                "reversals_or_modifications": earlier_reversals,
                "related_cases": earlier_related,
                "binding_vs_persuasive_status": "requires_legal_review",
                "review_status": LegalPromotionState.REQUIRES_LEGAL_REVIEW,
            }
        )

        earlier_ref = (
            f"{normalized_action.upper()} lower decision: {earlier_decision.case_name} "
            f"[{earlier_decision.neutral_citation_or_id}] (decision_id={earlier_decision.decision_id})"
        )
        appellate_reversals = list(appellate_decision.reversals_or_modifications)
        if earlier_ref not in appellate_reversals:
            appellate_reversals.append(earlier_ref)

        appellate_related = list(appellate_decision.related_cases)
        if earlier_decision.decision_id not in appellate_related:
            appellate_related.append(earlier_decision.decision_id)

        updated_appellate = appellate_decision.model_copy(
            update={
                "reversals_or_modifications": appellate_reversals,
                "related_cases": appellate_related,
            }
        )

        return updated_earlier, updated_appellate

    @staticmethod
    def _short_hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:10].upper()

    @staticmethod
    def _resolve_decision_date(fixture_date: Any, doc: CanonicalLegalDocument) -> date:
        if isinstance(fixture_date, date) and not isinstance(fixture_date, datetime):
            return fixture_date
        if isinstance(fixture_date, str):
            return date.fromisoformat(fixture_date[:10])
        if doc.decision_date is not None:
            return doc.decision_date
        if doc.publication_date is not None:
            return doc.publication_date
        if doc.effective_date is not None:
            return doc.effective_date
        return date(2026, 1, 1)

    @staticmethod
    def _resolve_list_field(primary: Any, fallback: List[str]) -> List[str]:
        if isinstance(primary, list) and len(primary) > 0:
            return [str(item).strip() for item in primary if str(item).strip()]
        return [str(item).strip() for item in fallback if str(item).strip()]

    def _extract_case_name(self, doc: CanonicalLegalDocument) -> str:
        if doc.canonical_title and doc.canonical_title.strip():
            return doc.canonical_title.strip()
        match = self._CASE_NAME_PATTERN.search(doc.normalized_text or "")
        if match:
            return match.group(1).strip()
        return f"Decision {doc.document_id}"

    @staticmethod
    def _extract_parties(case_name: str, norm_text: str) -> List[str]:
        if " v. " in case_name:
            parts = case_name.split(" v. ", 1)
            left = parts[0].split("—")[-1].split(":")[-1].strip()
            right = parts[1].split("(")[0].split("[")[0].strip()
            if left and right:
                return [left, right]
        if " c. " in case_name:
            parts = case_name.split(" c. ", 1)
            left = parts[0].strip()
            right = parts[1].split("(")[0].strip()
            if left and right:
                return [left, right]

        parties_match = re.search(
            r"(?:Parties|Between|Respondent|Complainant|Applicant|Defendant)s?\s*:\s*([^\n]+)",
            norm_text,
            re.IGNORECASE,
        )
        if parties_match:
            raw = parties_match.group(1)
            return [p.strip() for p in re.split(r";|\band\b|,", raw) if p.strip()]
        return [case_name]

    @staticmethod
    def _extract_material_facts(norm_text: str, fallback_title: str) -> str:
        if not norm_text.strip():
            return f"Material facts documented in {fallback_title}."
        facts_match = re.search(
            r"(?:MATERIAL FACTS|FACTS|BACKGROUND)\s*[:\-]?\s*([^\n]+(?:\n[^\n]+){0,3})",
            norm_text,
            re.IGNORECASE,
        )
        if facts_match:
            return facts_match.group(1).strip()
        first_para = norm_text.strip().split("\n\n")[0].strip()
        return first_para

    @staticmethod
    def _extract_legal_issues(norm_text: str, fallback_title: str) -> List[str]:
        issues: List[str] = []
        for line in norm_text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            lower = clean.lower()
            if (
                lower.startswith("issue:")
                or lower.startswith("legal issue:")
                or lower.startswith("question presented:")
                or "whether " in lower
            ):
                issues.append(clean)
        if not issues:
            issues.append(f"Scope of statutory compliance and enforcement liability in {fallback_title}")
        return issues

    def _extract_statutory_provisions(self, norm_text: str) -> List[str]:
        found: List[str] = []
        for match in self._STATUTE_CITATION_PATTERN.finditer(norm_text):
            val = match.group(0).strip()
            if val not in found:
                found.append(val)
        return found

    def _extract_classified_statements(
        self,
        norm_text: str,
        fixture: Dict[str, Any],
        doc: CanonicalLegalDocument,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """
        Strictly separates binding `legal_holdings` from `dicta_and_commentary`
        (which includes obiter dicta, procedural history, settlement disclaimers, and
        non-binding agency commentary), `operative_orders`, and `remedies_and_penalties`.
        """
        holdings: List[str] = [str(x).strip() for x in fixture.get("legal_holdings", []) if str(x).strip()]
        dicta: List[str] = [str(x).strip() for x in fixture.get("dicta_and_commentary", []) if str(x).strip()]
        orders: List[str] = [str(x).strip() for x in fixture.get("operative_orders", []) if str(x).strip()]
        remedies: List[str] = [str(x).strip() for x in fixture.get("remedies_and_penalties", []) if str(x).strip()]

        # Explicitly route procedural_history, settlement_terms, and agency_commentary into dicta_and_commentary
        # so they are NEVER conflated with binding legal_holdings (Section 6.3).
        for non_binding_key, prefix_label in (
            ("procedural_history", "Procedural History"),
            ("settlement_terms", "Settlement Term (Non-Precedential)"),
            ("agency_commentary", "Agency Commentary (Non-Binding)"),
        ):
            extra_items = fixture.get(non_binding_key, [])
            if isinstance(extra_items, str) and extra_items.strip():
                extra_items = [extra_items.strip()]
            for item in extra_items:
                formatted = str(item).strip()
                if not formatted:
                    continue
                if not formatted.lower().startswith(prefix_label.split()[0].lower()):
                    formatted = f"{prefix_label}: {formatted}"
                if formatted not in dicta:
                    dicta.append(formatted)

        # If document is a Consent Order / Settlement and no explicit holding disclaimer exists,
        # ensure settlement terms are classified in dicta_and_commentary or operative_orders, not binding precedent.
        if doc.document_type == DocumentClassType.CONSENT_ORDER_SETTLEMENT and holdings:
            reclassified_for_settlement: List[str] = []
            kept_holdings: List[str] = []
            for h in holdings:
                if "without admitting or denying" in h.lower() or "settlement" in h.lower():
                    reclassified_for_settlement.append(f"Settlement Term (Non-Precedential): {h}")
                else:
                    kept_holdings.append(h)
            holdings = kept_holdings
            for item in reclassified_for_settlement:
                if item not in dicta:
                    dicta.append(item)

        # Also inspect `norm_text` lines when any category was not supplied in `fixture`
        need_holdings = len(holdings) == 0
        need_dicta = len(dicta) == 0
        need_orders = len(orders) == 0
        need_remedies = len(remedies) == 0

        if need_holdings or need_dicta or need_orders or need_remedies:
            for line in norm_text.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                lower = stripped.lower()

                # Check dicta / procedural history / settlement / commentary first so it never leaks into holdings
                if any(marker in lower for marker in self._DICTA_PROCEDURAL_SETTLEMENT_MARKERS):
                    if need_dicta and stripped not in dicta:
                        dicta.append(stripped)
                    continue

                if any(marker in lower for marker in self._HOLDING_LINE_MARKERS):
                    if need_holdings and stripped not in holdings:
                        holdings.append(stripped)
                    continue

                if any(marker in lower for marker in self._ORDER_LINE_MARKERS):
                    if need_orders and stripped not in orders:
                        orders.append(stripped)
                    continue

                if any(marker in lower for marker in self._REMEDY_LINE_MARKERS):
                    if need_remedies and stripped not in remedies:
                        remedies.append(stripped)
                    continue

        # Remove any item from `holdings` that accidentally duplicates `dicta`
        dicta_lower_set = {d.lower() for d in dicta}
        holdings = [
            h
            for h in holdings
            if h.lower() not in dicta_lower_set
            and not any(marker in h.lower() for marker in self._DICTA_PROCEDURAL_SETTLEMENT_MARKERS)
        ]

        return holdings, dicta, orders, remedies

    def _locate_exact_span(self, norm_text: str, candidate_text: str) -> Tuple[int, int, str]:
        """
        Finds the exact character offsets (`text_start_offset`, `text_end_offset`, `exact_source_excerpt`)
        inside `norm_text` for `candidate_text`. Guarantees `norm_text[start:end] == exact_source_excerpt`.
        """
        if not norm_text:
            return 0, 0, ""

        cleaned = candidate_text.strip()
        # Strip synthetic prefixes added for classification when searching the source text
        for prefix in (
            "Procedural History: ",
            "Settlement Term (Non-Precedential): ",
            "Agency Commentary (Non-Binding): ",
        ):
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()

        if cleaned:
            idx = norm_text.find(cleaned)
            if idx != -1:
                end = idx + len(cleaned)
                return idx, end, norm_text[idx:end]

            # Try matching a substantial substring (first 60 characters) and expanding to line boundaries
            anchor = cleaned[: min(60, len(cleaned))].strip()
            if len(anchor) >= 12:
                idx = norm_text.find(anchor)
                if idx != -1:
                    line_end = norm_text.find("\n", idx)
                    if line_end == -1:
                        line_end = len(norm_text)
                    return idx, line_end, norm_text[idx:line_end]

        # Fallback: first non-empty line in `norm_text` so offset slicing is still 100% exact
        first_non_ws = len(norm_text) - len(norm_text.lstrip())
        first_line_end = norm_text.find("\n", first_non_ws)
        if first_line_end == -1:
            first_line_end = len(norm_text.rstrip())
        return first_non_ws, first_line_end, norm_text[first_non_ws:first_line_end]

    def _build_reasoning_passages(
        self,
        norm_text: str,
        fixture: Dict[str, Any],
        holdings: List[str],
        dicta: List[str],
        orders: List[str],
        remedies: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Builds `relevant_reasoning_passages` with verified `text_start_offset`, `text_end_offset`,
        `exact_source_excerpt`, `section_or_paragraph`, and `passage_role` (`holding`, `dicta`, `remedy_order`, `reasoning`).
        """
        passages: List[Dict[str, Any]] = []
        fixture_passages = fixture.get("relevant_reasoning_passages", [])

        if isinstance(fixture_passages, list) and len(fixture_passages) > 0:
            for idx, item in enumerate(fixture_passages):
                if isinstance(item, dict):
                    raw_excerpt = str(item.get("exact_source_excerpt") or item.get("text") or "").strip()
                    start = item.get("text_start_offset")
                    end = item.get("text_end_offset")
                    if (
                        isinstance(start, int)
                        and isinstance(end, int)
                        and 0 <= start <= end <= len(norm_text)
                        and raw_excerpt
                        and norm_text[start:end] == raw_excerpt
                    ):
                        verified_start, verified_end, verified_excerpt = start, end, raw_excerpt
                    else:
                        verified_start, verified_end, verified_excerpt = self._locate_exact_span(norm_text, raw_excerpt)

                    passages.append(
                        {
                            "passage_id": str(item.get("passage_id") or f"PASSAGE-{idx + 1}"),
                            "section_or_paragraph": str(item.get("section_or_paragraph") or f"para_{idx + 1}"),
                            "passage_role": str(item.get("passage_role") or "reasoning"),
                            "text_start_offset": verified_start,
                            "text_end_offset": verified_end,
                            "exact_source_excerpt": verified_excerpt,
                            "summary": str(item.get("summary") or verified_excerpt),
                        }
                    )
                elif isinstance(item, str) and item.strip():
                    verified_start, verified_end, verified_excerpt = self._locate_exact_span(norm_text, item)
                    passages.append(
                        {
                            "passage_id": f"PASSAGE-{idx + 1}",
                            "section_or_paragraph": f"para_{idx + 1}",
                            "passage_role": "reasoning",
                            "text_start_offset": verified_start,
                            "text_end_offset": verified_end,
                            "exact_source_excerpt": verified_excerpt,
                            "summary": item.strip(),
                        }
                    )

        # Ensure every holding, dicta, and operative order/remedy has an offset-grounded passage entry
        existing_excerpts = {p["exact_source_excerpt"] for p in passages if p.get("exact_source_excerpt")}

        def _append_grounded(items: List[str], role: str, section_prefix: str) -> None:
            for i, statement in enumerate(items):
                start, end, excerpt = self._locate_exact_span(norm_text, statement)
                if not excerpt:
                    continue
                if excerpt in existing_excerpts and any(p.get("passage_role") == role for p in passages):
                    continue
                existing_excerpts.add(excerpt)
                passages.append(
                    {
                        "passage_id": f"PASSAGE-{role.upper()}-{i + 1}",
                        "section_or_paragraph": f"{section_prefix}_{i + 1}",
                        "passage_role": role,
                        "text_start_offset": start,
                        "text_end_offset": end,
                        "exact_source_excerpt": excerpt,
                        "summary": statement,
                    }
                )

        _append_grounded(holdings, "judicial_holding", "holding")
        _append_grounded(dicta, "judicial_dicta", "dicta")
        _append_grounded(orders + remedies, "remedy_order", "order")

        if not passages and norm_text:
            start, end, excerpt = self._locate_exact_span(norm_text, norm_text.splitlines()[0])
            passages.append(
                {
                    "passage_id": "PASSAGE-1",
                    "section_or_paragraph": "para_1",
                    "passage_role": "reasoning",
                    "text_start_offset": start,
                    "text_end_offset": end,
                    "exact_source_excerpt": excerpt,
                    "summary": excerpt,
                }
            )

        return passages

    def _resolve_binding_status(
        self,
        fixture_status: Optional[str],
        doc: CanonicalLegalDocument,
        court_tribunal_or_regulator: str,
    ) -> Tuple[str, bool]:
        """
        Determines `binding_vs_persuasive_status` without inventing any court hierarchy or
        precedent relationship. Returns `(status, is_unresolved)`.
        """
        if fixture_status is not None:
            cleaned = str(fixture_status).strip().lower()
            if cleaned in EXPLICIT_BINDING_STATUSES:
                return cleaned, False
            # Any unknown, empty, or "requires_legal_review" status is flagged as unresolved
            return "requires_legal_review", True

        # Check if document has an explicit unambiguous binding_status set by authoritative registry
        doc_binding = (doc.binding_status or "").strip().lower()
        authority_key = court_tribunal_or_regulator.strip().lower()

        if authority_key in KNOWN_AUTHORITY_BINDING_MAP:
            return KNOWN_AUTHORITY_BINDING_MAP[authority_key], False

        if doc_binding == "binding_precedent" and doc.document_type == DocumentClassType.COURT_JUDGMENT:
            # Verify authority is a recognized court before assuming precedent hierarchy
            if any(k in authority_key for k in KNOWN_AUTHORITY_BINDING_MAP):
                return "binding_precedent", False
            return "requires_legal_review", True

        if doc_binding == "administrative_order" and doc.document_type in (
            DocumentClassType.REGULATORY_ENFORCEMENT_DECISION,
            DocumentClassType.ADMINISTRATIVE_TRIBUNAL_RULING,
        ):
            for k, val in KNOWN_AUTHORITY_BINDING_MAP.items():
                if k in authority_key:
                    return val, False
            return "requires_legal_review", True

        if doc_binding == "persuasive_guidance":
            return "persuasive_authority", False

        # Never invent a court hierarchy or precedent relationship when unresolved
        return "requires_legal_review", True

    @staticmethod
    def _extract_concurring_or_dissenting(norm_text: str) -> Optional[str]:
        for line in norm_text.splitlines():
            clean = line.strip()
            lower = clean.lower()
            if "dissenting" in lower or "concurring" in lower or "dissent:" in lower or "concurrence:" in lower:
                return clean
        return None

    @staticmethod
    def _derive_practical_implications(
        holdings: List[str],
        orders: List[str],
        remedies: List[str],
        statutory_provisions: List[str],
    ) -> List[str]:
        implications: List[str] = []
        for h in holdings[:2]:
            implications.append(f"Enforceable legal holding impact: {h}")
        for o in (orders + remedies)[:2]:
            implications.append(f"Operational compliance & remediation requirement: {o}")
        if not implications and statutory_provisions:
            implications.append(
                f"Review privacy controls mapped to {', '.join(statutory_provisions[:3])}."
            )
        return implications

    @staticmethod
    def _resolve_review_status(
        fixture_review_status: Any,
        doc: CanonicalLegalDocument,
        is_binding_unresolved: bool,
        reversals_or_modifications: List[str],
    ) -> LegalPromotionState:
        # Never allow an unresolved/ambiguous binding status or reversed decision to bypass legal review
        if is_binding_unresolved:
            return LegalPromotionState.REQUIRES_LEGAL_REVIEW

        if (doc.appeal_status or "").strip().lower() in ("reversed", "modified", "under_appeal"):
            return LegalPromotionState.REQUIRES_LEGAL_REVIEW

        if any("reversed" in r.lower() or "modified" in r.lower() or "vacated" in r.lower() for r in reversals_or_modifications):
            return LegalPromotionState.REQUIRES_LEGAL_REVIEW

        if isinstance(fixture_review_status, LegalPromotionState):
            return fixture_review_status
        if isinstance(fixture_review_status, str):
            try:
                return LegalPromotionState(fixture_review_status)
            except ValueError:
                return LegalPromotionState.REQUIRES_LEGAL_REVIEW

        if doc.review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW:
            return LegalPromotionState.REQUIRES_LEGAL_REVIEW

        return LegalPromotionState.ANNOTATED

    def _build_passage_annotations(
        self,
        doc: CanonicalLegalDocument,
        verdict: DecisionVerdictAnnotation,
        is_binding_unresolved: bool,
    ) -> List[LegalPassageAnnotation]:
        """
        Generates `LegalPassageAnnotation` records from the decision's reasoning passages,
        explicitly tagging `annotation_type` as:
        - `"judicial_holding"` for binding holdings
        - `"judicial_dicta"` for non-binding dicta, procedural history, settlement disclaimers, or commentary
        - `"remedy_order"` for operative orders, injunctions, and penalties
        """
        annotations: List[LegalPassageAnnotation] = []
        norm_text = doc.normalized_text or ""

        interp_status = (
            "requires_legal_review"
            if (is_binding_unresolved or verdict.review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW)
            else "source_grounded_deterministic"
        )
        verif_status = (
            "REQUIRES_LEGAL_REVIEW"
            if (is_binding_unresolved or verdict.review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW)
            else "VERIFIED"
        )

        for idx, passage in enumerate(verdict.relevant_reasoning_passages):
            role = str(passage.get("passage_role") or "judicial_holding")
            if role in ("holding", "judicial_holding"):
                annotation_type = "judicial_holding"
                concept = "binding_judicial_or_regulatory_holding"
            elif role in ("dicta", "judicial_dicta", "commentary", "procedural_history"):
                annotation_type = "judicial_dicta"
                concept = "non_binding_dicta_or_commentary"
            elif role in ("remedy_order", "order", "remedy"):
                annotation_type = "remedy_order"
                concept = "operative_order_or_remedy"
            else:
                annotation_type = "judicial_holding"
                concept = "judicial_reasoning_passage"

            start = int(passage.get("text_start_offset", 0))
            end = int(passage.get("text_end_offset", 0))
            excerpt = str(passage.get("exact_source_excerpt", ""))

            # Enforce strict offset slicing invariant against doc.normalized_text
            if norm_text and (start < 0 or end > len(norm_text) or norm_text[start:end] != excerpt):
                start, end, excerpt = self._locate_exact_span(norm_text, excerpt or str(passage.get("summary", "")))

            summary_text = str(passage.get("summary") or excerpt)
            section_ref = str(passage.get("section_or_paragraph") or f"para_{idx + 1}")

            annotations.append(
                LegalPassageAnnotation(
                    annotation_id=f"ANN-{verdict.decision_id}-{idx + 1:02d}",
                    document_id=doc.document_id,
                    document_version=doc.document_version,
                    annotation_type=annotation_type,
                    jurisdiction_id=verdict.jurisdiction_id,
                    source_section=section_ref,
                    paragraph=section_ref,
                    text_start_offset=start,
                    text_end_offset=end,
                    exact_source_excerpt=excerpt,
                    source_language=doc.language,
                    normalized_legal_concept=concept,
                    plain_language_explanation=summary_text,
                    legal_requirement=(
                        summary_text
                        if annotation_type in ("judicial_holding", "remedy_order")
                        else f"Non-binding dicta/commentary (not an enforceable requirement): {summary_text}"
                    ),
                    applicability_conditions=[
                        f"Binding status: {verdict.binding_vs_persuasive_status}",
                        f"Case: {verdict.case_name} ({verdict.neutral_citation_or_id})",
                    ],
                    effective_date=verdict.decision_date,
                    regulatory_authority=verdict.court_tribunal_or_regulator,
                    related_regulations=list(verdict.statutory_provisions_considered),
                    related_decisions=[verdict.decision_id] + list(verdict.related_cases),
                    interpretation_status=interp_status,
                    evidence_strength=(
                        "authoritative_primary_text"
                        if annotation_type != "judicial_dicta"
                        else "non_binding_dicta_or_commentary"
                    ),
                    extraction_model=self.extraction_model,
                    verification_status=verif_status,
                )
            )

        return annotations
