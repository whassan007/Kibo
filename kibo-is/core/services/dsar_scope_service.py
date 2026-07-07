"""
MODULE 6 – DSAR Workflows
DSAR Scope Service: determine which systems/data categories to include.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.dsar_request import (
    DataSubjectAccessRequest,
    DsarScope,
    RequestedDataElement,
)

# Default data categories to always include when in scope
DEFAULT_DATA_CATEGORIES = [
    'PersonalInformation',
    'ContactDetails',
    'PaymentInfo',
    'LocationData',
    'BehavioralData',
]


class DsarScopeService:
    """Determines which systems and data categories are in scope for a DSAR."""

    def __init__(self, db: Session):
        self.db = db

    def determine_scope(
        self,
        request_id: str,
        systems_override: Optional[List[str]] = None,
        categories_override: Optional[List[str]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        scope_determined_by: Optional[str] = None,
    ) -> Optional[DsarScope]:
        """
        Determine scope for a DSAR request.
        Uses override lists if provided; otherwise falls back to defaults.
        Creates RequestedDataElement records per (system, category) pair.
        """
        request = self.db.get(DataSubjectAccessRequest, request_id)
        if not request:
            return None

        systems = systems_override or []
        categories = categories_override or DEFAULT_DATA_CATEGORIES

        scope = DsarScope(
            id=str(uuid4()),
            tenant_id=request.tenant_id,
            request_id=request_id,
            systems_in_scope=systems,
            data_categories=categories,
            from_date=from_date,
            to_date=to_date,
            scope_determined_at=datetime.utcnow(),
            scope_determined_by=scope_determined_by,
        )
        self.db.add(scope)

        # Create collection tasks for each (system, category) pair
        for system_id in systems:
            for category in categories:
                element = RequestedDataElement(
                    id=str(uuid4()),
                    tenant_id=request.tenant_id,
                    request_id=request_id,
                    system_id=system_id,
                    data_category=category,
                    field_name='all',
                    status='pending',
                )
                self.db.add(element)

        # Advance request status
        request.status = 'scoping'
        self.db.add(request)
        self.db.commit()
        self.db.refresh(scope)
        return scope

    def get_scope(self, request_id: str) -> Optional[DsarScope]:
        return (
            self.db.query(DsarScope)
            .filter(DsarScope.request_id == request_id)
            .first()
        )

    def list_pending_elements(self, request_id: str) -> List[RequestedDataElement]:
        return (
            self.db.query(RequestedDataElement)
            .filter(
                RequestedDataElement.request_id == request_id,
                RequestedDataElement.status == 'pending',
            )
            .all()
        )

    def mark_element_collected(
        self,
        element_id: str,
        record_count: int,
        data_size_mb: float,
        collected_by: Optional[str] = None,
    ) -> Optional[RequestedDataElement]:
        element = self.db.get(RequestedDataElement, element_id)
        if not element:
            return None
        element.status = 'collected'
        element.actual_record_count = record_count
        element.actual_data_size_mb = data_size_mb
        element.collected_at = datetime.utcnow()
        element.collected_by = collected_by
        self.db.add(element)
        self.db.commit()
        return element
