"""
MODULE 6 – DSAR Workflows
DSAR Redaction Service: apply configurable PII masking rules before delivery.
"""

import re
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.dsar_redaction import RedactionRule, AppliedRedaction

# ─── Built-in redaction patterns ─────────────────────────────────────────────

_BUILTIN_RULES: List[Dict[str, Any]] = [
    {
        'type': 'email_mask',
        'pattern': r'(\w[\w.+-]*)@([\w.-]+\.\w+)',
        'replacement': r'\1***@\2',
        'fields': ['email', 'sender', 'recipient', 'reply_to'],
    },
    {
        'type': 'phone_mask',
        'pattern': r'(\+?[\d\s\-().]{7,})(?=\s|$)',
        'replacement': '***-****',
        'fields': ['phone', 'mobile', 'telephone', 'fax'],
    },
    {
        'type': 'ssn_mask',
        'pattern': r'\d{3}-\d{2}-(\d{4})',
        'replacement': r'***-**-\1',
        'fields': ['ssn', 'social_security', 'sin'],
    },
    {
        'type': 'credit_card_mask',
        'pattern': r'\b(?:\d[ -]?){13,15}\d\b',
        'replacement': '****-****-****-XXXX',
        'fields': ['card_number', 'credit_card', 'payment_card'],
    },
]


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class DsarRedactionService:
    """
    Applies redaction rules to collected data before it is packaged for delivery.
    Logs every applied redaction to AppliedRedaction for compliance audit.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Core redaction ────────────────────────────────────────────────────────

    def apply_redactions(
        self,
        request_id: str,
        tenant_id: str,
        data: Dict[str, Any],
        element_id: Optional[str] = None,
        applied_by: Optional[str] = 'system',
    ) -> Dict[str, Any]:
        """
        Deep-copy `data`, apply all active rules, log each redaction,
        and return the redacted copy.
        """
        redacted = json.loads(json.dumps(data, default=str))  # Deep copy + serialise
        rules = self._get_active_rules()

        for rule in rules:
            redacted = self._apply_rule_to_dict(
                request_id=request_id,
                tenant_id=tenant_id,
                element_id=element_id,
                rule=rule,
                data=redacted,
                applied_by=applied_by,
            )

        return redacted

    def _apply_rule_to_dict(
        self,
        request_id: str,
        tenant_id: str,
        element_id: Optional[str],
        rule: Dict[str, Any],
        data: Dict[str, Any],
        applied_by: Optional[str],
    ) -> Dict[str, Any]:
        """Recursively apply a single rule to a data dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._apply_rule_to_dict(
                    request_id, tenant_id, element_id, rule, value, applied_by
                )
            elif isinstance(value, list):
                result[key] = [
                    self._apply_rule_to_dict(
                        request_id, tenant_id, element_id, rule,
                        item if isinstance(item, dict) else {'_v': item},
                        applied_by,
                    ).get('_v', item) if not isinstance(item, dict) else
                    self._apply_rule_to_dict(
                        request_id, tenant_id, element_id, rule, item, applied_by
                    )
                    for item in value
                ]
            elif isinstance(value, str) and key in rule.get('fields', []):
                redacted_value = re.sub(rule['pattern'], rule['replacement'], value)
                if redacted_value != value:
                    self._log_redaction(
                        request_id=request_id,
                        tenant_id=tenant_id,
                        element_id=element_id,
                        rule_type=rule['type'],
                        field_name=key,
                        original_value=value,
                        redacted_value=redacted_value,
                        applied_by=applied_by,
                    )
                result[key] = redacted_value
            else:
                result[key] = value
        return result

    def _log_redaction(
        self,
        request_id: str,
        tenant_id: str,
        element_id: Optional[str],
        rule_type: str,
        field_name: str,
        original_value: str,
        redacted_value: str,
        applied_by: Optional[str],
    ) -> None:
        log = AppliedRedaction(
            id=str(uuid4()),
            tenant_id=tenant_id,
            request_id=request_id,
            element_id=element_id,
            field_name=field_name,
            original_value_hash=_sha256(original_value),
            redacted_value=redacted_value,
            justification=f'Matched rule: {rule_type}',
            applied_at=datetime.utcnow(),
            applied_by=applied_by,
        )
        self.db.add(log)
        # Flush (not commit) so we commit once in the caller
        self.db.flush()

    # ── Rules management ──────────────────────────────────────────────────────

    def _get_active_rules(self) -> List[Dict[str, Any]]:
        """
        Return DB-configured rules first (if any), then fall back to builtins.
        """
        db_rules = (
            self.db.query(RedactionRule)
            .filter(RedactionRule.is_active == True)
            .order_by(RedactionRule.priority.desc())
            .all()
        )
        if db_rules:
            return [
                {
                    'type': r.rule_type,
                    'pattern': r.pattern,
                    'replacement': r.replacement,
                    'fields': r.applies_to_fields or [],
                }
                for r in db_rules
            ]
        return _BUILTIN_RULES

    def create_rule(
        self,
        tenant_id: str,
        name: str,
        rule_type: str,
        pattern: str,
        replacement: str,
        fields: List[str],
        categories: Optional[List[str]] = None,
        created_by: Optional[str] = None,
    ) -> RedactionRule:
        rule = RedactionRule(
            id=str(uuid4()),
            tenant_id=tenant_id,
            name=name,
            rule_type=rule_type,
            pattern=pattern,
            replacement=replacement,
            applies_to_fields=fields,
            applies_to_categories=categories or [],
            is_active=True,
            created_by=created_by,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def list_rules(self, tenant_id: str) -> List[RedactionRule]:
        return (
            self.db.query(RedactionRule)
            .filter(RedactionRule.tenant_id == tenant_id)
            .all()
        )

    def list_applied_redactions(self, request_id: str) -> List[AppliedRedaction]:
        return (
            self.db.query(AppliedRedaction)
            .filter(AppliedRedaction.request_id == request_id)
            .all()
        )
