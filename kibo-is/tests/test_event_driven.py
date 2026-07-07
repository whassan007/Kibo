import pytest
import os
import sys
import asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.events.domain_events import AssessmentApproved, ControlImplemented
from core.events.event_bus import InMemoryEventBus
from core.handlers.assessment_handlers import AssessmentHandlers
from core.handlers.risk_handlers import RiskHandlers
from core.models.base import Base
from core.models.risks import Risk
from core.models.controls import Control
from core.models.associations import risk_control

@pytest.fixture(scope="function")
def test_db_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory

@pytest.mark.asyncio
async def test_assessment_approved_creates_risk(test_db_factory):
    event_bus = InMemoryEventBus()
    handlers = AssessmentHandlers(test_db_factory, event_bus)
    await event_bus.subscribe('AssessmentApproved', handlers.on_assessment_approved)

    # 1. Publish AssessmentApproved event
    assessment_id = f"PIA-{str(uuid4())[:6].upper()}"
    event = AssessmentApproved(
        tenant_id='test-tenant',
        aggregate_id=assessment_id,
        aggregate_type='Assessment',
        approved_by='dpo_user',
        risk_score=8.5,
        findings='High risk found',
        timestamp=datetime.utcnow()
    )
    
    await event_bus.publish(event)
    
    # Allow background handlers to complete
    await asyncio.sleep(0.1)
    
    # 2. Verify Risk was created in DB
    db = test_db_factory()
    try:
        risks = db.query(Risk).filter_by(tenant_id='test-tenant', source_assessment_id=assessment_id).all()
        assert len(risks) == 1
        assert risks[0].risk_score == 8.5
        assert risks[0].status == 'open'
        assert risks[0].severity == 'high'
    finally:
        db.close()

@pytest.mark.asyncio
async def test_control_implementation_updates_risk(test_db_factory):
    event_bus = InMemoryEventBus()
    handlers = RiskHandlers(test_db_factory, event_bus)
    await event_bus.subscribe('ControlImplemented', handlers.on_control_implemented)

    db = test_db_factory()
    try:
        # 1. Create a Risk
        risk = Risk(
            id=str(uuid4()),
            tenant_id='test-tenant',
            title='Insecure Storage',
            description='Storage is unencrypted',
            severity='high',
            risk_score=8.0,
            status='open',
            probability='possible',
            residual_risk_score=8.0
        )
        db.add(risk)
        
        # 2. Create a Control
        control = Control(
            id=str(uuid4()),
            tenant_id='test-tenant',
            title='AES-256 Encryption',
            effectiveness_rating='effective',  # 0.9 reduction
            implementation_status='implemented'
        )
        db.add(control)
        db.commit()
        
        # 3. Link them in the join table
        db.execute(risk_control.insert().values(risk_id=risk.id, control_id=control.id))
        db.commit()
        
        # 4. Emit ControlImplemented event
        event = ControlImplemented(
            tenant_id='test-tenant',
            aggregate_id=control.id,
            aggregate_type='Control',
            control_id=control.id,
            timestamp=datetime.utcnow()
        )
        
        await event_bus.publish(event)
        
        # Allow handlers to run
        await asyncio.sleep(0.1)
        
        # 5. Verify Risk status is mitigated and residual risk is calculated
        db_check = test_db_factory()
        try:
            fetched_risk = db_check.get(Risk, risk.id)
            assert fetched_risk.status == 'mitigated'
            # Residual risk = 8.0 * (1 - 0.9) = 0.8
            assert fetched_risk.residual_risk_score == pytest.approx(0.8)
        finally:
            db_check.close()
            
    finally:
        db.close()
