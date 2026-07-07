"""
MODULE 6 – DSAR Workflows
Full DSAR request entities: DataSubject, DataSubjectAccessRequest, DsarScope, RequestedDataElement.
Replaces the minimal dsar_request.py stub.
"""

from datetime import datetime
from sqlalchemy import (Column, String, DateTime, JSON, Boolean, Text,
                        ForeignKey, Integer, Float, Index)
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str

# ─── Jurisdiction deadline constants (days) ───────────────────────────────────
JURISDICTION_DEADLINES: dict[str, int] = {
    'GDPR':    30,
    'CCPA':    45,
    'PIPEDA':  30,
    'Law25':   45,
    'UK_GDPR': 30,
    'LGPD':    30,
    'PDPL':    30,   # Saudi Arabia
}


class DataSubject(VersionedEntity, TenantScoped):
    """Represents a data subject (person) who filed a DSAR."""
    __tablename__ = 'data_subjects'

    # Identification
    identifier_type = Column(String, nullable=False)    # email, user_id, phone, full_name
    identifier_value = Column(String, nullable=False)

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String, nullable=True)  # none, email, phone, government_id
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String, nullable=True)

    # Representation (for authorised agents)
    is_represented = Column(Boolean, default=False)
    representative_name = Column(String, nullable=True)
    representative_authorization = Column(String, nullable=True)  # Document path

    # Relationships
    requests = relationship('DataSubjectAccessRequest', back_populates='data_subject',
                            cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_data_subjects_tenant_id_type', 'tenant_id', 'identifier_type', 'identifier_value'),
    )


class DataSubjectAccessRequest(VersionedEntity, TenantScoped):
    """Core DSAR record – covers the full lifecycle from receipt to delivery."""
    __tablename__ = 'dsar_requests'

    # Subject link
    data_subject_id = Column(String, ForeignKey('data_subjects.id'), nullable=False, index=True)

    # Request details
    request_type = Column(String, nullable=False)   # access, deletion, portability, rectification, object
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    received_via = Column(String, nullable=True)    # email, web_form, phone, mail, other

    # Jurisdiction & deadline
    jurisdiction = Column(String, nullable=False)           # GDPR, CCPA, PIPEDA, Law25 …
    deadline = Column(DateTime, nullable=False)             # Auto-calculated from received_at + jurisdiction days
    days_remaining = Column(Integer, nullable=True)         # Recalculated by a scheduler

    # Status
    status = Column(String, default='received')
    # Allowed: received, pending_verification, scoping, collecting, redacting, ready, delivered, refused

    # Refusal (optional)
    refuse_reason = Column(String, nullable=True)           # frivolous, excessive, already_provided, no_data
    refuse_justification = Column(Text, nullable=True)

    # Requestor contact
    requestor_email = Column(String, nullable=False)
    requestor_phone = Column(String, nullable=True)
    preferred_delivery = Column(String, default='email')    # email, download, mail

    # Assignment & timing
    assigned_to = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    data_subject = relationship('DataSubject', back_populates='requests')
    scope = relationship('DsarScope', uselist=False, back_populates='request',
                         cascade='all, delete-orphan')
    data_elements = relationship('RequestedDataElement', back_populates='request',
                                 cascade='all, delete-orphan')
    package = relationship('DeliveryPackage', uselist=False, back_populates='request',
                           cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_dsar_requests_deadline', 'deadline'),
        Index('ix_dsar_requests_status', 'status'),
        Index('ix_dsar_requests_data_subject', 'data_subject_id'),
    )


class DsarScope(VersionedEntity, TenantScoped):
    """Defines which systems and data categories are in scope for a DSAR."""
    __tablename__ = 'dsar_scope'

    request_id = Column(String, ForeignKey('dsar_requests.id'), unique=True, nullable=False)

    # Systems and categories in scope
    systems_in_scope = Column(JSON, default=list)          # [system_ids]
    data_categories = Column(JSON, default=list)           # [PersonalInfo, PaymentInfo, …]

    # Optional time range from the request
    from_date = Column(DateTime, nullable=True)
    to_date = Column(DateTime, nullable=True)

    # Size estimates
    estimated_data_size_mb = Column(Float, nullable=True)
    estimated_record_count = Column(Integer, nullable=True)

    # Who determined scope
    scope_determined_at = Column(DateTime, nullable=True)
    scope_determined_by = Column(String, nullable=True)

    request = relationship('DataSubjectAccessRequest', back_populates='scope')


class RequestedDataElement(VersionedEntity, TenantScoped):
    """Granular tracking of each piece of data to be collected/delivered."""
    __tablename__ = 'requested_data_elements'

    request_id = Column(String, ForeignKey('dsar_requests.id'), nullable=False, index=True)

    # What data
    system_id = Column(String, nullable=False)
    data_category = Column(String, nullable=False)   # PersonalInfo, PaymentInfo, …
    field_name = Column(String, nullable=True)        # email, phone, all

    # Collection
    status = Column(String, default='pending')        # pending, collecting, collected, redacted, included, excluded
    collection_method = Column(String, nullable=True) # database_query, export, manual, api

    # Results
    actual_record_count = Column(Integer, nullable=True)
    actual_data_size_mb = Column(Float, nullable=True)

    collected_at = Column(DateTime, nullable=True)
    collected_by = Column(String, nullable=True)

    request = relationship('DataSubjectAccessRequest', back_populates='data_elements')

    __table_args__ = (
        Index('ix_requested_data_elements_request', 'request_id', 'status'),
    )
