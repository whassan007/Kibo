import os
import re
import sqlite3
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")
SOURCES_MD = os.path.join(os.path.dirname(__file__), "src", "assets", "Sources.md")

def sanitize_id(title):
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    clean = re.sub(r'\s+', '_', clean.strip())
    return f"H1_{clean.upper()}"[:40]

def parse_sources_md():
    if not os.path.exists(SOURCES_MD):
        print(f"Sources file not found at {SOURCES_MD}")
        return []

    with open(SOURCES_MD, "r", encoding="utf-8") as f:
        lines = f.readlines()

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
            
            sources.append({
                "title": title.strip(),
                "url": url,
                "jurisdiction": current_jurisdiction
            })

    return sources

def sync_sources_to_db(parsed_sources):
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

    for src in parsed_sources:
        title = src["title"]
        url = src["url"]
        jurisdiction = src["jurisdiction"]

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
            props["last_verified"] = "2026-07-04"
            
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
                "last_verified": "2026-07-04"
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
