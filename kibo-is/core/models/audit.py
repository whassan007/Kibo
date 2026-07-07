from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, ForeignKey, Index
from core.models.base import Base, Timestamped, generate_uuid_str

class AccessLog(Base, Timestamped):
    __tablename__ = 'access_logs'
    
    id = Column(String, primary_key=True, default=generate_uuid_str)
    tenant_id = Column(String, ForeignKey('tenants.id', ondelete='SET NULL'), nullable=True)
    user_id = Column(String, nullable=True)
    
    method = Column(String, nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    __table_args__ = (
        Index('ix_access_logs_tenant_created', 'tenant_id', 'created_at'),
    )
