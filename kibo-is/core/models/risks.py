from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped
from core.models.associations import risk_control, risk_jurisdiction

class Risk(VersionedEntity, TenantScoped):
    __tablename__ = 'risks'
    
    # Map to legacy table risk_id with default UUID generator
    id = Column('risk_id', String, primary_key=True, default=lambda: str(uuid4()))
    
    title = Column('issue', String, nullable=False)
    description = Column('recommendation', Text, nullable=True)
    severity = Column('risk_level', String, nullable=True)  # low, medium, high, critical
    probability = Column('likelihood', String, nullable=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    residual_risk_score = Column(Float, nullable=True)
    status = Column(String, default='open', nullable=False)  # open, mitigated, accepted, rejected
    risk_owner = Column('assigned_to', String, nullable=True)
    accepts_risk = Column(String, nullable=True)
    risk_acceptance_date = Column(DateTime, nullable=True)
    risk_acceptance_justification = Column(Text, nullable=True)
    mitigation_deadline = Column(DateTime, nullable=True)
    
    # FKs
    source_assessment_id = Column(String, ForeignKey('assessments.id', ondelete='SET NULL'), nullable=True)
    sourced_from_system_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    sourced_from_vendor_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    sourced_from_process_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    source_assessment = relationship('Assessment', back_populates='risks', foreign_keys=[source_assessment_id])
    sourced_from_system = relationship('System', back_populates='risks', foreign_keys=[sourced_from_system_id])
    sourced_from_vendor = relationship('Vendor', back_populates='risks', foreign_keys=[sourced_from_vendor_id])
    sourced_from_process = relationship('Process', back_populates='generated_risks', foreign_keys=[sourced_from_process_id])
    
    mitigations = relationship('Control', secondary=risk_control, back_populates='mitigates_risks')
    affects_jurisdictions = relationship('Jurisdiction', secondary=risk_jurisdiction)
