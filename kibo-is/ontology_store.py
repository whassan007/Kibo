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
    
    # 1. Seed Core Classes (Eleven Classes — extended from Ontology_builder entities)
    classes = [
        ("Jurisdiction", None),
        ("LegalFramework", None),
        ("RegulatoryAuthority", None),
        ("DataSubject", None),
        ("DataCategory", None),
        ("ProcessingActivity", None),
        ("ComplianceObligation", None),
        ("AssessmentArtifact", None),
        # Added from Ontology_builder discovery engine
        ("PrivacyTort", None),
        ("PenaltyExposure", None),
        ("CrossBorderFramework", None),
        ("TrainingMaterial", None),
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
        
        # Training Materials
        ("AnnualSecurityTraining", "TrainingMaterial", "Annual Security Awareness Training", json.dumps({"url": "/assets/Policies/AnnualSecurityTraining.pdf"})),
        ("DataRetentionTraining", "TrainingMaterial", "Data Retention Policy Training", json.dumps({"url": "/assets/Policies/DataRetentionTraining.pdf"})),
        ("PrivacyImpactAssessment", "TrainingMaterial", "Privacy Impact Assessment Workshop", json.dumps({"url": "/assets/Policies/PrivacyImpactAssessment.pdf"})),
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
        ("StandardReview", "AssessmentArtifact", "Standard Compliance Review", json.dumps({"hasSLAClock": 60})),

        # ---- Privacy Torts (from Ontology_builder.py PRIVACY_TORTS) ----
        ("T_US_Intrusion", "PrivacyTort", "Intrusion upon seclusion (US)", json.dumps({"jurisdiction": "United States"})),
        ("T_US_PubDisc", "PrivacyTort", "Public disclosure of private facts (US)", json.dumps({"jurisdiction": "United States"})),
        ("T_US_FalseLight", "PrivacyTort", "False light (US)", json.dumps({"jurisdiction": "United States"})),
        ("T_US_Approp", "PrivacyTort", "Appropriation of name/likeness (US)", json.dumps({"jurisdiction": "United States"})),
        ("T_CA_Intrusion", "PrivacyTort", "Intrusion upon seclusion (Canada)", json.dumps({"jurisdiction": "Canada"})),
        ("T_CA_PubDisc", "PrivacyTort", "Public disclosure of private facts (Canada)", json.dumps({"jurisdiction": "Canada"})),
        ("T_EU_Infringement", "PrivacyTort", "Infringement of personality rights (EU)", json.dumps({"jurisdiction": "European Union"})),
        ("T_EU_BreachConf", "PrivacyTort", "Breach of confidentiality (EU)", json.dumps({"jurisdiction": "European Union"})),

        # ---- Penalty / Regulatory Exposure nodes (from Ontology_builder.py PENALTIES) ----
        ("Pen_OPC_Fed", "PenaltyExposure", "OPC (Federal Canada)", json.dumps({"jurisdiction": "Canada (Federal)", "max_penalty": "CAD 100k/violation"})),
        ("Pen_FTC", "PenaltyExposure", "FTC (US Federal)", json.dumps({"jurisdiction": "United States", "max_penalty": "USD 43,792/violation"})),
        ("Pen_EU_DPA", "PenaltyExposure", "EU DPA (European Union)", json.dumps({"jurisdiction": "European Union", "max_penalty": "4% global turnover or EUR 20M"})),
        ("Pen_CAI_QC", "PenaltyExposure", "CAI Quebec (Law 25)", json.dumps({"jurisdiction": "Quebec, Canada", "max_penalty": "CAD 25M or 4% of worldwide turnover"})),

        # ---- Cross-Border Frameworks (from Ontology_builder.py CROSS_BORDER_AGREEMENTS) ----
        ("CB_CETA", "CrossBorderFramework", "CETA (Canada-EU)", json.dumps({"parties": ["Canada", "EU"], "type": "Trade Agreement with Data Chapter"})),
        ("CB_USMCA", "CrossBorderFramework", "USMCA (US-Mexico-Canada)", json.dumps({"parties": ["US", "Canada", "Mexico"], "type": "Trade Agreement with Digital Trade Chapter"})),
        ("CB_EU_US_DPF", "CrossBorderFramework", "EU-US Data Privacy Framework", json.dumps({"parties": ["EU", "US"], "type": "Adequacy Decision"})),
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
        ("AI_Training", "CPRA_ADMT", "mandatesArtifact"),

        # ---- Tort -> Penalty enforcement edges ----
        ("T_US_Intrusion", "Pen_FTC", "enforcedBy"),
        ("T_US_PubDisc", "Pen_FTC", "enforcedBy"),
        ("T_US_FalseLight", "Pen_FTC", "enforcedBy"),
        ("T_US_Approp", "Pen_FTC", "enforcedBy"),
        ("T_CA_Intrusion", "Pen_OPC_Fed", "enforcedBy"),
        ("T_CA_PubDisc", "Pen_OPC_Fed", "enforcedBy"),
        ("T_EU_Infringement", "Pen_EU_DPA", "enforcedBy"),
        ("T_EU_BreachConf", "Pen_EU_DPA", "enforcedBy"),

        # ---- Framework -> Penalty regulator edges ----
        ("PIPEDA", "Pen_OPC_Fed", "regulatedBy"),
        ("Law_25", "Pen_CAI_QC", "regulatedBy"),
        ("GDPR", "Pen_EU_DPA", "regulatedBy"),
        ("CCPA", "Pen_FTC", "regulatedBy"),
        ("VCDPA", "Pen_FTC", "regulatedBy"),
        ("TDPSA", "Pen_FTC", "regulatedBy"),

        # ---- Cross-border frameworks -> Transfer artifact ----
        ("CB_CETA", "Law25_TIA", "triggersArtifact"),
        ("CB_USMCA", "Law25_TIA", "triggersArtifact"),
        ("CB_EU_US_DPF", "Article35_DPIA", "triggersArtifact"),

        # ---- Torts connected to Jurisdiction context ----
        ("CA_Federal", "T_CA_Intrusion", "recognizesTort"),
        ("CA_Federal", "T_CA_PubDisc", "recognizesTort"),
        ("EU_Union", "T_EU_Infringement", "recognizesTort"),
        ("EU_Union", "T_EU_BreachConf", "recognizesTort"),
    ]
    cursor.executemany("INSERT INTO ontology_edges VALUES (?, ?, ?)", edges)
    
    conn.commit()
    conn.close()

# ---------------------------------------------------------------------------
# Graph-traversal routing (used by route_to_statutory_artifacts)
# ---------------------------------------------------------------------------
# State/province -> federal parent, so federal statutes (PIPEDA, HIPAA, FERPA,
# FTC Act) activate for sub-national transactions.
JURISDICTION_PARENTS = {
    "Ontario": "CA_Federal", "Quebec": "CA_Federal", "Alberta": "CA_Federal",
    "California": "US_Federal", "Texas": "US_Federal", "New_York": "US_Federal",
    "Illinois": "US_Federal", "Washington": "US_Federal", "Virginia": "US_Federal",
}

def derive_compliance_routing(jurisdictions, data_categories, activities):
    """Two-hop ontology traversal:

      context (jurisdictions + data categories + activities)
        -> active LegalFrameworks   (enforcesFramework / triggersFramework)
        -> mandated controls        (mandatesControl)
        -> produced artifacts       (producesArtifact + legacy mandatesArtifact)

    Activation rules (conjunctive gating — avoids e.g. HIPAA firing in Ontario):
      1. A framework enforced by a context jurisdiction is active, UNLESS it has
         DataCategory trigger edges and none of them match the context (sector
         statutes like HIPAA require jurisdiction AND data type).
      2. A framework with no territorial edge at all (PCI-DSS, SOX, NIST —
         contractual/sectoral) activates on a data/activity trigger alone.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    jurs = {j for j in (jurisdictions or []) if j}
    for j in list(jurs):
        parent = JURISDICTION_PARENTS.get(j)
        if parent:
            jurs.add(parent)
    cats = set(data_categories or [])
    acts = set(activities or [])

    def targets(sources, predicate):
        if not sources:
            return set()
        ph = ",".join("?" * len(sources))
        cur.execute(
            f"SELECT DISTINCT target_id FROM ontology_edges "
            f"WHERE source_id IN ({ph}) AND predicate = ?",
            (*sources, predicate))
        return {r[0] for r in cur.fetchall()}

    jur_frameworks = targets(jurs, "enforcesFramework")

    cur.execute("SELECT DISTINCT target_id FROM ontology_edges "
                "WHERE predicate = 'enforcesFramework'")
    territorially_bound = {r[0] for r in cur.fetchall()}

    # framework -> data categories that gate it
    cur.execute("""SELECT e.source_id, e.target_id FROM ontology_edges e
                   JOIN ontology_instances i ON i.instance_id = e.source_id
                   WHERE e.predicate = 'triggersFramework'
                     AND i.class_id = 'DataCategory'""")
    data_gates = {}
    for src, tgt in cur.fetchall():
        data_gates.setdefault(tgt, set()).add(src)

    active = set()
    for fw in jur_frameworks:
        gate = data_gates.get(fw)
        if gate and not (gate & cats):
            continue
        active.add(fw)

    trig_frameworks = targets(cats | acts, "triggersFramework")
    active |= (trig_frameworks - territorially_bound)

    controls = targets(active, "mandatesControl")
    artifacts = targets(controls, "producesArtifact")

    # Legacy direct mandatesArtifact edges, gated by their parent framework so a
    # bare activity match (e.g. "Collection" in Illinois) can't fire a Quebec PIA.
    ARTIFACT_GATE = {
        "PHIPA_TRA": "PHIPA", "Law25_PIA": "Law_25", "Law25_TIA": "Law_25",
        "Article35_DPIA": "GDPR", "CPRA_ADMT": "CCPA",
    }
    for art in targets(jurs | cats | acts, "mandatesArtifact"):
        gate_fw = ARTIFACT_GATE.get(art)
        if gate_fw is None or gate_fw in active:
            artifacts.add(art)

    conn.close()
    return {
        "active_frameworks": sorted(active),
        "mandated_controls": sorted(controls),
        "mandated_artifacts": sorted(artifacts),
    }

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
