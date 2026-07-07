# PHASE 1 IMPLEMENTATION GUIDE
## 4 Modules for KIBO Enterprise Readiness

**Duration:** 16 weeks  
**Target:** Enterprise pilot deployment  
**Language:** Python (FastAPI) + SQLAlchemy + PostgreSQL  
**IDE:** Antigravity IDE + Gemma4

---

## QUICK START

### For Antigravity IDE Users:

1. **Open Antigravity IDE**
2. **For each module:**
   - Open the module file (MODULE_1_*.md, MODULE_2_*.md, etc.)
   - Copy the entire "IMPLEMENTATION PROMPT FOR GEMMA4" section
   - Paste into Antigravity IDE chat with Gemma4
   - Gemma4 will generate the implementation code
   - Follow the FILE STRUCTURE to place files correctly

### Module Sequence (MUST follow this order):

```
Week 1-8:  MODULE 1: Domain Model (Foundational)
            ↓
Week 5-10: MODULE 2: Multi-Tenancy (parallel start week 5)
            ↓
Week 9-16: MODULE 3: Event-Driven (parallel start week 9)
            ↓
Week 10-14: MODULE 4: Audit Logging (parallel start week 10)
```

---

## MODULE OVERVIEW TABLE

| Module | Weeks | Effort | Focus | Deliverable |
|--------|-------|--------|-------|-------------|
| 1 | 1-8 | High | Domain model + repositories | SQLAlchemy ORM + migrations |
| 2 | 5-10 | High | Tenant isolation + middleware | Multi-tenant context + RBAC |
| 3 | 9-16 | High | Event bus + handlers | Event-driven cascade logic |
| 4 | 10-14 | Medium | Audit trails + versioning | Immutable audit logs |

---

## WEEK-BY-WEEK PLAN

### WEEK 1-2: Foundation (Module 1 Start)

**Goals:**
- Design domain model
- Create base entity classes
- Define all domain entities

**Deliverables:**
- `core/models/base.py` - Base classes
- `core/models/assets.py` - System, Vendor, DataElement, Process
- `core/models/assessments.py` - Assessment hierarchy
- `core/models/risks.py` - Risk, RiskAcceptance
- `core/models/controls.py` - Control, ControlTest
- `core/models/contracts.py` - Contract, Jurisdiction

**Tasks:**
```
[ ] Design ERD (Entity Relationship Diagram)
[ ] Create base.py with VersionedEntity + TenantScoped
[ ] Create assets.py with all asset types
[ ] Create assessments.py with Assessment subclasses (PIA, DPIA, TIA, etc.)
[ ] Create risks.py with Risk entity
[ ] Create controls.py with Control entity
[ ] Add all relationships (foreign keys, backrefs)
[ ] Run tests: entity creation, relationships
```

**Acceptance:** Entities created with correct relationships

---

### WEEK 3-4: Repositories (Module 1 Continue)

**Goals:**
- Create repository pattern
- Implement CRUD + filtering
- Add tenant-scoped queries

**Deliverables:**
- `core/repositories/base_repository.py` - Generic CRUD
- `core/repositories/system_repository.py`
- `core/repositories/assessment_repository.py`
- `core/repositories/risk_repository.py`

**Tasks:**
```
[ ] Create BaseRepository[T] class
[ ] Implement async CRUD methods (create, get, update, delete)
[ ] Add filtering by tenant_id
[ ] Create entity-specific repositories
[ ] Add relationship navigation (system.assessments, etc.)
[ ] Test CRUD operations
[ ] Test relationship traversal
```

**Acceptance:** All repositories provide consistent interface

---

### WEEK 5-6: Migrations + Multi-Tenancy Start (Module 1 End + Module 2 Start)

**Goals:**
- Create Alembic migrations
- Set up PostgreSQL
- Start multi-tenancy design

**Deliverables:**
- `migrations/versions/*.py` - Alembic migration files
- `core/models/tenant.py` - Tenant, TenantMembership entities
- `core/context/tenant_context.py` - TenantContext + context vars

**Tasks:**
```
[ ] Initialize Alembic
[ ] Generate migration: "Initial schema with domain models"
[ ] Test migration on PostgreSQL
[ ] Verify schema created correctly
[ ] Create Tenant entity
[ ] Create TenantMembership entity
[ ] Implement TenantContext + context vars
[ ] Add get_current_tenant() helper
```

**Acceptance:** PostgreSQL schema initialized, tenant context available

---

### WEEK 7-8: Module 1 Testing + Integration (Parallel Module 2)

**Goals:**
- Comprehensive testing
- Integration with existing code
- Begin multi-tenancy middleware

**Deliverables:**
- `tests/test_models.py` - Model tests
- `tests/test_repositories.py` - Repository tests
- `core/middleware/tenant_isolation.py` - Tenant middleware (start)

**Tasks:**
```
[ ] Write tests for all entities
[ ] Test relationships work correctly
[ ] Test repositories (CRUD, filtering)
[ ] Test tenant context isolation
[ ] Integrate with existing agent_gateway.py
[ ] Update existing code to use repositories
[ ] Create TenantIsolationMiddleware (skeleton)
[ ] Run integration tests
```

**Acceptance:** 90%+ test coverage, backward compatible

---

### WEEK 9-10: Module 2 Middleware + Module 3 Start

**Goals:**
- Complete tenant isolation
- Begin event-driven system

**Deliverables:**
- `core/middleware/tenant_isolation.py` (complete)
- `core/middleware/audit_middleware.py` (complete)
- `core/security/tenant_validation.py` - RBAC
- `core/events/domain_events.py` - Event definitions (start)

**Tasks:**
```
[ ] Implement TenantIsolationMiddleware fully
[ ] Extract tenant from header/subdomain
[ ] Verify user membership in tenant
[ ] Create AuditLoggingMiddleware
[ ] Implement RBAC (Role-based Access Control)
[ ] Create permission matrix
[ ] Define all domain events (AssessmentApproved, RiskCreated, etc.)
[ ] Test middleware doesn't leak data
```

**Acceptance:** Zero cross-tenant data access, RBAC working

---

### WEEK 11-12: Event Bus + Processing (Module 3 Continue)

**Goals:**
- Implement event bus
- Create event handlers
- Wire up cascade logic

**Deliverables:**
- `core/events/event_bus.py` - Event bus interface
- `core/events/redis_bus.py` - Redis Streams implementation
- `core/handlers/assessment_handlers.py`
- `core/handlers/risk_handlers.py`
- `core/handlers/control_handlers.py`
- `core/services/event_processor.py`

**Tasks:**
```
[ ] Choose event stream (Redis Streams or Kafka)
[ ] Implement EventBus interface
[ ] Create Redis Streams implementation
[ ] Define event handlers (AssessmentApproved, RiskCreated, etc.)
[ ] Implement cascade logic:
    - Assessment approved → Create Risk
    - Risk created → Notify DPO
    - Control implemented → Update Risk status
[ ] Test idempotency (can replay events)
[ ] Test event throughput > 1000/sec
[ ] Integrate event publishing into LangGraph nodes
```

**Acceptance:** Events auto-propagate across modules

---

### WEEK 13-14: Audit Logging (Module 4 Start)

**Goals:**
- Implement audit trail system
- Create versioning
- Add integrity checking

**Deliverables:**
- `core/models/audit_log.py` - AuditLog, EntityVersion tables
- `core/audit/audit_service.py` - Audit CRUD + queries
- `core/audit/audit_decorator.py` - @audit_log decorator
- `core/audit/temporal_query.py` - Time-travel queries

**Tasks:**
```
[ ] Create AuditLog table (append-only)
[ ] Create EntityVersion table (snapshots)
[ ] Create DataAccessLog table
[ ] Implement AuditService with:
    - log_change() - record all changes
    - log_data_access() - record who accessed what
    - get_entity_audit_trail() - get history
    - get_entity_state_at_time() - time-travel query
[ ] Implement hash chain for integrity
[ ] Create @audit_log decorator
[ ] Add temporal query capabilities
[ ] Test integrity verification
[ ] Integrate audit logging into all entities
```

**Acceptance:** All changes logged, cannot be tampered with

---

### WEEK 15-16: Testing + Go/No-Go Checkpoint

**Goals:**
- Comprehensive integration testing
- Verify go/no-go checkpoint criteria
- Prepare for Phase 2

**Deliverables:**
- `tests/test_integration_full_flow.py` - Full workflow tests
- `tests/test_multitenancy_isolation.py` - Isolation verification
- `tests/test_event_propagation.py` - Event cascade verification
- Checkpoint verification report

**Tasks:**
```
[ ] Write end-to-end workflow test
[ ] Test full flow: Assessment → Risk → Control updates
[ ] Verify multi-tenancy isolation with multiple tenants
[ ] Test cross-tenant access attempts (should fail)
[ ] Load test: 1000+ concurrent workflows
[ ] Verify audit trail completeness
[ ] Test temporal queries
[ ] Verify event idempotency
[ ] Performance testing (latency, throughput)

Go/No-Go Checkpoint Criteria:
[ ] Single enterprise customer isolated
[ ] Assessments → Risk Register auto-propagate
[ ] Complete audit trails available
[ ] CPO/DPO/Analyst dashboards functional
[ ] 1000+ concurrent workflows supported
[ ] Zero inter-tenant data leakage verified
```

---

## TESTING CHECKLIST

### Unit Tests (Each Module)
- [ ] Entity creation + relationships
- [ ] Repository CRUD operations
- [ ] Tenant context isolation
- [ ] Event publishing
- [ ] Audit logging

### Integration Tests
- [ ] Assessment → Risk cascade
- [ ] Risk → Control updates
- [ ] Tenant isolation verification
- [ ] Audit trail completeness
- [ ] Event idempotency

### Performance Tests
- [ ] Query latency < 100ms (p99)
- [ ] Event processing < 100ms (p99)
- [ ] Audit log writes < 50ms
- [ ] Concurrent workflows: 1000+

### Security Tests
- [ ] Cross-tenant access = 403
- [ ] User impersonation = 403
- [ ] Audit integrity = verified
- [ ] No data leakage

---

## FILE STRUCTURE CREATED

After all 4 modules, your codebase will have:

```
kibo-is/
├── core/
│   ├── models/
│   │   ├── base.py              # VersionedEntity, TenantScoped
│   │   ├── assets.py            # System, Vendor, DataElement, Process
│   │   ├── assessments.py       # Assessment hierarchy
│   │   ├── risks.py             # Risk, RiskAcceptance
│   │   ├── controls.py          # Control, ControlTest
│   │   ├── contracts.py         # Contract, Jurisdiction
│   │   ├── tenant.py            # Tenant, TenantMembership
│   │   ├── audit_log.py         # AuditLog, EntityVersion, DataAccessLog
│   │   └── associations.py      # Join tables
│   ├── repositories/
│   │   ├── base_repository.py
│   │   ├── system_repository.py
│   │   ├── assessment_repository.py
│   │   ├── risk_repository.py
│   │   ├── control_repository.py
│   │   ├── tenant_repository.py
│   │   └── audit_repository.py
│   ├── services/
│   │   ├── system_service.py
│   │   ├── assessment_service.py
│   │   ├── risk_service.py
│   │   ├── control_service.py
│   │   └── event_processor.py
│   ├── context/
│   │   ├── tenant_context.py
│   │   └── request_context.py
│   ├── middleware/
│   │   ├── tenant_isolation.py
│   │   ├── audit_logging.py
│   │   └── error_handling.py
│   ├── events/
│   │   ├── domain_events.py
│   │   ├── event_bus.py
│   │   └── redis_bus.py
│   ├── handlers/
│   │   ├── assessment_handlers.py
│   │   ├── risk_handlers.py
│   │   ├── control_handlers.py
│   │   ├── notification_handlers.py
│   │   └── audit_handlers.py
│   ├── audit/
│   │   ├── audit_service.py
│   │   ├── audit_decorator.py
│   │   ├── temporal_query.py
│   │   └── evidence_export.py
│   └── security/
│       ├── tenant_validation.py
│       └── permissions.py
├── api/
│   └── v1/
│       ├── assessments.py
│       ├── risks.py
│       ├── controls.py
│       ├── vendors.py
│       ├── audit.py
│       └── middleware.py
├── migrations/
│   └── versions/
│       ├── *.py (Alembic migrations)
└── tests/
    ├── test_models.py
    ├── test_repositories.py
    ├── test_multitenancy.py
    ├── test_event_driven.py
    ├── test_audit_logging.py
    └── test_integration_full_flow.py
```

---

## HOW TO USE WITH ANTIGRAVITY IDE

### Step 1: Copy Module Prompt
1. Open `MODULE_1_DOMAIN_MODEL.md`
2. Find "IMPLEMENTATION PROMPT FOR GEMMA4" section
3. Copy entire prompt (from "```" to closing "```")

### Step 2: Paste into Antigravity
1. Open Antigravity IDE
2. Select Gemma4 model
3. Paste the prompt into chat
4. Wait for code generation

### Step 3: Implement Generated Code
1. Gemma4 will output Python code
2. Create files in specified locations
3. Run tests provided
4. Fix any issues

### Step 4: Move to Next Module
1. After Module 1 passes all tests
2. Move to Module 2
3. Repeat process

---

## DEPENDENCIES & INTEGRATION

### Module Dependencies:
```
MODULE 1 (Domain Model)
    ↓ (provides entities + repositories)
MODULE 2 (Multi-Tenancy) + MODULE 3 (Events) [parallel start week 5/9]
    ↓ (tenant context + events)
MODULE 4 (Audit Logging) [parallel start week 10]
    ↓ (complete audit trail)
PHASE 1 COMPLETE → Go/No-Go Checkpoint
```

### Integration Points with Existing Code:

**agent_gateway.py:**
- Replace `ProjectIntake` Pydantic with `Process` entity
- Replace `StatutaryArtifact` with `Assessment` + subclasses
- Update nodes to emit events
- Use repositories instead of direct DB queries

**ontology_store.py:**
- Query from new entity relationships
- Use domain model instead of hardcoded edges

**rule_engine.py:**
- Access Risk and Control entities
- Use new risk scoring logic

---

## SUCCESS METRICS

### Week 8 (Module 1 Complete):
- ✅ All entities created with relationships
- ✅ PostgreSQL schema migrated
- ✅ Repositories provide CRUD + filtering
- ✅ Tests pass with 90%+ coverage
- ✅ Backward compatibility maintained

### Week 10 (Module 2 Complete):
- ✅ All requests have tenant context
- ✅ Cross-tenant access = 403
- ✅ Audit logs include tenant + user
- ✅ Zero inter-tenant leakage verified
- ✅ Performance < 10ms/request

### Week 16 (Module 3 + 4 Complete):
- ✅ Assessment → Risk auto-propagation
- ✅ Event throughput > 1000/sec
- ✅ All changes logged + auditable
- ✅ Temporal queries working
- ✅ 1000+ concurrent workflows

### Go/No-Go Checkpoint (Week 16):
- ✅ Single enterprise customer isolated
- ✅ Complete audit trails available
- ✅ Role-specific dashboards functional
- ✅ Zero inter-tenant data leakage
- ✅ Ready for Phase 2

---

## NEXT PHASE (WEEKS 17-32)

After Phase 1 completes and Go/No-Go checkpoint passes:

**Phase 2: Enterprise Features**
1. Vendor Risk Management (6 wks)
2. DSAR Workflows (4 wks)
3. Breach/Incident Management (4 wks)
4. Notification System (4 wks)
5. Policy Management (4 wks)
6. Training Tracking (3 wks)

All built on top of these 4 solid modules.

---

## TIPS FOR SUCCESS

### Code Quality:
- Write tests FIRST (TDD approach)
- Use type hints everywhere
- Document with docstrings
- Keep functions small (< 50 lines)

### Testing:
- Unit test each component
- Integration test workflows
- Performance test load
- Security test isolation

### Performance:
- Use indexes for queries
- Cache frequently accessed data
- Batch event processing
- Monitor metrics constantly

### Documentation:
- Docstring every function
- Keep README updated
- Document migrations
- Create ADRs (Architecture Decision Records)

---

## TROUBLESHOOTING

### "Entity not found" errors:
- Check tenant_id filter is applied
- Verify entity exists in DB
- Check for soft deletes

### "Cross-tenant access" failures:
- Verify middleware is loaded
- Check tenant context is set
- Review permission decorators

### Event handler not running:
- Verify event bus started
- Check handler subscription
- Review consumer group offset
- Check dead-letter queue

### Audit log writes slow:
- Check PostgreSQL indexes
- Monitor disk I/O
- Review batch insert size
- Consider partitioning

---

## SUPPORT & QUESTIONS

For each module, detailed implementation prompts are provided for Gemma4. If you encounter issues:

1. **Check acceptance criteria** - Are all requirements met?
2. **Review tests** - Do tests pass?
3. **Check integration** - Is module integrated with previous ones?
4. **Performance** - Are performance targets met?

Each module has been designed to work independently while building toward the integrated Phase 1 system.

---

**Total Effort:** 16 weeks  
**Team Size:** 4-6 engineers  
**Timeline to Go/No-Go:** Week 16 checkpoint  
**Timeline to Phase 2 Ready:** Week 32

Good luck! These 4 modules will transform KIBO from functionally sound to enterprise-ready. 🚀

