import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base
from core.models.assets import System
from core.repositories.system_repository import SystemRepository

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
async def test_system_repository_crud(db_session):
    repo = SystemRepository(db_session)
    
    # Create
    system = System(
        tenant_id="tenant_x",
        name="Rep System",
        risk_classification="medium"
    )
    created = await repo.create(system)
    assert created.id is not None
    
    # Get by ID
    fetched = await repo.get_by_id(created.id)
    assert fetched.name == "Rep System"
    
    # Get by Tenant
    tenant_list = await repo.get_by_tenant("tenant_x")
    assert len(tenant_list) == 1
    
    # Update
    updated = await repo.update(created.id, name="Updated Rep System")
    assert updated.name == "Updated Rep System"
    
    # Delete
    await repo.delete(created.id)
    deleted = await repo.get_by_id(created.id)
    assert deleted is None
