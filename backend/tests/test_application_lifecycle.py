"""
Behavioral Unit Tests: Application Lifecycle & FastAPI Endpoint Branches
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.ml.sentiment_engine import SentimentEngine
from backend.app.ml.trust_score_engine import TrustScoreEngine
from backend.app.ml.risk_prediction import RiskPredictionEngine


def test_sentiment_engine_scoring_branches():
    engine = SentimentEngine()
    assert engine.analyze_sentiment("")["label"] == "neutral"
    assert engine.analyze_sentiment("Loved it, high quality!")["label"] == "positive"
    assert engine.analyze_sentiment("Scam, absolute fraud!")["label"] == "negative"


def test_trust_score_engine_tier_branches():
    engine = TrustScoreEngine()
    res_high = engine.calculate_trust_score(1.0, 0.0, 100, 0, True, 0.0)
    assert res_high["trust_tier"] == "High Trust"

    res_mod = engine.calculate_trust_score(0.5, 0.15, 10, 2, False, 25.0)
    assert res_mod["trust_tier"] in ["Moderate Trust", "Low Trust"]

    res_crit = engine.calculate_trust_score(-0.8, 0.85, 5, 10, False, 80.0)
    assert res_crit["trust_tier"] == "Critical Alert"


def test_risk_prediction_engine_branches():
    engine = RiskPredictionEngine()
    res_severe = engine.evaluate_risk(0.8, 10, 5, 0.9, 10)
    assert res_severe["risk_level"] in ["High", "Severe"]

    res_low = engine.evaluate_risk(0.0, 0, 0, 0.0, 0)
    assert res_low["risk_level"] == "Low"


@pytest.mark.asyncio
async def test_api_404_not_found_branches(client: AsyncClient, auth_headers: dict):
    fake_id = str(uuid4())

    assert (await client.get(f"/api/v1/trust/{fake_id}")).status_code == 404
    assert (await client.get(f"/api/v1/risk/{fake_id}")).status_code == 404
    assert (await client.get(f"/api/v1/companies/{fake_id}")).status_code == 404
    assert (await client.get(f"/api/v1/reviews/{fake_id}", headers=auth_headers)).status_code == 404


@pytest.mark.asyncio
async def test_auth_duplicate_and_invalid_branches(client: AsyncClient):
    uid = uuid4().hex[:6]
    user_payload = {
        "email": f"user_{uid}@example.com",
        "username": f"user_{uid}",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }
    # Register user 1
    r1 = await client.post("/api/v1/auth/register", json=user_payload)
    assert r1.status_code == 201

    # Duplicate email registration
    dup_email_payload = {**user_payload, "username": f"other_{uid}"}
    r2 = await client.post("/api/v1/auth/register", json=dup_email_payload)
    assert r2.status_code == 401
    assert r2.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Invalid login password
    invalid_login = {"username": f"user_{uid}", "password": "WrongPassword123!"}
    r3 = await client.post("/api/v1/auth/login", json=invalid_login)
    assert r3.status_code == 401
    assert r3.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Non-existent user login
    r4 = await client.post("/api/v1/auth/login", json={"username": "non_existent_user", "password": "Password123!"})
    assert r4.status_code == 401


@pytest.mark.asyncio
async def test_review_analysis_and_retrieval_workflow(client: AsyncClient, auth_headers: dict):
    # 1. Create company
    c_resp = await client.post("/api/v1/companies/", json={
        "name": "Audit Target Corp",
        "domain": f"audittarget_{uuid4().hex[:6]}.com",
        "industry": "Fintech"
    }, headers=auth_headers)
    assert c_resp.status_code == 201
    comp_id = c_resp.json()["company_id"]

    # 2. Analyze review
    rev_resp = await client.post("/api/v1/reviews/analyze", json={
        "company_id": comp_id,
        "source": "Trustpilot",
        "rating": 4.5,
        "raw_text": "Excellent platform! Contact support@audittarget.com for questions."
    }, headers=auth_headers)
    assert rev_resp.status_code == 201
    rev_id = rev_resp.json()["review"]["review_id"]

    # 3. Retrieve review by ID
    get_rev = await client.get(f"/api/v1/reviews/{rev_id}", headers=auth_headers)
    assert get_rev.status_code == 200
    assert get_rev.json()["review"]["review_id"] == rev_id
    assert "[EMAIL REDACTED]" in get_rev.json()["review"]["cleaned_text"]

    # 4. Review non-existent company 404
    fake_id = str(uuid4())
    bad_rev = await client.post("/api/v1/reviews/analyze", json={
        "company_id": fake_id,
        "source": "BBB",
        "rating": 1.0,
        "raw_text": "Bad"
    }, headers=auth_headers)
    assert bad_rev.status_code == 404


@pytest.mark.asyncio
async def test_enabled_subsystem_flags_error_handling(client: AsyncClient, auth_headers: dict):
    old_ollama = settings.ENABLE_OLLAMA
    old_qdrant = settings.ENABLE_QDRANT
    old_crew = settings.ENABLE_CREWAI

    try:
        settings.ENABLE_OLLAMA = True
        settings.ENABLE_QDRANT = True
        settings.ENABLE_CREWAI = True

        # Chat when enabled should catch missing ollama/qdrant dependencies cleanly and return 503
        chat_resp = await client.post("/api/v1/chat/", json={"query": "Test query"})
        assert chat_resp.status_code == 503
        assert chat_resp.json()["error"]["code"] == "RAG_SERVICE_UNAVAILABLE"

        # Reports when enabled without evidence should return 503 evidence unavailable (non-existent company returns 404)
        report_404 = await client.post("/api/v1/reports/generate", json={"company_id": str(uuid4())}, headers=auth_headers)
        assert report_404.status_code == 404

        # Create company + analyze review to generate real DB evidence
        c_res = await client.post("/api/v1/companies/", json={"name": "Report Evidence Corp", "domain": f"repevid_{uuid4().hex[:6]}.com", "industry": "SaaS"}, headers=auth_headers)
        c_id = c_res.json()["company_id"]

        # Reports when company has no reviews returns 503 evidence unavailable
        report_no_evidence = await client.post("/api/v1/reports/generate", json={"company_id": c_id}, headers=auth_headers)
        assert report_no_evidence.status_code == 503
        assert report_no_evidence.json()["error"]["code"] == "CREWAI_EVIDENCE_UNAVAILABLE"

        # Add review with ML analysis
        await client.post("/api/v1/reviews/analyze", json={"company_id": c_id, "source": "G2", "rating": 5.0, "raw_text": "Outstanding SaaS platform, fast response times."}, headers=auth_headers)

        # Reports with valid DB evidence returns 200 report markdown
        report_ok = await client.post("/api/v1/reports/generate", json={"company_id": c_id}, headers=auth_headers)
        assert report_ok.status_code == 200
        assert report_ok.json()["company_name"] == "Report Evidence Corp"
        assert "report_markdown" in report_ok.json()

    finally:
        settings.ENABLE_OLLAMA = old_ollama
        settings.ENABLE_QDRANT = old_qdrant
        settings.ENABLE_CREWAI = old_crew


@pytest.mark.asyncio
async def test_all_authenticated_endpoints_and_rag_branches(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    # 1. Create company
    domain = f"testcorp_{uuid4().hex[:6]}.com"
    c_resp = await client.post("/api/v1/companies/", json={
        "name": "Test Coverage Corp",
        "domain": domain,
        "industry": "Ecommerce"
    }, headers=auth_headers)
    assert c_resp.status_code == 201
    comp_id = c_resp.json()["company_id"]

    # Test duplicate domain registration 401
    dup_comp = await client.post("/api/v1/companies/", json={
        "name": "Test Coverage Corp 2",
        "domain": domain,
        "industry": "Ecommerce"
    }, headers=auth_headers)
    assert dup_comp.status_code == 401

    # Companies endpoints
    list_c = await client.get("/api/v1/companies/", headers=auth_headers)
    assert list_c.status_code == 200
    get_c = await client.get(f"/api/v1/companies/{comp_id}", headers=auth_headers)
    assert get_c.status_code == 200

    # 2. Add a review to company
    rev_resp = await client.post("/api/v1/reviews/analyze", json={
        "company_id": comp_id,
        "source": "Google Reviews",
        "rating": 5.0,
        "raw_text": "Great service! Contact owner at CEO@testcorp.com or 555-123-4567."
    }, headers=auth_headers)
    assert rev_resp.status_code == 201

    # Trust endpoint
    trust_resp = await client.get(f"/api/v1/trust/{comp_id}", headers=auth_headers)
    assert trust_resp.status_code == 200
    assert trust_resp.json()["company_id"] == comp_id

    # Risk endpoints
    risk_comp = await client.get(f"/api/v1/risk/{comp_id}", headers=auth_headers)
    assert risk_comp.status_code == 200

    # Alerts endpoints
    alerts_list = await client.get("/api/v1/alerts/", headers=auth_headers)
    assert alerts_list.status_code == 200
    alerts_sum = await client.get("/api/v1/alerts/summary", headers=auth_headers)
    assert alerts_sum.status_code == 200

    # Search endpoints
    s_comp = await client.get("/api/v1/search/?q=Test", headers=auth_headers)
    assert s_comp.status_code == 200
    nl_q = await client.get("/api/v1/search/nl?prompt=Show+ecommerce+companies", headers=auth_headers)
    assert nl_q.status_code == 200

    # Non-existent company 404s
    fake_uuid = str(uuid4())
    assert (await client.get(f"/api/v1/companies/{fake_uuid}", headers=auth_headers)).status_code == 404
    assert (await client.get(f"/api/v1/trust/{fake_uuid}", headers=auth_headers)).status_code == 404
    assert (await client.get(f"/api/v1/risk/{fake_uuid}", headers=auth_headers)).status_code == 404

    # Direct DB execution with existing db_session
    from backend.app.api.v1.endpoints import search, alerts, risk, trust, companies
    from uuid import UUID as PyUUID

    await search.global_search(q="Test", db=db_session)
    await search.natural_language_search(prompt="Show fintech companies", db=db_session)
    await alerts.get_active_alerts(db=db_session)
    await alerts.get_alerts_summary(db=db_session)
    await risk.get_risk_score(company_id=PyUUID(comp_id), db=db_session)
    await trust.get_trust_score(company_id=PyUUID(comp_id), db=db_session)
    await companies.list_companies(limit=10, offset=0, db=db_session)
    await companies.get_company(company_id=PyUUID(comp_id), db=db_session)


@pytest.mark.asyncio
async def test_liveness_and_readiness_probes(client: AsyncClient):
    root_res = await client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["status"] == "online"

    health_res = await client.get("/healthz")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "ok"

    ready_res = await client.get("/readyz")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"

