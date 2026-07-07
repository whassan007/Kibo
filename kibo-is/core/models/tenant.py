from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from core.models.base import Base, VersionedEntity, Timestamped, generate_uuid_str

class Tenant(VersionedEntity, Timestamped):
    __tablename__ = 'tenants'
    
    id = Column(String, primary_key=True)  # slug: "acme-corp"
    name = Column(String, unique=True, nullable=False)  # "ACME Corporation"
    industry = Column(String, nullable=True)  # healthcare, finance, ngo, etc.
    size = Column(String, nullable=True)  # small, medium, large, enterprise
    primary_jurisdiction = Column(String, nullable=True)  # Ontario, Quebec, California, EU
    
    # Subscription
    subscription_tier = Column(String, nullable=True)  # free, starter, pro, enterprise
    features_enabled = Column(JSON, default={}, nullable=False)  # {vendor_risk: true, dsar: false, ...}
    max_users = Column(Integer, default=10, nullable=False)
    max_assessments_per_month = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_suspended = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    memberships = relationship('TenantMembership', back_populates='tenant', cascade='all, delete-orphan')
    settings = relationship('TenantSettings', back_populates='tenant', uselist=False, cascade='all, delete-orphan')

class TenantMembership(VersionedEntity):
    __tablename__ = 'tenant_memberships'
    
    tenant_id = Column(String, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, dpo, analyst, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    tenant = relationship('Tenant', back_populates='memberships')

class TenantSettings(VersionedEntity):
    __tablename__ = 'tenant_settings'
    
    tenant_id = Column(String, ForeignKey('tenants.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Compliance settings
    require_dpo_approval = Column(Boolean, default=True, nullable=False)
    assessment_timeout_days = Column(Integer, default=30, nullable=False)
    breach_notification_deadline_hours = Column(Integer, default=72, nullable=False)
    
    # Data retention
    assessment_archive_years = Column(Integer, default=7, nullable=False)
    audit_log_retention_years = Column(Integer, default=7, nullable=False)
    
    # Integration
    webhook_url = Column(String, nullable=True)
    sso_provider = Column(String, nullable=True)  # okta, azure, google
    
    tenant = relationship('Tenant', back_populates='settings')
