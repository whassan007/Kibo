from sqlalchemy import Column, String, Date, Boolean, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped
import enum

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

class Vendor(VersionedEntity, TenantScoped):
    __tablename__ = "vendors"
    name = Column(String, nullable=False)
    service = Column(String, nullable=False)
    risk_rating = Column(Enum(RiskRating), nullable=False)
    dpa_status = Column(Enum(DPAStatus), nullable=False, default=DPAStatus.none)
    dpa_expiration_date = Column(Date, nullable=True)
    sccs_in_place = Column(Boolean, default=False)
    soc2_type = Column(Enum(SOC2Type), default=SOC2Type.none)
    cross_border = Column(Boolean, default=False)
    status = Column(String, nullable=False, default="active")
    next_review_date = Column(Date, nullable=True)

    assessments = relationship("VendorAssessment", back_populates="vendor", cascade="all, delete-orphan")
    risks = relationship("VendorRisk", back_populates="vendor", cascade="all, delete-orphan")
    subprocessors = relationship("Subprocessor", back_populates="vendor", cascade="all, delete-orphan")

class VendorAssessment(VersionedEntity, TenantScoped):
    __tablename__ = "vendor_assessments"
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    score = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    vendor = relationship("Vendor", back_populates="assessments")

class VendorDPA(VersionedEntity, TenantScoped):
    __tablename__ = "vendor_dpas"
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    agreement_url = Column(String, nullable=False)
    signed_at = Column(Date, nullable=True)
    vendor = relationship("Vendor", back_populates="assessments")  # reuse relationship for simplicity

class VendorEvidence(VersionedEntity, TenantScoped):
    __tablename__ = "vendor_evidence"
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    evidence_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    vendor = relationship("Vendor", back_populates="assessments")

class Subprocessor(VersionedEntity, TenantScoped):
    __tablename__ = "subprocessors"
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=False)
    name = Column(String, nullable=False)
    service = Column(String, nullable=False)
    risk_rating = Column(Enum(RiskRating), nullable=False)
    vendor = relationship("Vendor", back_populates="subprocessors")
