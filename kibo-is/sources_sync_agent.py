import os
import re
import sqlite3
import json
from datetime import datetime, timezone

from core.security.source_security import RegulatorySourceSecurityGuard

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")
SOURCES_MD = os.path.join(os.path.dirname(__file__), "src", "assets", "Sources.md")

def sanitize_id(title):
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    clean = re.sub(r'\s+', '_', clean.strip())
    return f"H1_{clean.upper()}"[:40]

def validate_and_sanitize_source_entry(title: str, url: str, jurisdiction: str, allowed_domains=None):
    """
    Validate synced URL against SSRF and sanitize title/jurisdiction against prompt injection
    using `RegulatorySourceSecurityGuard` before ingestion.
    """
    validated_url = RegulatorySourceSecurityGuard.validate_source_url(url, allowed_domains=allowed_domains)
    sanitized_title = RegulatorySourceSecurityGuard.sanitize_document_text(title)
    sanitized_jur = RegulatorySourceSecurityGuard.sanitize_document_text(jurisdiction)
    return {
        "title": sanitized_title["text"].strip(),
        "url": validated_url,
        "jurisdiction": sanitized_jur["text"].strip(),
        "security_flags": sanitized_title["security_flags"] + sanitized_jur["security_flags"],
    }

def parse_sources_md(validate_network: bool = False):
    if not os.path.exists(SOURCES_MD):
        print(f"Sources file not found at {SOURCES_MD}")
        return []

    with open(SOURCES_MD, "r", encoding="utf-8") as f:
        raw_content = f.read()

    sanitized_doc = RegulatorySourceSecurityGuard.sanitize_document_text(raw_content)
    lines = sanitized_doc["text"].splitlines()

    current_jurisdiction = "Global"
    sources = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        jur_match = re.match(r'^###\s*\*\*([^*]+)\*\*', line_str)
        if jur_match:
            current_jurisdiction = jur_match.group(1).strip()
            continue

        item_match = re.match(r'^\*\s*\*\*([^*]+)\*\*\s*:?\s*(https?://\S+)', line_str)
        if item_match:
            title = item_match.group(1).strip().rstrip(":")
            url_part = item_match.group(2).strip()
            url = url_part.split(" and ")[0].split(" ")[0].strip()

            if validate_network:
                try:
                    RegulatorySourceSecurityGuard.validate_source_url(url)
                except ValueError as exc:
                    print(f"[Security Guard] Skipping rejected source URL {url}: {exc}")
                    continue

            sources.append({
                "title": title.strip(),
                "url": url,
                "jurisdiction": current_jurisdiction
            })

    return sources

def sync_sources_to_db(parsed_sources, validate_urls: bool = True):
    if not os.path.exists(DB_FILE):
        print(f"Database not found at {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT instance_id, label, properties_json FROM ontology_instances WHERE class_id = 'LegalFramework' OR instance_id LIKE 'H1_%'")
    existing_rows = cursor.fetchall()
    
    existing_instances = []
    for inst_id, label, props_json in existing_rows:
        try:
            props = json.loads(props_json) if props_json else {}
        except Exception:
            props = {}
        existing_instances.append({
            "id": inst_id,
            "label": label,
            "props": props
        })

    updates_count = 0
    inserts_count = 0
    verified_date = datetime.now(timezone.utc).date().isoformat()

    for src in parsed_sources:
        raw_title = src["title"]
        raw_url = src["url"]
        raw_jurisdiction = src["jurisdiction"]

        if validate_urls:
            try:
                checked = validate_and_sanitize_source_entry(raw_title, raw_url, raw_jurisdiction)
                title = checked["title"]
                url = checked["url"]
                jurisdiction = checked["jurisdiction"]
                security_flags = checked["security_flags"]
            except ValueError as exc:
                print(f"[Security Guard] Blocked unsafe source URL '{raw_url}': {exc}")
                continue
        else:
            title = RegulatorySourceSecurityGuard.sanitize_document_text(raw_title)["text"]
            url = raw_url
            jurisdiction = RegulatorySourceSecurityGuard.sanitize_document_text(raw_jurisdiction)["text"]
            security_flags = []

        matched_inst = None
        title_lower = title.lower()
        
        for inst in existing_instances:
            inst_label_lower = inst["label"].lower()
            inst_id_lower = inst["id"].lower()
            
            if (inst_label_lower in title_lower or 
                title_lower in inst_label_lower or
                inst_id_lower.replace("h1_", "").replace("_", " ") in title_lower):
                matched_inst = inst
                break

        if matched_inst:
            inst_id = matched_inst["id"]
            props = matched_inst["props"]
            props["url"] = url
            props["jurisdiction"] = jurisdiction
            props["last_verified"] = verified_date
            props["security_flags"] = security_flags
            
            cursor.execute(
                "UPDATE ontology_instances SET properties_json = ? WHERE instance_id = ?",
                (json.dumps(props), inst_id)
            )
            updates_count += 1
        else:
            inst_id = sanitize_id(title)
            props = {
                "url": url,
                "jurisdiction": jurisdiction,
                "version": "Consolidated",
                "last_verified": verified_date,
                "security_flags": security_flags,
            }
            cursor.execute(
                "INSERT OR REPLACE INTO ontology_instances (instance_id, class_id, label, properties_json) VALUES (?, ?, ?, ?)",
                (inst_id, "LegalFramework", title, json.dumps(props))
            )
            inserts_count += 1

    conn.commit()
    conn.close()
    print(f"Synced sources: Updated {updates_count} existing nodes, Inserted {inserts_count} new nodes.")

if __name__ == "__main__":
    sources = parse_sources_md()
    print(f"Parsed {len(sources)} sources from Sources.md.")
    sync_sources_to_db(sources)
