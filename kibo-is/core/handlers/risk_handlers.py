import json
from uuid import uuid4
from datetime import datetime
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.models.risks import Risk
from core.models.controls import Control
from core.events.domain_events import ControlImplemented, RiskStatusChanged
from core.context.tenant_context import set_tenant_context, TenantContext

class RiskHandlers:
    def __init__(self, db_session_factory, event_bus):
        self.db_session_factory = db_session_factory
        self.event_bus = event_bus
        
    async def on_control_implemented(self, event: Any):
        if isinstance(event, dict):
            payload = event.copy()
            if 'timestamp' in payload and isinstance(payload['timestamp'], str):
                payload['timestamp'] = datetime.fromisoformat(payload['timestamp'])
            if 'implementation_date' in payload and isinstance(payload['implementation_date'], str):
                payload['implementation_date'] = datetime.fromisoformat(payload['implementation_date'])
            event = ControlImplemented(**payload)
            
        context = TenantContext(
            tenant_id=event.tenant_id,
            tenant_name=f"{event.tenant_id.capitalize()} Tenant",
            user_id="system",
            user_role="dpo",
            is_admin=True
        )
        set_tenant_context(context)
        
        db = self.db_session_factory()
        try:
            # Get control
            control = db.get(Control, event.control_id)
            if not control:
                print(f"[RiskHandlers] Control {event.control_id} not found")
                return
                
            # Find all risks that this control mitigates.
            from core.models.associations import risk_control
            stmt = select(Risk).join(
                risk_control, risk_control.c.risk_id == Risk.id
            ).where(
                risk_control.c.control_id == event.control_id,
                Risk.tenant_id == event.tenant_id
            )
            
            result = db.execute(stmt)
            risks = result.scalars().all()
            
            for risk in risks:
                old_status = risk.status
                new_residual_score = self._calculate_residual_risk(risk, control)
                risk.residual_risk_score = new_residual_score
                
                tolerance = getattr(risk, 'risk_tolerance', 4.0) or 4.0
                if new_residual_score <= tolerance:
                    risk.status = 'mitigated'
                else:
                    risk.status = 'partially_mitigated'
                    
                db.add(risk)
                
                if risk.status != old_status:
                    status_event = RiskStatusChanged(
                        tenant_id=event.tenant_id,
                        aggregate_id=risk.id,
                        aggregate_type='Risk',
                        new_status=risk.status,
                        old_status=old_status,
                        reason=f"Control {control.title} implemented",
                        timestamp=datetime.utcnow()
                    )
                    await self.event_bus.publish(status_event)
                    
            db.commit()
        finally:
            db.close()
            
    def _calculate_residual_risk(self, risk: Risk, control: Control) -> float:
        control_effectiveness = self._get_control_effectiveness(control)
        return risk.risk_score * (1 - control_effectiveness)
        
    def _get_control_effectiveness(self, control: Control) -> float:
        effectiveness_map = {
            'not_assessed': 0.0,
            'ineffective': 0.1,
            'partially_effective': 0.5,
            'effective': 0.9
        }
        return effectiveness_map.get(control.effectiveness_rating, 0.0)

def register_risk_handlers(event_bus, db_session_factory):
    handlers = RiskHandlers(db_session_factory, event_bus)
    event_bus.subscribe('ControlImplemented', handlers.on_control_implemented)
