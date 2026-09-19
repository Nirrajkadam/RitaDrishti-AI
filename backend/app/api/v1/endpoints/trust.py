"""
RitaDrishti-AI — Trust Index API Endpoint (Database Persisted & Calculated)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.core.exceptions import EntityNotFoundError
from backend.app.db.models import CompanyModel, ReviewModel, AIAnalysisModel
from backend.app.db.repositories import CompanyRepository
from backend.app.db.schemas import TrustScoreResponse
from backend.app.ml.trust_score_engine import TrustScoreEngine

router = APIRouter()
trust_engine = TrustScoreEngine()


@router.get("/{company_id}", response_model=TrustScoreResponse)
async def get_trust_score(company_id: UUID, db: AsyncSession = Depends(get_db)):
    """Calculates and returns multi-factor Trust Score metrics derived from database records."""
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{company_id}' not found.")

    # Query aggregate review and sentiment stats
    stmt = (
        select(
            func.count(AIAnalysisModel.analysis_id),
            func.avg(AIAnalysisModel.sentiment_score),
            func.avg(AIAnalysisModel.fake_probability)
        )
        .where(AIAnalysisModel.company_id == company_id)
    )
    result = await db.execute(stmt)
    total_reviews, avg_sentiment, avg_fake = result.one()

    total_count = total_reviews or 0
    sentiment_score = float(avg_sentiment or 0.0)
    fake_prob = float(avg_fake or 0.0)

    trust_res = trust_engine.calculate_trust_score(
        avg_sentiment_score=sentiment_score,
        avg_fake_prob=fake_prob,
        total_reviews=total_count,
        unresolved_complaints=0,
        verified_status=company.verified_status,
        overall_risk_score=15.0 if fake_prob > 0.2 else 5.0
    )

    return TrustScoreResponse(
        company_id=company_id,
        trust_index=trust_res["trust_index"],
        transparency_score=trust_res["components"]["transparency_score"],
        sentiment_factor=trust_res["components"]["sentiment_factor"],
        fake_review_penalty=trust_res["components"]["authenticity_score"],
        complaint_penalty=trust_res["components"]["complaint_penalty"],
        trust_tier=trust_res["trust_tier"]
    )
