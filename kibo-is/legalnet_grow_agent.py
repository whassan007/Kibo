import sys
import os
import re
import sqlite3
import json
import subprocess

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")
DOT_FILE = os.path.join(os.path.dirname(__file__), "src", "LegalNet.md")

# Mapping node prefixes to ontology classes
PREFIX_TO_CLASS = {
    "In_Loc_": "Jurisdiction",
    "In_Data_": "DataCategory",
    "In_Act_": "ProcessingActivity",
    "In_Evt_": "ProcessingActivity",
    "H1_": "LegalFramework",
    "T_": "ComplianceObligation",  # Privacy Tort
    "H2_": "ComplianceObligation", # Cross-cutting control
    "Cert_": "AssessmentArtifact", # Certification
    "H3_": "ComplianceObligation", # Operational control
    "Pen_": "ComplianceObligation", # Penalty
    "Out_": "AssessmentArtifact"   # Output artifact
}

def determine_class(node_id):
    for prefix, cls in PREFIX_TO_CLASS.items():
        if node_id.startswith(prefix):
            return cls
    return "ComplianceObligation"

def parse_dot_file(filepath):
    nodes = []
    edges = []
    
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Match nodes: node_id [label="...", shape=...];
    node_pattern = re.compile(r'(\w+)\s*\[label="([^"]+)"(?:,\s*shape=\w+)?(?:,\s*style="[^"]+")?(?:,\s*fillcolor="[^"]+")?(?:,\s*color="[^"]+")?\];')
    for match in node_pattern.finditer(content):
        node_id, label = match.groups()
        # Clean label newlines
        label = label.replace('\\n', ' ').replace('\n', ' ')
        nodes.append({"id": node_id, "label": label, "class": determine_class(node_id)})
        
    # Match edges: source -> target;
    edge_pattern = re.compile(r'(\w+)\s*->\s*(\w+);')
    for match in edge_pattern.finditer(content):
        src, dst = match.groups()
        nodes_ids = {n["id"] for n in nodes}
        # Only add edge if both nodes are valid
        if src in nodes_ids and dst in nodes_ids:
            edges.append({"source": src, "target": dst, "predicate": "linksTo"})
            
    return nodes, edges

def sync_to_db(nodes, edges):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Initialize ontology tables if they do not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_classes (
            class_id TEXT PRIMARY KEY,
            parent_class_id TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_instances (
            instance_id TEXT PRIMARY KEY,
            class_id TEXT,
            label TEXT NOT NULL,
            properties_json TEXT,
            FOREIGN KEY(class_id) REFERENCES ontology_classes(class_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_edges (
            source_id TEXT,
            target_id TEXT,
            predicate TEXT,
            PRIMARY KEY (source_id, target_id, predicate)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_change_log (
            version INTEGER PRIMARY KEY AUTOINCREMENT,
            proposed_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            change_details_json TEXT NOT NULL,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert classes if empty
    cursor.execute("SELECT COUNT(*) FROM ontology_classes")
    if cursor.fetchone()[0] == 0:
        classes = [
            ("Jurisdiction", None),
            ("LegalFramework", None),
            ("RegulatoryAuthority", None),
            ("DataSubject", None),
            ("DataCategory", None),
            ("ProcessingActivity", None),
            ("ComplianceObligation", None),
            ("AssessmentArtifact", None)
        ]
        cursor.executemany("INSERT INTO ontology_classes VALUES (?, ?)", classes)

    # Sync parsed graph
    cursor.execute("DELETE FROM ontology_instances")
    cursor.execute("DELETE FROM ontology_edges")
    
    for n in nodes:
        cursor.execute("INSERT OR REPLACE INTO ontology_instances VALUES (?, ?, ?, ?)",
                       (n["id"], n["class"], n["label"], json.dumps({})))
                       
    for e in edges:
        cursor.execute("INSERT OR REPLACE INTO ontology_edges VALUES (?, ?, ?)",
                       (e["source"], e["target"], e["predicate"]))
                       
    conn.commit()
    conn.close()
    print(f"Successfully synchronized {len(nodes)} nodes and {len(edges)} edges to the database.")

def export_db_to_dot():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT instance_id, label FROM ontology_instances")
    nodes = cursor.fetchall()
    
    cursor.execute("SELECT source_id, target_id, predicate FROM ontology_edges")
    edges = cursor.fetchall()
    
    conn.close()
    
    # Sort nodes into subgraphs/layers
    layers = {
        "cluster_input": [],
        "cluster_hidden1": [],
        "cluster_torts": [],
        "cluster_hidden2": [],
        "cluster_cert": [],
        "cluster_hidden3": [],
        "cluster_penalty": [],
        "cluster_output": []
    }
    
    for nid, label in nodes:
        placed = False
        for prefix, layer in [
            ("In_", "cluster_input"),
            ("H1_", "cluster_hidden1"),
            ("T_", "cluster_torts"),
            ("H2_", "cluster_hidden2"),
            ("Cert_", "cluster_cert"),
            ("H3_", "cluster_hidden3"),
            ("Pen_", "cluster_penalty"),
            ("Out_", "cluster_output")
        ]:
            if nid.startswith(prefix):
                layers[layer].append((nid, label))
                placed = True
                break
        if not placed:
            layers["cluster_output"].append((nid, label))
            
    # Write Graphviz format
    lines = [
        "digraph EnterpriseComplianceNeuralNet {",
        "    rankdir=LR;",
        "    splines=polyline;",
        "    nodesep=0.3;",
        "    ranksep=1.5;",
        "",
        '    node [fontname="monospace", fontsize=10, shape=box, style="filled",',
        '          fillcolor="#ffffff", color="#000000"];',
        '    edge [fontname="monospace", fontsize=8, color="#000000"];',
        ""
    ]
    
    labels = {
        "cluster_input": "INPUT LAYER: Context & Triggers",
        "cluster_hidden1": "HIDDEN LAYER 1: Statutory Frameworks",
        "cluster_torts": "HIDDEN LAYER 1.5: Privacy Torts",
        "cluster_hidden2": "HIDDEN LAYER 2: Cross-Cutting Governance",
        "cluster_cert": "HIDDEN LAYER 2.5: Certification Requirements",
        "cluster_hidden3": "HIDDEN LAYER 3: Required Operational Controls",
        "cluster_penalty": "LAYER 3.5: Penalty & Infraction Mapping",
        "cluster_output": "OUTPUT LAYER: Mandatory Artefacts & Actions"
    }
    
    for layer, items in layers.items():
        lines.append(f"    subgraph {layer} {{")
        lines.append(f'        label = "{labels[layer]}";')
        for nid, label in items:
            shape = "box"
            if nid.startswith("In_Loc_") or nid.startswith("In_Data_") or nid.startswith("In_Act_"):
                shape = "circle"
            elif nid.startswith("In_Evt_"):
                shape = "doublecircle"
            lines.append(f'        {nid:<16} [label="{label}", shape={shape}];')
        lines.append("    }")
        lines.append("")
        
    lines.append("    // EDGES")
    for src, dst, pred in edges:
        lines.append(f"    {src:<16} -> {dst};")
        
    lines.append("}")
    
    with open(DOT_FILE, "w") as f:
        f.write("\n".join(lines))
    print(f"Successfully exported Graphviz network to {DOT_FILE}.")

def query_growth_suggestions():
    # Fetch current nodes and edges to feed to the LLM
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT instance_id, label FROM ontology_instances")
    nodes = cursor.fetchall()
    cursor.execute("SELECT source_id, target_id FROM ontology_edges")
    edges = cursor.fetchall()
    conn.close()
    
    nodes_str = "\n".join([f"- {nid}: {label}" for nid, label in nodes])
    edges_str = "\n".join([f"- {src} -> {dst}" for src, dst in edges])
    
    prompt = f"""
You are the KIBO Compliance Intelligence Agent. Your task is to review the current enterprise compliance network and suggest three NEW regulatory additions to grow the network.
Suggestions should reflect actual real-world developments in privacy law (e.g. EU AI Act requirements, new US state laws, or Canadian Federal bill amendments).

Here are the current compliance nodes:
{nodes_str}

Here are the current connections (edges):
{edges_str}

Analyze the network. Formulate exactly 3 growth proposals. Each proposal must introduce:
1. One framework (H1_), control (H3_), or output artifact (Out_) node with a unique ID and descriptive label.
2. The edges connecting this new node to the existing network.

Format your response as a valid JSON object containing a "changes" array:
{{
  "changes": [
    {{
      "node_id": "H1_EU_AIAct_HighRisk",
      "label": "High-Risk AI Systems classification",
      "reason": "Classifies AI applications that pose safety or rights risks under EU AI Act.",
      "edges": [
        {{"source": "In_Act_AI", "target": "H1_EU_AIAct_HighRisk"}},
        {{"source": "H1_EU_AIAct_HighRisk", "target": "H3_ConformityAssessment_AIAct"}}
      ]
    }},
    ...
  ]
}}
Respond with the raw JSON only. Do not include markdown code block syntax.
"""
    
    # Query nemotron-3-super:latest on waelbot using the query_nemotron helper script or system prompt
    sys.path.append("/Users/dr.wael/.gemini/antigravity-ide/brain/f23bbb0f-bf38-4d3e-82bf-c701d2834305")
    from scratch.query_nemotron import query_nemotron
    print("Querying reasoning-core:latest on waelbot for growth suggestions...")
    res = query_nemotron(prompt, "You are a professional legal compliance graph generator. Return only raw JSON.")
    
    # Clean json block wrappers if any
    res_clean = re.sub(r'```json\s*|\s*```', '', res).strip()
    return json.loads(res_clean)

def apply_growth_suggestions(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    changes_made = []
    
    for item in data.get("changes", []):
        node_id = item["node_id"]
        label = item["label"]
        reason = item["reason"]
        edges = item.get("edges", [])
        
        # Insert node
        cls = determine_class(node_id)
        cursor.execute("INSERT OR REPLACE INTO ontology_instances VALUES (?, ?, ?, ?)",
                       (node_id, cls, label, json.dumps({})))
        changes_made.append(f"Added Node: {node_id} ({label})")
        
        # Insert edges
        for edge in edges:
            src = edge["source"]
            dst = edge["target"]
            cursor.execute("INSERT OR REPLACE INTO ontology_edges VALUES (?, ?, ?)",
                           (src, dst, "linksTo"))
            changes_made.append(f"Added Edge: {src} -> {dst}")
            
    # Log to change log
    if changes_made:
        cursor.execute("INSERT INTO ontology_change_log (proposed_by, reason, change_details_json) VALUES (?, ?, ?)",
                       ("LegalNet Grow Agent", "Continuous network self-improvement", json.dumps(changes_made)))
        
    conn.commit()
    conn.close()
    
    print(f"Applied updates:")
    for change in changes_made:
        print(f" - {change}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 legalnet_grow_agent.py {--sync | --grow}")
        sys.exit(1)
        
    arg = sys.argv[1]
    if arg == "--sync":
        nodes, edges = parse_dot_file(DOT_FILE)
        sync_to_db(nodes, edges)
    elif arg == "--grow":
        suggestions = query_growth_suggestions()
        apply_growth_suggestions(suggestions)
        export_db_to_dot()
    else:
        print("Unknown argument.")
