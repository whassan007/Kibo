import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_gateway import app, SessionLocal
from core.models.tenant import Tenant, TenantMembership
from core.models.audit import AccessLog
from core.context.tenant_context import clear_tenant_context

@pytest.fixture(scope="module")
def client():
    # Setup test database records
    db = SessionLocal()
    try:
        # Create tenant A and B
        tenant_a = db.get(Tenant, "tenant-a")
        if not tenant_a:
            tenant_a = Tenant(id="tenant-a", name="Tenant A", is_active=True)
            db.add(tenant_a)
        tenant_b = db.get(Tenant, "tenant-b")
        if not tenant_b:
            tenant_b = Tenant(id="tenant-b", name="Tenant B", is_active=True)
            db.add(tenant_b)
            
        # Add membership
        mem_a = db.query(TenantMembership).filter_by(tenant_id="tenant-a", user_id="user_a").first()
        if not mem_a:
            mem_a = TenantMembership(tenant_id="tenant-a", user_id="user_a", role="analyst", is_active=True)
            db.add(mem_a)
            
        mem_b = db.query(TenantMembership).filter_by(tenant_id="tenant-b", user_id="user_b").first()
        if not mem_b:
            mem_b = TenantMembership(tenant_id="tenant-b", user_id="user_b", role="analyst", is_active=True)
            db.add(mem_b)
            
        db.commit()
    finally:
        db.close()
        
    yield TestClient(app)
    
    # Cleanup after tests
    clear_tenant_context()

def test_tenant_isolation_list(client):
    # 1. Create an assessment for tenant-a
    response_create = client.post(
        "/api/assessments",
        headers={"X-Tenant-ID": "tenant-a", "X-User-ID": "user_a", "x-kibo-scope": "expert"},
        json={
            "title": "Assessment Tenant A",
            "type": "PIA",
            "output_type": "PDF",
            "level": 1,
            "prepared_by": "user_a",
            "jurisdictions": ["Quebec"],
            "roles_in_scope": ["analyst"],
            "departments_in_scope": ["HR"],
            "services_in_scope": ["Payroll"],
            "data_types": ["Salary"],
            "cross_border": False,
            "cross_border_jurisdictions": [],
            "source": "Manual",
            "source_id": ""
        }
    )
    assert response_create.status_code == 200
    created_id = response_create.json()["assessment_id"]
    
    # 2. Query assessments for tenant-a (should find it)
    response_list_a = client.get(
        "/api/assessments",
        headers={"X-Tenant-ID": "tenant-a", "X-User-ID": "user_a", "x-kibo-scope": "expert"}
    )
    assert response_list_a.status_code == 200
    ids_a = [a["assessment_id"] for a in response_list_a.json()]
    assert created_id in ids_a
    
    # 3. Query assessments for tenant-b (should NOT find it)
    response_list_b = client.get(
        "/api/assessments",
        headers={"X-Tenant-ID": "tenant-b", "X-User-ID": "user_b", "x-kibo-scope": "expert"}
    )
    assert response_list_b.status_code == 200
    ids_b = [a["assessment_id"] for a in response_list_b.json()]
    assert created_id not in ids_b
    
    # 4. Try to fetch details of tenant-a assessment with tenant-b credentials (should fail)
    response_get_unauth = client.get(
        f"/api/assessments/{created_id}",
        headers={"X-Tenant-ID": "tenant-b", "X-User-ID": "user_b", "x-kibo-scope": "expert"}
    )
    assert response_get_unauth.status_code == 404

def test_tenant_access_control(client):
    # Try to access tenant-a with user_b (should return 403 Forbidden)
    response = client.get(
        "/api/assessments",
        headers={"X-Tenant-ID": "tenant-a", "X-User-ID": "user_b", "x-kibo-scope": "expert"}
    )
    assert response.status_code == 403
    assert "User user_b not a member of tenant tenant-a" in response.json()["detail"]

def test_access_log_created(client):
    db = SessionLocal()
    try:
        # Check that AccessLog entries were created for the requests
        logs = db.query(AccessLog).filter_by(tenant_id="tenant-a").all()
        assert len(logs) > 0
        assert logs[0].method in ["GET", "POST"]
        assert "/api/assessments" in logs[0].path
    finally:
        db.close()
