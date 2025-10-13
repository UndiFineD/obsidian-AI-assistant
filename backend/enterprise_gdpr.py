# Enterprise GDPR Compliance Module
# Implements data protection and privacy controls for GDPR compliance

import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataCategory(Enum):
    PERSONAL_DATA = "personal_data"  # Names, emails, user IDs
    SENSITIVE_DATA = "sensitive_data"  # Health, biometric, etc.
    DOCUMENT_CONTENT = "document_content"  # User documents and notes
    USAGE_DATA = "usage_data"  # Analytics and system logs
    SYSTEM_DATA = "system_data"  # Configuration and metadata


class ProcessingPurpose(Enum):
    SERVICE_PROVISION = "service_provision"  # Core AI assistant functionality
    ANALYTICS = "analytics"  # Usage analytics and insights
    SECURITY = "security"  # Security monitoring and audit
    SUPPORT = "support"  # Customer support and troubleshooting
    MARKETING = "marketing"  # Marketing and communications


class LegalBasis(Enum):
    CONSENT = "consent"  # User consent (Art. 6(1)(a))
    CONTRACT = "contract"  # Performance of contract (Art. 6(1)(b))
    LEGAL_OBLIGATION = "legal_obligation"  # Legal obligation (Art. 6(1)(c))
    LEGITIMATE_INTEREST = "legitimate_interest"  # Legitimate interest (Art. 6(1)(f))


@dataclass
class DataProcessingRecord:
    """Record of data processing activities (Art. 30 GDPR)"""

    processing_id: str
    data_category: DataCategory
    purpose: ProcessingPurpose
    legal_basis: LegalBasis
    data_subjects: str  # Description of data subject categories
    data_types: List[str]  # Types of personal data processed
    recipients: List[str]  # Categories of recipients
    retention_period: str  # Data retention period
    security_measures: List[str]  # Security measures implemented
    created_at: datetime
    updated_at: datetime


@dataclass
class ConsentRecord:
    """User consent tracking"""

    consent_id: str
    user_id: str
    tenant_id: str
    purpose: ProcessingPurpose
    granted: bool
    granted_at: datetime
    withdrawn_at: Optional[datetime] = None
    consent_text: str = ""
    version: str = "1.0"


@dataclass
class DataSubjectRequest:
    """Data subject rights request (Art. 15-22 GDPR)"""

    request_id: str
    user_id: str
    tenant_id: str
    request_type: str  # access, rectification, erasure, portability, etc.
    status: str  # pending, in_progress, completed, rejected
    submitted_at: datetime
    completed_at: Optional[datetime] = None
    details: str = ""
    response_data: Optional[Dict[str, Any]] = None


class GDPRComplianceManager:
    """GDPR compliance management system"""

    def __init__(self):
        self.processing_records: Dict[str, DataProcessingRecord] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        self.data_retention_policies: Dict[DataCategory, int] = {}  # days
        self._initialize_default_records()

    def _initialize_default_records(self):
        """Initialize default processing records"""
        # Core service provision
        self.register_processing_activity(
            DataProcessingRecord(
                processing_id="core_service",
                data_category=DataCategory.DOCUMENT_CONTENT,
                purpose=ProcessingPurpose.SERVICE_PROVISION,
                legal_basis=LegalBasis.CONTRACT,
                data_subjects="Users of AI assistant service",
                data_types=["document text", "search queries", "AI responses"],
                recipients=["Internal AI processing systems"],
                retention_period="As long as user account exists",
                security_measures=[
                    "Encryption at rest",
                    "Access controls",
                    "Audit logging",
                ],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

        # Analytics processing
        self.register_processing_activity(
            DataProcessingRecord(
                processing_id="analytics",
                data_category=DataCategory.USAGE_DATA,
                purpose=ProcessingPurpose.ANALYTICS,
                legal_basis=LegalBasis.LEGITIMATE_INTEREST,
                data_subjects="Users of AI assistant service",
                data_types=["usage statistics", "performance metrics", "error logs"],
                recipients=["Internal analytics systems"],
                retention_period="12 months",
                security_measures=[
                    "Pseudonymization",
                    "Access controls",
                    "Data minimization",
                ],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

        # Set default retention policies (in days)
        self.data_retention_policies = {
            DataCategory.PERSONAL_DATA: 2555,  # 7 years
            DataCategory.DOCUMENT_CONTENT: 0,  # Indefinite (user controlled)
            DataCategory.USAGE_DATA: 365,  # 1 year
            DataCategory.SYSTEM_DATA: 2190,  # 6 years
            DataCategory.SENSITIVE_DATA: 1095,  # 3 years
        }

    def register_processing_activity(self, record: DataProcessingRecord):
        """Register a data processing activity"""
        self.processing_records[record.processing_id] = record
        logger.info(f"Registered processing activity: {record.processing_id}")

    def record_consent(
        self,
        user_id: str,
        tenant_id: str,
        purpose: ProcessingPurpose,
        granted: bool,
        consent_text: str = "",
    ) -> ConsentRecord:
        """Record user consent for data processing"""
        consent_id = str(uuid.uuid4())

        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            tenant_id=tenant_id,
            purpose=purpose,
            granted=granted,
            granted_at=datetime.now(UTC),
            consent_text=consent_text,
        )

        self.consent_records[consent_id] = consent
        logger.info(f"Recorded consent: {user_id} -> {purpose.value} = {granted}")
        return consent

    def withdraw_consent(self, user_id: str, purpose: ProcessingPurpose) -> bool:
        """Withdraw user consent for specific purpose"""
        # Find active consent records for user and purpose
        for consent in self.consent_records.values():
            if (
                consent.user_id == user_id
                and consent.purpose == purpose
                and consent.granted
                and consent.withdrawn_at is None
            ):

                consent.granted = False
                consent.withdrawn_at = datetime.now(UTC)
                logger.info(f"Consent withdrawn: {user_id} -> {purpose.value}")
                return True

        return False

    def has_valid_consent(self, user_id: str, purpose: ProcessingPurpose) -> bool:
        """Check if user has valid consent for processing purpose"""
        for consent in self.consent_records.values():
            if (
                consent.user_id == user_id
                and consent.purpose == purpose
                and consent.granted
                and consent.withdrawn_at is None
            ):
                return True

        return False

    def submit_data_subject_request(
        self, user_id: str, tenant_id: str, request_type: str, details: str = ""
    ) -> DataSubjectRequest:
        """Submit a data subject rights request"""
        request_id = str(uuid.uuid4())

        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            tenant_id=tenant_id,
            request_type=request_type,
            status="pending",
            submitted_at=datetime.now(UTC),
            details=details,
        )

        self.data_subject_requests[request_id] = request
        logger.info(f"Data subject request submitted: {request_type} from {user_id}")
        return request

    async def process_access_request(self, request_id: str) -> Dict[str, Any]:
        """Process right of access request (Art. 15 GDPR)"""
        request = self.data_subject_requests.get(request_id)
        if not request or request.request_type != "access":
            return {"error": "Invalid access request"}

        user_data = await self._collect_user_data(request.user_id, request.tenant_id)

        request.status = "completed"
        request.completed_at = datetime.now(UTC)
        request.response_data = user_data

        logger.info(f"Access request completed for user: {request.user_id}")
        return user_data

    async def process_erasure_request(self, request_id: str) -> bool:
        """Process right to erasure request (Art. 17 GDPR)"""
        request = self.data_subject_requests.get(request_id)
        if not request or request.request_type != "erasure":
            return False

        # Check if erasure is legally possible
        if not self._can_erase_data(request.user_id):
            request.status = "rejected"
            request.completed_at = datetime.now(UTC)
            return False

        # Perform data erasure
        success = await self._erase_user_data(request.user_id, request.tenant_id)

        request.status = "completed" if success else "rejected"
        request.completed_at = datetime.now(UTC)

        logger.info(
            f"Erasure request processed for user: {request.user_id}, success: {success}"
        )
        return success

    async def process_portability_request(
        self, request_id: str
    ) -> Optional[Dict[str, Any]]:
        """Process data portability request (Art. 20 GDPR)"""
        request = self.data_subject_requests.get(request_id)
        if not request or request.request_type != "portability":
            return None

        # Export user data in structured format
        export_data = await self._export_user_data(request.user_id, request.tenant_id)

        request.status = "completed"
        request.completed_at = datetime.now(UTC)
        request.response_data = {"export_url": export_data.get("download_url")}

        logger.info(f"Portability request completed for user: {request.user_id}")
        return export_data

    async def _collect_user_data(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Collect all personal data for access request"""
        # This would integrate with actual data storage systems
        user_data = {
            "personal_information": {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "collection_date": datetime.now(UTC).isoformat(),
            },
            "document_data": {
                "total_documents": 0,
                "total_size_bytes": 0,
                "categories": [],
            },
            "usage_analytics": {
                "total_queries": 0,
                "last_activity": None,
                "feature_usage": {},
            },
            "consent_records": [
                {
                    "purpose": consent.purpose.value,
                    "granted": consent.granted,
                    "granted_at": consent.granted_at.isoformat(),
                    "withdrawn_at": (
                        consent.withdrawn_at.isoformat()
                        if consent.withdrawn_at
                        else None
                    ),
                }
                for consent in self.consent_records.values()
                if consent.user_id == user_id
            ],
            "processing_activities": [
                {
                    "activity": record.processing_id,
                    "purpose": record.purpose.value,
                    "legal_basis": record.legal_basis.value,
                    "data_types": record.data_types,
                }
                for record in self.processing_records.values()
            ],
        }

        return user_data

    def _can_erase_data(self, user_id: str) -> bool:
        """Check if user data can be erased (considering legal obligations)"""
        # Check for legal obligations that prevent erasure
        # E.g., audit logs, financial records, etc.

        # For demo purposes, always allow erasure
        # In production, this would check various constraints
        return True

    async def _erase_user_data(self, user_id: str, tenant_id: str) -> bool:
        """Erase all user personal data"""
        try:
            # Remove or pseudonymize user data across all systems
            # This would integrate with actual data storage systems

            # Remove consent records
            to_remove = [
                consent_id
                for consent_id, consent in self.consent_records.items()
                if consent.user_id == user_id
            ]

            for consent_id in to_remove:
                del self.consent_records[consent_id]

            logger.info(f"Erased data for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to erase data for user {user_id}: {str(e)}")
            return False

    async def _export_user_data(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Export user data in machine-readable format"""
        user_data = await self._collect_user_data(user_id, tenant_id)

        # Generate export file
        export_id = str(uuid.uuid4())
        export_filename = f"user_data_export_{user_id}_{export_id}.json"

        # In production, this would create actual files and secure download URLs
        return {
            "export_id": export_id,
            "filename": export_filename,
            "download_url": f"/gdpr/export/{export_id}",
            "expires_at": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
            "data": user_data,
        }

    def generate_processing_record_report(self) -> Dict[str, Any]:
        """Generate Article 30 processing record report"""
        return {
            "organization": "Obsidian AI Assistant",
            "controller_contact": "dpo@obsidian-ai.com",
            "report_generated": datetime.now(UTC).isoformat(),
            "processing_activities": [
                {
                    "id": record.processing_id,
                    "data_category": record.data_category.value,
                    "purpose": record.purpose.value,
                    "legal_basis": record.legal_basis.value,
                    "data_subjects": record.data_subjects,
                    "data_types": record.data_types,
                    "recipients": record.recipients,
                    "retention_period": record.retention_period,
                    "security_measures": record.security_measures,
                    "last_updated": record.updated_at.isoformat(),
                }
                for record in self.processing_records.values()
            ],
        }

    def check_data_retention(self) -> List[Dict[str, Any]]:
        """Check for data that should be deleted based on retention policies"""
        # This would scan actual data storage and identify expired data
        expired_data = []

        for category, retention_days in self.data_retention_policies.items():
            if retention_days > 0:  # 0 means indefinite retention
                cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)

                # In production, this would query actual data stores
                expired_data.append(
                    {
                        "category": category.value,
                        "retention_days": retention_days,
                        "cutoff_date": cutoff_date.isoformat(),
                        "estimated_records": 0,  # Would be actual count
                    }
                )

        return expired_data


# FastAPI endpoints for GDPR compliance
class GDPREndpoints:
    """GDPR compliance API endpoints"""

    def __init__(self, app, gdpr_manager: GDPRComplianceManager):
        self.app = app
        self.gdpr_manager = gdpr_manager
        self._register_endpoints()

    def _register_endpoints(self):
        """Register GDPR endpoints with FastAPI"""

        @self.app.post("/gdpr/consent")
        async def record_consent(request_data: Dict[str, Any], request):
            """Record user consent"""
            user_id = request.state.user.get("user_id")
            tenant_id = request.state.user.get("tenant_id")

            purpose_str = request_data.get("purpose")
            granted = request_data.get("granted", False)
            consent_text = request_data.get("consent_text", "")

            try:
                purpose = ProcessingPurpose(purpose_str)
                consent = self.gdpr_manager.record_consent(
                    user_id, tenant_id, purpose, granted, consent_text
                )

                return {
                    "consent_id": consent.consent_id,
                    "message": f"Consent {'granted' if granted else 'denied'} for {purpose.value}",
                }
            except ValueError:
                return {"error": f"Invalid purpose: {purpose_str}", "status_code": 400}

        @self.app.delete("/gdpr/consent/{purpose}")
        async def withdraw_consent(purpose: str, request):
            """Withdraw user consent"""
            user_id = request.state.user.get("user_id")

            try:
                purpose_enum = ProcessingPurpose(purpose)
                success = self.gdpr_manager.withdraw_consent(user_id, purpose_enum)

                if success:
                    return {"message": f"Consent withdrawn for {purpose}"}
                else:
                    return {"error": "No active consent found", "status_code": 404}
            except ValueError:
                return {"error": f"Invalid purpose: {purpose}", "status_code": 400}

        @self.app.post("/gdpr/request")
        async def submit_data_request(request_data: Dict[str, Any], request):
            """Submit data subject rights request"""
            user_id = request.state.user.get("user_id")
            tenant_id = request.state.user.get("tenant_id")

            request_type = request_data.get("type")
            details = request_data.get("details", "")

            if request_type not in [
                "access",
                "rectification",
                "erasure",
                "portability",
                "restriction",
            ]:
                return {"error": "Invalid request type", "status_code": 400}

            dsr = self.gdpr_manager.submit_data_subject_request(
                user_id, tenant_id, request_type, details
            )

            return {
                "request_id": dsr.request_id,
                "type": dsr.request_type,
                "status": dsr.status,
                "submitted_at": dsr.submitted_at.isoformat(),
            }

        @self.app.get("/gdpr/request/{request_id}")
        async def get_request_status(request_id: str, request):
            """Get data subject request status"""
            user_id = request.state.user.get("user_id")

            dsr = self.gdpr_manager.data_subject_requests.get(request_id)
            if not dsr or dsr.user_id != user_id:
                return {"error": "Request not found", "status_code": 404}

            response = {
                "request_id": dsr.request_id,
                "type": dsr.request_type,
                "status": dsr.status,
                "submitted_at": dsr.submitted_at.isoformat(),
                "completed_at": (
                    dsr.completed_at.isoformat() if dsr.completed_at else None
                ),
            }

            if dsr.status == "completed" and dsr.response_data:
                response["data"] = dsr.response_data

            return response

        @self.app.get("/gdpr/processing-records")
        async def get_processing_records():
            """Get data processing records (public information)"""
            return self.gdpr_manager.generate_processing_record_report()

        @self.app.get("/gdpr/my-data")
        async def get_my_data(request):
            """Get user's own data (simplified access request)"""
            user_id = request.state.user.get("user_id")
            tenant_id = request.state.user.get("tenant_id")

            user_data = await self.gdpr_manager._collect_user_data(user_id, tenant_id)
            return user_data
