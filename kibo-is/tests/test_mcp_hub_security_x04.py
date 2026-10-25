"""RD-13 tenant/role boundaries and RD-18 signed enterprise hub invocations."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.office.hub_router import router
from core.security.auth import create_tenant_jwt


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("KIBO_STRICT_AUTH", "1")
    monkeypatch.setenv("KIBO_JWT_SECRET", "x04-test-signing-key-at-least-32-bytes-long")
    monkeypatch.setenv("KIBO_JWT_ISSUER", "https://x04.example.test")
    monkeypatch.setenv("KIBO_JWT_AUDIENCE", "kibo-enterprise")
    monkeypatch.setenv("KIBO_JWT_ALGORITHM", "HS256")
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def headers():
    return {"Authorization": "Bearer " + create_tenant_jwt(
        "employee-x04", "tenant-ca", roles=("EMPLOYEE",))}


@pytest.mark.parametrize("provider", ["m365_copilot", "claude_enterprise", "gemini_enterprise"])
def test_rd18_real_jwt_hub_verification(client, provider):
    response = client.post("/api/v1/integrations/enterprise/verify", headers=headers(),
                           json={"hub_provider": provider, "question": "Explain privacy policy"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["authenticated"] is True
    assert body["hub_provider"] == provider
    assert body["result"]["organization_context"]["tenant_id"] == "tenant-ca"


@pytest.mark.parametrize("path,payload", [
    ("copilot/query", {"question": "Explain privacy policy"}),
    ("mcp/invoke", {"tool_name": "lookup_privacy_tasks"}),
    ("copilot/query", {"hub_provider": "gemini_enterprise", "question": "Explain privacy policy"}),
])
def test_rd13_authenticated_and_unauthenticated(client, path, payload):
    url = "/api/v1/integrations/" + path
    assert client.post(url, json=payload).status_code == 401
    assert client.post(url, headers={"X-Tenant-ID": "tenant-ca", "X-User-Role": "DPO"}, json=payload).status_code == 401
    response = client.post(url, headers=headers(), json=payload)
    assert response.status_code == 200, response.text
    assert client.post(url, headers=headers(), json={**payload, "role": "DPO"}).status_code == 403
    invalid = headers()
    invalid["Authorization"] += "tampered"
    assert client.post(url, headers=invalid, json=payload).status_code == 401


@pytest.mark.parametrize("arguments,top", [
    ({"tenant_id": "tenant-us"}, {}),
    ({"target_tenant_id": "tenant-us"}, {}),
    ({"authenticated_tenant_id": "tenant-us", "tenant_id": "tenant-us"}, {}),
    ({"tenant_id": "tenant-ca"}, {"tenant_id": "tenant-us"}),
    ({"role": "DPO"}, {}),
])
def test_rd13_mcp_boundary(client, arguments, top):
    response = client.post("/api/v1/integrations/mcp/invoke", headers=headers(),
                           json={"tool_name": "lookup_privacy_tasks", "arguments": arguments, **top})
    assert response.status_code == 403, response.text


def test_header_cannot_escalate_role(client):
    response = client.post("/api/v1/integrations/mcp/invoke",
                           headers={**headers(), "X-User-Role": "DPO"},
                           json={"tool_name": "lookup_privacy_tasks"})
    assert response.status_code == 200
    assert response.json()["result"]["role"] == "EMPLOYEE"


@pytest.mark.parametrize("field", ["tenant_id", "target_tenant_id"])
def test_legacy_header_payload_tenant_mismatch(client, monkeypatch, field):
    monkeypatch.setenv("KIBO_STRICT_AUTH", "0")
    response = client.post("/api/v1/integrations/copilot/query",
                           headers={"X-Tenant-ID": "tenant-ca"},
                           json={"question": "Explain privacy policy", field: "tenant-us"})
    assert response.status_code == 403
    assert "CROSS_TENANT_ACCESS_DENIED" in response.json()["detail"]


def test_principal_without_roles_cannot_inherit_tool_default(client):
    token = create_tenant_jwt("employee-x04", "tenant-ca", roles=())
    response = client.post("/api/v1/integrations/mcp/invoke",
                           headers={"Authorization": "Bearer " + token},
                           json={"tool_name": "lookup_privacy_tasks"})
    assert response.status_code == 403
