"""
RitaDrishti-AI — Endpoints Unit & Integration Tests (Trust, Risk, Alerts, Search, Chat, Reports)
Tests real database queries and feature-gated 503 error responses.
"""

import pytest
from httpx import AsyncClient
from backend.app.db.repositories import CompanyRepository, ReviewRepository, UserRepository


@pytest.mark.asyncio
async def test_database_connected_trust_and_risk_endpoints(client: AsyncClient, auth_headers: dict):
    # 1. Create company via POST /api/v1/companies
    comp_payload = {
        "name": "Acme Cloud Solutions",
        "domain": "acmecloud.io",
        "industry": "Cloud SaaS",
        "description": "Enterprise cloud provider."
    }
    comp_resp = await client.post("/api/v1/companies/", json=comp_payload, headers=auth_headers)
    assert comp_resp.status_code == 201
    company_id = comp_resp.json()["company_id"]

    # 2. Test Trust Score Endpoint
    trust_resp = await client.get(f"/api/v1/trust/{company_id}")
    assert trust_resp.status_code == 200
    trust_data = trust_resp.json()
    assert "trust_index" in trust_data
    assert trust_data["company_id"] == company_id

    # 3. Test Risk Score Endpoint
    risk_resp = await client.get(f"/api/v1/risk/{company_id}")
    assert risk_resp.status_code == 200
    risk_data = risk_resp.json()
    assert "overall_risk_score" in risk_data
    assert risk_data["company_id"] == company_id

    # 4. Submit Suspicious Review to trigger Fraud Alert
    review_payload = {
        "company_id": company_id,
        "source": "Trustpilot",
        "rating": 5.0,
        "raw_text": "BEST PRODUCT EVER!!! Contact spam@example.com MUST BUY 100% FIVE STARS!!"
    }
    await client.post("/api/v1/reviews/analyze", json=review_payload, headers=auth_headers)

    # 5. Test Alerts Endpoint
    alerts_resp = await client.get("/api/v1/alerts/")
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    assert alerts[0]["type"] == "Fraud Alert"

    # 6. Test Search Endpoints
    search_resp = await client.get("/api/v1/search/?q=Acme")
    assert search_resp.status_code == 200
    assert search_resp.json()["count"] >= 1

    nl_resp = await client.get("/api/v1/search/nl?prompt=Show cloud companies")
    assert nl_resp.status_code == 200
    assert "parsed_filters" in nl_resp.json()


@pytest.mark.asyncio
async def test_disabled_chat_endpoint_returns_503(client: AsyncClient):
    resp = await client.post("/api/v1/chat/", json={"query": "What is Acme trust score?"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "OLLAMA_DISABLED"


@pytest.mark.asyncio
async def test_disabled_reports_endpoint_returns_503(client: AsyncClient):
    resp = await client.post("/api/v1/reports/generate", json={"company_name": "Acme Cloud"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "CREWAI_DISABLED"
