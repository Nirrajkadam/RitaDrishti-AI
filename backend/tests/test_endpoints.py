"""
RitaDrishti-AI — Endpoints Unit & Integration Tests (Trust, Risk, Alerts, Search, Chat, Reports)
Tests real database queries and feature-gated 503 error responses.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from backend.app.config import settings
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
    trust_resp = await client.get(f"/api/v1/trust/{company_id}", headers=auth_headers)
    assert trust_resp.status_code == 200
    trust_data = trust_resp.json()
    assert "trust_index" in trust_data
    assert trust_data["company_id"] == company_id

    # 3. Test Risk Score Endpoint
    risk_resp = await client.get(f"/api/v1/risk/{company_id}", headers=auth_headers)
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
    alerts_resp = await client.get("/api/v1/alerts/", headers=auth_headers)
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    assert alerts[0]["type"] == "Fraud Alert"

    alerts_sum = await client.get("/api/v1/alerts/summary", headers=auth_headers)
    assert alerts_sum.status_code == 200

    # 6. Test Search Endpoints
    search_resp = await client.get("/api/v1/search/?q=Acme", headers=auth_headers)
    assert search_resp.status_code == 200
    assert search_resp.json()["count"] >= 1

    nl_resp = await client.get("/api/v1/search/nl?prompt=Show+cloud+companies", headers=auth_headers)
    assert nl_resp.status_code == 200
    assert "parsed_filters" in nl_resp.json()


@pytest.mark.asyncio
async def test_disabled_chat_endpoint_returns_503(client: AsyncClient):
    resp = await client.post("/api/v1/chat/", json={"query": "What is Acme trust score?"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "OLLAMA_OR_QDRANT_DISABLED"


@pytest.mark.asyncio
async def test_disabled_reports_endpoint_returns_503(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/reports/generate", json={"company_id": str(uuid4())}, headers=auth_headers)
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "CREWAI_DISABLED"


@pytest.mark.asyncio
async def test_reports_generation_workflow_when_enabled(client: AsyncClient, auth_headers: dict, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "ENABLE_CREWAI", True)

    # 1. Non-existent company -> 404
    fake_id = str(uuid4())
    r_404 = await client.post("/api/v1/reports/generate", json={"company_id": fake_id}, headers=auth_headers)
    assert r_404.status_code == 404

    # 2. Company with no reviews -> 503 CREWAI_EVIDENCE_UNAVAILABLE
    c_res = await client.post("/api/v1/companies/", json={
        "name": "No Reviews Inc",
        "domain": f"noreviews_{uuid4().hex[:6]}.com",
        "industry": "Tech"
    }, headers=auth_headers)
    comp_id = c_res.json()["company_id"]

    r_no_ev = await client.post("/api/v1/reports/generate", json={"company_id": comp_id}, headers=auth_headers)
    assert r_no_ev.status_code == 503
    assert r_no_ev.json()["error"]["code"] == "CREWAI_EVIDENCE_UNAVAILABLE"

    # 3. Add review & analysis to company
    await client.post("/api/v1/reviews/analyze", json={
        "company_id": comp_id,
        "source": "G2",
        "rating": 5.0,
        "raw_text": "Great service and fast setup."
    }, headers=auth_headers)

    # 4. Generate executive report -> 200
    r_ok = await client.post("/api/v1/reports/generate", json={"company_id": comp_id}, headers=auth_headers)
    assert r_ok.status_code == 200
    data = r_ok.json()
    assert data["company_name"] == "No Reviews Inc"
    assert "Review Analysis Assessment" in data["report_markdown"]



@pytest.mark.asyncio
async def test_auth_registration_and_login_error_branches(client: AsyncClient):
    uid = uuid4().hex[:6]
    user_data = {
        "email": f"auth_test_{uid}@example.com",
        "username": f"auth_user_{uid}",
        "password": "StrongPassword123!",
        "full_name": "Auth Test User"
    }

    # Successful registration
    r1 = await client.post("/api/v1/auth/register", json=user_data)
    assert r1.status_code == 201
    user_res = r1.json()
    assert user_res["username"] == f"auth_user_{uid}"

    # Duplicate username -> 401
    dup_user = {**user_data, "email": f"diff_email_{uid}@example.com"}
    r2 = await client.post("/api/v1/auth/register", json=dup_user)
    assert r2.status_code == 401

    # Duplicate email -> 401
    dup_email = {**user_data, "username": f"diff_username_{uid}"}
    r3 = await client.post("/api/v1/auth/register", json=dup_email)
    assert r3.status_code == 401

    # Login non-existent user -> 401
    r4 = await client.post("/api/v1/auth/login", json={"username": "non_existent_123", "password": "Password123!"})
    assert r4.status_code == 401

    # Login wrong password -> 401
    r5 = await client.post("/api/v1/auth/login", json={"username": f"auth_user_{uid}", "password": "WrongPassword!"})
    assert r5.status_code == 401

    # Successful login
    r6 = await client.post("/api/v1/auth/login", json={"username": f"auth_user_{uid}", "password": "StrongPassword123!"})
    assert r6.status_code == 200
    token = r6.json()["access_token"]

    # /me endpoint
    me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["username"] == f"auth_user_{uid}"


@pytest.mark.asyncio
async def test_search_nl_filtering_and_company_endpoints(client: AsyncClient, auth_headers: dict):
    # 1. Create company with unique domain
    domain = f"searchtech_{uuid4().hex[:6]}.com"
    c_res = await client.post("/api/v1/companies/", json={
        "name": "Search Tech Corp",
        "domain": domain,
        "industry": "Software"
    }, headers=auth_headers)
    assert c_res.status_code == 201
    comp_id = c_res.json()["company_id"]

    # Test list companies
    c_list = await client.get("/api/v1/companies/")
    assert c_list.status_code == 200
    assert len(c_list.json()) >= 1

    # Test get company by ID
    c_get = await client.get(f"/api/v1/companies/{comp_id}")
    assert c_get.status_code == 200
    assert c_get.json()["name"] == "Search Tech Corp"

    # Test duplicate domain -> 401
    c_dup = await client.post("/api/v1/companies/", json={
        "name": "Search Tech Dup",
        "domain": domain,
        "industry": "Software"
    }, headers=auth_headers)
    assert c_dup.status_code == 401

    # 2. Submit reviews to test search NL calculation branch for reviewed companies
    await client.post("/api/v1/reviews/analyze", json={
        "company_id": comp_id,
        "source": "Glassdoor",
        "rating": 5.0,
        "raw_text": "Excellent company with high quality software engineering culture."
    }, headers=auth_headers)

    # 3. Call NL search and global search
    nl_res = await client.get("/api/v1/search/nl?prompt=Show+Software+companies")
    assert nl_res.status_code == 200
    data = nl_res.json()
    assert "parsed_filters" in data

    s_res = await client.get("/api/v1/search/?q=Search")
    assert s_res.status_code == 200
    assert s_res.json()["count"] >= 1



