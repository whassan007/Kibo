from core.repositories.tenant_repository import TenantScopedRepository
from core.models.controls import Control
from sqlalchemy.orm import Session

class ControlRepository(TenantScopedRepository[Control]):
    def __init__(self, db: Session):
        super().__init__(db, Control)
