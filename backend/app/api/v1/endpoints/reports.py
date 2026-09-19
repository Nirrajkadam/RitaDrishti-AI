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
    raise ServiceUnavailableError(
        code="CREWAI_DISABLED",
        message="CrewAI Multi-Agent live research pipeline is disabled in this prototype environment.",
        retryable=False
    )
