import os
import json
from typing import List, Dict, Any, Optional

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")

class RuleEngine:
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self):
        """Load rules from persistent local JSON storage."""
        if os.path.exists(RULES_FILE):
            try:
                with open(RULES_FILE, "r") as f:
                    self.rules = json.load(f)
            except Exception as e:
                print(f"Error loading rules from {RULES_FILE}: {e}")
                self.rules = []
        else:
            # Seed default demo rules
            self.rules = [
                {
                    "rule_id": "rule-999",
                    "condition": {
                        "client": "FinServe LLC",
                        "type": "Vendor",
                        "jurisdiction": "US"
                    },
                    "action": "auto-approve",
                    "human_reasoning": "Standard SCCs present. Governed by prior DPA."
                }
            ]
            self.save_rules()

    def save_rules(self):
        """Save rules persistently."""
        try:
            with open(RULES_FILE, "w") as f:
                json.dump(self.rules, f, indent=2)
        except Exception as e:
            print(f"Error saving rules to {RULES_FILE}: {e}")

    def add_rule(self, condition: Dict[str, Any], action: str, reasoning: str) -> Dict[str, Any]:
        """Learn and add a new rule."""
        rule_id = f"rule-{len(self.rules) + 1000}"
        new_rule = {
            "rule_id": rule_id,
            "condition": condition,
            "action": action,
            "human_reasoning": reasoning
        }
        self.rules.append(new_rule)
        self.save_rules()
        return new_rule

    def evaluate(self, request_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate request_context against learned rules.
        Returns matching rule if found, otherwise None.
        """
        for rule in self.rules:
            condition = rule.get("condition", {})
            match = True
            for key, val in condition.items():
                # Perform fuzzy/case-insensitive equality match for typical string fields
                req_val = request_context.get(key)
                if req_val is None:
                    match = False
                    break
                if str(req_val).strip().lower() != str(val).strip().lower():
                    match = False
                    break
            if match:
                return rule
        return None
