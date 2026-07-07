"""
MODULE 6 – DSAR Workflows
LangGraph-compatible DSAR fulfillment workflow.

Falls back to a simple sequential runner if langgraph is not installed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict
from datetime import datetime


# ─── Workflow State ───────────────────────────────────────────────────────────

class DsarState(TypedDict, total=False):
    request_id: str
    tenant_id: str
    status: str
    scope: Optional[Dict[str, Any]]
    collected_data: Optional[Dict[str, Any]]
    redacted_data: Optional[Dict[str, Any]]
    verification_complete: bool
    package_ready: bool
    package_id: Optional[str]
    delivered: bool
    error: Optional[str]


# ─── Node functions ───────────────────────────────────────────────────────────

def node_verify_subject(
    state: DsarState,
    intake_service,
) -> DsarState:
    """Verify the data subject identity (sets status to scoping on success)."""
    try:
        from core.services.dsar_intake_service import DsarIntakeService
        request = intake_service.get_request(state['request_id'])
        if not request:
            return {**state, 'status': 'error', 'error': 'Request not found'}

        # In a real system, identity verification would be async.
        # Here we auto-advance if already received.
        if request.status in ('received', 'scoping'):
            return {**state, 'status': 'scoping'}
        return {**state, 'status': request.status}
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


def node_determine_scope(
    state: DsarState,
    scope_service,
) -> DsarState:
    """Determine data scope for the request."""
    try:
        scope = scope_service.determine_scope(
            request_id=state['request_id'],
            scope_determined_by='system',
        )
        scope_data = {
            'systems': scope.systems_in_scope if scope else [],
            'categories': scope.data_categories if scope else [],
        }
        return {**state, 'scope': scope_data, 'status': 'collecting'}
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


def node_collect_data(
    state: DsarState,
    collection_service,
) -> DsarState:
    """Collect data from all in-scope systems (stub – integrations hook here)."""
    try:
        # Real implementation would dispatch to system-specific connectors.
        # Stub: return a placeholder payload.
        scope = state.get('scope') or {}
        collected: Dict[str, Any] = {
            'request_id': state['request_id'],
            'total_records': 0,
            'data': {},
        }
        for system in scope.get('systems', []):
            for category in scope.get('categories', []):
                key = f"{system}::{category}"
                collected['data'][key] = []  # Real: query the system here

        return {**state, 'collected_data': collected, 'status': 'redacting'}
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


def node_apply_redactions(
    state: DsarState,
    redaction_service,
) -> DsarState:
    """Apply PII redaction rules to all collected data."""
    try:
        collected = state.get('collected_data') or {}
        redacted = redaction_service.apply_redactions(
            request_id=state['request_id'],
            tenant_id=state['tenant_id'],
            data=collected,
        )
        return {**state, 'redacted_data': redacted, 'status': 'packaging'}
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


def node_prepare_package(
    state: DsarState,
    delivery_service,
) -> DsarState:
    """Assemble and sign the delivery package."""
    try:
        redacted = state.get('redacted_data') or {}
        package = delivery_service.prepare_package(
            request_id=state['request_id'],
            tenant_id=state['tenant_id'],
            redacted_data=redacted,
        )
        return {
            **state,
            'package_ready': True,
            'package_id': package.id,
            'status': 'ready',
        }
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


def node_deliver_data(
    state: DsarState,
    delivery_service,
    intake_service,
) -> DsarState:
    """Mark package as delivered."""
    try:
        request = intake_service.get_request(state['request_id'])
        if not request:
            return {**state, 'status': 'error', 'error': 'Request not found for delivery'}

        delivery_service.deliver_package(
            request_id=state['request_id'],
            delivery_method=request.preferred_delivery or 'email',
            delivery_address=request.requestor_email,
        )
        return {**state, 'delivered': True, 'status': 'delivered'}
    except Exception as exc:
        return {**state, 'status': 'error', 'error': str(exc)}


# ─── Sequential runner (LangGraph fallback) ───────────────────────────────────

class DsarFulfillmentWorkflow:
    """
    Orchestrates the end-to-end DSAR fulfillment pipeline.
    Can be wired to LangGraph StateGraph or run as a plain sequential runner.
    """

    def __init__(
        self,
        intake_service,
        scope_service,
        collection_service,
        redaction_service,
        delivery_service,
    ):
        self.intake_service = intake_service
        self.scope_service = scope_service
        self.collection_service = collection_service
        self.redaction_service = redaction_service
        self.delivery_service = delivery_service

    def run(self, request_id: str, tenant_id: str) -> DsarState:
        """Execute the full DSAR pipeline synchronously."""
        state: DsarState = {
            'request_id': request_id,
            'tenant_id': tenant_id,
            'status': 'received',
            'scope': None,
            'collected_data': None,
            'redacted_data': None,
            'verification_complete': False,
            'package_ready': False,
            'package_id': None,
            'delivered': False,
            'error': None,
        }

        pipeline = [
            lambda s: node_verify_subject(s, self.intake_service),
            lambda s: node_determine_scope(s, self.scope_service),
            lambda s: node_collect_data(s, self.collection_service),
            lambda s: node_apply_redactions(s, self.redaction_service),
            lambda s: node_prepare_package(s, self.delivery_service),
            lambda s: node_deliver_data(s, self.delivery_service, self.intake_service),
        ]

        for step in pipeline:
            state = step(state)
            if state.get('status') == 'error':
                break

        return state


# ─── Optional LangGraph wiring ────────────────────────────────────────────────

def build_langgraph_workflow(services: Dict[str, Any]):
    """
    Build a LangGraph StateGraph if langgraph is available.
    Returns None if the package is not installed.
    """
    try:
        from langgraph.graph import StateGraph, START, END  # type: ignore

        def _verify(state):
            return node_verify_subject(state, services['intake'])

        def _scope(state):
            return node_determine_scope(state, services['scope'])

        def _collect(state):
            return node_collect_data(state, services['collection'])

        def _redact(state):
            return node_apply_redactions(state, services['redaction'])

        def _package(state):
            return node_prepare_package(state, services['delivery'])

        def _deliver(state):
            return node_deliver_data(state, services['delivery'], services['intake'])

        graph = StateGraph(DsarState)
        graph.add_node('verify', _verify)
        graph.add_node('scope', _scope)
        graph.add_node('collect', _collect)
        graph.add_node('redact', _redact)
        graph.add_node('package', _package)
        graph.add_node('deliver', _deliver)

        graph.add_edge(START, 'verify')
        graph.add_edge('verify', 'scope')
        graph.add_edge('scope', 'collect')
        graph.add_edge('collect', 'redact')
        graph.add_edge('redact', 'package')
        graph.add_edge('package', 'deliver')
        graph.add_edge('deliver', END)

        return graph.compile()
    except ImportError:
        return None
