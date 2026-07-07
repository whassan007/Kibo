import pytest
import os
import sys
from datetime import datetime, timedelta

# Ensure kibo-is directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base
from core.models.audit_log import AuditLog, EntityVersion, DataAccessLog
from core.audit.audit_service import AuditService
from core.audit.temporal_query import TemporalQuery
from core.context.tenant_context import Tenant, set_current_tenant, set_tenant_id

@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    # Setup default tenant context
    tenant = Tenant(id="test_tenant", name="Test Tenant", user_id="user_expert", role="expert")
    set_current_tenant(tenant)
    set_tenant_id("test_tenant")
    
    db = Session()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_audit_log_created_on_change(db_session):
    audit_service = AuditService(db_session)
    
    # 1. Log a change (e.g. Assessment creation)
    log = await audit_service.log_change(
        action="CREATE",
        entity_type="Assessment",
        entity_id="PIA-2026-001",
        previous_state=None,
        new_state={"title": "Test Assessment", "status": "draft"},
        user_id="user_expert",
        reason="Initial creation"
    )
    
    assert log is not None
    assert log.action == "CREATE"
    assert log.entity_type == "Assessment"
    assert log.entity_id == "PIA-2026-001"
    
    # 2. Get audit trail and verify
    trail = await audit_service.get_entity_audit_trail("Assessment", "PIA-2026-001")
    assert len(trail) == 1
    assert trail[0].action == "CREATE"
    assert trail[0].new_state["title"] == "Test Assessment"

@pytest.mark.asyncio
async def test_temporal_query(db_session):
    audit_service = AuditService(db_session)
    temporal_query = TemporalQuery(db_session)
    
    entity_id = "PIA-2026-002"
    
    # Log version 1
    v1_time = datetime.utcnow()
    await audit_service.log_change(
        action="CREATE",
        entity_type="Assessment",
        entity_id=entity_id,
        previous_state=None,
        new_state={"status": "draft"},
        user_id="user_expert",
        reason="Create draft",
        timestamp=v1_time
    )
    
    # Log version 2 (simulating time delay)
    v2_time = v1_time + timedelta(seconds=2)
    await audit_service.log_change(
        action="UPDATE",
        entity_type="Assessment",
        entity_id=entity_id,
        previous_state={"status": "draft"},
        new_state={"status": "approved"},
        user_id="user_expert",
        reason="Approve assessment",
        timestamp=v2_time
    )
    
    # Query state at v1_time + 1 second (should be "draft")
    state_before = await temporal_query.get_entity_as_of(
        "Assessment", entity_id, v1_time + timedelta(seconds=1)
    )
    assert state_before is not None
    assert state_before["status"] == "draft"
    
    # Query state at v2_time + 1 second (should be "approved")
    state_after = await temporal_query.get_entity_as_of(
        "Assessment", entity_id, v2_time + timedelta(seconds=1)
    )
    assert state_after is not None
    assert state_after["status"] == "approved"

@pytest.mark.asyncio
async def test_audit_integrity(db_session):
    audit_service = AuditService(db_session)
    
    log = await audit_service.log_change(
        action="CREATE",
        entity_type="Assessment",
        entity_id="PIA-2026-003",
        previous_state=None,
        new_state={"title": "Untampered"},
        user_id="user_expert"
    )
    
    # Verify untampered integrity
    is_valid = await audit_service.verify_integrity(log.id)
    assert is_valid is True
    
    # Simulate tampering by modifying database directly bypassing change_hash recalculation
    log.action = "TAMPERED_ACTION"
    db_session.commit()
    
    # Verify tampered integrity fails
    is_valid_after_tamper = await audit_service.verify_integrity(log.id)
    assert is_valid_after_tamper is False
