import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from agent_gateway import app
from core.live_events import SUPPORTED_EVENT_TYPES, live_event_broker


client = TestClient(app)


def test_supported_20_event_types_registered():
    assert len(SUPPORTED_EVENT_TYPES) == 20
    expected = {
        "case.created",
        "case.assigned",
        "case.stage_changed",
        "assessment.saved",
        "assessment.submitted",
        "assessment.approved",
        "incident.created",
        "incident.severity_changed",
        "incident.deadline_updated",
        "dsar.deadline_approaching",
        "approval.requested",
        "approval.completed",
        "regulation.discovered",
        "regulation.verified",
        "regulation.impact_detected",
        "agent.started",
        "agent.progress",
        "agent.completed",
        "agent.failed",
        "integration.status_changed",
    }
    assert set(SUPPORTED_EVENT_TYPES) == expected


def test_verified_session_and_unauthorized_tenant_blocked():
    res = client.get(
        "/api/v1/auth/session",
        headers={"X-Tenant-ID": "tnt-enterprise-global-001", "X-User-Role": "CPO"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["session_verified"] is True
    assert body["active_tenant_id"] == "tnt-enterprise-global-001"
    assert len(body["authorized_organizations"]) >= 3

    # Attempting to switch to an unauthorized tenant must fail with 403
    unauth = client.get(
        "/api/v1/auth/session",
        headers={"X-Tenant-ID": "tnt-spoofed-unauthorized-999"},
    )
    assert unauth.status_code == 403


def test_publish_recent_and_deduplication_tenant_isolation():
    payload = {
        "event_id": "evt-x01-dedup-test-01",
        "event_type": "incident.created",
        "title": "Incident War Room Created",
        "summary": "72h GDPR & Law 25 RROSH countdown started.",
        "severity": "critical",
        "entity_type": "incident",
        "entity_id": "INC-2026-881",
        "target_section": "incidents",
        "requires_human_review": True,
    }
    r1 = client.post(
        "/api/v1/events/publish",
        json=payload,
        headers={"X-Tenant-ID": "tnt-enterprise-global-001"},
    )
    assert r1.status_code == 200
    seq1 = r1.json()["event"]["sequence_id"]

    # Duplicate publish with same event_id must return exact same sequence_id without duplicating
    r2 = client.post(
        "/api/v1/events/publish",
        json=payload,
        headers={"X-Tenant-ID": "tnt-enterprise-global-001"},
    )
    assert r2.status_code == 200
    assert r2.json()["event"]["sequence_id"] == seq1

    # Other tenant must not see tnt-enterprise-global-001 events
    other = client.get(
        "/api/v1/events/recent",
        headers={"X-Tenant-ID": "tnt-eu-bank-sovereign-002"},
    )
    assert other.status_code == 200
    other_ids = [e["event_id"] for e in other.json()["events"]]
    assert "evt-x01-dedup-test-01" not in other_ids


def test_sse_stream_endpoint_and_cursor_resumption():
    res = client.get(
        "/api/v1/events/stream?max_events=2&last_event_id=0",
        headers={"X-Tenant-ID": "tnt-enterprise-global-001"},
    )
    assert res.status_code == 200
    assert "text/event-stream" in res.headers.get("content-type", "")
    text = res.text
    assert "retry: 3000" in text
    assert "id: " in text
    assert "data: " in text
