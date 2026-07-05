"""
neuralnet_ontology.py — DOT -> KIBO ontology converter/importer.

Parses the EnterpriseComplianceNeuralNet graphviz file, applies legal
corrections (wrong jurisdictions, undefined nodes, wrong regulators),
maps every layer onto the ontology_store.py schema, and either:

  --jsonld PATH   write a W3C JSON-LD file (full graph: current DB + expansion)
                  suitable for POST /api/ontology/import
  --apply         merge additively into kibo_state.db (preferred: keeps the
                  existing seed, adds classes, logs to ontology_change_log)
  (no flag)       dry run: print a summary of what would be imported

Usage:
  ../.venv/bin/python neuralnet_ontology.py compliance_neuralnet.dot --apply
  ../.venv/bin/python neuralnet_ontology.py compliance_neuralnet.dot --jsonld expansion.jsonld
"""

import json
import os
import re
import sqlite3
import sys

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")

# ---------------------------------------------------------------------------
# 1. CLASS DETECTION — DOT id prefix -> ontology class
# ---------------------------------------------------------------------------
PREFIX_CLASS = [
    ("In_Loc_",  "Jurisdiction"),
    ("In_Data_", "DataCategory"),
    ("In_Act_",  "ProcessingActivity"),
    ("In_Evt_",  "EventTrigger"),
    ("H1_",      "LegalFramework"),
    ("T_",       "PrivacyTort"),
    ("H2_",      "GovernanceControl"),
    ("H3_",      "ComplianceObligation"),
    ("Cert_",    "Certification"),
    ("Pen_",     "PenaltyExposure"),
    ("Out_",     "AssessmentArtifact"),
]

NEW_CLASSES = ["EventTrigger", "PrivacyTort", "GovernanceControl",
               "Certification", "PenaltyExposure"]

# ---------------------------------------------------------------------------
# 2. PREDICATE MAP — (source class, target class) -> edge predicate
#    "mandatesArtifact" and "enforcesFramework" match the existing seed so
#    route_to_statutory_artifacts() keeps working unchanged.
# ---------------------------------------------------------------------------
PREDICATES = {
    ("Jurisdiction",        "LegalFramework"):       "enforcesFramework",
    ("DataCategory",        "LegalFramework"):       "triggersFramework",
    ("ProcessingActivity",  "LegalFramework"):       "triggersFramework",
    ("EventTrigger",        "LegalFramework"):       "triggersFramework",
    ("LegalFramework",      "PrivacyTort"):          "exposesToTort",
    ("DataCategory",        "PrivacyTort"):          "exposesToTort",
    ("ProcessingActivity",  "PrivacyTort"):          "exposesToTort",
    ("EventTrigger",        "PrivacyTort"):          "exposesToTort",
    ("PrivacyTort",         "GovernanceControl"):    "mitigatedBy",
    ("LegalFramework",      "GovernanceControl"):    "mandatesControl",
    ("LegalFramework",      "ComplianceObligation"): "mandatesControl",
    ("GovernanceControl",   "Certification"):        "supportsCertification",
    ("Certification",       "ComplianceObligation"): "requiresControl",
    ("GovernanceControl",   "ComplianceObligation"): "implementedBy",
    ("ComplianceObligation","AssessmentArtifact"):   "producesArtifact",
    ("GovernanceControl",   "AssessmentArtifact"):   "producesArtifact",
    ("Certification",       "AssessmentArtifact"):   "producesArtifact",
    ("LegalFramework",      "PenaltyExposure"):      "exposesToPenalty",
    ("PrivacyTort",         "PenaltyExposure"):      "exposesToPenalty",
    ("PenaltyExposure",     "AssessmentArtifact"):   "canIssue",
    ("Jurisdiction",        "AssessmentArtifact"):   "mandatesArtifact",
    ("DataCategory",        "AssessmentArtifact"):   "mandatesArtifact",
    ("ProcessingActivity",  "AssessmentArtifact"):   "mandatesArtifact",
    ("EventTrigger",        "ComplianceObligation"): "activatesControl",
    ("ProcessingActivity",  "ComplianceObligation"): "activatesControl",
}

# ---------------------------------------------------------------------------
# 3. ID MAP — DOT ids -> existing ontology_store.py instance ids, so the
#    expansion attaches to the seeded graph instead of duplicating it.
# ---------------------------------------------------------------------------
ID_MAP = {
    "In_Loc_ON": "Ontario",          "In_Loc_QC": "Quebec",
    "In_Loc_Fed": "CA_Federal",      "In_Loc_US_CA": "California",
    "In_Loc_US_TX": "Texas",         "In_Loc_EU": "EU_Union",
    "In_Loc_UK": "UK",               "In_Loc_AU": "Australia",
    "In_Loc_SG": "Singapore",        "In_Loc_US_NY": "New_York",
    "In_Loc_US_IL": "Illinois",      "In_Loc_US_WA": "Washington",
    "In_Loc_CA_AB": "Alberta",       "In_Loc_US_Fed": "US_Federal",
    "H1_PHIPA": "PHIPA",             "H1_Law25": "Law_25",
    "H1_PIPEDA": "PIPEDA",           "H1_CPRA": "CCPA",
    "H1_GDPR": "GDPR",               "H1_FIPPA": "FIPPA",
    "H1_TDPSA": "TDPSA",
    "In_Data_PHI": "PHI",            "In_Data_Bio": "BiometricData",
    "In_Data_PII": "PersonalInformation_PI",
    "In_Data_Fin": "FinancialData",
    "In_Act_XBorder": "Transfer",    "In_Act_AI": "Profiling",
}

# ---------------------------------------------------------------------------
# 4. CORRECTIONS — fixes to the source graph, applied on DOT ids.
# ---------------------------------------------------------------------------
# (src, dst) edges rewritten to legally correct endpoints
EDGE_REMAPS = {
    # BIPA is Illinois, not Texas
    ("In_Loc_US_TX", "H1_BIPA"): ("In_Loc_US_IL", "H1_BIPA"),
    # My Health My Data is Washington State, not Texas
    ("In_Loc_US_TX", "H1_MHMDA"): ("In_Loc_US_WA", "H1_MHMDA"),
    # PIPA (AB) is Alberta provincial, not Canada federal
    ("In_Loc_Fed", "H1_PIPA_AB"): ("In_Loc_CA_AB", "H1_PIPA_AB"),
    # Texas comprehensive law is TDPSA, not CPRA
    ("In_Loc_US_TX", "H1_CPRA"): ("In_Loc_US_TX", "H1_TDPSA"),
    # New York has SHIELD Act (no comprehensive CPRA-like law)
    ("In_Loc_US_NY", "H1_CPRA"): ("In_Loc_US_NY", "H1_NY_SHIELD"),
    # FERPA / FTC Act are US federal, not Canada federal
    ("In_Loc_Fed", "H1_FERPA"): ("In_Loc_US_Fed", "H1_FERPA"),
    ("In_Loc_Fed", "H1_FTCAct5"): ("In_Loc_US_Fed", "H1_FTCAct5"),
    # H2_Gov_Leadership is undefined in the DOT; the real node is H3_Leadership
    ("H1_Law25", "H2_Gov_Leadership"): ("H1_Law25", "H3_Leadership"),
    ("H1_GDPR", "H2_Gov_Leadership"): ("H1_GDPR", "H3_Leadership"),
    # NYDFS enforces Part 500 itself; SEC is the wrong regulator
    ("H1_NYDFS", "Pen_SEC"): ("H1_NYDFS", "Pen_NYDFS"),
    # FERPA is enforced by the US Dept of Education, not the FTC
    ("H1_FERPA", "Pen_FTC"): ("H1_FERPA", "Pen_ED"),
    # BIPA's teeth are its private right of action in IL courts
    ("H1_BIPA", "Pen_FTC"): ("H1_BIPA", "Pen_ILCourts"),
    # NYC LL144 is enforced by NYC DCWP
    ("H1_NYC_AIBias", "Pen_FTC"): ("H1_NYC_AIBias", "Pen_NYC_DCWP"),
    # MHMDA is enforced by the WA AG (via CPA) + private right of action
    ("H1_MHMDA", "Pen_FTC"): ("H1_MHMDA", "Pen_WA_AG"),
    # PCI-DSS is contractual: card brand / acquirer fines, not SEC
    ("H1_PCI_DSS", "Pen_SEC"): ("H1_PCI_DSS", "Pen_CardBrands"),
}

# edges deleted outright (wrong regulator / wrong jurisdiction / undefined node)
EDGE_DROPS = {
    ("In_Loc_Fed", "H1_ISO27001"),      # ISO 27001 is voluntary, not enforced by a jurisdiction
    ("H1_Fin", "Pen_SEC"),              # H1_Fin never defined
    ("H1_FIPPA", "Pen_OPC_Fed"), ("H1_FIPPA", "Pen_OPC_QC"),   # FIPPA -> IPC ON only
    ("H1_PHIPA", "Pen_OPC_Fed"), ("H1_PHIPA", "Pen_OPC_QC"),   # PHIPA -> IPC ON only
    ("H1_Law25", "Pen_OPC_ON"),                                 # Law 25 -> CAI only
    ("H1_PIPA_AB", "Pen_OPC_Fed"), ("H1_PIPA_AB", "Pen_OPC_ON"),
    ("H1_PIPA_AB", "Pen_OPC_QC"),                               # PIPA AB -> OIPC AB
    ("H1_ISO27001", "Pen_SEC"),         # a standard, not a statute
    ("H1_GDPR", "Pen_FTC"),             # GDPR is not FTC-enforced
    ("H1_EU_AIAct", "Pen_FTC"),
    # Torts are civil claims, not regulator fines — rerouted to Pen_CivilCourts below
    ("T_US_Intrusion", "Pen_FTC"), ("T_US_PubDisc", "Pen_FTC"),
    ("T_US_FalseLight", "Pen_FTC"), ("T_US_Approp", "Pen_FTC"),
    ("T_CA_Intrusion", "Pen_OPC_Fed"), ("T_CA_PubDisc", "Pen_OPC_Fed"),
    ("T_CA_FalseLight", "Pen_OPC_Fed"), ("T_CA_Approp", "Pen_OPC_Fed"),
    ("T_EU_Infringement", "Pen_EU_DPA"), ("T_EU_BreachConf", "Pen_EU_DPA"),
    ("T_EU_DataProtViol", "Pen_EU_DPA"), ("T_EU_RTBF", "Pen_EU_DPA"),
}

# nodes referenced by corrections but absent from the DOT: (dot_id, class, label, props)
NEW_NODES = [
    ("In_Loc_US_IL", "Jurisdiction", "Illinois",
     {"region": "North America", "level": "Regional"}),
    ("In_Loc_US_WA", "Jurisdiction", "Washington",
     {"region": "North America", "level": "Regional"}),
    ("In_Loc_CA_AB", "Jurisdiction", "Alberta",
     {"region": "North America", "level": "Regional"}),
    ("In_Loc_US_Fed", "Jurisdiction", "United States Federal",
     {"region": "North America", "level": "National"}),
    ("H1_TDPSA", "LegalFramework", "Texas TDPSA", {"status": "Active"}),
    ("H1_NY_SHIELD", "LegalFramework", "New York SHIELD Act", {"status": "Active"}),
    ("Pen_NYDFS", "PenaltyExposure",
     "NYDFS Part 500 enforcement (per-violation / per-day penalties)", {}),
    ("Pen_OIPC_AB", "PenaltyExposure",
     "OIPC Alberta — PIPA offences up to CAD 100k", {"max_fine_cad": 100000}),
    ("Pen_ED", "PenaltyExposure",
     "US Dept of Education — FERPA federal funding conditions", {}),
    ("Pen_CardBrands", "PenaltyExposure",
     "Card brand / acquirer fines (PCI-DSS, contractual)", {}),
    ("Pen_ILCourts", "PenaltyExposure",
     "BIPA private right of action — USD 1k negligent / 5k willful per violation",
     {"per_violation_usd": 5000}),
    ("Pen_NYC_DCWP", "PenaltyExposure",
     "NYC DCWP — Local Law 144 civil penalties", {}),
    ("Pen_WA_AG", "PenaltyExposure",
     "Washington AG enforcement + private right of action (MHMDA via CPA)", {}),
    ("Pen_CivilCourts", "PenaltyExposure",
     "Civil litigation — tort damages / class actions", {}),
    ("StudentRecords", "DataCategory", "Student Education Records",
     {"isSensitive": True}),
]

# edges added beyond the DOT (dot-id space; predicates derived from classes)
EXTRA_EDGES = [
    ("In_Loc_CA_AB", "H1_PIPA_AB"),
    ("In_Loc_US_Fed", "H1_HIPAA"),      # HIPAA is US federal law
    ("H1_PIPA_AB", "Pen_OIPC_AB"),
    ("In_Loc_US_IL", "H1_BIPA"),
    ("In_Loc_US_WA", "H1_MHMDA"),
    # data-category gates so sector statutes need jurisdiction AND data type
    ("StudentRecords", "H1_FERPA"),
    ("In_Data_Bio", "H1_BIPA"),
    ("In_Data_PHI", "H1_MHMDA"),
] + [(t, "Pen_CivilCourts") for t in [
    "T_US_Intrusion", "T_US_PubDisc", "T_US_FalseLight", "T_US_Approp",
    "T_CA_Intrusion", "T_CA_PubDisc", "T_CA_FalseLight", "T_CA_Approp",
    "T_EU_Infringement", "T_EU_BreachConf", "T_EU_DataProtViol", "T_EU_RTBF"]]

# label corrections pushed onto existing/parsed nodes (dot_id -> label)
LABEL_FIXES = {
    "Pen_OPC_QC": "CAI QC — AMPs up to CAD 10M or 2% of turnover; "
                  "penal up to CAD 25M or 4% (Law 25)",
}

# ---------------------------------------------------------------------------
# DOT parsing
# ---------------------------------------------------------------------------
NODE_RE = re.compile(r'^\s*(\w+)\s*\[\s*label\s*=\s*"((?:[^"\\]|\\.)*)"',
                     re.MULTILINE | re.DOTALL)
EDGE_RE = re.compile(r'(\w+)\s*->\s*(\w+)')
DOT_KEYWORDS = {"node", "edge", "graph", "subgraph", "digraph", "label", "rankdir"}


def classify(dot_id):
    for prefix, cls in PREFIX_CLASS:
        if dot_id.startswith(prefix):
            return cls
    return None


def clean_label(raw):
    text = raw.replace("\\n", "\n")
    text = re.sub(r"\s*\n\s*", "\n", text).strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # strip layer prefixes like "Framework:", "Control:", "[ARTIFACT]"
    if lines and re.match(r"^(\[?(ARTIFACT|ACTION)\]?|Framework:|Control:|Certification:|Penalty:|.{0,10} Tort:|Loc:|Data:|Act:|Event:)\s*$",
                          lines[0]):
        lines = lines[1:]
    elif lines:
        lines[0] = re.sub(r"^(\[(ARTIFACT|ACTION)\]|Framework:|Control:|Certification:|Penalty:|Loc:|Data:|Act:|Event:)\s*",
                          "", lines[0]).strip()
    label = lines[0] if lines else raw
    description = " ".join(lines[1:]) if len(lines) > 1 else None
    return label, description


def parse_dot(path):
    src = open(path, encoding="utf-8").read()
    src = re.sub(r"//[^\n]*|/\*.*?\*/", "", src, flags=re.DOTALL)  # strip comments
    nodes = {}
    for m in NODE_RE.finditer(src):
        dot_id, raw_label = m.group(1), m.group(2)
        if dot_id in DOT_KEYWORDS or classify(dot_id) is None:
            continue
        label, desc = clean_label(raw_label)
        props = {"description": desc} if desc else {}
        nodes[dot_id] = (classify(dot_id), label, props)
    stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', src)   # remove labels before edge scan
    edges = set()
    for m in EDGE_RE.finditer(stripped):
        edges.add((m.group(1), m.group(2)))
    return nodes, edges


# ---------------------------------------------------------------------------
# Build corrected instance/edge sets in KIBO id space
# ---------------------------------------------------------------------------
def build(path):
    nodes, edges = parse_dot(path)

    for dot_id, cls, label, props in NEW_NODES:
        nodes.setdefault(dot_id, (cls, label, props))
    for dot_id, label in LABEL_FIXES.items():
        if dot_id in nodes:
            cls, _, props = nodes[dot_id]
            nodes[dot_id] = (cls, label, props)

    corrected, dropped, remapped = set(), [], []
    for e in edges:
        if e in EDGE_DROPS:
            dropped.append(e)
            continue
        if e in EDGE_REMAPS:
            remapped.append((e, EDGE_REMAPS[e]))
            e = EDGE_REMAPS[e]
        corrected.add(e)
    corrected.update(EXTRA_EDGES)

    def kid(dot_id):
        return ID_MAP.get(dot_id, dot_id)

    instances = {}   # kibo_id -> (class, label, props)
    for dot_id, (cls, label, props) in nodes.items():
        instances[kid(dot_id)] = (cls, label, props)

    triples, skipped = set(), []
    for src, dst in corrected:
        s_cls = nodes.get(src, (classify(src),))[0]
        d_cls = nodes.get(dst, (classify(dst),))[0]
        pred = PREDICATES.get((s_cls, d_cls))
        if pred is None:
            skipped.append((src, dst, s_cls, d_cls))
            continue
        triples.add((kid(src), kid(dst), pred))

    return instances, triples, {"dropped": dropped, "remapped": remapped,
                                "skipped": skipped}


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
def read_db_graph():
    """Current DB content, so JSON-LD export is a complete graph
    (import_jsonld() wipes instances/edges before importing)."""
    if not os.path.exists(DB_FILE):
        return [], []
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT instance_id, class_id, label, properties_json FROM ontology_instances")
    inst = cur.fetchall()
    cur.execute("SELECT source_id, target_id, predicate FROM ontology_edges")
    edg = cur.fetchall()
    conn.close()
    return inst, edg


def to_jsonld(instances, triples, out_path):
    graph, seen = [], set()
    db_inst, db_edges = read_db_graph()
    if not db_inst:
        print("WARNING: kibo_state.db not found/empty — JSON-LD contains the "
              "expansion only. import_jsonld() wipes existing rows, so only "
              "import this against a DB you intend to replace.")
    for iid, cls, label, props_str in db_inst:
        node = {"@id": f"kibo:{iid}", "@type": f"kibo:{cls}", "label": label}
        for k, v in (json.loads(props_str) if props_str else {}).items():
            node[f"kibo:{k}"] = v
        graph.append(node)
        seen.add(iid)
    for iid, (cls, label, props) in sorted(instances.items()):
        if iid in seen:
            continue
        node = {"@id": f"kibo:{iid}", "@type": f"kibo:{cls}", "label": label}
        for k, v in props.items():
            node[f"kibo:{k}"] = v
        graph.append(node)
    all_edges = {(s, t, p) for s, t, p in db_edges} | triples
    for s, t, p in sorted(all_edges):
        graph.append({"@id": f"kibo:{s}", f"kibo:{p}": {"@id": f"kibo:{t}"}})
    doc = {"@context": {"kibo": "https://kibo.is/ontology#",
                        "label": "http://www.w3.org/2000/01/rdf-schema#label"},
           "@graph": graph}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    print(f"Wrote {out_path}: {len(graph)} graph items "
          f"({len(all_edges)} edges).")


def apply_to_db(instances, triples):
    if not os.path.exists(DB_FILE):
        sys.exit(f"ERROR: {DB_FILE} not found. Run ontology_store.py first.")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    for cls in NEW_CLASSES:
        cur.execute("INSERT OR IGNORE INTO ontology_classes VALUES (?, ?)", (cls, None))
    added_i = 0
    for iid, (cls, label, props) in instances.items():
        cur.execute("INSERT OR IGNORE INTO ontology_instances VALUES (?, ?, ?, ?)",
                    (iid, cls, label, json.dumps(props)))
        added_i += cur.rowcount
    for dot_id, label in LABEL_FIXES.items():
        cur.execute("UPDATE ontology_instances SET label=? WHERE instance_id=?",
                    (label, ID_MAP.get(dot_id, dot_id)))
    added_e = 0
    for s, t, p in triples:
        cur.execute("INSERT OR IGNORE INTO ontology_edges VALUES (?, ?, ?)", (s, t, p))
        added_e += cur.rowcount
    cur.execute(
        "INSERT INTO ontology_change_log (proposed_by, reason, change_details_json) "
        "VALUES (?, ?, ?)",
        ("neuralnet_ontology.py",
         "Imported EnterpriseComplianceNeuralNet DOT expansion (with legal corrections)",
         json.dumps({"instances_added": added_i, "edges_added": added_e,
                     "new_classes": NEW_CLASSES})))
    conn.commit()
    conn.close()
    print(f"Applied: +{added_i} instances, +{added_e} edges "
          f"(existing rows preserved). Logged to ontology_change_log.")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    dot_path = args[0]
    instances, triples, report = build(dot_path)

    print(f"Parsed {dot_path}")
    print(f"  instances: {len(instances)}   edges: {len(triples)}")
    print(f"  corrections — dropped: {len(report['dropped'])}, "
          f"remapped: {len(report['remapped'])}")
    if report["skipped"]:
        print("  WARNING — edges with no predicate mapping (not imported):")
        for s, d, sc, dc in report["skipped"]:
            print(f"    {s} ({sc}) -> {d} ({dc})")

    by_pred = {}
    for _, _, p in triples:
        by_pred[p] = by_pred.get(p, 0) + 1
    for p, n in sorted(by_pred.items(), key=lambda x: -x[1]):
        print(f"    {p}: {n}")

    if "--jsonld" in args:
        to_jsonld(instances, triples, args[args.index("--jsonld") + 1])
    if "--apply" in args:
        apply_to_db(instances, triples)
    if "--jsonld" not in args and "--apply" not in args:
        print("\nDry run only. Use --apply (additive DB merge) or --jsonld PATH.")


if __name__ == "__main__":
    main()
