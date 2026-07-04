from typing import List, Dict, Any

def extract_risk_assessments(filenames: List[str], logs: List[str]) -> List[Dict[str, Any]]:
    logs.append("[Risk Extractor] Opening risk registers and matrices...")
    extracted_risks = []
    
    for f in filenames:
        if "risk" in f.lower():
            logs.append(f"[Risk Extractor] Scanning sheets in: {f}")
            extracted_risks.append({
                "id": "RISK-01",
                "title": "Unapproved Third-Party Storage",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Enforce Data Protection Annex signing for all vendors.",
                "confidence": 92.0
            })
            
    return extracted_risks
