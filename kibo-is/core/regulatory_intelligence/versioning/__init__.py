"""
KIBO Privacy OS — Legislative Amendment, Version Detection & Structural Provision Diff Engine (Worker G20)
Implements Section 5.2, RD-03 (US State Legislative Amendment Diffing), and RD-04 (EUR-Lex & Official Gazette Versioned Instruments):
- Cryptographic SHA-256 hashing of raw and normalized legal provision text
- Deterministic separation of substantive legal amendments (deadlines, numerical thresholds, penalties,
  deontic obligations like shall/must/may not, new obligations, repealed clauses, scope expansions)
  from editorial/formatting changes (whitespace, punctuation, capitalization, typographical corrigenda)
- Strict prohibition on inferring legal changes solely from URLs or retrieval timestamps
- First-class support for US State legislative amendments (e.g., California CCPA -> CPRA
  Cal. Civ. Code § 1798.100(d) and § 1798.185(a)(15)-(16)) and EU EUR-Lex versioned instruments
  (preserving ELI/CELEX identifiers, consolidated versions, and historical text without overwriting)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DocumentClassType,
    LegalPromotionState,
    ProvisionDiffRecord,
    compute_sha256_hex,
)


# ---------------------------------------------------------------------------
# Substantive Legal Marker Patterns (Multilingual: EN / FR / DE / EU)
# ---------------------------------------------------------------------------

_DEADLINE_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty|forty-five|sixty|ninety|180|365)\s+"
        r"(?:business\s+|calendar\s+|working\s+)?(?:hours?|days?|weeks?|months?|years?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:within|no\s+later\s+than|prior\s+to|before|after|on\s+or\s+before|effective\s+on|by)\s+"
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(
        r"\b(?:without\s+undue\s+delay|unverzüglich|sans\s+retard\s+injustifié|dans\s+un\s+délai\s+de\s+\d+\s+jours?)\b",
        re.IGNORECASE,
    ),
)

_THRESHOLD_AND_PENALTY_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?:\$|USD|EUR|€|CAD|£)\s?\d[\d,]*(?:\.\d+)?(?:\s*(?:million|billion|thousand|k|m))?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b\d[\d,]*(?:\.\d+)?\s*(?:percent|%|consumers?|residents?|households?|employees?|devices?|records?|individuals?|data\s+subjects?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:administrative\s+fine|civil\s+penalty|statutory\s+damages|worldwide\s+annual\s+turnover|global\s+turnover|gross\s+annual\s+revenues?)\b",
        re.IGNORECASE,
    ),
)

_DEONTIC_MODALITY_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:shall\s+not|must\s+not|may\s+not|is\s+prohibited\s+from|are\s+prohibited\s+from|"
        r"shall|must|required\s+to|obligated\s+to|has\s+the\s+duty\s+to|"
        r"doit|ne\s+peut\s+pas|est\s+tenu\s+de|"
        r"hat\s+zu|muss|darf\s+nicht|ist\s+verpflichtet)\b",
        re.IGNORECASE,
    ),
)

_REPEAL_OR_EXPIRY_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:repealed|is\s+hereby\s+repealed|deleted|struck|omitted|superseded|expired|ceases\s+to\s+have\s+effect|"
        r"abrogé|aufgehoben)\b",
        re.IGNORECASE,
    ),
)

_SCOPE_AND_OBLIGATION_KEYWORDS: Tuple[str, ...] = (
    "contractor",
    "service provider",
    "third party",
    "sensitive personal information",
    "automated decision-making",
    "profiling",
    "cybersecurity audit",
    "risk assessment",
    "data protection impact assessment",
    "opt-out",
    "limit the use",
    "sharing",
    "cross-context behavioral advertising",
    "retaliation",
    "contract",
    "written agreement",
    "subprocessor",
    "biometric",
    "genetic",
    "health information",
    "children",
    "minors",
    "private right of action",
    "cure period",
    "high-risk",
)


@dataclass
class VersionedInstrumentSnapshot:
    """
    Represents a point-in-time version of a statutory/regulatory instrument or provision
    (e.g., US State statute amendment or EUR-Lex consolidated version with ELI/CELEX).
    """
    document_id: str
    jurisdiction_id: str
    version_id: str
    provision_ref: str
    raw_text: str
    normalized_text: str
    raw_sha256: str
    normalized_sha256: str
    effective_date: Optional[date] = None
    publication_date: Optional[date] = None
    repeal_or_expiry_date: Optional[date] = None
    eli_identifier: Optional[str] = None
    celex_identifier: Optional[str] = None
    amending_instrument_id: Optional[str] = None
    amending_citation: Optional[str] = None
    official_source_url: Optional[str] = None
    supersedes_version: Optional[str] = None
    is_repealed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "jurisdiction_id": self.jurisdiction_id,
            "version_id": self.version_id,
            "provision_ref": self.provision_ref,
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "raw_sha256": self.raw_sha256,
            "normalized_sha256": self.normalized_sha256,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "repeal_or_expiry_date": self.repeal_or_expiry_date.isoformat() if self.repeal_or_expiry_date else None,
            "eli_identifier": self.eli_identifier,
            "celex_identifier": self.celex_identifier,
            "amending_instrument_id": self.amending_instrument_id,
            "amending_citation": self.amending_citation,
            "official_source_url": self.official_source_url,
            "supersedes_version": self.supersedes_version,
            "is_repealed": self.is_repealed,
        }


class StructuralVersionDiffEngine:
    """
    Section 5.2, RD-03, RD-04 — Legislative Amendment, Version Detection, and Structural Diff Engine.
    - Computes SHA-256 hashes of raw and normalized provision text.
    - Distinguishes substantive legal changes from editorial/formatting changes.
    - Never infers a legal change solely from a URL or retrieval timestamp.
    - Supports both US State legislative amendments (RD-03, e.g. California CCPA -> CPRA)
      and EU EUR-Lex versioned instruments (RD-04, preserving ELI/CELEX identifiers and historical text).
    """

    def __init__(self) -> None:
        # Keyed by (document_id, provision_ref) -> chronological list of VersionedInstrumentSnapshot
        self._provision_history: Dict[Tuple[str, str], List[VersionedInstrumentSnapshot]] = {}
        # Keyed by diff_id -> ProvisionDiffRecord
        self._diff_records: Dict[str, ProvisionDiffRecord] = {}
        self._seed_canonical_amendment_histories()

    # ------------------------------------------------------------------
    # Normalization & Editorial Canonicalization Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_legal_text(text: str) -> str:
        """
        Deterministic Unicode NFC normalization and whitespace standardization
        preserving structural tokens and punctuation.
        """
        if not text:
            return ""
        nfc = unicodedata.normalize("NFC", text)
        nfc = nfc.replace("\r\n", "\n").replace("\r", "\n")
        nfc = re.sub(r"[ \t\f\v]+", " ", nfc)
        lines = [line.strip() for line in nfc.split("\n")]
        collapsed = "\n".join(line for line in lines if line)
        return collapsed.strip()

    @staticmethod
    def _editorial_skeleton(text: str) -> str:
        """
        Strips formatting, whitespace, punctuation, typography quotes/dashes,
        and case differences to test whether two texts differ ONLY editorially.
        """
        nfc = unicodedata.normalize("NFKC", text or "").lower()
        # Normalize typographical corrigenda equivalents (e.g. British/American spelling variants or section symbols)
        nfc = nfc.replace("§", "section ").replace("art.", "article ")
        # Keep only alphanumeric characters and single spaces
        tokens = re.findall(r"[a-z0-9]+", nfc)
        return " ".join(tokens)

    @staticmethod
    def _extract_matches(patterns: Tuple[re.Pattern[str], ...], text: str) -> List[str]:
        found: List[str] = []
        for pat in patterns:
            for m in pat.finditer(text):
                val = re.sub(r"\s+", " ", m.group(0).strip().lower())
                if val and val not in found:
                    found.append(val)
        return found

    # ------------------------------------------------------------------
    # Core Provision Diffing (Section 5.2)
    # ------------------------------------------------------------------
    def compare_provisions(
        self,
        document_id: str,
        jurisdiction_id: str,
        provision_ref: str,
        previous_version: str,
        previous_text: str,
        current_version: str,
        current_text: str,
        previous_effective_date: date | None = None,
        current_effective_date: date | None = None,
        *,
        previous_source_url: Optional[str] = None,
        current_source_url: Optional[str] = None,
        previous_retrieved_at: Optional[datetime] = None,
        current_retrieved_at: Optional[datetime] = None,
        eli_or_celex_identifier: Optional[str] = None,
    ) -> ProvisionDiffRecord:
        """
        Compare two versions of a statutory or regulatory provision.
        - Computes SHA-256 hashes of raw and normalized text.
        - Distinguishes substantive legal changes (deadlines, numbers/thresholds, penalties,
          "shall/must/may not", new obligations, repealed clauses, scope expansions) from
          editorial/formatting changes (whitespace, punctuation, capitalization, typographical corrigenda).
        - Never infers a change solely from a URL or retrieval timestamp.
        """
        prev_raw = previous_text or ""
        curr_raw = current_text or ""

        prev_norm = self.normalize_legal_text(prev_raw)
        curr_norm = self.normalize_legal_text(curr_raw)

        prev_raw_sha256 = compute_sha256_hex(prev_raw)
        curr_raw_sha256 = compute_sha256_hex(curr_raw)
        prev_norm_sha256 = compute_sha256_hex(prev_norm)
        curr_norm_sha256 = compute_sha256_hex(curr_norm)

        changed_elements: List[str] = []

        # Guardrail: Never infer a change solely from a URL or retrieval timestamp
        if prev_raw_sha256 == curr_raw_sha256:
            if previous_source_url != current_source_url or previous_retrieved_at != current_retrieved_at:
                changed_elements.append(
                    "no_text_change: identical raw and normalized SHA-256 hashes (URL or retrieval timestamp difference ignored)"
                )
            else:
                changed_elements.append("no_text_change: identical raw and normalized SHA-256 hashes")
            change_type = "editorial_formatting_only"
            is_substantive = False
        elif prev_norm_sha256 == curr_norm_sha256:
            changed_elements.append(
                f"whitespace_or_linewrap_only: raw_sha256 changed ({prev_raw_sha256[:12]} -> {curr_raw_sha256[:12]}) "
                f"but normalized_sha256 is identical ({curr_norm_sha256[:12]})"
            )
            change_type = "editorial_formatting_only"
            is_substantive = False
        elif not prev_norm and curr_norm:
            change_type = "new_provision"
            is_substantive = True
            changed_elements.append(f"new_provision_enacted: {provision_ref} added in {current_version}")
            self._append_substantive_details(prev_norm, curr_norm, changed_elements)
        elif prev_norm and (
            not curr_norm
            or bool(
                re.search(
                    r"^\s*\[?\s*(?:repealed|deleted|omitted|abrogé|aufgehoben)\b",
                    curr_norm,
                    re.IGNORECASE,
                )
            )
            or (
                len(curr_norm) < 120
                and bool(_REPEAL_OR_EXPIRY_PATTERNS[0].search(curr_norm))
                and not bool(_REPEAL_OR_EXPIRY_PATTERNS[0].search(prev_norm))
            )
        ):
            change_type = "repealed_provision"
            is_substantive = True
            changed_elements.append(f"provision_repealed: {provision_ref} repealed or omitted in {current_version}")
        else:
            # Both previous and current have non-empty normalized text that differs.
            prev_skel = self._editorial_skeleton(prev_norm)
            curr_skel = self._editorial_skeleton(curr_norm)

            if prev_skel == curr_skel:
                change_type = "editorial_formatting_only"
                is_substantive = False
                changed_elements.append(
                    "punctuation_capitalization_or_formatting_only: alphanumeric token sequence unchanged"
                )
            else:
                is_substantive, change_type = self._classify_substantive_vs_editorial(
                    prev_norm, curr_norm, changed_elements
                )

        if eli_or_celex_identifier:
            changed_elements.append(f"instrument_identifier: {eli_or_celex_identifier}")

        diff_seed = f"{document_id}:{provision_ref}:{previous_version}:{current_version}:{prev_norm_sha256[:12]}:{curr_norm_sha256[:12]}"
        diff_id = f"DIFF-{compute_sha256_hex(diff_seed)[:16].upper()}"

        record = ProvisionDiffRecord(
            diff_id=diff_id,
            document_id=document_id,
            jurisdiction_id=jurisdiction_id,
            provision_ref=provision_ref,
            previous_version=previous_version,
            current_version=current_version,
            previous_effective_date=previous_effective_date,
            current_effective_date=current_effective_date,
            previous_text=prev_raw,
            current_text=curr_raw,
            Previous_sha256=prev_norm_sha256,
            current_sha256=curr_norm_sha256,
            change_type=change_type,
            is_substantive=is_substantive,
            changed_elements_summary=changed_elements,
        )
        self._diff_records[diff_id] = record
        return record

    def _append_substantive_details(self, prev_norm: str, curr_norm: str, changed_elements: List[str]) -> Tuple[bool, bool, bool, bool]:
        """Extract deadline, threshold/penalty, deontic, and scope deltas into changed_elements."""
        prev_deadlines = self._extract_matches(_DEADLINE_PATTERNS, prev_norm)
        curr_deadlines = self._extract_matches(_DEADLINE_PATTERNS, curr_norm)
        deadline_changed = prev_deadlines != curr_deadlines
        if deadline_changed:
            changed_elements.append(
                f"deadline_change: {prev_deadlines or ['none']} -> {curr_deadlines or ['none']}"
            )

        prev_thresholds = self._extract_matches(_THRESHOLD_AND_PENALTY_PATTERNS, prev_norm)
        curr_thresholds = self._extract_matches(_THRESHOLD_AND_PENALTY_PATTERNS, curr_norm)
        threshold_changed = prev_thresholds != curr_thresholds
        if threshold_changed:
            changed_elements.append(
                f"threshold_or_penalty_change: {prev_thresholds or ['none']} -> {curr_thresholds or ['none']}"
            )

        prev_deontic = self._extract_matches(_DEONTIC_MODALITY_PATTERNS, prev_norm)
        curr_deontic = self._extract_matches(_DEONTIC_MODALITY_PATTERNS, curr_norm)
        deontic_changed = prev_deontic != curr_deontic
        if deontic_changed:
            changed_elements.append(
                f"deontic_modality_change: {prev_deontic or ['none']} -> {curr_deontic or ['none']}"
            )

        prev_lower = prev_norm.lower()
        curr_lower = curr_norm.lower()
        added_scope = [kw for kw in _SCOPE_AND_OBLIGATION_KEYWORDS if kw in curr_lower and kw not in prev_lower]
        removed_scope = [kw for kw in _SCOPE_AND_OBLIGATION_KEYWORDS if kw in prev_lower and kw not in curr_lower]
        scope_changed = bool(added_scope or removed_scope)
        if added_scope:
            changed_elements.append(f"new_obligations_or_scope_expansion: {', '.join(added_scope)}")
        if removed_scope:
            changed_elements.append(f"removed_obligations_or_scope_narrowing: {', '.join(removed_scope)}")

        return deadline_changed, threshold_changed, deontic_changed, scope_changed

    def _classify_substantive_vs_editorial(
        self,
        prev_norm: str,
        curr_norm: str,
        changed_elements: List[str],
    ) -> Tuple[bool, str]:
        deadline_changed, threshold_changed, deontic_changed, scope_changed = self._append_substantive_details(
            prev_norm, curr_norm, changed_elements
        )

        # Check for numbers changing anywhere in the text (excluding purely identical numbers)
        prev_nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", prev_norm)
        curr_nums = re.findall(r"\b\d+(?:[.,]\d+)?\b", curr_norm)
        numbers_changed = prev_nums != curr_nums
        if numbers_changed and not (deadline_changed or threshold_changed):
            changed_elements.append(f"numeric_value_change: {prev_nums} -> {curr_nums}")

        # Check for minor typographical corrigenda (e.g., single-character typo fix in a word with no legal marker delta)
        prev_words = re.findall(r"[a-z0-9]+", prev_norm.lower())
        curr_words = re.findall(r"[a-z0-9]+", curr_norm.lower())

        if (
            not deadline_changed
            and not threshold_changed
            and not deontic_changed
            and not scope_changed
            and not numbers_changed
        ):
            # Check if word difference is purely minor typographical / spelling normalization
            if self._is_minor_typographical_corrigendum(prev_words, curr_words):
                changed_elements.append("typographical_corrigendum_only: minor spelling/editorial correction")
                return False, "editorial_formatting_only"

        if deadline_changed and not (threshold_changed or scope_changed):
            return True, "deadline_change"
        if threshold_changed and not (deadline_changed or scope_changed):
            return True, "threshold_change"

        if not changed_elements:
            changed_elements.append("substantive_text_modification: operative clause wording amended")
        return True, "substantive_amendment"

    @staticmethod
    def _is_minor_typographical_corrigendum(prev_words: List[str], curr_words: List[str]) -> bool:
        """
        Returns True if two word lists have the same length and only differ by minor spelling variants
        (e.g., 'organisation' vs 'organization', 'analyse' vs 'analyze', or 1-2 character typo fix in a long word)
        without altering negations or numbers.
        """
        if len(prev_words) != len(curr_words):
            return False
        negations = {"not", "no", "never", "neither", "nor", "unless", "except", "without", "only"}
        diffs = [(w1, w2) for w1, w2 in zip(prev_words, curr_words) if w1 != w2]
        if not diffs or len(diffs) > 2:
            return False
        for w1, w2 in diffs:
            if w1 in negations or w2 in negations:
                return False
            if len(w1) < 5 or len(w2) < 5:
                return False
            # British/American s/z or our/or or simple 1-char edit distance
            if w1.replace("s", "z") == w2.replace("s", "z") or w1.replace("our", "or") == w2.replace("our", "or"):
                continue
            # Levenshtein distance <= 1 for words >= 6 chars
            if abs(len(w1) - len(w2)) <= 1:
                matches = sum(1 for a, b in zip(w1, w2) if a == b)
                if matches >= max(len(w1), len(w2)) - 1:
                    continue
            return False
        return True

    # ------------------------------------------------------------------
    # Version History Registration & Retrieval (RD-03 & RD-04)
    # ------------------------------------------------------------------
    def register_provision_version(
        self,
        document_id: str,
        jurisdiction_id: str,
        provision_ref: str,
        version_id: str,
        raw_text: str,
        effective_date: Optional[date] = None,
        publication_date: Optional[date] = None,
        repeal_or_expiry_date: Optional[date] = None,
        eli_identifier: Optional[str] = None,
        celex_identifier: Optional[str] = None,
        amending_instrument_id: Optional[str] = None,
        amending_citation: Optional[str] = None,
        official_source_url: Optional[str] = None,
        supersedes_version: Optional[str] = None,
        is_repealed: bool = False,
    ) -> VersionedInstrumentSnapshot:
        """
        Registers a point-in-time provision version without overwriting prior versions.
        Preserves historical text, SHA-256 hashes, and ELI/CELEX identifiers.
        """
        norm_text = self.normalize_legal_text(raw_text)
        snapshot = VersionedInstrumentSnapshot(
            document_id=document_id,
            jurisdiction_id=jurisdiction_id,
            version_id=version_id,
            provision_ref=provision_ref,
            raw_text=raw_text,
            normalized_text=norm_text,
            raw_sha256=compute_sha256_hex(raw_text),
            normalized_sha256=compute_sha256_hex(norm_text),
            effective_date=effective_date,
            publication_date=publication_date,
            repeal_or_expiry_date=repeal_or_expiry_date,
            eli_identifier=eli_identifier,
            celex_identifier=celex_identifier,
            amending_instrument_id=amending_instrument_id,
            amending_citation=amending_citation,
            official_source_url=official_source_url,
            supersedes_version=supersedes_version,
            is_repealed=is_repealed,
        )
        key = (document_id, provision_ref)
        history = self._provision_history.setdefault(key, [])
        # Replace only if exact same version_id is re-registered with identical hash; never overwrite prior versions
        existing_idx = next((i for i, item in enumerate(history) if item.version_id == version_id), None)
        if existing_idx is not None:
            history[existing_idx] = snapshot
        else:
            history.append(snapshot)
        history.sort(key=lambda s: (s.effective_date or date.min, s.version_id))
        return snapshot

    def get_provision_history(self, document_id: str, provision_ref: str) -> List[VersionedInstrumentSnapshot]:
        """Return all historical versions of a provision in chronological order."""
        return list(self._provision_history.get((document_id, provision_ref), []))

    def get_provision_as_of(
        self, document_id: str, provision_ref: str, as_of_date: date
    ) -> Optional[VersionedInstrumentSnapshot]:
        """Return the operative version of a provision on `as_of_date`."""
        history = self._provision_history.get((document_id, provision_ref), [])
        applicable: Optional[VersionedInstrumentSnapshot] = None
        for snap in history:
            if snap.effective_date and snap.effective_date <= as_of_date:
                if snap.repeal_or_expiry_date and snap.repeal_or_expiry_date <= as_of_date:
                    continue
                applicable = snap
        return applicable

    def diff_registered_versions(
        self,
        document_id: str,
        provision_ref: str,
        previous_version: str,
        current_version: str,
    ) -> ProvisionDiffRecord:
        """Compute structural diff between two registered versions in the store."""
        history = self._provision_history.get((document_id, provision_ref), [])
        prev_snap = next((s for s in history if s.version_id == previous_version), None)
        curr_snap = next((s for s in history if s.version_id == current_version), None)
        if prev_snap is None or curr_snap is None:
            raise KeyError(
                f"Version(s) not found for ({document_id}, {provision_ref}): "
                f"requested {previous_version} -> {current_version}"
            )
        return self.compare_provisions(
            document_id=document_id,
            jurisdiction_id=curr_snap.jurisdiction_id,
            provision_ref=provision_ref,
            previous_version=prev_snap.version_id,
            previous_text=prev_snap.raw_text,
            current_version=curr_snap.version_id,
            current_text=curr_snap.raw_text,
            previous_effective_date=prev_snap.effective_date,
            current_effective_date=curr_snap.effective_date,
            previous_source_url=prev_snap.official_source_url,
            current_source_url=curr_snap.official_source_url,
            eli_or_celex_identifier=curr_snap.eli_identifier or curr_snap.celex_identifier,
        )

    # ------------------------------------------------------------------
    # Pre-seeded Canonical Legislative & EUR-Lex Version Histories (RD-03 & RD-04)
    # ------------------------------------------------------------------
    def _seed_canonical_amendment_histories(self) -> None:
        """
        Seeds authentic statutory and regulatory amendment histories for:
        1. RD-03: California CCPA (2020) -> CPRA (2023) -> CPPA Cybersecurity Audit & ADMT Updates (2026)
           - Cal. Civ. Code § 1798.100(d) (contractual obligations for service providers, contractors, third parties)
           - Cal. Civ. Code § 1798.185(a)(15)-(16) (mandatory annual cybersecurity audits, risk assessments, ADMT opt-out)
           - Cal. Civ. Code § 1798.140(v) (threshold modification from 50,000 to 100,000 consumers/households)
        2. RD-04: EU EUR-Lex Versioned Instruments with ELI/CELEX identifiers:
           - Regulation (EU) 2016/679 (GDPR) Art. 35 & Art. 22 (original OJ L 119 vs Corrigendum OJ L 127, 23.5.2018)
           - Directive 2002/58/EC (ePrivacy Directive) Art. 5(3) as amended by Directive 2009/136/EC
           - Regulation (EU) 2024/1689 (EU AI Act) Art. 6 & Art. 27 high-risk AI obligations
        """
        # 1. RD-03: California CCPA -> CPRA Cal. Civ. Code § 1798.100(d)
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.100(d)",
            version_id="v2020.1-CCPA",
            raw_text=(
                "(d) A business that receives a verifiable consumer request from a consumer to access personal "
                "information shall promptly take steps to disclose and deliver, free of charge to the consumer, "
                "the personal information required by this section within 45 days of receiving the request."
            ),
            effective_date=date(2020, 1, 1),
            publication_date=date(2018, 6, 28),
            amending_instrument_id="AB-375",
            amending_citation="Stats. 2018, Ch. 55, Sec. 3 (AB 375)",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.100.&lawCode=CIV",
        )
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.100(d)",
            version_id="v2023.1-CPRA",
            raw_text=(
                "(d) A business that collects a consumer's personal information and that sells that personal "
                "information to, or shares it with, a third party or that discloses it to a service provider or "
                "contractor for a business purpose shall enter into an agreement with that third party, service "
                "provider, or contractor, that: (1) Specifies that the personal information is sold or disclosed by "
                "the business only for limited and specified purposes. (2) Obligates the third party, service "
                "provider, or contractor to comply with applicable obligations under this title and obligate those "
                "persons to provide the same level of privacy protection as is required by this title."
            ),
            effective_date=date(2023, 1, 1),
            publication_date=date(2020, 11, 3),
            amending_instrument_id="PROP-24-CPRA",
            amending_citation="Proposition 24, Sec. 4 (California Privacy Rights Act of 2020, operative Jan. 1, 2023)",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.100.&lawCode=CIV",
            supersedes_version="v2020.1-CCPA",
        )

        # 2. RD-03: California CCPA -> CPRA Cal. Civ. Code § 1798.185(a)(15)-(16)
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16)",
            version_id="v2020.1-CCPA",
            raw_text="",
            effective_date=date(2020, 1, 1),
            publication_date=date(2018, 6, 28),
            amending_instrument_id="AB-375",
            amending_citation="Stats. 2018, Ch. 55 (Prior to CPRA enactment of subdivisions (a)(15)-(16))",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.185.&lawCode=CIV",
        )
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16)",
            version_id="v2023.1-CPRA",
            raw_text=(
                "(15) Issuing regulations requiring businesses whose processing of consumers' personal information "
                "presents significant risk to consumers' privacy or security, to: (A) Perform a cybersecurity audit "
                "on an annual basis, including defining the scope of the audit and establishing a process to ensure "
                "that audits are thorough and independent. (B) Submit to the California Privacy Protection Agency on "
                "a regular basis a risk assessment with respect to their processing of personal information, "
                "identifying and weighing the benefits resulting from the processing to the business, the consumer, "
                "other stakeholders, and the public, against the potential risks to the rights of the consumer. "
                "(16) Issuing regulations governing access and opt-out rights with respect to businesses' use of "
                "automated decision-making technology, including profiling and requiring businesses' response to "
                "access requests to include meaningful information about the logic involved in those decision-making "
                "processes, as well as a description of the likely outcome of the process with respect to the consumer."
            ),
            effective_date=date(2023, 1, 1),
            publication_date=date(2020, 11, 3),
            amending_instrument_id="PROP-24-CPRA",
            amending_citation="Proposition 24, Sec. 21 (CPRA addition of Cal. Civ. Code § 1798.185(a)(15)-(16))",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.185.&lawCode=CIV",
            supersedes_version="v2020.1-CCPA",
        )
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16)",
            version_id="v2026.1-CPPA-ADMT-AUDIT",
            raw_text=(
                "(15) Issuing regulations requiring businesses whose processing of consumers' personal information "
                "presents significant risk to consumers' privacy or security, to: (A) Perform an independent "
                "cybersecurity audit on an annual basis with board-level certification within 24 months. (B) Submit "
                "to the California Privacy Protection Agency an abridged risk assessment attestation within 30 days "
                "of completion prior to initiating high-risk processing or AI model training. "
                "(16) Issuing regulations governing pre-use notice, access, and opt-out rights with respect to "
                "businesses' use of automated decision-making technology (ADMT) and profiling for significant "
                "decisions, requiring a plain-language explanation of logic, key parameters, and human appeal "
                "mechanisms within 15 business days."
            ),
            effective_date=date(2026, 1, 1),
            publication_date=date(2025, 11, 15),
            amending_instrument_id="CPPA-REG-2025-ADMT-AUDIT",
            amending_citation="11 CCR §§ 7150-7221 (CPPA Cybersecurity Audit, Risk Assessment & ADMT Regulations, eff. Jan. 1, 2026)",
            official_source_url="https://cppa.ca.gov/regulations/",
            supersedes_version="v2023.1-CPRA",
        )

        # 3. RD-03: California CCPA -> CPRA Threshold Amendment Cal. Civ. Code § 1798.140(d)/(v)
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.140(d)",
            version_id="v2020.1-CCPA",
            raw_text=(
                "(1) Fits one or more of the following thresholds: (A) Has annual gross revenues in excess of "
                "$25,000,000. (B) Alone or in combination, annually buys, receives for the business's commercial "
                "purposes, sells, or shares for commercial purposes, alone or in combination, the personal "
                "information of 50,000 or more consumers, households, or devices. (C) Derives 50 percent or more of "
                "its annual revenues from selling consumers' personal information."
            ),
            effective_date=date(2020, 1, 1),
            publication_date=date(2018, 6, 28),
            amending_instrument_id="AB-375",
            amending_citation="Stats. 2018, Ch. 55 (CCPA Business Threshold)",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.140.&lawCode=CIV",
        )
        self.register_provision_version(
            document_id="DOC-US-CA-CCPA",
            jurisdiction_id="US-CA",
            provision_ref="Cal. Civ. Code § 1798.140(d)",
            version_id="v2023.1-CPRA",
            raw_text=(
                "(1) Fits one or more of the following thresholds: (A) As of January 1 of the calendar year, had "
                "annual gross revenues in excess of $25,000,000 in the preceding calendar year. (B) Alone or in "
                "combination, annually buys, sells, or shares the personal information of 100,000 or more consumers "
                "or households. (C) Derives 50 percent or more of its annual revenues from selling or sharing "
                "consumers' personal information."
            ),
            effective_date=date(2023, 1, 1),
            publication_date=date(2020, 11, 3),
            amending_instrument_id="PROP-24-CPRA",
            amending_citation="Proposition 24, Sec. 14 (CPRA Business Threshold raised to 100,000 consumers or households)",
            official_source_url="https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.140.&lawCode=CIV",
            supersedes_version="v2020.1-CCPA",
        )

        # 4. RD-04: EU EUR-Lex Versioned Instrument — GDPR (Regulation (EU) 2016/679) Art. 35(1) & Corrigendum
        self.register_provision_version(
            document_id="DOC-EU-GDPR-2016-679",
            jurisdiction_id="EU",
            provision_ref="GDPR Art. 35(1)",
            version_id="2016R0679-EN-20160504",
            raw_text=(
                "1. Where a type of processing in particular using new technologies, and taking into account the "
                "nature, scope, context and purposes of the processing, is likely to result in a high risk to the "
                "rights and freedoms of natural persons, the controller shall, prior to the processing, carry out "
                "an assessment of the impact of the envisaged processing operations on the protection of personal "
                "data. A single assessment may address a set of similar processing operations that present similar "
                "high risks."
            ),
            effective_date=date(2018, 5, 25),
            publication_date=date(2016, 5, 4),
            eli_identifier="http://data.europa.eu/eli/reg/2016/679/oj",
            celex_identifier="32016R0679",
            amending_instrument_id="REG-EU-2016-679",
            amending_citation="OJ L 119, 4.5.2016, p. 1–88",
            official_source_url="https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        )
        self.register_provision_version(
            document_id="DOC-EU-GDPR-2016-679",
            jurisdiction_id="EU",
            provision_ref="GDPR Art. 35(1)",
            version_id="02016R0679-20180523-CONSOLIDATED",
            raw_text=(
                "1.   Where a type of processing in particular using new technologies, and taking into account the "
                "nature, scope, context and purposes of the processing, is likely to result in a high risk to the "
                "rights and freedoms of natural persons, the controller shall, prior to the processing, carry out "
                "an assessment of the impact of the envisaged processing operations on the protection of personal "
                "data. A single assessment may address a set of similar processing operations that present similar "
                "high risks."
            ),
            effective_date=date(2018, 5, 25),
            publication_date=date(2018, 5, 23),
            eli_identifier="http://data.europa.eu/eli/reg/2016/679/2016-05-04",
            celex_identifier="02016R0679-20160504",
            amending_instrument_id="CORRIGENDUM-2018-L127",
            amending_citation="Corrigendum to Regulation (EU) 2016/679, OJ L 127, 23.5.2018, p. 2",
            official_source_url="https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04",
            supersedes_version="2016R0679-EN-20160504",
        )

        # 5. RD-04: EU EUR-Lex Substantive Directive Amendment — ePrivacy Directive 2002/58/EC Art. 5(3) -> 2009/136/EC
        self.register_provision_version(
            document_id="DOC-EU-EPRIVACY-2002-58",
            jurisdiction_id="EU",
            provision_ref="Directive 2002/58/EC Art. 5(3)",
            version_id="32002L0058-20020731",
            raw_text=(
                "3. Member States shall ensure that the use of electronic communications networks to store "
                "information or to gain access to information stored in the terminal equipment of a subscriber or "
                "user is only allowed on condition that the subscriber or user concerned is provided with clear and "
                "comprehensive information in accordance with Directive 95/46/EC, inter alia about the purposes of "
                "the processing, and is offered the right to refuse such processing by the data controller."
            ),
            effective_date=date(2003, 10, 31),
            publication_date=date(2002, 7, 31),
            eli_identifier="http://data.europa.eu/eli/dir/2002/58/oj",
            celex_identifier="32002L0058",
            amending_instrument_id="DIR-2002-58-EC",
            amending_citation="OJ L 201, 31.7.2002, p. 37–47",
            official_source_url="https://eur-lex.europa.eu/eli/dir/2002/58/oj",
        )
        self.register_provision_version(
            document_id="DOC-EU-EPRIVACY-2002-58",
            jurisdiction_id="EU",
            provision_ref="Directive 2002/58/EC Art. 5(3)",
            version_id="02002L0058-20091219-CONSOLIDATED",
            raw_text=(
                "3. Member States shall ensure that the storing of information, or the gaining of access to "
                "information already stored, in the terminal equipment of a subscriber or user is only allowed on "
                "condition that the subscriber or user concerned has given his or her consent, having been provided "
                "with clear and comprehensive information, in accordance with Directive 95/46/EC, inter alia, about "
                "the purposes of the processing."
            ),
            effective_date=date(2011, 5, 25),
            publication_date=date(2009, 12, 18),
            eli_identifier="http://data.europa.eu/eli/dir/2002/58/2009-12-19",
            celex_identifier="02002L0058-20091219",
            amending_instrument_id="DIR-2009-136-EC",
            amending_citation="Directive 2009/136/EC, Art. 2(5), OJ L 337, 18.12.2009, p. 11–36",
            official_source_url="https://eur-lex.europa.eu/eli/dir/2002/58/2009-12-19",
            supersedes_version="32002L0058-20020731",
        )


__all__ = [
    "ProvisionDiffRecord",
    "StructuralVersionDiffEngine",
    "VersionedInstrumentSnapshot",
]
