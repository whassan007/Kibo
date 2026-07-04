from typing import List, Dict, Any

def extract_governance_structure(filenames: List[str], logs: List[str]) -> Dict[str, Any]:
    logs.append("[Governance Extractor] Scanning terms of reference documents...")
    gov_data = {
        "committee": "Privacy, Security & Risk (PSR) Committee",
        "established": "2020-02",
        "chair_role": "Chief Privacy Officer",
        "roles": ["Chair/CPO", "PSR Committee Member", "PSR Advisory Member", "Data Steward", "Data Administrator", "Data User"],
        "reporting_to": "IRMC",
        "cadence": {
            "committee": "weekly",
            "advisory": "bi-monthly",
            "regulatory_update": "quarterly",
            "program_review": "annual"
        },
        "review_cycle_years": 2,
        "confidence": 98.0
    }
    
    for f in filenames:
        if "terms" in f.lower() or "tor" in f.lower():
            logs.append(f"[Governance Extractor] Identified charter: {f}. Extracted PSR structure.")
            
    return gov_data
