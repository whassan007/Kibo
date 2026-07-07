"""
MODULE 6 – DSAR Workflows
Data collection models: CollectionTask and CollectedDataElement.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str


class CollectionTask(VersionedEntity, TenantScoped):
    """A discrete collection task targeting a specific system for a DSAR."""
    __tablename__ = 'collection_tasks'

    request_id = Column(String, ForeignKey('dsar_requests.id'), nullable=False, index=True)
    system_id = Column(String, nullable=False)
    system_name = Column(String, nullable=True)
    data_category = Column(String, nullable=False)

    status = Column(String, default='pending')   # pending, in_progress, completed, failed, skipped
    collection_method = Column(String)            # database_query, api_export, manual, file_export
    query_template = Column(Text, nullable=True)  # SQL or API query used

    # Results
    records_found = Column(Integer, nullable=True)
    data_size_mb = Column(Float, nullable=True)
    collection_output = Column(JSON, nullable=True)   # Collected data (structured)

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    assigned_to = Column(String, nullable=True)

    error_message = Column(Text, nullable=True)       # If status=failed

    request = relationship('DataSubjectAccessRequest', foreign_keys=[request_id])

    __table_args__ = (
        Index('ix_collection_tasks_request_status', 'request_id', 'status'),
    )
