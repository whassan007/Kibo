"""
Statutory & Judicial Legal Annotation Engine (G17, G18).
"""

from .statute_annotator import StatutoryProvisionAnnotator
from .decision_annotator import JudicialAndEnforcementAnnotator

__all__ = [
    "StatutoryProvisionAnnotator",
    "JudicialAndEnforcementAnnotator",
]
