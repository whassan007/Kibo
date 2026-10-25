"""Persistent discovery scheduling and transactional ingestion outbox.

Connectors implement fetch(cursor, timeout) and return an iterable of
DiscoveryDocument objects with opaque, resumable cursors. Ingestion consumers
must use task_id as their idempotency key. Run one scheduler per source/cadence;
this module does not provide distributed worker leases.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import time
import uuid
from typing import Any, Callable

from sqlalchemy import Column, Float, JSON, String, Text, UniqueConstraint, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .. import DiscoveryStatusCode, SourceHealthStatus, compute_sha256_hex

Base = declarative_base()
DEFAULT_CADENCES = {
    "federal_and_eu_feeds": 21600,
    "state_provincial_legislative": 86400,
    "regulator_and_enforcement_decisions": 86400,
    "judicial_decisions": 86400,
    "full_source_reconciliation": 604800,
    "historical_backfill": None,
}


class DiscoveryCheckpoint(Base):
    __tablename__ = "discovery_checkpoints"
    source_id = Column(String(255), primary_key=True)
    cadence = Column(String(100), primary_key=True)
    cursor = Column(Text, nullable=True)
    last_success_at = Column(Float, nullable=True)
    health_status = Column(String(40), nullable=False, default=SourceHealthStatus.HEALTHY.value)


class DiscoveryRunAuditLog(Base):
    __tablename__ = "discovery_run_audit_logs"
    run_id = Column(String(36), primary_key=True)
    source_id = Column(String(255), nullable=False, index=True)
    cadence = Column(String(100), nullable=False)
    state = Column(String(32), nullable=False, default="IN_PROGRESS")
    status_code = Column(String(40), nullable=True)
    started_at = Column(Float, nullable=False)
    finished_at = Column(Float, nullable=True)
    evidence = Column(JSON, nullable=False, default=list)


class IngestionTaskRecord(Base):
    __tablename__ = "discovery_ingestion_tasks"
    __table_args__ = (UniqueConstraint("source_id", "document_id", "content_sha256"),)
    task_id = Column(String(36), primary_key=True)
    source_id = Column(String(255), nullable=False)
    document_id = Column(String(512), nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    provenance = Column(JSON, nullable=False)
    run_id = Column(String(36), nullable=False)
    state = Column(String(32), nullable=False, default="PENDING")


@dataclass(frozen=True)
class DiscoveryDocument:
    document_id: str
    content: str
    cursor: str
    provenance: dict[str, Any] = field(default_factory=dict)


class DiscoveryStore:
    """SQLAlchemy store accepting SQLite or PostgreSQL URLs (or an Engine)."""

    def __init__(self, database="sqlite:///discovery.db"):
        self.engine = database if isinstance(database, Engine) else create_engine(database)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(self.engine, expire_on_commit=False)


class ScheduledDiscoveryEngine:
    def __init__(self, store: DiscoveryStore, *, cadences=None, max_attempts=3,
                 backoff_seconds=1.0, timeout_seconds=30.0,
                 clock: Callable = time.time, sleep: Callable = time.sleep,
                 alert_sink: Callable | None = None):
        self.store = store
        self.cadences = {**DEFAULT_CADENCES, **(cadences or {})}
        if any(v is not None and v <= 0 for v in self.cadences.values()):
            raise ValueError("Cadences must be positive or controlled (None)")
        if max_attempts < 1 or backoff_seconds < 0 or timeout_seconds <= 0:
            raise ValueError("Invalid retry/timeout configuration")
        self.max_attempts = max_attempts
        self.backoff = backoff_seconds
        self.timeout = timeout_seconds
        self.clock, self.sleep, self.alert_sink = clock, sleep, alert_sink

    def is_due(self, source_id, cadence, *, controlled=False):
        interval = self.cadences[cadence]
        if interval is None:
            return controlled
        with self.store.session() as session:
            cp = session.get(DiscoveryCheckpoint, (source_id, cadence))
            return cp is None or cp.last_success_at is None or self.clock() >= cp.last_success_at + interval

    def _fetch(self, connector, cursor):
        # Materialize within the deadline, including lazy network iterators.
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(lambda: list(connector.fetch(cursor=cursor, timeout=self.timeout)))
        try:
            return future.result(timeout=self.timeout)
        finally:
            # Late connector results never write to the store. Connectors should
            # also honor the supplied timeout to release their network resources.
            pool.shutdown(wait=False, cancel_futures=True)

    def run(self, source_id, cadence, connector, *, controlled=False, force=False):
        """Run a due source; None means not due. Controlled jobs require opt-in."""
        if self.cadences[cadence] is None and not controlled:
            return None
        with self.store.session() as session:
            interrupted = session.scalar(select(DiscoveryRunAuditLog.run_id).where(
                DiscoveryRunAuditLog.source_id == source_id,
                DiscoveryRunAuditLog.cadence == cadence,
                DiscoveryRunAuditLog.state == "IN_PROGRESS").limit(1))
        if not force and not interrupted and not self.is_due(source_id, cadence, controlled=controlled):
            return None
        with self.store.session.begin() as session:
            cp = session.get(DiscoveryCheckpoint, (source_id, cadence))
            if cp is None:
                cp = DiscoveryCheckpoint(source_id=source_id, cadence=cadence)
                session.add(cp)
            audit = session.scalars(select(DiscoveryRunAuditLog).where(
                DiscoveryRunAuditLog.source_id == source_id,
                DiscoveryRunAuditLog.cadence == cadence,
                DiscoveryRunAuditLog.state == "IN_PROGRESS").order_by(DiscoveryRunAuditLog.started_at)).first()
            if audit is None:
                audit = DiscoveryRunAuditLog(run_id=str(uuid.uuid4()), source_id=source_id,
                    cadence=cadence, started_at=self.clock(), evidence=[])
                session.add(audit)
            else:
                audit.evidence = [*audit.evidence, {"event": "RESUMED", "at": self.clock()}]
            run_id, cursor = audit.run_id, cp.cursor

        for attempt in range(1, self.max_attempts + 1):
            try:
                documents = self._fetch(connector, cursor)
                break
            except Exception as exc:
                delay = self.backoff * 2 ** (attempt - 1)
                alert = {"event": "SOURCE_HEALTH_ALERT", "source_id": source_id,
                         "health": SourceHealthStatus.UNREACHABLE.value,
                         "attempt": attempt, "error": str(exc), "at": self.clock(),
                         "retry_delay": delay if attempt < self.max_attempts else None}
                with self.store.session.begin() as session:
                    cp = session.get(DiscoveryCheckpoint, (source_id, cadence))
                    cp.health_status = SourceHealthStatus.UNREACHABLE.value
                    audit = session.get(DiscoveryRunAuditLog, run_id)
                    audit.evidence = [*audit.evidence, alert]
                    if attempt == self.max_attempts:
                        audit.state = "FAILED"
                        audit.status_code = DiscoveryStatusCode.SOURCE_UNAVAILABLE.value
                        audit.finished_at = self.clock()
                if self.alert_sink:
                    try:
                        self.alert_sink(alert)
                    except Exception as alert_error:
                        with self.store.session.begin() as session:
                            audit = session.get(DiscoveryRunAuditLog, run_id)
                            audit.evidence = [*audit.evidence, {"event": "ALERT_DELIVERY_FAILED", "error": str(alert_error)}]
                if attempt == self.max_attempts:
                    return DiscoveryStatusCode.SOURCE_UNAVAILABLE
                self.sleep(delay)

        for document in documents:
            digest = compute_sha256_hex(document.content)
            with self.store.session.begin() as session:
                existing = session.scalar(select(IngestionTaskRecord.task_id).where(
                    IngestionTaskRecord.source_id == source_id,
                    IngestionTaskRecord.document_id == document.document_id,
                    IngestionTaskRecord.content_sha256 == digest))
                if existing is None:
                    session.add(IngestionTaskRecord(task_id=str(uuid.uuid4()), source_id=source_id,
                        document_id=document.document_id, content_sha256=digest, content=document.content,
                        provenance=document.provenance, run_id=run_id))
                cp = session.get(DiscoveryCheckpoint, (source_id, cadence))
                cp.cursor = document.cursor
                audit = session.get(DiscoveryRunAuditLog, run_id)
                audit.evidence = [*audit.evidence, {"event": "UNCHANGED" if existing else "QUEUED",
                    "document_id": document.document_id, "sha256": digest,
                    "cursor": document.cursor, "provenance": document.provenance, "at": self.clock()}]
        with self.store.session.begin() as session:
            cp = session.get(DiscoveryCheckpoint, (source_id, cadence))
            cp.last_success_at, cp.health_status = self.clock(), SourceHealthStatus.HEALTHY.value
            audit = session.get(DiscoveryRunAuditLog, run_id)
            audit.state, audit.status_code, audit.finished_at = "COMPLETED", DiscoveryStatusCode.OK.value, self.clock()
        return DiscoveryStatusCode.OK
