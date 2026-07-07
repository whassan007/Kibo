from core.repositories.tenant_repository import TenantScopedRepository
from core.models.assets import Vendor
from sqlalchemy.orm import Session

class VendorRepository(TenantScopedRepository[Vendor]):
    def __init__(self, db: Session):
        super().__init__(db, Vendor)
