"""
RitaDrishti-AI — Multi-Agent Executive Reports API Endpoint
"""

from fastapi import APIRouter
from backend.app.db.schemas import AuditReportRequest, AuditReportResponse
from backend.app.agents.crew_manager import CrewManager

router = APIRouter()
crew_manager = CrewManager()

@router.post("/generate", response_model=AuditReportResponse)
async def generate_executive_report(req: AuditReportRequest):
    """Triggers CrewAI Multi-Agent audit workflow and returns executive markdown report."""
    audit_res = crew_manager.run_full_audit(company_name=req.company_name)
    return {
        "company_name": req.company_name,
        "report_markdown": audit_res["report_markdown"]
    }
