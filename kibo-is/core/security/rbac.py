"""Deny-by-default action policies with tenant and human approval gates."""
from enum import Enum
from fnmatch import fnmatchcase
from fastapi import HTTPException


class Role(str, Enum):
    PUBLIC = "PUBLIC"
    EMPLOYEE = "EMPLOYEE"
    ANALYST = "ANALYST"
    DPO = "DPO"
    CPO = "CPO"
    LEGAL = "LEGAL"
    AUDITOR = "AUDITOR"
    TENANT_ADMIN = "TENANT_ADMIN"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


CONSEQUENTIAL_ACTIONS = frozenset({
    "breach.notify_regulator", "regulation.promote_to_production",
    "dsar.override_exemption", "assessment.approve_high_risk",
})
READ = {"assessment.read", "assessments.read", "risks.read", "controls.read",
        "vendors.read", "reports.read", "regulation.read", "dsar.read"}
ROLE_PERMISSIONS = {
    Role.PUBLIC: {"public.read"},
    Role.EMPLOYEE: {"public.read", "dsar.create", "dsar.read_own", "assessment.create"},
    Role.ANALYST: READ | {"assessment.create", "assessment.update", "assessments.create", "assessments.update", "risks.create", "risks.update", "vendors.create", "vendors.update"},
    Role.DPO: READ | {"assessment.create", "assessment.update", "assessment.approve", "dsar.process", "breach.manage", "breach.notify_regulator", "assessment.approve_high_risk"},
    Role.CPO: READ | CONSEQUENTIAL_ACTIONS | {"assessment.*", "assessments.*", "risks.*", "controls.*", "vendors.*", "reports.export", "dsar.process", "breach.manage"},
    Role.LEGAL: READ | {"dsar.override_exemption", "regulation.promote_to_production", "breach.notify_regulator", "legal.*"},
    Role.AUDITOR: READ | {"audit.read", "audit.export", "reports.export"},
    Role.TENANT_ADMIN: READ | {"users.manage", "settings.configure", "membership.manage"},
    Role.SYSTEM_ADMIN: {"*"},
}


def _role(value):
    value = str(getattr(value, "value", value)).upper()
    return Role({"ADMIN": "TENANT_ADMIN", "VIEWER": "AUDITOR"}.get(value, value))


class ABACPolicyEngine:
    def is_allowed(self, principal, action: str, resource=None, context=None) -> bool:
        resource, context = resource or {}, context or {}
        attr = lambda obj, key, default=None: obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)
        tenant_id = attr(resource, "tenant_id")
        if tenant_id and tenant_id != principal.tenant_id:
            return False
        region = attr(resource, "residency_region")
        if region and region != principal.residency_region:
            return False
        if context.get("required_scope") and context["required_scope"] not in principal.scopes:
            return False
        if action == "dsar.read_own" and attr(resource, "user_id") != principal.user_id:
            return False
        if action in CONSEQUENTIAL_ACTIONS:
            # These records must come from a trusted approval store, never request JSON.
            approvals = context.get("approvals", ())
            approvers = set()
            eligible = {
                "breach.notify_regulator": {Role.CPO, Role.DPO, Role.LEGAL},
                "regulation.promote_to_production": {Role.CPO, Role.LEGAL},
                "dsar.override_exemption": {Role.CPO, Role.LEGAL},
                "assessment.approve_high_risk": {Role.CPO, Role.DPO},
            }[action]
            for approval in approvals:
                if not isinstance(approval, dict):
                    continue
                try:
                    role = _role(approval.get("role", ""))
                except ValueError:
                    continue
                if (approval.get("verified") is True and approval.get("human") is True
                    and approval.get("action") == action
                    and approval.get("tenant_id") == principal.tenant_id
                    and approval.get("resource_id") == attr(resource, "id")
                    and attr(resource, "id") is not None
                    and role in eligible and approval.get("user_id")
                    and approval["user_id"] != principal.user_id):
                    approvers.add(approval["user_id"])
            if len(approvers) < 2:
                return False
        return True

    def enforce(self, principal, action, resource=None, context=None):
        if not self.is_allowed(principal, action, resource, context):
            raise HTTPException(403, "Attribute or human approval policy denied access")
        return True


class RBACPolicyEngine:
    def __init__(self):
        self.abac = ABACPolicyEngine()

    def is_allowed(self, principal, action: str, resource=None, context=None) -> bool:
        action = action.replace(":", ".")
        roles = set()
        for role in principal.roles:
            try:
                roles.add(_role(role))
            except ValueError:
                continue
        allowed = any(fnmatchcase(action, permission)
                      for role in roles for permission in ROLE_PERMISSIONS[role])
        return allowed and self.abac.is_allowed(principal, action, resource, context)

    def enforce(self, principal, action, resource=None, context=None):
        if not self.is_allowed(principal, action, resource, context):
            raise HTTPException(403, "Action requires authorization and applicable human approvals")
        return True

    authorize = enforce
