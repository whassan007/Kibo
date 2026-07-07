from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Any

@dataclass
class DomainEvent:
    """Base class for all domain events"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    tenant_id: str = "default"
    aggregate_id: Optional[str] = None
    aggregate_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__

# Assessment Events
@dataclass
class AssessmentCreated(DomainEvent):
    title: str = ""
    assessment_type: str = "PIA"  # PIA, DPIA, TIA
    status: str = 'draft'

@dataclass
class AssessmentSubmitted(DomainEvent):
    submitted_by: str = ""
    legal_basis: str = ""

@dataclass
class AssessmentApproved(DomainEvent):
    approved_by: str = ""
    risk_score: float = 0.0
    findings: str = ""
    mitigations: List[str] = field(default_factory=list)

@dataclass
class AssessmentRejected(DomainEvent):
    rejected_by: str = ""
    rejection_reason: str = ""

# Risk Events
@dataclass
class RiskCreated(DomainEvent):
    title: str = ""
    severity: str = "low"  # low, medium, high, critical
    source_assessment_id: Optional[str] = None
    risk_score: float = 0.0
    mitigation_required: bool = False

@dataclass
class RiskStatusChanged(DomainEvent):
    new_status: str = "open"  # open, mitigated, accepted
    old_status: str = "open"
    reason: Optional[str] = None

@dataclass
class RiskAccepted(DomainEvent):
    accepted_by: str = ""
    acceptance_date: datetime = field(default_factory=datetime.utcnow)
    justification: str = ""

# Control Events
@dataclass
class ControlImplemented(DomainEvent):
    control_id: Optional[str] = None
    implementation_date: datetime = field(default_factory=datetime.utcnow)
    implemented_in_systems: List[str] = field(default_factory=list)

@dataclass
class ControlTested(DomainEvent):
    test_date: datetime = field(default_factory=datetime.utcnow)
    test_result: str = "effective"  # effective, partially_effective, ineffective
    evidence: str = ""

# Vendor Events
@dataclass
class VendorAssessed(DomainEvent):
    vendor_id: Optional[str] = None
    assessment_type: str = "security"
    risk_level: str = "low"

@dataclass
class VendorDPAExpiring(DomainEvent):
    vendor_id: Optional[str] = None
    days_until_expiry: int = 30
    expiry_date: datetime = field(default_factory=datetime.utcnow)

# System Events
@dataclass
class SystemReclassified(DomainEvent):
    system_id: Optional[str] = None
    old_classification: str = "low"
    new_classification: str = "high"

@dataclass
class DataFlowChanged(DomainEvent):
    source_system: Optional[str] = None
    destination_system: Optional[str] = None
    data_categories: List[str] = field(default_factory=list)

# Regulation Events
@dataclass
class RegulationUpdated(DomainEvent):
    regulation_name: str = ""
    effective_date: datetime = field(default_factory=datetime.utcnow)
    impact_summary: str = ""

# Compliance Events
@dataclass
class ComplianceGapIdentified(DomainEvent):
    gap_description: str = ""
    affected_systems: List[str] = field(default_factory=list)
    affected_processes: List[str] = field(default_factory=list)
    remediation_priority: str = "low"


# ── MODULE 5: Vendor Risk Events ──────────────────────────────────────────────

@dataclass
class DPAApproved(DomainEvent):
    """Emitted when a Data Processing Agreement is approved / executed."""
    vendor_id: Optional[str] = None
    dpa_id: Optional[str] = None
    approved_by: str = ""


@dataclass
class DPAExpired(DomainEvent):
    """Emitted when a DPA passes its expiry date without renewal."""
    vendor_id: Optional[str] = None
    dpa_id: Optional[str] = None
    expired_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VendorOnboarded(DomainEvent):
    """Emitted when a vendor completes the onboarding workflow."""
    vendor_id: Optional[str] = None
    approval_status: str = "approved"     # approved, conditional, blocked


# ── MODULE 6: DSAR Events ─────────────────────────────────────────────────────

@dataclass
class DsarReceived(DomainEvent):
    """Emitted when a new DSAR is registered."""
    request_type: str = "access"          # access, deletion, portability, object
    jurisdiction: str = "GDPR"
    deadline: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DsarStatusChanged(DomainEvent):
    """Emitted whenever a DSAR status transitions."""
    old_status: str = ""
    new_status: str = ""
    changed_by: Optional[str] = None


@dataclass
class DsarDeadlineApproaching(DomainEvent):
    """Emitted when a DSAR is within the alert window before its deadline."""
    days_remaining: int = 5
    deadline: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DsarDelivered(DomainEvent):
    """Emitted when a DSAR package has been successfully delivered."""
    delivery_method: str = "email"
    package_id: Optional[str] = None
    delivered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DsarRefused(DomainEvent):
    """Emitted when a DSAR is refused with documented justification."""
    refuse_reason: str = ""
    refused_by: Optional[str] = None

