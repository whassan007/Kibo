"""
KIBO Privacy OS — Continuous Regulatory Intelligence FastAPI Router (Worker G22)

Exposes `/api/v1/regulatory-intelligence` endpoints:
- `GET /sources`: list and filter official regulatory sources (`country`, `jurisdiction_code`, `source_kind`, `language`) from `get_all_curated_sources()`.
- `GET /sources/summary`: summary counts of sources, jurisdictions, and domains.
- `POST /discover`: trigger a discovery run via `ScheduledDiscoveryEngine` or `OfficialRegulatoryConnector` (enforcing `RegulatorySourceSecurityGuard`).
- `GET /documents`: list verified canonical documents from `CitationVerificationService`.
- `GET /annotations/statutes`: return statutory annotations from `StatutoryProvisionAnnotator`.
- `GET /annotations/decisions`: return judicial & enforcement annotations from `JudicialAndEnforcementAnnotator` (with filters for `jurisdiction_code`, `authority_name`, `precedential_status`, `include_overturned`).
- `POST /citations/verify`: verify a citation and quote via `CitationVerificationService.verify_citation(...)` (`RD-06`, `RD-10`).
- `GET /versioning/diffs`: list or compute provision diffs via `StructuralVersionDiffEngine` (`RD-03`, `RD-04`).
- `GET /knowledge-graph/query`: execute temporal & relational KG queries (`query_type`: `law_as_of`, `sector_decisions`, `provision_decisions`, `effective_in_year`, `amendment_impact`, `overturned_decisions`) via `TemporalRegulatoryKnowledgeGraph` (`RD-12`).
- `GET /monitoring/metrics`: return the comprehensive Section 14 metrics payload from `RegulatoryIntelligenceMonitor`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    CitationVerificationResult,
    DecisionVerdictAnnotation,
    DiscoveryStatusCode,
    DocumentClassType,
    LegalPassageAnnotation,
    LegalPromotionState,
    ProvisionDiffRecord,
    RegulatorySourceEntry,
    SourceHealthStatus,
)
from core.regulatory_intelligence.annotations import (
    JudicialAndEnforcementAnnotator,
    StatutoryProvisionAnnotator,
)
from core.regulatory_intelligence.citations.verifier import (
    CitationVerificationService,
    build_default_canonical_corpus,
)
from core.regulatory_intelligence.connectors import (
    GLOBAL_CONNECTOR,
    GLOBAL_DOCUMENT_STORE,
    ImmutableDocumentStore,
    OfficialRegulatoryConnector,
)
from core.regulatory_intelligence.discovery import ScheduledDiscoveryEngine
from core.regulatory_intelligence.discovery.scheduler import (
    DiscoveryDocument,
    DiscoveryStore,
)
from core.regulatory_intelligence.legal_relations import TemporalRegulatoryKnowledgeGraph
from core.regulatory_intelligence.monitoring import RegulatoryIntelligenceMonitor
from core.regulatory_intelligence.source_registry import (
    get_all_curated_sources,
    get_allowed_official_domains,
)
from core.regulatory_intelligence.verification import AuthoritativePromotionGuard
from core.regulatory_intelligence.versioning import StructuralVersionDiffEngine
from core.security.auth import (
    PrincipalContext,
    get_current_user_optional,
    require_authenticated_user,
)
from core.security.source_security import RegulatorySourceSecurityGuard


# ---------------------------------------------------------------------------
# Singleton Service Instances
# ---------------------------------------------------------------------------
_CORPUS: Dict[str, CanonicalLegalDocument] = build_default_canonical_corpus()
_VERIFIER = CitationVerificationService(
    document_store=GLOBAL_DOCUMENT_STORE,
    canonical_corpus=_CORPUS,
)
_PROMOTION_GUARD = AuthoritativePromotionGuard(citation_verifier=_VERIFIER)
_STATUTE_ANNOTATOR = StatutoryProvisionAnnotator()
_DECISION_ANNOTATOR = JudicialAndEnforcementAnnotator()
_DIFF_ENGINE = StructuralVersionDiffEngine()
_KNOWLEDGE_GRAPH = TemporalRegulatoryKnowledgeGraph()
_MONITOR = RegulatoryIntelligenceMonitor(
    citation_verifier=_VERIFIER,
    statute_annotator=_STATUTE_ANNOTATOR,
    decision_annotator=_DECISION_ANNOTATOR,
    diff_engine=_DIFF_ENGINE,
    knowledge_graph=_KNOWLEDGE_GRAPH,
)
_DISCOVERY_ENGINE_DB = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_DISCOVERY_STORE = DiscoveryStore(_DISCOVERY_ENGINE_DB)
_DISCOVERY_ENGINE = ScheduledDiscoveryEngine(_DISCOVERY_STORE)


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------
class DiscoveryTriggerRequest(BaseModel):
    source_id: Optional[str] = Field(
        default=None,
        description="Curated source_id (e.g., SRC-US-FED-ECFR, SRC-CA-FED-JUSTICE-LAWS, SRC-EU-EURLEX)",
    )
    jurisdiction_code: Optional[str] = Field(default=None, description="Optional jurisdiction filter")
    official_url: Optional[str] = Field(default=None, description="Optional override URL (must pass SSRF & domain allowlist)")
    document_id: Optional[str] = Field(default=None, description="Document identifier for direct ingestion")
    canonical_title: Optional[str] = Field(default=None, description="Canonical title for direct ingestion")
    document_type: str = Field(default="statute", description="DocumentClassType value")
    raw_content_override: Optional[str] = Field(
        default=None,
        description="Optional raw content for deterministic test ingestion (sanitized via RegulatorySourceSecurityGuard)",
    )
    simulate_outage: bool = Field(default=False, description="Simulate network outage (RD-11)")
    cadence: str = Field(default="federal_and_eu_feeds", description="Scheduler cadence name")
    force: bool = Field(default=True, description="Force immediate discovery run")
    language: str = Field(default="en", description="ISO 639-1 language code")


class CitationVerifyRequest(BaseModel):
    citation_query: str = Field(..., description="Official citation, neutral citation, ELI/CELEX, or document_id")
    claimed_excerpt: str = Field(..., description="Claimed verbatim statutory or judicial passage")
    document_id: Optional[str] = Field(default=None, description="Optional explicit document_id")
    claimed_section: Optional[str] = Field(default=None, description="Claimed article or section reference")
    claimed_authority: Optional[str] = Field(default=None, description="Claimed issuing authority")
    claimed_version: Optional[str] = Field(default=None, description="Claimed document version")
    as_of_date: Optional[date] = Field(default=None, description="Optional point-in-time date check")
    check_promotion_guard: bool = Field(default=False, description="Also run AuthoritativePromotionGuard (RD-10)")


def _infer_country_from_jurisdiction(jurisdiction_id: str, parent_jurisdiction: Optional[str] = None) -> str:
    jur = (jurisdiction_id or "").strip().upper()
    parent = (parent_jurisdiction or "").strip().upper()
    if jur.startswith("US") or parent.startswith("US"):
        return "US"
    if jur.startswith("CA") or parent.startswith("CA"):
        return "CA"
    if jur.startswith("EU") or jur.startswith("DE-") or parent.startswith("EU"):
        return "EU"
    return jur.split("-")[0] if "-" in jur else jur


# ---------------------------------------------------------------------------
# FastAPI Router Definition
# ---------------------------------------------------------------------------
router = APIRouter(
    prefix="/api/v1/regulatory-intelligence",
    tags=["Regulatory Intelligence"],
)


@router.get("/sources")
def list_regulatory_sources(
    request: Request,
    country: Optional[str] = Query(default=None, description="Filter by country/macro-region (US, CA, EU)"),
    jurisdiction_code: Optional[str] = Query(default=None, description="Filter by jurisdiction_id (e.g. US-CA, CA-ON, EU-DE)"),
    source_kind: Optional[str] = Query(default=None, description="Filter by authority_type or legal_instrument_types"),
    language: Optional[str] = Query(default=None, description="Filter by ISO 639-1 language code (e.g. en, fr, de)"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    List and filter official curated regulatory sources from `get_all_curated_sources()`.
    """
    sources = get_all_curated_sources()

    if country:
        c_norm = country.strip().upper()
        sources = [
            s
            for s in sources
            if _infer_country_from_jurisdiction(s.jurisdiction_id, s.parent_jurisdiction) == c_norm
            or s.jurisdiction_id.upper().startswith(c_norm)
        ]

    if jurisdiction_code:
        j_norm = jurisdiction_code.strip().upper()
        sources = [
            s
            for s in sources
            if s.jurisdiction_id.upper() == j_norm
            or (s.parent_jurisdiction and s.parent_jurisdiction.upper() == j_norm)
        ]

    if source_kind:
        k_norm = source_kind.strip().lower()
        sources = [
            s
            for s in sources
            if k_norm in s.authority_type.lower()
            or any(k_norm in inst.lower() for inst in s.legal_instrument_types)
            or any(k_norm in cov.lower() for cov in s.publication_coverage)
        ]

    if language:
        l_norm = language.strip().lower()
        sources = [
            s
            for s in sources
            if any(lang.lower() == l_norm for lang in s.languages)
        ]

    return {
        "total": len(sources),
        "filters": {
            "country": country,
            "jurisdiction_code": jurisdiction_code,
            "source_kind": source_kind,
            "language": language,
        },
        "sources": [s.model_dump(mode="json") for s in sources],
    }


@router.get("/sources/summary")
def get_sources_summary(
    request: Request,
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Return summary counts of curated official regulatory sources, jurisdictions, authority types,
    languages, and allowed official domains.
    """
    sources = get_all_curated_sources()
    domains = get_allowed_official_domains()
    by_country: Dict[str, int] = {"US": 0, "CA": 0, "EU": 0}
    by_authority_type: Dict[str, int] = {}
    jurisdictions = set()
    languages = set()

    for s in sources:
        jurisdictions.add(s.jurisdiction_id)
        macro = _infer_country_from_jurisdiction(s.jurisdiction_id, s.parent_jurisdiction)
        by_country[macro] = by_country.get(macro, 0) + 1
        by_authority_type[s.authority_type] = by_authority_type.get(s.authority_type, 0) + 1
        for lang in s.languages:
            languages.add(lang.lower())

    return {
        "total_sources": len(sources),
        "total_jurisdictions": len(jurisdictions),
        "total_allowed_domains": len(domains),
        "sources_by_country": by_country,
        "sources_by_authority_type": by_authority_type,
        "supported_languages": sorted(languages),
        "allowed_domains_sample": domains[:50],
    }


@router.post("/discover")
def trigger_discovery_run(
    payload: DiscoveryTriggerRequest,
    request: Request,
    principal: PrincipalContext = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    """
    Trigger a regulatory discovery run via `OfficialRegulatoryConnector` and `ScheduledDiscoveryEngine`,
    strictly enforcing `RegulatorySourceSecurityGuard` (SSRF, domain allowlist, and prompt-injection sanitization).
    """
    sources = get_all_curated_sources()
    target_source: Optional[RegulatorySourceEntry] = None

    if payload.source_id:
        target_source = next((s for s in sources if s.source_id == payload.source_id), None)
        if target_source is None:
            raise HTTPException(status_code=404, detail=f"Regulatory source '{payload.source_id}' not found")
    elif payload.jurisdiction_code:
        j_norm = payload.jurisdiction_code.strip().upper()
        target_source = next((s for s in sources if s.jurisdiction_id.upper() == j_norm), None)
        if target_source is None:
            raise HTTPException(status_code=404, detail=f"No source found for jurisdiction '{payload.jurisdiction_code}'")
    else:
        target_source = sources[0]

    target_url = payload.official_url or target_source.discovery_endpoint
    allowed_domains = set(get_allowed_official_domains()) | {target_source.official_domain.lower()}

    # Validate URL via RegulatorySourceSecurityGuard before any network/connector activity
    try:
        RegulatorySourceSecurityGuard.validate_source_url(target_url, allowed_domains=allowed_domains)
    except ValueError as exc:
        return {
            "status": DiscoveryStatusCode.BLOCKED_SECURITY.value,
            "source_id": target_source.source_id,
            "target_url": target_url,
            "error": str(exc),
            "fabricated_fallback_used": False,
        }

    # Handle simulated outage (RD-11)
    if payload.simulate_outage:
        res = GLOBAL_CONNECTOR.fetch_and_ingest(
            target_source,
            document_id=payload.document_id or f"DOC-{target_source.source_id}",
            canonical_title=payload.canonical_title or f"{target_source.authority_name} Publication",
            official_url=target_url,
            simulate_outage=True,
            language=payload.language,
        )
        return res

    doc_id = payload.document_id or f"DOC-{target_source.source_id}-DISCOVERED"
    title = payload.canonical_title or f"{target_source.authority_name} Official Regulatory Instrument"
    raw_content = payload.raw_content_override or (
        f"Section 1. Official publication from {target_source.authority_name} ({target_source.jurisdiction_id}). "
        f"Regulated entities shall maintain verifiable compliance records."
    )

    try:
        doc_type = DocumentClassType(payload.document_type.lower())
    except ValueError:
        doc_type = DocumentClassType.STATUTE

    ingest_result = GLOBAL_CONNECTOR.fetch_and_ingest(
        target_source,
        document_id=doc_id,
        canonical_title=title,
        document_type=doc_type,
        official_url=target_url,
        raw_content_override=raw_content,
        simulate_outage=False,
        language=payload.language,
    )

    # Also record in ScheduledDiscoveryEngine transactional outbox
    class _StaticDiscoveryConnector:
        def fetch(self, *, cursor, timeout):
            return [
                DiscoveryDocument(
                    document_id=doc_id,
                    content=raw_content,
                    cursor=f"cursor-{doc_id}",
                    provenance={
                        "source_id": target_source.source_id,
                        "official_url": target_url,
                        "jurisdiction_id": target_source.jurisdiction_id,
                    },
                )
            ]

    cadence_key = payload.cadence if payload.cadence in _DISCOVERY_ENGINE.cadences else "federal_and_eu_feeds"
    sched_status = _DISCOVERY_ENGINE.run(
        target_source.source_id,
        cadence_key,
        _StaticDiscoveryConnector(),
        controlled=True,
        force=payload.force,
    )

    stored_doc = ingest_result.get("document")
    if isinstance(stored_doc, CanonicalLegalDocument):
        _VERIFIER.register_canonical_document(stored_doc)

    return {
        "status": ingest_result.get("status", DiscoveryStatusCode.OK.value),
        "scheduler_status": sched_status.value if hasattr(sched_status, "value") else str(sched_status),
        "source_id": target_source.source_id,
        "jurisdiction_id": target_source.jurisdiction_id,
        "security_flags": ingest_result.get("security_flags", []),
        "fabricated_fallback_used": False,
        "document": stored_doc.model_dump(mode="json") if isinstance(stored_doc, CanonicalLegalDocument) else stored_doc,
        "triggered_by": principal.user_id,
        "tenant_id": principal.tenant_id,
    }


@router.get("/documents")
def list_canonical_documents(
    request: Request,
    jurisdiction_code: Optional[str] = Query(default=None, description="Filter by jurisdiction_id"),
    document_type: Optional[str] = Query(default=None, description="Filter by DocumentClassType"),
    language: Optional[str] = Query(default=None, description="Filter by language"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    List verified canonical legal documents from `CitationVerificationService`.
    """
    docs = list(_VERIFIER._iter_all_known_documents())

    if jurisdiction_code:
        j_norm = jurisdiction_code.strip().upper()
        docs = [
            d
            for d in docs
            if d.jurisdiction_id.upper() == j_norm
            or any(p.upper() == j_norm for p in d.parent_jurisdictions)
        ]

    if document_type:
        dt_norm = document_type.strip().lower()
        docs = [d for d in docs if d.document_type.value.lower() == dt_norm]

    if language:
        l_norm = language.strip().lower()
        docs = [
            d
            for d in docs
            if d.language.lower() == l_norm or l_norm in {k.lower() for k in d.original_language_passages.keys()}
        ]

    return {
        "total": len(docs),
        "documents": [d.model_dump(mode="json") for d in docs],
    }


@router.get("/annotations/statutes")
def get_statutory_annotations(
    request: Request,
    jurisdiction_code: Optional[str] = Query(default=None, description="Filter by jurisdiction_id (e.g. US-FED, US-CA, CA-QC, EU-DE)"),
    document_id: Optional[str] = Query(default=None, description="Filter by canonical document_id"),
    language: Optional[str] = Query(default=None, description="Filter by source_language"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Return passage-grounded statutory & regulatory annotations from `StatutoryProvisionAnnotator`.
    """
    docs = list(_VERIFIER._iter_all_known_documents())
    statutory_types = {
        DocumentClassType.STATUTE,
        DocumentClassType.REGULATION,
        DocumentClassType.OFFICIAL_POLICY_DIRECTIVE,
        DocumentClassType.LEGISLATIVE_BILL,
    }
    docs = [d for d in docs if d.document_type in statutory_types]

    if jurisdiction_code:
        j_norm = jurisdiction_code.strip().upper()
        docs = [
            d
            for d in docs
            if d.jurisdiction_id.upper() == j_norm
            or any(p.upper() == j_norm for p in d.parent_jurisdictions)
        ]

    if document_id:
        docs = [d for d in docs if d.document_id == document_id]

    annotations: List[LegalPassageAnnotation] = []
    for doc in docs:
        doc_anns = _STATUTE_ANNOTATOR.annotate_document(doc)
        for ann in doc_anns:
            if language and ann.source_language.lower() != language.strip().lower():
                continue
            annotations.append(ann)

    return {
        "total": len(annotations),
        "annotations": [a.model_dump(mode="json") for a in annotations],
    }


@router.get("/annotations/decisions")
def get_decision_annotations(
    request: Request,
    jurisdiction_code: Optional[str] = Query(default=None, description="Filter by jurisdiction_id"),
    authority_name: Optional[str] = Query(default=None, description="Filter by court, tribunal, or regulator name"),
    precedential_status: Optional[str] = Query(default=None, description="Filter by binding_vs_persuasive_status"),
    include_overturned: bool = Query(default=True, description="Include reversed/overturned decisions"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Return judicial, tribunal, and regulatory enforcement annotations from `JudicialAndEnforcementAnnotator`.
    """
    docs = list(_VERIFIER._iter_all_known_documents())
    decision_types = {
        DocumentClassType.COURT_JUDGMENT,
        DocumentClassType.REGULATORY_ENFORCEMENT_DECISION,
        DocumentClassType.ADMINISTRATIVE_TRIBUNAL_RULING,
        DocumentClassType.CONSENT_ORDER_SETTLEMENT,
    }
    docs = [d for d in docs if d.document_type in decision_types]

    if jurisdiction_code:
        j_norm = jurisdiction_code.strip().upper()
        docs = [
            d
            for d in docs
            if d.jurisdiction_id.upper() == j_norm
            or any(p.upper() == j_norm for p in d.parent_jurisdictions)
        ]

    decisions: List[Dict[str, Any]] = []
    for doc in docs:
        is_overturned_doc = (
            doc.review_status == LegalPromotionState.SUPERSEDED
            or (doc.appeal_status or "").lower() in {"reversed", "overturned", "vacated"}
            or "reversed" in (doc.binding_status or "").lower()
            or "superseded" in (doc.binding_status or "").lower()
        )
        if not include_overturned and is_overturned_doc:
            continue

        verdict, passage_anns = _DECISION_ANNOTATOR.annotate_decision(doc)

        if authority_name:
            auth_q = authority_name.strip().lower()
            if auth_q not in verdict.court_tribunal_or_regulator.lower():
                continue

        if precedential_status:
            prec_q = precedential_status.strip().lower()
            if prec_q not in verdict.binding_vs_persuasive_status.lower():
                continue

        entry = verdict.model_dump(mode="json")
        entry["is_overturned_or_reversed"] = is_overturned_doc
        entry["passage_annotations_count"] = len(passage_anns)
        decisions.append(entry)

    return {
        "total": len(decisions),
        "decisions": decisions,
    }


@router.post("/citations/verify")
def verify_citation_endpoint(
    payload: CitationVerifyRequest,
    request: Request,
    principal: PrincipalContext = Depends(require_authenticated_user),
) -> Dict[str, Any]:
    """
    Verify a citation and verbatim excerpt across all 7 mandatory provenance dimensions
    via `CitationVerificationService.verify_citation(...)` (`RD-06`, `RD-10`).
    """
    target_doc = (
        _VERIFIER.get_canonical_document(payload.document_id)
        if payload.document_id
        else None
    )
    verification: CitationVerificationResult = _VERIFIER.verify_citation(
        citation_query=payload.citation_query,
        claimed_excerpt=payload.claimed_excerpt,
        document=target_doc,
        claimed_section=payload.claimed_section,
        claimed_authority=payload.claimed_authority,
        claimed_version=payload.claimed_version,
        as_of_date=payload.as_of_date,
    )

    response_data = verification.model_dump(mode="json")
    if payload.check_promotion_guard:
        promotion_report = _PROMOTION_GUARD.verify_candidate_record(
            {
                "citation_query": payload.citation_query,
                "claimed_excerpt": payload.claimed_excerpt,
                "document_id": payload.document_id or verification.document_id,
                "claimed_section": payload.claimed_section,
                "claimed_authority": payload.claimed_authority,
                "claimed_version": payload.claimed_version,
            },
            citation_result=verification,
            document=target_doc,
            as_of_date=payload.as_of_date,
        )
        response_data["promotion_guard"] = promotion_report.model_dump(mode="json")

    return response_data


@router.get("/versioning/diffs")
def get_versioning_diffs(
    request: Request,
    document_id: Optional[str] = Query(default=None, description="Filter or compute diff for document_id"),
    provision_ref: Optional[str] = Query(default=None, description="Filter or compute diff for provision_ref"),
    previous_version: Optional[str] = Query(default=None, description="Optional previous_version ID"),
    current_version: Optional[str] = Query(default=None, description="Optional current_version ID"),
    substantive_only: bool = Query(default=False, description="Only return substantive legal changes"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    List or compute structural provision diffs via `StructuralVersionDiffEngine` (`RD-03`, `RD-04`).
    """
    if document_id and provision_ref and previous_version and current_version:
        try:
            diff_rec = _DIFF_ENGINE.diff_registered_versions(
                document_id=document_id,
                provision_ref=provision_ref,
                previous_version=previous_version,
                current_version=current_version,
            )
            return {
                "total": 1,
                "diffs": [diff_rec.model_dump(mode="json")],
            }
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Materialize diffs across all registered multi-version provision histories
    computed_diffs: List[ProvisionDiffRecord] = []
    for (doc_id, prov_ref), history in _DIFF_ENGINE._provision_history.items():
        if document_id and doc_id != document_id:
            continue
        if provision_ref and prov_ref != provision_ref:
            continue
        if len(history) >= 2:
            for idx in range(len(history) - 1):
                prev_snap = history[idx]
                curr_snap = history[idx + 1]
                diff_rec = _DIFF_ENGINE.diff_registered_versions(
                    document_id=doc_id,
                    provision_ref=prov_ref,
                    previous_version=prev_snap.version_id,
                    current_version=curr_snap.version_id,
                )
                if substantive_only and not diff_rec.is_substantive:
                    continue
                computed_diffs.append(diff_rec)

    return {
        "total": len(computed_diffs),
        "diffs": [d.model_dump(mode="json") for d in computed_diffs],
    }


@router.get("/knowledge-graph/query")
def query_knowledge_graph(
    request: Request,
    query_type: str = Query(
        ...,
        description="One of: law_as_of, sector_decisions, provision_decisions, effective_in_year, amendment_impact, overturned_decisions",
    ),
    target_id: Optional[str] = Query(default=None, description="Law ID, processing activity, or amendment ID"),
    as_of_date: Optional[str] = Query(default=None, description="ISO date (YYYY-MM-DD) for law_as_of"),
    jurisdiction_code: Optional[str] = Query(default=None, description="Jurisdiction ID (e.g. CA-ON, EU-DE, US-CA)"),
    sector: Optional[str] = Query(default=None, description="Sector name (e.g. hospital, healthcare, banking)"),
    provision_ref: Optional[str] = Query(default=None, description="Provision reference (e.g. GDPR Art. 22, Art. 38)"),
    year: Optional[int] = Query(default=None, description="Year integer (e.g. 2023, 2026) for effective_in_year"),
    amendment_id: Optional[str] = Query(default=None, description="Amendment ID for amendment_impact"),
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Execute temporal and relational queries against `TemporalRegulatoryKnowledgeGraph` (`RD-12`):
    - `law_as_of`
    - `sector_decisions`
    - `provision_decisions`
    - `effective_in_year`
    - `amendment_impact`
    - `overturned_decisions`
    """
    qt = query_type.strip().lower()

    if qt == "law_as_of":
        law_or_act = target_id or "LAW-US-CA-CCPA"
        dt_str = as_of_date or "2026-01-01"
        res = _KNOWLEDGE_GRAPH.query_law_as_of(law_or_act, dt_str)
        return {"query_type": qt, "result": res}

    if qt == "sector_decisions":
        jur = jurisdiction_code or "CA-ON"
        sec = sector or "hospital"
        rows = _KNOWLEDGE_GRAPH.query_decisions_affecting_sector(jur, sec)
        return {"query_type": qt, "jurisdiction_code": jur, "sector": sec, "total": len(rows), "decisions": rows}

    if qt == "provision_decisions":
        jur = jurisdiction_code or "EU-DE"
        prov = provision_ref or "GDPR Art. 22"
        rows = _KNOWLEDGE_GRAPH.query_decisions_interpreting_provision(jur, prov)
        return {
            "query_type": qt,
            "jurisdiction_code": jur,
            "provision_ref": prov,
            "total": len(rows),
            "decisions": rows,
        }

    if qt == "effective_in_year":
        jur = jurisdiction_code or "US-CA"
        yr = year or 2026
        rows = _KNOWLEDGE_GRAPH.query_regulations_effective_in_year(jur, yr)
        return {
            "query_type": qt,
            "jurisdiction_code": jur,
            "year": yr,
            "total": len(rows),
            "regulations": rows,
        }

    if qt == "amendment_impact":
        amd_id = amendment_id or target_id or "AMD-US-CA-CPPA-ADMT-2026"
        rows = _KNOWLEDGE_GRAPH.query_organizations_affected_by_amendment(amd_id)
        return {
            "query_type": qt,
            "amendment_id": amd_id,
            "total": len(rows),
            "affected_organizations": rows,
        }

    if qt == "overturned_decisions":
        rows = _KNOWLEDGE_GRAPH.query_overturned_or_reversed_decisions()
        return {
            "query_type": qt,
            "total": len(rows),
            "decisions": rows,
        }

    raise HTTPException(
        status_code=400,
        detail=(
            f"Unsupported query_type '{query_type}'. Must be one of: "
            "law_as_of, sector_decisions, provision_decisions, effective_in_year, amendment_impact, overturned_decisions"
        ),
    )


@router.get("/monitoring/metrics")
def get_monitoring_metrics(
    request: Request,
    principal: Optional[PrincipalContext] = Depends(get_current_user_optional),
) -> Dict[str, Any]:
    """
    Return the comprehensive Section 14 Regulatory Intelligence Monitoring & Metrics payload
    from `RegulatoryIntelligenceMonitor`.
    """
    return _MONITOR.get_all_metrics()


def get_regulatory_intelligence_router() -> APIRouter:
    """Factory returning the Regulatory Intelligence FastAPI `APIRouter`."""
    return router


__all__ = [
    "router",
    "get_regulatory_intelligence_router",
]
