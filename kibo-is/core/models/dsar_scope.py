from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from core.models.base import Base, Timestamped
from datetime import datetime

class DataCategory(Base, Timestamped):
    __tablename__ = 'dsar_data_categories'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

class System(Base, Timestamped):
    __tablename__ = 'dsar_systems'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

class DSARScope(Base, Timestamped):
    __tablename__ = 'dsar_scopes'
    id = Column(String, primary_key=True)
    dsar_request_id = Column(String, ForeignKey('dsar_requests.id', ondelete='CASCADE'), nullable=False)
    # JSON list of data category IDs
    data_category_ids = Column(JSON, default=[])  # e.g., ["cat-1", "cat-2"]
    # JSON list of system IDs
    system_ids = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    dsar_request = relationship('DSARRequest', back_populates='scope')
