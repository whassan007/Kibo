"""
KIBO Privacy OS — Unified Corporate Hub Router (Copilot, Claude Enterprise MCP, Gemini Enterprise)
Implements Section 11 & Acceptance Tests 11 & 12:
- `GET /api/v1/integrations/status`
- `POST /api/v1/integrations/copilot/query`
- `POST /api/v1/integrations/mcp/invoke`
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from core.context.tenant_context import _tenant_context
from core.security.auth import PrincipalContext, principal_from_request, strict_auth_enabled
from integrations.claude_mcp.kibo_privacy_mcp import (
    APPROVED_MCP_TOOLS,
    MCP_SECURITY_AUDIT_LOG,
    get_privacy_guidance,
    invoke_mcp_tool,
    mcp,
)

logger = logging.getLogger("kibo.core.office.hub_router")

router = APIRouter(
    prefix="/api/v1/integrations",
    tags=["Corporate AI Integrations (Copilot, Claude, Gemini)"],
)

INTEGRATIONS_DIR = Path(__file__).resolve().parents[2] / "integrations"


class CopilotQueryPayload(BaseModel):
    question: str = Field(..., description="Employee or privacy officer natural-language question")
    tenant_id: Optional[str] = Field(default=None, description="Tenant ID (validated against authenticated session)")
    target_tenant_id: Optional[str] = Field(default=None, description="Optional target tenant ID (blocked if cross-tenant)")
    user_id: Optional[str] = Field(default=None, description="Caller user ID")
    role: str = Field(default="EMPLOYEE", description="Caller role")
    hub_provider: str = Field(default="m365_copilot", description="m365_copilot, claude_enterprise, or gemini_enterprise")
    jurisdictions: Optional[List[str]] = Field(default=None)
    vendor_name: Optional[str] = Field(default=None)
    data_categories: Optional[List[str]] = Field(default=None)
    involves_ai: bool = Field(default=False)
    involves_cross_border_transfer: bool = Field(default=False)


class MCPInvokePayload(BaseModel):
    tool_name: str = Field(..., description="One of the 8 approved KIBO Privacy Office MCP tools")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool invocation arguments")
    tenant_id: Optional[str] = Field(default=None, description="Optional top-level tenant_id")
    user_id: Optional[str] = Field(default=None, description="Optional top-level user_id")
    role: Optional[str] = Field(default=None, description="Optional top-level role")
    read_only_default: bool = Field(default=False, description="When True, blocks write tools unless write_grant=True")
    jsonrpc: str = Field(default="2.0")
    id: Optional[str] = Field(default="mcp-req-1")


def _resolve_verified_caller(request: Request, fallback_tenant: Optional[str] = None, fallback_user: Optional[str] = None, fallback_role: Optional[str] = None) -> Dict[str, str]:
    """
    Bind authenticated callers to the middleware PrincipalContext or verified JWT.
    Context variables, headers and payload fallbacks are compatibility inputs only
    for unauthenticated local mode; they never supersede authenticated claims.
    """
    ctx = _tenant_context.get()
    header_tenant = request.headers.get("X-Tenant-ID")
    header_user = request.headers.get("X-User-ID")
    header_role = request.headers.get("X-User-Role")

    principal = getattr(request.state, "principal", None)
    if principal is None:
        principal = principal_from_request(request)
    if strict_auth_enabled() and not (
        isinstance(principal, PrincipalContext) and principal.authenticated
    ):
        raise HTTPException(401, "Verified enterprise token required")
    if isinstance(principal, PrincipalContext) and principal.authenticated:
        if header_tenant and header_tenant != principal.tenant_id:
            raise HTTPException(403, "CROSS_TENANT_ACCESS_DENIED: Tenant mismatch")
        if fallback_tenant and fallback_tenant != principal.tenant_id:
            raise HTTPException(403, "CROSS_TENANT_ACCESS_DENIED: Tenant mismatch")
        roles = tuple(role.upper() for role in principal.roles)
        if not roles:
            raise HTTPException(403, "ROLE_ACCESS_DENIED: Principal has no granted roles")
        if fallback_role and fallback_role.upper() not in roles:
            raise HTTPException(403, "ROLE_ESCALATION_DENIED: Role is not granted to principal")
        return {
            "tenant_id": principal.tenant_id,
            "user_id": principal.user_id,
            "role": fallback_role.upper() if fallback_role else (roles[0] if roles else ""),
        }
    if header_tenant and fallback_tenant and header_tenant != fallback_tenant:
        raise HTTPException(403, "CROSS_TENANT_ACCESS_DENIED: Tenant mismatch")

    if ctx and ctx.tenant_id and ctx.tenant_id != "default":
        verified_tenant = ctx.tenant_id
        verified_user = ctx.user_id or header_user or fallback_user or "user_enterprise"
        verified_role = ctx.user_role or header_role or fallback_role or "EMPLOYEE"
    elif principal and principal.tenant_id and principal.tenant_id != "default":
        verified_tenant = principal.tenant_id
        verified_user = principal.user_id or header_user or fallback_user or "user_enterprise"
        verified_role = (principal.roles[0] if principal.roles else None) or header_role or fallback_role or "EMPLOYEE"
    elif header_tenant:
        verified_tenant = header_tenant.strip()
        verified_user = (header_user or fallback_user or "user_enterprise").strip()
        verified_role = (header_role or fallback_role or "EMPLOYEE").strip()
    elif fallback_tenant:
        verified_tenant = fallback_tenant.strip()
        verified_user = (fallback_user or "user_enterprise").strip()
        verified_role = (fallback_role or "EMPLOYEE").strip()
    else:
        raise HTTPException(status_code=403, detail="CROSS_TENANT_ACCESS_DENIED: Explicit verified tenant context required")

    return {
        "tenant_id": verified_tenant,
        "user_id": verified_user,
        "role": verified_role.upper(),
    }


@router.get("/status")
async def get_integrations_status() -> Dict[str, Any]:
    """
    Lists Microsoft 365 Copilot & Teams, Claude Enterprise MCP, and Google Gemini Enterprise
    integration package status, manifest versions, approved tools, and security controls.
    """
    m365_dir = INTEGRATIONS_DIR / "m365_copilot"
    claude_dir = INTEGRATIONS_DIR / "claude_mcp"
    gemini_dir = INTEGRATIONS_DIR / "gemini_enterprise"

    m365_manifest = json.loads((m365_dir / "manifest.json").read_text(encoding="utf-8"))
    declarative_agent = json.loads((m365_dir / "declarativeAgent.json").read_text(encoding="utf-8"))
    api_plugin = json.loads((m365_dir / "kibo-api-plugin.json").read_text(encoding="utf-8"))
    gemini_manifest = json.loads((gemini_dir / "gemini_extension.json").read_text(encoding="utf-8"))

    approved_tools = list(APPROVED_MCP_TOOLS.keys())

    return {
        "status": "operational",
        "server_name": mcp.name,
        "approved_tools_count": len(approved_tools),
        "approved_tools": approved_tools,
        "security_controls": {
            "organization_aware_permissions": True,
            "mandatory_tenant_context_validation": True,
            "strict_tenant_isolation": True,
            "default_read_only_mode": True,
            "consequential_writes_create_drafts_only": True,
            "human_approval_required_for_external_dispatch": True,
            "audit_logged_invocations_count": len(MCP_SECURITY_AUDIT_LOG),
        },
        "packages": {
            "m365_copilot_and_teams": {
                "ready": True,
                "manifest_version": m365_manifest.get("manifestVersion"),
                "declarative_agent_version": declarative_agent.get("version"),
                "api_plugin_version": api_plugin.get("schema_version"),
                "openapi_spec": str(m365_dir / "openapi.yaml"),
                "auth_scheme": "Microsoft Entra ID OAuth2 / BearerAuth + X-Tenant-ID",
                "functions_count": len(api_plugin.get("functions", [])),
            },
            "claude_enterprise_mcp": {
                "ready": True,
                "server_module": str(claude_dir / "kibo_privacy_mcp.py"),
                "server_name": mcp.name,
                "transports": ["stdio", "http_jsonrpc"],
                "tools_count": len(approved_tools),
            },
            "gemini_enterprise": {
                "ready": True,
                "extension_manifest": str(gemini_dir / "gemini_extension.json"),
                "extension_name": gemini_manifest.get("name"),
                "version": gemini_manifest.get("version"),
                "auth_type": gemini_manifest.get("manifest", {}).get("authConfig", {}).get("authType"),
                "tools_count": len(gemini_manifest.get("toolConfigs", [])),
            },
        },
    }


@router.post("/copilot/query")
async def handle_copilot_query(payload: CopilotQueryPayload, request: Request) -> Dict[str, Any]:
    """
    Handles Microsoft 365 Copilot, Teams, Claude Enterprise, and Gemini Enterprise privacy
    guidance queries with strict server-side tenant isolation and Acceptance Test 12 verification.
    """
    caller = _resolve_verified_caller(
        request,
        fallback_tenant=payload.tenant_id,
        fallback_user=payload.user_id,
        fallback_role=payload.role if "role" in payload.model_fields_set else None,
    )
    requested_tenant = payload.tenant_id or caller["tenant_id"]

    try:
        result = get_privacy_guidance(
            tenant_id=requested_tenant,
            user_id=caller["user_id"],
            role=caller["role"],
            question=payload.question,
            jurisdictions=payload.jurisdictions,
            vendor_name=payload.vendor_name,
            data_categories=payload.data_categories,
            involves_ai=payload.involves_ai,
            involves_cross_border_transfer=payload.involves_cross_border_transfer,
            authenticated_tenant_id=caller["tenant_id"],
            target_tenant_id=payload.target_tenant_id,
        )
        result["hub_provider"] = payload.hub_provider
        return result
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/mcp/invoke")
async def handle_mcp_invoke(payload: MCPInvokePayload, request: Request) -> Dict[str, Any]:
    """
    Executes `kibo_privacy_mcp` tools over HTTP/JSON-RPC with strict server-side tenant isolation
    (Acceptance Test 11). If a caller authenticated to `tenant-ca` attempts to query or pass arguments
    targeting `tenant-us`, returns HTTP 403 `CROSS_TENANT_ACCESS_DENIED`.
    """
    arg_tenant = payload.arguments.get("tenant_id") or payload.tenant_id
    arg_user = payload.arguments.get("user_id") or payload.user_id
    arg_role = payload.arguments.get("role") or payload.role

    caller = _resolve_verified_caller(
        request,
        fallback_tenant=arg_tenant,
        fallback_user=arg_user,
        fallback_role=arg_role,
    )

    for tenant in (payload.tenant_id, payload.arguments.get("tenant_id"), payload.arguments.get("target_tenant_id")):
        if tenant and tenant != caller["tenant_id"]:
            raise HTTPException(403, "CROSS_TENANT_ACCESS_DENIED: Tenant mismatch")
    if payload.role:
        _resolve_verified_caller(request, fallback_role=payload.role)

    call_args = dict(payload.arguments)
    if payload.tenant_id and "tenant_id" not in call_args:
        call_args["tenant_id"] = payload.tenant_id
    if payload.user_id and "user_id" not in call_args:
        call_args["user_id"] = payload.user_id
    if payload.role and "role" not in call_args:
        call_args["role"] = payload.role

    try:
        output = invoke_mcp_tool(
            payload.tool_name,
            call_args,
            authenticated_tenant_id=caller["tenant_id"],
            authenticated_user_id=caller["user_id"],
            authenticated_role=caller["role"],
            read_only_default=payload.read_only_default,
        )
        return {
            "jsonrpc": payload.jsonrpc,
            "id": payload.id,
            "tool_name": payload.tool_name,
            "authenticated_tenant_id": caller["tenant_id"],
            "result": output,
        }
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/enterprise/verify")
async def verify_enterprise_hub(payload: CopilotQueryPayload, request: Request) -> Dict[str, Any]:
    """RD-18: verify a Bearer JWT and execute a tenant-scoped hub tool."""
    if payload.hub_provider not in {"m365_copilot", "claude_enterprise", "gemini_enterprise"}:
        raise HTTPException(400, "Unsupported enterprise hub provider")
    if not request.headers.get("Authorization", "").lower().startswith("bearer "):
        raise HTTPException(401, "Verified enterprise Bearer token required")
    principal = principal_from_request(request)
    if not principal.authenticated:
        raise HTTPException(401, "Verified enterprise Bearer token required")
    result = await handle_copilot_query(payload, request)
    return {"authenticated": True, "hub_provider": payload.hub_provider,
            "tool_name": "get_privacy_guidance", "result": result}
