#!/usr/bin/env python3
"""
Compliance Discovery & Enterprise NeuralNet Updater
Discovers laws, torts, penalties, and agreements across US/CA/EU jurisdictions,
then automatically updates the EnterpriseComplianceNeuralNet Graphviz diagram.
"""

import re
import json
import os
import sqlite3
from typing import Dict, List, Tuple, Optional
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the shared SQLite ontology store
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "kibo_state.db")

# =========================================================================
# DATA LAYER: Known & Discoverable Entities
# =========================================================================
BASE_LAWS = {
    "PHIPA (ON)": {"name": "Personal Health Information Protection Act", "jurisdiction": "Ontario, Canada", "type": "Privacy Law"},
    "PIPEDA (CA)": {"name": "Personal Information Protection and Electronic Documents Act", "jurisdiction": "Canada (Federal)", "type": "Privacy Law"},
    "CCPA / CPRA (US)": {"name": "California Consumer Privacy Act / California Privacy Rights Act", "jurisdiction": "California, US", "type": "Privacy Law"},
    "GDPR (EU)": {"name": "General Data Protection Regulation", "jurisdiction": "European Union", "type": "Privacy Law"},
    # Add more baseline laws as needed
}

DISCOVERABLE_LAWS = {
    "Health Information Act (AB)": {"name": "Health Information Act", "jurisdiction": "Alberta, Canada", "type": "Health Privacy Law"},
    "Personal Information Protection Act (AB)": {"name": "Personal Information Protection Act", "jurisdiction": "Alberta, Canada", "type": "Privacy Law"},
    "Colorado Privacy Act (CPA)": {"name": "Colorado Privacy Act", "jurisdiction": "Colorado, US", "type": "Privacy Law"},
    "City of Toronto Privacy Ordinance": {"name": "City of Toronto Privacy Ordinance", "jurisdiction": "Toronto, ON", "type": "Municipal Privacy Law"},
}

PRIVACY_TORTS = {
    "US Intrusion upon seclusion": {"name": "Intrusion upon seclusion", "jurisdiction": "United States", "type": "Privacy Tort"},
    "Canada Public disclosure of private facts": {"name": "Public disclosure of private facts", "jurisdiction": "Canada", "type": "Privacy Tort"},
    "EU Infringement of personality rights": {"name": "Infringement of personality rights", "jurisdiction": "European Union", "type": "Privacy Tort"},
}

PENALTIES = {
    "OPC (Federal)": {"name": "Office of the Privacy Commissioner of Canada", "jurisdiction": "Canada (Federal)", "type": "Regulator Penalty", "max": "CAD 100k/violation"},
    "FTC": {"name": "Federal Trade Commission", "jurisdiction": "United States", "type": "Regulator Penalty", "max": "$43,792/violation"},
    "EU DPA": {"name": "European Data Protection Authority", "jurisdiction": "European Union", "type": "Regulator Penalty", "max": "4% global turnover OR €20M"},
}

CROSS_BORDER_AGREEMENTS = {
    "CETA (Canada-EU)": {"name": "Comprehensive Economic and Trade Agreement", "jurisdiction": "Canada-EU", "type": "Cross-Border Data Framework"},
    "USMCA (US-Mexico-Canada)": {"name": "United States-Mexico-Canada Agreement", "jurisdiction": "US-CAN-MEX", "type": "Cross-Border Data Framework"},
}

# =========================================================================
# DISCOVERY ENGINE
# =========================================================================
class ComplianceDiscoveryEngine:
    def __init__(self):
        self.known = {**BASE_LAWS, **DISCOVERABLE_LAWS}
        self.torts = PRIVACY_TORTS
        self.penalties = PENALTIES
        self.agreements = CROSS_BORDER_AGREEMENTS
        
    def discover_for_jurisdiction(self, jurisdiction: str) -> Dict:
        """Discover relevant laws, torts, penalties, and agreements for a given jurisdiction."""
        logger.info(f"🔍 Discovering compliance landscape for: {jurisdiction}")
        
        region = jurisdiction.lower()
        results = {"laws": [], "torts": [], "penalties": [], "agreements": []}
        
        # 1. Discover Laws
        for key, info in self.known.items():
            if info["jurisdiction"].lower() in region or region in info["jurisdiction"].lower():
                results["laws"].append({**info, "discovery_method": "Jurisdiction Match"})
                
        # 2. Discover Torts based on region
        for key, info in self.torts.items():
            if "us" in region and "united states" in info["jurisdiction"].lower():
                results["torts"].append({**info, "discovery_method": "Regional Tort Mapping"})
            elif "canada" in region and "canada" in info["jurisdiction"].lower():
                results["torts"].append({**info, "discovery_method": "Regional Tort Mapping"})
            elif ("eu" in region or "european union" in region) and "european union" in info["jurisdiction"].lower():
                results["torts"].append({**info, "discovery_method": "Regional Tort Mapping"})
                
        # 3. Discover Penalties
        for key, info in self.penalties.items():
            if info["jurisdiction"].lower() in region or region in info["jurisdiction"].lower():
                results["penalties"].append({**info, "discovery_method": "Regulatory Mapping"})
                
        # 4. Discover Cross-Border Agreements
        for key, info in self.agreements.items():
            if info["jurisdiction"] in jurisdiction or jurisdiction.split(",")[0].upper() in info["jurisdiction"]:
                results["agreements"].append({**info, "discovery_method": "Treaty Matching"})
                
        # Fallback: if no specific matches, add global defaults for testing robustness
        if not results["laws"] and not results["penalties"]:
            logger.warning(f"⚠️ No direct matches for '{jurisdiction}'. Adding baseline regional entities.")
            if "us" in region or "canada" in region:
                results["penalties"].append(self.penalties.get("FTC", {}))
            if "eu" in region:
                results["penalties"].append(self.penalties.get("EU DPA", {}))
                
        return results

# =========================================================================
# GRAPHVIZ UPGRADER
# =========================================================================
class GraphvizUpgrader:
    def __init__(self, base_template_path: str):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
            
        self.generated_nodes = {}  # {id: node_string}
        self.generated_edges = []  # [edge_string]
        self.counters = {"H1": 0, "T": 0, "Pen": 0, "Ag": 0}
        
    def _escape_label(self, text: str) -> str:
        """Escape special characters for Graphviz labels."""
        return text.replace('"', '\\"').replace('\n', '\\n')
        
    def _gen_id(self, prefix: str) -> str:
        nid = f"{prefix}_DISC_{self.counters[prefix]:03d}"
        self.counters[prefix] += 1
        return nid
        
    def process_discovery(self, jurisdiction: str, data: Dict):
        """Process discovered entities and generate graph nodes/edges."""
        
        # --- NEW LAWS -> Layer 1 (Statutory Frameworks) ---
        for law in data.get("laws", []):
            nid = self._gen_id("H1")
            label = self._escape_label(f"Framework:\n{law['name']}\n({law['jurisdiction']})")
            self.generated_nodes[nid] = f'{nid} [label="{label}", style=filled, fillcolor="#e6f3ff", color="#003366", shape=box];'
            
            # Connect to governance controls
            for ctrl in ["H2_Gov_Policy", "H2_Gov_Training", "H2_Gov_Vendor", "H2_Gov_Monitoring"]:
                self.generated_edges.append(f'{nid} -> {ctrl};')
                
            # Connect to outputs
            for out in ["Out_PrivacyNotice", "Out_TrainingRecord", "Out_VendorAgreement", "Out_AuditEvidence"]:
                self.generated_edges.append(f'{nid} -> {out};')
                
            # Map to jurisdiction-specific penalty/regulator
            if "canada" in law["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_OPC_Fed;')
            elif "us" in law["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_FTC;')
            elif "eu" in law["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_EU_DPA;')
                
        # --- NEW TORTS -> Layer 1.5 (Privacy Torts) ---
        for tort in data.get("torts", []):
            nid = self._gen_id("T")
            label = self._escape_label(f"{tort['type']}:\n{tort['name']}\n({tort['jurisdiction']})")
            self.generated_nodes[nid] = f'{nid} [label="{label}", style=filled, fillcolor="#fff4e6", color="#cc5500", shape=box];'
            
            # Connect to governance & penalties
            for ctrl in ["H2_Gov_Policy", "H2_Gov_Training"]:
                self.generated_edges.append(f'{nid} -> {ctrl};')
                
            if "us" in tort["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_FTC;')
            elif "canada" in tort["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_OPC_Fed;')
            elif "eu" in tort["jurisdiction"].lower():
                self.generated_edges.append(f'{nid} -> Pen_EU_DPA;')
                
        # --- NEW PENALTIES -> Layer 3.5 (Penalty & Infraction Mapping) ---
        for pen in data.get("penalties", []):
            nid = self._gen_id("Pen")
            max_pen = pen.get("max", "Variable")
            label = self._escape_label(f"Penalty:\n{pen['name']}\nUp to {max_pen}")
            self.generated_nodes[nid] = f'{nid} [label="{label}", style=filled, fillcolor="#ffe6e6", color="#990000", shape=box];'
            
            # Connect to output artefacts
            for out in ["Out_FineNotice", "Out_CorrectiveOrder", "Out_CeaseDesist", "Out_RemediationPlan"]:
                self.generated_edges.append(f'{nid} -> {out};')
                
        # --- NEW AGREEMENTS -> Cross-Border Layer (Integrated near Layer 1) ---
        for ag in data.get("agreements", []):
            nid = self._gen_id("Ag")
            label = self._escape_label(f"Framework:\n{ag['name']}\n({ag['jurisdiction']})")
            self.generated_nodes[nid] = f'{nid} [label="{label}", style=filled, fillcolor="#e6ffea", color="#006633", shape=box];'
            
            # Agreements typically bridge jurisdictions or trigger cross-border controls
            for ctrl in ["H2_Gov_Vendor", "H2_Gov_Monitoring"]:
                self.generated_edges.append(f'{nid} -> {ctrl};')
            self.generated_edges.append(f'{nid} -> Out_TIA_SCC [style=dotted, label="Cross-Border Data Flow"];')

    def compile_updated_graph(self) -> str:
        """Merge generated nodes and edges into the base template."""
        graph = self.template
        
        # 1. Insert new Law Nodes before "/* ---------- NEW STATUTES FROM PROVIDED LIST ---------- */"
        law_nodes = [n for n in self.generated_nodes.values() if n.startswith("H1_")]
        if law_nodes:
            marker = "    /* ---------- NEW STATUTES FROM PROVIDED LIST ---------- */"
            pos = graph.find(marker)
            if pos != -1:
                insertion = "\n".join(law_nodes) + "\n    "
                graph = graph[:pos] + insertion + graph[pos:]
                
        # 2. Insert new Tort Nodes before "/* ---- EU‑style Torts */"
        tort_nodes = [n for n in self.generated_nodes.values() if n.startswith("T_DISC_")]
        if tort_nodes:
            marker = "        /* ---- EU‑style Torts */"
            pos = graph.find(marker)
            if pos != -1:
                insertion = "\n".join(tort_nodes) + "\n    "
                graph = graph[:pos] + insertion + graph[pos:]
                
        # 3. Insert new Penalty Nodes before "/* Optional sector‑specific US health penalty */"
        pen_nodes = [n for n in self.generated_nodes.values() if n.startswith("Pen_DISC_")]
        if pen_nodes:
            marker = "        /* Optional sector‑specific US health penalty (HHS) – kept for completeness */"
            pos = graph.find(marker)
            if pos != -1:
                insertion = "\n".join(pen_nodes) + "\n    "
                graph = graph[:pos] + insertion + graph[pos:]
                
        # 4. Insert new Agreement Nodes after "/* Sector‑Specific Overlays */"
        ag_nodes = [n for n in self.generated_nodes.values() if n.startswith("Ag_")]
        if ag_nodes:
            marker = "    /* Sector‑Specific Overlays */"
            pos = graph.find(marker)
            if pos != -1:
                insertion = "\n".join(ag_nodes) + "\n    "
                graph = graph[:pos] + insertion + graph[pos:]
                
        # 5. Append new edges before style highlights section
        new_edges_str = "\n    // =============================== DYNAMIC COMPLIANCE EDGES ==================================\n"
        new_edges_str += "\n".join(self.generated_edges)
        
        highlight_marker = "    // ==============================================================\n    // OPTIONAL: STYLE HIGHLIGHTS FOR URGENT ACTIONS\n    // =============================================================="
        pos = graph.find(highlight_marker)
        if pos != -1:
            graph = graph[:pos] + new_edges_str + "\n\n" + graph[pos:]
            
        return graph

    def sync_to_db(self):
        """Write all discovered nodes and edges into kibo_state.db so the
        live ontology store stays in sync with the Graphviz diagram."""
        if not os.path.exists(DB_FILE):
            logger.warning(f"kibo_state.db not found at {DB_FILE} — skipping DB sync.")
            return

        # Class-prefix to ontology class mapping (mirrors legalnet_grow_agent)
        PREFIX_CLASS = {
            "H1_": "LegalFramework",
            "T_": "PrivacyTort",
            "Pen_": "PenaltyExposure",
            "Ag_": "CrossBorderFramework",
        }

        def resolve_class(node_id: str) -> str:
            for prefix, cls in PREFIX_CLASS.items():
                if node_id.startswith(prefix):
                    return cls
            return "ComplianceObligation"

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        inserted_nodes = 0
        inserted_edges = 0

        for node_id, node_gv in self.generated_nodes.items():
            # Extract label from Graphviz string: label="..."
            label_match = re.search(r'label="([^"]+)"', node_gv)
            label = label_match.group(1).replace("\\n", " ").strip() if label_match else node_id
            cls = resolve_class(node_id)
            cursor.execute(
                "INSERT OR REPLACE INTO ontology_instances "
                "(instance_id, class_id, label, properties_json) VALUES (?, ?, ?, ?)",
                (node_id, cls, label, json.dumps({"source": "Ontology_builder", "discovered": True}))
            )
            inserted_nodes += 1

        for edge_str in self.generated_edges:
            # Parse: SRC -> DST; (optional style/label attrs)
            m = re.match(r'(\w+)\s*->\s*(\w+)', edge_str)
            if m:
                src, dst = m.group(1), m.group(2)
                cursor.execute(
                    "INSERT OR REPLACE INTO ontology_edges "
                    "(source_id, target_id, predicate) VALUES (?, ?, ?)",
                    (src, dst, "linksTo")
                )
                inserted_edges += 1

        # Log the sync event to the change log
        if inserted_nodes or inserted_edges:
            cursor.execute(
                "INSERT INTO ontology_change_log (proposed_by, reason, change_details_json) "
                "VALUES (?, ?, ?)",
                (
                    "Ontology_builder",
                    "Compliance discovery sync from Ontology_builder.py",
                    json.dumps({"nodes_synced": inserted_nodes, "edges_synced": inserted_edges})
                )
            )

        conn.commit()
        conn.close()
        logger.info(f"DB sync complete: {inserted_nodes} nodes, {inserted_edges} edges written to kibo_state.db.")

# =========================================================================
# MAIN EXECUTION
# =========================================================================
def main():
    base_gv_path = "EnterpriseComplianceNeuralNet.gv"  # Ensure this file exists with your original diagram
    
    print("🚀 Initializing Compliance Discovery & Graph Updater...")
    
    # Initialize engines
    discovery = ComplianceDiscoveryEngine()
    updater = GraphvizUpgrader(base_gv_path)
    
    target_jurisdictions = [
        "Alberta, Canada",
        "Colorado, United States", 
        "European Union",
        "City of Toronto, Ontario"
    ]
    
    discovered_count = 0
    
    for jur in target_jurisdictions:
        time.sleep(0.5) # Responsible polling
        data = discovery.discover_for_jurisdiction(jur)
        
        print(f"\n📊 Found {len(data['laws'])} laws, {len(data['torts'])} torts, "
              f"{len(data['penalties'])} penalties, {len(data['agreements'])} agreements in {jur}")
              
        if data["laws"] or data["torts"] or data["penalties"] or data["agreements"]:
            updater.process_discovery(jur, data)
            discovered_count += 1
            
    print(f"\n✅ Processed {discovered_count} jurisdictions. Generating updated graph...")
    
    # Compile & Save
    updated_graph = updater.compile_updated_graph()
    output_path = "EnterpriseComplianceNeuralNet_Updated.gv"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(updated_graph)
        
    print(f"💾 Updated graph saved to: {output_path}")
    print("📋 Render with: dot -Tpng EnterpriseComplianceNeuralNet_Updated.gv -o updated_compliance.png")

    # --- Sync discovered entities to kibo_state.db ---
    print("\n💾 Syncing discovered entities to kibo_state.db...")
    updater.sync_to_db()
    print("✅ Database sync complete.")

if __name__ == "__main__":
    # Create a placeholder base file if it doesn't exist (for demo purposes)
    if not os.path.exists("EnterpriseComplianceNeuralNet.gv"):
        print("⚠️ Base graph file 'EnterpriseComplianceNeuralNet.gv' not found.")
        print("   Please place your original diagram content in this file and re-run.")
    else:
        main()
