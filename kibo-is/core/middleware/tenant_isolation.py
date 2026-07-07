import json
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from core.context.tenant_context import set_tenant_context, TenantContext
from core.models.tenant import Tenant, TenantMembership

class TenantIsolationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session_factory):
        super().__init__(app)
        self.db_session_factory = db_session_factory

    async def dispatch(self, request: Request, call_next):
        # Allow system diagnostics / metadata routes or test paths
        if request.url.path.startswith('/api/public') or request.url.path.startswith('/docs') or request.url.path.startswith('/openapi.json'):
            return await call_next(request)
            
        # Extract tenant ID
        tenant_id = self.extract_tenant_from_request(request)
        if not tenant_id:
            # For backward compatibility, default to "default" if no header is present
            tenant_id = "default"
            
        db = self.db_session_factory()
        try:
            # Verify tenant exists
            stmt = select(Tenant).where(Tenant.id == tenant_id)
            result = db.execute(stmt)
            tenant_obj = result.scalar_one_or_none()
            
            if not tenant_obj:
                # If tenant doesn't exist, we auto-create "default" to ensure backward compatibility
                if tenant_id == "default":
                    tenant_obj = Tenant(
                        id="default",
                        name="Default Tenant",
                        subscription_tier="enterprise",
                        features_enabled={"vendor_risk": True},
                        is_active=True
                    )
                    db.add(tenant_obj)
                    db.commit()
                    db.refresh(tenant_obj)
                else:
                    return JSONResponse(status_code=403, content={"detail": f"Tenant {tenant_id} not found"})
                    
            if not tenant_obj.is_active or tenant_obj.is_suspended:
                return JSONResponse(status_code=403, content={"detail": f"Tenant {tenant_id} is inactive or suspended"})
                
            # Extract user ID
            user_id = self.extract_user_from_request(request)
            if not user_id:
                # Mock default user for backward compatibility
                user_id = "user_expert"
                
            # Verify or auto-create membership
            stmt = select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.user_id == user_id
            )
            res_mem = db.execute(stmt)
            membership_obj = res_mem.scalar_one_or_none()
            
            if not membership_obj:
                if tenant_id == "default":
                    membership_obj = TenantMembership(
                        tenant_id=tenant_id,
                        user_id=user_id,
                        role="admin" if "admin" in user_id else "dpo" if "dpo" in user_id else "analyst",
                        is_active=True
                    )
                    db.add(membership_obj)
                    db.commit()
                    db.refresh(membership_obj)
                else:
                    return JSONResponse(status_code=403, content={"detail": f"User {user_id} not a member of tenant {tenant_id}"})
                    
            if not membership_obj.is_active:
                return JSONResponse(status_code=403, content={"detail": "Membership is inactive"})
                
            # Set tenant context
            context = TenantContext(
                tenant_id=tenant_id,
                tenant_name=tenant_obj.name,
                user_id=user_id,
                user_role=membership_obj.role,
                features_enabled=tenant_obj.features_enabled or {},
                is_admin=(membership_obj.role == 'admin' or user_id == "user_expert")
            )
            set_tenant_context(context)
            
            # Attach db session to state
            request.state.db = db
            
            response = await call_next(request)
            response.headers['X-Tenant-ID'] = tenant_id
            return response
        finally:
            db.close()

    def extract_tenant_from_request(self, request: Request) -> str:
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            return tenant_id
            
        host = request.headers.get('host', '')
        parts = host.split('.')
        if len(parts) > 2:
            return parts[0]
            
        return request.query_params.get('tenant')

    def extract_user_from_request(self, request: Request) -> str:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        user_id = request.headers.get('X-User-ID')
        if user_id:
            return user_id
        return request.cookies.get('user_id')
