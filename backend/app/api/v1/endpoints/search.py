"""
RitaDrishti-AI — Global & Natural Language Search API Endpoint (Database Connected)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer, case
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.db.repositories import CompanyRepository
from backend.app.db.models import AIAnalysisModel
from backend.app.ml.nl_query_engine import NaturalLanguageQueryEngine
from backend.app.ml.trust_score_engine import TrustScoreEngine
from backend.app.ml.risk_prediction import RiskPredictionEngine

router = APIRouter()
nl_engine = NaturalLanguageQueryEngine()
trust_engine = TrustScoreEngine()
risk_engine = RiskPredictionEngine()


@router.get("/")
async def global_search(
    q: str = Query(..., description="Company name, domain, or industry keyword"),
    db: AsyncSession = Depends(get_db)
):
    """Global keyword search across registered database company names, domains, and industries."""
    repo = CompanyRepository(db)
    companies = await repo.list_companies(limit=100)

    query = q.lower().strip()
    results = [
        {
            "company_id": str(c.company_id),
            "name": c.name,
            "domain": c.domain,
            "industry": c.industry,
            "verified_status": c.verified_status
        }
        for c in companies
        if query in c.name.lower() or query in c.domain.lower() or query in c.industry.lower()
    ]

    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/nl")
async def natural_language_search(
    prompt: str = Query(..., description="Natural language search prompt, e.g. 'Show fintech companies'"),
    db: AsyncSession = Depends(get_db)
):
    """Natural Language Search endpoint parsing query intent and filtering database companies."""
    repo = CompanyRepository(db)
    companies = await repo.list_companies(limit=100)
    companies_dict = []
    for c in companies:
        stmt = (
            select(
                func.count(AIAnalysisModel.analysis_id),
                func.avg(AIAnalysisModel.sentiment_score),
                func.avg(AIAnalysisModel.fake_probability),
                func.sum(case((AIAnalysisModel.is_suspicious == True, 1), else_=0)),
                func.sum(case((AIAnalysisModel.sentiment_label == "negative", 1), else_=0))
            )
            .where(AIAnalysisModel.company_id == c.company_id)
        )
        res = (await db.execute(stmt)).one()
        total_count = res[0] or 0
        avg_sentiment = float(res[1] or 0.0)
        avg_fake = float(res[2] or 0.0)
        suspicious_count = res[3] or 0
        negative_count = res[4] or 0

        if total_count > 0:
            fake_ratio = suspicious_count / total_count
            neg_ratio = negative_count / total_count
            t_res = trust_engine.calculate_trust_score(
                avg_sentiment_score=avg_sentiment,
                avg_fake_prob=avg_fake,
                total_reviews=total_count,
                unresolved_complaints=0,
                verified_status=c.verified_status,
                overall_risk_score=15.0 if avg_fake > 0.2 else 5.0
            )
            r_res = risk_engine.evaluate_risk(
                fake_review_ratio=fake_ratio,
                unresolved_complaints=0,
                critical_complaints=0,
                negative_sentiment_ratio=neg_ratio,
                negative_news_count=0
            )
            score = t_res["trust_index"]
            level = r_res["risk_level"]
        else:
            score = None
            level = "UNRATED"

        companies_dict.append({
            "company_id": str(c.company_id),
            "name": c.name,
            "domain": c.domain,
            "industry": c.industry,
            "verified_status": c.verified_status,
            "trust_score": score,
            "risk_level": level
        })

    filtered = nl_engine.execute_nl_search(prompt, companies_dict)
    parsed_meta = nl_engine.parse_query(prompt)

    return {
        "natural_language_prompt": prompt,
        "parsed_filters": parsed_meta["filters"],
        "count": len(filtered),
        "results": filtered
    }
