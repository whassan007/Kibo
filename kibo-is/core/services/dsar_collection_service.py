"""
MODULE 6 – DSAR Workflows
DSAR Collection Service: collect data from registered systems for a DSAR request.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.dsar_request import DataSubjectAccessRequest, RequestedDataElement
from core.models.dsar_collection import CollectionTask


class DsarCollectionService:
    """
    Orchestrates data collection across systems for a DSAR.
    Each system integration creates a CollectionTask; results are stored
    in collection_output for downstream redaction.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Task management ───────────────────────────────────────────────────────

    def create_collection_task(
        self,
        request_id: str,
        tenant_id: str,
        system_id: str,
        system_name: str,
        data_category: str,
        collection_method: str = 'database_query',
        query_template: Optional[str] = None,
        assigned_to: Optional[str] = None,
    ) -> CollectionTask:
        task = CollectionTask(
            id=str(uuid4()),
            tenant_id=tenant_id,
            request_id=request_id,
            system_id=system_id,
            system_name=system_name,
            data_category=data_category,
            status='pending',
            collection_method=collection_method,
            query_template=query_template,
            assigned_to=assigned_to,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def start_task(self, task_id: str) -> Optional[CollectionTask]:
        task = self.db.get(CollectionTask, task_id)
        if not task:
            return None
        task.status = 'in_progress'
        task.started_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        return task

    def complete_task(
        self,
        task_id: str,
        records_found: int,
        data_size_mb: float,
        collection_output: Dict[str, Any],
    ) -> Optional[CollectionTask]:
        """Mark task as completed and store collected data."""
        task = self.db.get(CollectionTask, task_id)
        if not task:
            return None
        task.status = 'completed'
        task.records_found = records_found
        task.data_size_mb = data_size_mb
        task.collection_output = collection_output
        task.completed_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        return task

    def fail_task(
        self,
        task_id: str,
        error_message: str,
    ) -> Optional[CollectionTask]:
        task = self.db.get(CollectionTask, task_id)
        if not task:
            return None
        task.status = 'failed'
        task.error_message = error_message
        task.completed_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        return task

    # ── Aggregation ───────────────────────────────────────────────────────────

    def aggregate_collected_data(self, request_id: str) -> Dict[str, Any]:
        """
        Merge all completed collection task outputs for a request
        into a single dict keyed by (system_id, data_category).
        """
        tasks = (
            self.db.query(CollectionTask)
            .filter(
                CollectionTask.request_id == request_id,
                CollectionTask.status == 'completed',
            )
            .all()
        )
        aggregated: Dict[str, Any] = {}
        total_records = 0
        for task in tasks:
            key = f"{task.system_id}::{task.data_category}"
            aggregated[key] = task.collection_output or {}
            total_records += task.records_found or 0

        return {
            'request_id': request_id,
            'total_records': total_records,
            'systems_collected': len(tasks),
            'data': aggregated,
        }

    def is_collection_complete(self, request_id: str) -> bool:
        """Return True only if all tasks are in terminal state (completed or skipped)."""
        pending = (
            self.db.query(CollectionTask)
            .filter(
                CollectionTask.request_id == request_id,
                CollectionTask.status.in_(['pending', 'in_progress']),
            )
            .count()
        )
        return pending == 0

    def list_tasks(self, request_id: str) -> List[CollectionTask]:
        return (
            self.db.query(CollectionTask)
            .filter(CollectionTask.request_id == request_id)
            .order_by(CollectionTask.created_at.asc())
            .all()
        )
