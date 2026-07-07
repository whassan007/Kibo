from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str

class DataProcessingAgreement(VersionedEntity, TenantScoped):
    __tablename__ = 'data_processing_agreements'
    id = Column(String, primary_key=True, default=generate_uuid_str)
    vendor_id = Column(String, nullable=False)
    dpa_type = Column(String)  # Data Processing Agreement, Sub-processor Agreement
    status = Column(String)  # draft, pending_signature, executed, expired, terminated
    execution_date = Column(DateTime, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    renewal_date = Column(DateTime, nullable=True)
    agreement_document = Column(String)  # file path
    standard_contractual_clauses = Column(Boolean, default=False)
    standard_contractual_clauses_version = Column(String, nullable=True)
    cross_border_transfer = Column(Boolean, default=False)
    source_jurisdiction = Column(String, nullable=True)
    destination_jurisdiction = Column(String, nullable=True)
    adequacy_decision = Column(Boolean, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    dpo_review_date = Column(DateTime, nullable=True)
    dpo_approval = Column(Boolean, nullable=True)
    renewal_notifications_sent = Column(JSON, default={})  # {"30_days": date, "7_days": date}
    last_reviewed_at = Column(DateTime, nullable=True)
    last_reviewed_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StandardContractualClause(VersionedEntity, TenantScoped):
    __tablename__ = 'standard_contractual_clauses'
    id = Column(String, primary_key=True, default=generate_uuid_str)
    dpa_id = Column(String, ForeignKey('data_processing_agreements.id'))
    clause_type = Column(String)  # Module One, Two, Three, Four
    module_description = Column(String)
    exporter_role = Column(String)  # Data Exporter
    importer_role = Column(String)  # Data Importer
    included = Column(Boolean, default=True)
    effective_date = Column(DateTime, default=datetime.utcnow)
