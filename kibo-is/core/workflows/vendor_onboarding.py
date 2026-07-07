"""
MODULE 5 – Vendor Risk Management
Vendor onboarding and DPA renewal LangGraph-compatible workflows.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict


# ─── Onboarding state ─────────────────────────────────────────────────────────

class VendorOnboardingState(TypedDict, total=False):
    vendor_id: str
    tenant_id: str
    vendor_name: str
    service_type: str
    assessment_results: Dict[str, Any]
    dpa_status: str
    risk_level: str
    approval_status: str
    error: Optional[str]


# ─── Onboarding nodes ─────────────────────────────────────────────────────────

def node_assess_security(
    state: VendorOnboardingState,
    assessment_service,
) -> VendorOnboardingState:
    """Run security assessment for the vendor."""
    try:
        assessment = assessment_service.create_assessment(
            vendor_id=state['vendor_id'],
            assessment_type='security',
            framework='ISO27001',
            tenant_id=state['tenant_id'],
        )
        # In a real flow the assessment would be completed via human review.
        # Here we record its creation and return.
        results = state.get('assessment_results', {})
        results['security_assessment_id'] = assessment.id
        return {**state, 'assessment_results': results}
    except Exception as exc:
        return {**state, 'error': str(exc)}


def node_assess_privacy(
    state: VendorOnboardingState,
    assessment_service,
) -> VendorOnboardingState:
    """Run privacy assessment for the vendor."""
    try:
        assessment = assessment_service.create_assessment(
            vendor_id=state['vendor_id'],
            assessment_type='privacy',
            framework='Custom',
            tenant_id=state['tenant_id'],
        )
        results = state.get('assessment_results', {})
        results['privacy_assessment_id'] = assessment.id
        return {**state, 'assessment_results': results}
    except Exception as exc:
        return {**state, 'error': str(exc)}


def node_check_dpa(
    state: VendorOnboardingState,
    dpa_service,
) -> VendorOnboardingState:
    """Check if a DPA is required and what its current status is."""
    try:
        dpas = dpa_service.list_by_vendor(
            vendor_id=state['vendor_id'],
            tenant_id=state['tenant_id'],
        )
        executed = [d for d in dpas if d.status == 'executed']
        dpa_status = 'executed' if executed else ('draft' if dpas else 'missing')
        return {**state, 'dpa_status': dpa_status}
    except Exception as exc:
        return {**state, 'error': str(exc)}


def node_approve_vendor(
    state: VendorOnboardingState,
    assessment_service,
) -> VendorOnboardingState:
    """Make the final onboarding approval decision based on risk level."""
    risk_level = state.get('risk_level', 'low')
    if risk_level == 'critical':
        approval_status = 'blocked'
    elif risk_level == 'high':
        approval_status = 'conditional'
    else:
        approval_status = 'approved'
    return {**state, 'approval_status': approval_status}


# ─── Onboarding workflow runner ───────────────────────────────────────────────

class VendorOnboardingWorkflow:
    """Sequential vendor onboarding pipeline."""

    def __init__(self, assessment_service, dpa_service):
        self.assessment_service = assessment_service
        self.dpa_service = dpa_service

    def run(
        self,
        vendor_id: str,
        tenant_id: str,
        vendor_name: str,
        service_type: str,
    ) -> VendorOnboardingState:
        state: VendorOnboardingState = {
            'vendor_id': vendor_id,
            'tenant_id': tenant_id,
            'vendor_name': vendor_name,
            'service_type': service_type,
            'assessment_results': {},
            'dpa_status': 'unknown',
            'risk_level': 'low',
            'approval_status': 'pending',
            'error': None,
        }
        for step in [
            lambda s: node_assess_security(s, self.assessment_service),
            lambda s: node_assess_privacy(s, self.assessment_service),
            lambda s: node_check_dpa(s, self.dpa_service),
            lambda s: node_approve_vendor(s, self.assessment_service),
        ]:
            state = step(state)
            if state.get('error'):
                break
        return state


# ─── DPA renewal state & workflow ─────────────────────────────────────────────

class DPARenewalState(TypedDict, total=False):
    dpa_id: str
    vendor_id: str
    tenant_id: str
    days_until_expiry: int
    notification_sent: bool
    renewal_task_created: bool
    error: Optional[str]


def node_send_notification(
    state: DPARenewalState,
    dpa_service,
) -> DPARenewalState:
    """Trigger expiry notification check for the DPA."""
    try:
        triggered = dpa_service.check_dpa_expiry(tenant_id=state['tenant_id'])
        matched = any(t['dpa_id'] == state['dpa_id'] for t in triggered)
        return {**state, 'notification_sent': matched}
    except Exception as exc:
        return {**state, 'error': str(exc)}


class DPARenewalWorkflow:
    """Sequential DPA renewal workflow."""

    def __init__(self, dpa_service):
        self.dpa_service = dpa_service

    def run(
        self,
        dpa_id: str,
        vendor_id: str,
        tenant_id: str,
        days_until_expiry: int,
    ) -> DPARenewalState:
        state: DPARenewalState = {
            'dpa_id': dpa_id,
            'vendor_id': vendor_id,
            'tenant_id': tenant_id,
            'days_until_expiry': days_until_expiry,
            'notification_sent': False,
            'renewal_task_created': False,
            'error': None,
        }
        state = node_send_notification(state, self.dpa_service)
        return state
