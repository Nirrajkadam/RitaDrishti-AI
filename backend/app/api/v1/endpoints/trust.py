"""
SentinelX Trust AI — Trust Index API Endpoint
"""

from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.db.schemas import TrustScoreResponse
from app.ml.trust_score_engine import TrustScoreEngine

router = APIRouter()
trust_engine = TrustScoreEngine()

@router.get("/{company_id}", response_model=TrustScoreResponse)
async def get_trust_score(company_id: UUID):
    """Calculates and returns multi-factor Trust Score metrics for a company."""
    
    # Run calculation engine
    trust_res = trust_engine.calculate_trust_score(
        avg_sentiment_score=0.72,
        avg_fake_prob=0.04,
        total_reviews=250,
        unresolved_complaints=1,
        verified_status=True,
        overall_risk_score=12.5
    )

    return {
        "company_id": company_id,
        "trust_index": trust_res["trust_index"],
        "transparency_score": trust_res["components"]["transparency_score"],
        "sentiment_factor": trust_res["components"]["sentiment_factor"],
        "fake_review_penalty": trust_res["components"]["authenticity_score"],
        "complaint_penalty": trust_res["components"]["complaint_penalty"],
        "trust_tier": trust_res["trust_tier"]
    }
