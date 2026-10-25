# KIBO Privacy OS — Genuine Live Experience & SSE Architecture (`docs/ux/LIVE-EXPERIENCE-PLAN.md`)

## 1. Three Dimensions of Liveliness (Section 3)

1. **Operational Liveliness (Backend SSE Stream `/api/v1/events/stream`)**:
   - Real-time Server-Sent Events emitted when actual backend state changes occur across all 20 mandatory event types:
     - `case.created`, `case.updated`, `case.assigned`
     - `assessment.started`, `assessment.progress`, `assessment.completed`
     - `incident.created`, `incident.updated`
     - `dsar.deadline_approaching`
     - `approval.requested`, `approval.completed`
     - `regulation.discovered`, `regulation.annotated`, `regulation.verified`, `regulation.changed`
     - `agent.started`, `agent.progress`, `agent.completed`, `agent.failed`
     - `integration.degraded`, `integration.recovered`
2. **Interaction Liveliness**:
   - Immediate click acknowledgment, progressive step indicators (`1..9` on assessments, `1..5` on DSARs, `1..5` on incidents), real multi-stage progress bars on JRAE and Governed Assistant runs, and persistent local drafts (`localStorage`) with timestamped confirmation.
3. **Visual Liveliness**:
   - Compact Live Activity Timeline on Executive Home and header drawer, smooth status transitions, and zero fake/randomized telemetry.

---

## 2. Canonical Live Event Envelope Schema (Section 7)

Every event published by [`kibo-is/core/live_events/__init__.py`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/live_events/__init__.py) and consumed by [`kibo-is/src/services/liveEventClient.ts`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/src/services/liveEventClient.ts) conforms to:

```json
{
  "event_id": "evt_000042_9f8a2b1c",
  "sequence": 42,
  "tenant_id": "tnt-enterprise-global-001",
  "event_type": "approval.completed",
  "timestamp": "2026-10-25T20:58:00Z",
  "resource_reference": "asmt_efvp_law25_001",
  "visibility_scope": ["CPO", "DPO", "LEGAL", "ANALYST"],
  "event_version": "1.0",
  "payload": {
    "summary": "DPO approved Quebec Law 25 EFVP & GDPR Art. 35 DPIA",
    "status": "approved",
    "approver_role": "DPO",
    "audit_ref": "AUDIT-ASMT-2026-1025-001"
  }
}
```

### Security & Reliability Invariants
- **Tenant Isolation:** Events emitted for `tenant-a` are never delivered to subscribers of `tenant-b` (except `PUBLIC_STATUTORY` `regulation.*` events).
- **No Sensitive Payloads in Generic Events:** Events carry resource IDs, status codes, and summary metadata—never raw PII/PHI.
- **Resume Cursor & Deduplication (`UX-11`):** Clients pass `Last-Event-ID` or `?cursor=<sequence>` on reconnect; `liveEventClient.ts` maintains a bounded `Set<string>` of seen `event_id` values so reconnected streams never duplicate UI notifications or state transitions.
- **Page Visibility Awareness:** When `document.visibilityState === 'hidden'`, background polling pauses and resumes cleanly on `visible`.
