"""
RitaDrishti-AI — Risk & Fraud Intelligence API Endpoint (Database Persisted & Calculated)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.core.exceptions import EntityNotFoundError
from backend.app.db.models import CompanyModel, AIAnalysisModel
from backend.app.db.repositories import CompanyRepository
from backend.app.db.schemas import RiskScoreResponse
from backend.app.ml.risk_prediction import RiskPredictionEngine

router = APIRouter()
risk_engine = RiskPredictionEngine()


@router.get("/{company_id}", response_model=RiskScoreResponse)
async def get_risk_score(company_id: UUID, db: AsyncSession = Depends(get_db)):
    """Calculates corporate fraud risk, regulatory risk, and anomaly signals from database records."""
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{company_id}' not found.")

    # Calculate fake review ratio & negative sentiment ratio from database
    total_stmt = select(func.count(AIAnalysisModel.analysis_id)).where(AIAnalysisModel.company_id == company_id)
    suspicious_stmt = select(func.count(AIAnalysisModel.analysis_id)).where(
        AIAnalysisModel.company_id == company_id,
        AIAnalysisModel.is_suspicious == True
    )
    negative_stmt = select(func.count(AIAnalysisModel.analysis_id)).where(
        AIAnalysisModel.company_id == company_id,
        AIAnalysisModel.sentiment_label == "negative"
    )

    total_count = (await db.execute(total_stmt)).scalar() or 0
    suspicious_count = (await db.execute(suspicious_stmt)).scalar() or 0
    negative_count = (await db.execute(negative_stmt)).scalar() or 0

    fake_ratio = (suspicious_count / total_count) if total_count > 0 else 0.0
    neg_ratio = (negative_count / total_count) if total_count > 0 else 0.0

    risk_res = risk_engine.evaluate_risk(
        fake_review_ratio=fake_ratio,
        unresolved_complaints=0,
        critical_complaints=0,
        negative_sentiment_ratio=neg_ratio,
        negative_news_count=0
    )

    return RiskScoreResponse(
        company_id=company_id,
        overall_risk_score=risk_res["overall_risk_score"],
        fraud_risk=risk_res["sub_scores"]["fraud_risk"],
        regulatory_risk=risk_res["sub_scores"]["regulatory_risk"],
        reputational_risk=risk_res["sub_scores"]["reputational_risk"],
        risk_level=risk_res["risk_level"],
        anomaly_signals=risk_res["anomaly_signals"]
    )
