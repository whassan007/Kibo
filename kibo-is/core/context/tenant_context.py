from contextvars import ContextVar
from typing import Optional, Any
from pydantic import BaseModel
from fastapi import HTTPException

# Thread-safe context variables
_tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default="default")

class TenantContext(BaseModel):
    tenant_id: str
    tenant_name: str
    user_id: str
    user_role: str
    features_enabled: dict = {}
    is_admin: bool = False

    def __init__(self, **data):
        if 'id' in data and 'tenant_id' not in data:
            data['tenant_id'] = data['id']
        if 'name' in data and 'tenant_name' not in data:
            data['tenant_name'] = data['name']
        if 'role' in data and 'user_role' not in data:
            data['user_role'] = data['role']
        super().__init__(**data)

    @property
    def id(self) -> str:
        return self.tenant_id

    @property
    def name(self) -> str:
        return self.tenant_name

    @property
    def role(self) -> str:
        return self.user_role

# Alias for backward compatibility
Tenant = TenantContext

_tenant_context: ContextVar[Optional[TenantContext]] = ContextVar('tenant_context', default=None)

def get_tenant_id() -> str:
    ctx = _tenant_context.get()
    if ctx:
        return ctx.tenant_id
    return _tenant_id_ctx.get()

def set_tenant_id(tenant_id: str) -> Any:
    return _tenant_id_ctx.set(tenant_id)

def get_current_tenant() -> Optional[TenantContext]:
    ctx = _tenant_context.get()
    if not ctx:
        # Fallback default tenant for compatibility
        return TenantContext(
            tenant_id="default",
            tenant_name="Default Tenant",
            user_id="system",
            user_role="CPO",
            is_admin=True
        )
    return ctx

def set_current_tenant(tenant: Any) -> Any:
    if isinstance(tenant, TenantContext):
        set_tenant_context(tenant)
    else:
        ctx = TenantContext(
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            user_id=tenant.user_id,
            user_role=tenant.role
        )
        set_tenant_context(ctx)

def set_tenant_context(context: TenantContext) -> None:
    _tenant_context.set(context)
    set_tenant_id(context.tenant_id)

def clear_tenant_context() -> None:
    _tenant_context.set(None)
    set_tenant_id("default")
