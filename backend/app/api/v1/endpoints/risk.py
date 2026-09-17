"""
RitaDrishti-AI — Risk & Fraud Intelligence API Endpoint
"""

from fastapi import APIRouter
from uuid import UUID
from backend.app.db.schemas import RiskScoreResponse
from backend.app.ml.risk_prediction import RiskPredictionEngine

router = APIRouter()
risk_engine = RiskPredictionEngine()

@router.get("/{company_id}", response_model=RiskScoreResponse)
async def get_risk_score(company_id: UUID):
    """Retrieves fraud risk, regulatory risk, and anomaly signals for a company."""
    
    risk_res = risk_engine.evaluate_risk(
        fake_review_ratio=0.05,
        unresolved_complaints=1,
        critical_complaints=0,
        negative_sentiment_ratio=0.15,
        negative_news_count=0
    )

    return {
        "company_id": company_id,
        "overall_risk_score": risk_res["overall_risk_score"],
        "fraud_risk": risk_res["sub_scores"]["fraud_risk"],
        "regulatory_risk": risk_res["sub_scores"]["regulatory_risk"],
        "reputational_risk": risk_res["sub_scores"]["reputational_risk"],
        "risk_level": risk_res["risk_level"],
        "anomaly_signals": risk_res["anomaly_signals"]
    }
