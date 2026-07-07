from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.models.audit_log import EntityVersion, AuditLog

class TemporalQuery:
    def __init__(self, db: Session):
        self.db = db
        
    async def get_entity_as_of(
        self,
        entity_type: str,
        entity_id: str,
        as_of: datetime
    ) -> Optional[dict]:
        """Get entity state at specific point in time"""
        stmt = select(EntityVersion).where(
            EntityVersion.entity_type == entity_type,
            EntityVersion.entity_id == str(entity_id),
            EntityVersion.created_at <= as_of
        ).order_by(EntityVersion.created_at.desc()).limit(1)
        
        result = self.db.execute(stmt)
        version = result.scalar_one_or_none()
        return version.snapshot if version else None
        
    async def get_change_history(
        self,
        entity_type: str,
        entity_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[dict]:
        """Get change history between dates"""
        stmt = select(AuditLog).where(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == str(entity_id)
        )
        
        if start_date:
            stmt = stmt.where(AuditLog.created_at >= start_date)
        if end_date:
            stmt = stmt.where(AuditLog.created_at <= end_date)
            
        stmt = stmt.order_by(AuditLog.created_at.asc())
        result = self.db.execute(stmt)
        logs = result.scalars().all()
        
        return [
            {
                'timestamp': log.created_at,
                'user': log.user_id,
                'action': log.action,
                'changes': log.changes,
                'reason': log.reason
            }
            for log in logs
        ]
