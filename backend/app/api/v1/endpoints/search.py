"""
RitaDrishti-AI — Global & Natural Language Search API Endpoint
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from app.ml.nl_query_engine import NaturalLanguageQueryEngine

router = APIRouter()
nl_engine = NaturalLanguageQueryEngine()

SAMPLE_COMPANIES_DATASET = [
    {"company_id": "1", "name": "Acme Cloud Solutions", "domain": "acmecloud.io", "industry": "Cloud SaaS", "trust_score": 88.5, "risk_level": "Low", "verified_status": True},
    {"company_id": "2", "name": "FinPay Tech", "domain": "finpay.com", "industry": "Fintech", "trust_score": 64.2, "risk_level": "Medium", "verified_status": True},
    {"company_id": "3", "name": "Apex Logistics", "domain": "apexlogistics.net", "industry": "Supply Chain", "trust_score": 38.1, "risk_level": "Severe", "verified_status": False},
    {"company_id": "4", "name": "Nova Health Solutions", "domain": "novahealth.org", "industry": "Healthcare", "trust_score": 91.0, "risk_level": "Low", "verified_status": True},
    {"company_id": "5", "name": "CyberShield Software", "domain": "cybershield.io", "industry": "Cybersecurity", "trust_score": 84.6, "risk_level": "Low", "verified_status": True}
]

@router.get("/")
async def global_search(q: str = Query(..., description="Company name, domain, or industry keyword")):
    """Global keyword search across company names, domains, and industries."""
    query = q.lower().strip()
    results = [
        c for c in SAMPLE_COMPANIES_DATASET
        if query in c["name"].lower() or query in c["domain"].lower() or query in c["industry"].lower()
    ]
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@router.get("/nl")
async def natural_language_search(prompt: str = Query(..., description="Natural language search prompt, e.g. 'Show high-risk fintech companies'")):
    """Natural Language Search endpoint that parses query intent and filters target company metrics."""
    filtered = nl_engine.execute_nl_search(prompt, SAMPLE_COMPANIES_DATASET)
    parsed_meta = nl_engine.parse_query(prompt)
    return {
        "natural_language_prompt": prompt,
        "parsed_filters": parsed_meta["filters"],
        "count": len(filtered),
        "results": filtered
    }
