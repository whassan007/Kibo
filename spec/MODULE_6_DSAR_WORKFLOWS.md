# MODULE 6: DATA SUBJECT ACCESS REQUEST (DSAR) WORKFLOWS
## For Antigravity IDE + Gemma4

**Duration:** 4 weeks  
**Priority:** HIGH (Table stakes)  
**Effort:** Medium-High  
**Dependencies:** MODULE 1-4 (Phase 1)

---

## OVERVIEW

Implement complete DSAR lifecycle: receipt → scope determination → data collection → redaction → delivery. Handle GDPR, CCPA, PIPEDA, Law 25 deadlines automatically.

**Current State:**
- No DSAR tracking
- Manual data collection
- No deadline management
- No redaction capability

**Target State:**
- DSAR intake portal
- Auto-deadline calculation by jurisdiction
- Data collection workflows
- Automated redaction rules
- Chain-of-custody tracking

---

## MODULE OBJECTIVES

1. ✅ Create DSAR entities (request, data elements, redactions)
2. ✅ Implement jurisdiction-aware deadline calculation
3. ✅ Build data collection workflow (LangGraph)
4. ✅ Create redaction engine for PII masking
5. ✅ Implement package verification + delivery
6. ✅ Add complete audit trail for compliance

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building a DSAR (Data Subject Access Request) management system for KIBO that handles all compliance jurisdictions.

TASK: Create end-to-end DSAR workflow with scope determination, data collection, redaction, and delivery.

REQUIREMENTS:
1. Multi-jurisdiction support: GDPR (30-45 days), CCPA (30-45 days), PIPEDA (30 days), Law 25 (45 days)
2. Data scope determination: What systems/data categories to include
3. Data collection: Query databases for personal data matching subject
4. Redaction rules: Mask other PII, legal privilege, confidential info
5. Verification: Ensure completeness before delivery
6. Audit trail: Log all steps for compliance proof

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── models/
│   │   ├── dsar_request.py        # Request, DataSubject, RequestedData
│   │   ├── dsar_scope.py          # Scope, DataCategory, System
│   │   ├── dsar_collection.py     # DataElement, CollectionTask
│   │   ├── dsar_redaction.py      # RedactionRule, AppliedRedaction
│   │   └── dsar_package.py        # DeliveryPackage, PackageVerification
│   ├── services/
│   │   ├── dsar_intake_service.py
│   │   ├── dsar_scope_service.py
│   │   ├── dsar_collection_service.py
│   │   ├── dsar_redaction_service.py
│   │   └── dsar_delivery_service.py
│   ├── workflows/
│   │   ├── dsar_fulfillment.py    # LangGraph workflow
│   │   └── dsar_templates.py
│   ├── rules/
│   │   └── redaction_rules.yaml   # Configurable redaction rules
│   └── integrations/
│       ├── slack_dsar.py          # Slack notifications
│       └── email_dsar.py          # Email delivery
├── api/
│   └── v1/
│       ├── dsar_intake.py         # Public + authenticated endpoints
│       ├── dsar_requests.py
│       └── dsar_packages.py
└── tests/
    └── test_dsar.py
```

IMPLEMENTATION DETAILS:

1. **models/dsar_request.py**: Request entities
   ```python
   from sqlalchemy import Column, String, DateTime, JSON, Boolean, Enum, ForeignKey, Text
   from core.models.base import VersionedEntity, TenantScoped, Timestamped
   
   class DataSubject(VersionedEntity, TenantScoped):
       __tablename__ = 'data_subjects'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       # Subject identification
       identifier_type = Column(String)  # email, user_id, phone, full_name
       identifier_value = Column(String)  # The actual value
       
       # Verification
       is_verified = Column(Boolean, default=False)
       verification_method = Column(String)  # none, email, phone, government_id
       verified_at = Column(DateTime, nullable=True)
       verified_by = Column(String, nullable=True)
       
       # Representation
       is_represented = Column(Boolean, default=False)
       representative_name = Column(String, nullable=True)
       representative_authorization = Column(String, nullable=True)  # Document path
       
       created_at = Column(DateTime, default=datetime.utcnow)
   
   class DataSubjectAccessRequest(VersionedEntity, TenantScoped):
       __tablename__ = 'dsar_requests'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       # Subject
       data_subject_id = Column(UUID, ForeignKey('data_subjects.id'))
       
       # Request details
       request_type = Column(String)  # access, deletion, portability, object
       received_at = Column(DateTime, nullable=False)
       received_via = Column(String)  # email, web_form, phone, other
       
       # Jurisdiction & deadline
       jurisdiction = Column(String)  # GDPR, CCPA, PIPEDA, Law25, etc.
       deadline = Column(DateTime, nullable=False)  # Auto-calculated
       days_remaining = Column(Integer)  # Calculated field
       
       # Status
       status = Column(String)  # received, pending_verification, scoping, collecting, redacting, ready, delivered, refused
       
       # Reasoning (if refused)
       refuse_reason = Column(String, nullable=True)  # frivolous, excessive, already_provided, no_data, etc.
       refuse_justification = Column(Text, nullable=True)
       
       # Requestor contact
       requestor_email = Column(String)
       requestor_phone = Column(String, nullable=True)
       preferred_delivery = Column(String)  # email, download, mail, etc.
       
       # Tracking
       assigned_to = Column(String, ForeignKey('users.id'), nullable=True)
       started_at = Column(DateTime, nullable=True)
       completed_at = Column(DateTime, nullable=True)
       delivered_at = Column(DateTime, nullable=True)
       
       # Relationships
       data_subject = relationship('DataSubject')
       scope = relationship('DsarScope', uselist=False, back_populates='request')
       data_elements = relationship('RequestedDataElement', back_populates='request')
       package = relationship('DeliveryPackage', uselist=False, back_populates='request')
       
       __table_args__ = (
           Index('ix_dsar_requests_deadline', 'deadline'),
           Index('ix_dsar_requests_status', 'status'),
           Index('ix_dsar_requests_data_subject', 'data_subject_id'),
       )
   
   class DsarScope(VersionedEntity, TenantScoped):
       __tablename__ = 'dsar_scope'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       request_id = Column(UUID, ForeignKey('dsar_requests.id'), unique=True)
       
       # Systems in scope
       systems_in_scope = Column(JSON)  # [system_ids]
       data_categories = Column(JSON)  # [PersonalInfo, PaymentInfo, HealthData, ...]
       
       # Time range
       from_date = Column(DateTime, nullable=True)  # If request specifies date range
       to_date = Column(DateTime, nullable=True)
       
       # Estimated metrics
       estimated_data_size_mb = Column(Float)
       estimated_record_count = Column(Integer)
       
       # Scope determination
       scope_determined_at = Column(DateTime, nullable=True)
       scope_determined_by = Column(String, nullable=True)
       
       request = relationship('DataSubjectAccessRequest', back_populates='scope')
   
   class RequestedDataElement(VersionedEntity, TenantScoped):
       __tablename__ = 'requested_data_elements'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       request_id = Column(UUID, ForeignKey('dsar_requests.id'))
       
       # What data
       system_id = Column(String)  # Which system
       data_category = Column(String)  # Type of data
       field_name = Column(String)  # email, phone, etc.
       
       # Collection status
       status = Column(String)  # pending, collecting, collected, redacted, included
       collection_method = Column(String)  # database_query, export, manual, api
       
       # Results
       actual_record_count = Column(Integer, nullable=True)
       actual_data_size_mb = Column(Float, nullable=True)
       
       collected_at = Column(DateTime, nullable=True)
       collected_by = Column(String, nullable=True)
       
       request = relationship('DataSubjectAccessRequest', back_populates='data_elements')
   ```

2. **services/dsar_intake_service.py**: Request intake
   ```python
   from datetime import datetime, timedelta
   from core.models.dsar_request import DataSubjectAccessRequest, DataSubject
   from core.context.tenant_context import get_tenant_id
   
   JURISDICTION_DEADLINES = {
       'GDPR': 30,      # 30 days from receipt
       'CCPA': 45,      # 45 days from receipt
       'PIPEDA': 30,    # 30 days from receipt
       'Law25': 45,     # 45 days from receipt
       'UK_GDPR': 30,   # 30 days from receipt
       'LGPD': 30,      # 30 days (Brazil)
   }
   
   class DsarIntakeService:
       def __init__(self, db: Session, event_bus):
           self.db = db
           self.event_bus = event_bus
       
       async def receive_request(
           self,
           request_type: str,  # access, deletion, portability, object
           jurisdiction: str,   # GDPR, CCPA, PIPEDA, Law25
           data_subject_identifier: str,  # email, user_id, etc.
           identifier_type: str,
           received_via: str,
           requestor_email: str,
           preferred_delivery: str = 'email'
       ) -> DataSubjectAccessRequest:
           """Receive and register DSAR"""
           
           tenant_id = get_tenant_id()
           
           # Create data subject if not exists
           data_subject = await self.db.execute(
               select(DataSubject).where(
                   DataSubject.tenant_id == tenant_id,
                   DataSubject.identifier_type == identifier_type,
                   DataSubject.identifier_value == data_subject_identifier
               )
           )
           subject = data_subject.scalar_one_or_none()
           
           if not subject:
               subject = DataSubject(
                   tenant_id=tenant_id,
                   identifier_type=identifier_type,
                   identifier_value=data_subject_identifier
               )
               self.db.add(subject)
               await self.db.flush()
           
           # Calculate deadline
           deadline_days = JURISDICTION_DEADLINES.get(jurisdiction, 30)
           deadline = datetime.utcnow() + timedelta(days=deadline_days)
           
           # Create request
           request = DataSubjectAccessRequest(
               tenant_id=tenant_id,
               data_subject_id=subject.id,
               request_type=request_type,
               received_at=datetime.utcnow(),
               received_via=received_via,
               jurisdiction=jurisdiction,
               deadline=deadline,
               status='received',
               requestor_email=requestor_email,
               preferred_delivery=preferred_delivery
           )
           
           self.db.add(request)
           await self.db.commit()
           
           # Emit event
           from core.events.domain_events import DsarReceived
           event = DsarReceived(
               event_id=str(uuid4()),
               tenant_id=tenant_id,
               aggregate_id=request.id,
               aggregate_type='DsarRequest',
               request_type=request_type,
               jurisdiction=jurisdiction,
               deadline=deadline,
               timestamp=datetime.utcnow()
           )
           
           await self.event_bus.publish(event)
           
           return request
       
       async def get_overdue_requests(self) -> List[DataSubjectAccessRequest]:
           """Get requests approaching or past deadline"""
           
           tenant_id = get_tenant_id()
           now = datetime.utcnow()
           
           stmt = select(DataSubjectAccessRequest).where(
               DataSubjectAccessRequest.tenant_id == tenant_id,
               DataSubjectAccessRequest.deadline <= now.replace(hour=23, minute=59),
               DataSubjectAccessRequest.status != 'delivered',
               DataSubjectAccessRequest.status != 'refused'
           )
           
           result = await self.db.execute(stmt)
           return result.scalars().all()
   ```

3. **services/dsar_scope_service.py**: Determine what data to include
   ```python
   from core.models.dsar_request import DsarScope, RequestedDataElement
   
   class DsarScopeService:
       def __init__(self, db: Session):
           self.db = db
       
       async def determine_scope(
           self,
           request_id: str
       ) -> DsarScope:
           """Determine which systems/data categories apply"""
           
           request = await self.db.get(DataSubjectAccessRequest, request_id)
           if not request:
               return None
           
           # Get all systems that process personal data
           from core.models.assets import System
           
           stmt = select(System).where(
               System.tenant_id == request.tenant_id,
               System.data_categories.contains(
                   ['PersonalInformation', 'SensitiveData', 'ChildrensData']
               )
           )
           
           result = await self.db.execute(stmt)
           systems = result.scalars().all()
           
           # Create scope
           scope = DsarScope(
               tenant_id=request.tenant_id,
               request_id=request_id,
               systems_in_scope=[str(s.id) for s in systems],
               data_categories=['PersonalInformation', 'PaymentInfo', 'LocationData'],
               scope_determined_at=datetime.utcnow()
           )
           
           # Create collection tasks
           for system in systems:
               for category in scope.data_categories:
                   element = RequestedDataElement(
                       tenant_id=request.tenant_id,
                       request_id=request_id,
                       system_id=str(system.id),
                       data_category=category,
                       field_name='all',
                       status='pending'
                   )
                   self.db.add(element)
           
           self.db.add(scope)
           await self.db.commit()
           
           return scope
   ```

4. **services/dsar_redaction_service.py**: Redaction engine
   ```python
   from core.models.dsar_redaction import AppliedRedaction
   import re
   
   class DsarRedactionService:
       def __init__(self, db: Session):
           self.db = db
       
       async def apply_redactions(
           self,
           request_id: str,
           data: dict
       ) -> dict:
           """Apply redaction rules to data before delivery"""
           
           redacted_data = json.loads(json.dumps(data))  # Deep copy
           
           # Get redaction rules
           rules = await self._get_redaction_rules()
           
           # Apply each rule
           for rule in rules:
               redacted_data = self._apply_rule(redacted_data, rule)
           
           return redacted_data
       
       def _apply_rule(self, data: dict, rule: dict) -> dict:
           """Apply single redaction rule"""
           
           rule_type = rule['type']  # email_mask, phone_mask, confidential, legal_privilege
           
           if rule_type == 'email_mask':
               # Mask email addresses: user***@domain.com
               pattern = r'(\w+)@(\w+\.\w+)'
               return {
                   k: re.sub(pattern, r'\1***@\2', str(v)) if isinstance(v, str) else v
                   for k, v in data.items()
               }
           
           elif rule_type == 'phone_mask':
               # Mask phone: ***-***-1234
               pattern = r'\d{3}-\d{3}-(\d{4})'
               return {
                   k: re.sub(pattern, r'***-***-\1', str(v)) if isinstance(v, str) else v
                   for k, v in data.items()
               }
           
           elif rule_type == 'ssn_mask':
               # Mask SSN: ***-**-1234
               pattern = r'\d{3}-\d{2}-(\d{4})'
               return {
                   k: re.sub(pattern, r'***-**-\1', str(v)) if isinstance(v, str) else v
                   for k, v in data.items()
               }
           
           return data
       
       async def _get_redaction_rules(self) -> List[dict]:
           """Get redaction rules from config"""
           # Load from YAML or database
           return [
               {'type': 'email_mask', 'fields': ['email', 'sender', 'recipient']},
               {'type': 'phone_mask', 'fields': ['phone', 'mobile']},
               {'type': 'ssn_mask', 'fields': ['ssn', 'social_security']},
           ]
   ```

5. **workflows/dsar_fulfillment.py**: LangGraph DSAR workflow
   ```python
   from langgraph.graph import StateGraph, START, END
   from langgraph.constants import Send
   
   class DsarState(TypedDict):
       request_id: str
       status: str
       scope: dict
       collected_data: dict
       redacted_data: dict
       verification_complete: bool
       package_ready: bool
   
   async def verify_subject(state: DsarState, service: DsarIntakeService):
       """Verify data subject identity"""
       # Implement verification logic
       return {'status': 'pending_verification' if verified else 'received'}
   
   async def determine_scope(state: DsarState, service: DsarScopeService):
       """Determine which data to include"""
       scope = await service.determine_scope(state['request_id'])
       return {'scope': scope, 'status': 'scoping'}
   
   async def collect_data(state: DsarState, service: DsarCollectionService):
       """Collect data from all relevant systems"""
       data = await service.collect_data(state['request_id'], state['scope'])
       return {'collected_data': data, 'status': 'collecting'}
   
   async def apply_redactions(state: DsarState, service: DsarRedactionService):
       """Apply redaction rules"""
       redacted = await service.apply_redactions(state['request_id'], state['collected_data'])
       return {'redacted_data': redacted, 'status': 'redacting'}
   
   async def prepare_package(state: DsarState, service: DsarDeliveryService):
       """Package data for delivery"""
       package = await service.prepare_package(state['request_id'], state['redacted_data'])
       return {'package_ready': True, 'status': 'ready'}
   
   async def deliver_data(state: DsarState, service: DsarDeliveryService):
       """Deliver to data subject"""
       await service.deliver_package(state['request_id'])
       return {'status': 'delivered'}
   
   # Build workflow
   workflow = StateGraph(DsarState)
   workflow.add_node('verify', verify_subject)
   workflow.add_node('scope', determine_scope)
   workflow.add_node('collect', collect_data)
   workflow.add_node('redact', apply_redactions)
   workflow.add_node('package', prepare_package)
   workflow.add_node('deliver', deliver_data)
   
   workflow.add_edge(START, 'verify')
   workflow.add_edge('verify', 'scope')
   workflow.add_edge('scope', 'collect')
   workflow.add_edge('collect', 'redact')
   workflow.add_edge('redact', 'package')
   workflow.add_edge('package', 'deliver')
   workflow.add_edge('deliver', END)
   
   dsar_fulfillment_graph = workflow.compile()
   ```

TESTING STRATEGY:

```python
@pytest.mark.asyncio
async def test_dsar_deadline_calculation():
    # Receive GDPR request
    request = await intake_service.receive_request(
        request_type='access',
        jurisdiction='GDPR',
        data_subject_identifier='user@example.com',
        identifier_type='email'
    )
    
    # Deadline should be 30 days from now
    expected = datetime.utcnow() + timedelta(days=30)
    assert (request.deadline - expected).total_seconds() < 60  # Within 1 minute

@pytest.mark.asyncio
async def test_redaction_masks_pii():
    # Test email masking
    data = {'email': 'john.doe@example.com', 'name': 'John Doe'}
    redacted = await redaction_service.apply_redactions('request-1', data)
    
    assert redacted['email'] == 'john***@example.com'
    assert redacted['name'] == 'John Doe'  # Not masked

@pytest.mark.asyncio
async def test_dsar_workflow_end_to_end():
    # Create request
    request = await intake_service.receive_request(...)
    
    # Run workflow
    result = await dsar_fulfillment_graph.ainvoke({
        'request_id': request.id,
        'status': 'received'
    })
    
    assert result['status'] == 'delivered'
    assert result['package_ready'] == True
```

INTEGRATION WITH PHASE 1:

✅ Multi-tenancy isolation (Module 2)
✅ Events for status changes (Module 3)
✅ Audit trail for all DSAR steps (Module 4)
✅ User management from existing code
```

---

## ACCEPTANCE CRITERIA

- [ ] DSAR requests tracked end-to-end
- [ ] Deadlines calculated per jurisdiction
- [ ] Data collection from all relevant systems
- [ ] Redaction rules applied before delivery
- [ ] Verification prevents incomplete packages
- [ ] Audit trail tracks all steps
- [ ] Email/download delivery working
- [ ] Tests verify accuracy of deadline calculation
- [ ] Performance: Deliver within SLA (< deadline)

---

## NEXT MODULE

After MODULE 6, proceed to MODULE 7: Breach/Incident Management (4 weeks)

