import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Index
from core.models.base import Base, Timestamped

def generate_uuid_str():
    return str(uuid.uuid4())

class AuditLog(Base, Timestamped):
    """Immutable audit log of all changes (append-only)"""
    __tablename__ = 'audit_logs'
    
    id = Column(String, primary_key=True, default=generate_uuid_str)
    tenant_id = Column(String, nullable=False)
    
    # Who made the change
    user_id = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_role = Column(String, nullable=True)
    
    # What changed
    action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, REJECT
    entity_type = Column(String, nullable=False)  # Assessment, Risk, Control, etc.
    entity_id = Column(String, nullable=False)
    
    # Before -> After
    previous_state = Column(JSON, nullable=True)  # Full state before change
    new_state = Column(JSON, nullable=True)  # Full state after change
    changes = Column(JSON, nullable=True)  # {field: {old: value, new: value}, ...}
    
    # Why did this happen
    reason = Column(Text, nullable=True)  # User-provided reason for change
    change_context = Column(JSON, nullable=True)  # {triggered_by: event, ...}
    
    # Request context
    request_id = Column(String, nullable=True)  # Correlation ID
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Integrity
    change_hash = Column(String, nullable=True)  # SHA256 of this record
    previous_hash = Column(String, nullable=True)  # SHA256 of previous record (chain)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_audit_tenant_created', 'tenant_id', 'created_at'),
        Index('ix_audit_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_user_date', 'user_id', 'created_at'),
        Index('ix_audit_action', 'action'),
    )

class EntityVersion(Base):
    """Temporal versioning - complete snapshots of entities over time"""
    __tablename__ = 'entity_versions'
    
    id = Column(String, primary_key=True, default=generate_uuid_str)
    tenant_id = Column(String, nullable=False)
    
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    version = Column(Integer, nullable=False)  # 1, 2, 3, ...
    
    # Complete snapshot of entity at this version
    snapshot = Column(JSON, nullable=False)  # Full entity state
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_entity_versions_id_entity', 'entity_type', 'entity_id', 'version'),
        Index('ix_entity_versions_tenant_created', 'tenant_id', 'created_at'),
    )

class DataAccessLog(Base, Timestamped):
    """Log of who accessed what data"""
    __tablename__ = 'data_access_logs'
    
    id = Column(String, primary_key=True, default=generate_uuid_str)
    tenant_id = Column(String, nullable=False)
    
    # Who accessed
    user_id = Column(String, nullable=False)
    user_email = Column(String, nullable=True)
    
    # What was accessed
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String, nullable=True)  # READ, DOWNLOAD, EXPORT
    
    # How much data
    record_count = Column(Integer, nullable=True)
    data_size_bytes = Column(Integer, nullable=True)
    
    # Why
    access_reason = Column(String, nullable=True)  # compliance_audit, routine_review, etc.
    justification = Column(Text, nullable=True)
    
    # Request context
    ip_address = Column(String, nullable=True)
    endpoint = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_data_access_tenant_user', 'tenant_id', 'user_id'),
        Index('ix_data_access_entity', 'entity_type', 'entity_id'),
    )
