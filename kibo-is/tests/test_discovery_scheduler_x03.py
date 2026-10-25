"""X03: durable schedules, source failures, and transactional restart recovery."""
import hashlib
import time

import pytest
from sqlalchemy import event, select

from core.regulatory_intelligence import DiscoveryStatusCode, SourceHealthStatus
from core.regulatory_intelligence.discovery import (
    DEFAULT_CADENCES, DiscoveryCheckpoint, DiscoveryDocument, DiscoveryRunAuditLog,
    DiscoveryStore, IngestionTaskRecord, ScheduledDiscoveryEngine,
)

CADENCE = "federal_and_eu_feeds"


class Connector:
    def __init__(self, documents=()):
        self.documents = documents
        self.cursors = []

    def fetch(self, *, cursor, timeout):
        self.cursors.append(cursor)
        return self.documents


@pytest.fixture
def store(tmp_path):
    return DiscoveryStore(f"sqlite:///{tmp_path / 'discovery.db'}")


def rows(store, model):
    with store.session() as session:
        return list(session.scalars(select(model)))


@pytest.mark.parametrize("cadence,interval", list(DEFAULT_CADENCES.items()))
def test_schedules(store, cadence, interval):
    now = [1000000.0]
    engine = ScheduledDiscoveryEngine(store, clock=lambda: now[0])
    connector = Connector()
    if interval is None:
        assert not engine.is_due("source", cadence)
        assert engine.run("source", cadence, connector, force=True) is None
        assert engine.run("source", cadence, connector, controlled=True) == DiscoveryStatusCode.OK
        return
    assert engine.run("source", cadence, connector) == DiscoveryStatusCode.OK
    assert not engine.is_due("source", cadence)
    now[0] += interval - 1
    assert engine.run("source", cadence, connector) is None
    now[0] += 1
    assert engine.is_due("source", cadence)


def test_configurable_cadence(store):
    engine = ScheduledDiscoveryEngine(store, cadences={CADENCE: 12}, clock=lambda: 100)
    engine.run("source", CADENCE, Connector())
    engine.clock = lambda: 112
    assert engine.is_due("source", CADENCE)


def test_incremental_dedup_and_provenance(store):
    engine = ScheduledDiscoveryEngine(store)
    document = DiscoveryDocument("doc", "official text", "cursor-1", {"url": "https://official.example/doc"})
    connector = Connector([document])
    engine.run("source", CADENCE, connector)
    engine.run("source", CADENCE, connector, force=True)
    assert connector.cursors == [None, "cursor-1"]
    tasks = rows(store, IngestionTaskRecord)
    assert len(tasks) == 1
    assert tasks[0].content_sha256 == hashlib.sha256(b"official text").hexdigest()
    assert tasks[0].provenance == document.provenance
    assert rows(store, DiscoveryRunAuditLog)[1].evidence[0]["event"] == "UNCHANGED"
    connector.documents = [DiscoveryDocument("doc", "amended text", "cursor-2", document.provenance)]
    engine.run("source", CADENCE, connector, force=True)
    assert len(rows(store, IngestionTaskRecord)) == 2
    assert rows(store, DiscoveryCheckpoint)[0].cursor == "cursor-2"


@pytest.mark.parametrize("error", [ConnectionError("offline"), TimeoutError("timed out")])
def test_outage_no_fabrication(store, error):
    delays, alerts = [], []
    class Offline:
        def fetch(self, **kwargs):
            raise error
    engine = ScheduledDiscoveryEngine(store, sleep=delays.append, alert_sink=alerts.append)
    assert engine.run("source", CADENCE, Offline()) == DiscoveryStatusCode.SOURCE_UNAVAILABLE
    assert delays == [1, 2]
    assert len(alerts) == 3
    assert rows(store, IngestionTaskRecord) == []
    cp = rows(store, DiscoveryCheckpoint)[0]
    assert cp.health_status == SourceHealthStatus.UNREACHABLE.value
    assert cp.cursor is None and cp.last_success_at is None
    audit = rows(store, DiscoveryRunAuditLog)[0]
    assert audit.state == "FAILED" and len(audit.evidence) == 3
    assert audit.status_code == DiscoveryStatusCode.SOURCE_UNAVAILABLE.value
    assert engine.run("source", CADENCE, Connector()) == DiscoveryStatusCode.OK
    assert rows(store, DiscoveryCheckpoint)[0].health_status == SourceHealthStatus.HEALTHY.value


def test_actual_deadline_discards_late_result(store):
    class Slow:
        def fetch(self, **kwargs):
            time.sleep(0.05)
            return [DiscoveryDocument("late", "text", "late")]
    engine = ScheduledDiscoveryEngine(store, timeout_seconds=0.005, max_attempts=1)
    assert engine.run("source", CADENCE, Slow()) == DiscoveryStatusCode.SOURCE_UNAVAILABLE
    time.sleep(0.06)
    assert rows(store, IngestionTaskRecord) == []


def test_restart_after_committed_document(store):
    """Kill the worker after one atomic commit; reopen the real database."""
    class WorkerKilled(BaseException):
        pass
    connector = Connector([
        DiscoveryDocument("one", "first", "1", {"url": "official/1"}),
        DiscoveryDocument("two", "second", "2", {"url": "official/2"}),
    ])
    commits = [0]
    def crash_after_document(session):
        commits[0] += 1
        if commits[0] == 2:  # run initialization, then first document
            raise WorkerKilled()
    event.listen(store.session, "after_commit", crash_after_document)
    with pytest.raises(WorkerKilled):
        ScheduledDiscoveryEngine(store).run("source", CADENCE, connector)
    event.remove(store.session, "after_commit", crash_after_document)
    assert rows(store, DiscoveryCheckpoint)[0].cursor == "1"
    assert len(rows(store, IngestionTaskRecord)) == 1
    original_run = rows(store, DiscoveryRunAuditLog)[0].run_id
    assert rows(store, DiscoveryRunAuditLog)[0].state == "IN_PROGRESS"
    reopened = DiscoveryStore(store.engine.url)
    # Even a source replaying the last committed item must remain idempotent.
    assert ScheduledDiscoveryEngine(reopened).run("source", CADENCE, connector) == DiscoveryStatusCode.OK
    assert connector.cursors == [None, "1"]
    tasks = rows(reopened, IngestionTaskRecord)
    assert len(tasks) == 2 and {t.run_id for t in tasks} == {original_run}
    assert {t.provenance["url"] for t in tasks} == {"official/1", "official/2"}
    audits = rows(reopened, DiscoveryRunAuditLog)
    assert len(audits) == 1 and audits[0].state == "COMPLETED"
    assert any(e["event"] == "RESUMED" for e in audits[0].evidence)
    assert rows(reopened, DiscoveryCheckpoint)[0].cursor == "2"


def test_document_failure_rolls_back_checkpoint_and_evidence(store):
    connector = Connector([DiscoveryDocument("doc", "text", "1", {"url": "official"})])
    def reject_task(mapper, connection, target):
        raise RuntimeError("storage failure")
    event.listen(IngestionTaskRecord, "before_insert", reject_task)
    try:
        with pytest.raises(RuntimeError, match="storage failure"):
            ScheduledDiscoveryEngine(store).run("source", CADENCE, connector)
    finally:
        event.remove(IngestionTaskRecord, "before_insert", reject_task)
    assert rows(store, IngestionTaskRecord) == []
    assert rows(store, DiscoveryCheckpoint)[0].cursor is None
    assert rows(store, DiscoveryRunAuditLog)[0].evidence == []
    assert ScheduledDiscoveryEngine(store).run("source", CADENCE, connector) == DiscoveryStatusCode.OK
    assert len(rows(store, IngestionTaskRecord)) == 1
