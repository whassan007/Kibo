def calculate_diff(old: dict, new: dict) -> dict:
    """Calculate what changed between old and new state"""
    if old is None:
        old = {}
    if new is None:
        new = {}
        
    changes = {}
    all_keys = set(old.keys()) | set(new.keys())
    
    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)
        
        if old_val != new_val:
            changes[key] = {
                'old': old_val,
                'new': new_val
            }
            
    return changes if changes else None
