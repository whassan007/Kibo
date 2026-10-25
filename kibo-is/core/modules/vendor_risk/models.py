import enum
from core.models.assets import Vendor
from core.models.vendor_assessment import VendorRiskAssessment as VendorAssessment, AssessmentEvidence as VendorEvidence
from core.models.vendor_dpa import DataProcessingAgreement as VendorDPA
from core.models.subprocessor import SubprocessorRegistry as Subprocessor

class RiskRating(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class DPAStatus(enum.Enum):
    none = "none"
    draft = "draft"
    executed = "executed"
    expired = "expired"

class SOC2Type(enum.Enum):
    none = "none"
    type_i = "type_i"
    type_ii = "type_ii"

__all__ = [
    "RiskRating",
    "DPAStatus",
    "SOC2Type",
    "Vendor",
    "VendorAssessment",
    "VendorDPA",
    "VendorEvidence",
    "Subprocessor",
]
