# MODULE 7: INCIDENT & BREACH MANAGEMENT
## For Antigravity IDE + Gemma4

**Duration:** 6-8 weeks | **Priority:** CRITICAL | **Effort:** Very High

---

## OVERVIEW

Detect, triage, and manage privacy incidents and data breaches with automatic severity assessment, timeline tracking, root cause analysis, and regulatory notification workflows.

**Current State:**
- Manual incident reporting
- Delayed breach detection
- No automated severity assessment
- Manual regulatory notifications
- Incomplete audit trails

**Target State:**
- Real-time incident detection
- Automatic severity classification (CVSS-like scoring)
- Root cause analysis workflow
- Automated regulatory notifications (GDPR, PIPEDA, CCPA, Law 25)
- Complete audit trail with timestamps
- Executive escalation routing
- Multi-jurisdiction compliance

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
Build incident and breach management system for KIBO to detect, assess, and respond to privacy incidents.

TASK: Create incident detection, severity assessment, breach tracking, and notification workflows.

REQUIREMENTS:
1. Incident Detection: Ingest from multiple sources (logs, monitoring alerts, user reports)
2. Severity Scoring: Auto-assess CVSS-style scores based on data sensitivity & scope
3. Breach Categorization: Classify as breach/incident/near-miss
4. Timeline Tracking: Record all key events with forensic detail
5. Root Cause Analysis: Structured RCA workflow
6. Regulatory Notifications: Auto-generate notices for GDPR, PIPEDA, CCPA, Law 25
7. Affected Individual Notification: Draft notification templates & track delivery
8. Escalation: Route to CISO/DPO/Legal based on severity
9. Audit Logging: Immutable record of all actions
10. Remediation Tracking: Monitor and close action items

FILE STRUCTURE:
kibo-is/
├── core/
│   ├── incident/
│   │   ├── incident_manager.py      # Incident lifecycle
│   │   ├── breach_detector.py        # Detection from multiple sources
│   │   ├── severity_scorer.py        # CVSS-like scoring
│   │   ├── breach_classifier.py      # Breach vs incident vs near-miss
│   │   ├── rca_engine.py             # Root cause analysis
│   │   ├── timeline_tracker.py       # Event sequencing
│   │   └── models/
│   │       ├── incident.py           # Incident entity
│   │       ├── breach.py             # Breach entity
│   │       ├── incident_event.py     # Timeline events
│   │       └── rca_finding.py        # RCA findings
│   ├── notifications/
│   │   ├── notification_engine.py    # Multi-channel dispatch
│   │   ├── gdpr_notifier.py          # GDPR Article 33/34 notices
│   │   ├── pipeda_notifier.py        # PIPEDA notification
│   │   ├── ccpa_notifier.py          # CCPA notification
│   │   ├── law25_notifier.py         # Quebec Law 25 notification
│   │   ├── notification_templates.py # Template management
│   │   └── models/
│   │       ├── notification.py       # Notification record
│   │       └── notification_recipient.py
│   └── services/
│       ├── incident_service.py
│       └── breach_service.py
├── integrations/
│   ├── log_ingester.py               # Log aggregation
│   ├── monitoring_alerts.py          # Alert feed integration
│   └── siem_connector.py             # SIEM integration
└── tests/
    ├── test_incident_management.py
    └── test_breach_notifications.py

KEY MODELS:
- Incident(id, title, description, severity_score, status, created_at)
- Breach(incident_id, data_categories[], affected_individuals_count, jurisdiction[], breach_type)
- IncidentEvent(incident_id, event_type, timestamp, actor, description, evidence_url)
- RCAFinding(incident_id, root_cause, contributing_factors, recommendations)
- RegulatorNotification(incident_id, jurisdiction, notification_type, status, sent_at)
- AffectedIndividualNotification(breach_id, recipient_count, delivery_status, sent_at)

INCIDENT DETECTION PIPELINE:
1. Monitor multiple sources:
   - Log aggregation (ELK, Splunk)
   - Monitoring alerts (Prometheus, Datadog)
   - User reports (portal)
   - Automated scans (DLP, antivirus)

2. Parse & correlate events
3. Flag potential breaches
4. Create incident record
5. Route to triage queue

SEVERITY SCORING (0-100):
- Data Sensitivity: Public (0-20), Internal (20-40), Sensitive (40-60), Highly Confidential (60-100)
- Scope: Individual (1x) vs Department (10x) vs Organization (100x)
- Type: Access (10), Modification (25), Deletion (50), Exfiltration (100)
- Scope multiplier: 1-100 individuals = base, 100-1000 = 10x, 1000+ = 100x
- Formula: Score = (Data_Sensitivity + Type) * Scope_Multiplier / 100
- Result: 0-10 = Low, 10-40 = Medium, 40-70 = High, 70+ = Critical

EXAMPLE CODE:

class SeverityScorer:
    def score(self, incident_data):
        # Data sensitivity
        sensitivity_scores = {
            'public': 5,
            'internal': 25,
            'sensitive': 50,
            'highly_confidential': 85
        }
        data_score = sensitivity_scores.get(incident_data['classification'], 0)
        
        # Incident type
        type_scores = {
            'access': 10,
            'modification': 25,
            'deletion': 50,
            'exfiltration': 100
        }
        type_score = type_scores.get(incident_data['type'], 0)
        
        # Scope
        affected_count = incident_data['affected_individuals']
        if affected_count < 100:
            scope_multiplier = 1
        elif affected_count < 1000:
            scope_multiplier = 10
        else:
            scope_multiplier = 100
        
        # Calculate
        base_score = (data_score + type_score) * scope_multiplier / 100
        final_score = min(100, base_score)
        
        # Classify
        if final_score < 10:
            severity = 'LOW'
        elif final_score < 40:
            severity = 'MEDIUM'
        elif final_score < 70:
            severity = 'HIGH'
        else:
            severity = 'CRITICAL'
        
        return {
            'score': final_score,
            'severity': severity,
            'escalate_to': ['CISO'] if severity == 'CRITICAL' else ['DPO']
        }

class BreachNotifier:
    def __init__(self, notification_engine):
        self.notifier = notification_engine
    
    async def notify_gdpr_breach(self, breach):
        # GDPR Article 33: Notify supervisory authority
        # GDPR Article 34: Notify data subjects
        
        # Determine notification timeline
        discovery_date = breach['discovery_date']
        notification_deadline = discovery_date + timedelta(days=72)
        
        if breach['risk_to_individuals'] == 'high':
            # Notify individuals without undue delay
            await self.notifier.send_notifications(
                recipients=breach['affected_individuals'],
                template='gdpr_data_subject_notification',
                context={
                    'breach_description': breach['description'],
                    'data_categories': breach['data_categories'],
                    'likely_consequences': breach['consequences'],
                    'measures_taken': breach['remediation'],
                    'contact': breach['dpo_contact']
                }
            )
        
        # Notify authority by deadline
        await self.notifier.send_regulatory_notification(
            jurisdiction='EU',
            template='gdpr_authority_notification',
            context={
                'breach_id': breach['id'],
                'notification_deadline': notification_deadline,
                'authority': breach['supervisory_authority'],
                'breach_summary': breach['description'],
                'affected_count': breach['affected_individuals_count'],
                'data_categories': breach['data_categories'],
                'measures_taken': breach['remediation']
            }
        )

class RCAEngine:
    async def analyze(self, incident_id):
        incident = load_incident(incident_id)
        
        # Gather timeline
        timeline = load_incident_events(incident_id)
        
        # Structured RCA
        rca = {
            'root_causes': [],
            'contributing_factors': [],
            'recommendations': []
        }
        
        # System root causes
        for event in timeline:
            if event['type'] == 'system_error':
                rca['root_causes'].append({
                    'category': 'Technical',
                    'description': event['description'],
                    'evidence': event['evidence_url']
                })
        
        # Process root causes
        for event in timeline:
            if event['type'] == 'process_failure':
                rca['contributing_factors'].append({
                    'process': event['process_name'],
                    'failure': event['description']
                })
        
        # Recommendations
        rca['recommendations'] = [
            'Implement monitoring for similar conditions',
            'Update incident response procedures',
            'Conduct security awareness training'
        ]
        
        return rca

NOTIFICATION TEMPLATES:
1. GDPR Data Subject Notification
2. GDPR Authority Notification (Article 33)
3. PIPEDA Individual Notification
4. CCPA Consumer Notification
5. Quebec Law 25 Notification
6. Internal Executive Summary
7. Public Statement (if required)

TESTING:
- Detect incident from log entry
- Score severity correctly
- Classify as breach/incident/near-miss
- Generate regulatory notification
- Track timeline accurately
- Verify RCA completeness
```

---

## ACCEPTANCE CRITERIA

- [ ] Incidents detected from multiple sources
- [ ] Severity scoring accurate (validated against known incidents)
- [ ] Breach classification correct (breach vs incident vs near-miss)
- [ ] Timeline tracking complete & forensic
- [ ] RCA workflow functional
- [ ] GDPR notifications generated correctly
- [ ] PIPEDA notifications generated correctly
- [ ] CCPA notifications generated correctly
- [ ] Law 25 notifications generated correctly
- [ ] Regulatory deadline tracking working
- [ ] Escalation routing correct
- [ ] Audit logging immutable & complete
- [ ] All notifications include required legal elements
- [ ] Performance: incident creation < 500ms

---

## NEXT MODULE

After MODULE 7, proceed to MODULE 8: Notification & Escalation System (4-6 weeks)
