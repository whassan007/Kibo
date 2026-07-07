"""
MODULE 6 – DSAR Workflows
Redaction models: RedactionRule and AppliedRedaction.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str


class RedactionRule(VersionedEntity, TenantScoped):
    """Configurable rule that defines how a field type should be redacted."""
    __tablename__ = 'redaction_rules'

    name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)    # email_mask, phone_mask, ssn_mask, full_redact, custom_regex
    description = Column(Text, nullable=True)
    pattern = Column(String, nullable=True)       # Regex pattern (for custom_regex type)
    replacement = Column(String, nullable=True)   # Replacement string template
    applies_to_fields = Column(JSON, default=list)  # ['email', 'sender', 'recipient']
    applies_to_categories = Column(JSON, default=list)  # ['PersonalInfo', 'HealthData']
    is_active = Column(Boolean, default=True)
    priority = Column(String, default='normal')  # low, normal, high
    created_by = Column(String, nullable=True)

    applied_redactions = relationship('AppliedRedaction', back_populates='rule')


class AppliedRedaction(VersionedEntity, TenantScoped):
    """Audit record of a single redaction applied to a DSAR data element."""
    __tablename__ = 'applied_redactions'

    request_id = Column(String, ForeignKey('dsar_requests.id'), nullable=False, index=True)
    element_id = Column(String, ForeignKey('requested_data_elements.id'), nullable=True, index=True)
    rule_id = Column(String, ForeignKey('redaction_rules.id'), nullable=True)

    field_name = Column(String, nullable=False)
    original_value_hash = Column(String, nullable=True)   # SHA256 of original (never store plaintext)
    redacted_value = Column(Text, nullable=True)          # Redacted representation
    justification = Column(Text, nullable=True)           # Why this was redacted

    applied_at = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(String, nullable=True)

    rule = relationship('RedactionRule', back_populates='applied_redactions')

    __table_args__ = (
        Index('ix_applied_redactions_request', 'request_id'),
    )
