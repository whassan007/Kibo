from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def generate_uuid_str():
    return str(uuid.uuid4())

class Timestamped:
    """Mixin class for models with created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class VersionedEntity(Base):
    __abstract__ = True
    id = Column(String, primary_key=True, default=generate_uuid_str)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

class TenantScoped:
    tenant_id = Column(String, nullable=False, index=True)
