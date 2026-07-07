from core.repositories.tenant_repository import TenantScopedRepository
from core.models.assets import System
from sqlalchemy.orm import Session

class SystemRepository(TenantScopedRepository[System]):
    def __init__(self, db: Session):
        super().__init__(db, System)
