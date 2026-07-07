# MODULE 3: EVENT-DRIVEN ARCHITECTURE
## For Antigravity IDE + Gemma4

**Duration:** 8 weeks  
**Priority:** CRITICAL  
**Effort:** High  
**Dependencies:** MODULE 1 (Domain Model), MODULE 2 (Multi-Tenancy)

---

## OVERVIEW

Replace linear LangGraph workflows with event-driven system. Assessments automatically cascade to Risks, which cascade to Controls, which update Risks.

**Current State:**
- LangGraph nodes run sequentially
- Manual API calls required for orchestration
- No automatic signal propagation
- Assessment completion doesn't trigger Risk creation

**Target State:**
- Events emitted on all state changes
- Handlers subscribe to relevant events
- Cross-module intelligence automatic
- Assessment → Risk → Control updates happen immediately

---

## MODULE OBJECTIVES

1. ✅ Create event bus (Redis Streams or Kafka)
2. ✅ Define all domain events (AssessmentCompleted, RiskCreated, ControlImplemented, etc.)
3. ✅ Implement event handlers for cascade logic
4. ✅ Update LangGraph nodes to emit events
5. ✅ Add event replay for recovery
6. ✅ Write comprehensive integration tests

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building an event-driven system for KIBO to enable automatic cross-module intelligence.

TASK: Create an event bus with handlers that automatically propagate compliance signals across the platform.

REQUIREMENTS:
1. Event Stream: Redis Streams (or Kafka if preferred)
2. Pattern: Event sourcing + event handlers
3. Tenant Awareness: All events include tenant_id
4. Idempotency: Handlers must be idempotent (safe to replay)
5. Monitoring: Track event processing + failures

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── events/
│   │   ├── __init__.py
│   │   ├── domain_events.py    # All domain events (dataclasses)
│   │   ├── event_bus.py        # EventBus interface + implementations
│   │   ├── redis_bus.py        # Redis Streams implementation
│   │   └── kafka_bus.py        # Kafka implementation (optional)
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── assessment_handlers.py   # Handle AssessmentCompleted event
│   │   ├── risk_handlers.py         # Handle RiskCreated, RiskUpdated
│   │   ├── control_handlers.py      # Handle ControlImplemented
│   │   ├── vendor_handlers.py       # Handle VendorAssessed
│   │   ├── notification_handlers.py # Send alerts on critical events
│   │   └── audit_handlers.py        # Log all events to audit trail
│   └── services/
│       ├── event_processor.py       # Main event loop + handler dispatcher
│       └── event_replay.py          # Recover from outages
└── tests/
    └── test_event_driven.py
```

IMPLEMENTATION DETAILS:

1. **events/domain_events.py**: Define all domain events
   ```python
   from dataclasses import dataclass
   from datetime import datetime
   from uuid import UUID
   from typing import Optional, Any, List
   
   @dataclass
   class DomainEvent:
       """Base class for all domain events"""
       event_id: str  # UUID
       event_type: str
       tenant_id: str
       aggregate_id: UUID  # The resource this event is about
       aggregate_type: str  # Assessment, Risk, Control, etc.
       timestamp: datetime
       user_id: Optional[str] = None
       metadata: dict = None  # Extra context
       
       def __post_init__(self):
           if not self.event_id:
               self.event_id = str(uuid4())
           if not self.timestamp:
               self.timestamp = datetime.utcnow()
   
   # Assessment Events
   @dataclass
   class AssessmentCreated(DomainEvent):
       title: str
       assessment_type: str  # PIA, DPIA, TIA
       status: str = 'draft'
   
   @dataclass
   class AssessmentSubmitted(DomainEvent):
       submitted_by: str
       legal_basis: str
   
   @dataclass
   class AssessmentApproved(DomainEvent):
       approved_by: str
       risk_score: float
       findings: str
       mitigations: List[str]
   
   @dataclass
   class AssessmentRejected(DomainEvent):
       rejected_by: str
       rejection_reason: str
   
   # Risk Events
   @dataclass
   class RiskCreated(DomainEvent):
       title: str
       severity: str  # low, medium, high, critical
       source_assessment_id: UUID  # Which assessment triggered this
       risk_score: float
       mitigation_required: bool
   
   @dataclass
   class RiskStatusChanged(DomainEvent):
       new_status: str  # open, mitigated, accepted
       old_status: str
       reason: Optional[str] = None
   
   @dataclass
   class RiskAccepted(DomainEvent):
       accepted_by: str
       acceptance_date: datetime
       justification: str
   
   # Control Events
   @dataclass
   class ControlImplemented(DomainEvent):
       control_id: UUID
       implementation_date: datetime
       implemented_in_systems: List[UUID]  # Which systems have this control
   
   @dataclass
   class ControlTested(DomainEvent):
       test_date: datetime
       test_result: str  # effective, partially_effective, ineffective
       evidence: str  # Summary of test evidence
   
   # Vendor Events
   @dataclass
   class VendorAssessed(DomainEvent):
       vendor_id: UUID
       assessment_type: str  # security, privacy, financial
       risk_level: str  # low, medium, high, critical
   
   @dataclass
   class VendorDPAExpiring(DomainEvent):
       vendor_id: UUID
       days_until_expiry: int
       expiry_date: datetime
   
   # System Events
   @dataclass
   class SystemReclassified(DomainEvent):
       system_id: UUID
       old_classification: str
       new_classification: str  # low → high
   
   @dataclass
   class DataFlowChanged(DomainEvent):
       source_system: UUID
       destination_system: UUID
       data_categories: List[str]
   
   # Regulation Events
   @dataclass
   class RegulationUpdated(DomainEvent):
       regulation_name: str  # e.g., "GDPR Article 35"
       effective_date: datetime
       impact_summary: str
   
   # Compliance Events
   @dataclass
   class ComplianceGapIdentified(DomainEvent):
       gap_description: str
       affected_systems: List[UUID]
       affected_processes: List[UUID]
       remediation_priority: str  # critical, high, medium, low
   ```

2. **events/event_bus.py**: Event bus interface
   ```python
   from abc import ABC, abstractmethod
   from typing import Callable, List, Type
   from core.events.domain_events import DomainEvent
   
   class EventBus(ABC):
       """Abstract event bus interface"""
       
       @abstractmethod
       async def publish(self, event: DomainEvent) -> None:
           """Publish an event to the event stream"""
           pass
       
       @abstractmethod
       async def subscribe(
           self,
           event_type: Type[DomainEvent],
           handler: Callable[[DomainEvent], None]
       ) -> None:
           """Subscribe to events of a specific type"""
           pass
       
       @abstractmethod
       async def process_events(self) -> None:
           """Main event loop - continuously process events"""
           pass
   
   # In-memory event bus (for testing)
   class InMemoryEventBus(EventBus):
       def __init__(self):
           self.events: List[DomainEvent] = []
           self.handlers: dict[Type[DomainEvent], List[Callable]] = {}
       
       async def publish(self, event: DomainEvent) -> None:
           self.events.append(event)
           
           # Call handlers synchronously
           event_type = type(event)
           handlers = self.handlers.get(event_type, [])
           for handler in handlers:
               await handler(event)
       
       async def subscribe(
           self,
           event_type: Type[DomainEvent],
           handler: Callable[[DomainEvent], None]
       ) -> None:
           if event_type not in self.handlers:
               self.handlers[event_type] = []
           self.handlers[event_type].append(handler)
   ```

3. **events/redis_bus.py**: Redis Streams implementation
   ```python
   import json
   import asyncio
   from redis.asyncio import Redis
   from core.events.domain_events import DomainEvent
   from core.events.event_bus import EventBus
   
   class RedisEventBus(EventBus):
       def __init__(self, redis: Redis, stream_name: str = 'compliance_events'):
           self.redis = redis
           self.stream_name = stream_name
           self.handlers: dict[str, List[Callable]] = {}
           self.consumer_group = 'event_processors'
       
       async def publish(self, event: DomainEvent) -> None:
           """Publish event to Redis Stream"""
           event_data = {
               'event_id': event.event_id,
               'event_type': event.event_type,
               'tenant_id': event.tenant_id,
               'aggregate_id': str(event.aggregate_id),
               'aggregate_type': event.aggregate_type,
               'timestamp': event.timestamp.isoformat(),
               'user_id': event.user_id,
               'payload': json.dumps(event.__dict__, default=str)
           }
           
           # Add to Redis Stream
           await self.redis.xadd(
               self.stream_name,
               event_data,
               maxlen=1000000  # Keep last 1M events
           )
           
           # Also publish to pub/sub for real-time subscribers
           await self.redis.publish(
               f'events:{event.tenant_id}',
               json.dumps(event_data)
           )
       
       async def subscribe(
           self,
           event_type: str,  # e.g., 'AssessmentApproved'
           handler: Callable[[DomainEvent], None]
       ) -> None:
           """Subscribe to event type"""
           if event_type not in self.handlers:
               self.handlers[event_type] = []
           self.handlers[event_type].append(handler)
       
       async def process_events(self) -> None:
           """Main event loop - process events from stream"""
           # Create consumer group if not exists
           try:
               await self.redis.xgroup_create(
                   self.stream_name,
                   self.consumer_group,
                   id='0',
                   mkstream=True
               )
           except:
               pass  # Group already exists
           
           while True:
               # Read events from stream
               events = await self.redis.xreadgroup(
                   {self.stream_name: '>'},
                   self.consumer_group,
                   count=10,
                   block=1000  # 1 second timeout
               )
               
               for stream, messages in events:
                   for message_id, data in messages:
                       try:
                           event_type = data.get(b'event_type').decode()
                           payload = json.loads(
                               data.get(b'payload').decode()
                           )
                           
                           # Call handlers for this event type
                           handlers = self.handlers.get(event_type, [])
                           for handler in handlers:
                               await handler(payload)
                           
                           # Acknowledge message
                           await self.redis.xack(
                               self.stream_name,
                               self.consumer_group,
                               message_id
                           )
                       except Exception as e:
                           print(f"Error processing event: {e}")
                           # Move to dead-letter queue
                           await self.redis.xadd(
                               f'{self.stream_name}:dlq',
                               {'error': str(e), 'message_id': message_id}
                           )
   ```

4. **handlers/assessment_handlers.py**: Assessment event handlers
   ```python
   from sqlalchemy.orm import Session
   from core.models import Assessment, Risk
   from core.events.domain_events import AssessmentApproved
   from core.context.tenant_context import set_tenant_context
   
   class AssessmentHandlers:
       def __init__(self, db: Session, event_bus):
           self.db = db
           self.event_bus = event_bus
       
       async def on_assessment_approved(self, event: AssessmentApproved):
           """
           When an assessment is approved:
           1. Create Risk entry if risk_score > threshold
           2. Emit RiskCreated event
           3. Notify DPO if critical risk
           4. Update compliance dashboard
           """
           
           # Set tenant context from event
           set_tenant_context(event.tenant_id)
           
           # Get assessment
           assessment = await self.db.get(Assessment, event.aggregate_id)
           if not assessment:
               print(f"Assessment {event.aggregate_id} not found")
               return
           
           # If risk score is high, create Risk entry
           if event.risk_score >= 7.0:
               risk = Risk(
                   tenant_id=event.tenant_id,
                   title=f"Risk from assessment: {assessment.title}",
                   description=event.findings,
                   severity=self._score_to_severity(event.risk_score),
                   risk_score=event.risk_score,
                   source_assessment_id=event.aggregate_id,
                   risk_owner=assessment.assigned_to,
                   status='open'
               )
               
               self.db.add(risk)
               await self.db.commit()
               
               # Emit RiskCreated event
               from core.events.domain_events import RiskCreated
               risk_event = RiskCreated(
                   event_id=str(uuid4()),
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
               
               # Notify DPO if critical
               if event.risk_score >= 8.5:
                   from core.events.domain_events import CriticalRiskNotification
                   notification = CriticalRiskNotification(...)
                   await self.event_bus.publish(notification)
       
       def _score_to_severity(self, score: float) -> str:
           if score >= 9.0:
               return 'critical'
           elif score >= 7.0:
               return 'high'
           elif score >= 5.0:
               return 'medium'
           else:
               return 'low'
   
   def register_assessment_handlers(event_bus, db):
       handlers = AssessmentHandlers(db, event_bus)
       event_bus.subscribe('AssessmentApproved', handlers.on_assessment_approved)
   ```

5. **handlers/risk_handlers.py**: Risk event handlers
   ```python
   from core.events.domain_events import RiskCreated, ControlImplemented
   from core.models import Risk, Control
   
   class RiskHandlers:
       def __init__(self, db: Session, event_bus):
           self.db = db
           self.event_bus = event_bus
       
       async def on_control_implemented(self, event: ControlImplemented):
           """
           When a control is implemented:
           1. Find all risks that this control mitigates
           2. Recalculate residual risk scores
           3. If residual risk ≤ tolerance, update status to 'mitigated'
           4. Emit RiskStatusChanged event
           """
           
           # Get control
           control = await self.db.get(Control, event.control_id)
           if not control:
               return
           
           # Find risks that this control mitigates
           risks = await self.db.execute(
               select(Risk).where(Risk.mitigations.contains(event.control_id))
           )
           
           for risk in risks.scalars():
               # Recalculate residual risk
               new_residual_score = self._calculate_residual_risk(risk, control)
               old_status = risk.status
               
               risk.residual_risk_score = new_residual_score
               
               # Check if now mitigated
               if new_residual_score <= risk.risk_tolerance:
                   risk.status = 'mitigated'
               
               self.db.add(risk)
           
           await self.db.commit()
           
           # Emit RiskStatusChanged events
           from core.events.domain_events import RiskStatusChanged
           for risk in risks.scalars():
               if risk.status != old_status:
                   event = RiskStatusChanged(
                       event_id=str(uuid4()),
                       tenant_id=event.tenant_id,
                       aggregate_id=risk.id,
                       aggregate_type='Risk',
                       new_status=risk.status,
                       old_status=old_status,
                       reason=f"Control {control.title} implemented",
                       timestamp=datetime.utcnow()
                   )
                   await self.event_bus.publish(event)
       
       def _calculate_residual_risk(self, risk: Risk, control: Control) -> float:
           # Residual risk = inherent risk × (1 - control effectiveness)
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
   ```

6. **services/event_processor.py**: Main event loop
   ```python
   import asyncio
   from core.events.event_bus import EventBus
   from core.handlers.assessment_handlers import register_assessment_handlers
   from core.handlers.risk_handlers import register_risk_handlers
   from core.handlers.control_handlers import register_control_handlers
   
   class EventProcessor:
       def __init__(self, event_bus: EventBus, db):
           self.event_bus = event_bus
           self.db = db
           self._register_handlers()
       
       def _register_handlers(self):
           """Register all event handlers"""
           register_assessment_handlers(self.event_bus, self.db)
           register_risk_handlers(self.event_bus, self.db)
           register_control_handlers(self.event_bus, self.db)
       
       async def start(self):
           """Start the event processing loop"""
           print("Event processor started")
           await self.event_bus.process_events()
   
   # In main.py or app startup
   @app.on_event('startup')
   async def startup():
       redis = await Redis.from_url(settings.REDIS_URL)
       event_bus = RedisEventBus(redis)
       event_processor = EventProcessor(event_bus, db)
       
       # Run event processor in background
       asyncio.create_task(event_processor.start())
       
       # Store in app.state for injection
       app.state.event_bus = event_bus
   ```

7. **Integration with LangGraph nodes**:
   ```python
   # Before: No event emission
   def phipa_tra_node(state: AgentState) -> Dict[str, Any]:
       # ... run assessment ...
       return {"artifacts": [art]}
   
   # After: Emit event
   async def phipa_tra_node(state: AgentState, event_bus: EventBus) -> Dict[str, Any]:
       # ... run assessment ...
       
       # Emit AssessmentApproved event
       from core.events.domain_events import AssessmentApproved
       event = AssessmentApproved(
           event_id=str(uuid4()),
           event_type='AssessmentApproved',
           tenant_id=state['tenant_id'],
           aggregate_id=state['id'],
           aggregate_type='Assessment',
           approved_by=state['user_id'],
           risk_score=score,
           findings=art['findings'],
           mitigations=art.get('mitigations', []),
           timestamp=datetime.utcnow()
       )
       
       await event_bus.publish(event)
       
       return {"artifacts": [art]}
   ```

TESTING STRATEGY:

1. **test_event_driven.py**: Integration tests
   ```python
   @pytest.mark.asyncio
   async def test_assessment_approved_creates_risk():
       # Setup
       assessment = await create_assessment(
           tenant_id='tenant-a',
           title='High-Risk Assessment',
           risk_score=8.5
       )
       
       # Publish AssessmentApproved event
       event = AssessmentApproved(
           event_id=str(uuid4()),
           tenant_id='tenant-a',
           aggregate_id=assessment.id,
           aggregate_type='Assessment',
           approved_by='user@acme.com',
           risk_score=8.5,
           findings='High risk found',
           mitigations=['mitigation1']
       )
       
       await event_bus.publish(event)
       
       # Verify Risk was created
       risks = await risk_repo.list_all_for_tenant('tenant-a')
       assert len(risks) == 1
       assert risks[0].source_assessment_id == assessment.id
   
   @pytest.mark.asyncio
   async def test_control_implementation_updates_risk():
       # Create risk + control
       risk = await create_risk(score=8.0, status='open')
       control = await create_control(effectiveness='effective')
       risk.mitigations = [control.id]
       
       # Publish ControlImplemented event
       event = ControlImplemented(
           event_id=str(uuid4()),
           tenant_id='tenant-a',
           aggregate_id=control.id,
           control_id=control.id,
           implementation_date=datetime.utcnow(),
           implemented_in_systems=[...]
       )
       
       await event_bus.publish(event)
       
       # Verify risk status changed to 'mitigated'
       updated_risk = await risk_repo.get_by_id(risk.id)
       assert updated_risk.status == 'mitigated'
       assert updated_risk.residual_risk_score < 8.0
   ```

DEPLOYMENT:

✅ Start Redis or Kafka
✅ Initialize event bus in app startup
✅ Register all event handlers
✅ Start event processor background loop
✅ Monitor event processing lag
✅ Set up dead-letter queue for failed events
✅ Test event replay recovery

MONITORING:

✅ Track event throughput (events/sec)
✅ Track handler latency (ms)
✅ Monitor dead-letter queue size
✅ Alert on processing lag > 1 minute
✅ Log all event emissions for audit
```

---

## ACCEPTANCE CRITERIA

- [ ] AssessmentApproved → RiskCreated (automatic)
- [ ] RiskCreated → Risk entry in DB (automatic)
- [ ] ControlImplemented → Risk status updated (automatic)
- [ ] All events include tenant_id (no cross-tenant)
- [ ] Event handlers are idempotent (safe to replay)
- [ ] Dead-letter queue for failed events
- [ ] Event throughput > 1000 events/sec
- [ ] Handler latency < 100ms median
- [ ] Event processing lag < 1 minute
- [ ] Tests verify cascade behavior

---

## NEXT STEPS AFTER MODULE 3

Once event-driven system is operational, MODULE 4 (Audit Logging) can:
- Log all events to immutable audit trail
- Implement event replay for compliance audits
- Track data access per event

