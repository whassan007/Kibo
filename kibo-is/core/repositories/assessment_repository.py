from core.repositories.tenant_repository import TenantScopedRepository
from core.models.assessments import Assessment
from sqlalchemy.orm import Session

class AssessmentRepository(TenantScopedRepository[Assessment]):
    def __init__(self, db: Session):
        super().__init__(db, Assessment)
