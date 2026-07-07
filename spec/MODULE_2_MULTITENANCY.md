# MODULE 2: MULTI-TENANCY ISOLATION LAYER
## For Antigravity IDE + Gemma4

**Duration:** 6 weeks  
**Priority:** CRITICAL  
**Effort:** High  
**Dependencies:** MODULE 1 (Domain Model)

---

## OVERVIEW

Implement complete tenant isolation at all layers: middleware → database → API responses. Ensure zero data leakage between customers.

**Current State:**
- All customers in single SQLite database
- No tenant context in requests
- No row-level isolation
- No audit trail of data access

**Target State:**
- Tenant context extracted from request (subdomain/header)
- Automatic row-level filtering
- Middleware validates tenant membership
- Audit logs include tenant + user + action

---

## MODULE OBJECTIVES

1. ✅ Create Tenant entity and TenantMembership
2. ✅ Implement request middleware for tenant context
3. ✅ Add tenant validation to all endpoints
4. ✅ Create TenantRepository with scoped queries
5. ✅ Add tenant filtering to all entity queries
6. ✅ Implement comprehensive access control tests

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are implementing multi-tenancy isolation for KIBO, ensuring complete data separation between customers.

TASK: Create a tenant isolation layer that prevents cross-tenant data access at all layers.

REQUIREMENTS:
1. Framework: FastAPI middleware + SQLAlchemy query filters
2. Tenant Context: Extract from headers (X-Tenant-ID) or subdomains
3. Database: PostgreSQL with row-level filtering
4. Audit: Log all data access with tenant context
5. Testing: Verify zero inter-tenant leakage

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── models/
│   │   ├── tenant.py           # Tenant, TenantMembership, TenantFeatures
│   │   └── audit.py            # AccessLog, DataAccessLog
│   ├── context/
│   │   ├── __init__.py
│   │   ├── tenant_context.py   # TenantContext, get_current_tenant()
│   │   └── request_context.py  # RequestContext with user + tenant
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── tenant_isolation.py # TenantIsolationMiddleware
│   │   ├── audit_logging.py    # AuditLoggingMiddleware
│   │   └── error_handling.py   # TenantErrorHandler
│   ├── repositories/
│   │   ├── tenant_repository.py
│   │   └── audit_repository.py
│   └── security/
│       ├── __init__.py
│       ├── tenant_validation.py
│       └── permissions.py
├── api/
│   └── v1/
│       └── middleware.py        # Dependency injection for tenant
└── tests/
    └── test_multitenancy.py
```

IMPLEMENTATION DETAILS:

1. **models/tenant.py**: Define Tenant and membership entities
   ```python
   from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
   from sqlalchemy.orm import relationship
   from core.models.base import VersionedEntity, Timestamped
   
   class Tenant(VersionedEntity, Timestamped):
       __tablename__ = 'tenants'
       id = Column(String, primary_key=True)  # slug: "acme-corp"
       name = Column(String, unique=True, nullable=False)  # "ACME Corporation"
       industry = Column(String)  # healthcare, finance, ngo, etc.
       size = Column(String)  # small, medium, large, enterprise
       primary_jurisdiction = Column(String)  # Ontario, Quebec, California, EU
       
       # Subscription
       subscription_tier = Column(String)  # free, starter, pro, enterprise
       features_enabled = Column(JSON, default={})  # {vendor_risk: true, dsar: false, ...}
       max_users = Column(Integer, default=10)
       max_assessments_per_month = Column(Integer)
       
       # Status
       is_active = Column(Boolean, default=True)
       is_suspended = Column(Boolean, default=False)
       
       # Relationships
       users = relationship('TenantUser', back_populates='tenant')
       memberships = relationship('TenantMembership', back_populates='tenant')
       settings = relationship('TenantSettings', back_populates='tenant', uselist=False)
   
   class TenantMembership(VersionedEntity):
       __tablename__ = 'tenant_memberships'
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
       user_id = Column(String, ForeignKey('users.id'), nullable=False)
       role = Column(String)  # admin, dpo, analyst, viewer
       is_active = Column(Boolean, default=True)
       
       # Relationships
       tenant = relationship('Tenant', back_populates='memberships')
       user = relationship('User', back_populates='tenant_memberships')
   
   class TenantSettings(VersionedEntity):
       __tablename__ = 'tenant_settings'
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), unique=True)
       
       # Compliance settings
       require_dpo_approval = Column(Boolean, default=True)
       assessment_timeout_days = Column(Integer, default=30)
       breach_notification_deadline_hours = Column(Integer, default=72)
       
       # Data retention
       assessment_archive_years = Column(Integer, default=7)
       audit_log_retention_years = Column(Integer, default=7)
       
       # Integration
       webhook_url = Column(String, nullable=True)
       sso_provider = Column(String, nullable=True)  # okta, azure, google
       
       tenant = relationship('Tenant', back_populates='settings')
   ```

2. **context/tenant_context.py**: Request-scoped tenant context
   ```python
   from contextvars import ContextVar
   from typing import Optional
   from pydantic import BaseModel
   
   class TenantContext(BaseModel):
       tenant_id: str
       tenant_name: str
       user_id: str
       user_role: str
       features_enabled: dict
       is_admin: bool
   
   # Thread-safe context variable
   _tenant_context: ContextVar[Optional[TenantContext]] = ContextVar(
       'tenant_context', default=None
   )
   
   def set_tenant_context(context: TenantContext) -> None:
       _tenant_context.set(context)
   
   def get_current_tenant() -> TenantContext:
       ctx = _tenant_context.get()
       if not ctx:
           raise HTTPException(
               status_code=401,
               detail="No tenant context. Request must include X-Tenant-ID header"
           )
       return ctx
   
   def get_tenant_id() -> str:
       return get_current_tenant().tenant_id
   
   def clear_tenant_context() -> None:
       _tenant_context.set(None)
   ```

3. **middleware/tenant_isolation.py**: Request middleware
   ```python
   from fastapi import Request, HTTPException
   from starlette.middleware.base import BaseHTTPMiddleware
   from sqlalchemy.orm import Session
   from core.context.tenant_context import set_tenant_context, TenantContext
   
   class TenantIsolationMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request: Request, call_next):
           # Extract tenant from subdomain or header
           tenant_id = extract_tenant_from_request(request)
           
           if not tenant_id:
               if request.url.path.startswith('/api/public'):
                   # Public endpoints don't need tenant
                   response = await call_next(request)
                   return response
               raise HTTPException(
                   status_code=400,
                   detail="Missing tenant context (X-Tenant-ID header or subdomain)"
               )
           
           # Get DB session
           db = request.state.db  # Injected by dependency
           
           # Verify tenant exists
           tenant = await db.execute(
               select(Tenant).where(Tenant.id == tenant_id)
           )
           tenant_obj = tenant.scalar_one_or_none()
           
           if not tenant_obj or not tenant_obj.is_active:
               raise HTTPException(
                   status_code=403,
                   detail=f"Tenant {tenant_id} not found or inactive"
               )
           
           # Get user
           user_id = extract_user_from_request(request)
           if not user_id:
               raise HTTPException(status_code=401, detail="Unauthorized")
           
           # Verify user belongs to tenant
           membership = await db.execute(
               select(TenantMembership).where(
                   TenantMembership.tenant_id == tenant_id,
                   TenantMembership.user_id == user_id,
                   TenantMembership.is_active == True
               )
           )
           membership_obj = membership.scalar_one_or_none()
           
           if not membership_obj:
               raise HTTPException(
                   status_code=403,
                   detail="User not a member of this tenant"
               )
           
           # Set tenant context
           context = TenantContext(
               tenant_id=tenant_id,
               tenant_name=tenant_obj.name,
               user_id=user_id,
               user_role=membership_obj.role,
               features_enabled=tenant_obj.features_enabled,
               is_admin=membership_obj.role == 'admin'
           )
           set_tenant_context(context)
           
           # Process request with tenant context
           response = await call_next(request)
           
           # Add tenant info to response headers
           response.headers['X-Tenant-ID'] = tenant_id
           
           return response
   
   def extract_tenant_from_request(request: Request) -> Optional[str]:
       # Priority:
       # 1. X-Tenant-ID header
       # 2. Subdomain (api.tenant-id.kibo.is → tenant-id)
       # 3. Query parameter (?tenant=tenant-id)
       
       # From header
       tenant_id = request.headers.get('X-Tenant-ID')
       if tenant_id:
           return tenant_id
       
       # From subdomain
       host = request.headers.get('host', '')
       parts = host.split('.')
       if len(parts) > 2:  # subdomain.kibo.is
           return parts[0]
       
       # From query param
       return request.query_params.get('tenant')
   
   def extract_user_from_request(request: Request) -> Optional[str]:
       # Get from Authorization header (JWT token)
       # Or from session cookie
       # Or from API key
       
       # For now: simple bearer token with user_id
       auth_header = request.headers.get('Authorization', '')
       if auth_header.startswith('Bearer '):
           # Parse JWT and extract user_id
           token = auth_header[7:]
           # decode_jwt(token) → {"user_id": "..."}
           return decode_jwt(token).get('user_id')
       
       # Session cookie fallback
       return request.cookies.get('user_id')
   ```

4. **middleware/audit_logging.py**: Log all data access
   ```python
   from datetime import datetime
   from starlette.middleware.base import BaseHTTPMiddleware
   from core.models.audit import AccessLog
   
   class AuditLoggingMiddleware(BaseHTTPMiddleware):
       async def dispatch(self, request: Request, call_next):
           # Record request start
           start_time = datetime.utcnow()
           
           # Get tenant and user from context
           try:
               tenant = get_current_tenant()
               tenant_id = tenant.tenant_id
               user_id = tenant.user_id
           except:
               tenant_id = None
               user_id = None
           
           # Process request
           response = await call_next(request)
           
           # Record request end
           duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
           
           # Log access
           log = AccessLog(
               tenant_id=tenant_id,
               user_id=user_id,
               method=request.method,
               path=request.url.path,
               status_code=response.status_code,
               duration_ms=duration_ms,
               ip_address=request.client.host if request.client else None,
               user_agent=request.headers.get('User-Agent'),
               timestamp=start_time
           )
           
           db = request.state.db
           db.add(log)
           await db.commit()
           
           return response
   ```

5. **models/audit.py**: Audit trail entities
   ```python
   from sqlalchemy import Column, String, Integer, DateTime, JSON, Float
   from core.models.base import Timestamped
   
   class AccessLog(Base, Timestamped):
       __tablename__ = 'access_logs'
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'))
       user_id = Column(String)
       
       method = Column(String)  # GET, POST, PUT, DELETE
       path = Column(String)
       status_code = Column(Integer)
       duration_ms = Column(Float)
       
       ip_address = Column(String)
       user_agent = Column(String)
       
       __table_args__ = (
           Index('ix_access_logs_tenant_timestamp', 'tenant_id', 'timestamp'),
       )
   
   class DataAccessLog(Base, Timestamped):
       __tablename__ = 'data_access_logs'
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
       user_id = Column(String, nullable=False)
       
       entity_type = Column(String)  # Assessment, Risk, System, Vendor
       entity_id = Column(String)
       action = Column(String)  # READ, CREATE, UPDATE, DELETE
       
       data_accessed = Column(JSON)  # Summary of what was accessed
       reason = Column(String, nullable=True)  # Why was it accessed
       
       __table_args__ = (
           Index('ix_data_access_logs_tenant_user', 'tenant_id', 'user_id'),
       )
   ```

6. **security/permissions.py**: Role-based access control
   ```python
   from enum import Enum
   from typing import List
   
   class Role(str, Enum):
       ADMIN = "admin"
       DPO = "dpo"
       ANALYST = "analyst"
       VIEWER = "viewer"
   
   # Permission matrix: role → actions
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
           role = Role(tenant.user_role)
           
           allowed_actions = PERMISSIONS.get(role, [])
           if action not in allowed_actions:
               raise HTTPException(
                   status_code=403,
                   detail=f"Role {role} not authorized for {action}"
               )
           
           return tenant
       
       return Depends(check_permission)
   
   @require_permission('assessments:create')
   async def create_assessment(assessment: AssessmentCreate):
       # Only runs if user has permission
       ...
   ```

7. **repositories/tenant_repository.py**: Scoped queries
   ```python
   from sqlalchemy import select
   from core.context.tenant_context import get_tenant_id
   from core.models.tenant import Tenant, TenantMembership
   
   class TenantRepository(BaseRepository[Tenant]):
       async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
           # Always verify requesting user has access to this tenant
           current_tenant = get_tenant_id()
           if tenant_id != current_tenant:
               raise HTTPException(status_code=403, detail="Access denied")
           
           return await super().get_by_id(tenant_id)
       
       async def get_members(self, tenant_id: str) -> List[TenantMembership]:
           current_tenant = get_tenant_id()
           if tenant_id != current_tenant:
               raise HTTPException(status_code=403, detail="Access denied")
           
           stmt = select(TenantMembership).where(
               TenantMembership.tenant_id == tenant_id,
               TenantMembership.is_active == True
           )
           result = await self.db.execute(stmt)
           return result.scalars().all()
   
   class TenantScopedRepository(BaseRepository[T]):
       """Base repository that automatically filters by tenant"""
       
       async def get_by_id(self, obj_id: UUID) -> Optional[T]:
           tenant_id = get_tenant_id()
           stmt = select(self.model_class).where(
               self.model_class.id == obj_id,
               self.model_class.tenant_id == tenant_id
           )
           result = await self.db.execute(stmt)
           return result.scalar_one_or_none()
       
       async def list_all(self) -> List[T]:
           tenant_id = get_tenant_id()
           stmt = select(self.model_class).where(
               self.model_class.tenant_id == tenant_id
           )
           result = await self.db.execute(stmt)
           return result.scalars().all()
   ```

8. **Integration with existing endpoints**:
   ```python
   # Before: queries could leak data
   @app.get("/api/assessments")
   def list_assessments():
       return db.query(Assessment).all()  # NO TENANT FILTER!
   
   # After: automatic tenant filtering
   @app.get("/api/assessments")
   async def list_assessments(repo: AssessmentRepository = Depends()):
       return await repo.list_all()  # Automatically filtered by tenant
   
   # Or explicit filtering:
   @app.get("/api/assessments")
   async def list_assessments(db: Session = Depends(get_db)):
       tenant_id = get_tenant_id()
       return db.query(Assessment).filter(
           Assessment.tenant_id == tenant_id
       ).all()
   ```

TESTING STRATEGY:

1. **test_multitenancy.py**: Verify isolation
   ```python
   import pytest
   from fastapi.testclient import TestClient
   
   @pytest.mark.asyncio
   async def test_cannot_access_other_tenant_data():
       # Create two tenants
       tenant_a = await create_tenant('tenant-a')
       tenant_b = await create_tenant('tenant-b')
       
       # Create assessment in tenant-a
       assessment_a = await create_assessment(
           tenant_id='tenant-a',
           title='Assessment A'
       )
       
       # Try to access from tenant-b
       response = client.get(
           f'/api/assessments/{assessment_a.id}',
           headers={'X-Tenant-ID': 'tenant-b'}
       )
       
       assert response.status_code == 403  # Forbidden
   
   @pytest.mark.asyncio
   async def test_cannot_impersonate_other_user():
       # Create user
       user = await create_user('user@acme.com', role='analyst')
       
       # Try to act as user from different tenant
       response = client.get(
           '/api/dashboard',
           headers={
               'X-Tenant-ID': 'tenant-a',
               'Authorization': f'Bearer {create_jwt(user_id="other_user", tenant_id="tenant-b")}'
           }
       )
       
       assert response.status_code == 403  # User not member of tenant-a
   
   @pytest.mark.asyncio
   async def test_audit_logs_record_access():
       # Access data
       response = client.get(
           '/api/assessments',
           headers={'X-Tenant-ID': 'tenant-a'}
       )
       
       # Verify audit log created
       logs = await access_log_repo.get_for_user('tenant-a', 'user@acme.com')
       assert len(logs) > 0
       assert logs[0].method == 'GET'
       assert logs[0].path == '/api/assessments'
   ```

INTEGRATION CHECKLIST:

✅ Add middleware to app.add_middleware()
✅ Update all repositories to inherit from TenantScopedRepository
✅ Add @require_permission() decorator to endpoints
✅ Create Tenant + TenantMembership entities in DB
✅ Update all queries to include tenant_id filter
✅ Add audit logging middleware
✅ Create audit tables in database
✅ Test inter-tenant isolation
✅ Document multi-tenancy architecture

DEPLOYMENT CHECKLIST:

✅ Migrate database schema (Alembic)
✅ Create seed tenants in prod
✅ Update environment variables (DATABASE_URL with PostgreSQL)
✅ Test subdomain routing
✅ Test header-based tenant extraction
✅ Monitor audit logs for suspicious access patterns
✅ Set up tenant onboarding workflow
```

---

## ACCEPTANCE CRITERIA

- [ ] All requests include tenant context (header or subdomain)
- [ ] Middleware validates user membership in tenant
- [ ] All queries automatically filtered by tenant_id
- [ ] Cross-tenant access attempts return 403
- [ ] Audit logs record all data access with user + tenant
- [ ] Tests verify zero inter-tenant data leakage
- [ ] Performance impact < 10ms per request
- [ ] Backward compatibility maintained

---

## NEXT STEPS AFTER MODULE 2

Once multi-tenancy is solid, MODULE 3 (Event-Driven Architecture) can:
- Emit events with tenant context
- Process events per-tenant (no cross-tenant contamination)
- Use tenant context in event handlers

