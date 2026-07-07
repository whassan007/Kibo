from datetime import datetime
from hashlib import sha256
import json
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.models.audit_log import AuditLog, EntityVersion, DataAccessLog, generate_uuid_str
from core.context.tenant_context import get_tenant_id, get_current_tenant
from core.audit.change_tracker import calculate_diff

class AuditService:
    def __init__(self, db: Session):
        self.db = db
        
    async def log_change(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        previous_state: dict = None,
        new_state: dict = None,
        user_id: str = None,
        reason: str = None,
        context: dict = None,
        timestamp: datetime = None
    ) -> AuditLog:
        """Log a change to the audit trail (append-only)"""
        tenant_id = get_tenant_id()
        
        # Calculate diff
        changes = calculate_diff(previous_state, new_state)
        
        tenant = get_current_tenant()
        user_email = tenant.name if tenant else None
        user_role = tenant.role if tenant else None
        if not user_id and tenant:
            user_id = tenant.user_id
            
        log_time = timestamp or datetime.utcnow()
            
        log = AuditLog(
            id=generate_uuid_str(),
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            previous_state=previous_state,
            new_state=new_state,
            changes=changes,
            reason=reason,
            change_context=context or {},
            created_at=log_time
        )
        
        # Get previous audit log for hash chain
        previous_log = await self._get_previous_audit_log(entity_type, entity_id)
        if previous_log:
            log.previous_hash = previous_log.change_hash
            
        # Calculate hash
        log.change_hash = self._calculate_hash(log)
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        # Create entity version snapshot
        if new_state:
            next_version = await self._get_next_version(entity_type, entity_id)
            version = EntityVersion(
                id=generate_uuid_str(),
                tenant_id=tenant_id,
                entity_type=entity_type,
                entity_id=str(entity_id),
                version=next_version,
                snapshot=new_state,
                created_by=user_id,
                reason=reason,
                created_at=log_time
            )
            self.db.add(version)
            self.db.commit()
            
        return log
        
    async def log_data_access(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: str,
        record_count: int = 1,
        reason: str = None,
        ip_address: str = None,
        endpoint: str = None
    ) -> DataAccessLog:
        """Log who accessed what data"""
        tenant_id = get_tenant_id()
        tenant = get_current_tenant()
        user_email = tenant.name if tenant else None
        
        log = DataAccessLog(
            id=generate_uuid_str(),
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            entity_type=entity_type,
            entity_id=str(entity_id),
            action=action,
            record_count=record_count,
            access_reason=reason,
            ip_address=ip_address,
            endpoint=endpoint,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
        
    async def get_entity_audit_trail(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit trail for specific entity"""
        tenant_id = get_tenant_id()
        stmt = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == str(entity_id)
        ).order_by(AuditLog.created_at.desc()).limit(limit)
        
        result = self.db.execute(stmt)
        return result.scalars().all()
        
    async def get_entity_state_at_time(
        self,
        entity_type: str,
        entity_id: str,
        as_of: datetime
    ) -> Optional[dict]:
        """Get entity state as it was at specific point in time"""
        tenant_id = get_tenant_id()
        
        stmt = select(EntityVersion).where(
            EntityVersion.tenant_id == tenant_id,
            EntityVersion.entity_type == entity_type,
            EntityVersion.entity_id == str(entity_id),
            EntityVersion.created_at <= as_of
        ).order_by(EntityVersion.created_at.desc()).limit(1)
        
        result = self.db.execute(stmt)
        version = result.scalar_one_or_none()
        return version.snapshot if version else None
        
    async def verify_integrity(self, audit_log_id: str) -> bool:
        """Verify audit log hasn't been tampered with"""
        log = self.db.get(AuditLog, audit_log_id)
        if not log:
            return False
            
        calculated_hash = self._calculate_hash(log)
        return calculated_hash == log.change_hash
        
    def _calculate_hash(self, log: AuditLog) -> str:
        """Calculate SHA256 hash for integrity checking"""
        data = {
            'id': str(log.id),
            'tenant_id': log.tenant_id,
            'action': log.action,
            'entity_type': log.entity_type,
            'entity_id': str(log.entity_id),
            'changes': log.changes,
            'created_at': log.created_at.isoformat() if isinstance(log.created_at, datetime) else str(log.created_at),
            'previous_hash': log.previous_hash or ''
        }
        json_str = json.dumps(data, sort_keys=True)
        return sha256(json_str.encode()).hexdigest()
        
    async def _get_previous_audit_log(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[AuditLog]:
        """Get the most recent audit log for this entity"""
        tenant_id = get_tenant_id()
        stmt = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == str(entity_id)
        ).order_by(AuditLog.created_at.desc()).limit(1)
        
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def _get_next_version(
        self,
        entity_type: str,
        entity_id: str
    ) -> int:
        """Get next version number for entity"""
        tenant_id = get_tenant_id()
        stmt = select(EntityVersion.version).where(
            EntityVersion.tenant_id == tenant_id,
            EntityVersion.entity_type == entity_type,
            EntityVersion.entity_id == str(entity_id)
        ).order_by(EntityVersion.version.desc()).limit(1)
        
        result = self.db.execute(stmt)
        last_version = result.scalar()
        return (last_version or 0) + 1
