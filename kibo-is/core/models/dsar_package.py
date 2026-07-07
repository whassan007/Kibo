"""
MODULE 6 – DSAR Workflows
Delivery package models: DeliveryPackage and PackageVerification.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Float, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str


class DeliveryPackage(VersionedEntity, TenantScoped):
    """The assembled, signed data package ready for delivery to the data subject."""
    __tablename__ = 'delivery_packages'

    request_id = Column(String, ForeignKey('dsar_requests.id'), unique=True, nullable=False)

    # Package contents
    package_format = Column(String, default='zip')       # zip, pdf, json, csv
    file_path = Column(String, nullable=True)            # Server-side path
    file_hash = Column(String, nullable=True)            # SHA256 checksum
    file_size_bytes = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)        # Total records included
    data_categories_included = Column(JSON, default=list)

    # Redaction metadata
    redactions_applied = Column(Integer, default=0)
    fully_redacted_categories = Column(JSON, default=list)  # Categories fully excluded

    # Signing & integrity
    is_signed = Column(Boolean, default=False)
    digital_signature = Column(Text, nullable=True)      # Base64 encoded signature
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(String, nullable=True)

    # Status
    status = Column(String, default='preparing')         # preparing, ready, delivered, expired
    prepared_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)         # Download link expiry

    # Delivery details
    delivery_method = Column(String, nullable=True)      # email, download, mail
    delivery_address = Column(String, nullable=True)     # Email / mailing address
    delivered_at = Column(DateTime, nullable=True)
    download_token = Column(String, nullable=True)       # Secure one-time download token
    download_token_expires_at = Column(DateTime, nullable=True)

    # Relationships
    request = relationship('DataSubjectAccessRequest', back_populates='package')
    verifications = relationship('PackageVerification', back_populates='package',
                                 cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_delivery_packages_status', 'status'),
    )


class PackageVerification(VersionedEntity, TenantScoped):
    """Checklist of verification steps passed before package is marked 'ready'."""
    __tablename__ = 'package_verifications'

    package_id = Column(String, ForeignKey('delivery_packages.id'), nullable=False, index=True)

    check_name = Column(String, nullable=False)     # completeness, redaction_applied, hash_verified, etc.
    check_passed = Column(Boolean, default=False)
    check_detail = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    checked_by = Column(String, nullable=True)       # user_id or 'system'

    package = relationship('DeliveryPackage', back_populates='verifications')
