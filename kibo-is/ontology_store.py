import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "kibo_state.db")

def init_ontology():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Classes Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_classes (
            class_id TEXT PRIMARY KEY,
            parent_class_id TEXT
        )
    """)
    
    # 2. Instances Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_instances (
            instance_id TEXT PRIMARY KEY,
            class_id TEXT,
            label TEXT NOT NULL,
            properties_json TEXT,
            FOREIGN KEY(class_id) REFERENCES ontology_classes(class_id)
        )
    """)
    
    # 3. Edges Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_edges (
            source_id TEXT,
            target_id TEXT,
            predicate TEXT,
            PRIMARY KEY (source_id, target_id, predicate)
        )
    """)
    
    # 4. Change Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ontology_change_log (
            version INTEGER PRIMARY KEY AUTOINCREMENT,
            proposed_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            change_details_json TEXT NOT NULL,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def seed_ontology():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Clear existing to enforce clean seed
    cursor.execute("DELETE FROM ontology_classes")
    cursor.execute("DELETE FROM ontology_instances")
    cursor.execute("DELETE FROM ontology_edges")
    
    # 1. Seed Core Classes (Eight Classes)
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
    
    # 2. Seed Instances
    instances = [
        # Jurisdictions
        ("CA_Federal", "Jurisdiction", "Canada Federal", json.dumps({"region": "North America", "level": "National"})),
        ("EU_Union", "Jurisdiction", "European Union", json.dumps({"region": "Europe", "level": "National"})),
        ("Quebec", "Jurisdiction", "Quebec", json.dumps({"region": "North America", "level": "Regional"})),
        ("Ontario", "Jurisdiction", "Ontario", json.dumps({"region": "North America", "level": "Regional"})),
        ("California", "Jurisdiction", "California", json.dumps({"region": "North America", "level": "Regional"})),
        ("Virginia", "Jurisdiction", "Virginia", json.dumps({"region": "North America", "level": "Regional"})),
        ("Texas", "Jurisdiction", "Texas", json.dumps({"region": "North America", "level": "Regional"})),
        
        # Legal Frameworks
        ("PIPEDA", "LegalFramework", "PIPEDA", json.dumps({"status": "Active"})),
        ("GDPR", "LegalFramework", "EU GDPR", json.dumps({"status": "Active"})),
        ("Law_25", "LegalFramework", "Quebec Law 25", json.dumps({"status": "Active"})),
        ("PHIPA", "LegalFramework", "Ontario PHIPA", json.dumps({"status": "Active"})),
        ("FIPPA", "LegalFramework", "Ontario FIPPA", json.dumps({"status": "Active"})),
        ("CCPA", "LegalFramework", "California CCPA/CPRA", json.dumps({"status": "Active"})),
        ("VCDPA", "LegalFramework", "Virginia VCDPA", json.dumps({"status": "Active"})),
        ("TDPSA", "LegalFramework", "Texas TDPSA", json.dumps({"status": "Active"})),
        
        # Regulatory Authorities
        ("OPC", "RegulatoryAuthority", "Office of the Privacy Commissioner of Canada", json.dumps({})),
        ("CAI", "RegulatoryAuthority", "Commission d'accès à l'information du Québec", json.dumps({})),
        ("CPPA", "RegulatoryAuthority", "California Privacy Protection Agency", json.dumps({})),
        ("IPC", "RegulatoryAuthority", "Information and Privacy Commissioner of Ontario", json.dumps({})),
        
        # Data Categories
        ("PersonalInformation_PI", "DataCategory", "Personal Information", json.dumps({"isSensitive": False})),
        ("SensitiveData", "DataCategory", "Sensitive Personal Data", json.dumps({"isSensitive": True})),
        ("PHI", "DataCategory", "Protected Health Information", json.dumps({"isSensitive": True})),
        ("BiometricData", "DataCategory", "Biometric Data", json.dumps({"isSensitive": True})),
        ("ChildrensData", "DataCategory", "Children's Data", json.dumps({"isSensitive": True, "child_age_limit_coppa": 13, "child_age_limit_law25": 14})),
        ("FinancialData", "DataCategory", "Financial Data", json.dumps({"isSensitive": True})),
        
        # Processing Activities
        ("Collection", "ProcessingActivity", "Collection", json.dumps({})),
        ("Storage", "ProcessingActivity", "Storage", json.dumps({})),
        ("Transfer", "ProcessingActivity", "Transfer", json.dumps({})),
        ("Profiling", "ProcessingActivity", "Profiling", json.dumps({})),
        ("AI_Training", "ProcessingActivity", "AI Model Training", json.dumps({})),
        
        # Assessment Artifacts
        ("PHIPA_TRA", "AssessmentArtifact", "PHIPA Threat & Risk Assessment", json.dumps({"hasSLAClock": 30})),
        ("Law25_TIA", "AssessmentArtifact", "Quebec Law 25 Transfer Impact Assessment", json.dumps({"hasSLAClock": 30})),
        ("Law25_PIA", "AssessmentArtifact", "Quebec Law 25 Privacy Impact Assessment", json.dumps({"hasSLAClock": 30})),
        ("Article35_DPIA", "AssessmentArtifact", "GDPR Article 35 Data Protection Impact Assessment", json.dumps({"hasSLAClock": 30})),
        ("CPRA_ADMT", "AssessmentArtifact", "CPRA Automated Decision-Making Assessment", json.dumps({"hasSLAClock": 45})),
        ("StandardReview", "AssessmentArtifact", "Standard Compliance Review", json.dumps({"hasSLAClock": 60}))
    ]
    cursor.executemany("INSERT INTO ontology_instances VALUES (?, ?, ?, ?)", instances)
    
    # 3. Seed Predicates / Edges
    edges = [
        # Frameworks mandated in Jurisdictions
        ("CA_Federal", "PIPEDA", "enforcesFramework"),
        ("EU_Union", "GDPR", "enforcesFramework"),
        ("Quebec", "Law_25", "enforcesFramework"),
        ("Ontario", "PHIPA", "enforcesFramework"),
        ("California", "CCPA", "enforcesFramework"),
        ("Virginia", "VCDPA", "enforcesFramework"),
        ("Texas", "TDPSA", "enforcesFramework"),
        
        # Adequacy relationships
        ("Quebec", "EU_Union", "isAdequate"),
        ("EU_Union", "Quebec", "isAdequate"),
        ("CA_Federal", "EU_Union", "isAdequate"),
        ("EU_Union", "CA_Federal", "isAdequate"),
        
        # Artifact mandates given context triggers (Jurisdiction/DataCategory/ProcessingActivity)
        ("Ontario", "PHIPA_TRA", "mandatesArtifact"),
        ("PHI", "PHIPA_TRA", "mandatesArtifact"),
        
        ("Quebec", "Law25_PIA", "mandatesArtifact"),
        ("Collection", "Law25_PIA", "mandatesArtifact"),
        ("Profiling", "Law25_PIA", "mandatesArtifact"),
        ("Transfer", "Law25_TIA", "mandatesArtifact"),
        
        ("EU_Union", "Article35_DPIA", "mandatesArtifact"),
        ("Storage", "Article35_DPIA", "mandatesArtifact"),
        
        ("California", "CPRA_ADMT", "mandatesArtifact"),
        ("AI_Training", "CPRA_ADMT", "mandatesArtifact")
    ]
    cursor.executemany("INSERT INTO ontology_edges VALUES (?, ?, ?)", edges)
    
    conn.commit()
    conn.close()

def export_jsonld():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT instance_id, class_id, label, properties_json FROM ontology_instances")
    instances = cursor.fetchall()
    
    cursor.execute("SELECT source_id, target_id, predicate FROM ontology_edges")
    edges = cursor.fetchall()
    
    conn.close()
    
    graph = []
    for inst_id, cls, label, props_str in instances:
        node = {
            "@id": f"kibo:{inst_id}",
            "@type": f"kibo:{cls}",
            "label": label
        }
        if props_str:
            props = json.loads(props_str)
            for k, v in props.items():
                node[f"kibo:{k}"] = v
        graph.append(node)
        
    for src, tgt, pred in edges:
        graph.append({
            "@id": f"kibo:{src}",
            f"kibo:{pred}": {"@id": f"kibo:{tgt}"}
        })
        
    jsonld = {
        "@context": {
            "kibo": "https://kibo.is/ontology#",
            "label": "http://www.w3.org/2000/01/rdf-schema#label"
        },
        "@graph": graph
    }
    return json.dumps(jsonld, indent=2)

def import_jsonld(json_str):
    data = json.loads(json_str)
    graph = data.get("@graph", [])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM ontology_instances")
    cursor.execute("DELETE FROM ontology_edges")
    
    for item in graph:
        node_id = item.get("@id", "").replace("kibo:", "")
        node_type = item.get("@type", "").replace("kibo:", "")
        label = item.get("label", node_id)
        
        if not node_id:
            continue
            
        # Determine if it's an instance or an edge link representation
        predicates = [k for k in item.keys() if k.startswith("kibo:") and k != "kibo:type"]
        
        if node_type:
            # It's an instance node
            props = {}
            for k, v in item.items():
                if k.startswith("kibo:") and k not in ["kibo:type"]:
                    props[k.replace("kibo:", "")] = v
            cursor.execute("INSERT OR REPLACE INTO ontology_instances VALUES (?, ?, ?, ?)",
                           (node_id, node_type, label, json.dumps(props)))
        
        # Links
        for pred in predicates:
            pred_name = pred.replace("kibo:", "")
            target_info = item[pred]
            if isinstance(target_info, dict) and "@id" in target_info:
                target_id = target_info["@id"].replace("kibo:", "")
                cursor.execute("INSERT OR REPLACE INTO ontology_edges VALUES (?, ?, ?)",
                               (node_id, target_id, pred_name))
                               
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_ontology()
    seed_ontology()
    print("Ontology seed complete.")
