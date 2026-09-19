"""
RitaDrishti-AI — Global & Natural Language Search API Endpoint (Database Connected)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.db.repositories import CompanyRepository
from backend.app.ml.nl_query_engine import NaturalLanguageQueryEngine

router = APIRouter()
nl_engine = NaturalLanguageQueryEngine()


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
    companies_dict = [
        {
            "company_id": str(c.company_id),
            "name": c.name,
            "domain": c.domain,
            "industry": c.industry,
            "verified_status": c.verified_status,
            "trust_score": 75.0,
            "risk_level": "Low"
        }
        for c in companies
    ]

    filtered = nl_engine.execute_nl_search(prompt, companies_dict)
    parsed_meta = nl_engine.parse_query(prompt)

    return {
        "natural_language_prompt": prompt,
        "parsed_filters": parsed_meta["filters"],
        "count": len(filtered),
        "results": filtered
    }
