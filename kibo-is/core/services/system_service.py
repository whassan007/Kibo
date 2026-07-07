from core.repositories.system_repository import SystemRepository
from core.models.assets import System

class SystemService:
    def __init__(self, system_repo: SystemRepository):
        self.system_repo = system_repo
        
    async def create_system(self, tenant_id: str, name: str, risk_classification: str = 'medium', **kwargs) -> System:
        system = System(
            tenant_id=tenant_id,
            name=name,
            risk_classification=risk_classification,
            **kwargs
        )
        return await self.system_repo.create(system)
