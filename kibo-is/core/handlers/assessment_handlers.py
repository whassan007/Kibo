import json
from uuid import uuid4
from datetime import datetime
from typing import Any
from sqlalchemy.orm import Session
from core.models.assessments import Assessment
from core.models.risks import Risk
from core.events.domain_events import AssessmentApproved, RiskCreated
from core.context.tenant_context import set_tenant_context, TenantContext

class AssessmentHandlers:
    def __init__(self, db_session_factory, event_bus):
        self.db_session_factory = db_session_factory
        self.event_bus = event_bus
    
    async def on_assessment_approved(self, event: Any):
        # Convert dictionary to AssessmentApproved if it was published as dict
        if isinstance(event, dict):
            # Resolve dataclass constructor from dict payload
            payload = event.copy()
            if 'timestamp' in payload and isinstance(payload['timestamp'], str):
                payload['timestamp'] = datetime.fromisoformat(payload['timestamp'])
            # Remove keys that aren't fields of AssessmentApproved if any
            event = AssessmentApproved(**payload)
            
        # Set tenant context from event
        context = TenantContext(
            tenant_id=event.tenant_id,
            tenant_name=f"{event.tenant_id.capitalize()} Tenant",
            user_id=event.approved_by or "system",
            user_role="dpo",
            is_admin=True
        )
        set_tenant_context(context)
        
        db = self.db_session_factory()
        try:
            # If risk score is high, create Risk entry
            if event.risk_score >= 7.0:
                risk = Risk(
                    id=str(uuid4()),
                    tenant_id=event.tenant_id,
                    title=f"Risk from assessment: {event.aggregate_id}",
                    description=event.findings or f"High risk found during assessment {event.aggregate_id}",
                    severity=self._score_to_severity(event.risk_score),
                    risk_score=event.risk_score,
                    source_assessment_id=event.aggregate_id,
                    risk_owner=event.approved_by or "dpo",
                    status='open',
                    probability='possible',
                    residual_risk_score=event.risk_score
                )
                
                db.add(risk)
                db.commit()
                db.refresh(risk)
                
                # Emit RiskCreated event
                risk_event = RiskCreated(
                    tenant_id=event.tenant_id,
                    aggregate_id=risk.id,
                    aggregate_type='Risk',
                    title=risk.title,
                    severity=risk.severity,
                    source_assessment_id=event.aggregate_id,
                    risk_score=event.risk_score,
                    mitigation_required=True,
                    user_id=event.approved_by,
                    timestamp=datetime.utcnow()
                )
                await self.event_bus.publish(risk_event)
        finally:
            db.close()
            
    def _score_to_severity(self, score: float) -> str:
        if score >= 9.0:
            return 'critical'
        elif score >= 7.0:
            return 'high'
        elif score >= 5.0:
            return 'medium'
        else:
            return 'low'

def register_assessment_handlers(event_bus, db_session_factory):
    handlers = AssessmentHandlers(db_session_factory, event_bus)
    event_bus.subscribe('AssessmentApproved', handlers.on_assessment_approved)
