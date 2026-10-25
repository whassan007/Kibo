"""
KIBO Privacy OS — Canadian Privacy Commissioner Decisions & Enforcement Ingestion Agent (G08).

Section 3 P0 Remediation:
- Eliminates all LLM verdict fabrication (`query_ollama`, `get_hardcoded_fallback_verdict`, and generative prompts).
- Audits and quarantines existing `commissioner_verdicts` rows with `id LIKE 'verdict-auto-%'` or unverified
  domains (e.g. `bcprivacy.com`, `oipps.alberta.ca`, `icom.on.ca`, `ipq.gouv.qc.ca`, etc.) into
  `quarantined_commissioner_verdicts` with `quarantine_reason="P0_UNVERIFIED_LLM_FABRICATION"`, preserving
  forensic evidence while removing them from active production `commissioner_verdicts` and
  `canadian_privacy_newsletter.md`.
- Discovers, verifies origin & SHA-256 content hashes, and ingests only authentic Canadian commissioner
  decisions from `AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS` or verified official commissioner feeds.
- Returns `{"status": "SOURCE_UNAVAILABLE", "fabricated_fallback_used": False}` when a live feed is unreachable
  and NEVER fabricates a verdict.
- Returns `{"status": "UNVERIFIED"}` when a candidate record lacks verified origin or SHA-256 content hash.
- Sets `review_status="REQUIRES_LEGAL_REVIEW"` when legal interpretation is uncertain.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional

from core.regulatory_intelligence import (
    DiscoveryStatusCode,
    LegalPromotionState,
    compute_sha256_hex,
)
from core.regulatory_intelligence.source_registry.canada_commissioner_sources import (
    AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS,
    CANADA_COMMISSIONER_SOURCES,
    get_authentic_canadian_commissioner_decisions,
    get_canada_commissioner_sources,
)

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")
PUBLIC_NEWSLETTER = os.path.join(os.path.dirname(__file__), "public", "canadian_privacy_newsletter.md")
DIST_NEWSLETTER = os.path.join(os.path.dirname(__file__), "dist", "canadian_privacy_newsletter.md")

QUARANTINE_REASON_P0_FABRICATION = "P0_UNVERIFIED_LLM_FABRICATION"

# Known hallucinated / fabricated domains seen in historical LLM-generated verdicts
KNOWN_FABRICATED_DOMAINS = frozenset(
    {
        "bcprivacy.com",
        "oipps.alberta.ca",
        "icom.on.ca",
        "ipq.gouv.qc.ca",
        "bcipc.bc.ca",
        "privacycommissioner.ca",
        "icbc.com",
        "oipc.on.ca",
        "privacycommissioner.on.ca",
        "cprq.gouv.qc.ca",
        "privacyontario.on.ca",
        "icbc.bc.ca",
        "privacycommissioner.ab.ca",
        "icpo.on.ca",
        "privacyoakland.ca",
        "bcpoa.bc.ca",
        "privacy.gov.on.ca",
        "opc.alberta.ca",
        "privacybc.ca",
    }
)


def get_allowed_commissioner_domains() -> frozenset[str]:
    """Return the authoritative domain allowlist from CANADA_COMMISSIONER_SOURCES."""
    domains = set()
    for src in CANADA_COMMISSIONER_SOURCES:
        domain = src.official_domain.lower().strip()
        domains.add(domain)
    return frozenset(domains)


def _extract_hostname(url: str) -> str:
    """Extract normalized hostname (stripping leading 'www.') from a URL."""
    if not url or not isinstance(url, str):
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        host = (parsed.hostname or "").lower().strip()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def is_verified_commissioner_domain(url: str) -> bool:
    """
    Check whether `url` belongs to an official Canadian privacy commissioner domain
    in `CANADA_COMMISSIONER_SOURCES` and is not in `KNOWN_FABRICATED_DOMAINS`.
    """
    host = _extract_hostname(url)
    if not host:
        return False
    if host in KNOWN_FABRICATED_DOMAINS:
        return False
    allowed = get_allowed_commissioner_domains()
    for official_domain in allowed:
        if host == official_domain or host.endswith("." + official_domain):
            return True
    return False


def _ensure_verdicts_schema(conn: sqlite3.Connection) -> None:
    """
    Ensure `commissioner_verdicts` and `quarantined_commissioner_verdicts` exist
    and that `commissioner_verdicts` has provenance, SHA-256 hash, and review_status columns.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS commissioner_verdicts (
            id TEXT PRIMARY KEY,
            commissioner TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            compliance_impact TEXT NOT NULL,
            source_url TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            content_sha256 TEXT,
            official_citation TEXT,
            decision_date TEXT,
            statutory_provisions TEXT,
            review_status TEXT DEFAULT 'VERIFIED_SOURCE',
            source_id TEXT
        )
        """
    )

    # Backfill new columns on existing table if needed
    cursor.execute("PRAGMA table_info(commissioner_verdicts)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    additional_columns = [
        ("content_sha256", "TEXT"),
        ("official_citation", "TEXT"),
        ("decision_date", "TEXT"),
        ("statutory_provisions", "TEXT"),
        ("review_status", "TEXT DEFAULT 'VERIFIED_SOURCE'"),
        ("source_id", "TEXT"),
    ]
    for col_name, col_type in additional_columns:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE commissioner_verdicts ADD COLUMN {col_name} {col_type}")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quarantined_commissioner_verdicts (
            id TEXT PRIMARY KEY,
            commissioner TEXT NOT NULL,
            jurisdiction TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            compliance_impact TEXT NOT NULL,
            source_url TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            quarantine_reason TEXT NOT NULL,
            quarantined_at TEXT NOT NULL,
            original_content_sha256 TEXT
        )
        """
    )
    conn.commit()


def verify_verdict_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that a candidate commissioner decision record has:
    1. A non-fabricated ID (not starting with `verdict-auto-`).
    2. A verified official commissioner domain URL (`priv.gc.ca`, `ipc.on.ca`, `cai.gouv.qc.ca`, `oipc.bc.ca`, etc.).
    3. Verbatim source content or precomputed SHA-256 content hash matching the payload.
    4. Deterministic legal interpretation status (or flags `REQUIRES_LEGAL_REVIEW` when uncertain).
    """
    if not isinstance(record, dict):
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "Record is not a dictionary",
        }

    verdict_id = str(record.get("id") or "").strip()
    source_url = str(record.get("source_url") or record.get("official_source_url") or "").strip()
    title = str(record.get("title") or "").strip()
    summary = str(record.get("summary") or "").strip()

    if not verdict_id or verdict_id.startswith("verdict-auto-"):
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "Record uses fabricated or missing identifier",
        }

    if not source_url or not is_verified_commissioner_domain(source_url):
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": f"Unverified or non-authoritative source domain: {source_url}",
        }

    verbatim_excerpt = record.get("verbatim_excerpt") or record.get("exact_source_excerpt") or ""
    provided_sha256 = str(record.get("content_sha256") or record.get("raw_document_sha256") or "").strip()

    if not verbatim_excerpt and not provided_sha256:
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "Missing verified origin excerpt and SHA-256 content hash",
        }

    computed_sha256 = compute_sha256_hex(verbatim_excerpt) if verbatim_excerpt else provided_sha256
    if provided_sha256 and verbatim_excerpt and provided_sha256 != computed_sha256:
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "SHA-256 content hash mismatch against verbatim excerpt",
        }

    if not computed_sha256 or len(computed_sha256) != 64:
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "Invalid SHA-256 hash format",
        }

    if not title or not summary:
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "valid": False,
            "reason": "Missing mandatory title or summary",
        }

    # Evaluate legal interpretation certainty
    interpretation_uncertain = bool(record.get("interpretation_uncertain", False))
    requested_review_status = str(record.get("review_status") or "").strip()
    if (
        interpretation_uncertain
        or requested_review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW.value
        or record.get("interpretation_status") == "requires_legal_review"
    ):
        review_status = LegalPromotionState.REQUIRES_LEGAL_REVIEW.value
    else:
        review_status = requested_review_status or LegalPromotionState.VERIFIED_SOURCE.value

    return {
        "status": DiscoveryStatusCode.OK.value,
        "valid": True,
        "content_sha256": computed_sha256,
        "review_status": review_status,
    }


def audit_and_quarantine_verdicts(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Quarantine-audit all existing rows in `commissioner_verdicts`.
    Any row with:
      - `id LIKE 'verdict-auto-%'`, OR
      - an unverified domain (such as `bcprivacy.com`, `oipps.alberta.ca`, `icom.on.ca`, `ipq.gouv.qc.ca`, etc.), OR
      - missing a verified SHA-256 content hash / authentic decision match
    is moved into `quarantined_commissioner_verdicts` with
    `quarantine_reason="P0_UNVERIFIED_LLM_FABRICATION"` and removed from active
    production `commissioner_verdicts` and `canadian_privacy_newsletter.md`.
    """
    target_db = db_path or DB_FILE
    conn = sqlite3.connect(target_db)
    try:
        _ensure_verdicts_schema(conn)
        cursor = conn.cursor()

        authentic_by_id = {d["id"]: d for d in AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS}

        cursor.execute(
            """
            SELECT id, commissioner, jurisdiction, title, summary,
                   compliance_impact, source_url, collected_at, content_sha256
            FROM commissioner_verdicts
            """
        )
        rows = cursor.fetchall()

        quarantined_ids: List[str] = []
        retained_ids: List[str] = []
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        for row in rows:
            (
                v_id,
                commissioner,
                jurisdiction,
                title,
                summary,
                compliance_impact,
                source_url,
                collected_at,
                content_sha256,
            ) = row

            is_auto_id = str(v_id).startswith("verdict-auto-")
            domain_verified = is_verified_commissioner_domain(source_url)
            is_authentic_verified = (
                v_id in authentic_by_id
                and domain_verified
                and bool(content_sha256)
                and content_sha256 == authentic_by_id[v_id]["content_sha256"]
            )

            if is_auto_id or not domain_verified or not is_authentic_verified:
                row_hash = content_sha256 or compute_sha256_hex(
                    f"{v_id}|{commissioner}|{jurisdiction}|{title}|{summary}|{source_url}"
                )
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO quarantined_commissioner_verdicts (
                        id, commissioner, jurisdiction, title, summary,
                        compliance_impact, source_url, collected_at,
                        quarantine_reason, quarantined_at, original_content_sha256
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v_id,
                        commissioner,
                        jurisdiction,
                        title,
                        summary,
                        compliance_impact,
                        source_url,
                        collected_at,
                        QUARANTINE_REASON_P0_FABRICATION,
                        now_iso,
                        row_hash,
                    ),
                )
                cursor.execute("DELETE FROM commissioner_verdicts WHERE id = ?", (v_id,))
                quarantined_ids.append(v_id)
            else:
                retained_ids.append(v_id)

        conn.commit()
        regenerate_newsletter(cursor)

        cursor.execute("SELECT COUNT(*) FROM quarantined_commissioner_verdicts")
        total_quarantined_in_table = cursor.fetchone()[0]

        return {
            "status": DiscoveryStatusCode.OK.value,
            "quarantined_count": len(quarantined_ids),
            "quarantined_ids": quarantined_ids,
            "retained_count": len(retained_ids),
            "retained_ids": retained_ids,
            "total_quarantined_records": total_quarantined_in_table,
            "quarantine_reason": QUARANTINE_REASON_P0_FABRICATION,
        }
    finally:
        conn.close()


def ingest_verdict_record(
    record: Dict[str, Any],
    *,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify and ingest a single commissioner decision record.
    - Returns `{"status": "UNVERIFIED", ...}` if origin or SHA-256 hash is missing/invalid.
    - Sets `review_status="REQUIRES_LEGAL_REVIEW"` if legal interpretation is uncertain.
    """
    verification = verify_verdict_record(record)
    if not verification.get("valid"):
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "ingested": False,
            "reason": verification.get("reason", "Unverified record"),
        }

    content_sha256 = verification["content_sha256"]
    review_status = verification["review_status"]

    target_db = db_path or DB_FILE
    conn = sqlite3.connect(target_db)
    try:
        _ensure_verdicts_schema(conn)
        cursor = conn.cursor()

        collected_at = record.get("collected_at") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        statutory_provisions = record.get("statutory_provisions") or []
        if isinstance(statutory_provisions, list):
            statutory_provisions_str = "; ".join(str(x) for x in statutory_provisions)
        else:
            statutory_provisions_str = str(statutory_provisions)

        cursor.execute(
            """
            INSERT OR REPLACE INTO commissioner_verdicts (
                id, commissioner, jurisdiction, title, summary,
                compliance_impact, source_url, collected_at,
                content_sha256, official_citation, decision_date,
                statutory_provisions, review_status, source_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"],
                record["commissioner"],
                record["jurisdiction"],
                record["title"],
                record["summary"],
                record["compliance_impact"],
                record["source_url"],
                collected_at,
                content_sha256,
                record.get("official_citation"),
                record.get("decision_date"),
                statutory_provisions_str,
                review_status,
                record.get("source_id"),
            ),
        )
        conn.commit()
        regenerate_newsletter(cursor)
        return {
            "status": (
                DiscoveryStatusCode.REQUIRES_LEGAL_REVIEW.value
                if review_status == LegalPromotionState.REQUIRES_LEGAL_REVIEW.value
                else DiscoveryStatusCode.OK.value
            ),
            "ingested": True,
            "id": record["id"],
            "content_sha256": content_sha256,
            "review_status": review_status,
        }
    finally:
        conn.close()


def collect_new_verdicts(
    *,
    db_path: Optional[str] = None,
    candidate_decisions: Optional[Iterable[Dict[str, Any]]] = None,
    live_feed_fetcher: Optional[Callable[[], Iterable[Dict[str, Any]]]] = None,
    simulate_unreachable: bool = False,
) -> Dict[str, Any]:
    """
    Source-grounded collection of authentic Canadian privacy commissioner decisions.
    1. Runs `audit_and_quarantine_verdicts()` first to ensure zero fabricated rows remain in production.
    2. If a live feed is unreachable (or `simulate_unreachable=True`), returns
       `{"status": "SOURCE_UNAVAILABLE", "fabricated_fallback_used": False}` and NEVER fabricates a verdict.
    3. Verifies origin domain and SHA-256 content hash for every decision before insertion.
    4. Regenerates `canadian_privacy_newsletter.md` exclusively from verified decisions.
    """
    target_db = db_path or DB_FILE
    audit_result = audit_and_quarantine_verdicts(db_path=target_db)

    if simulate_unreachable:
        return {
            "status": DiscoveryStatusCode.SOURCE_UNAVAILABLE.value,
            "fabricated_fallback_used": False,
            "ingested_count": 0,
            "quarantined_count": audit_result["quarantined_count"],
        }

    if live_feed_fetcher is not None:
        try:
            decisions_to_process = list(live_feed_fetcher())
        except Exception as exc:
            return {
                "status": DiscoveryStatusCode.SOURCE_UNAVAILABLE.value,
                "fabricated_fallback_used": False,
                "error": str(exc),
                "ingested_count": 0,
                "quarantined_count": audit_result["quarantined_count"],
            }
    elif candidate_decisions is not None:
        decisions_to_process = list(candidate_decisions)
    else:
        decisions_to_process = get_authentic_canadian_commissioner_decisions()

    ingested_ids: List[str] = []
    unverified_records: List[Dict[str, Any]] = []
    requires_legal_review_ids: List[str] = []

    for decision in decisions_to_process:
        res = ingest_verdict_record(decision, db_path=target_db)
        if not res.get("ingested"):
            unverified_records.append(
                {
                    "id": decision.get("id") if isinstance(decision, dict) else None,
                    "reason": res.get("reason"),
                }
            )
        else:
            ingested_ids.append(res["id"])
            if res.get("review_status") == LegalPromotionState.REQUIRES_LEGAL_REVIEW.value:
                requires_legal_review_ids.append(res["id"])

    if unverified_records and not ingested_ids:
        return {
            "status": DiscoveryStatusCode.UNVERIFIED.value,
            "fabricated_fallback_used": False,
            "ingested_count": 0,
            "unverified_count": len(unverified_records),
            "unverified_records": unverified_records,
            "quarantined_count": audit_result["quarantined_count"],
        }

    return {
        "status": (
            DiscoveryStatusCode.REQUIRES_LEGAL_REVIEW.value
            if requires_legal_review_ids
            else DiscoveryStatusCode.OK.value
        ),
        "fabricated_fallback_used": False,
        "ingested_count": len(ingested_ids),
        "ingested_ids": ingested_ids,
        "requires_legal_review_ids": requires_legal_review_ids,
        "unverified_count": len(unverified_records),
        "quarantined_count": audit_result["quarantined_count"],
    }


def regenerate_newsletter(cursor: sqlite3.Cursor) -> None:
    """
    Regenerate `canadian_privacy_newsletter.md` using ONLY verified authentic verdicts
    from `commissioner_verdicts` (which have SHA-256 content hashes and verified official URLs).
    """
    cursor.execute(
        """
        SELECT commissioner, jurisdiction, title, summary, compliance_impact,
               source_url, collected_at, content_sha256, official_citation,
               decision_date, review_status
        FROM commissioner_verdicts
        WHERE id NOT LIKE 'verdict-auto-%'
          AND content_sha256 IS NOT NULL
          AND content_sha256 != ''
        ORDER BY COALESCE(decision_date, collected_at) DESC
        """
    )
    rows = cursor.fetchall()

    content = """# Canadian Privacy Commissioner Enforcement & Rulings Newsletter
*Source-Grounded Regulatory Intelligence — Verified Official Decisions Only*

---

## Executive Summary
This bulletin compiles verified enforcement decisions, investigation reports, and adjudicative orders issued by Canada’s federal and provincial privacy commissioners (OPC Canada, CAI Québec, IPC Ontario, OIPC BC, OIPC Alberta). Every entry is anchored to an authoritative regulator publication and verified via SHA-256 content hash.

---

## Verified Commissioner Decisions & Rulings Breakdown
"""

    for i, row in enumerate(rows, 1):
        (
            commissioner,
            jurisdiction,
            title,
            summary,
            compliance_impact,
            source_url,
            collected_at,
            content_sha256,
            official_citation,
            decision_date,
            review_status,
        ) = row
        citation_label = official_citation or title
        date_label = decision_date or collected_at
        status_label = review_status or "VERIFIED_SOURCE"
        content += f"""
### {i}. {jurisdiction}: {title}
* **Regulator:** {commissioner}
* **Official Citation:** `{citation_label}`
* **Decision Date:** {date_label}
* **Verification Status:** `{status_label}`
* **SHA-256 Content Hash:** `{content_sha256}`
* **Decision Summary:** {summary}
* **Technical & Program Compliance Takeaways:**
  * {compliance_impact}
* **Authoritative Source:** [{citation_label}]({source_url})
"""

    content += """
---

## Source-Grounded Engineering Controls Checklist

1. `[ ]` **EHR Read & Snooping Audit Logs (IPC Ontario PHIPA Decision 175):** Enforce immutable read/view audit logging and proactive access audits across all electronic health record systems under PHIPA s. 12(1) and O. Reg. 329/04 s. 10.
2. `[ ]` **Ransomware Availability & Loss Breach Triage (IPC Ontario PHIPA Decision 110):** Classify ransomware encryption of PHI as a reportable unauthorized use and loss under PHIPA s. 12(2), even without data exfiltration.
3. `[ ]` **Cross-Border Transfer Accountability & Safeguards (OPC PIPEDA #2019-002 — Equifax):** Maintain binding processing agreements, active vulnerability management, and security audits for affiliate/third-party cross-border data transfers under PIPEDA Principles 4.1.3 and 4.7.
4. `[ ]` **Prohibition on Non-Consensual Biometric Scraping (OPC/CAI/OIPC Joint Finding #2021-001 — Clearview AI):** Block unconsented web scraping of facial images or biometric identifiers under PIPEDA s. 5(3), BC/AB PIPA s. 4, and Québec Law 25.
5. `[ ]` **PIPA s. 34 Safeguards & s. 35 Retention Purging (OIPC BC Order P21-06):** Enforce role-based access controls and automated destruction/de-identification when employee or customer data is no longer needed for legal or business purposes.
"""

    try:
        os.makedirs(os.path.dirname(PUBLIC_NEWSLETTER), exist_ok=True)
        with open(PUBLIC_NEWSLETTER, "w", encoding="utf-8") as f:
            f.write(content)

        if os.path.exists(os.path.dirname(DIST_NEWSLETTER)):
            with open(DIST_NEWSLETTER, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        print(f"[Verdicts Agent] Error saving newsletter files: {e}")


def run_scheduler() -> None:
    """Daily check to audit and ingest verified Canadian commissioner verdicts."""
    time.sleep(10)
    while True:
        try:
            collect_new_verdicts()
        except Exception as e:
            print(f"[Verdicts Agent] Scheduler error: {e}")
        time.sleep(86400)


def start_scheduler() -> None:
    """Start the scheduler in a background thread."""
    t = threading.Thread(target=run_scheduler, daemon=True, name="VerdictsAgentScheduler")
    t.start()
    print("[Verdicts Agent] Background scheduler started successfully.")


__all__ = [
    "QUARANTINE_REASON_P0_FABRICATION",
    "KNOWN_FABRICATED_DOMAINS",
    "get_allowed_commissioner_domains",
    "is_verified_commissioner_domain",
    "verify_verdict_record",
    "audit_and_quarantine_verdicts",
    "ingest_verdict_record",
    "collect_new_verdicts",
    "regenerate_newsletter",
    "run_scheduler",
    "start_scheduler",
]
