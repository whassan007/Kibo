"""
MODULE 6 – DSAR Workflows
Pydantic schemas for DSAR entities: intake, scope, collection, redaction, delivery.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─── DataSubject ──────────────────────────────────────────────────────────────

class DataSubjectBase(BaseModel):
    identifier_type: str = Field(..., example="email")
    identifier_value: str = Field(..., example="user@example.com")

class DataSubjectCreate(DataSubjectBase):
    tenant_id: str = "default"

class DataSubjectRead(DataSubjectBase):
    id: str
    tenant_id: str
    is_verified: bool = False
    verification_method: Optional[str] = None
    verified_at: Optional[datetime] = None
    class Config:
        orm_mode = True


# ─── DSAR Request ─────────────────────────────────────────────────────────────

class DSARRequestCreate(BaseModel):
    tenant_id: str = "default"
    request_type: str = Field(..., example="access")
    jurisdiction: str = Field(..., example="GDPR")
    identifier_type: str = Field(..., example="email")
    identifier_value: str = Field(..., example="user@example.com")
    requestor_email: str
    received_via: str = "web_form"
    preferred_delivery: str = "email"
    assigned_to: Optional[str] = None

class DSARRequestRead(BaseModel):
    id: str
    tenant_id: str
    data_subject_id: str
    request_type: str
    jurisdiction: str
    status: str
    received_at: datetime
    deadline: datetime
    days_remaining: Optional[int] = None
    requestor_email: str
    preferred_delivery: str
    assigned_to: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    refuse_reason: Optional[str] = None
    refuse_justification: Optional[str] = None
    class Config:
        orm_mode = True

class DSARRequestSummary(BaseModel):
    id: str
    status: str
    jurisdiction: str
    deadline: datetime
    days_remaining: Optional[int] = None


# ─── DSAR Scope ───────────────────────────────────────────────────────────────

class DSARScopeCreate(BaseModel):
    systems_override: Optional[List[str]] = None
    categories_override: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    scope_determined_by: Optional[str] = None

class DSARScopeRead(BaseModel):
    id: str
    request_id: str
    systems_in_scope: List[str] = []
    data_categories: List[str] = []
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    estimated_data_size_mb: Optional[float] = None
    estimated_record_count: Optional[int] = None
    scope_determined_at: Optional[datetime] = None
    scope_determined_by: Optional[str] = None
    class Config:
        orm_mode = True


# ─── Collection Task ─────────────────────────────────────────────────────────

class CollectionTaskRead(BaseModel):
    id: str
    request_id: str
    system_id: str
    system_name: Optional[str] = None
    data_category: str
    status: str
    collection_method: Optional[str] = None
    records_found: Optional[int] = None
    data_size_mb: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    class Config:
        orm_mode = True

class CollectionTaskComplete(BaseModel):
    records_found: int
    data_size_mb: float
    collection_output: Optional[Dict[str, Any]] = None


# ─── Redaction ────────────────────────────────────────────────────────────────

class RedactionRuleCreate(BaseModel):
    tenant_id: str = "default"
    name: str
    rule_type: str
    pattern: str
    replacement: str
    fields: List[str]
    categories: Optional[List[str]] = None

class RedactionRuleRead(BaseModel):
    id: str
    tenant_id: str
    name: str
    rule_type: str
    pattern: Optional[str] = None
    replacement: Optional[str] = None
    applies_to_fields: List[str] = []
    applies_to_categories: List[str] = []
    is_active: bool = True
    priority: str = "normal"
    class Config:
        orm_mode = True

class AppliedRedactionRead(BaseModel):
    id: str
    request_id: str
    field_name: str
    original_value_hash: Optional[str] = None
    redacted_value: Optional[str] = None
    justification: Optional[str] = None
    applied_at: datetime
    applied_by: Optional[str] = None
    class Config:
        orm_mode = True


# ─── Delivery Package ────────────────────────────────────────────────────────

class DeliveryPackageRead(BaseModel):
    id: str
    request_id: str
    package_format: str = "zip"
    file_hash: Optional[str] = None
    file_size_bytes: Optional[int] = None
    record_count: Optional[int] = None
    data_categories_included: List[str] = []
    redactions_applied: int = 0
    is_signed: bool = False
    status: str
    prepared_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    delivery_method: Optional[str] = None
    delivered_at: Optional[datetime] = None
    download_token: Optional[str] = None
    class Config:
        orm_mode = True

class PackageVerificationRead(BaseModel):
    id: str
    package_id: str
    check_name: str
    check_passed: bool
    check_detail: Optional[str] = None
    checked_at: datetime
    checked_by: Optional[str] = None
    class Config:
        orm_mode = True


# ─── Workflow State ───────────────────────────────────────────────────────────

class DSARWorkflowState(BaseModel):
    """Read-only representation of the DSAR fulfillment workflow state."""
    request_id: str
    tenant_id: str
    status: str
    scope: Optional[Dict[str, Any]] = None
    collected_data: Optional[Dict[str, Any]] = None
    redacted_data: Optional[Dict[str, Any]] = None
    verification_complete: bool = False
    package_ready: bool = False
    package_id: Optional[str] = None
    delivered: bool = False
    error: Optional[str] = None
