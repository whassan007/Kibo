# MODULE 5: VENDOR RISK MANAGEMENT
## For Antigravity IDE + Gemma4

**Duration:** 6 weeks  
**Priority:** HIGH  
**Effort:** High  
**Dependencies:** MODULE 1-4 (Phase 1 complete)

---

## OVERVIEW

Implement comprehensive vendor risk assessment and monitoring. Track vendor assessments, DPA status, SOC2 compliance, and auto-trigger renewal workflows.

**Current State:**
- No vendor risk tracking
- Manual DPA expiration monitoring
- No assessment templates
- No risk scoring

**Target State:**
- Vendor assessment framework with scoring
- DPA status dashboard
- Auto-renewal notifications (30/7 days before expiry)
- Sub-processor tracking
- Risk-based compliance monitoring

---

## MODULE OBJECTIVES

1. ✅ Create Vendor Assessment entities + scoring
2. ✅ Implement assessment templates (Security, Privacy, Financial)
3. ✅ Build vendor dashboard with risk heatmap
4. ✅ Create DPA renewal workflow + notifications
5. ✅ Implement sub-processor registry
6. ✅ Add vendor audit trails and evidence

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building a vendor risk management system for KIBO to track third-party risks and compliance.

TASK: Create comprehensive vendor assessment and risk management workflows.

REQUIREMENTS:
1. Vendor Assessment Framework: Security, Privacy, Financial, Operational
2. Risk Scoring: 0-100 scale with configurable thresholds
3. DPA Management: Track status, expiry, renewal triggers
4. Sub-processor Registry: Nested vendor relationships
5. Notifications: Auto-trigger on risk changes, DPA expiry
6. Audit Trail: All vendor changes logged with evidence

FILE STRUCTURE:
```
kibo-is/
├── core/
│   ├── models/
│   │   ├── vendor_assessment.py   # VendorAssessment, AssessmentResult
│   │   ├── vendor_dpa.py          # DPA, StandardContractualClause
│   │   ├── vendor_evidence.py     # AssessmentEvidence, SOC2Certificate
│   │   └── subprocessor.py        # SubprocessorRegistry, DataTransfer
│   ├── services/
│   │   ├── vendor_assessment_service.py
│   │   ├── vendor_risk_service.py
│   │   ├── dpa_management_service.py
│   │   └── subprocessor_service.py
│   ├── workflows/
│   │   ├── vendor_onboarding.py   # LangGraph workflow
│   │   └── dpa_renewal.py         # DPA renewal workflow
│   └── templates/
│       ├── assessment_templates.py
│       └── vendor_questionnaires.py
├── api/
│   └── v1/
│       ├── vendors.py
│       ├── assessments.py
│       ├── dpas.py
│       └── subprocessors.py
└── tests/
    └── test_vendor_risk.py
```

IMPLEMENTATION DETAILS:

1. **models/vendor_assessment.py**: Assessment framework
   ```python
   from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Enum
   from core.models.base import VersionedEntity, TenantScoped
   
   class AssessmentTemplate(VersionedEntity, TenantScoped):
       __tablename__ = 'assessment_templates'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       assessment_type = Column(String)  # security, privacy, financial, operational
       name = Column(String)
       description = Column(Text)
       questions = Column(JSON)  # {q1: {text, weight, options}, ...}
       scoring_rubric = Column(JSON)  # How to score answers
       
       # Risk thresholds
       critical_threshold = Column(Float, default=85)  # >= 85 = critical
       high_threshold = Column(Float, default=70)
       medium_threshold = Column(Float, default=50)
       
       created_by = Column(String)
       created_at = Column(DateTime, default=datetime.utcnow)
   
   class VendorAssessment(VersionedEntity, TenantScoped):
       __tablename__ = 'vendor_assessments'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       vendor_id = Column(UUID, ForeignKey('assets.id'))
       assessment_type = Column(String)  # security, privacy, financial
       framework = Column(String)  # ISO27001, SOC2, NIST, Custom
       
       # Status
       status = Column(String)  # draft, in_progress, completed, approved, conditional, blocked
       started_at = Column(DateTime)
       completed_at = Column(DateTime, nullable=True)
       
       # Scoring
       risk_score = Column(Float)  # 0-100
       risk_level = Column(String)  # low, medium, high, critical
       
       # Assessment details
       assessor_id = Column(String, ForeignKey('users.id'))
       attestation_document = Column(String, nullable=True)  # File path
       
       # Evidence & findings
       findings = Column(JSON)  # List of issues found
       recommendations = Column(JSON)  # Recommended mitigations
       
       # Renewal
       expiry_date = Column(DateTime, nullable=True)
       renewal_triggered_at = Column(DateTime, nullable=True)
       
       # Relationships
       vendor = relationship('Vendor', back_populates='assessments')
       results = relationship('AssessmentResult', back_populates='assessment')
       evidence = relationship('AssessmentEvidence', back_populates='assessment')
   
   class AssessmentResult(VersionedEntity, TenantScoped):
       __tablename__ = 'assessment_results'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       assessment_id = Column(UUID, ForeignKey('vendor_assessments.id'))
       question_id = Column(String)
       answer = Column(String)  # Answer text
       score = Column(Float)  # 0-10
       evidence = Column(Text)  # Supporting evidence
       
       assessment = relationship('VendorAssessment', back_populates='results')
   
   class AssessmentEvidence(VersionedEntity, TenantScoped):
       __tablename__ = 'assessment_evidence'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       assessment_id = Column(UUID, ForeignKey('vendor_assessments.id'))
       evidence_type = Column(String)  # document, certificate, audit_report, attestation
       title = Column(String)
       file_path = Column(String)
       file_hash = Column(String)  # SHA256
       
       uploaded_at = Column(DateTime, default=datetime.utcnow)
       uploaded_by = Column(String)
       expires_at = Column(DateTime, nullable=True)
       
       assessment = relationship('VendorAssessment', back_populates='evidence')
   ```

2. **models/vendor_dpa.py**: Data Processing Agreements
   ```python
   from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
   
   class DataProcessingAgreement(VersionedEntity, TenantScoped):
       __tablename__ = 'data_processing_agreements'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       vendor_id = Column(UUID, ForeignKey('assets.id'), nullable=False)
       dpa_type = Column(String)  # Data Processing Agreement, Sub-processor Agreement
       
       # Status
       status = Column(String)  # draft, pending_signature, executed, expired, terminated
       
       # Dates
       execution_date = Column(DateTime, nullable=True)
       effective_date = Column(DateTime, nullable=True)
       expiry_date = Column(DateTime, nullable=True)
       renewal_date = Column(DateTime, nullable=True)
       
       # Content
       agreement_document = Column(String)  # File path
       standard_contractual_clauses = Column(Boolean, default=False)
       standard_contractual_clauses_version = Column(String, nullable=True)
       
       # Compliance
       cross_border_transfer = Column(Boolean, default=False)
       source_jurisdiction = Column(String, nullable=True)
       destination_jurisdiction = Column(String, nullable=True)
       adequacy_decision = Column(Boolean, nullable=True)  # Is destination adequate?
       
       # Approvals
       approved_by = Column(String, ForeignKey('users.id'), nullable=True)
       approved_at = Column(DateTime, nullable=True)
       dpo_review_date = Column(DateTime, nullable=True)
       dpo_approval = Column(Boolean, nullable=True)
       
       # Tracking
       renewal_notifications_sent = Column(JSON, default={})  # {30_days: date, 7_days: date}
       last_reviewed_at = Column(DateTime, nullable=True)
       last_reviewed_by = Column(String, nullable=True)
       
       vendor = relationship('Vendor')
   
   class StandardContractualClause(Base, TenantScoped):
       __tablename__ = 'standard_contractual_clauses'
       id = Column(UUID, primary_key=True, default=uuid4)
       
       dpa_id = Column(UUID, ForeignKey('data_processing_agreements.id'))
       clause_type = Column(String)  # Module One, Module Two, Module Three, Module Four
       module_description = Column(String)
       exporter_role = Column(String)  # Data Exporter
       importer_role = Column(String)  # Data Importer
       
       included = Column(Boolean, default=True)
       effective_date = Column(DateTime, default=datetime.utcnow)
   ```

3. **services/vendor_risk_service.py**: Risk calculation
   ```python
   from sqlalchemy import select
   from core.models.vendor_assessment import VendorAssessment, AssessmentResult
   
   class VendorRiskService:
       def __init__(self, db: Session):
           self.db = db
       
       async def calculate_risk_score(
           self,
           assessment_id: str
       ) -> dict:
           """Calculate vendor risk score from assessment results"""
           
           assessment = await self.db.get(VendorAssessment, assessment_id)
           if not assessment:
               return None
           
           # Get all results for this assessment
           stmt = select(AssessmentResult).where(
               AssessmentResult.assessment_id == assessment_id
           )
           result = await self.db.execute(stmt)
           results = result.scalars().all()
           
           if not results:
               return None
           
           # Calculate weighted score
           total_score = sum(r.score for r in results)
           average_score = total_score / len(results) * 10  # Convert to 0-100
           
           # Determine risk level
           if average_score >= 85:
               risk_level = 'critical'
           elif average_score >= 70:
               risk_level = 'high'
           elif average_score >= 50:
               risk_level = 'medium'
           else:
               risk_level = 'low'
           
           assessment.risk_score = average_score
           assessment.risk_level = risk_level
           self.db.add(assessment)
           await self.db.commit()
           
           # Emit event
           from core.events.domain_events import VendorAssessed
           event = VendorAssessed(
               event_id=str(uuid4()),
               tenant_id=get_tenant_id(),
               aggregate_id=assessment.vendor_id,
               aggregate_type='Vendor',
               vendor_id=assessment.vendor_id,
               assessment_type=assessment.assessment_type,
               risk_level=risk_level,
               timestamp=datetime.utcnow(),
               user_id=assessment.assessor_id
           )
           
           await event_bus.publish(event)
           
           return {
               'risk_score': average_score,
               'risk_level': risk_level,
               'assessment_id': assessment_id
           }
       
       async def get_vendor_risk_summary(
           self,
           vendor_id: str
       ) -> dict:
           """Get overall vendor risk across all assessments"""
           
           tenant_id = get_tenant_id()
           
           # Get all assessments for vendor
           stmt = select(VendorAssessment).where(
               VendorAssessment.tenant_id == tenant_id,
               VendorAssessment.vendor_id == vendor_id,
               VendorAssessment.status == 'completed'
           ).order_by(VendorAssessment.completed_at.desc())
           
           result = await self.db.execute(stmt)
           assessments = result.scalars().all()
           
           if not assessments:
               return None
           
           # Calculate overall risk
           security_risk = next(
               (a.risk_score for a in assessments if a.assessment_type == 'security'),
               None
           )
           privacy_risk = next(
               (a.risk_score for a in assessments if a.assessment_type == 'privacy'),
               None
           )
           financial_risk = next(
               (a.risk_score for a in assessments if a.assessment_type == 'financial'),
               None
           )
           
           # Weighted average
           weights = {'security': 0.4, 'privacy': 0.35, 'financial': 0.25}
           overall_score = (
               (security_risk or 50) * weights['security'] +
               (privacy_risk or 50) * weights['privacy'] +
               (financial_risk or 50) * weights['financial']
           )
           
           return {
               'vendor_id': vendor_id,
               'overall_risk_score': overall_score,
               'security_risk': security_risk,
               'privacy_risk': privacy_risk,
               'financial_risk': financial_risk,
               'assessments': [
                   {
                       'type': a.assessment_type,
                       'score': a.risk_score,
                       'level': a.risk_level,
                       'completed_at': a.completed_at.isoformat()
                   }
                   for a in assessments
               ]
           }
   ```

4. **services/dpa_management_service.py**: DPA lifecycle
   ```python
   from datetime import datetime, timedelta
   from core.models.vendor_dpa import DataProcessingAgreement
   from core.events.domain_events import VendorDPAExpiring
   
   class DPAManagementService:
       def __init__(self, db: Session, event_bus):
           self.db = db
           self.event_bus = event_bus
       
       async def check_dpa_expiry(self):
           """Check for expiring DPAs and trigger notifications"""
           
           tenant_id = get_tenant_id()
           now = datetime.utcnow()
           thirty_days = now + timedelta(days=30)
           seven_days = now + timedelta(days=7)
           
           # Find DPAs expiring in 30 days
           stmt = select(DataProcessingAgreement).where(
               DataProcessingAgreement.tenant_id == tenant_id,
               DataProcessingAgreement.expiry_date <= thirty_days,
               DataProcessingAgreement.expiry_date > now,
               DataProcessingAgreement.status == 'executed'
           )
           
           result = await self.db.execute(stmt)
           expiring_dpas = result.scalars().all()
           
           for dpa in expiring_dpas:
               days_until_expiry = (dpa.expiry_date - now).days
               
               # Check if we already sent 30-day notification
               if '30_days' not in (dpa.renewal_notifications_sent or {}):
                   # Emit event
                   event = VendorDPAExpiring(
                       event_id=str(uuid4()),
                       tenant_id=tenant_id,
                       aggregate_id=dpa.vendor_id,
                       aggregate_type='Vendor',
                       vendor_id=dpa.vendor_id,
                       days_until_expiry=days_until_expiry,
                       expiry_date=dpa.expiry_date,
                       timestamp=datetime.utcnow()
                   )
                   
                   await self.event_bus.publish(event)
                   
                   # Mark notification sent
                   dpa.renewal_notifications_sent = dpa.renewal_notifications_sent or {}
                   dpa.renewal_notifications_sent['30_days'] = now.isoformat()
                   self.db.add(dpa)
               
               # Create renewal task
               if days_until_expiry <= 30:
                   from core.models.task import Task
                   task = Task(
                       tenant_id=tenant_id,
                       title=f"Renew DPA for {dpa.vendor.name}",
                       task_type='dpa_renewal',
                       priority='high',
                       due_date=dpa.expiry_date - timedelta(days=14),
                       linked_entity_type='Vendor',
                       linked_entity_id=dpa.vendor_id
                   )
                   self.db.add(task)
           
           await self.db.commit()
       
       async def create_dpa(
           self,
           vendor_id: str,
           dpa_type: str,
           effective_date: datetime,
           expiry_date: datetime,
           document_path: str
       ) -> DataProcessingAgreement:
           """Create new DPA"""
           
           tenant_id = get_tenant_id()
           
           dpa = DataProcessingAgreement(
               tenant_id=tenant_id,
               vendor_id=vendor_id,
               dpa_type=dpa_type,
               status='draft',
               effective_date=effective_date,
               expiry_date=expiry_date,
               agreement_document=document_path
           )
           
           self.db.add(dpa)
           await self.db.commit()
           
           return dpa
       
       async def approve_dpa(
           self,
           dpa_id: str,
           approved_by: str
       ) -> DataProcessingAgreement:
           """Approve DPA"""
           
           dpa = await self.db.get(DataProcessingAgreement, dpa_id)
           if not dpa:
               return None
           
           dpa.status = 'executed'
           dpa.approved_by = approved_by
           dpa.approved_at = datetime.utcnow()
           
           self.db.add(dpa)
           await self.db.commit()
           
           # Emit event
           from core.events.domain_events import DPAApproved
           event = DPAApproved(
               event_id=str(uuid4()),
               tenant_id=get_tenant_id(),
               aggregate_id=dpa.vendor_id,
               dpa_id=dpa_id,
               approved_by=approved_by,
               timestamp=datetime.utcnow()
           )
           
           await self.event_bus.publish(event)
           
           return dpa
   ```

5. **workflows/vendor_onboarding.py**: LangGraph vendor onboarding
   ```python
   from langgraph.graph import StateGraph, START, END
   from langgraph.constants import Send
   
   class VendorOnboardingState(TypedDict):
       vendor_id: str
       vendor_name: str
       service_type: str  # cloud, saas, consultant, etc.
       assessment_results: dict
       dpa_status: str
       risk_level: str
       approval_status: str
   
   async def assess_vendor_security(state: VendorOnboardingState, service: VendorRiskService):
       """Run security assessment"""
       # ... assessment logic ...
       return {'assessment_results': results}
   
   async def assess_vendor_privacy(state: VendorOnboardingState, service: VendorRiskService):
       """Run privacy assessment"""
       # ... assessment logic ...
       return {'assessment_results': results}
   
   async def check_dpa_requirements(state: VendorOnboardingState, service: DPAManagementService):
       """Check if DPA is required and status"""
       # ... DPA logic ...
       return {'dpa_status': status}
   
   async def approve_vendor(state: VendorOnboardingState, service: VendorRiskService):
       """Final approval decision"""
       if state['risk_level'] == 'critical':
           return {'approval_status': 'blocked', 'vendor_id': state['vendor_id']}
       elif state['risk_level'] == 'high':
           return {'approval_status': 'conditional', 'vendor_id': state['vendor_id']}
       else:
           return {'approval_status': 'approved', 'vendor_id': state['vendor_id']}
   
   # Build workflow
   workflow = StateGraph(VendorOnboardingState)
   workflow.add_node('assess_security', assess_vendor_security)
   workflow.add_node('assess_privacy', assess_vendor_privacy)
   workflow.add_node('check_dpa', check_dpa_requirements)
   workflow.add_node('approve', approve_vendor)
   
   workflow.add_edge(START, 'assess_security')
   workflow.add_edge(START, 'assess_privacy')
   workflow.add_edge('assess_security', 'check_dpa')
   workflow.add_edge('assess_privacy', 'check_dpa')
   workflow.add_edge('check_dpa', 'approve')
   workflow.add_edge('approve', END)
   
   vendor_onboarding_graph = workflow.compile()
   ```

6. **API endpoints**:
   ```python
   from fastapi import APIRouter, Depends
   
   router = APIRouter(prefix='/api/vendors', tags=['vendors'])
   
   @router.post('/{vendor_id}/assessments')
   async def create_assessment(
       vendor_id: str,
       assessment_type: str,
       framework: str,
       service: VendorRiskService = Depends()
   ):
       """Create new vendor assessment"""
       # Implementation
       pass
   
   @router.get('/{vendor_id}/risk-summary')
   async def get_vendor_risk(
       vendor_id: str,
       service: VendorRiskService = Depends()
   ):
       """Get vendor risk summary across all assessments"""
       return await service.get_vendor_risk_summary(vendor_id)
   
   @router.get('/dashboard/heatmap')
   async def get_vendor_risk_heatmap(
       service: VendorRiskService = Depends()
   ):
       """Get risk heatmap for all vendors (assessment_type x risk_level)"""
       # Implementation
       pass
   
   @router.post('/dpa/{vendor_id}/renewal')
   async def trigger_dpa_renewal(
       vendor_id: str,
       service: DPAManagementService = Depends()
   ):
       """Manually trigger DPA renewal workflow"""
       # Implementation
       pass
   ```

TESTING STRATEGY:

```python
@pytest.mark.asyncio
async def test_vendor_assessment_scoring():
    # Create assessment with results
    assessment = await create_assessment(vendor_id='vendor-1')
    result1 = await add_result(assessment_id=assessment.id, score=9.0)
    result2 = await add_result(assessment_id=assessment.id, score=8.0)
    
    # Calculate score
    summary = await risk_service.calculate_risk_score(assessment.id)
    
    assert summary['risk_score'] > 80  # High score
    assert summary['risk_level'] == 'high'

@pytest.mark.asyncio
async def test_dpa_expiry_notification():
    # Create DPA expiring in 25 days
    future = datetime.utcnow() + timedelta(days=25)
    dpa = await create_dpa(vendor_id='vendor-2', expiry_date=future)
    
    # Check for expiry
    await dpa_service.check_dpa_expiry()
    
    # Verify event emitted
    assert event_bus.events[-1].event_type == 'VendorDPAExpiring'
    assert event_bus.events[-1].days_until_expiry == 25
```

INTEGRATION WITH PHASE 1:

✅ Vendor entity (already in Module 1)
✅ Risk entity linked to assessments
✅ Event-driven notifications (Module 3)
✅ Audit logging for all changes (Module 4)
✅ Multi-tenant isolation (Module 2)
```

---

## ACCEPTANCE CRITERIA

- [ ] All vendor assessments scored with risk levels
- [ ] DPA status tracked with renewal dates
- [ ] Auto-notifications at 30/7 days before expiry
- [ ] Sub-processor registry implemented
- [ ] Risk heatmap dashboard available
- [ ] Evidence storage and retrieval working
- [ ] Audit trail complete for all vendor changes
- [ ] Tests verify scoring accuracy
- [ ] Performance: dashboard loads in < 2 seconds

---

## NEXT MODULE

After MODULE 5, proceed to MODULE 6: DSAR Workflows (4 weeks)

