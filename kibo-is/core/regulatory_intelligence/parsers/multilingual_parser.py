"""
KIBO Privacy OS — Multilingual Document Parsing and Normalization (Worker G16)
Implements Section 4.3 & RD-08:
- Deterministic Unicode NFC normalization and whitespace standardization while preserving section/article boundaries
- Cryptographic SHA-256 hashing (`raw_document_sha256` and `normalized_text_sha256`)
- Multilingual statutory/regulatory provision extraction across English (`en`), French (`fr`), German (`de`),
  and EU member-state languages (`es`, `it`, `nl`, `pl`, `pt`, `sv`, etc.)
- Guaranteed exact character offset slicing (`normalized_text[text_start_offset:text_end_offset] == exact_source_excerpt`)
- Bilingual and translated passage alignment that never assumes an unverified English translation is legally authoritative
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    from .. import compute_sha256_hex
except ImportError:
    import hashlib

    def compute_sha256_hex(content: str | bytes) -> str:
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()


SUPPORTED_EU_AND_GLOBAL_LANGUAGES: Tuple[str, ...] = (
    "en",  # English
    "fr",  # French (Canada Federal, Quebec Law 25, France CNIL, EU)
    "de",  # German (BDSG, BfDI, Austria DSB, EU)
    "es",  # Spanish (AEPD, LOPDGDD, EU)
    "it",  # Italian (Garante, Codice Privacy, EU)
    "nl",  # Dutch (AP, UAVG, EU)
    "pl",  # Polish (UODO, EU)
    "pt",  # Portuguese (CNPD, LGPD, EU)
    "sv",  # Swedish (IMY, EU)
    "da",  # Danish
    "fi",  # Finnish
    "el",  # Greek
    "cs",  # Czech
    "ro",  # Romanian
    "hu",  # Hungarian
    "bg",  # Bulgarian
    "sk",  # Slovak
    "hr",  # Croatian
    "lt",  # Lithuanian
    "sl",  # Slovenian
    "lv",  # Latvian
    "et",  # Estonian
    "ga",  # Irish
    "mt",  # Maltese
)

OFFICIAL_BILINGUAL_COAUTHORITATIVE_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("en", "fr"),
    ("fr", "en"),
)


@dataclass(frozen=True)
class NormalizedDocumentResult:
    """Container holding normalized text alongside raw and normalized SHA-256 hashes."""
    raw_text: str
    normalized_text: str
    raw_document_sha256: str
    normalized_text_sha256: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "raw_document_sha256": self.raw_document_sha256,
            "normalized_text_sha256": self.normalized_text_sha256,
        }


@dataclass(frozen=True)
class ProvisionSegment:
    """Structured statutory/regulatory provision with verified character offsets."""
    source_section: str
    article: Optional[str]
    subsection: Optional[str]
    paragraph: Optional[str]
    text_start_offset: int
    text_end_offset: int
    exact_source_excerpt: str
    source_language: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_section": self.source_section,
            "article": self.article,
            "subsection": self.subsection,
            "paragraph": self.paragraph,
            "text_start_offset": self.text_start_offset,
            "text_end_offset": self.text_end_offset,
            "exact_source_excerpt": self.exact_source_excerpt,
            "source_language": self.source_language,
        }


@dataclass
class TranslationAlignmentResult:
    """Aligned original and translated legal passages with explicit authority status."""
    original_lang: str
    translated_lang: str
    translation_status: str
    is_translation_authoritative: bool
    requires_legal_review_for_translation: bool
    raw_original_sha256: str
    normalized_original_sha256: str
    raw_translated_sha256: str
    normalized_translated_sha256: str
    original_normalized_text: str
    translated_normalized_text: str
    original_language_passages: Dict[str, str] = field(default_factory=dict)
    translated_passages: Dict[str, str] = field(default_factory=dict)
    aligned_provisions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_lang": self.original_lang,
            "translated_lang": self.translated_lang,
            "translation_status": self.translation_status,
            "is_translation_authoritative": self.is_translation_authoritative,
            "requires_legal_review_for_translation": self.requires_legal_review_for_translation,
            "raw_original_sha256": self.raw_original_sha256,
            "normalized_original_sha256": self.normalized_original_sha256,
            "raw_translated_sha256": self.raw_translated_sha256,
            "normalized_translated_sha256": self.normalized_translated_sha256,
            "original_normalized_text": self.original_normalized_text,
            "translated_normalized_text": self.translated_normalized_text,
            "original_language_passages": self.original_language_passages,
            "translated_passages": self.translated_passages,
            "aligned_provisions": self.aligned_provisions,
        }


class MultilingualLegalParser:
    """
    Deterministic multilingual legal document parser and normalizer.

    Supports English (`en`), French (`fr`), German (`de`), and EU member-state languages
    (`es`, `it`, `nl`, `pl`, `pt`, `sv`, etc.).
    Guarantees:
    1. Unicode NFC normalization and canonical whitespace/newline handling while preserving
       statutory/regulatory section and article boundaries.
    2. Cryptographic SHA-256 digests (`raw_document_sha256` and `normalized_text_sha256`).
    3. Exact character offset slicing: `normalized_text[start:end] == exact_source_excerpt`.
    4. Strict translation governance (Section 4.3 & RD-08): unverified machine translations
       are explicitly marked `unverified_machine_translation` and never treated as legally
       authoritative.
    """

    # Inline sub-unit extractors applied within a provision block
    _SUBSECTION_PATTERNS: Dict[str, List[re.Pattern[str]]] = {
        "en": [
            re.compile(r"\b[Ss]ubsection\s+(\([a-zA-Z0-9]+\)|\d+(?:\.\d+)*)"),
            re.compile(r"(?:^|\s)(\(\d+\)|\([a-z]\))(?=\s+[A-Z])"),
        ],
        "fr": [
            re.compile(r"\b(?:alin[ée]a|al\.)\s*(\d+(?:er|e)?|\([0-9a-z]+\))", re.IGNORECASE),
            re.compile(r"\b(?:paragraphe|par\.)\s*(\(\d+\)|\d+(?:\.\d+)*)", re.IGNORECASE),
            re.compile(r"(?:^|\s)(\(\d+\))(?=\s+[A-ZÉÈÊÀÂÎÔÛÇ])"),
        ],
        "de": [
            re.compile(r"\b(?:Absatz|Abs\.)\s*(\(\d+\)|\d+[a-z]?)", re.IGNORECASE),
            re.compile(r"(?:^|\s)(\(\d+\))(?=\s+[A-ZÄÖÜ])"),
        ],
        "default": [
            re.compile(
                r"\b(?:apartado|apdo\.|comma|lid|ust\.|ustęp|n\.º|parágrafo|stycke|stycket)\s*(\(\d+\)|\d+[a-z]?)",
                re.IGNORECASE,
            ),
            re.compile(r"(?:^|\s)(\(\d+\))(?=\s+[A-ZÀ-ÖØ-Þ])"),
        ],
    }

    _PARAGRAPH_PATTERNS: Dict[str, List[re.Pattern[str]]] = {
        "en": [
            re.compile(r"\b(?:[Pp]aragraph|[Pp]ara\.)\s*(\([a-zA-Z0-9]+\)|\d+(?:\.\d+)*)"),
            re.compile(r"(?:^|\n)\s*(\([a-z0-9]+\)|\d+\.)\s+"),
        ],
        "fr": [
            re.compile(r"\b(?:paragraphe|par\.|alin[ée]a|al\.)\s*(\d+(?:er|e|°)?|\([a-z0-9]+\))", re.IGNORECASE),
            re.compile(r"(?:^|\n)\s*(\d+°|\([a-z0-9]+\))\s+"),
        ],
        "de": [
            re.compile(r"\b(?:Satz|S\.|Nummer|Nr\.)\s*(\d+[a-z]?)", re.IGNORECASE),
            re.compile(r"(?:^|\n)\s*(\d+\.)\s+"),
        ],
        "default": [
            re.compile(
                r"\b(?:párrafo|lettera|lett\.|onderdeel|pkt|punkt|alínea|alinea)\s*(\([a-z0-9]+\)|\d+[a-z]?|[a-z]\))",
                re.IGNORECASE,
            ),
        ],
    }

    # Line-anchored heading patterns across languages
    # Matches top-level statutory/regulatory headings at the start of a line
    _HEADING_PATTERNS: Dict[str, List[Tuple[str, re.Pattern[str]]]] = {
        "en": [
            # e.g. "45 CFR § 164.404", "16 CFR § 314.4", "5 U.S.C. § 552a"
            (
                "cfr_usc_section",
                re.compile(
                    r"^(?P<full>(?P<title>\d+)\s+(?:CFR|C\.F\.R\.|U\.S\.C\.)\s*(?:§+|sec\.?|section)\s*(?P<num>\d+(?:\.\d+)*(?:[a-zA-Z0-9\-]*))(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "§ 1798.100", "§§ 1798.100", "§ 164.502(a)"
            (
                "symbol_section",
                re.compile(
                    r"^(?P<full>§+\s*(?P<num>\d+(?:[\.\-]\d+)*[a-zA-Z]?)(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                ),
            ),
            # e.g. "Section 17", "Sec. 5", "SECTION 1798.105", "Section 12(1)"
            (
                "section",
                re.compile(
                    r"^(?P<full>(?:Section|Sec\.)\s+(?P<num>\d+(?:[\.\-]\d+)*[a-zA-Z]?)(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Article 35", "Art. 5(1)", "ARTICLE 82"
            (
                "article",
                re.compile(
                    r"^(?P<full>(?:Article|Art\.)\s+(?P<num>[IVXLCDM]+|\d+(?:[\.\-]\d+)*[a-zA-Z]?)(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Chapter V", "Chapter 3", "Part IV"
            (
                "chapter",
                re.compile(
                    r"^(?P<full>(?:Chapter|Part|Title|Division|Schedule)\s+(?P<num>[IVXLCDM]+|\d+(?:[\.\-]\d+)*[a-zA-Z]?))\b",
                    re.IGNORECASE,
                ),
            ),
        ],
        "fr": [
            # e.g. "Article 17", "art. 3.3", "Art. 12(1)", "Article 1er"
            (
                "article",
                re.compile(
                    r"^(?P<full>(?:Article|Art\.)\s+(?P<num>\d+(?:er|e)?(?:[\.\-]\d+)*[a-zA-Z]?)(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Chapitre V", "Chapitre 3", "Titre II", "Section IV"
            (
                "chapter",
                re.compile(
                    r"^(?P<full>(?:Chapitre|Titre|Section|Annexe)\s+(?P<num>[IVXLCDM]+|\d+(?:er|e)?(?:[\.\-]\d+)*[a-zA-Z]?))\b",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Loi 25, art. 3.3" or "Loi 25" or "L.R.C. (1985), ch. P-21, art. 5"
            (
                "loi",
                re.compile(
                    r"^(?P<full>Loi\s+(?:n°\s*|sur\s+[a-zA-Zéèêàâîôûç\s]+,\s*)?(?P<num>\d+(?:[\-\.]\d+)*)(?:\s*,?\s*(?:art\.|article)\s*(?P<art>\d+(?:[\.\-]\d+)*))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "§ 3" or Quebec numbered section "3.3." at start of line followed by uppercase
            (
                "numbered_article",
                re.compile(
                    r"^(?P<full>§+\s*(?P<num>\d+(?:[\.\-]\d+)*))",
                ),
            ),
        ],
        "de": [
            # e.g. "§ 38 BDSG", "§ 26 Abs. 1 Satz 1 BDSG", "§ 26", "§ 22 Absatz (1)"
            (
                "paragraph_symbol",
                re.compile(
                    r"^(?P<full>§+\s*(?P<num>\d+[a-zA-Z]?)(?:\s+(?:Absatz|Abs\.)\s*(?P<sub>\(\d+\)|\d+[a-z]?))?(?:\s+(?:Satz|S\.)\s*(?P<para>\d+))?(?:\s+(?P<code_name>[A-ZÄÖÜ]{2,10}))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Artikel 35", "Art. 6 Abs. 1", "Artikel 82 DSGVO"
            (
                "article",
                re.compile(
                    r"^(?P<full>(?:Artikel|Art\.)\s+(?P<num>\d+[a-zA-Z]?)(?:\s+(?:Absatz|Abs\.)\s*(?P<sub>\(\d+\)|\d+[a-z]?))?(?:\s+(?:Satz|S\.)\s*(?P<para>\d+))?(?:\s+(?P<code_name>[A-ZÄÖÜ]{2,10}))?)",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Absatz (1)", "Absatz 2", "Abs. 1 Satz 1" when standalone heading line
            (
                "absatz_standalone",
                re.compile(
                    r"^(?P<full>(?:Absatz|Abs\.)\s*(?P<sub>\(\d+\)|\d+[a-z]?)(?:\s+(?:Satz|S\.)\s*(?P<para>\d+))?)\s*$",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Satz 1" when standalone heading line
            (
                "satz_standalone",
                re.compile(
                    r"^(?P<full>(?:Satz|S\.)\s*(?P<para>\d+))\s*$",
                    re.IGNORECASE,
                ),
            ),
            # e.g. "Kapitel V", "Abschnitt 2", "Teil 3"
            (
                "chapter",
                re.compile(
                    r"^(?P<full>(?:Kapitel|Abschnitt|Teil|Unterabschnitt)\s+(?P<num>[IVXLCDM]+|\d+(?:[\.\-]\d+)*))\b",
                    re.IGNORECASE,
                ),
            ),
        ],
        "default": [
            # EU member-state languages:
            # ES: Artículo 12, Art. 12, Capítulo III
            # IT: Articolo 12, Art. 12, Capo III
            # NL: Artikel 12, Art. 12, Hoofdstuk III
            # PL: Artykuł 12, Art. 12, § 3, Rozdział III
            # PT: Artigo 12.º, Artigo 12, Art. 12, Capítulo III
            # SV: Artikel 12, 12 §, 3 kap. 2 §
            (
                "eu_article",
                re.compile(
                    r"^(?P<full>(?:Art[íi]culo|Articolo|Artikel|Artykuł|Artigo|Art\.|Article|Section|Sec\.)\s+(?P<num>\d+(?:\.º|º|er|e)?(?:[\.\-]\d+)*[a-zA-Z]?)(?:\s*(?P<sub>\([a-zA-Z0-9]+\)))?)",
                    re.IGNORECASE,
                ),
            ),
            (
                "swedish_or_symbol_section",
                re.compile(
                    r"^(?P<full>(?:(?P<chap>\d+)\s*kap\.\s*)?(?:§+\s*(?P<num1>\d+(?:[\.\-]\d+)*[a-zA-Z]?)|(?P<num2>\d+[a-zA-Z]?)\s*§))",
                    re.IGNORECASE,
                ),
            ),
            (
                "eu_chapter",
                re.compile(
                    r"^(?P<full>(?:Cap[íi]tulo|Capo|Hoofdstuk|Rozdział|Kapitel|Kapitel|Chapitre|Chapter)\s+(?P<num>[IVXLCDM]+|\d+(?:[\.\-]\d+)*))\b",
                    re.IGNORECASE,
                ),
            ),
        ],
    }

    def __init__(self) -> None:
        self.last_raw_document_sha256: Optional[str] = None
        self.last_normalized_text_sha256: Optional[str] = None

    def normalize_document(self, raw_text: str) -> NormalizedDocumentResult:
        """
        Normalizes `raw_text` using Unicode NFC, standardizes line endings and whitespace
        while preserving section/article boundaries, and returns both `raw_document_sha256`
        and `normalized_text_sha256`.
        """
        if not isinstance(raw_text, str):
            raise TypeError("raw_text must be a string")

        raw_sha256 = compute_sha256_hex(raw_text)
        normalized = self._normalize_text_internal(raw_text)
        normalized_sha256 = compute_sha256_hex(normalized)

        self.last_raw_document_sha256 = raw_sha256
        self.last_normalized_text_sha256 = normalized_sha256

        return NormalizedDocumentResult(
            raw_text=raw_text,
            normalized_text=normalized,
            raw_document_sha256=raw_sha256,
            normalized_text_sha256=normalized_sha256,
        )

    def normalize_text(self, raw_text: str) -> str:
        """
        Normalizes Unicode (NFC), standardizes line endings and whitespace while preserving
        section/article boundaries, and computes `self.last_raw_document_sha256` and
        `self.last_normalized_text_sha256`.
        """
        result = self.normalize_document(raw_text)
        return result.normalized_text

    @staticmethod
    def compute_document_hashes(raw_text: str, normalized_text: Optional[str] = None) -> Dict[str, str]:
        """Returns `raw_document_sha256` and `normalized_text_sha256` for a document."""
        if normalized_text is None:
            normalized_text = MultilingualLegalParser._normalize_text_internal(raw_text)
        return {
            "raw_document_sha256": compute_sha256_hex(raw_text),
            "normalized_text_sha256": compute_sha256_hex(normalized_text),
        }

    @staticmethod
    def _normalize_text_internal(raw_text: str) -> str:
        # 1. Unicode NFC canonical composition (unifies accented characters in FR/DE/EU languages)
        text = unicodedata.normalize("NFC", raw_text)

        # 2. Remove BOM and zero-width formatting artifacts
        text = text.replace("\ufeff", "").replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")

        # 3. Standardize all line endings (CRLF, CR, Unicode line/paragraph separators) to LF (\n)
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u2028", "\n").replace("\u2029", "\n\n")

        # 4. Replace non-breaking spaces and thin/figure spaces with standard ASCII space
        text = re.sub(r"[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000\t]", " ", text)

        # 5. Normalize horizontal whitespace per line while preserving line/section boundaries
        lines = text.split("\n")
        cleaned_lines: List[str] = []
        for line in lines:
            # Collapse multiple horizontal spaces into one space and strip trailing/leading spaces
            compact_line = re.sub(r" {2,}", " ", line).strip()
            cleaned_lines.append(compact_line)

        text = "\n".join(cleaned_lines)

        # 6. Collapse 3+ consecutive newlines into double newline (\n\n) to preserve section boundaries cleanly
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _get_heading_patterns(self, language: str) -> List[Tuple[str, re.Pattern[str]]]:
        lang = (language or "en").lower().split("-")[0]
        if lang in self._HEADING_PATTERNS:
            # Also append fallback patterns that don't conflict so multi-format citations work seamlessly
            primary = list(self._HEADING_PATTERNS[lang])
            for fallback_kind, fallback_pat in self._HEADING_PATTERNS["default"]:
                primary.append((fallback_kind, fallback_pat))
            return primary
        return self._HEADING_PATTERNS["default"] + self._HEADING_PATTERNS["en"]

    def _match_heading_line(self, line: str, language: str) -> Optional[Dict[str, Optional[str]]]:
        """Attempts to match a statutory/regulatory heading at the start of `line`."""
        if not line:
            return None

        patterns = self._get_heading_patterns(language)
        for kind, pattern in patterns:
            m = pattern.match(line)
            if not m:
                continue

            groups = m.groupdict()
            full_heading = groups.get("full", m.group(0)).strip()
            num = groups.get("num") or groups.get("num1") or groups.get("num2")
            sub = groups.get("sub")
            para = groups.get("para")
            art = groups.get("art")

            source_section = full_heading
            article: Optional[str] = None
            subsection: Optional[str] = sub
            paragraph: Optional[str] = para

            if kind in ("article", "eu_article"):
                article = f"Article {num}" if num else full_heading
            elif kind == "loi" and art:
                article = f"art. {art}"
            elif kind == "paragraph_symbol":
                article = None
            elif kind == "absatz_standalone":
                subsection = sub
            elif kind == "satz_standalone":
                paragraph = para

            return {
                "kind": kind,
                "source_section": source_section,
                "article": article,
                "subsection": subsection,
                "paragraph": paragraph,
            }
        return None

    def _refine_subunits(
        self,
        excerpt: str,
        language: str,
        initial_article: Optional[str],
        initial_subsection: Optional[str],
        initial_paragraph: Optional[str],
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extracts inline article, subsection (`Absatz`, `alinéa`, `(1)`), and paragraph (`Satz`, `(a)`) markers."""
        lang = (language or "en").lower().split("-")[0]
        article = initial_article
        subsection = initial_subsection
        paragraph = initial_paragraph

        if article is None:
            art_match = re.search(
                r"\b(?:Article|Artikel|Art[íi]culo|Articolo|Artykuł|Artigo|art\.)\s*(\d+(?:er|e|\.º|º)?(?:[\.\-]\d+)*[a-zA-Z]?)",
                excerpt,
                re.IGNORECASE,
            )
            if art_match:
                article = art_match.group(0).strip()

        if subsection is None:
            sub_patterns = self._SUBSECTION_PATTERNS.get(lang, []) + self._SUBSECTION_PATTERNS["default"]
            for pat in sub_patterns:
                m = pat.search(excerpt)
                if m:
                    subsection = m.group(1).strip()
                    break

        if paragraph is None:
            para_patterns = self._PARAGRAPH_PATTERNS.get(lang, []) + self._PARAGRAPH_PATTERNS["default"]
            for pat in para_patterns:
                m = pat.search(excerpt)
                if m:
                    candidate = m.group(1).strip()
                    if candidate != subsection:
                        paragraph = candidate
                        break

        return article, subsection, paragraph

    def extract_provisions(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        """
        Parses statutory/regulatory headings across languages (`en`, `fr`, `de`, `es`, `it`, `nl`, `pl`, `pt`, `sv`, etc.)
        and returns structured provision dictionaries containing:
        - `source_section`
        - `article`
        - `subsection`
        - `paragraph`
        - `text_start_offset`
        - `text_end_offset`
        - `exact_source_excerpt` (guaranteed `text[text_start_offset:text_end_offset] == exact_source_excerpt`)
        - `source_language`

        Note: If `text` is already normalized, offsets index directly into `text`. If callers pass
        normalized text produced by `normalize_text()`, `normalized_text[start:end] == exact_source_excerpt`
        holds identically.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        lang_code = (language or "en").lower().split("-")[0]

        # Build line span table over `text` so character offsets are 100% exact against `text`
        line_spans: List[Tuple[int, int, str]] = []
        cursor = 0
        for raw_line in text.splitlines(keepends=True):
            line_start = cursor
            line_end = cursor + len(raw_line)
            stripped_content = raw_line.rstrip("\r\n")
            line_spans.append((line_start, line_start + len(stripped_content), stripped_content))
            cursor = line_end

        heading_Anchors: List[Tuple[int, Dict[str, Optional[str]]]] = []
        for idx, (line_start, _line_end, line_str) in enumerate(line_spans):
            stripped_lead = line_str.lstrip(" ")
            lead_delta = len(line_str) - len(stripped_lead)
            matched = self._match_heading_line(stripped_lead, lang_code)
            if matched is not None:
                heading_Anchors.append((idx, {**matched, "_char_start": str(line_start + lead_delta)}))

        provisions: List[Dict[str, Any]] = []

        if not heading_Anchors:
            # Fallback: treat entire non-whitespace span as a single provision
            first_non_ws = len(text) - len(text.lstrip())
            last_non_ws = len(text.rstrip())
            excerpt = text[first_non_ws:last_non_ws]
            article, subsection, paragraph = self._refine_subunits(excerpt, lang_code, None, None, None)
            source_section = article or "Section 1"
            assert text[first_non_ws:last_non_ws] == excerpt
            return [
                ProvisionSegment(
                    source_section=source_section,
                    article=article,
                    subsection=subsection,
                    paragraph=paragraph,
                    text_start_offset=first_non_ws,
                    text_end_offset=last_non_ws,
                    exact_source_excerpt=excerpt,
                    source_language=lang_code,
                ).to_dict()
            ]

        for anchor_pos, (line_idx, meta) in enumerate(heading_Anchors):
            start_offset = int(meta["_char_start"] or line_spans[line_idx][0])
            if anchor_pos + 1 < len(heading_Anchors):
                next_line_idx = heading_Anchors[anchor_pos + 1][0]
                raw_end_offset = line_spans[next_line_idx][0]
            else:
                raw_end_offset = len(text)

            # Trim trailing whitespace/newlines from this provision slice while keeping exact offsets
            slice_candidate = text[start_offset:raw_end_offset]
            trimmed_slice = slice_candidate.rstrip()
            end_offset = start_offset + len(trimmed_slice)
            exact_excerpt = text[start_offset:end_offset]

            # Strict invariant check
            if text[start_offset:end_offset] != exact_excerpt:
                raise AssertionError("Offset invariant violated during provision extraction")

            article, subsection, paragraph = self._refine_subunits(
                exact_excerpt,
                lang_code,
                meta.get("article"),
                meta.get("subsection"),
                meta.get("paragraph"),
            )

            segment = ProvisionSegment(
                source_section=str(meta["source_section"]),
                article=article,
                subsection=subsection,
                paragraph=paragraph,
                text_start_offset=start_offset,
                text_end_offset=end_offset,
                exact_source_excerpt=exact_excerpt,
                source_language=lang_code,
            )
            provisions.append(segment.to_dict())

        return provisions

    def align_bilingual_or_translated_passages(
        self,
        original_text: str,
        original_lang: str,
        translated_text: str,
        translated_lang: str = "en",
        verified_translation: bool = False,
        official_bilingual_coauthoritative: bool = False,
    ) -> Dict[str, Any]:
        """
        Preserves original-language passages, links translations to exact source sections and
        character offsets, and sets `translation_status` strictly according to Section 4.3 & RD-08:
        - `"official_bilingual_coauthoritative"`: when `official_bilingual_coauthoritative=True`
          (e.g., Canada Federal Acts / PIPEDA EN+FR or EU EUR-Lex co-authoritative official languages).
        - `"verified_translation"`: when `verified_translation=True` (counsel-verified or official regulator translation).
        - `"unverified_machine_translation"`: default whenever a translation is not explicitly verified
          or co-authoritative. Never assumes an unverified English translation is legally authoritative!
        """
        orig_lang_norm = (original_lang or "en").lower().split("-")[0]
        trans_lang_norm = (translated_lang or "en").lower().split("-")[0]

        orig_norm_res = self.normalize_document(original_text)
        trans_norm_res = self.normalize_document(translated_text)

        orig_provisions = self.extract_provisions(orig_norm_res.normalized_text, language=orig_lang_norm)
        trans_provisions = self.extract_provisions(trans_norm_res.normalized_text, language=trans_lang_norm)

        if official_bilingual_coauthoritative:
            translation_status = "official_bilingual_coauthoritative"
            is_authoritative = True
            requires_review = False
        elif verified_translation:
            translation_status = "verified_translation"
            is_authoritative = False  # Original text remains primary legal authority; translation is verified reference
            requires_review = False
        else:
            translation_status = "unverified_machine_translation"
            is_authoritative = False
            requires_review = True

        original_passages_map: Dict[str, str] = {}
        translated_passages_map: Dict[str, str] = {}
        aligned_provisions: List[Dict[str, Any]] = []

        max_len = max(len(orig_provisions), len(trans_provisions))
        for idx in range(max_len):
            orig_prov = orig_provisions[idx] if idx < len(orig_provisions) else None
            trans_prov = trans_provisions[idx] if idx < len(trans_provisions) else None

            section_key = (
                orig_prov["source_section"]
                if orig_prov is not None
                else (trans_prov["source_section"] if trans_prov is not None else f"passage_{idx + 1}")
            )

            if orig_prov is not None:
                original_passages_map[section_key] = orig_prov["exact_source_excerpt"]
            if trans_prov is not None:
                translated_passages_map[section_key] = trans_prov["exact_source_excerpt"]

            aligned_provisions.append(
                {
                    "alignment_index": idx,
                    "section_key": section_key,
                    "original_language": orig_lang_norm,
                    "translated_language": trans_lang_norm,
                    "translation_status": translation_status,
                    "authoritative_source_is_original": True,
                    "is_translation_legally_authoritative": is_authoritative,
                    "requires_legal_review": requires_review,
                    "original_provision": orig_prov,
                    "translated_provision": trans_prov,
                }
            )

        result = TranslationAlignmentResult(
            original_lang=orig_lang_norm,
            translated_lang=trans_lang_norm,
            translation_status=translation_status,
            is_translation_authoritative=is_authoritative,
            requires_legal_review_for_translation=requires_review,
            raw_original_sha256=orig_norm_res.raw_document_sha256,
            normalized_original_sha256=orig_norm_res.normalized_text_sha256,
            raw_translated_sha256=trans_norm_res.raw_document_sha256,
            normalized_translated_sha256=trans_norm_res.normalized_text_sha256,
            original_normalized_text=orig_norm_res.normalized_text,
            translated_normalized_text=trans_norm_res.normalized_text,
            original_language_passages=original_passages_map,
            translated_passages=translated_passages_map,
            aligned_provisions=aligned_provisions,
        )
        return result.to_dict()
