import functools
from core.audit.audit_service import AuditService
from core.context.tenant_context import get_current_tenant

def audit_log(entity_type: str, action: str):
    """Decorator to automatically log function calls"""
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get before state if available
            before_state = kwargs.get('previous_state')
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Get after state
            after_state = kwargs.get('new_state') or result
            
            # Log to audit trail
            db = kwargs.get('db')
            if db:
                audit_service = AuditService(db)
                tenant = get_current_tenant()
                user_id = tenant.user_id if tenant else "system"
                
                entity_id = kwargs.get('entity_id') or kwargs.get('assessment_id')
                if not entity_id and hasattr(result, 'id'):
                    entity_id = result.id
                elif not entity_id and isinstance(result, dict) and 'id' in result:
                    entity_id = result['id']
                elif not entity_id and isinstance(result, dict) and 'assessment_id' in result:
                    entity_id = result['assessment_id']
                    
                await audit_service.log_change(
                    action=action,
                    entity_type=entity_type,
                    entity_id=str(entity_id) if entity_id else "unknown",
                    previous_state=before_state,
                    new_state=after_state,
                    user_id=user_id,
                    reason=kwargs.get('reason')
                )
            
            return result
        
        return wrapper
    
    return decorator
