from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from core.models.audit import AccessLog

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session_factory):
        super().__init__(app)
        self.db_session_factory = db_session_factory

    async def dispatch(self, request: Request, call_next):
        # Record request start
        start_time = datetime.utcnow()
        
        # Process request
        response = await call_next(request)
        
        # Record request end
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Extract tenant and user directly from request headers to avoid ContextVar propagation issues
        tenant_id = request.headers.get('X-Tenant-ID') or "default"
        
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            user_id = auth_header[7:]
        else:
            user_id = request.headers.get('X-User-ID') or request.cookies.get('user_id') or "user_expert"
            
        # Ignore docs/openapi/public assets from noise logging
        if request.url.path.startswith('/docs') or request.url.path.startswith('/openapi.json'):
            return response
            
        db = self.db_session_factory()
        try:
            log = AccessLog(
                tenant_id=tenant_id,
                user_id=user_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get('User-Agent'),
                created_at=start_time
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"[AuditLoggingMiddleware] Failed to log request: {e}")
        finally:
            db.close()
            
        return response
