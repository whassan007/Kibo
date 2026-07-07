import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base
from core.models.assets import System, Vendor, DataElement, Process
from core.models.assessments import PIAssessment, DPIAssessment
from core.models.risks import Risk
from core.models.controls import Control
from core.models.contracts import Jurisdiction, Contract

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

def test_create_system_and_relationships(db_session):
    # Create system
    system = System(
        tenant_id="test_tenant",
        name="Primary HR DB",
        description="Stores HR payroll records",
        data_categories=["PersonalInformation", "BiometricData"],
        processing_activities=["Storage", "Access"],
        jurisdiction="Quebec",
        risk_classification="high",
        storage_location="US-East",
        encryption_method="AES-256"
    )
    db_session.add(system)
    db_session.commit()
    
    assert system.id is not None
    assert system.name == "Primary HR DB"
    assert system.asset_type == "system"

def test_create_vendor_and_contract(db_session):
    vendor = Vendor(
        tenant_id="test_tenant",
        name="SecureCloud Inc",
        country_of_origin="Canada",
        dpa_status="executed",
        soc2_type="type_ii"
    )
    db_session.add(vendor)
    db_session.commit()
    
    contract = Contract(
        tenant_id="test_tenant",
        vendor_id=vendor.id,
        contract_type="DPA",
        has_dpa=True
    )
    db_session.add(contract)
    db_session.commit()
    
    assert len(vendor.contracts) == 1
    assert vendor.contracts[0].contract_type == "DPA"
