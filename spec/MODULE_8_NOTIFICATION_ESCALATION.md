# MODULE 8: NOTIFICATION & ESCALATION SYSTEM
## For Antigravity IDE + Gemma4

**Duration:** 4-6 weeks | **Priority:** HIGH | **Effort:** High

---

## OVERVIEW

Multi-channel notification and intelligent escalation routing for alerts, approvals, and incidents. Ensures critical messages reach the right person via the right channel at the right time.

**Current State:**
- Single notification channel (email)
- No escalation logic
- Manual routing
- No retry/reliability
- Limited delivery tracking

**Target State:**
- Multi-channel (Email, Slack, SMS, Teams, PagerDuty)
- Intelligent escalation (severity-based routing)
- Template management
- Reliable delivery with retry logic
- Full audit trail
- Rate limiting & deduplication
- Timezone-aware scheduling
- Do-not-disturb compliance

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
Build notification and escalation system for KIBO to route alerts and approvals intelligently.

TASK: Create multi-channel notification engine with escalation logic, templates, and delivery tracking.

REQUIREMENTS:
1. Multi-Channel Dispatch: Email, Slack, SMS, Teams, PagerDuty
2. Escalation Logic: Route based on severity, availability, role
3. Template Management: Reusable, compliance-aware templates
4. Retry & Reliability: Exponential backoff, DLQ for failed sends
5. Delivery Tracking: Know who received what when
6. Do-Not-Disturb: Respect user schedules
7. Rate Limiting: Prevent notification spam
8. Audit Logging: Immutable record of all notifications
9. Timezone Awareness: Schedule across time zones
10. Deduplication: Don't send duplicate notifications

FILE STRUCTURE:
kibo-is/
├── core/
│   ├── notifications/
│   │   ├── notification_engine.py    # Orchestration
│   │   ├── channel_adapters/
│   │   │   ├── email_adapter.py      # SMTP
│   │   │   ├── slack_adapter.py      # Slack webhook
│   │   │   ├── sms_adapter.py        # Twilio
│   │   │   ├── teams_adapter.py      # Teams webhook
│   │   │   └── pagerduty_adapter.py  # PagerDuty API
│   │   ├── escalation_engine.py      # Routing logic
│   │   ├── template_engine.py        # Template rendering
│   │   ├── delivery_tracker.py       # Status tracking
│   │   ├── retry_handler.py          # Exponential backoff
│   │   ├── deduplication.py          # Prevent duplicates
│   │   ├── rate_limiter.py           # Throttling
│   │   └── models/
│   │       ├── notification_rule.py  # Escalation rules
│   │       ├── notification_template.py
│   │       ├── notification_delivery.py
│   │       └── escalation_path.py
│   └── services/
│       └── notification_service.py
└── tests/
    ├── test_notification_engine.py
    └── test_escalation_logic.py

KEY MODELS:
- NotificationRule(id, trigger, severity, escalation_path[], channels[])
- NotificationTemplate(id, name, category, subject, body, required_fields[])
- NotificationDelivery(id, notification_id, recipient, channel, status, sent_at, read_at)
- EscalationPath(id, level, approver_role, preferred_channel, timeout_minutes)
- NotificationDeduplication(template_id, recipient, timeframe_minutes, max_sends_per_period)

ESCALATION LOGIC:
Level 1 (Immediate):
- CRITICAL incidents → email + Slack + SMS
- Wait 5 min for read receipt
- If no response, escalate to Level 2

Level 2 (Manager escalation):
- Send to manager + team lead
- Wait 10 minutes
- If still no response, escalate to Level 3

Level 3 (Executive escalation):
- Send to CTO/CISO/CEO
- Wait 15 minutes
- If no response, page on-call

Level 4 (Emergency):
- Page all on-call
- Use phone call
- Page operations team

EXAMPLE CODE:

class NotificationEngine:
    def __init__(self, channels, escalator):
        self.channels = channels  # email, slack, sms, teams, pagerduty
        self.escalator = escalator
    
    async def send(self, notification_request):
        # Validate
        if self.deduplicator.is_duplicate(notification_request):
            return {'status': 'skipped', 'reason': 'duplicate'}
        
        # Rate limit
        if self.rate_limiter.is_throttled(notification_request['recipient']):
            return {'status': 'throttled'}
        
        # Determine channels & escalation
        escalation_path = self.escalator.get_path(
            severity=notification_request['severity'],
            recipient_role=notification_request['recipient_role']
        )
        
        delivery_records = []
        
        for level in escalation_path:
            # Render template
            message = self.template_engine.render(
                template_name=notification_request['template'],
                context=notification_request['context']
            )
            
            # Send via preferred channel
            for channel_name in level['channels']:
                channel = self.channels[channel_name]
                
                delivery = {
                    'recipient': level['approver'],
                    'channel': channel_name,
                    'message': message,
                    'sent_at': datetime.now(),
                    'status': 'pending'
                }
                
                try:
                    await channel.send(level['approver'], message)
                    delivery['status'] = 'sent'
                except Exception as e:
                    delivery['status'] = 'failed'
                    delivery['error'] = str(e)
                    # Queue for retry
                    await self.retry_handler.queue(delivery, level['retry_after_minutes'])
                
                delivery_records.append(delivery)
            
            # Wait for response
            response = await self._wait_for_response(
                recipient=level['approver'],
                timeout_minutes=level['timeout_minutes']
            )
            
            if response:
                # Someone responded, done escalating
                break
        
        return {'status': 'sent', 'deliveries': delivery_records}

class EscalationEngine:
    def get_path(self, severity, recipient_role, availability=None):
        if severity == 'CRITICAL':
            return [
                {
                    'level': 1,
                    'approver': recipient_role,
                    'channels': ['email', 'slack', 'sms'],
                    'timeout_minutes': 5,
                    'retry_after_minutes': 5
                },
                {
                    'level': 2,
                    'approver': self._get_manager(recipient_role),
                    'channels': ['slack', 'sms', 'phone'],
                    'timeout_minutes': 10,
                    'retry_after_minutes': 10
                },
                {
                    'level': 3,
                    'approver': 'ciso',
                    'channels': ['pagerduty', 'phone'],
                    'timeout_minutes': 15,
                    'retry_after_minutes': 5
                }
            ]
        elif severity == 'HIGH':
            return [
                {
                    'level': 1,
                    'approver': recipient_role,
                    'channels': ['email', 'slack'],
                    'timeout_minutes': 30,
                    'retry_after_minutes': 15
                },
                {
                    'level': 2,
                    'approver': self._get_manager(recipient_role),
                    'channels': ['slack', 'email'],
                    'timeout_minutes': 60,
                    'retry_after_minutes': 30
                }
            ]
        else:  # MEDIUM / LOW
            return [
                {
                    'level': 1,
                    'approver': recipient_role,
                    'channels': ['email'],
                    'timeout_minutes': 120,
                    'retry_after_minutes': 60
                }
            ]

class SlackAdapter:
    async def send(self, user_id, message):
        payload = {
            'channel': f'@{user_id}',
            'text': message['text'],
            'blocks': self._build_blocks(message)
        }
        
        response = await httpx.post(
            self.webhook_url,
            json=payload
        )
        
        if response.status_code != 200:
            raise NotificationError(f'Slack send failed: {response.text}')
        
        return response.json()

class SMSAdapter:
    async def send(self, phone_number, message):
        # Using Twilio
        message_obj = self.twilio_client.messages.create(
            body=message['text'],
            from_=self.twilio_number,
            to=phone_number
        )
        
        return {'sid': message_obj.sid}

class RetryHandler:
    async def queue(self, delivery, retry_after_minutes):
        # Store in Redis with TTL
        retry_key = f"notification:retry:{delivery['recipient']}:{uuid4()}"
        
        await redis.setex(
            retry_key,
            timedelta(minutes=retry_after_minutes),
            json.dumps(delivery)
        )
        
        # Schedule background task
        await scheduler.schedule_in(
            timedelta(minutes=retry_after_minutes),
            self.retry_delivery,
            [delivery]
        )
    
    async def retry_delivery(self, delivery):
        # Re-attempt send with exponential backoff
        max_retries = 3
        backoff = 2
        
        for attempt in range(max_retries):
            try:
                await self.channel.send(delivery['recipient'], delivery['message'])
                delivery['status'] = 'sent'
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = backoff ** attempt
                    await asyncio.sleep(wait * 60)
                else:
                    # Send to DLQ
                    delivery['status'] = 'failed'
                    await self.dlq.put(delivery)

class RateLimiter:
    def is_throttled(self, recipient):
        key = f"notification:rate:{recipient}"
        count = redis.get(key)
        
        if count and int(count) >= self.max_per_hour:
            return True
        
        redis.incr(key)
        redis.expire(key, 3600)
        
        return False

class TemplateEngine:
    def render(self, template_name, context):
        template = load_template(template_name)
        
        # Render with Jinja2
        rendered = template.render(**context)
        
        return {
            'text': rendered,
            'blocks': self._parse_blocks(rendered)
        }

NOTIFICATION TEMPLATES:
1. Assessment Approval Needed
2. Breach Detected - Critical
3. Compliance Gap Found
4. Deadline Approaching
5. Access Request Pending
6. Control Non-Compliance
7. Vendor Risk Alert
8. Regulatory Change Detected
9. Incident Escalation
10. Executive Summary

DELIVERY TRACKING:
- sent_at: timestamp of dispatch
- delivered_at: timestamp of provider delivery
- read_at: timestamp of recipient reading (if supported)
- clicked_at: timestamp of link click (if tracked)
- response_at: timestamp of action taken

TESTING:
- Slack message sends correctly
- SMS message delivers
- Email includes all required fields
- Escalation path routes correctly
- Retry handler executes exponential backoff
- Rate limiter prevents spam
- Deduplication works
- Delivery tracking is accurate
```

---

## ACCEPTANCE CRITERIA

- [ ] Email notifications send & deliver
- [ ] Slack messages send & format correctly
- [ ] SMS sends via Twilio
- [ ] Teams messages send
- [ ] PagerDuty incidents created
- [ ] Escalation path routes correctly
- [ ] Retry handler uses exponential backoff
- [ ] Rate limiting prevents spam
- [ ] Deduplication prevents duplicates
- [ ] Do-not-disturb honored
- [ ] Delivery tracking complete
- [ ] Audit log immutable
- [ ] Performance: send < 1 second
- [ ] Reliability: 99.9% delivery rate

---

## PHASE 2 COMPLETE

After MODULE 8 (Week 32):

✅ Vendor risk management (MODULE 5)  
✅ DSAR workflows (MODULE 6)  
✅ Incident & breach management (MODULE 7)  
✅ Notification & escalation (MODULE 8)  

**Result:** KIBO is now an enterprise-grade SaaS with full compliance workflows, 20+ customers, ready for Phase 3.

---

## NEXT PHASE

Proceed to PHASE 3 (Weeks 33-52) for:
- MODULE 9: Kubernetes Deployment (8 weeks)
- MODULE 10: Advanced Analytics (6 weeks)
- MODULE 11: Regulatory Intelligence (6 weeks)
- MODULE 12: AI/ML Integration (8 weeks)
