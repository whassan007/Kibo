from typing import TypeVar, Optional, List
from fastapi import HTTPException
from sqlalchemy import select
from core.repositories.base_repository import BaseRepository, T
from core.context.tenant_context import get_tenant_id
from core.models.tenant import Tenant, TenantMembership

class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, db):
        super().__init__(db, Tenant)
        
    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
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
        result = self.db.execute(stmt)
        return result.scalars().all()

class TenantScopedRepository(BaseRepository[T]):
    """Base repository that automatically filters by tenant"""
    
    async def get_by_id(self, obj_id: str) -> Optional[T]:
        from core.context.tenant_context import _tenant_context
        if _tenant_context.get() is None:
            # Bypass filtering if no tenant context is set (e.g. in standalone unit tests)
            return await super().get_by_id(obj_id)
            
        tenant_id = get_tenant_id()
        stmt = select(self.model_class).where(
            self.model_class.id == obj_id,
            self.model_class.tenant_id == tenant_id
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def list_all(self) -> List[T]:
        from core.context.tenant_context import _tenant_context
        if _tenant_context.get() is None:
            # Bypass filtering if no tenant context is set (e.g. in standalone unit tests)
            return await super().list_all()
            
        tenant_id = get_tenant_id()
        stmt = select(self.model_class).where(
            self.model_class.tenant_id == tenant_id
        )
        result = self.db.execute(stmt)
        return result.scalars().all()
