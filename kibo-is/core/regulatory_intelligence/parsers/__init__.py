"""
KIBO Privacy OS — Multilingual Document Parsing and Normalization Package (G16)
Provides deterministic Unicode normalization, multilingual provision segmentation,
exact character offset extraction, and authoritative bilingual/translated passage alignment.
"""

from .multilingual_parser import (
    MultilingualLegalParser,
    NormalizedDocumentResult,
    ProvisionSegment,
    TranslationAlignmentResult,
)

__all__ = [
    "MultilingualLegalParser",
    "NormalizedDocumentResult",
    "ProvisionSegment",
    "TranslationAlignmentResult",
]
