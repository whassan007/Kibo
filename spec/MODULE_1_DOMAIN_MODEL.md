# MODULE 1: UNIFIED DOMAIN MODEL REFACTORING
## For Antigravity IDE + Gemma4

**Duration:** 8 weeks  
**Priority:** CRITICAL  
**Effort:** High  
**Dependencies:** None (foundational)

---

## OVERVIEW

Replace scattered Pydantic models with unified domain-driven design architecture. Create semantic entity graph connecting Assets → Systems → Vendors → Risks → Controls → Assessments.

**Current State:**
- Entities scattered across `agent_gateway.py`
- No relationships between models
- Data flows are hardcoded
- Ontology read-only

**Target State:**
- Normalized SQLAlchemy ORM models
- Domain relationships explicit
- Entity queries unified
- Foundation for multi-tenancy

---

## MODULE OBJECTIVES

1. ✅ Create base entity classes (VersionedEntity, TenantScoped)
2. ✅ Implement core domain entities (System, Vendor, Process, DataElement, Risk, Control, Assessment)
3. ✅ Build relationship mappings
4. ✅ Create repository pattern for consistent queries
5. ✅ Migrate seed data to new schema
6. ✅ Write comprehensive tests

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building the domain model for KIBO, a privacy compliance platform.

TASK: Create a unified domain model using SQLAlchemy that replaces scattered Pydantic models with a coherent entity graph.

REQUIREMENTS:
1. Database: PostgreSQL (use connection string from env var: DATABASE_URL)
2. ORM: SQLAlchemy 2.0 with async support
3. Style: Domain-Driven Design (entities > repositories > services)
4. Patterns: Base classes, mixins, relationships, constraints

ENTITIES TO CREATE:

1. Base Classes (in core/models/base.py):
   - VersionedEntity: Abstract base with id, version, created_at, updated_at, created_by, updated_by
   - TenantScoped: Mixin that adds tenant_id to all entities
   - Timestamped: Mixin with created_at, updated_at

2. Core Entities (in core/models/):

   Asset (abstract):
   - id (UUID, PK)
   - asset_type (string: "System", "Vendor", "Process")
   - tenant_id (FK to Tenant)
   - name, description
   - owner_id (FK to User)
   - created_at, updated_at

   System (extends Asset):
   - asset_type = "System"
   - data_categories (JSON: [PersonalInformation, PHI, BiometricData, ...])
   - processing_activities (JSON: [Collection, Storage, Transfer, AI_Training, ...])
   - jurisdiction (string: Ontario, Quebec, California, EU, ...)
   - risk_classification (string: low, medium, high, critical)
   - storage_location (string)
   - encryption_method (string: AES-256, TLS-1.3, etc.)
   - relationships:
     - processes_data_elements (many DataElement)
     - implements_controls (many Control)
     - subject_of_assessments (many Assessment)
     - triggers_risks (many Risk)

   Vendor (extends Asset):
   - asset_type = "Vendor"
   - service_description (text)
   - country_of_origin (string)
   - dpa_status (string: none, draft, executed, expired)
   - dpa_expiry_date (datetime, nullable)
   - soc2_type (string: none, type_i, type_ii)
   - cross_border (boolean)
   - relationships:
     - has_contracts (many Contract)
     - has_assessments (many Assessment)
     - has_risks (many Risk)
     - sub_processor_for (many DataProcessor)

   DataElement (extends Asset):
   - asset_type = "DataElement"
   - data_category (enum: PersonalInformation, PHI, ChildrensData, ...)
   - sensitivity (string: public, internal, confidential, restricted)
   - retention_days (integer)
   - stored_in (FK to System)
   - relationships:
     - processed_by (many Process)
     - flows_to (many DataElement, self-referential)

   Process (extends Asset):
   - asset_type = "Process"
   - process_type (string: collection, transfer, profiling, ai_training, etc.)
   - legal_basis (string: consent, contract, legal_obligation, vital_interests, public_task, legitimate_interest)
   - data_categories (JSON array)
   - activities (JSON array)
   - jurisdiction (string)
   - involves_children (boolean)
   - child_age_minimum (integer, nullable)
   - relationships:
     - processes_data_elements (many DataElement)
     - requires_assessments (many Assessment, polymorphic)
     - generates_risks (many Risk)
     - implements_controls (many Control)

   Assessment (abstract, extends VersionedEntity, TenantScoped):
   - assessment_type (string: PIA, DPIA, TIA, TRA, etc.) - discriminator
   - title, description
   - status (string: draft, in_review, approved, rejected, archived)
   - risk_score (float: 0-10)
   - legal_basis (string)
   - findings (text)
   - mitigations (JSON array)
   - assigned_to (FK to User)
   - submitted_at (datetime, nullable)
   - approved_at (datetime, nullable)
   - approved_by (FK to User, nullable)
   - relationships:
     - assesses_process (FK to Process)
     - sources_risks (many Risk)
     - recommends_controls (many Control)
     - linked_vendor (FK to Vendor, nullable)

   Risk (extends VersionedEntity, TenantScoped):
   - id, title, description
   - severity (string: low, medium, high, critical)
   - probability (string: rare, unlikely, possible, likely, almost_certain)
   - risk_score (float: 0-100) - calculated from severity + probability
   - residual_risk_score (float, nullable)
   - status (string: open, mitigated, accepted, rejected)
   - risk_owner (FK to User)
   - accepts_risk (FK to User, nullable)
   - risk_acceptance_date (datetime, nullable)
   - risk_acceptance_justification (text, nullable)
   - mitigation_deadline (datetime, nullable)
   - relationships:
     - sourced_from_assessment (FK to Assessment)
     - sourced_from_system (FK to System, nullable)
     - sourced_from_vendor (FK to Vendor, nullable)
     - mitigations (many Control)
     - affects_jurisdictions (many Jurisdiction via join table)

   Control (extends VersionedEntity, TenantScoped):
   - id, title, description
   - control_type (string: preventive, detective, corrective, compensating)
   - implementation_status (string: planned, in_progress, implemented, monitored, decommissioned)
   - effectiveness_rating (string: not_assessed, ineffective, partially_effective, effective)
   - control_owner (FK to User)
   - test_results (JSON array)
   - last_tested (datetime, nullable)
   - relationships:
     - mitigates_risks (many Risk)
     - implements_frameworks (many Framework)
     - implemented_in_systems (many System)
     - evidence (many ComplianceEvidence)

   Jurisdiction (simple table):
   - id, code (string, PK: Ontario, Quebec, California, EU, ...)
   - name (string)
   - primary_statute (string)
   - access_request_deadline_days (integer)

   Contract (extends VersionedEntity, TenantScoped):
   - id, vendor_id (FK to Vendor)
   - contract_type (string: DPA, SCC, Service Agreement, etc.)
   - effective_date, expiry_date
   - has_dpa (boolean)
   - has_scc (boolean)
   - cross_border_transfer (boolean)
   - relationships:
     - vendor (FK)
     - required_assessments (many Assessment)

3. Relationships (via SQLAlchemy relationship() + foreign keys):
   System:
     - processes_data_elements: one-to-many DataElement (system_id FK)
     - subject_of_assessments: one-to-many Assessment (assessed_system_id FK)
   
   Vendor:
     - has_contracts: one-to-many Contract (vendor_id FK)
     - has_assessments: one-to-many Assessment (vendor_id FK)
   
   Assessment:
     - assesses_process: many-to-one Process
     - sources_risks: one-to-many Risk (source_assessment_id FK)
   
   Risk:
     - mitigations: many-to-many Control (via risk_control association table)
     - affects_jurisdictions: many-to-many Jurisdiction (via risk_jurisdiction join table)

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # VersionedEntity, TenantScoped, Timestamped
│   │   ├── assets.py        # System, Vendor, DataElement, Process
│   │   ├── assessments.py   # Assessment (base + subclasses)
│   │   ├── risks.py         # Risk, RiskAcceptance
│   │   ├── controls.py      # Control, ControlTest
│   │   ├── contracts.py     # Contract, Jurisdiction
│   │   └── associations.py  # Join tables (risk_control, risk_jurisdiction, etc.)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py  # BaseRepository[T] with CRUD + filtering
│   │   ├── system_repository.py
│   │   ├── vendor_repository.py
│   │   ├── assessment_repository.py
│   │   ├── risk_repository.py
│   │   └── control_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── system_service.py
│   │   ├── assessment_service.py
│   │   ├── risk_service.py
│   │   └── control_service.py
│   └── schema.py            # Alembic migrations for DB schema
├── migrations/
│   └── versions/            # Alembic migration files
└── tests/
    ├── test_models.py
    ├── test_repositories.py
    └── test_services.py
```

IMPLEMENTATION DETAILS:

1. **base.py**: Define abstract base classes
   ```python
   from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
   from sqlalchemy.orm import declarative_base
   from datetime import datetime
   from uuid import uuid4
   
   Base = declarative_base()
   
   class VersionedEntity(Base):
       __abstract__ = True
       id = Column(UUID, primary_key=True, default=uuid4)
       version = Column(Integer, default=1)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
       created_by = Column(String, nullable=True)
       updated_by = Column(String, nullable=True)
   
   class TenantScoped:
       __abstract__ = True
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False, index=True)
   ```

2. **assets.py**: Define System, Vendor, DataElement, Process
   ```python
   from sqlalchemy import Column, String, Integer, JSON, Boolean, ForeignKey
   from sqlalchemy.orm import relationship
   from core.models.base import VersionedEntity, TenantScoped
   
   class Asset(VersionedEntity, TenantScoped):
       __tablename__ = 'assets'
       __mapper_args__ = {
           'polymorphic_identity': 'asset',
           'polymorphic_on': Column('asset_type', String)
       }
       asset_type = Column(String)
       name = Column(String, nullable=False)
       description = Column(String)
       owner_id = Column(String, ForeignKey('users.id'))
   
   class System(Asset):
       __mapper_args__ = {'polymorphic_identity': 'system'}
       data_categories = Column(JSON)
       processing_activities = Column(JSON)
       jurisdiction = Column(String)
       risk_classification = Column(String)
       storage_location = Column(String)
       encryption_method = Column(String)
       
       # Relationships
       data_elements = relationship('DataElement', back_populates='system')
       assessments = relationship('Assessment', back_populates='system')
   ```

3. **assessments.py**: Define Assessment hierarchy (PIA, DPIA, TIA, TRA, etc.)
   ```python
   from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
   from sqlalchemy.orm import relationship
   from core.models.base import VersionedEntity, TenantScoped
   
   class Assessment(VersionedEntity, TenantScoped):
       __tablename__ = 'assessments'
       __mapper_args__ = {
           'polymorphic_identity': 'assessment',
           'polymorphic_on': Column('assessment_type', String)
       }
       assessment_type = Column(String)
       title = Column(String, nullable=False)
       description = Column(Text)
       status = Column(String, default='draft')
       risk_score = Column(Float)
       legal_basis = Column(String)
       findings = Column(Text)
       mitigations = Column(JSON)  # List of mitigation recommendations
       assigned_to = Column(String, ForeignKey('users.id'))
       submitted_at = Column(DateTime, nullable=True)
       approved_at = Column(DateTime, nullable=True)
       approved_by = Column(String, ForeignKey('users.id'), nullable=True)
       
       # Relationships
       risks = relationship('Risk', back_populates='source_assessment')
   
   class PIAssessment(Assessment):
       __mapper_args__ = {'polymorphic_identity': 'pia'}
       assessed_system_id = Column(UUID, ForeignKey('assets.id'))
       child_population = Column(Boolean, default=False)
   
   class DPIAssessment(Assessment):
       __mapper_args__ = {'polymorphic_identity': 'dpia'}
       assessed_system_id = Column(UUID, ForeignKey('assets.id'))
       cross_border_transfer = Column(Boolean, default=False)
   
   class TIAssessment(Assessment):
       __mapper_args__ = {'polymorphic_identity': 'tia'}
       source_jurisdiction = Column(String)
       destination_jurisdiction = Column(String)
       transfer_mechanism = Column(String)  # SCC, Adequacy, etc.
   ```

4. **repositories/base_repository.py**: Generic CRUD + filtering
   ```python
   from typing import Generic, TypeVar, Optional, List
   from sqlalchemy.orm import Session
   from sqlalchemy import select
   
   T = TypeVar('T')
   
   class BaseRepository(Generic[T]):
       def __init__(self, db: Session, model_class: type[T]):
           self.db = db
           self.model_class = model_class
       
       async def create(self, obj: T) -> T:
           self.db.add(obj)
           await self.db.commit()
           await self.db.refresh(obj)
           return obj
       
       async def get_by_id(self, obj_id: UUID) -> Optional[T]:
           return await self.db.get(self.model_class, obj_id)
       
       async def get_by_tenant(self, tenant_id: str) -> List[T]:
           stmt = select(self.model_class).where(self.model_class.tenant_id == tenant_id)
           result = await self.db.execute(stmt)
           return result.scalars().all()
       
       async def update(self, obj_id: UUID, **kwargs) -> T:
           obj = await self.get_by_id(obj_id)
           for key, value in kwargs.items():
               setattr(obj, key, value)
           await self.db.commit()
           return obj
       
       async def delete(self, obj_id: UUID) -> None:
           obj = await self.get_by_id(obj_id)
           await self.db.delete(obj)
           await self.db.commit()
   ```

5. **Migrations**: Use Alembic
   ```bash
   alembic init migrations
   # Edit migrations/env.py to use SQLAlchemy models
   alembic revision --autogenerate -m "Initial schema with domain models"
   alembic upgrade head
   ```

TESTING STRATEGY:

1. **test_models.py**: Verify entity structure
   - Can create entities with required fields
   - Relationships are correctly mapped
   - Constraints are enforced

2. **test_repositories.py**: Verify CRUD operations
   - Create, read, update, delete
   - Filtering by tenant
   - Relationship traversal

3. **test_services.py**: Verify business logic
   - Assessment creation chains to Risk creation
   - Risk scoring calculations
   - Control effectiveness updates

INTEGRATION POINTS:

1. Replace `ProjectIntake` Pydantic model with `Process` entity
2. Replace `StatutaryArtifact` with `Assessment` + subclasses
3. Update `agent_gateway.py` nodes to use repositories instead of direct queries
4. Update `ontology_store.py` to query from new entity relationships
5. Update `rule_engine.py` to access Risk and Control entities

ACCEPTANCE CRITERIA:

✅ All entities created with relationships
✅ Migrations run successfully on PostgreSQL
✅ Repositories provide CRUD with filtering
✅ Tests pass (90%+ coverage)
✅ Legacy code can read from new schema
✅ No breaking changes to API (backward compatible)

EXPECTED TIMELINE:

- Week 1-2: Design + base classes + models
- Week 3-4: Repositories + services
- Week 5-6: Migrations + integration
- Week 7-8: Testing + documentation

DELIVERABLES:

1. core/models/ - All entity definitions
2. core/repositories/ - All repository implementations
3. migrations/ - Alembic schema migrations
4. tests/ - Comprehensive test suite
5. INTEGRATION_GUIDE.md - How to migrate existing code
```

---

## ACCEPTANCE CRITERIA

- [ ] All 8 entity classes created with correct relationships
- [ ] PostgreSQL schema migrations run without errors
- [ ] Repositories provide consistent CRUD interface
- [ ] Tests pass with 90%+ code coverage
- [ ] Backward compatibility maintained (legacy code still works)
- [ ] Data migrated from old schema to new
- [ ] Documentation complete

---

## NEXT STEPS AFTER MODULE 1

Once domain model is solid, MODULE 2 (Multi-Tenancy Isolation) can:
- Use tenant_id from TenantScoped mixin
- Filter all queries by tenant automatically
- Add tenant validation middleware

