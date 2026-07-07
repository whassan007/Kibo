from typing import Generic, TypeVar, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model_class: type[T]):
        self.db = db
        self.model_class = model_class
        
    async def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
        
    async def get_by_id(self, obj_id: str) -> Optional[T]:
        return self.db.get(self.model_class, obj_id)
        
    async def get_by_tenant(self, tenant_id: str) -> List[T]:
        stmt = select(self.model_class).where(self.model_class.tenant_id == tenant_id)
        result = self.db.execute(stmt)
        return result.scalars().all()
        
    async def update(self, obj_id: str, **kwargs) -> T:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj
        
    async def delete(self, obj_id: str) -> None:
        obj = await self.get_by_id(obj_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
