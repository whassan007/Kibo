import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.context.tenant_context import set_tenant_id, set_current_tenant, Tenant
from core.audit.audit_service import AuditService

class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session_factory):
        super().__init__(app)
        self.db_session_factory = db_session_factory
        
    async def dispatch(self, request: Request, call_next):
        # Extract tenant ID from headers
        tenant_id = request.headers.get("X-Tenant-ID") or "default"
        set_tenant_id(tenant_id)
        
        # Extract user information from authorization header
        auth_header = request.headers.get("Authorization")
        user_id = "anonymous"
        user_role = "PUBLIC"
        if auth_header and auth_header.startswith("Bearer "):
            role = auth_header.split(" ")[1].upper()
            user_id = f"user_{role.lower()}"
            user_role = role
        elif not auth_header:
            # Fallback default for testing (matches agent_gateway default role)
            user_id = "user_cpo"
            user_role = "CPO"
            
        tenant = Tenant(
            id=tenant_id,
            name=f"{tenant_id.capitalize()} Tenant",
            user_id=user_id,
            role=user_role
        )
        set_current_tenant(tenant)
        
        # Proceed with request
        response = await call_next(request)
        
        # If request is a read request to a sensitive entity, log it to DataAccessLog
        if request.method == "GET":
            db = self.db_session_factory()
            try:
                # Regex match for assessments and transactions
                path = request.url.path
                match_tx = re.match(r"/api/transactions/([^/]+)$", path)
                match_assessment = re.match(r"/api/assessments/([^/]+)$", path)
                match_risk = re.match(r"/api/risks/([^/]+)$", path)
                
                entity_type = None
                entity_id = None
                
                if match_tx:
                    entity_type = "Transaction"
                    entity_id = match_tx.group(1)
                elif match_assessment:
                    entity_type = "Assessment"
                    entity_id = match_assessment.group(1)
                elif match_risk:
                    entity_type = "Risk"
                    entity_id = match_risk.group(1)
                    
                if entity_type and entity_id and not entity_id.startswith("trail") and not entity_id.startswith("version"):
                    service = AuditService(db)
                    await service.log_data_access(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        action="READ",
                        user_id=user_id,
                        reason="API_GET_REQUEST",
                        ip_address=request.client.host if request.client else None,
                        endpoint=path
                    )
            except Exception as e:
                # Log print for debugging, but don't crash the request
                print(f"Error in audit middleware logging: {e}")
            finally:
                db.close()
                
        return response
