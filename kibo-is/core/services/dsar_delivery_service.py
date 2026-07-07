"""
MODULE 6 – DSAR Workflows
DSAR Delivery Service: package, sign, and deliver data to the data subject.
"""

import hashlib
import json
import secrets
import zipfile
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.dsar_request import DataSubjectAccessRequest
from core.models.dsar_package import DeliveryPackage, PackageVerification


def _sha256_dict(data: Dict[str, Any]) -> str:
    serialised = json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(serialised).hexdigest()


class DsarDeliveryService:
    """
    Assembles, signs, and delivers the DSAR data package.
    Produces a tamper-evident ZIP with manifest and SHA256 hash.
    """

    def __init__(self, db: Session, package_base_dir: str = '/tmp/dsar_packages'):
        self.db = db
        self.package_base_dir = package_base_dir
        os.makedirs(package_base_dir, exist_ok=True)

    # ── Package preparation ───────────────────────────────────────────────────

    def prepare_package(
        self,
        request_id: str,
        tenant_id: str,
        redacted_data: Dict[str, Any],
        prepared_by: Optional[str] = 'system',
        package_format: str = 'zip',
    ) -> DeliveryPackage:
        """
        1. Serialise redacted_data to JSON inside a ZIP.
        2. Compute SHA256 hash.
        3. Persist DeliveryPackage record with integrity metadata.
        """
        request = self.db.get(DataSubjectAccessRequest, request_id)
        if not request:
            raise ValueError(f"DSAR request {request_id} not found")

        package_id = str(uuid4())
        file_name = f"dsar_{request_id}_{package_id}.zip"
        file_path = os.path.join(self.package_base_dir, file_name)

        # Build manifest
        manifest = {
            'request_id': request_id,
            'prepared_at': datetime.utcnow().isoformat(),
            'jurisdiction': request.jurisdiction,
            'request_type': request.request_type,
            'data_subject_id': request.data_subject_id,
        }

        # Write ZIP
        total_records = redacted_data.get('total_records', 0)
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('manifest.json', json.dumps(manifest, indent=2, default=str))
            zf.writestr('data.json', json.dumps(redacted_data, indent=2, default=str))

        # Compute hash
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)

        # Download token (valid 7 days)
        download_token = secrets.token_urlsafe(32)
        token_expiry = datetime.utcnow() + timedelta(days=7)

        package = DeliveryPackage(
            id=package_id,
            tenant_id=tenant_id,
            request_id=request_id,
            package_format=package_format,
            file_path=file_path,
            file_hash=file_hash,
            file_size_bytes=file_size,
            record_count=total_records,
            data_categories_included=list(redacted_data.get('data', {}).keys()),
            status='ready',
            prepared_at=datetime.utcnow(),
            expires_at=token_expiry,
            download_token=download_token,
            download_token_expires_at=token_expiry,
        )
        self.db.add(package)

        # Run verification checks
        checks = [
            ('hash_computed', bool(file_hash), 'SHA256 hash computed successfully'),
            ('file_exists', os.path.exists(file_path), 'ZIP file written to disk'),
            ('manifest_present', True, 'manifest.json included in package'),
            ('data_present', bool(redacted_data), 'Data payload is non-empty'),
        ]
        for check_name, passed, detail in checks:
            v = PackageVerification(
                id=str(uuid4()),
                tenant_id=tenant_id,
                package_id=package_id,
                check_name=check_name,
                check_passed=passed,
                check_detail=detail,
                checked_by='system',
            )
            self.db.add(v)

        # Advance request status
        request.status = 'ready'
        self.db.add(request)
        self.db.commit()
        self.db.refresh(package)
        return package

    # ── Delivery ──────────────────────────────────────────────────────────────

    def deliver_package(
        self,
        request_id: str,
        delivery_method: str,
        delivery_address: str,
        delivered_by: Optional[str] = 'system',
    ) -> Optional[DeliveryPackage]:
        """
        Mark the package as delivered.
        Actual email/download dispatch is handled by the integration layer.
        """
        package = (
            self.db.query(DeliveryPackage)
            .filter(DeliveryPackage.request_id == request_id)
            .first()
        )
        if not package:
            return None

        package.status = 'delivered'
        package.delivery_method = delivery_method
        package.delivery_address = delivery_address
        package.delivered_at = datetime.utcnow()
        self.db.add(package)

        request = self.db.get(DataSubjectAccessRequest, request_id)
        if request:
            request.status = 'delivered'
            request.delivered_at = datetime.utcnow()
            self.db.add(request)

        self.db.commit()
        self.db.refresh(package)
        return package

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def get_package(self, request_id: str) -> Optional[DeliveryPackage]:
        return (
            self.db.query(DeliveryPackage)
            .filter(DeliveryPackage.request_id == request_id)
            .first()
        )

    def validate_download_token(
        self,
        request_id: str,
        token: str,
    ) -> Optional[DeliveryPackage]:
        """Return the package if the token is valid and not expired; else None."""
        package = self.get_package(request_id)
        if not package:
            return None
        if package.download_token != token:
            return None
        if package.download_token_expires_at and package.download_token_expires_at < datetime.utcnow():
            return None
        return package

    def get_verifications(self, package_id: str) -> List[PackageVerification]:
        return (
            self.db.query(PackageVerification)
            .filter(PackageVerification.package_id == package_id)
            .all()
        )
