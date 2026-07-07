from core.repositories.risk_repository import RiskRepository
from core.models.risks import Risk

class RiskService:
    def __init__(self, risk_repo: RiskRepository):
        self.risk_repo = risk_repo
        
    def calculate_risk_score(self, severity: str, probability: str) -> float:
        severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        prob_map = {'rare': 1, 'unlikely': 2, 'possible': 3, 'likely': 4, 'almost_certain': 5}
        
        sev_val = severity_map.get(str(severity).lower(), 1)
        prob_val = prob_map.get(str(probability).lower(), 1)
        
        return float(sev_val * prob_val * 5)
        
    async def create_risk(self, tenant_id: str, title: str, severity: str, probability: str, **kwargs) -> Risk:
        score = self.calculate_risk_score(severity, probability)
        risk = Risk(
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            probability=probability,
            risk_score=score,
            **kwargs
        )
        return await self.risk_repo.create(risk)
