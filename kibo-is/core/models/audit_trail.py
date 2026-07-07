from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AuditTrailEntry(BaseModel):
    id: str
    tenant_id: str
    timestamp: datetime
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    changes: Optional[dict] = None
    reason: Optional[str] = None

class AuditTrail(BaseModel):
    entity_type: str
    entity_id: str
    entries: List[AuditTrailEntry]
