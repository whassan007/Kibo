from core.models.base import Base, VersionedEntity, TenantScoped, Timestamped
from core.models.assets import Asset, System, Vendor, DataElement, Process
from core.models.assessments import Assessment, PIAssessment, DPIAssessment, TIAssessment
from core.models.risks import Risk
from core.models.controls import Control
from core.models.contracts import Jurisdiction, Contract
from core.models.associations import risk_control, risk_jurisdiction, system_control, process_data_element, process_control
from core.models.audit_log import AuditLog, EntityVersion, DataAccessLog
from core.models.tenant import Tenant, TenantMembership, TenantSettings
from core.models.audit import AccessLog

# Phase 2 – Module 5: Vendor Risk
from core.models.vendor_assessment import VendorRiskAssessment, AssessmentResult, AssessmentEvidence
from core.models.vendor_dpa import DataProcessingAgreement, StandardContractualClause
from core.models.subprocessor import SubprocessorRegistry, DataTransfer

# Phase 2 – Module 6: DSAR Workflows
from core.models.dsar_request import DataSubject, DataSubjectAccessRequest, DsarScope, RequestedDataElement
from core.models.dsar_collection import CollectionTask
from core.models.dsar_redaction import RedactionRule, AppliedRedaction
from core.models.dsar_package import DeliveryPackage, PackageVerification
# NOTE: core/models/dsar_scope.py (legacy) and core/models/vendor_risk_assessment.py (legacy)
# are NOT imported here to avoid tablename collisions with Phase 1 + Phase 2 models.

