# MODULE 4: AUDIT LOGGING FRAMEWORK
## For Antigravity IDE + Gemma4

**Duration:** 4 weeks  
**Priority:** CRITICAL  
**Effort:** Medium  
**Dependencies:** MODULE 1 (Domain Model), MODULE 2 (Multi-Tenancy), MODULE 3 (Events)

---

## OVERVIEW

Implement comprehensive, immutable audit logging for compliance. Track all changes with who, what, when, and why.

**Current State:**
- No audit trail of decisions
- Cannot explain why assessment was approved/rejected
- No evidence for regulators
- No versioning of assessments

**Target State:**
- All changes logged to immutable append-only tables
- Complete audit trail per entity
- Temporal versioning (can see state at any point in time)
- Evidence exportable for audits

---

## MODULE OBJECTIVES

1. ✅ Create AuditLog, EntityVersion, and DataAccessLog tables
2. ✅ Implement audit logging middleware
3. ✅ Create temporal query capabilities (AS OF specific timestamp)
4. ✅ Build audit trail visualization endpoints
5. ✅ Add evidence export for compliance
6. ✅ Write comprehensive audit tests

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building an immutable audit logging system for KIBO to ensure compliance auditability.

TASK: Create comprehensive audit logging that captures all changes, decisions, and data access.

REQUIREMENTS:
1. Append-only audit tables (no deletes, only inserts)
2. Temporal queries (show state at any point in time)
3. Complete change tracking (before → after)
4. Cryptographic integrity (hash chains)
5. Tenant-scoped audit logs (no cross-tenant visibility)

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── models/
│   │   ├── audit_log.py         # AuditLog, EntityVersion, DataAccessLog
│   │   └── audit_trail.py       # AuditTrail (aggregated view)
│   ├── audit/
│   │   ├── __init__.py
│   │   ├── audit_service.py     # AuditService with CRUD + queries
│   │   ├── audit_decorator.py   # @audit_log decorator for functions
│   │   ├── change_tracker.py    # Track what changed (diff generation)
│   │   ├── temporal_query.py    # Query entity state at specific time
│   │   └── evidence_export.py   # Export audit evidence for compliance
│   └── middleware/
│       └── audit_middleware.py  # Middleware to capture all requests
└── tests/
    └── test_audit_logging.py
```

IMPLEMENTATION DETAILS:

1. **models/audit_log.py**: Audit tables
   ```python
   from sqlalchemy import Column, String, Text, DateTime, JSON, Integer, Index
   from sqlalchemy.orm import relationship
   from core.models.base import Timestamped
   
   class AuditLog(Base, Timestamped):
       """Immutable audit log of all changes (append-only)"""
       __tablename__ = 'audit_logs'
       
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
       
       # Who made the change
       user_id = Column(String, nullable=True)
       user_email = Column(String, nullable=True)
       user_role = Column(String, nullable=True)
       
       # What changed
       action = Column(String, nullable=False)  # CREATE, UPDATE, DELETE, APPROVE, REJECT
       entity_type = Column(String, nullable=False)  # Assessment, Risk, Control, etc.
       entity_id = Column(String, nullable=False)
       
       # Before → After (only store if diff is small)
       previous_state = Column(JSON, nullable=True)  # Full state before change
       new_state = Column(JSON, nullable=True)  # Full state after change
       changes = Column(JSON, nullable=True)  # {field: {old: value, new: value}, ...}
       
       # Why did this happen
       reason = Column(Text, nullable=True)  # User-provided reason for change
       change_context = Column(JSON, nullable=True)  # {triggered_by: event, ...}
       
       # Request context
       request_id = Column(String, nullable=True)  # Correlation ID
       ip_address = Column(String, nullable=True)
       user_agent = Column(String, nullable=True)
       
       # Integrity
       change_hash = Column(String, nullable=True)  # SHA256 of this record
       previous_hash = Column(String, nullable=True)  # SHA256 of previous record (chain)
       
       # Timestamps
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       
       # Indexes for efficient querying
       __table_args__ = (
           Index('ix_audit_tenant_created', 'tenant_id', 'created_at'),
           Index('ix_audit_entity', 'entity_type', 'entity_id'),
           Index('ix_audit_user_date', 'user_id', 'created_at'),
           Index('ix_audit_action', 'action'),
       )
   
   class EntityVersion(Base):
       """Temporal versioning - complete snapshots of entities over time"""
       __tablename__ = 'entity_versions'
       
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
       
       entity_type = Column(String, nullable=False)
       entity_id = Column(String, nullable=False)
       version = Column(Integer, nullable=False)  # 1, 2, 3, ...
       
       # Complete snapshot of entity at this version
       snapshot = Column(JSON, nullable=False)  # Full entity state
       
       # Metadata
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       created_by = Column(String)
       reason = Column(Text)
       
       __table_args__ = (
           Index('ix_entity_versions_id_entity', 'entity_type', 'entity_id', 'version'),
           Index('ix_entity_versions_tenant_created', 'tenant_id', 'created_at'),
       )
   
   class DataAccessLog(Base, Timestamped):
       """Log of who accessed what data"""
       __tablename__ = 'data_access_logs'
       
       id = Column(UUID, primary_key=True, default=uuid4)
       tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
       
       # Who accessed
       user_id = Column(String, nullable=False)
       user_email = Column(String, nullable=True)
       
       # What was accessed
       entity_type = Column(String, nullable=False)
       entity_id = Column(String, nullable=False)
       action = Column(String)  # READ, DOWNLOAD, EXPORT
       
       # How much data
       record_count = Column(Integer)
       data_size_bytes = Column(Integer)
       
       # Why
       access_reason = Column(String, nullable=True)  # compliance_audit, routine_review, etc.
       justification = Column(Text, nullable=True)
       
       # Request context
       ip_address = Column(String, nullable=True)
       endpoint = Column(String, nullable=True)
       
       created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
       
       __table_args__ = (
           Index('ix_data_access_tenant_user', 'tenant_id', 'user_id'),
           Index('ix_data_access_entity', 'entity_type', 'entity_id'),
       )
   ```

2. **audit/audit_service.py**: Service for logging and querying
   ```python
   from datetime import datetime
   from hashlib import sha256
   import json
   from sqlalchemy import select
   from core.models.audit_log import AuditLog, EntityVersion, DataAccessLog
   from core.context.tenant_context import get_tenant_id
   
   class AuditService:
       def __init__(self, db: Session):
           self.db = db
       
       async def log_change(
           self,
           action: str,
           entity_type: str,
           entity_id: str,
           previous_state: dict = None,
           new_state: dict = None,
           user_id: str = None,
           reason: str = None,
           context: dict = None
       ) -> AuditLog:
           """Log a change to the audit trail"""
           
           tenant_id = get_tenant_id()
           
           # Calculate diff
           changes = self._calculate_diff(previous_state, new_state)
           
           # Create audit log entry
           log = AuditLog(
               tenant_id=tenant_id,
               user_id=user_id,
               action=action,
               entity_type=entity_type,
               entity_id=entity_id,
               previous_state=previous_state,
               new_state=new_state,
               changes=changes,
               reason=reason,
               change_context=context or {},
               created_at=datetime.utcnow()
           )
           
           # Get previous audit log for hash chain
           previous_log = await self._get_previous_audit_log(
               entity_type, entity_id
           )
           if previous_log:
               log.previous_hash = previous_log.change_hash
           
           # Calculate hash
           log.change_hash = self._calculate_hash(log)
           
           self.db.add(log)
           await self.db.commit()
           
           # Also create entity version snapshot
           if new_state:
               version = EntityVersion(
                   tenant_id=tenant_id,
                   entity_type=entity_type,
                   entity_id=entity_id,
                   version=await self._get_next_version(entity_type, entity_id),
                   snapshot=new_state,
                   created_by=user_id,
                   reason=reason,
                   created_at=datetime.utcnow()
               )
               self.db.add(version)
               await self.db.commit()
           
           return log
       
       async def log_data_access(
           self,
           entity_type: str,
           entity_id: str,
           action: str,
           user_id: str,
           record_count: int = 1,
           reason: str = None
       ) -> DataAccessLog:
           """Log who accessed what data"""
           
           tenant_id = get_tenant_id()
           
           log = DataAccessLog(
               tenant_id=tenant_id,
               user_id=user_id,
               entity_type=entity_type,
               entity_id=entity_id,
               action=action,
               record_count=record_count,
               access_reason=reason,
               created_at=datetime.utcnow()
           )
           
           self.db.add(log)
           await self.db.commit()
           
           return log
       
       async def get_entity_audit_trail(
           self,
           entity_type: str,
           entity_id: str,
           limit: int = 100
       ) -> List[AuditLog]:
           """Get audit trail for specific entity"""
           
           tenant_id = get_tenant_id()
           
           stmt = select(AuditLog).where(
               AuditLog.tenant_id == tenant_id,
               AuditLog.entity_type == entity_type,
               AuditLog.entity_id == entity_id
           ).order_by(AuditLog.created_at.desc()).limit(limit)
           
           result = await self.db.execute(stmt)
           return result.scalars().all()
       
       async def get_entity_state_at_time(
           self,
           entity_type: str,
           entity_id: str,
           as_of: datetime
       ) -> Optional[dict]:
           """Get entity state as it was at specific point in time"""
           
           tenant_id = get_tenant_id()
           
           # Find the version closest to as_of timestamp
           stmt = select(EntityVersion).where(
               EntityVersion.tenant_id == tenant_id,
               EntityVersion.entity_type == entity_type,
               EntityVersion.entity_id == entity_id,
               EntityVersion.created_at <= as_of
           ).order_by(EntityVersion.created_at.desc()).limit(1)
           
           result = await self.db.execute(stmt)
           version = result.scalar_one_or_none()
           
           return version.snapshot if version else None
       
       async def verify_integrity(
           self,
           audit_log_id: str
       ) -> bool:
           """Verify audit log hasn't been tampered with"""
           
           log = await self.db.get(AuditLog, audit_log_id)
           if not log:
               return False
           
           # Recalculate hash
           calculated_hash = self._calculate_hash(log)
           
           # Compare
           return calculated_hash == log.change_hash
       
       def _calculate_diff(self, old: dict, new: dict) -> dict:
           """Calculate what changed between old and new state"""
           if not old or not new:
               return None
           
           changes = {}
           all_keys = set(old.keys()) | set(new.keys())
           
           for key in all_keys:
               old_val = old.get(key)
               new_val = new.get(key)
               
               if old_val != new_val:
                   changes[key] = {
                       'old': old_val,
                       'new': new_val
                   }
           
           return changes if changes else None
       
       def _calculate_hash(self, log: AuditLog) -> str:
           """Calculate SHA256 hash for integrity checking"""
           data = {
               'id': str(log.id),
               'tenant_id': log.tenant_id,
               'action': log.action,
               'entity_type': log.entity_type,
               'entity_id': log.entity_id,
               'changes': log.changes,
               'created_at': log.created_at.isoformat(),
               'previous_hash': log.previous_hash or ''
           }
           
           json_str = json.dumps(data, sort_keys=True)
           return sha256(json_str.encode()).hexdigest()
       
       async def _get_previous_audit_log(
           self,
           entity_type: str,
           entity_id: str
       ) -> Optional[AuditLog]:
           """Get the most recent audit log for this entity"""
           
           tenant_id = get_tenant_id()
           
           stmt = select(AuditLog).where(
               AuditLog.tenant_id == tenant_id,
               AuditLog.entity_type == entity_type,
               AuditLog.entity_id == entity_id
           ).order_by(AuditLog.created_at.desc()).limit(1)
           
           result = await self.db.execute(stmt)
           return result.scalar_one_or_none()
       
       async def _get_next_version(
           self,
           entity_type: str,
           entity_id: str
       ) -> int:
           """Get next version number for entity"""
           
           tenant_id = get_tenant_id()
           
           stmt = select(EntityVersion.version).where(
               EntityVersion.tenant_id == tenant_id,
               EntityVersion.entity_type == entity_type,
               EntityVersion.entity_id == entity_id
           ).order_by(EntityVersion.version.desc()).limit(1)
           
           result = await self.db.execute(stmt)
           last_version = result.scalar()
           
           return (last_version or 0) + 1
   ```

3. **audit/audit_decorator.py**: Function decorator for automatic logging
   ```python
   import functools
   from core.audit.audit_service import AuditService
   from core.context.tenant_context import get_current_tenant
   
   def audit_log(entity_type: str, action: str):
       """Decorator to automatically log function calls"""
       
       def decorator(func):
           @functools.wraps(func)
           async def wrapper(*args, **kwargs):
               # Get before state if available
               before_state = kwargs.get('previous_state')
               
               # Call function
               result = await func(*args, **kwargs)
               
               # Get after state
               after_state = kwargs.get('new_state') or result
               
               # Log to audit trail
               audit_service = AuditService(kwargs.get('db'))
               tenant = get_current_tenant()
               
               await audit_service.log_change(
                   action=action,
                   entity_type=entity_type,
                   entity_id=kwargs.get('entity_id'),
                   previous_state=before_state,
                   new_state=after_state,
                   user_id=tenant.user_id,
                   reason=kwargs.get('reason')
               )
               
               return result
           
           return wrapper
       
       return decorator
   
   # Usage:
   @audit_log('Assessment', 'APPROVED')
   async def approve_assessment(
       assessment_id: str,
       approved_by: str,
       reason: str,
       db: Session,
       previous_state: dict,
       new_state: dict
   ):
       # ... approval logic ...
       pass
   ```

4. **audit/temporal_query.py**: Time travel queries
   ```python
   from datetime import datetime
   from sqlalchemy import select
   
   class TemporalQuery:
       def __init__(self, db: Session):
           self.db = db
       
       async def get_entity_as_of(
           self,
           entity_type: str,
           entity_id: str,
           as_of: datetime
       ) -> dict:
           """Get entity state at specific point in time"""
           
           # Find latest version before as_of
           from core.models.audit_log import EntityVersion
           
           stmt = select(EntityVersion).where(
               EntityVersion.entity_type == entity_type,
               EntityVersion.entity_id == entity_id,
               EntityVersion.created_at <= as_of
           ).order_by(EntityVersion.created_at.desc()).limit(1)
           
           result = await self.db.execute(stmt)
           version = result.scalar_one_or_none()
           
           return version.snapshot if version else None
       
       async def get_change_history(
           self,
           entity_type: str,
           entity_id: str,
           start_date: datetime = None,
           end_date: datetime = None
       ) -> List[dict]:
           """Get change history between dates"""
           
           from core.models.audit_log import AuditLog
           
           stmt = select(AuditLog).where(
               AuditLog.entity_type == entity_type,
               AuditLog.entity_id == entity_id
           )
           
           if start_date:
               stmt = stmt.where(AuditLog.created_at >= start_date)
           if end_date:
               stmt = stmt.where(AuditLog.created_at <= end_date)
           
           stmt = stmt.order_by(AuditLog.created_at.asc())
           
           result = await self.db.execute(stmt)
           logs = result.scalars().all()
           
           return [
               {
                   'timestamp': log.created_at,
                   'user': log.user_id,
                   'action': log.action,
                   'changes': log.changes
               }
               for log in logs
           ]
   ```

5. **audit/evidence_export.py**: Compliance evidence export
   ```python
   from datetime import datetime
   import csv
   import json
   
   class EvidenceExporter:
       def __init__(self, audit_service: AuditService):
           self.audit_service = audit_service
       
       async def export_audit_trail_csv(
           self,
           entity_type: str,
           entity_id: str,
           output_path: str
       ):
           """Export audit trail as CSV for compliance audits"""
           
           logs = await self.audit_service.get_entity_audit_trail(
               entity_type, entity_id
           )
           
           with open(output_path, 'w', newline='') as csvfile:
               fieldnames = [
                   'timestamp', 'user_id', 'action', 'changes', 'reason'
               ]
               writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
               
               writer.writeheader()
               for log in logs:
                   writer.writerow({
                       'timestamp': log.created_at.isoformat(),
                       'user_id': log.user_id,
                       'action': log.action,
                       'changes': json.dumps(log.changes),
                       'reason': log.reason
                   })
       
       async def generate_compliance_report(
           self,
           start_date: datetime,
           end_date: datetime
       ) -> dict:
           """Generate compliance report with audit summaries"""
           
           report = {
               'report_period': {
                   'start': start_date.isoformat(),
                   'end': end_date.isoformat()
               },
               'assessments': {
                   'total_created': 0,
                   'total_approved': 0,
                   'total_rejected': 0,
                   'list': []
               },
               'risks': {
                   'total_created': 0,
                   'total_mitigated': 0,
                   'list': []
               },
               'access_summary': {
                   'total_accesses': 0,
                   'by_user': {},
                   'by_entity_type': {}
               }
           }
           
           # Populate from audit logs...
           # (Implementation details omitted for brevity)
           
           return report
   ```

6. **API endpoints for audit trails**:
   ```python
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix='/api/audit', tags=['audit'])
   
   @router.get('/assessment/{assessment_id}/trail')
   async def get_assessment_audit_trail(
       assessment_id: str,
       audit_service: AuditService = Depends()
   ):
       """Get complete audit trail for assessment"""
       return await audit_service.get_entity_audit_trail(
           'Assessment', assessment_id
       )
   
   @router.get('/assessment/{assessment_id}/version/{timestamp}')
   async def get_assessment_at_time(
       assessment_id: str,
       timestamp: datetime,
       temporal_query: TemporalQuery = Depends()
   ):
       """Get assessment state at specific point in time"""
       return await temporal_query.get_entity_as_of(
           'Assessment', assessment_id, timestamp
       )
   
   @router.post('/export/compliance-report')
   async def export_compliance_report(
       start_date: datetime,
       end_date: datetime,
       exporter: EvidenceExporter = Depends()
   ):
       """Export compliance evidence report"""
       return await exporter.generate_compliance_report(
           start_date, end_date
       )
   
   @router.get('/integrity/verify/{log_id}')
   async def verify_audit_log_integrity(
       log_id: str,
       audit_service: AuditService = Depends()
   ):
       """Verify audit log hasn't been tampered with"""
       is_valid = await audit_service.verify_integrity(log_id)
       return {'log_id': log_id, 'is_valid': is_valid}
   ```

TESTING STRATEGY:

1. **test_audit_logging.py**: Comprehensive audit tests
   ```python
   @pytest.mark.asyncio
   async def test_audit_log_created_on_change():
       # Create assessment
       assessment = await create_assessment(title='Test')
       
       # Update assessment
       assessment.status = 'approved'
       await audit_service.log_change(
           action='APPROVED',
           entity_type='Assessment',
           entity_id=assessment.id,
           previous_state={'status': 'draft'},
           new_state={'status': 'approved'}
       )
       
       # Verify audit log created
       logs = await audit_service.get_entity_audit_trail('Assessment', assessment.id)
       assert len(logs) > 0
       assert logs[0].action == 'APPROVED'
   
   @pytest.mark.asyncio
   async def test_temporal_query():
       # Create assessment
       assessment = await create_assessment(title='Test')
       now = datetime.utcnow()
       
       # Approve assessment
       await audit_service.log_change(
           action='APPROVED',
           entity_type='Assessment',
           entity_id=assessment.id,
           new_state={'status': 'approved'}
       )
       
       # Get state before approval
       temporal = TemporalQuery(db)
       state_before = await temporal.get_entity_as_of(
           'Assessment', assessment.id,
           now - timedelta(minutes=1)
       )
       assert state_before['status'] == 'draft'
   
   @pytest.mark.asyncio
   async def test_audit_integrity():
       # Create audit log
       log = await audit_service.log_change(...)
       
       # Verify integrity
       is_valid = await audit_service.verify_integrity(log.id)
       assert is_valid == True
   ```

INTEGRATION:

✅ Add audit logging to all entity creation/update/delete
✅ Add audit logging to all approvals/decisions
✅ Log all data access (READ, EXPORT, DOWNLOAD)
✅ Export audit evidence on demand
✅ Temporal queries available for compliance
✅ Hash chain integrity verification

DEPLOYMENT:

✅ Create audit log tables in PostgreSQL
✅ Initialize AuditService in app
✅ Register audit endpoints in API
✅ Start archiving audit logs after 90 days (if retention < 7 years)
✅ Set up automated backups of audit logs
✅ Configure read-only access to audit tables (no deletes)
```

---

## ACCEPTANCE CRITERIA

- [ ] All changes logged with who/what/when/why
- [ ] Audit logs are append-only (cannot delete)
- [ ] Hash chain provides integrity verification
- [ ] Temporal queries show entity state at any point
- [ ] Audit trails exportable as CSV/PDF for compliance
- [ ] Data access logged (who accessed what)
- [ ] Zero cross-tenant audit data leakage
- [ ] Tests verify integrity cannot be compromised
- [ ] Performance: < 50ms per audit log write
- [ ] Evidence export completes in < 5 seconds

---

## COMPLETION CHECKLIST FOR PHASE 1

After completing all 4 modules, verify:

### Module 1: Domain Model ✅
- [ ] All entities created with relationships
- [ ] PostgreSQL schema migrated successfully
- [ ] Repositories provide CRUD interface
- [ ] Tests pass with 90%+ coverage
- [ ] Backward compatibility maintained

### Module 2: Multi-Tenancy ✅
- [ ] All requests include tenant context
- [ ] Cross-tenant access returns 403
- [ ] Audit logs record tenant + user
- [ ] Zero inter-tenant data leakage verified
- [ ] Performance impact < 10ms/request

### Module 3: Event-Driven ✅
- [ ] AssessmentApproved → RiskCreated (automatic)
- [ ] ControlImplemented → Risk status updated
- [ ] All events include tenant context
- [ ] Event handlers are idempotent
- [ ] Event throughput > 1000 events/sec
- [ ] Handler latency < 100ms median

### Module 4: Audit Logging ✅
- [ ] All changes logged with hash chain
- [ ] Temporal queries work correctly
- [ ] Evidence export available
- [ ] Integrity verification passes
- [ ] Performance < 50ms per log write

### Phase 1 Go/No-Go Criteria ✅
- [ ] Single enterprise customer isolated
- [ ] Assessments → Risk Register auto-propagate
- [ ] Complete audit trails available
- [ ] CPO/DPO/Analyst dashboards functional
- [ ] 1000+ concurrent workflows supported
- [ ] Zero inter-tenant data leakage verified

---

## NEXT PHASE

After Phase 1 is complete and Go/No-Go checkpoint passed:

**Phase 2 (Weeks 17-32): Enterprise Features**
- Vendor risk management
- DSAR workflows
- Breach/incident management
- Notification system
- Policy management

Use these 4 modules as foundation for all Phase 2 work.

