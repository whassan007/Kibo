"""RD-13: REST, legal evidence, export and vector tenant boundaries."""
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.context.tenant_context import TenantContext, _tenant_context
from core.middleware.tenant_isolation import (
    TenantIsolationMiddleware, enforce_tenant_isolation,
    filter_annotations_by_tenant, verify_tenant_export_access,
    filter_vector_search_results,
)
from core.models.base import Base
from core.models.tenant import Tenant, TenantMembership, TenantSettings
from core.models.audit import AccessLog


@pytest.fixture
def tenant_context():
    token = _tenant_context.set(TenantContext(
        tenant_id="tenant-a", tenant_name="A", user_id="alice", user_role="analyst"))
    yield
    _tenant_context.reset(token)


@pytest.fixture
def isolated_app(monkeypatch):
    monkeypatch.delenv("KIBO_STRICT_AUTH", raising=False)
    monkeypatch.setenv("KIBO_ENV", "test")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine, tables=[Tenant.__table__, TenantMembership.__table__,
                                             TenantSettings.__table__, AccessLog.__table__])
    sessions = sessionmaker(bind=engine)
    with sessions() as db:
        db.add_all([Tenant(id=tid, name=tid, is_active=True)
                    for tid in ("tenant-a", "tenant-b")])
        db.flush()
        db.add(TenantMembership(tenant_id="tenant-a", user_id="alice",
                                role="analyst", is_active=True))
        db.commit()
    app = FastAPI()
    app.add_middleware(TenantIsolationMiddleware, db_session_factory=sessions)

    @app.get("/records/{tenant_id}")
    def records(tenant_id: str):
        context = enforce_tenant_isolation(tenant_id)
        return {"tenant_id": context.tenant_id, "role": context.user_role,
                "is_admin": context.is_admin}

    with TestClient(app) as client:
        yield client, sessions
    engine.dispose()


def test_cross_tenant_rest_denied(isolated_app):
    client, _ = isolated_app
    headers = {"X-Tenant-ID": "tenant-a", "X-User-ID": "alice"}
    assert client.get("/records/tenant-a", headers=headers).status_code == 200
    assert client.get("/records/tenant-b", headers=headers).status_code == 403
    headers["X-Tenant-ID"] = "tenant-b"
    assert client.get("/records/tenant-b", headers=headers).status_code == 403


def test_cross_tenant_legal_evidence_denied(tenant_context):
    own = {"tenant_id": "tenant-a", "evidence": "own"}
    records = [own, {"tenant_id": "tenant-b", "evidence": "secret"},
               {"evidence": "untagged"}, {"tenant_id": "PUBLIC_STATUTORY"},
               SimpleNamespace(tenant_id="tenant-b")]
    assert filter_annotations_by_tenant(records, "tenant-a") == [own]
    with pytest.raises(HTTPException) as exc:
        filter_annotations_by_tenant(records, "tenant-b")
    assert exc.value.status_code == 403


@pytest.mark.parametrize("owner", ["tenant-b", None, "PUBLIC_STATUTORY", ""])
def test_cross_tenant_document_export_denied(tenant_context, owner):
    with pytest.raises(HTTPException) as exc:
        verify_tenant_export_access(owner, "tenant-a")
    assert exc.value.status_code == 403
    assert verify_tenant_export_access("tenant-a", "tenant-a") is True


def test_public_statutory_export_requires_opt_in(tenant_context):
    for owner in (None, "PUBLIC_STATUTORY"):
        assert verify_tenant_export_access(owner, "tenant-a", include_public_statutory=True)
    with pytest.raises(HTTPException):
        verify_tenant_export_access("tenant-b", "tenant-a", include_public_statutory=True)


def test_cross_tenant_vector_results_filtered(tenant_context):
    own = SimpleNamespace(tenant_id="tenant-a")
    public = {"tenant_id": "PUBLIC_STATUTORY", "is_public_statutory": True}
    global_law = {"tenant_id": None, "is_public_statutory": True}
    results = [own, public, global_law, {"tenant_id": "tenant-b"},
               {"tenant_id": "tenant-b", "is_public_statutory": True},
               {"tenant_id": None, "evidence": "untagged customer evidence"},
               {"tenant_id": "PUBLIC_STATUTORY", "annotation": "not a statute"}]
    assert filter_vector_search_results(results, "tenant-a") == [own]
    assert filter_vector_search_results(results, "tenant-a", include_public_statutory=True) == [own, public, global_law]
    with pytest.raises(HTTPException):
        filter_vector_search_results(results, "tenant-b", include_public_statutory=True)


@pytest.mark.parametrize("helper,args", [
    (filter_annotations_by_tenant, ([], "tenant-a")),
    (filter_vector_search_results, ([], "tenant-a")),
    (verify_tenant_export_access, ("tenant-a", "tenant-a")),
    (verify_tenant_export_access, ("PUBLIC_STATUTORY", "tenant-b")),
])
def test_helpers_require_context(helper, args):
    token = _tenant_context.set(None)
    try:
        with pytest.raises(HTTPException) as exc:
            helper(*args)
        assert exc.value.status_code == 403
    finally:
        _tenant_context.reset(token)


@pytest.mark.parametrize("user_id", ["admin", "untrusted_admin_user", "dpo", "admin_dpo"])
def test_username_cannot_provision_privileges(isolated_app, user_id):
    client, sessions = isolated_app
    response = client.get("/records/default", headers={"X-User-ID": user_id})
    assert response.status_code == 200
    assert response.json() == {"tenant_id": "default", "role": "analyst", "is_admin": False}
    with sessions() as db:
        membership = db.execute(select(TenantMembership).where(
            TenantMembership.user_id == user_id)).scalar_one()
        assert membership.role == "analyst"


@pytest.mark.parametrize("user_id", ["admin", "dpo", "untrusted_admin_user"])
def test_strict_auth_never_auto_provisions(isolated_app, monkeypatch, user_id):
    client, sessions = isolated_app
    monkeypatch.setenv("KIBO_STRICT_AUTH", "true")
    assert client.get("/records/default", headers={"X-User-ID": user_id}).status_code == 401
    with sessions() as db:
        assert db.get(Tenant, "default") is None
        assert db.execute(select(TenantMembership).where(
            TenantMembership.user_id == user_id)).scalar_one_or_none() is None
