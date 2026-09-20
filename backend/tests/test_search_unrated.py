"""
Behavioral Unit Tests: Natural Language Search & Unrated Company States
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from backend.app.ml.nl_query_engine import NaturalLanguageQueryEngine


def test_nl_query_engine_unreviewed_company_filtering():
    nl = NaturalLanguageQueryEngine()

    companies = [
        {"company_id": "1", "name": "Reviewed Cloud", "industry": "Cloud SaaS", "trust_score": 85.0, "risk_level": "Low"},
        {"company_id": "2", "name": "Unreviewed Stealth", "industry": "Cloud Infrastructure", "trust_score": None, "risk_level": "UNRATED"}
    ]

    # Search without trust score filter should return both
    r1 = nl.execute_nl_search("Show cloud companies", companies)
    assert len(r1) == 2

    # Search with min trust score filter (> 70) should exclude unreviewed company
    r2 = nl.execute_nl_search("Show cloud companies with trust score > 70", companies)
    assert len(r2) == 1
    assert r2[0]["name"] == "Reviewed Cloud"


@pytest.mark.asyncio
async def test_search_endpoint_returns_unrated_state_for_new_company(client: AsyncClient, auth_headers: dict):
    comp_data = {
        "name": "Stealth Cyber Ltd",
        "domain": f"stealth_{uuid4().hex[:6]}.io",
        "industry": "Cybersecurity"
    }
    create_resp = await client.post("/api/v1/companies/", json=comp_data, headers=auth_headers)
    comp_id = create_resp.json()["company_id"]

    nl_resp = await client.get("/api/v1/search/nl?prompt=Show Cybersecurity companies")
    assert nl_resp.status_code == 200
    results = nl_resp.json()["results"]
    matched = next((r for r in results if r["company_id"] == comp_id), None)
    assert matched is not None
    assert matched["trust_score"] is None
    assert matched["risk_level"] == "UNRATED"
