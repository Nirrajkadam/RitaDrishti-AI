"""
RitaDrishti-AI — Multi-Agent Executive Reports API Endpoint
"""

from fastapi import APIRouter
from backend.app.config import settings
from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.db.schemas import AuditReportRequest, AuditReportResponse

router = APIRouter()


@router.post("/generate", response_model=AuditReportResponse)
async def generate_executive_report(req: AuditReportRequest):
    """Triggers CrewAI Multi-Agent audit workflow and returns executive markdown report."""
    if not settings.ENABLE_CREWAI:
        raise ServiceUnavailableError(
            code="CREWAI_DISABLED",
            message="CrewAI Multi-Agent Report Generation service is disabled. Set ENABLE_CREWAI=true to enable.",
            retryable=False
        )

    from backend.app.agents.crew_manager import CrewManager
    crew_manager = CrewManager()
    audit_res = crew_manager.run_full_audit(company_name=req.company_name)
    return {
        "company_name": req.company_name,
        "report_markdown": audit_res["report_markdown"]
    }
