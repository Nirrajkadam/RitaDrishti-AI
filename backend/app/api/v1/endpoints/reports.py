"""
RitaDrishti-AI — Multi-Agent Executive Reports API Endpoint
"""

from fastapi import APIRouter, Depends
from backend.app.config import settings
from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.core.security import get_current_user
from backend.app.db.models import UserModel
from backend.app.db.schemas import AuditReportRequest, AuditReportResponse

router = APIRouter()


@router.post("/generate", response_model=AuditReportResponse)
async def generate_executive_report(
    req: AuditReportRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Triggers CrewAI Multi-Agent audit workflow and returns executive markdown report."""
    if not settings.ENABLE_CREWAI:
        raise ServiceUnavailableError(
            code="CREWAI_DISABLED",
            message="CrewAI Multi-Agent report generation is disabled. Set ENABLE_CREWAI=true to enable.",
            retryable=False
        )

    try:
        from backend.app.agents.crew_manager import CrewManager, AuditEvidence, EvidenceUnavailableError
        crew_manager = CrewManager()
        evidence = AuditEvidence(company_name=req.company_name)
        audit_res = crew_manager.run_full_audit(evidence)
        return {
            "company_name": req.company_name,
            "report_markdown": audit_res["report_markdown"]
        }
    except EvidenceUnavailableError as e:
        raise ServiceUnavailableError(
            code="CREWAI_EVIDENCE_UNAVAILABLE",
            message=str(e),
            retryable=False
        )
    except Exception as e:
        raise ServiceUnavailableError(
            code="CREWAI_EXECUTION_FAILED",
            message=f"CrewAI execution failed: {e}",
            retryable=False
        )
