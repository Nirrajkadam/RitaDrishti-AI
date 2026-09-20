from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.core.database import get_db
from backend.app.core.exceptions import ServiceUnavailableError, EntityNotFoundError
from backend.app.core.security import get_current_user
from backend.app.db.models import UserModel, CompanyModel, AIAnalysisModel, ReviewModel
from backend.app.db.repositories import CompanyRepository
from backend.app.db.schemas import AuditReportRequest, AuditReportResponse
from backend.app.ml.trust_score_engine import TrustScoreEngine

router = APIRouter()
trust_engine = TrustScoreEngine()


@router.post("/generate", response_model=AuditReportResponse)
async def generate_executive_report(
    req: AuditReportRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers CrewAI Multi-Agent audit workflow and returns executive markdown report."""
    if not settings.ENABLE_CREWAI:
        raise ServiceUnavailableError(
            code="CREWAI_DISABLED",
            message="CrewAI Multi-Agent report generation is disabled. Set ENABLE_CREWAI=true to enable.",
            retryable=False
        )

    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(req.company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{req.company_id}' not found.")

    try:
        from backend.app.agents.crew_manager import (
            CrewManager, AuditEvidence, ReviewAnalysisEvidence, EvidenceUnavailableError
        )

        # Retrieve reviews & AI analyses for this company from DB
        stmt = (
            select(ReviewModel, AIAnalysisModel)
            .join(AIAnalysisModel, ReviewModel.review_id == AIAnalysisModel.review_id)
            .where(ReviewModel.company_id == req.company_id)
        )
        results = (await db.execute(stmt)).all()

        analyses_evidence = []
        total_fake_prob = 0.0
        total_sentiment = 0.0

        for rev, analysis in results:
            cleaned = rev.cleaned_text or rev.raw_text or ""
            analyses_evidence.append(
                ReviewAnalysisEvidence(
                    raw_text=rev.raw_text or "",
                    cleaned_text=cleaned,
                    sentiment_score=float(analysis.sentiment_score or 0.0),
                    fake_probability=float(analysis.fake_probability or 0.0),
                    is_suspicious=bool(analysis.is_suspicious)
                )
            )
            total_fake_prob += float(analysis.fake_probability or 0.0)
            total_sentiment += float(analysis.sentiment_score or 0.0)

        calculated_trust_score = None
        if len(results) > 0:
            avg_fake = total_fake_prob / len(results)
            avg_sent = total_sentiment / len(results)
            t_res = trust_engine.calculate_trust_score(
                avg_sentiment_score=avg_sent,
                avg_fake_prob=avg_fake,
                total_reviews=len(results),
                unresolved_complaints=0,
                verified_status=company.verified_status,
                overall_risk_score=15.0 if avg_fake > 0.2 else 5.0
            )
            calculated_trust_score = float(t_res["trust_index"])

        crew_manager = CrewManager()
        evidence = AuditEvidence(
            company_name=company.name,
            trust_score=calculated_trust_score,
            analyses=analyses_evidence
        )
        audit_res = crew_manager.run_full_audit(evidence)

        return {
            "company_name": company.name,
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
