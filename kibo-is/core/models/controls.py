from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped
from core.models.associations import risk_control, system_control

class Control(VersionedEntity, TenantScoped):
    __tablename__ = 'controls'
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    control_type = Column(String, nullable=True)  # preventive, detective, corrective, compensating
    implementation_status = Column(String, default='planned', nullable=False)  # planned, in_progress, etc.
    effectiveness_rating = Column(String, default='not_assessed', nullable=False)  # not_assessed, effective, etc.
    control_owner = Column(String, nullable=True)
    test_results = Column(JSON, nullable=True)
    last_tested = Column(DateTime, nullable=True)
    
    # Relationships
    mitigates_risks = relationship('Risk', secondary=risk_control, back_populates='mitigations')
    implemented_in_systems = relationship('System', secondary=system_control, back_populates='implemented_controls')
