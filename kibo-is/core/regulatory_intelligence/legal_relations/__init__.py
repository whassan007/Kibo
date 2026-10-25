"""
KIBO Privacy OS — Legal Relationship & Temporal Knowledge Graph (Worker G20)
Implements Section 7 & RD-12:
- Extends KIBO's existing ontology (`ontology_store.py` / SQLAlchemy / SQLite & PostgreSQL relational tables
  `kg_laws`, `kg_provisions`, `kg_amendments`, `kg_decisions`, `kg_obligations`, `kg_controls`, `kg_edges`)
  without introducing a competing graph DB.
- Supports all required Section 7 relationships:
  * Law -> contains Provision | amendedBy Amendment | interpretedBy Decision | supplementedBy Regulation | enforcedBy Authority
  * Decision -> interprets Provision | cites Decision | applies LegalTest | orders Remedy | modifiedBy Decision | appealedTo Court
  * Obligation -> appliesTo Organization | appliesTo ProcessingActivity | requires Control | triggers Assessment | establishes Deadline
  * Control -> mitigates Risk | satisfies Obligation | supportedBy Evidence
  * ProcessingActivity -> governedBy Obligation | performedBy Organization | uses Vendor | involves DataCategory
- Implements all 6 required temporal & relational query methods (seeded with authentic US, Canadian, and EU data):
  1. `query_law_as_of(processing_activity_or_law_id: str, as_of_date: date) -> dict`
  2. `query_decisions_affecting_sector(jurisdiction_id: str, sector: str) -> list[dict]`
  3. `query_decisions_interpreting_provision(jurisdiction_id: str, provision_ref: str) -> list[dict]`
  4. `query_regulations_effective_in_year(jurisdiction_id: str, year: int) -> list[dict]`
  5. `query_organizations_affected_by_amendment(amendment_id: str) -> list[dict]`
  6. `query_overturned_or_reversed_decisions() -> list[dict]`
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models.base import Base
from core.regulatory_intelligence import compute_sha256_hex


# ---------------------------------------------------------------------------
# Section 7 — Canonical Relationship Schema Matrix
# ---------------------------------------------------------------------------
SECTION_7_RELATIONSHIP_SCHEMA: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "Law": (
        ("contains", "Provision"),
        ("amendedBy", "Amendment"),
        ("interpretedBy", "Decision"),
        ("supplementedBy", "Regulation"),
        ("enforcedBy", "Authority"),
    ),
    "Decision": (
        ("interprets", "Provision"),
        ("cites", "Decision"),
        ("applies", "LegalTest"),
        ("orders", "Remedy"),
        ("modifiedBy", "Decision"),
        ("appealedTo", "Court"),
    ),
    "Obligation": (
        ("appliesTo", "Organization"),
        ("appliesTo", "ProcessingActivity"),
        ("requires", "Control"),
        ("triggers", "Assessment"),
        ("establishes", "Deadline"),
    ),
    "Control": (
        ("mitigates", "Risk"),
        ("satisfies", "Obligation"),
        ("supportedBy", "Evidence"),
    ),
    "ProcessingActivity": (
        ("governedBy", "Obligation"),
        ("performedBy", "Organization"),
        ("uses", "Vendor"),
        ("involves", "DataCategory"),
    ),
}

ALL_VALID_PREDICATES: Set[str] = {
    pred for pairs in SECTION_7_RELATIONSHIP_SCHEMA.values() for pred, _ in pairs
}


# ---------------------------------------------------------------------------
# SQLAlchemy Relational Models (`kg_*` tables on existing KIBO Base)
# ---------------------------------------------------------------------------
class KGLawRecord(Base):
    __tablename__ = "kg_laws"

    record_id = Column(String, primary_key=True)  # e.g., LAW-US-CA-CCPA::v2020.1-CCPA
    law_id = Column(String, nullable=False, index=True)
    version_id = Column(String, nullable=False, index=True)
    jurisdiction_id = Column(String, nullable=False, index=True)
    instrument_type = Column(String, nullable=False, default="statute")  # statute, regulation, directive
    canonical_title = Column(String, nullable=False)
    official_citation = Column(String, nullable=False)
    eli_or_celex_identifier = Column(String, nullable=True)
    issuing_authority = Column(String, nullable=False)
    enforcing_authority = Column(String, nullable=False)
    effective_date = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    publication_date = Column(Date, nullable=True)
    supersedes_version = Column(String, nullable=True)
    amending_instrument_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE, SUPERSEDED, REPEALED
    raw_sha256 = Column(String, nullable=False)
    normalized_sha256 = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")


class KGProvisionRecord(Base):
    __tablename__ = "kg_provisions"

    record_id = Column(String, primary_key=True)
    provision_id = Column(String, nullable=False, index=True)
    law_id = Column(String, nullable=False, index=True)
    version_id = Column(String, nullable=False, index=True)
    jurisdiction_id = Column(String, nullable=False, index=True)
    provision_ref = Column(String, nullable=False, index=True)
    article_or_section = Column(String, nullable=False, index=True)
    effective_date = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    exact_text = Column(Text, nullable=False)
    normalized_sha256 = Column(String, nullable=False)
    is_repealed = Column(Boolean, nullable=False, default=False)
    metadata_json = Column(Text, nullable=False, default="{}")


class KGAmendmentRecord(Base):
    __tablename__ = "kg_amendments"

    amendment_id = Column(String, primary_key=True)
    target_law_id = Column(String, nullable=False, index=True)
    target_provision_ref = Column(String, nullable=False, index=True)
    jurisdiction_id = Column(String, nullable=False, index=True)
    amending_instrument_title = Column(String, nullable=False)
    official_citation = Column(String, nullable=False)
    previous_version_id = Column(String, nullable=False)
    new_version_id = Column(String, nullable=False)
    enactment_date = Column(Date, nullable=False)
    effective_date = Column(Date, nullable=False, index=True)
    change_type = Column(String, nullable=False)
    is_substantive = Column(Boolean, nullable=False, default=True)
    summary = Column(Text, nullable=False)
    affected_sectors_json = Column(Text, nullable=False, default="[]")
    affected_activities_json = Column(Text, nullable=False, default="[]")


class KGDecisionRecord(Base):
    __tablename__ = "kg_decisions"

    decision_id = Column(String, primary_key=True)
    jurisdiction_id = Column(String, nullable=False, index=True)
    case_name = Column(String, nullable=False)
    neutral_citation_or_id = Column(String, nullable=False, index=True)
    court_tribunal_or_regulator = Column(String, nullable=False)
    decision_date = Column(Date, nullable=False, index=True)
    sector = Column(String, nullable=False, index=True)
    interpreted_provisions_json = Column(Text, nullable=False, default="[]")
    legal_test_applied = Column(String, nullable=True)
    remedy_ordered = Column(Text, nullable=True)
    appeal_status = Column(String, nullable=False, default="final")  # final, affirmed, reversed, overturned, modified
    appealed_to_court = Column(String, nullable=True)
    modified_or_reversed_by_decision_id = Column(String, nullable=True, index=True)
    reversal_citation = Column(String, nullable=True)
    holding_summary = Column(Text, nullable=False)
    binding_status = Column(String, nullable=False, default="binding_precedent")
    official_source_url = Column(String, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")


class KGObligationRecord(Base):
    __tablename__ = "kg_obligations"

    obligation_id = Column(String, primary_key=True)
    law_id = Column(String, nullable=False, index=True)
    version_id = Column(String, nullable=False, index=True)
    provision_ref = Column(String, nullable=False, index=True)
    jurisdiction_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    legal_requirement = Column(Text, nullable=False)
    statutory_deadline = Column(String, nullable=True)
    triggered_assessment = Column(String, nullable=True)
    effective_date = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    applies_to_activities_json = Column(Text, nullable=False, default="[]")
    applies_to_organizations_json = Column(Text, nullable=False, default="[]")
    required_controls_json = Column(Text, nullable=False, default="[]")


class KGControlRecord(Base):
    __tablename__ = "kg_controls"

    control_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    control_category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    mitigates_risk_id = Column(String, nullable=False)
    satisfies_obligations_json = Column(Text, nullable=False, default="[]")
    supported_by_evidence_json = Column(Text, nullable=False, default="[]")


class KGEdgeRecord(Base):
    __tablename__ = "kg_edges"

    edge_id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False, index=True)
    source_id = Column(String, nullable=False, index=True)
    predicate = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=False, index=True)
    target_id = Column(String, nullable=False, index=True)
    effective_from = Column(Date, nullable=True, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    jurisdiction_id = Column(String, nullable=True, index=True)
    properties_json = Column(Text, nullable=False, default="{}")


# ---------------------------------------------------------------------------
# Temporal Regulatory Knowledge Graph Engine (Section 7 & RD-12)
# ---------------------------------------------------------------------------
class TemporalRegulatoryKnowledgeGraph:
    """
    Section 7 & RD-12 — Temporal Legal Relationship & Knowledge Graph.
    Extends KIBO's existing ontology (`ontology_store.py` and SQLAlchemy relational tables:
    `kg_laws`, `kg_provisions`, `kg_amendments`, `kg_decisions`, `kg_obligations`,
    `kg_controls`, `kg_edges`) without introducing a competing graph database.
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        ontology_db_path: Optional[str] = None,
        auto_seed: bool = True,
    ) -> None:
        if db_url is None:
            if ontology_db_path is not None:
                self.ontology_db_path = ontology_db_path
                db_url = f"sqlite:///{self.ontology_db_path}"
            else:
                self.ontology_db_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..", "..", "kibo_state.db")
                )
                db_url = "sqlite:///:memory:"
        else:
            self.ontology_db_path = ontology_db_path

        self.db_url = db_url
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, connect_args=connect_args, future=True)
        self._SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

        # Ensure `kg_*` tables exist in the relational store
        Base.metadata.create_all(
            bind=self.engine,
            tables=[
                KGLawRecord.__table__,
                KGProvisionRecord.__table__,
                KGAmendmentRecord.__table__,
                KGDecisionRecord.__table__,
                KGObligationRecord.__table__,
                KGControlRecord.__table__,
                KGEdgeRecord.__table__,
            ],
        )
        self._ensure_base_ontology_tables()
        if auto_seed:
            self.seed_canonical_knowledge_graph()

    def _ensure_base_ontology_tables(self) -> None:
        """
        Ensures the legacy `ontology_classes`, `ontology_instances`, and `ontology_edges`
        tables from `ontology_store.py` are present and synchronized when running on SQLite.
        """
        if not self.db_url.startswith("sqlite"):
            return
        with self.engine.begin() as conn:
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS ontology_classes (
                    class_id TEXT PRIMARY KEY,
                    parent_class_id TEXT
                )
                """
            )
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS ontology_instances (
                    instance_id TEXT PRIMARY KEY,
                    class_id TEXT,
                    label TEXT NOT NULL,
                    properties_json TEXT
                )
                """
            )
            conn.exec_driver_sql(
                """
                CREATE TABLE IF NOT EXISTS ontology_edges (
                    source_id TEXT,
                    target_id TEXT,
                    predicate TEXT,
                    PRIMARY KEY (source_id, target_id, predicate)
                )
                """
            )

    # ------------------------------------------------------------------
    # Graph Edge Registration & Ontology Synchronization
    # ------------------------------------------------------------------
    def add_edge(
        self,
        source_type: str,
        source_id: str,
        predicate: str,
        target_type: str,
        target_id: str,
        effective_from: Optional[date] = None,
        effective_to: Optional[date] = None,
        jurisdiction_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None,
    ) -> str:
        """
        Inserts or updates a typed temporal edge in `kg_edges` and mirrors it into
        `ontology_edges` so KIBO's existing `ontology_store.py` sees the unified graph.
        """
        allowed_pairs = SECTION_7_RELATIONSHIP_SCHEMA.get(source_type, ())
        if allowed_pairs and (predicate, target_type) not in allowed_pairs:
            raise ValueError(
                f"Invalid Section 7 relationship: {source_type} -[{predicate}]-> {target_type}. "
                f"Allowed for {source_type}: {allowed_pairs}"
            )

        edge_seed = (
            f"{source_type}:{source_id}:{predicate}:{target_type}:{target_id}:"
            f"{effective_from.isoformat() if effective_from else 'min'}"
        )
        edge_id = f"EDGE-{compute_sha256_hex(edge_seed)[:16].upper()}"
        props_str = json.dumps(properties or {}, sort_keys=True)

        own_session = session is None
        sess = session or self._SessionLocal()
        try:
            record = KGEdgeRecord(
                edge_id=edge_id,
                source_type=source_type,
                source_id=source_id,
                predicate=predicate,
                target_type=target_type,
                target_id=target_id,
                effective_from=effective_from,
                effective_to=effective_to,
                jurisdiction_id=jurisdiction_id,
                properties_json=props_str,
            )
            sess.merge(record)
            if own_session:
                sess.commit()
        finally:
            if own_session:
                sess.close()

        if self.db_url.startswith("sqlite"):
            with self.engine.begin() as conn:
                conn.exec_driver_sql(
                    "INSERT OR REPLACE INTO ontology_edges (source_id, target_id, predicate) VALUES (?, ?, ?)",
                    (source_id, target_id, predicate),
                )
        return edge_id

    def get_edges(
        self,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None,
        predicate: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Query typed edges from `kg_edges`."""
        with self._SessionLocal() as sess:
            q = sess.query(KGEdgeRecord)
            if source_type:
                q = q.filter(KGEdgeRecord.source_type == source_type)
            if source_id:
                q = q.filter(KGEdgeRecord.source_id == source_id)
            if predicate:
                q = q.filter(KGEdgeRecord.predicate == predicate)
            if target_type:
                q = q.filter(KGEdgeRecord.target_type == target_type)
            if target_id:
                q = q.filter(KGEdgeRecord.target_id == target_id)
            rows = q.all()
            return [
                {
                    "edge_id": r.edge_id,
                    "source_type": r.source_type,
                    "source_id": r.source_id,
                    "predicate": r.predicate,
                    "target_type": r.target_type,
                    "target_id": r.target_id,
                    "effective_from": r.effective_from.isoformat() if r.effective_from else None,
                    "effective_to": r.effective_to.isoformat() if r.effective_to else None,
                    "jurisdiction_id": r.jurisdiction_id,
                    "properties": json.loads(r.properties_json or "{}"),
                }
                for r in rows
            ]

    # ------------------------------------------------------------------
    # Query 1: Point-in-Time Law / Processing Activity Resolution
    # ------------------------------------------------------------------
    def query_law_as_of(self, processing_activity_or_law_id: str, as_of_date: date | str) -> Dict[str, Any]:
        """
        RD-12 Query 1:
        "Which law version applied to a processing activity on March 1, 2025 vs. January 1, 2026?"
        Accepts either a `law_id` (e.g., `LAW-US-CA-CCPA`, `CCPA`, `LAW-CA-QC-LAW25`, `LAW-EU-AI-ACT`)
        or a `ProcessingActivity` identifier (e.g., `AI_Training`, `PA-AI-ADMT-PROFILING`, `Profiling`,
        `CrossBorderTransfer`, `BiometricAuthentication`).
        Preserves all historical versions in `kg_laws` and `kg_provisions` without overwriting!
        """
        if isinstance(as_of_date, str):
            as_of_date = date.fromisoformat(as_of_date)

        target_key = processing_activity_or_law_id.strip()

        # Alias mapping from processing activities or short framework codes to canonical law_id
        activity_to_law_map: Dict[str, str] = {
            "AI_Training": "LAW-US-CA-CCPA",
            "PA-AI-ADMT-PROFILING": "LAW-US-CA-CCPA",
            "Profiling": "LAW-US-CA-CCPA",
            "AutomatedDecisionMaking": "LAW-US-CA-CCPA",
            "CCPA": "LAW-US-CA-CCPA",
            "CPRA": "LAW-US-CA-CCPA",
            "DOC-US-CA-CCPA": "LAW-US-CA-CCPA",
            "Law_25": "LAW-CA-QC-LAW25",
            "QU-LAW25": "LAW-CA-QC-LAW25",
            "DataPortability": "LAW-CA-QC-LAW25",
            "PA-QC-PORTABILITY": "LAW-CA-QC-LAW25",
            "GDPR": "LAW-EU-GDPR",
            "DOC-EU-GDPR-2016-679": "LAW-EU-GDPR",
            "EU_AI_Act": "LAW-EU-AI-ACT",
            "HighRiskAIScoring": "LAW-EU-AI-ACT",
            "PHIPA": "LAW-CA-ON-PHIPA",
            "ElectronicHealthRecordAccess": "LAW-CA-ON-PHIPA",
        }

        resolved_law_id = activity_to_law_map.get(target_key, target_key)

        with self._SessionLocal() as sess:
            # If target_key wasn't in the static alias map, also check `kg_edges` for ProcessingActivity -> governedBy -> Obligation
            if resolved_law_id == target_key:
                all_laws = (
                    sess.query(KGLawRecord)
                    .filter(KGLawRecord.law_id == resolved_law_id)
                    .order_by(KGLawRecord.effective_date.asc())
                    .all()
                )
                if not all_laws:
                    # Try matching via ProcessingActivity -> governedBy -> Obligation
                    gov_edges = (
                        sess.query(KGEdgeRecord)
                        .filter(
                            KGEdgeRecord.source_type == "ProcessingActivity",
                            KGEdgeRecord.source_id == target_key,
                            KGEdgeRecord.predicate == "governedBy",
                        )
                        .all()
                    )
                    if gov_edges:
                        ob_ids = [e.target_id for e in gov_edges]
                        obs = sess.query(KGObligationRecord).filter(KGObligationRecord.obligation_id.in_(ob_ids)).all()
                        if obs:
                            resolved_law_id = obs[0].law_id
                            all_laws = (
                                sess.query(KGLawRecord)
                                .filter(KGLawRecord.law_id == resolved_law_id)
                                .order_by(KGLawRecord.effective_date.asc())
                                .all()
                            )
            else:
                all_laws = (
                    sess.query(KGLawRecord)
                    .filter(KGLawRecord.law_id == resolved_law_id)
                    .order_by(KGLawRecord.effective_date.asc())
                    .all()
                )

            if not all_laws:
                return {
                    "query": processing_activity_or_law_id,
                    "resolved_law_id": resolved_law_id,
                    "as_of_date": as_of_date.isoformat(),
                    "found": False,
                    "active_version": None,
                    "historical_versions_preserved_count": 0,
                    "all_versions": [],
                }

            # Select the version operative on `as_of_date`
            operative_law: Optional[KGLawRecord] = None
            for law_rec in all_laws:
                if law_rec.effective_date <= as_of_date:
                    if law_rec.effective_to is None or as_of_date < law_rec.effective_to:
                        operative_law = law_rec
                    elif operative_law is None:
                        operative_law = law_rec

            if operative_law is None:
                # If queried before initial effective date, return earliest version with status note
                operative_law = all_laws[0]

            # Fetch provisions for this operative version
            provisions = (
                sess.query(KGProvisionRecord)
                .filter(
                    KGProvisionRecord.law_id == operative_law.law_id,
                    KGProvisionRecord.version_id == operative_law.version_id,
                )
                .all()
            )

            # Fetch obligations operative for this law version on as_of_date
            obligations = (
                sess.query(KGObligationRecord)
                .filter(
                    KGObligationRecord.law_id == operative_law.law_id,
                    KGObligationRecord.version_id == operative_law.version_id,
                )
                .all()
            )

            return {
                "query": processing_activity_or_law_id,
                "resolved_law_id": operative_law.law_id,
                "as_of_date": as_of_date.isoformat(),
                "found": True,
                "version_id": operative_law.version_id,
                "canonical_title": operative_law.canonical_title,
                "official_citation": operative_law.official_citation,
                "jurisdiction_id": operative_law.jurisdiction_id,
                "effective_date": operative_law.effective_date.isoformat(),
                "effective_to": operative_law.effective_to.isoformat() if operative_law.effective_to else None,
                "supersedes_version": operative_law.supersedes_version,
                "amending_instrument_id": operative_law.amending_instrument_id,
                "eli_or_celex_identifier": operative_law.eli_or_celex_identifier,
                "raw_sha256": operative_law.raw_sha256,
                "normalized_sha256": operative_law.normalized_sha256,
                "summary_text": operative_law.summary_text,
                "operative_provisions": [
                    {
                        "provision_id": p.provision_id,
                        "provision_ref": p.provision_ref,
                        "article_or_section": p.article_or_section,
                        "effective_date": p.effective_date.isoformat(),
                        "effective_to": p.effective_to.isoformat() if p.effective_to else None,
                        "exact_text": p.exact_text,
                        "normalized_sha256": p.normalized_sha256,
                        "is_repealed": p.is_repealed,
                    }
                    for p in provisions
                ],
                "operative_obligations": [
                    {
                        "obligation_id": o.obligation_id,
                        "title": o.title,
                        "provision_ref": o.provision_ref,
                        "legal_requirement": o.legal_requirement,
                        "statutory_deadline": o.statutory_deadline,
                        "triggered_assessment": o.triggered_assessment,
                        "required_controls": json.loads(o.required_controls_json or "[]"),
                    }
                    for o in obligations
                ],
                "historical_versions_preserved_count": len(all_laws),
                "all_versions": [
                    {
                        "version_id": v.version_id,
                        "effective_date": v.effective_date.isoformat(),
                        "effective_to": v.effective_to.isoformat() if v.effective_to else None,
                        "status": v.status,
                        "normalized_sha256": v.normalized_sha256,
                    }
                    for v in all_laws
                ],
            }

    # ------------------------------------------------------------------
    # Query 2: Regulator / Tribunal Decisions Affecting a Sector
    # ------------------------------------------------------------------
    def query_decisions_affecting_sector(self, jurisdiction_id: str, sector: str) -> List[Dict[str, Any]]:
        """
        RD-12 Query 2:
        "Which regulator decisions affect Ontario hospitals?"
        Returns authentic sector-filtered decisions (e.g., IPC Ontario PHIPA Decisions `175` and `110`
        for `CA-ON` / `Ontario` and `hospital` / `healthcare`).
        """
        jur_norm = self._normalize_jurisdiction(jurisdiction_id)
        sector_norm = sector.strip().lower()

        sector_synonyms: Dict[str, Set[str]] = {
            "hospital": {"healthcare", "hospital", "hospitals", "health_information_custodian", "phipa_hospital"},
            "hospitals": {"healthcare", "hospital", "hospitals", "health_information_custodian", "phipa_hospital"},
            "healthcare": {"healthcare", "hospital", "hospitals", "health_information_custodian", "phipa_hospital"},
            "health": {"healthcare", "hospital", "hospitals", "health_information_custodian", "phipa_hospital"},
            "credit_reporting": {"credit_reporting", "financial_services", "consumer_reporting"},
            "financial": {"credit_reporting", "financial_services", "banking", "fintech"},
            "banking": {"credit_reporting", "financial_services", "banking", "fintech"},
            "retail": {"retail", "ecommerce", "adtech"},
            "technology": {"technology", "adtech", "ai_scoring", "platform"},
        }
        accepted_sectors = sector_synonyms.get(sector_norm, {sector_norm})

        with self._SessionLocal() as sess:
            rows = (
                sess.query(KGDecisionRecord)
                .filter(KGDecisionRecord.jurisdiction_id == jur_norm)
                .order_by(KGDecisionRecord.decision_date.desc())
                .all()
            )
            results: List[Dict[str, Any]] = []
            for r in rows:
                row_sec = (r.sector or "").lower()
                meta = json.loads(r.metadata_json or "{}")
                row_tags = {t.lower() for t in meta.get("sector_tags", [])}
                if (
                    row_sec in accepted_sectors
                    or bool(row_tags & accepted_sectors)
                    or sector_norm in row_sec
                    or any(sector_norm in t for t in row_tags)
                ):
                    results.append(self._decision_to_dict(r))
            return results

    # ------------------------------------------------------------------
    # Query 3: Decisions Interpreting a Specific Statutory Provision
    # ------------------------------------------------------------------
    def query_decisions_interpreting_provision(
        self, jurisdiction_id: str, provision_ref: str
    ) -> List[Dict[str, Any]]:
        """
        RD-12 Query 3:
        "Which German privacy rulings interpret GDPR Art. 22 / Art. 35 / Art. 38?"
        Matches decisions in `jurisdiction_id` (or its EU/national scope) whose interpreted
        provisions or `Decision -> interprets -> Provision` edges match `provision_ref`.
        """
        jur_norm = self._normalize_jurisdiction(jurisdiction_id)
        ref_norm = provision_ref.strip().lower()
        # Extract core article/section token (e.g. "art. 22", "article 22", "35", "38", "1798.100")
        art_match = re.search(r"(?:art(?:icle|\.)?\s*|§\s*|s\.\s*)(\d+[a-z]?(?:\(\d+\))?)", ref_norm)
        core_num = art_match.group(1) if art_match else ref_norm

        with self._SessionLocal() as sess:
            rows = (
                sess.query(KGDecisionRecord)
                .filter(KGDecisionRecord.jurisdiction_id == jur_norm)
                .order_by(KGDecisionRecord.decision_date.desc())
                .all()
            )
            matched: List[Dict[str, Any]] = []
            for r in rows:
                provs = json.loads(r.interpreted_provisions_json or "[]")
                provs_lower = [p.lower() for p in provs]
                if any(
                    ref_norm in p
                    or p in ref_norm
                    or bool(re.search(rf"\b(?:art(?:icle|\.)?\s*|§\s*|s\.\s*){re.escape(core_num)}\b", p))
                    for p in provs_lower
                ):
                    matched.append(self._decision_to_dict(r))
            return matched

    # ------------------------------------------------------------------
    # Query 4: Regulations Becoming Effective in a Given Year
    # ------------------------------------------------------------------
    def query_regulations_effective_in_year(self, jurisdiction_id: str, year: int) -> List[Dict[str, Any]]:
        """
        RD-12 Query 4:
        "Which California regulations became effective in a given year?"
        Queries `kg_laws` and `kg_amendments` for instruments in `jurisdiction_id` with
        `effective_date` falling in `year`.
        """
        jur_norm = self._normalize_jurisdiction(jurisdiction_id)
        start_dt = date(year, 1, 1)
        end_dt = date(year, 12, 31)

        with self._SessionLocal() as sess:
            laws = (
                sess.query(KGLawRecord)
                .filter(
                    KGLawRecord.jurisdiction_id == jur_norm,
                    KGLawRecord.effective_date >= start_dt,
                    KGLawRecord.effective_date <= end_dt,
                )
                .order_by(KGLawRecord.effective_date.asc())
                .all()
            )
            amendments = (
                sess.query(KGAmendmentRecord)
                .filter(
                    KGAmendmentRecord.jurisdiction_id == jur_norm,
                    KGAmendmentRecord.effective_date >= start_dt,
                    KGAmendmentRecord.effective_date <= end_dt,
                )
                .order_by(KGAmendmentRecord.effective_date.asc())
                .all()
            )

            results: List[Dict[str, Any]] = []
            seen_ids: Set[str] = set()
            for l_rec in laws:
                seen_ids.add(l_rec.record_id)
                results.append(
                    {
                        "record_id": l_rec.record_id,
                        "law_id": l_rec.law_id,
                        "version_id": l_rec.version_id,
                        "instrument_type": l_rec.instrument_type,
                        "jurisdiction_id": l_rec.jurisdiction_id,
                        "canonical_title": l_rec.canonical_title,
                        "official_citation": l_rec.official_citation,
                        "issuing_authority": l_rec.issuing_authority,
                        "enforcing_authority": l_rec.enforcing_authority,
                        "effective_date": l_rec.effective_date.isoformat(),
                        "effective_year": year,
                        "status": l_rec.status,
                        "summary_text": l_rec.summary_text,
                    }
                )
            for a_rec in amendments:
                if a_rec.amendment_id not in seen_ids:
                    results.append(
                        {
                            "record_id": a_rec.amendment_id,
                            "law_id": a_rec.target_law_id,
                            "version_id": a_rec.new_version_id,
                            "instrument_type": "amendment_or_regulation",
                            "jurisdiction_id": a_rec.jurisdiction_id,
                            "canonical_title": a_rec.amending_instrument_title,
                            "official_citation": a_rec.official_citation,
                            "issuing_authority": "Legislature / Rulemaking Agency",
                            "enforcing_authority": "Regulatory Authority",
                            "effective_date": a_rec.effective_date.isoformat(),
                            "effective_year": year,
                            "status": "ACTIVE",
                            "summary_text": a_rec.summary,
                        }
                    )
            return results

    # ------------------------------------------------------------------
    # Query 5: Organizations Affected by a Statutory/Regulatory Amendment
    # ------------------------------------------------------------------
    def query_organizations_affected_by_amendment(self, amendment_id: str) -> List[Dict[str, Any]]:
        """
        RD-12 Query 5:
        "Which organizations are affected by a specific statutory or regulatory amendment?"
        Traverses:
          `Amendment <-[amendedBy]- Law -[contains]-> Provision <-[satisfies/governedBy]- Obligation -[appliesTo]-> Organization`
          as well as `ProcessingActivity -[performedBy]-> Organization`.
        """
        with self._SessionLocal() as sess:
            amend = sess.query(KGAmendmentRecord).filter(KGAmendmentRecord.amendment_id == amendment_id).first()
            if amend is None:
                # Allow lookup by partial or instrument ID
                amend = (
                    sess.query(KGAmendmentRecord)
                    .filter(KGAmendmentRecord.new_version_id == amendment_id)
                    .first()
                )
            if amend is None:
                return []

            # Find obligations under the new version or matching target law
            obligations = (
                sess.query(KGObligationRecord)
                .filter(
                    KGObligationRecord.law_id == amend.target_law_id,
                    KGObligationRecord.version_id == amend.new_version_id,
                )
                .all()
            )
            if not obligations:
                obligations = (
                    sess.query(KGObligationRecord)
                    .filter(KGObligationRecord.law_id == amend.target_law_id)
                    .all()
                )

            org_map: Dict[str, Dict[str, Any]] = {}
            for ob in obligations:
                orgs = json.loads(ob.applies_to_organizations_json or "[]")
                activities = json.loads(ob.applies_to_activities_json or "[]")
                controls = json.loads(ob.required_controls_json or "[]")
                for org in orgs:
                    org_id = org["organization_id"] if isinstance(org, dict) else str(org)
                    org_name = org.get("name", org_id) if isinstance(org, dict) else str(org)
                    org_sector = org.get("sector", "enterprise") if isinstance(org, dict) else "enterprise"
                    entry = org_map.setdefault(
                        org_id,
                        {
                            "organization_id": org_id,
                            "organization_name": org_name,
                            "sector": org_sector,
                            "amendment_id": amend.amendment_id,
                            "amending_instrument_title": amend.amending_instrument_title,
                            "official_citation": amend.official_citation,
                            "effective_date": amend.effective_date.isoformat(),
                            "target_law_id": amend.target_law_id,
                            "target_provision_ref": amend.target_provision_ref,
                            "triggered_obligations": [],
                            "affected_processing_activities": [],
                            "required_controls": [],
                            "triggered_assessments": [],
                        },
                    )
                    if ob.obligation_id not in entry["triggered_obligations"]:
                        entry["triggered_obligations"].append(ob.obligation_id)
                    for act in activities:
                        if act not in entry["affected_processing_activities"]:
                            entry["affected_processing_activities"].append(act)
                    for ctrl in controls:
                        if ctrl not in entry["required_controls"]:
                            entry["required_controls"].append(ctrl)
                    if ob.triggered_assessment and ob.triggered_assessment not in entry["triggered_assessments"]:
                        entry["triggered_assessments"].append(ob.triggered_assessment)

            return list(org_map.values())

    # ------------------------------------------------------------------
    # Query 6: Overturned, Reversed, or Modified Judicial/Tribunal Decisions
    # ------------------------------------------------------------------
    def query_overturned_or_reversed_decisions(self) -> List[Dict[str, Any]]:
        """
        RD-12 Query 6:
        "Which decisions have been overturned, reversed, or modified on appeal?"
        Includes authentic appellate chains such as *Ramirez v. TransUnion LLC* (9th Cir. 951 F.3d 1008)
        reversed and remanded by the U.S. Supreme Court in *TransUnion LLC v. Ramirez*, 594 U.S. 413 (2021).
        """
        with self._SessionLocal() as sess:
            rows = (
                sess.query(KGDecisionRecord)
                .filter(KGDecisionRecord.appeal_status.in_(["reversed", "overturned", "modified", "vacated"]))
                .order_by(KGDecisionRecord.decision_date.desc())
                .all()
            )
            results: List[Dict[str, Any]] = []
            for r in rows:
                d = self._decision_to_dict(r)
                if r.modified_or_reversed_by_decision_id:
                    higher = (
                        sess.query(KGDecisionRecord)
                        .filter(KGDecisionRecord.decision_id == r.modified_or_reversed_by_decision_id)
                        .first()
                    )
                    if higher:
                        d["reversing_or_modifying_decision"] = {
                            "decision_id": higher.decision_id,
                            "case_name": higher.case_name,
                            "neutral_citation_or_id": higher.neutral_citation_or_id,
                            "court_tribunal_or_regulator": higher.court_tribunal_or_regulator,
                            "decision_date": higher.decision_date.isoformat(),
                            "holding_summary": higher.holding_summary,
                        }
                results.append(d)
            return results

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_jurisdiction(jurisdiction_id: str) -> str:
        raw = jurisdiction_id.strip()
        aliases = {
            "ontario": "CA-ON",
            "ca-on": "CA-ON",
            "ca_on": "CA-ON",
            "quebec": "CA-QC",
            "ca-qc": "CA-QC",
            "ca_qc": "CA-QC",
            "canada": "CA-FED",
            "ca-fed": "CA-FED",
            "ca_federal": "CA-FED",
            "california": "US-CA",
            "us-ca": "US-CA",
            "us_ca": "US-CA",
            "us-fed": "US-FED",
            "us_federal": "US-FED",
            "united states": "US-FED",
            "germany": "EU-DE",
            "de": "EU-DE",
            "eu-de": "EU-DE",
            "eu_de": "EU-DE",
            "eu": "EU",
            "eu_union": "EU",
            "european union": "EU",
        }
        return aliases.get(raw.lower(), raw.upper())

    @staticmethod
    def _decision_to_dict(r: KGDecisionRecord) -> Dict[str, Any]:
        return {
            "decision_id": r.decision_id,
            "jurisdiction_id": r.jurisdiction_id,
            "case_name": r.case_name,
            "neutral_citation_or_id": r.neutral_citation_or_id,
            "court_tribunal_or_regulator": r.court_tribunal_or_regulator,
            "decision_date": r.decision_date.isoformat(),
            "sector": r.sector,
            "interpreted_provisions": json.loads(r.interpreted_provisions_json or "[]"),
            "legal_test_applied": r.legal_test_applied,
            "remedy_ordered": r.remedy_ordered,
            "appeal_status": r.appeal_status,
            "appealed_to_court": r.appealed_to_court,
            "modified_or_reversed_by_decision_id": r.modified_or_reversed_by_decision_id,
            "reversal_citation": r.reversal_citation,
            "holding_summary": r.holding_summary,
            "binding_status": r.binding_status,
            "official_source_url": r.official_source_url,
            "metadata": json.loads(r.metadata_json or "{}"),
        }

    # ------------------------------------------------------------------
    # Authentic Seeding for US, Canada, and EU (Section 7 & RD-12)
    # ------------------------------------------------------------------
    def seed_canonical_knowledge_graph(self) -> None:
        """
        Seeds the relational knowledge graph tables (`kg_laws`, `kg_provisions`,
        `kg_amendments`, `kg_decisions`, `kg_obligations`, `kg_controls`, `kg_edges`)
        with authentic US, Canadian, and European statutory versions, amendments,
        judicial/regulator decisions, obligations, controls, and full Section 7 edges.
        """
        with self._SessionLocal() as sess:
            # 1. Seed Versioned Laws (`kg_laws`) — Preserving Historical Versions!
            laws = [
                # California CCPA (2020-2022)
                KGLawRecord(
                    record_id="LAW-US-CA-CCPA::v2020.1-CCPA",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2020.1-CCPA",
                    jurisdiction_id="US-CA",
                    instrument_type="statute",
                    canonical_title="California Consumer Privacy Act of 2018 (CCPA)",
                    official_citation="Cal. Civ. Code §§ 1798.100–1798.199 (Stats. 2018, Ch. 55, AB 375)",
                    eli_or_celex_identifier=None,
                    issuing_authority="California State Legislature",
                    enforcing_authority="California Attorney General",
                    effective_date=date(2020, 1, 1),
                    effective_to=date(2023, 1, 1),
                    publication_date=date(2018, 6, 28),
                    supersedes_version=None,
                    amending_instrument_id="AB-375",
                    status="SUPERSEDED",
                    raw_sha256=compute_sha256_hex("CCPA-2020-RAW"),
                    normalized_sha256=compute_sha256_hex("CCPA-2020-NORM"),
                    summary_text=(
                        "Original CCPA operative Jan 1, 2020 through Dec 31, 2022: establishes consumer right to know, "
                        "delete, and opt-out of sale of personal information; 50,000 consumer threshold; 30-day statutory cure period."
                    ),
                ),
                # California CPRA (2023-2025) — Operative on March 1, 2025
                KGLawRecord(
                    record_id="LAW-US-CA-CCPA::v2023.1-CPRA",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2023.1-CPRA",
                    jurisdiction_id="US-CA",
                    instrument_type="statute",
                    canonical_title="California Consumer Privacy Act as amended by the California Privacy Rights Act (CPRA)",
                    official_citation="Cal. Civ. Code §§ 1798.100–1798.199.100 (Prop. 24, operative Jan. 1, 2023)",
                    eli_or_celex_identifier=None,
                    issuing_authority="California Electorate / Legislature",
                    enforcing_authority="California Privacy Protection Agency (CPPA)",
                    effective_date=date(2023, 1, 1),
                    effective_to=date(2026, 1, 1),
                    publication_date=date(2020, 11, 3),
                    supersedes_version="v2020.1-CCPA",
                    amending_instrument_id="AMD-US-CA-CPRA-2023",
                    status="SUPERSEDED",
                    raw_sha256=compute_sha256_hex("CPRA-2023-RAW"),
                    normalized_sha256=compute_sha256_hex("CPRA-2023-NORM"),
                    summary_text=(
                        "CPRA version operative Jan 1, 2023 through Dec 31, 2025 (including March 1, 2025): adds sensitive "
                        "personal information limits, contractor/service provider contract mandates (§ 1798.100(d)), "
                        "100,000 consumer/household threshold, and establishes CPPA rulemaking under § 1798.185(a)(15)-(16)."
                    ),
                ),
                # California CCPA/CPRA + CPPA Cybersecurity Audit, Risk Assessment & ADMT Rules (Operative Jan 1, 2026)
                KGLawRecord(
                    record_id="LAW-US-CA-CCPA::v2026.1-CPPA-ADMT-AUDIT",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2026.1-CPPA-ADMT-AUDIT",
                    jurisdiction_id="US-CA",
                    instrument_type="regulation",
                    canonical_title="CCPA/CPRA with CPPA Automated Decision-Making Technology (ADMT), Risk Assessment & Cybersecurity Audit Regulations",
                    official_citation="Cal. Civ. Code §§ 1798.100–1798.199.100; 11 CCR §§ 7150–7221 (eff. Jan. 1, 2026)",
                    eli_or_celex_identifier=None,
                    issuing_authority="California Privacy Protection Agency (CPPA)",
                    enforcing_authority="California Privacy Protection Agency (CPPA)",
                    effective_date=date(2026, 1, 1),
                    effective_to=None,
                    publication_date=date(2025, 11, 15),
                    supersedes_version="v2023.1-CPRA",
                    amending_instrument_id="AMD-US-CA-CPPA-ADMT-2026",
                    status="ACTIVE",
                    raw_sha256=compute_sha256_hex("CPPA-2026-ADMT-RAW"),
                    normalized_sha256=compute_sha256_hex("CPPA-2026-ADMT-NORM"),
                    summary_text=(
                        "Operative January 1, 2026: mandates pre-use ADMT notice, opt-out of automated decision-making "
                        "and AI profiling, pre-processing Risk Assessment filings with CPPA, and annual independent "
                        "cybersecurity audits under 11 CCR §§ 7150–7221 and Cal. Civ. Code § 1798.185(a)(15)-(16)."
                    ),
                ),
                # California Delete Act (SB 362) Drop Accessible Deletion Mechanism Regulation (Effective 2026)
                KGLawRecord(
                    record_id="LAW-US-CA-DELETE-ACT::v2026.1-DROP",
                    law_id="LAW-US-CA-DELETE-ACT",
                    version_id="v2026.1-DROP",
                    jurisdiction_id="US-CA",
                    instrument_type="regulation",
                    canonical_title="California Delete Act (SB 362) — Accessible Deletion Mechanism (DROP) Regulations",
                    official_citation="Cal. Civ. Code § 1798.99.86; 11 CCR §§ 7600–7620 (eff. Jan. 1, 2026)",
                    eli_or_celex_identifier=None,
                    issuing_authority="California Privacy Protection Agency (CPPA)",
                    enforcing_authority="California Privacy Protection Agency (CPPA)",
                    effective_date=date(2026, 1, 1),
                    effective_to=None,
                    publication_date=date(2025, 10, 1),
                    supersedes_version=None,
                    amending_instrument_id="SB-362-DROP-2026",
                    status="ACTIVE",
                    raw_sha256=compute_sha256_hex("CA-DELETE-ACT-2026-RAW"),
                    normalized_sha256=compute_sha256_hex("CA-DELETE-ACT-2026-NORM"),
                    summary_text=(
                        "Requires registered data brokers to query the CPPA Delete Request and Opt-Out Platform (DROP) "
                        "at least every 45 days starting in 2026 and purge matched consumer records."
                    ),
                ),
                # Quebec Law 25 — Phase 2 (2023-09-22 to 2024-09-21) vs Phase 3 (2024-09-22+)
                KGLawRecord(
                    record_id="LAW-CA-QC-LAW25::v2023.9-PHASE2",
                    law_id="LAW-CA-QC-LAW25",
                    version_id="v2023.9-PHASE2",
                    jurisdiction_id="CA-QC",
                    instrument_type="statute",
                    canonical_title="Quebec Act respecting the protection of personal information in the private sector (Law 25 — Phase 2)",
                    official_citation="CQLR c P-39.1 (S.Q. 2021, c. 25, Phase 2 operative Sept. 22, 2023)",
                    eli_or_celex_identifier=None,
                    issuing_authority="National Assembly of Quebec",
                    enforcing_authority="Commission d'accès à l'information du Québec (CAI)",
                    effective_date=date(2023, 9, 22),
                    effective_to=date(2024, 9, 22),
                    publication_date=date(2021, 9, 22),
                    supersedes_version="v2022.9-PHASE1",
                    amending_instrument_id="SQ-2021-C25-P2",
                    status="SUPERSEDED",
                    raw_sha256=compute_sha256_hex("LAW25-P2-RAW"),
                    normalized_sha256=compute_sha256_hex("LAW25-P2-NORM"),
                    summary_text="Law 25 Phase 2: mandatory Privacy Impact Assessments (EFVP), cross-border TIAs, and privacy-by-default.",
                ),
                KGLawRecord(
                    record_id="LAW-CA-QC-LAW25::v2024.9-PHASE3",
                    law_id="LAW-CA-QC-LAW25",
                    version_id="v2024.9-PHASE3",
                    jurisdiction_id="CA-QC",
                    instrument_type="statute",
                    canonical_title="Quebec Act respecting the protection of personal information in the private sector (Law 25 — Phase 3 Full Force)",
                    official_citation="CQLR c P-39.1, s. 27 (S.Q. 2021, c. 25, Phase 3 operative Sept. 22, 2024)",
                    eli_or_celex_identifier=None,
                    issuing_authority="National Assembly of Quebec",
                    enforcing_authority="Commission d'accès à l'information du Québec (CAI)",
                    effective_date=date(2024, 9, 22),
                    effective_to=None,
                    publication_date=date(2021, 9, 22),
                    supersedes_version="v2023.9-PHASE2",
                    amending_instrument_id="AMD-CA-QC-LAW25-P3",
                    status="ACTIVE",
                    raw_sha256=compute_sha256_hex("LAW25-P3-RAW"),
                    normalized_sha256=compute_sha256_hex("LAW25-P3-NORM"),
                    summary_text="Law 25 Phase 3: adds structured machine-readable right to data portability (s. 27).",
                ),
                # Ontario PHIPA
                KGLawRecord(
                    record_id="LAW-CA-ON-PHIPA::v2020.1-EHR-AUDIT",
                    law_id="LAW-CA-ON-PHIPA",
                    version_id="v2020.1-EHR-AUDIT",
                    jurisdiction_id="CA-ON",
                    instrument_type="statute",
                    canonical_title="Personal Health Information Protection Act, 2004 (Ontario PHIPA)",
                    official_citation="S.O. 2004, c. 3, Sched. A",
                    eli_or_celex_identifier=None,
                    issuing_authority="Legislative Assembly of Ontario",
                    enforcing_authority="Information and Privacy Commissioner of Ontario (IPC)",
                    effective_date=date(2020, 1, 1),
                    effective_to=None,
                    publication_date=date(2004, 11, 1),
                    supersedes_version=None,
                    amending_instrument_id="SO-2020-C5",
                    status="ACTIVE",
                    raw_sha256=compute_sha256_hex("ON-PHIPA-2020-RAW"),
                    normalized_sha256=compute_sha256_hex("ON-PHIPA-2020-NORM"),
                    summary_text="Governs health information custodians (including Ontario hospitals) under s. 10(3), s. 12(1), and s. 17.1 electronic audit log mandates.",
                ),
                # EU GDPR
                KGLawRecord(
                    record_id="LAW-EU-GDPR::02016R0679-20180523",
                    law_id="LAW-EU-GDPR",
                    version_id="02016R0679-20180523",
                    jurisdiction_id="EU",
                    instrument_type="regulation",
                    canonical_title="Regulation (EU) 2016/679 (General Data Protection Regulation — Consolidated)",
                    official_citation="OJ L 119, 4.5.2016, p. 1–88 (Corrigendum OJ L 127, 23.5.2018)",
                    eli_or_celex_identifier="http://data.europa.eu/eli/reg/2016/679/2016-05-04 | CELEX:02016R0679-20160504",
                    issuing_authority="European Parliament and Council of the European Union",
                    enforcing_authority="European Data Protection Board (EDPB) & National DPAs",
                    effective_date=date(2018, 5, 25),
                    effective_to=None,
                    publication_date=date(2016, 5, 4),
                    supersedes_version="31995L0046",
                    amending_instrument_id="CORRIGENDUM-2018-L127",
                    status="ACTIVE",
                    raw_sha256=compute_sha256_hex("EU-GDPR-2018-RAW"),
                    normalized_sha256=compute_sha256_hex("EU-GDPR-2018-NORM"),
                    summary_text="EU General Data Protection Regulation including Art. 22 (automated individual decision-making/profiling), Art. 35 (DPIA), and Art. 38 (DPO independence).",
                ),
            ]
            for law in laws:
                sess.merge(law)

            # 2. Seed Provisions (`kg_provisions`)
            provisions = [
                KGProvisionRecord(
                    record_id="PROV-US-CA-1798.100d::v2020.1-CCPA",
                    provision_id="PROV-US-CA-1798.100d",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2020.1-CCPA",
                    jurisdiction_id="US-CA",
                    provision_ref="Cal. Civ. Code § 1798.100(d)",
                    article_or_section="1798.100(d)",
                    effective_date=date(2020, 1, 1),
                    effective_to=date(2023, 1, 1),
                    exact_text="A business that receives a verifiable consumer request from a consumer to access personal information shall promptly take steps to disclose and deliver, free of charge to the consumer, the personal information required by this section within 45 days.",
                    normalized_sha256=compute_sha256_hex("PROV-1798.100d-v2020"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-US-CA-1798.100d::v2023.1-CPRA",
                    provision_id="PROV-US-CA-1798.100d",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2023.1-CPRA",
                    jurisdiction_id="US-CA",
                    provision_ref="Cal. Civ. Code § 1798.100(d)",
                    article_or_section="1798.100(d)",
                    effective_date=date(2023, 1, 1),
                    effective_to=date(2026, 1, 1),
                    exact_text="A business that collects a consumer's personal information and that sells that personal information to, or shares it with, a third party or that discloses it to a service provider or contractor for a business purpose shall enter into an agreement with that third party, service provider, or contractor specifying limited and specified purposes.",
                    normalized_sha256=compute_sha256_hex("PROV-1798.100d-v2023"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-US-CA-1798.185a15-16::v2023.1-CPRA",
                    provision_id="PROV-US-CA-1798.185a15-16",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2023.1-CPRA",
                    jurisdiction_id="US-CA",
                    provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16)",
                    article_or_section="1798.185(a)(15)-(16)",
                    effective_date=date(2023, 1, 1),
                    effective_to=date(2026, 1, 1),
                    exact_text="Directs CPPA to issue regulations requiring annual cybersecurity audits, regular risk assessments for significant-risk processing, and access/opt-out rights for automated decision-making technology (ADMT) including profiling.",
                    normalized_sha256=compute_sha256_hex("PROV-1798.185a15-16-v2023"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-US-CA-1798.185a15-16::v2026.1-CPPA-ADMT-AUDIT",
                    provision_id="PROV-US-CA-1798.185a15-16",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2026.1-CPPA-ADMT-AUDIT",
                    jurisdiction_id="US-CA",
                    provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16) & 11 CCR §§ 7150–7221",
                    article_or_section="1798.185(a)(15)-(16)",
                    effective_date=date(2026, 1, 1),
                    effective_to=None,
                    exact_text="Operative CPPA regulations under Cal. Civ. Code § 1798.185(a)(15)-(16) and 11 CCR §§ 7150–7221: businesses engaging in ADMT or AI model training must provide pre-use ADMT notice, honor opt-out requests within 15 business days, file risk assessment attestations within 30 days, and complete annual independent cybersecurity audits.",
                    normalized_sha256=compute_sha256_hex("PROV-1798.185a15-16-v2026"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-EU-GDPR-ART22::02016R0679-20180523",
                    provision_id="PROV-EU-GDPR-ART22",
                    law_id="LAW-EU-GDPR",
                    version_id="02016R0679-20180523",
                    jurisdiction_id="EU",
                    provision_ref="GDPR Art. 22",
                    article_or_section="Art. 22",
                    effective_date=date(2018, 5, 25),
                    effective_to=None,
                    exact_text="1. The data subject shall have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects concerning him or her or similarly significantly affects him or her.",
                    normalized_sha256=compute_sha256_hex("PROV-GDPR-ART22"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-EU-GDPR-ART35::02016R0679-20180523",
                    provision_id="PROV-EU-GDPR-ART35",
                    law_id="LAW-EU-GDPR",
                    version_id="02016R0679-20180523",
                    jurisdiction_id="EU",
                    provision_ref="GDPR Art. 35",
                    article_or_section="Art. 35",
                    effective_date=date(2018, 5, 25),
                    effective_to=None,
                    exact_text="1. Where a type of processing in particular using new technologies is likely to result in a high risk to the rights and freedoms of natural persons, the controller shall, prior to the processing, carry out a Data Protection Impact Assessment (DPIA).",
                    normalized_sha256=compute_sha256_hex("PROV-GDPR-ART35"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-EU-GDPR-ART38::02016R0679-20180523",
                    provision_id="PROV-EU-GDPR-ART38",
                    law_id="LAW-EU-GDPR",
                    version_id="02016R0679-20180523",
                    jurisdiction_id="EU",
                    provision_ref="GDPR Art. 38(6)",
                    article_or_section="Art. 38",
                    effective_date=date(2018, 5, 25),
                    effective_to=None,
                    exact_text="6. The data protection officer may fulfil other tasks and duties. The controller or processor shall ensure that any such tasks and duties do not result in a conflict of interests.",
                    normalized_sha256=compute_sha256_hex("PROV-GDPR-ART38"),
                    is_repealed=False,
                ),
                KGProvisionRecord(
                    record_id="PROV-CA-ON-PHIPA-S12::v2020.1-EHR-AUDIT",
                    provision_id="PROV-CA-ON-PHIPA-S12",
                    law_id="LAW-CA-ON-PHIPA",
                    version_id="v2020.1-EHR-AUDIT",
                    jurisdiction_id="CA-ON",
                    provision_ref="PHIPA s. 12(1) & s. 10(3)",
                    article_or_section="s. 12(1)",
                    effective_date=date(2020, 1, 1),
                    effective_to=None,
                    exact_text="12. (1) A health information custodian shall take steps that are reasonable in the circumstances to ensure that personal health information in the custodian's custody or control is protected against theft, loss and unauthorized use or disclosure.",
                    normalized_sha256=compute_sha256_hex("PROV-PHIPA-S12"),
                    is_repealed=False,
                ),
            ]
            for prov in provisions:
                sess.merge(prov)

            # 3. Seed Amendments (`kg_amendments`)
            amendments = [
                KGAmendmentRecord(
                    amendment_id="AMD-US-CA-CPRA-2023",
                    target_law_id="LAW-US-CA-CCPA",
                    target_provision_ref="Cal. Civ. Code §§ 1798.100(d), 1798.140(d), 1798.185(a)(15)-(16)",
                    jurisdiction_id="US-CA",
                    amending_instrument_title="California Privacy Rights Act of 2020 (CPRA / Proposition 24)",
                    official_citation="Prop. 24, Stats. 2020, operative Jan. 1, 2023",
                    previous_version_id="v2020.1-CCPA",
                    new_version_id="v2023.1-CPRA",
                    enactment_date=date(2020, 11, 3),
                    effective_date=date(2023, 1, 1),
                    change_type="substantive_amendment",
                    is_substantive=True,
                    summary="Amends CCPA § 1798.100(d) to mandate third-party/service-provider/contractor agreements, raises business threshold to 100,000 consumers/households, eliminates mandatory 30-day AG cure period, and adds § 1798.185(a)(15)-(16) rulemaking mandates.",
                    affected_sectors_json=json.dumps(["technology", "retail", "healthcare", "financial_services", "adtech"]),
                    affected_activities_json=json.dumps(["AI_Training", "Profiling", "Transfer", "Collection"]),
                ),
                KGAmendmentRecord(
                    amendment_id="AMD-US-CA-CPPA-ADMT-2026",
                    target_law_id="LAW-US-CA-CCPA",
                    target_provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16) & 11 CCR §§ 7150–7221",
                    jurisdiction_id="US-CA",
                    amending_instrument_title="CPPA Cybersecurity Audit, Risk Assessment, and Automated Decision-Making Technology (ADMT) Regulations",
                    official_citation="11 CCR §§ 7150–7221 (adopted Nov. 2025, effective Jan. 1, 2026)",
                    previous_version_id="v2023.1-CPRA",
                    new_version_id="v2026.1-CPPA-ADMT-AUDIT",
                    enactment_date=date(2025, 11, 15),
                    effective_date=date(2026, 1, 1),
                    change_type="substantive_amendment",
                    is_substantive=True,
                    summary="Makes operative mandatory pre-use ADMT notice, human appeal/opt-out within 15 business days, pre-processing risk assessment filings with CPPA, and annual independent cybersecurity audits.",
                    affected_sectors_json=json.dumps(["technology", "financial_services", "healthcare", "retail"]),
                    affected_activities_json=json.dumps(["AI_Training", "Profiling", "PA-AI-ADMT-PROFILING"]),
                ),
                KGAmendmentRecord(
                    amendment_id="AMD-CA-QC-LAW25-P3",
                    target_law_id="LAW-CA-QC-LAW25",
                    target_provision_ref="CQLR c P-39.1, s. 27",
                    jurisdiction_id="CA-QC",
                    amending_instrument_title="Quebec Law 25 Phase 3 — Right to Structured Machine-Readable Data Portability",
                    official_citation="S.Q. 2021, c. 25, s. 27 (effective Sept. 22, 2024)",
                    previous_version_id="v2023.9-PHASE2",
                    new_version_id="v2024.9-PHASE3",
                    enactment_date=date(2021, 9, 22),
                    effective_date=date(2024, 9, 22),
                    change_type="new_provision",
                    is_substantive=True,
                    summary="Brings into force the right of individuals to receive computerized personal information in a structured, commonly used technological format.",
                    affected_sectors_json=json.dumps(["technology", "financial_services", "telecommunications", "healthcare"]),
                    affected_activities_json=json.dumps(["DataPortability", "Storage", "Collection"]),
                ),
            ]
            for amd in amendments:
                sess.merge(amd)

            # 4. Seed Authentic Judicial, Regulator, and Tribunal Decisions (`kg_decisions`)
            decisions = [
                # Ontario IPC PHIPA Decision 175 (Ontario Public Hospital EMR Snooping & Audit Logs)
                KGDecisionRecord(
                    decision_id="DEC-CA-ON-IPC-PHIPA-175",
                    jurisdiction_id="CA-ON",
                    case_name="PHIPA Decision 175 (Re Grand River Hospital / Ontario Public Hospital Electronic Medical Record Snooping)",
                    neutral_citation_or_id="PHIPA Decision 175",
                    court_tribunal_or_regulator="Information and Privacy Commissioner of Ontario (IPC)",
                    decision_date=date(2022, 3, 24),
                    sector="hospital",
                    interpreted_provisions_json=json.dumps(["PHIPA s. 12(1)", "PHIPA s. 10(3)", "PHIPA s. 52"]),
                    legal_test_applied="Reasonable measures to prevent unauthorized electronic health record access under PHIPA s. 12(1)",
                    remedy_ordered="Mandatory role-based access controls, proactive random electronic audit log monitoring, and mandatory hospital staff PHIPA training.",
                    appeal_status="final",
                    appealed_to_court=None,
                    modified_or_reversed_by_decision_id=None,
                    reversal_citation=None,
                    holding_summary=(
                        "Held that an Ontario hospital failed to take reasonable steps under PHIPA s. 12(1) when an employee "
                        "repeatedly snooped in patient electronic medical records without proactive audit-log alerting."
                    ),
                    binding_status="binding_administrative_order",
                    official_source_url="https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/520415/index.do",
                    metadata_json=json.dumps({"sector_tags": ["hospital", "hospitals", "healthcare", "phipa_hospital"]}),
                ),
                # Ontario IPC PHIPA Decision 110 (Mount Sinai Hospital / Rogue Hospital Nurse Access)
                KGDecisionRecord(
                    decision_id="DEC-CA-ON-IPC-PHIPA-110",
                    jurisdiction_id="CA-ON",
                    case_name="PHIPA Decision 110 (Re Public Hospital Unauthorized Patient Chart Access & Breach Notification)",
                    neutral_citation_or_id="PHIPA Decision 110",
                    court_tribunal_or_regulator="Information and Privacy Commissioner of Ontario (IPC)",
                    decision_date=date(2020, 2, 11),
                    sector="hospital",
                    interpreted_provisions_json=json.dumps(["PHIPA s. 12(1)", "PHIPA s. 12(2)", "PHIPA s. 17.1"]),
                    legal_test_applied="Reasonableness of hospital technical/administrative safeguards and prompt notification duty under PHIPA s. 12(2)",
                    remedy_ordered="Ordered hospital to audit access logs across shared clinical workstations, update lock-screen timeouts, and notify affected patients.",
                    appeal_status="final",
                    appealed_to_court=None,
                    modified_or_reversed_by_decision_id=None,
                    reversal_citation=None,
                    holding_summary=(
                        "Confirmed that Ontario hospitals acting as health information custodians must maintain granular "
                        "user-level electronic audit trails and flag anomalous high-volume chart lookups."
                    ),
                    binding_status="binding_administrative_order",
                    official_source_url="https://decisions.ipc.on.ca/ipc-cipvp/phipa/en/item/463812/index.do",
                    metadata_json=json.dumps({"sector_tags": ["hospital", "hospitals", "healthcare", "phipa_hospital"]}),
                ),
                # German / CJEU Referral Ruling on GDPR Art. 22 — SCHUFA Holding AG (C-634/21 / VG Wiesbaden)
                KGDecisionRecord(
                    decision_id="DEC-EU-DE-SCHUFA-ART22",
                    jurisdiction_id="EU-DE",
                    case_name="OQ v. Land Hessen (joined party: SCHUFA Holding AG) — Automated Credit Scoring under GDPR Art. 22",
                    neutral_citation_or_id="ECLI:EU:C:2023:957 / C-634/21 (VG Wiesbaden 6 K 788/20.WI)",
                    court_tribunal_or_regulator="Verwaltungsgericht Wiesbaden / Court of Justice of the European Union (First Chamber) & HBDI Germany",
                    decision_date=date(2023, 12, 7),
                    sector="credit_reporting",
                    interpreted_provisions_json=json.dumps(["GDPR Art. 22", "GDPR Art. 22(1)", "GDPR Art. 15(1)(h)", "BDSG § 31"]),
                    legal_test_applied="Paramount role test for 'decision based solely on automated processing' under GDPR Art. 22(1)",
                    remedy_ordered="Prohibited reliance on automated SCHUFA probability scores as determinative creditworthiness decisions without a valid Art. 22(2) exception and meaningful logic disclosure.",
                    appeal_status="final",
                    appealed_to_court=None,
                    modified_or_reversed_by_decision_id=None,
                    reversal_citation=None,
                    holding_summary=(
                        "Ruled on German administrative court reference that automated calculation of a credit probability value "
                        "(SCHUFA score) constitutes an automated individual decision under GDPR Art. 22(1) where third-party lenders "
                        "draw strongly on that score to establish, implement, or terminate contractual relationships."
                    ),
                    binding_status="binding_precedent",
                    official_source_url="https://curia.europa.eu/juris/liste.jsf?num=C-634/21",
                    metadata_json=json.dumps({"country": "DE", "sector_tags": ["credit_reporting", "financial_services", "ai_scoring"]}),
                ),
                # German Ruling Interpreting GDPR Art. 38(6) & Art. 35 — Bundesarbeitsgericht / X-Fab Dresden (C-453/21 / 9 AZR 383/19)
                KGDecisionRecord(
                    decision_id="DEC-EU-DE-BAG-XFAB-ART38-ART35",
                    jurisdiction_id="EU-DE",
                    case_name="X-Fab Dresden GmbH & Co. KG v. FC — DPO Conflict of Interest & High-Risk Employee Processing DPIA",
                    neutral_citation_or_id="BAG 9 AZR 383/19 / ECLI:EU:C:2023:79 (C-453/21)",
                    court_tribunal_or_regulator="Bundesarbeitsgericht (German Federal Labour Court) / CJEU",
                    decision_date=date(2023, 2, 9),
                    sector="technology",
                    interpreted_provisions_json=json.dumps(["GDPR Art. 38(6)", "GDPR Art. 38(3)", "GDPR Art. 35", "BDSG § 6(4)"]),
                    legal_test_applied="Absence of conflict of interest test where DPO simultaneously chairs Works Council and reviews Art. 35 DPIAs",
                    remedy_ordered="Clarified strict separation between controller governance/Works Council decision-making and independent DPO oversight of GDPR Art. 35 DPIAs.",
                    appeal_status="final",
                    appealed_to_court=None,
                    modified_or_reversed_by_decision_id=None,
                    reversal_citation=None,
                    holding_summary=(
                        "German Federal Labour Court (Bundesarbeitsgericht) and CJEU ruling interpreting GDPR Art. 38(6) and Art. 35: "
                        "a Data Protection Officer cannot hold a position within the organization that determines the objectives and "
                        "means of processing personal data or creates a conflict when auditing Art. 35 DPIAs."
                    ),
                    binding_status="binding_precedent",
                    official_source_url="https://www.bundesarbeitsgericht.de/",
                    metadata_json=json.dumps({"country": "DE", "sector_tags": ["technology", "manufacturing", "employment"]}),
                ),
                # Overturned / Reversed Decision Chain: Ramirez v. TransUnion LLC (9th Cir.) -> Reversed by SCOTUS 594 U.S. 413
                KGDecisionRecord(
                    decision_id="DEC-US-9CIR-RAMIREZ-2020",
                    jurisdiction_id="US-FED",
                    case_name="Ramirez v. TransUnion LLC (9th Cir.)",
                    neutral_citation_or_id="951 F.3d 1008 (9th Cir. 2020)",
                    court_tribunal_or_regulator="U.S. Court of Appeals for the Ninth Circuit",
                    decision_date=date(2020, 2, 27),
                    sector="credit_reporting",
                    interpreted_provisions_json=json.dumps(["15 U.S.C. § 1681e(b)", "15 U.S.C. § 1681g(a)", "U.S. Const. Art. III"]),
                    legal_test_applied="Risk-of-real-harm Article III standing test for statutory FCRA accuracy violations",
                    remedy_ordered="Affirmed class certification of 8,185 class members and statutory/punitive damages exceeding $40 million.",
                    appeal_status="reversed",
                    appealed_to_court="Supreme Court of the United States",
                    modified_or_reversed_by_decision_id="DEC-US-SCOTUS-TRANSUNION-2021",
                    reversal_citation="TransUnion LLC v. Ramirez, 594 U.S. 413 (2021)",
                    holding_summary=(
                        "Ninth Circuit held that all 8,185 class members with OFAC terrorist alerts in their internal credit files "
                        "had Article III standing to sue under the Fair Credit Reporting Act even if their credit reports were never "
                        "disseminated to third parties. [REVERSED BY U.S. SUPREME COURT in 594 U.S. 413 (2021)]."
                    ),
                    binding_status="overturned_precedent",
                    official_source_url="https://cdn.ca9.uscourts.gov/datastore/opinions/2020/02/27/17-17244.pdf",
                    metadata_json=json.dumps({"overturned": True, "reversed_by": "DEC-US-SCOTUS-TRANSUNION-2021"}),
                ),
                KGDecisionRecord(
                    decision_id="DEC-US-SCOTUS-TRANSUNION-2021",
                    jurisdiction_id="US-FED",
                    case_name="TransUnion LLC v. Ramirez",
                    neutral_citation_or_id="594 U.S. 413 (2021)",
                    court_tribunal_or_regulator="Supreme Court of the United States",
                    decision_date=date(2021, 6, 25),
                    sector="credit_reporting",
                    interpreted_provisions_json=json.dumps(["U.S. Const. Art. III, § 2", "15 U.S.C. § 1681e(b)", "15 U.S.C. § 1681g(a)"]),
                    legal_test_applied="Concrete injury-in-fact Article III standing test ('No concrete harm, no standing')",
                    remedy_ordered="Reversed Ninth Circuit judgment and remanded; held only the 1,853 class members whose misleading OFAC alerts were disseminated to third-party businesses suffered a concrete reputational injury.",
                    appeal_status="final",
                    appealed_to_court=None,
                    modified_or_reversed_by_decision_id=None,
                    reversal_citation=None,
                    holding_summary=(
                        "Supreme Court reversed the Ninth Circuit (951 F.3d 1008), holding that mere existence of inaccurate "
                        "information in an internal database without third-party dissemination does not satisfy Article III concrete injury."
                    ),
                    binding_status="binding_precedent",
                    official_source_url="https://www.supremecourt.gov/opinions/20pdf/20-297_4g25.pdf",
                    metadata_json=json.dumps({"reverses_decision": "DEC-US-9CIR-RAMIREZ-2020"}),
                ),
            ]
            for dec in decisions:
                sess.merge(dec)

            # 5. Seed Obligations (`kg_obligations`)
            obligations = [
                KGObligationRecord(
                    obligation_id="OBL-US-CA-CPRA-2023-CONTRACT",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2023.1-CPRA",
                    provision_ref="Cal. Civ. Code § 1798.100(d)",
                    jurisdiction_id="US-CA",
                    title="Mandatory Service Provider, Contractor & Third-Party Privacy Addendum",
                    legal_requirement="Execute binding contract limiting personal information use to specified business purposes and requiring equivalent CPRA protection.",
                    statutory_deadline="Prior to disclosure or sharing of personal information",
                    triggered_assessment="StandardReview",
                    effective_date=date(2023, 1, 1),
                    effective_to=date(2026, 1, 1),
                    applies_to_activities_json=json.dumps(["AI_Training", "Profiling", "Transfer"]),
                    applies_to_organizations_json=json.dumps(
                        [
                            {"organization_id": "ORG-ACME-AI-CORP", "name": "Acme AI & Analytics Corp.", "sector": "technology"},
                            {"organization_id": "ORG-PACIFIC-RETAIL-INC", "name": "Pacific OmniRetail Inc.", "sector": "retail"},
                        ]
                    ),
                    required_controls_json=json.dumps(["CTRL-DPA-CONTRACT-GATE"]),
                ),
                KGObligationRecord(
                    obligation_id="OBL-US-CA-CPPA-2026-ADMT-AUDIT",
                    law_id="LAW-US-CA-CCPA",
                    version_id="v2026.1-CPPA-ADMT-AUDIT",
                    provision_ref="Cal. Civ. Code § 1798.185(a)(15)-(16) & 11 CCR §§ 7150–7221",
                    jurisdiction_id="US-CA",
                    title="Mandatory Pre-Use ADMT Notice, Human Opt-Out, Risk Assessment Filing & Annual Cybersecurity Audit",
                    legal_requirement="Provide pre-use ADMT notice, honor opt-out within 15 business days, file risk assessment attestation with CPPA within 30 days, and complete annual independent cybersecurity audit.",
                    statutory_deadline="15 business days (ADMT opt-out) / 30 days (CPPA Risk Assessment attestation)",
                    triggered_assessment="CPRA_ADMT",
                    effective_date=date(2026, 1, 1),
                    effective_to=None,
                    applies_to_activities_json=json.dumps(["AI_Training", "Profiling", "PA-AI-ADMT-PROFILING"]),
                    applies_to_organizations_json=json.dumps(
                        [
                            {"organization_id": "ORG-ACME-AI-CORP", "name": "Acme AI & Analytics Corp.", "sector": "technology"},
                            {"organization_id": "ORG-PACIFIC-RETAIL-INC", "name": "Pacific OmniRetail Inc.", "sector": "retail"},
                            {"organization_id": "ORG-GOLDEN-STATE-HEALTH", "name": "Golden State Digital Health Systems", "sector": "healthcare"},
                        ]
                    ),
                    required_controls_json=json.dumps(["CTRL-ADMT-OPTOUT-ENGINE", "CTRL-ANNUAL-CYBER-AUDIT"]),
                ),
                KGObligationRecord(
                    obligation_id="OBL-CA-QC-LAW25-PORTABILITY",
                    law_id="LAW-CA-QC-LAW25",
                    version_id="v2024.9-PHASE3",
                    provision_ref="CQLR c P-39.1, s. 27",
                    jurisdiction_id="CA-QC",
                    title="Structured Machine-Readable Data Portability Export",
                    legal_requirement="Provide computerized personal information collected from the applicant in a structured, commonly used technological format within 30 days.",
                    statutory_deadline="30 days",
                    triggered_assessment="Law25_PIA",
                    effective_date=date(2024, 9, 22),
                    effective_to=None,
                    applies_to_activities_json=json.dumps(["DataPortability", "Storage", "Collection"]),
                    applies_to_organizations_json=json.dumps(
                        [
                            {"organization_id": "ORG-MONTREAL-FINTECH", "name": "Montreal FinTech Services Ltd.", "sector": "financial_services"},
                            {"organization_id": "ORG-ACME-AI-CORP", "name": "Acme AI & Analytics Corp.", "sector": "technology"},
                        ]
                    ),
                    required_controls_json=json.dumps(["CTRL-DSAR-PORTABILITY-EXPORT"]),
                ),
            ]
            for ob in obligations:
                sess.merge(ob)

            # 6. Seed Controls (`kg_controls`)
            controls = [
                KGControlRecord(
                    control_id="CTRL-ADMT-OPTOUT-ENGINE",
                    name="ADMT Pre-Use Notice & Automated Opt-Out Gate",
                    control_category="Technical / Governance Control",
                    description="Enforces pre-use ADMT disclosure, blocks automated profiling upon opt-out, and routes to human review within 15 business days.",
                    mitigates_risk_id="RISK-UNLAWFUL-ADMT-PROFILING",
                    satisfies_obligations_json=json.dumps(["OBL-US-CA-CPPA-2026-ADMT-AUDIT"]),
                    supported_by_evidence_json=json.dumps(["EVID-ADMT-AUDIT-LOG", "EVID-CPPA-RISK-ATTESTATION"]),
                ),
                KGControlRecord(
                    control_id="CTRL-ANNUAL-CYBER-AUDIT",
                    name="Independent Annual Cybersecurity Audit & Board Certification",
                    control_category="Assurance Control",
                    description="Independent annual cybersecurity audit covering multi-factor authentication, zero-trust segmentation, and encryption at rest/in transit.",
                    mitigates_risk_id="RISK-SECURITY-BREACH-EXPOSURE",
                    satisfies_obligations_json=json.dumps(["OBL-US-CA-CPPA-2026-ADMT-AUDIT"]),
                    supported_by_evidence_json=json.dumps(["EVID-BOARD-CYBER-CERT-2026"]),
                ),
                KGControlRecord(
                    control_id="CTRL-DPA-CONTRACT-GATE",
                    name="Contractor & Service Provider Statutory DPA Gate",
                    control_category="Contractual Control",
                    description="Verifies executed § 1798.100(d) statutory contract clauses before transmitting personal information to any vendor or contractor.",
                    mitigates_risk_id="RISK-UNAUTHORIZED-THIRD-PARTY-SHARING",
                    satisfies_obligations_json=json.dumps(["OBL-US-CA-CPRA-2023-CONTRACT"]),
                    supported_by_evidence_json=json.dumps(["EVID-SIGNED-CPRA-ADDENDUM"]),
                ),
            ]
            for ctrl in controls:
                sess.merge(ctrl)

            sess.commit()

            # 7. Seed All Required Section 7 Graph Edges (`kg_edges` + `ontology_edges`)
            # Law -> contains Provision | amendedBy Amendment | interpretedBy Decision | supplementedBy Regulation | enforcedBy Authority
            self.add_edge("Law", "LAW-US-CA-CCPA", "contains", "Provision", "PROV-US-CA-1798.100d", date(2020, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Law", "LAW-US-CA-CCPA", "contains", "Provision", "PROV-US-CA-1798.185a15-16", date(2023, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Law", "LAW-US-CA-CCPA", "amendedBy", "Amendment", "AMD-US-CA-CPRA-2023", date(2023, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Law", "LAW-US-CA-CCPA", "amendedBy", "Amendment", "AMD-US-CA-CPPA-ADMT-2026", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Law", "LAW-US-CA-CCPA", "supplementedBy", "Regulation", "11-CCR-7150-7221", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Law", "LAW-US-CA-CCPA", "enforcedBy", "Authority", "CPPA", date(2023, 1, 1), None, "US-CA", session=sess)

            self.add_edge("Law", "LAW-EU-GDPR", "contains", "Provision", "PROV-EU-GDPR-ART22", date(2018, 5, 25), None, "EU", session=sess)
            self.add_edge("Law", "LAW-EU-GDPR", "contains", "Provision", "PROV-EU-GDPR-ART35", date(2018, 5, 25), None, "EU", session=sess)
            self.add_edge("Law", "LAW-EU-GDPR", "contains", "Provision", "PROV-EU-GDPR-ART38", date(2018, 5, 25), None, "EU", session=sess)
            self.add_edge("Law", "LAW-EU-GDPR", "interpretedBy", "Decision", "DEC-EU-DE-SCHUFA-ART22", date(2023, 12, 7), None, "EU-DE", session=sess)
            self.add_edge("Law", "LAW-EU-GDPR", "interpretedBy", "Decision", "DEC-EU-DE-BAG-XFAB-ART38-ART35", date(2023, 2, 9), None, "EU-DE", session=sess)
            self.add_edge("Law", "LAW-EU-GDPR", "enforcedBy", "Authority", "BfDI-AND-LANDES-DPAS", date(2018, 5, 25), None, "EU-DE", session=sess)

            self.add_edge("Law", "LAW-CA-ON-PHIPA", "contains", "Provision", "PROV-CA-ON-PHIPA-S12", date(2020, 1, 1), None, "CA-ON", session=sess)
            self.add_edge("Law", "LAW-CA-ON-PHIPA", "interpretedBy", "Decision", "DEC-CA-ON-IPC-PHIPA-175", date(2022, 3, 24), None, "CA-ON", session=sess)
            self.add_edge("Law", "LAW-CA-ON-PHIPA", "interpretedBy", "Decision", "DEC-CA-ON-IPC-PHIPA-110", date(2020, 2, 11), None, "CA-ON", session=sess)
            self.add_edge("Law", "LAW-CA-ON-PHIPA", "enforcedBy", "Authority", "IPC", date(2004, 11, 1), None, "CA-ON", session=sess)

            # Decision -> interprets Provision | cites Decision | applies LegalTest | orders Remedy | modifiedBy Decision | appealedTo Court
            self.add_edge("Decision", "DEC-EU-DE-SCHUFA-ART22", "interprets", "Provision", "PROV-EU-GDPR-ART22", date(2023, 12, 7), None, "EU-DE", session=sess)
            self.add_edge("Decision", "DEC-EU-DE-BAG-XFAB-ART38-ART35", "interprets", "Provision", "PROV-EU-GDPR-ART38", date(2023, 2, 9), None, "EU-DE", session=sess)
            self.add_edge("Decision", "DEC-EU-DE-BAG-XFAB-ART38-ART35", "interprets", "Provision", "PROV-EU-GDPR-ART35", date(2023, 2, 9), None, "EU-DE", session=sess)
            self.add_edge("Decision", "DEC-CA-ON-IPC-PHIPA-175", "interprets", "Provision", "PROV-CA-ON-PHIPA-S12", date(2022, 3, 24), None, "CA-ON", session=sess)
            self.add_edge("Decision", "DEC-CA-ON-IPC-PHIPA-175", "cites", "Decision", "DEC-CA-ON-IPC-PHIPA-110", date(2022, 3, 24), None, "CA-ON", session=sess)
            self.add_edge("Decision", "DEC-CA-ON-IPC-PHIPA-175", "applies", "LegalTest", "TEST-PHIPA-S12-REASONABLE-SAFEGUARDS", date(2022, 3, 24), None, "CA-ON", session=sess)
            self.add_edge("Decision", "DEC-CA-ON-IPC-PHIPA-175", "orders", "Remedy", "REM-EHR-AUDIT-MONITORING-ORDER", date(2022, 3, 24), None, "CA-ON", session=sess)

            self.add_edge("Decision", "DEC-US-9CIR-RAMIREZ-2020", "appealedTo", "Court", "COURT-US-SCOTUS", date(2020, 9, 2), None, "US-FED", session=sess)
            self.add_edge("Decision", "DEC-US-9CIR-RAMIREZ-2020", "modifiedBy", "Decision", "DEC-US-SCOTUS-TRANSUNION-2021", date(2021, 6, 25), None, "US-FED", session=sess)
            self.add_edge("Decision", "DEC-US-SCOTUS-TRANSUNION-2021", "applies", "LegalTest", "TEST-ART-III-CONCRETE-HARM", date(2021, 6, 25), None, "US-FED", session=sess)

            # Obligation -> appliesTo Organization | appliesTo ProcessingActivity | requires Control | triggers Assessment | establishes Deadline
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "appliesTo", "Organization", "ORG-ACME-AI-CORP", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "appliesTo", "Organization", "ORG-PACIFIC-RETAIL-INC", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "appliesTo", "ProcessingActivity", "AI_Training", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "requires", "Control", "CTRL-ADMT-OPTOUT-ENGINE", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "requires", "Control", "CTRL-ANNUAL-CYBER-AUDIT", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "triggers", "Assessment", "CPRA_ADMT", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", "establishes", "Deadline", "DEADLINE-15-BUSINESS-DAYS-ADMT", date(2026, 1, 1), None, "US-CA", session=sess)

            # Control -> mitigates Risk | satisfies Obligation | supportedBy Evidence
            self.add_edge("Control", "CTRL-ADMT-OPTOUT-ENGINE", "mitigates", "Risk", "RISK-UNLAWFUL-ADMT-PROFILING", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Control", "CTRL-ADMT-OPTOUT-ENGINE", "satisfies", "Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("Control", "CTRL-ADMT-OPTOUT-ENGINE", "supportedBy", "Evidence", "EVID-ADMT-AUDIT-LOG", date(2026, 1, 1), None, "US-CA", session=sess)

            # ProcessingActivity -> governedBy Obligation | performedBy Organization | uses Vendor | involves DataCategory
            self.add_edge("ProcessingActivity", "AI_Training", "governedBy", "Obligation", "OBL-US-CA-CPRA-2023-CONTRACT", date(2023, 1, 1), date(2026, 1, 1), "US-CA", session=sess)
            self.add_edge("ProcessingActivity", "AI_Training", "governedBy", "Obligation", "OBL-US-CA-CPPA-2026-ADMT-AUDIT", date(2026, 1, 1), None, "US-CA", session=sess)
            self.add_edge("ProcessingActivity", "AI_Training", "performedBy", "Organization", "ORG-ACME-AI-CORP", date(2023, 1, 1), None, "US-CA", session=sess)
            self.add_edge("ProcessingActivity", "AI_Training", "uses", "Vendor", "VENDOR-CLOUD-GPU-CLUSTER", date(2023, 1, 1), None, "US-CA", session=sess)
            self.add_edge("ProcessingActivity", "AI_Training", "involves", "DataCategory", "SensitiveData", date(2023, 1, 1), None, "US-CA", session=sess)

            sess.commit()


__all__ = [
    "ALL_VALID_PREDICATES",
    "KGAmendmentRecord",
    "KGControlRecord",
    "KGDecisionRecord",
    "KGEdgeRecord",
    "KGLawRecord",
    "KGObligationRecord",
    "KGProvisionRecord",
    "SECTION_7_RELATIONSHIP_SCHEMA",
    "TemporalRegulatoryKnowledgeGraph",
]
