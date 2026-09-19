"""
RitaDrishti-AI — Endpoints Unit & Integration Tests (Alerts, Trust, Risk, Search, Chat, Reports)
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trust_scores_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/trust/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 200
    data = resp.json()
    assert "trust_index" in data
    assert data["trust_tier"] is not None


@pytest.mark.asyncio
async def test_risk_intelligence_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/risk/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_risk_score" in data
    assert "risk_level" in data


@pytest.mark.asyncio
async def test_alerts_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/alerts/")
    assert resp.status_code == 200
    alerts = resp.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0


@pytest.mark.asyncio
async def test_search_endpoints(client: AsyncClient):
    resp_global = await client.get("/api/v1/search/?q=Acme")
    assert resp_global.status_code == 200
    assert resp_global.json()["count"] >= 1

    resp_nl = await client.get("/api/v1/search/nl?prompt=high risk fintech companies")
    assert resp_nl.status_code == 200
    assert "parsed_filters" in resp_nl.json()


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
