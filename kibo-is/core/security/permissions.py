from enum import Enum
from fastapi import Request, HTTPException, Depends
from core.context.tenant_context import get_current_tenant

class Role(str, Enum):
    ADMIN = "admin"
    DPO = "dpo"
    ANALYST = "analyst"
    VIEWER = "viewer"

PERMISSIONS = {
    Role.ADMIN: [
        'assessments:create', 'assessments:read', 'assessments:update', 'assessments:delete',
        'risks:create', 'risks:read', 'risks:update', 'risks:accept',
        'controls:create', 'controls:read', 'controls:update',
        'vendors:create', 'vendors:read', 'vendors:update',
        'users:manage',
        'reports:export',
        'settings:configure'
    ],
    Role.DPO: [
        'assessments:create', 'assessments:read', 'assessments:update', 'assessments:approve',
        'risks:create', 'risks:read', 'risks:update',
        'controls:read',
        'vendors:read',
        'reports:read',
    ],
    Role.ANALYST: [
        'assessments:create', 'assessments:read', 'assessments:update',
        'risks:read',
        'controls:read',
        'vendors:read',
    ],
    Role.VIEWER: [
        'assessments:read',
        'risks:read',
        'controls:read',
        'vendors:read',
    ]
}

def require_permission(action: str):
    async def check_permission(request: Request):
        tenant = get_current_tenant()
        if not tenant:
            raise HTTPException(status_code=401, detail="Unauthorized: No tenant context")
            
        role = Role(tenant.user_role)
        allowed_actions = PERMISSIONS.get(role, [])
        if action not in allowed_actions:
            raise HTTPException(
                status_code=403,
                detail=f"Role {role.value} not authorized for {action}"
            )
        return tenant
    return Depends(check_permission)
