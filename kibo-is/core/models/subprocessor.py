"""
MODULE 5 – Vendor Risk Management
SubprocessorRegistry and DataTransfer models for tracking nested vendor relationships.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str


class SubprocessorRegistry(VersionedEntity, TenantScoped):
    """Registry entry linking a sub-processor to a primary vendor."""
    __tablename__ = 'subprocessor_registry'

    vendor_id = Column(String, ForeignKey('assets.id'), nullable=False, index=True)
    subprocessor_name = Column(String, nullable=False)
    subprocessor_service = Column(String)                # Description of service provided
    country_of_processing = Column(String)               # ISO 3166-1 alpha-2
    data_categories_processed = Column(JSON, default=list)  # e.g. [PersonalInfo, Payment]

    # Risk
    risk_rating = Column(String, default='medium')        # low, medium, high, critical
    last_assessed_at = Column(DateTime, nullable=True)

    # DPA link
    dpa_in_place = Column(Boolean, default=False)
    dpa_reference = Column(String, nullable=True)         # Reference to DPA document

    # Status
    status = Column(String, default='active')             # active, inactive, terminated
    onboarded_at = Column(DateTime, default=datetime.utcnow)
    terminated_at = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    vendor = relationship('Vendor', foreign_keys=[vendor_id])
    data_transfers = relationship('DataTransfer', back_populates='subprocessor_entry',
                                  cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_subprocessor_registry_vendor', 'vendor_id', 'status'),
    )


class DataTransfer(VersionedEntity, TenantScoped):
    """Records individual data transfers to/from a sub-processor."""
    __tablename__ = 'data_transfers'

    subprocessor_id = Column(String, ForeignKey('subprocessor_registry.id'),
                             nullable=False, index=True)
    transfer_mechanism = Column(String, nullable=False)   # SCC, BCR, adequacy_decision, derogation
    source_country = Column(String, nullable=False)
    destination_country = Column(String, nullable=False)

    # Transfer metadata
    data_categories = Column(JSON, default=list)
    transfer_frequency = Column(String)                   # continuous, daily, weekly, ad_hoc
    transfer_volume = Column(String, nullable=True)       # Estimated data volume

    # Safeguards
    safeguard_type = Column(String, nullable=True)        # encryption, pseudonymisation, etc.
    safeguard_details = Column(Text, nullable=True)

    # Compliance
    adequacy_decision = Column(Boolean, nullable=True)
    scc_version = Column(String, nullable=True)           # 2021 EU SCCs version
    bcr_reference = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    subprocessor_entry = relationship('SubprocessorRegistry', back_populates='data_transfers')

    __table_args__ = (
        Index('ix_data_transfers_subprocessor', 'subprocessor_id', 'is_active'),
    )
