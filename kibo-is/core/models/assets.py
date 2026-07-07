from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped
from core.models.associations import system_control, process_data_element, process_control

class Asset(VersionedEntity, TenantScoped):
    __tablename__ = 'assets'
    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': 'asset_type'
    }
    asset_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(String, nullable=True)
    
    # Common fields moved to base to avoid STI column conflicts
    data_categories = Column(JSON, nullable=True)
    jurisdiction = Column(String, nullable=True)

class System(Asset):
    __mapper_args__ = {'polymorphic_identity': 'system'}
    processing_activities = Column(JSON, nullable=True)
    risk_classification = Column(String, nullable=True)
    storage_location = Column(String, nullable=True)
    encryption_method = Column(String, nullable=True)
    
    # Relationships
    data_elements = relationship('DataElement', back_populates='system', cascade='all, delete-orphan', foreign_keys='DataElement.system_id')
    assessments = relationship('Assessment', back_populates='system', foreign_keys='Assessment.assessed_system_id')
    risks = relationship('Risk', back_populates='sourced_from_system', foreign_keys='Risk.sourced_from_system_id')
    implemented_controls = relationship('Control', secondary=system_control, back_populates='implemented_in_systems')

class Vendor(Asset):
    __mapper_args__ = {'polymorphic_identity': 'vendor'}
    service_description = Column(String, nullable=True)
    country_of_origin = Column(String, nullable=True)
    dpa_status = Column(String, nullable=True)  # none, draft, executed, expired
    dpa_expiry_date = Column(String, nullable=True)
    soc2_type = Column(String, nullable=True)  # none, type_i, type_ii
    cross_border = Column(Boolean, default=False)
    
    # Relationships
    contracts = relationship('Contract', back_populates='vendor', cascade='all, delete-orphan')
    assessments = relationship('Assessment', back_populates='linked_vendor', foreign_keys='Assessment.linked_vendor_id')
    risks = relationship('Risk', back_populates='sourced_from_vendor', foreign_keys='Risk.sourced_from_vendor_id')

class DataElement(Asset):
    __mapper_args__ = {'polymorphic_identity': 'data_element'}
    data_category = Column(String, nullable=True)
    sensitivity = Column(String, nullable=True)  # public, internal, confidential, restricted
    retention_days = Column(Integer, nullable=True)
    system_id = Column(String, ForeignKey('assets.id', ondelete='CASCADE'), nullable=True)
    
    # Relationships
    system = relationship('System', back_populates='data_elements', foreign_keys=[system_id], remote_side='System.id')

class Process(Asset):
    __mapper_args__ = {'polymorphic_identity': 'process'}
    process_type = Column(String, nullable=True)  # collection, transfer, profiling, ai_training
    legal_basis = Column(String, nullable=True)
    activities = Column(JSON, nullable=True)
    involves_children = Column(Boolean, default=False)
    child_age_minimum = Column(Integer, nullable=True)
    
    # Relationships
    data_elements = relationship(
        'DataElement',
        secondary=process_data_element,
        primaryjoin="Process.id == process_data_element.c.process_id",
        secondaryjoin="DataElement.id == process_data_element.c.data_element_id"
    )
    assessments = relationship('Assessment', back_populates='assesses_process', foreign_keys='Assessment.assesses_process_id')
    generated_risks = relationship('Risk', back_populates='sourced_from_process', foreign_keys='Risk.sourced_from_process_id')
    controls = relationship('Control', secondary=process_control)
