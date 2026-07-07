from datetime import datetime
import csv
import json
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from core.audit.audit_service import AuditService
from core.models.audit_log import AuditLog, DataAccessLog

class EvidenceExporter:
    def __init__(self, audit_service: AuditService):
        self.audit_service = audit_service
        self.db = audit_service.db
        
    async def export_audit_trail_csv(
        self,
        entity_type: str,
        entity_id: str,
        output_path: str
    ):
        """Export audit trail as CSV for compliance audits"""
        logs = await self.audit_service.get_entity_audit_trail(
            entity_type, entity_id
        )
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'user_id', 'user_email', 'user_role', 'action', 'changes', 'reason'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for log in logs:
                writer.writerow({
                    'timestamp': log.created_at.isoformat() if isinstance(log.created_at, datetime) else str(log.created_at),
                    'user_id': log.user_id or '',
                    'user_email': log.user_email or '',
                    'user_role': log.user_role or '',
                    'action': log.action,
                    'changes': json.dumps(log.changes) if log.changes else '',
                    'reason': log.reason or ''
                })
                
    async def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """Generate compliance report with audit summaries"""
        # Count assessments created/approved/rejected from AuditLog
        assessment_created_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.entity_type == 'Assessment',
            AuditLog.action == 'CREATE',
            AuditLog.created_at.between(start_date, end_date)
        )
        assessment_approved_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.entity_type == 'Assessment',
            AuditLog.action.in_(['APPROVED', 'APPROVE']),
            AuditLog.created_at.between(start_date, end_date)
        )
        assessment_rejected_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.entity_type == 'Assessment',
            AuditLog.action.in_(['REJECTED', 'REJECT']),
            AuditLog.created_at.between(start_date, end_date)
        )
        
        # Count risks created/mitigated
        risk_created_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.entity_type == 'Risk',
            AuditLog.action == 'CREATE',
            AuditLog.created_at.between(start_date, end_date)
        )
        risk_mitigated_stmt = select(func.count(AuditLog.id)).where(
            AuditLog.entity_type == 'Risk',
            AuditLog.action.in_(['MITIGATED', 'MITIGATE']),
            AuditLog.created_at.between(start_date, end_date)
        )
        
        # Data access summary
        total_access_stmt = select(func.count(DataAccessLog.id)).where(
            DataAccessLog.created_at.between(start_date, end_date)
        )
        
        total_created = self.db.execute(assessment_created_stmt).scalar() or 0
        total_approved = self.db.execute(assessment_approved_stmt).scalar() or 0
        total_rejected = self.db.execute(assessment_rejected_stmt).scalar() or 0
        
        total_risks_created = self.db.execute(risk_created_stmt).scalar() or 0
        total_risks_mitigated = self.db.execute(risk_mitigated_stmt).scalar() or 0
        
        total_accesses = self.db.execute(total_access_stmt).scalar() or 0
        
        # Get details lists
        assessments_stmt = select(AuditLog).where(
            AuditLog.entity_type == 'Assessment',
            AuditLog.created_at.between(start_date, end_date)
        ).order_by(AuditLog.created_at.desc()).limit(50)
        assessments = self.db.execute(assessments_stmt).scalars().all()
        
        risks_stmt = select(AuditLog).where(
            AuditLog.entity_type == 'Risk',
            AuditLog.created_at.between(start_date, end_date)
        ).order_by(AuditLog.created_at.desc()).limit(50)
        risks = self.db.execute(risks_stmt).scalars().all()
        
        report = {
            'report_period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'assessments': {
                'total_created': total_created,
                'total_approved': total_approved,
                'total_rejected': total_rejected,
                'list': [
                    {
                        'id': log.entity_id,
                        'action': log.action,
                        'user': log.user_id,
                        'timestamp': log.created_at.isoformat() if isinstance(log.created_at, datetime) else str(log.created_at)
                    }
                    for log in assessments
                ]
            },
            'risks': {
                'total_created': total_risks_created,
                'total_mitigated': total_risks_mitigated,
                'list': [
                    {
                        'id': log.entity_id,
                        'action': log.action,
                        'user': log.user_id,
                        'timestamp': log.created_at.isoformat() if isinstance(log.created_at, datetime) else str(log.created_at)
                    }
                    for log in risks
                ]
            },
            'access_summary': {
                'total_accesses': total_accesses,
                'by_user': {},
                'by_entity_type': {}
            }
        }
        
        return report
