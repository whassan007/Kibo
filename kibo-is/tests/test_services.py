import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base
from core.repositories.risk_repository import RiskRepository
from core.repositories.assessment_repository import AssessmentRepository
from core.repositories.control_repository import ControlRepository
from core.services.risk_service import RiskService
from core.services.assessment_service import AssessmentService
from core.services.control_service import ControlService
from core.models.controls import Control

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.asyncio
async def test_risk_service_calculations(db_session):
    risk_repo = RiskRepository(db_session)
    risk_service = RiskService(risk_repo)
    
    risk = await risk_service.create_risk(
        tenant_id="test_tenant",
        title="Database Breach",
        severity="critical",
        probability="likely"
    )
    
    # 4 (critical) * 4 (likely) * 5 = 80
    assert risk.risk_score == 80.0

@pytest.mark.asyncio
async def test_assessment_chains_risk_creation(db_session):
    risk_repo = RiskRepository(db_session)
    risk_service = RiskService(risk_repo)
    assessment_repo = AssessmentRepository(db_session)
    assessment_service = AssessmentService(assessment_repo, risk_service)
    
    # Create high risk assessment (risk_score = 7.5 > 5.0)
    assessment = await assessment_service.create_assessment(
        tenant_id="test_tenant",
        assessment_type="pia",
        title="High Risk PIA",
        risk_score=7.5
    )
    
    assert assessment.id is not None
    
    # Verify that a Risk was automatically generated and saved
    risks = await risk_repo.get_by_tenant("test_tenant")
    assert len(risks) == 1
    assert risks[0].source_assessment_id == assessment.id
    assert "High Risk from Assessment" in risks[0].title

@pytest.mark.asyncio
async def test_control_effectiveness_update(db_session):
    control_repo = ControlRepository(db_session)
    control_service = ControlService(control_repo)
    
    control = Control(
        tenant_id="test_tenant",
        title="Encryption at Rest",
        effectiveness_rating="not_assessed"
    )
    db_session.add(control)
    db_session.commit()
    
    updated = await control_service.update_effectiveness(
        control.id,
        rating="effective",
        test_result={"status": "pass", "auditor": "Wael"}
    )
    
    assert updated.effectiveness_rating == "effective"
    assert len(updated.test_results) == 1
    assert updated.test_results[0]["status"] == "pass"
