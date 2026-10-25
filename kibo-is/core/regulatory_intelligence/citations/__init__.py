"""
KIBO Privacy OS — Deterministic Citation Verification Package (Worker G19)
Exports `CitationVerificationService`, `FABRICATED_NEGATIVE_TEST_FIXTURES`,
and `build_default_canonical_corpus`.
"""

from .verifier import (
    CitationVerificationService,
    FABRICATED_NEGATIVE_TEST_FIXTURES,
    build_default_canonical_corpus,
)

__all__ = [
    "CitationVerificationService",
    "FABRICATED_NEGATIVE_TEST_FIXTURES",
    "build_default_canonical_corpus",
]
