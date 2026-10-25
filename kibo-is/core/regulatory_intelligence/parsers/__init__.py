"""
Multilingual & Structural Legal Document Parsers (G16).
"""

from .multilingual_parser import (
    MultilingualLegalParser,
    SUPPORTED_EU_AND_GLOBAL_LANGUAGES,
    OFFICIAL_BILINGUAL_COAUTHORITATIVE_PAIRS,
)

__all__ = [
    "MultilingualLegalParser",
    "SUPPORTED_EU_AND_GLOBAL_LANGUAGES",
    "OFFICIAL_BILINGUAL_COAUTHORITATIVE_PAIRS",
]
