from typing import Dict, Any, List

def analyze_profile_gaps(profile: Dict[str, Any], logs: List[str]) -> List[Dict[str, Any]]:
    logs.append("[Gap Detector] Running automated compliance check against PIPEDA & Law 25 rules...")
    gaps = []
    
    # 1. Check for Clinical Transcripts retention conflict (Data Inventory vs Vendor)
    inventory_items = profile.get("data_inventory", [])
    vendors = profile.get("vendors", [])
    
    clinical_inv = next((d for d in inventory_items if d["asset"] == "Clinical Transcripts"), None)
    aselo_vendor = next((v for v in vendors if v["name"] == "Aselo/Twilio"), None)
    
    if clinical_inv and aselo_vendor:
        inv_retention = clinical_inv.get("retention", "")
        vendor_retention = aselo_vendor.get("retention", "")
        
        # Check if there's a conflict
        if "indefinite" in inv_retention.lower() and "90-day" in vendor_retention.lower():
            gaps.append({
                "id": "gap-1",
                "type": "conflict",
                "title": "Retention Conflict on Clinical Transcripts",
                "details": f"Clinical Transcripts show '{inv_retention}' in your inventory, but the Aselo backend rules specify a '{vendor_retention}'. Which retention rule governs?",
                "priority": "high",
                "status": "pending"
            })
            
    # 2. Check for unconfirmed DPA status
    blackbaud = next((v for v in vendors if v["name"] == "Blackbaud"), None)
    if blackbaud:
        dpa = blackbaud.get("dpa_status", "")
        if "review" in dpa.lower() or "unconfirmed" in dpa.lower():
            gaps.append({
                "id": "gap-2",
                "type": "missing",
                "title": "Blackbaud DPA Status Unconfirmed",
                "details": "Blackbaud DPA is listed as under review. Is there a signed DPA on file?",
                "priority": "medium",
                "status": "pending"
            })
            
    # 3. Check for low-confidence governance items
    governance = profile.get("governance", {})
    chair = governance.get("chair_role", {}).get("value", "")
    if chair == "Chief Privacy Officer":
        gaps.append({
            "id": "gap-3",
            "type": "unconfirmed",
            "title": "Confirm CPO as PSR Chairperson",
            "details": "Extracted Chief Privacy Officer as PSR Committee Chair. Confirm accountability allocation?",
            "priority": "low",
            "status": "pending"
        })
        
    logs.append(f"[Gap Detector] Analysis complete. Surfaced {len(gaps)} compliance gap(s).")
    return gaps
