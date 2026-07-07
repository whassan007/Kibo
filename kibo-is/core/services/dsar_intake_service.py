"""
MODULE 6 – DSAR Workflows
DSAR Intake Service: receive requests, calculate jurisdiction-aware deadlines.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import select

from core.models.dsar_request import (
    DataSubject,
    DataSubjectAccessRequest,
    JURISDICTION_DEADLINES,
)


class DsarIntakeService:
    """Handles DSAR intake: create data subjects, register requests, compute deadlines."""

    def __init__(self, db: Session):
        self.db = db

    # ── Receive a new DSAR ────────────────────────────────────────────────────

    def receive_request(
        self,
        tenant_id: str,
        request_type: str,
        jurisdiction: str,
        identifier_type: str,
        identifier_value: str,
        requestor_email: str,
        received_via: str = 'web_form',
        preferred_delivery: str = 'email',
        assigned_to: Optional[str] = None,
    ) -> DataSubjectAccessRequest:
        """
        Register a new DSAR:
        1. Find or create the DataSubject record.
        2. Auto-calculate deadline from jurisdiction table.
        3. Persist and return the request.
        """
        # Find or create the data subject
        subject = (
            self.db.query(DataSubject)
            .filter(
                DataSubject.tenant_id == tenant_id,
                DataSubject.identifier_type == identifier_type,
                DataSubject.identifier_value == identifier_value,
            )
            .first()
        )
        if not subject:
            subject = DataSubject(
                id=str(uuid4()),
                tenant_id=tenant_id,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
            )
            self.db.add(subject)
            self.db.flush()

        # Calculate deadline
        deadline_days = JURISDICTION_DEADLINES.get(jurisdiction, 30)
        received_at = datetime.utcnow()
        deadline = received_at + timedelta(days=deadline_days)
        days_remaining = deadline_days

        request = DataSubjectAccessRequest(
            id=str(uuid4()),
            tenant_id=tenant_id,
            data_subject_id=subject.id,
            request_type=request_type,
            received_at=received_at,
            received_via=received_via,
            jurisdiction=jurisdiction,
            deadline=deadline,
            days_remaining=days_remaining,
            status='received',
            requestor_email=requestor_email,
            preferred_delivery=preferred_delivery,
            assigned_to=assigned_to,
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    # ── Verification ──────────────────────────────────────────────────────────

    def mark_verified(
        self,
        request_id: str,
        verification_method: str,
        verified_by: Optional[str] = None,
    ) -> Optional[DataSubjectAccessRequest]:
        req = self.db.get(DataSubjectAccessRequest, request_id)
        if not req:
            return None
        subject = self.db.get(DataSubject, req.data_subject_id)
        if subject:
            subject.is_verified = True
            subject.verification_method = verification_method
            subject.verified_at = datetime.utcnow()
            subject.verified_by = verified_by
            self.db.add(subject)
        req.status = 'scoping'
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    # ── Refuse ────────────────────────────────────────────────────────────────

    def refuse_request(
        self,
        request_id: str,
        reason: str,
        justification: str,
    ) -> Optional[DataSubjectAccessRequest]:
        req = self.db.get(DataSubjectAccessRequest, request_id)
        if not req:
            return None
        req.status = 'refused'
        req.refuse_reason = reason
        req.refuse_justification = justification
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_request(self, request_id: str) -> Optional[DataSubjectAccessRequest]:
        return self.db.get(DataSubjectAccessRequest, request_id)

    def list_requests(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[DataSubjectAccessRequest]:
        q = self.db.query(DataSubjectAccessRequest).filter(
            DataSubjectAccessRequest.tenant_id == tenant_id
        )
        if status:
            q = q.filter(DataSubjectAccessRequest.status == status)
        return q.order_by(DataSubjectAccessRequest.deadline.asc()).offset(skip).limit(limit).all()

    def get_overdue_requests(self, tenant_id: str) -> List[DataSubjectAccessRequest]:
        """Return all non-terminal requests past their deadline."""
        now = datetime.utcnow()
        terminal = ('delivered', 'refused')
        return (
            self.db.query(DataSubjectAccessRequest)
            .filter(
                DataSubjectAccessRequest.tenant_id == tenant_id,
                DataSubjectAccessRequest.deadline <= now,
                DataSubjectAccessRequest.status.notin_(terminal),
            )
            .order_by(DataSubjectAccessRequest.deadline.asc())
            .all()
        )

    def get_approaching_deadline(
        self,
        tenant_id: str,
        within_days: int = 5,
    ) -> List[DataSubjectAccessRequest]:
        """Return non-terminal requests with deadline within `within_days` days."""
        now = datetime.utcnow()
        cutoff = now + timedelta(days=within_days)
        terminal = ('delivered', 'refused')
        return (
            self.db.query(DataSubjectAccessRequest)
            .filter(
                DataSubjectAccessRequest.tenant_id == tenant_id,
                DataSubjectAccessRequest.deadline <= cutoff,
                DataSubjectAccessRequest.deadline > now,
                DataSubjectAccessRequest.status.notin_(terminal),
            )
            .order_by(DataSubjectAccessRequest.deadline.asc())
            .all()
        )
