from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped

class Assessment(VersionedEntity, TenantScoped):
    __tablename__ = 'assessments'
    __mapper_args__ = {
        'polymorphic_identity': 'assessment',
        'polymorphic_on': 'assessment_type'
    }
    assessment_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default='draft', nullable=False)
    risk_score = Column(Float, nullable=True)
    legal_basis = Column(String, nullable=True)
    findings = Column(Text, nullable=True)
    mitigations = Column(JSON, nullable=True)  # List of recommendation maps
    assigned_to = Column(String, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)
    
    # FKs
    assesses_process_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    linked_vendor_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    assessed_system_id = Column(String, ForeignKey('assets.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    assesses_process = relationship('Process', back_populates='assessments', foreign_keys=[assesses_process_id])
    linked_vendor = relationship('Vendor', back_populates='assessments', foreign_keys=[linked_vendor_id])
    system = relationship('System', back_populates='assessments', foreign_keys=[assessed_system_id])
    
    risks = relationship('Risk', back_populates='source_assessment')

class PIAssessment(Assessment):
    __mapper_args__ = {'polymorphic_identity': 'pia'}
    child_population = Column(Boolean, default=False)

class DPIAssessment(Assessment):
    __mapper_args__ = {'polymorphic_identity': 'dpia'}
    cross_border_transfer = Column(Boolean, default=False)

class TIAssessment(Assessment):
    __mapper_args__ = {'polymorphic_identity': 'tia'}
    source_jurisdiction = Column(String, nullable=True)
    destination_jurisdiction = Column(String, nullable=True)
    transfer_mechanism = Column(String, nullable=True)
