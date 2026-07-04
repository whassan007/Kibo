from typing import List, Dict, Any

def extract_pia_insights(filenames: List[str], logs: List[str]) -> List[Dict[str, Any]]:
    logs.append("[PIA Extractor] Reviewing uploaded PIAs...")
    extracted_insights = []
    
    for f in filenames:
        if "pia" in f.lower():
            logs.append(f"[PIA Extractor] Found assessment file: {f}")
            extracted_insights.append({
                "project": "Clinical Support Chat Integration",
                "jurisdictions": ["Ontario", "Quebec"],
                "data_types": "Patient PHI, chat transcript logs",
                "confidence": 94.0
            })
            
    return extracted_insights
