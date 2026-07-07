from core.repositories.assessment_repository import AssessmentRepository
from core.services.risk_service import RiskService
from core.models.assessments import PIAssessment, DPIAssessment, TIAssessment

class AssessmentService:
    def __init__(self, assessment_repo: AssessmentRepository, risk_service: RiskService = None):
        self.assessment_repo = assessment_repo
        self.risk_service = risk_service
        
    async def create_assessment(self, tenant_id: str, assessment_type: str, title: str, **kwargs) -> any:
        if assessment_type == 'pia':
            assessment = PIAssessment(tenant_id=tenant_id, title=title, **kwargs)
        elif assessment_type == 'dpia':
            assessment = DPIAssessment(tenant_id=tenant_id, title=title, **kwargs)
        elif assessment_type == 'tia':
            assessment = TIAssessment(tenant_id=tenant_id, title=title, **kwargs)
        else:
            raise ValueError(f"Unknown assessment type: {assessment_type}")
            
        created = await self.assessment_repo.create(assessment)
        
        # If there's an associated risk score or critical status, automatically trigger risk creation
        if created.risk_score and created.risk_score > 5.0 and self.risk_service:
            await self.risk_service.create_risk(
                tenant_id=tenant_id,
                title=f"High Risk from Assessment: {title}",
                severity="high",
                probability="possible",
                source_assessment_id=created.id
            )
            
        return created
