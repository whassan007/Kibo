from core.repositories.control_repository import ControlRepository
from core.models.controls import Control

class ControlService:
    def __init__(self, control_repo: ControlRepository):
        self.control_repo = control_repo
        
    async def update_effectiveness(self, control_id: str, rating: str, test_result: dict = None) -> Control:
        control = await self.control_repo.get_by_id(control_id)
        if not control:
            raise ValueError(f"Control not found: {control_id}")
            
        control.effectiveness_rating = rating
        if test_result:
            results = list(control.test_results or [])
            results.append(test_result)
            control.test_results = results
            
        await self.control_repo.update(
            control_id,
            effectiveness_rating=control.effectiveness_rating,
            test_results=control.test_results
        )
        return control
