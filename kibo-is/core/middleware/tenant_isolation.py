"""Tenant identity, membership enforcement and shared retrieval guards."""
import logging
from contextvars import ContextVar

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from core.context.tenant_context import (
    TenantContext, _tenant_context, _tenant_id_ctx,
)
from core.models.tenant import Tenant, TenantMembership
from core.models.audit import AccessLog
from core.security.auth import principal_from_request, strict_auth_enabled

logger = logging.getLogger(__name__)
_access_scope = ContextVar("tenant_access_scope", default=None)


def _record_denial(db, tenant_id, user_id, method, path, request=None):
    logger.warning("Tenant access denied: tenant=%r user=%r method=%s path=%s",
                   tenant_id, user_id, method, path)
    try:
        # Unknown tenant IDs cannot satisfy the AccessLog foreign key.
        exists = db.get(Tenant, tenant_id) if tenant_id else None
        db.add(AccessLog(tenant_id=tenant_id if exists else None, user_id=user_id,
                         method=method, path=path, status_code=403, duration_ms=0,
                         ip_address=request.client.host if request and request.client else None,
                         user_agent=request.headers.get("user-agent") if request else None))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist tenant access denial")


def enforce_tenant_isolation(requested_tenant_id: str):
    """Require an explicit tenant context; never use the legacy default fallback.

    MCP and retrieval entry points must establish a verified tenant context and
    call this guard before running tenant-scoped SQL or retrieving records.
    """
    context = _tenant_context.get()
    if not context or not requested_tenant_id or context.tenant_id != requested_tenant_id:
        scope = _access_scope.get()
        if scope:
            db, request = scope
            _record_denial(db, requested_tenant_id, context.user_id if context else None,
                           request.method, request.url.path, request)
        raise HTTPException(403, "Cross-tenant access attempt blocked")
    return context


def filter_records_by_tenant(records: list, tenant_id: str) -> list:
    """Fail closed for missing context, mismatched tenants and untagged records."""
    enforce_tenant_isolation(tenant_id)
    return [record for record in records
            if (record.get("tenant_id") if isinstance(record, dict)
                else getattr(record, "tenant_id", None)) == tenant_id]


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session_factory):
        super().__init__(app)
        self.db_session_factory = db_session_factory

    async def dispatch(self, request: Request, call_next):
        # Reset at the boundary, including public routes, and restore caller context.
        context_token = _tenant_context.set(None)
        id_token = _tenant_id_ctx.set("default")
        scope_token = None
        db = None
        try:
            public = (request.url.path == "/api/public" or request.url.path.startswith("/api/public/")
                      or request.url.path in {"/docs", "/docs/oauth2-redirect", "/openapi.json"})
            if public and not request.headers.get("Authorization") and not request.headers.get("X-Tenant-ID"):
                return await call_next(request)
            db = self.db_session_factory()
            try:
                principal = principal_from_request(request)
            except HTTPException as exc:
                if exc.status_code == 403:
                    verified = getattr(request.state, "principal", None)
                    _record_denial(db, request.headers.get("X-Tenant-ID"),
                                   verified.user_id if verified else request.headers.get("X-User-ID"), request.method,
                                   request.url.path, request)
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
            tenant_id, user_id = principal.tenant_id, principal.user_id
            request.state.principal = principal

            def deny(detail):
                _record_denial(db, tenant_id, user_id, request.method, request.url.path, request)
                return JSONResponse(status_code=403, content={"detail": detail})

            tenant = db.execute(select(Tenant).where(Tenant.id == tenant_id)).scalar_one_or_none()
            legacy_default = not strict_auth_enabled() and not principal.authenticated and tenant_id == "default"
            if tenant is None and legacy_default:
                tenant = Tenant(id="default", name="Default Tenant", subscription_tier="enterprise",
                                features_enabled={"vendor_risk": True}, is_active=True)
                db.add(tenant)
                db.commit()
                db.refresh(tenant)
            if tenant is None:
                return deny(f"Tenant {tenant_id} not found")
            if not tenant.is_active or tenant.is_suspended:
                return deny(f"Tenant {tenant_id} is inactive or suspended")
            membership = db.execute(select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == user_id)).scalar_one_or_none()
            if membership is None and legacy_default:
                # An existing member cannot select another tenant through legacy headers.
                existing = db.execute(select(TenantMembership).where(
                    TenantMembership.user_id == user_id)).scalars().first()
                if existing is None:
                    membership = TenantMembership(tenant_id=tenant_id, user_id=user_id,
                        role="admin" if "admin" in user_id else "dpo" if "dpo" in user_id else "analyst",
                        is_active=True)
                    db.add(membership)
                    db.commit()
                    db.refresh(membership)
            if membership is None:
                return deny(f"User {user_id} not a member of tenant {tenant_id}")
            if not membership.is_active:
                return deny("Membership is inactive")
            context = TenantContext(tenant_id=tenant_id, tenant_name=tenant.name,
                user_id=user_id, user_role=membership.role,
                features_enabled=tenant.features_enabled or {},
                is_admin=membership.role.upper() in {"ADMIN", "TENANT_ADMIN", "SYSTEM_ADMIN"})
            _tenant_context.set(context)
            _tenant_id_ctx.set(tenant_id)
            scope_token = _access_scope.set((db, request))
            request.state.db = db
            response = await call_next(request)
            response.headers["X-Tenant-ID"] = tenant_id
            return response
        finally:
            if scope_token is not None:
                _access_scope.reset(scope_token)
            _tenant_context.reset(context_token)
            _tenant_id_ctx.reset(id_token)
            if db is not None:
                db.close()

    def extract_tenant_from_request(self, request: Request) -> str:
        return principal_from_request(request).tenant_id

    def extract_user_from_request(self, request: Request) -> str:
        return principal_from_request(request).user_id
