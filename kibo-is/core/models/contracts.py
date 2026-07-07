from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.models.base import Base, VersionedEntity, TenantScoped

class Jurisdiction(Base):
    __tablename__ = 'jurisdictions'
    
    id = Column(String, primary_key=True)  # e.g. "Quebec", "EU", "California"
    name = Column(String, nullable=False)
    primary_statute = Column(String, nullable=True)
    access_request_deadline_days = Column(Integer, nullable=True)

class Contract(VersionedEntity, TenantScoped):
    __tablename__ = 'contracts'
    
    vendor_id = Column(String, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    contract_type = Column(String, nullable=True)  # DPA, SCC, Service Agreement
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    has_dpa = Column(Boolean, default=False)
    has_scc = Column(Boolean, default=False)
    cross_border_transfer = Column(Boolean, default=False)
    
    # Relationships
    vendor = relationship('Vendor', back_populates='contracts', foreign_keys=[vendor_id])
