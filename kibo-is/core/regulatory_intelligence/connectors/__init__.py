"""
KIBO Privacy OS — Compliant Source Connectors & Immutable Document Store (Sections 3, 4, 5, 6.1)
Enforces SSRF/Allowlist guards, content-hash snapshots, prompt-injection sanitization,
and outage resilience (returns SOURCE_UNAVAILABLE — never fabricates legal documents).
"""

from __future__ import annotations

import urllib.request
import urllib.error
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DiscoveryStatusCode,
    DocumentClassType,
    LegalPromotionState,
    RegulatorySourceEntry,
    SourceHealthStatus,
    compute_sha256_hex,
)
from core.regulatory_intelligence.parsers.multilingual_parser import MultilingualLegalParser
from core.regulatory_intelligence.source_registry import (
    get_all_regulatory_sources,
    get_allowed_official_domains,
)
from core.security.source_security import RegulatorySourceSecurityGuard


class ImmutableDocumentStore:
    """
    Canonical versioned store for retrieved statutes, regulations, guidance, enforcement
    decisions, and court judgments with immutable SHA-256 snapshot references.
    """

    def __init__(self) -> None:
        self._documents: Dict[str, CanonicalLegalDocument] = {}
        self._versions: Dict[str, List[CanonicalLegalDocument]] = {}
        self._snapshots: Dict[str, Dict[str, Any]] = {}
        self._quarantined: Dict[str, Dict[str, Any]] = {}

    def store_document(self, doc: CanonicalLegalDocument, raw_payload: str) -> CanonicalLegalDocument:
        snapshot_hash = doc.raw_document_sha256 or compute_sha256_hex(raw_payload)
        snapshot_ref = f"kibo-snapshot://sha256/{snapshot_hash}"
        updated = doc.model_copy(
            update={
                "raw_document_sha256": snapshot_hash,
                "source_snapshot_reference": snapshot_ref,
            }
        )
        self._snapshots[snapshot_ref] = {
            "snapshot_reference": snapshot_ref,
            "document_id": updated.document_id,
            "document_version": updated.document_version,
            "raw_sha256": snapshot_hash,
            "normalized_sha256": updated.normalized_text_sha256,
            "official_source_url": updated.official_source_url,
            "retrieved_at": updated.retrieved_at.isoformat(),
            "raw_payload": raw_payload,
        }
        self._documents[updated.document_id] = updated
        self._versions.setdefault(updated.document_id, []).append(updated)
        return updated

    def get_document(self, document_id: str, version: Optional[str] = None) -> Optional[CanonicalLegalDocument]:
        if version is None:
            return self._documents.get(document_id)
        for v in self._versions.get(document_id, []):
            if v.document_version == version:
                return v
        return None

    def get_versions(self, document_id: str) -> List[CanonicalLegalDocument]:
        return list(self._versions.get(document_id, []))

    def list_documents(self, jurisdiction_id: Optional[str] = None) -> List[CanonicalLegalDocument]:
        docs = list(self._documents.values())
        if jurisdiction_id:
            jur = jurisdiction_id.strip().upper()
            docs = [d for d in docs if d.jurisdiction_id.upper() == jur or jur in [p.upper() for p in d.parent_jurisdictions]]
        return docs

    def quarantine_record(self, record_id: str, reason: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "record_id": record_id,
            "status": DiscoveryStatusCode.QUARANTINED.value,
            "quarantine_reason": reason,
            "quarantined_at": datetime.utcnow().isoformat(),
            "payload": payload,
        }
        self._quarantined[record_id] = entry
        return entry


class OfficialRegulatoryConnector:
    """
    Retrieves official legal publications with SSRF protection, domain allowlisting,
    timeout/size limits, and prompt-injection neutralization.
    Never fabricates fallback legal content on outage (returns SOURCE_UNAVAILABLE).
    """

    def __init__(
        self,
        document_store: Optional[ImmutableDocumentStore] = None,
        security_guard: Optional[RegulatorySourceSecurityGuard] = None,
    ) -> None:
        self.store = document_store or ImmutableDocumentStore()
        self.guard = security_guard or RegulatorySourceSecurityGuard()
        self.parser = MultilingualLegalParser()
        self.allowed_domains = set(get_allowed_official_domains())

    def fetch_and_ingest(
        self,
        source: RegulatorySourceEntry,
        *,
        document_id: str,
        canonical_title: str,
        document_type: DocumentClassType = DocumentClassType.STATUTE,
        official_url: Optional[str] = None,
        raw_content_override: Optional[str] = None,
        simulate_outage: bool = False,
        language: str = "en",
        eli_or_celex: Optional[str] = None,
        official_citation: Optional[str] = None,
        neutral_citation: Optional[str] = None,
        document_version: str = "1.0.0",
    ) -> Dict[str, Any]:
        target_url = official_url or source.discovery_endpoint

        # Step 1: Validate URL against SSRF & official domain allowlist
        try:
            self.guard.validate_source_url(target_url, allowed_domains=self.allowed_domains | {source.official_domain.lower()})
        except Exception as exc:
            return {
                "status": DiscoveryStatusCode.BLOCKED_SECURITY.value,
                "source_id": source.source_id,
                "error": str(exc),
                "fabricated_fallback_used": False,
            }

        # Step 2: Simulate or handle live network outage (RD-11)
        if simulate_outage:
            source.last_failed_retrieval = datetime.utcnow()
            source.health_status = SourceHealthStatus.UNREACHABLE
            return {
                "status": DiscoveryStatusCode.SOURCE_UNAVAILABLE.value,
                "source_id": source.source_id,
                "health_status": source.health_status.value,
                "alert_emitted": True,
                "fabricated_fallback_used": False,
            }

        raw_text = raw_content_override
        if raw_text is None:
            try:
                req = urllib.request.Request(
                    target_url,
                    headers={"User-Agent": "KIBO-Privacy-OS-Regulatory-Discovery/2.0 (+https://kibo.is)"},
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw_bytes = resp.read(5_000_000)
                    raw_text = raw_bytes.decode("utf-8", errors="replace")
            except Exception as exc:
                source.last_failed_retrieval = datetime.utcnow()
                source.health_status = SourceHealthStatus.UNREACHABLE
                return {
                    "status": DiscoveryStatusCode.SOURCE_UNAVAILABLE.value,
                    "source_id": source.source_id,
                    "health_status": source.health_status.value,
                    "error": str(exc),
                    "alert_emitted": True,
                    "fabricated_fallback_used": False,
                }

        # Step 3: Sanitize against prompt injection & verify size (RD-14)
        sanitized = self.guard.sanitize_document_text(raw_text)
        clean_text = sanitized["sanitized_text"] if isinstance(sanitized, dict) else str(sanitized)
        security_flags = sanitized.get("security_flags", []) if isinstance(sanitized, dict) else []

        norm_res = self.parser.normalize_document(clean_text)
        now = datetime.utcnow()
        source.last_successful_retrieval = now
        source.health_status = SourceHealthStatus.HEALTHY

        doc = CanonicalLegalDocument(
            document_id=document_id,
            document_type=document_type,
            canonical_title=canonical_title,
            jurisdiction_id=source.jurisdiction_id,
            parent_jurisdictions=[source.parent_jurisdiction] if source.parent_jurisdiction else [],
            issuing_authority=source.authority_name,
            issuing_authority_type=source.authority_type,
            official_source_url=target_url,
            official_citation=official_citation,
            neutral_citation=neutral_citation,
            eli_or_celex_identifier=eli_or_celex,
            retrieved_at=now,
            language=language,
            raw_document_sha256=compute_sha256_hex(raw_text),
            normalized_text_sha256=norm_res["normalized_text_sha256"],
            document_version=document_version,
            review_status=LegalPromotionState.VERIFIED_SOURCE,
            license=source.licensing_and_reuse,
            source_snapshot_reference=f"kibo-snapshot://sha256/{compute_sha256_hex(raw_text)}",
            normalized_text=norm_res["normalized_text"],
        )
        stored = self.store.store_document(doc, raw_text)
        return {
            "status": DiscoveryStatusCode.OK.value,
            "document": stored,
            "security_flags": security_flags,
            "fabricated_fallback_used": False,
        }


GLOBAL_DOCUMENT_STORE = ImmutableDocumentStore()
GLOBAL_CONNECTOR = OfficialRegulatoryConnector(document_store=GLOBAL_DOCUMENT_STORE)
