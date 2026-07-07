from core.repositories.tenant_repository import TenantScopedRepository
from core.models.risks import Risk
from sqlalchemy.orm import Session

class RiskRepository(TenantScopedRepository[Risk]):
    def __init__(self, db: Session):
        super().__init__(db, Risk)
