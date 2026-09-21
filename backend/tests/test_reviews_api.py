"""
RitaDrishti-AI — End-to-End Vertical Review Analysis & Persistence Integration Tests
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_end_to_end_vertical_review_workflow(client: AsyncClient, auth_headers: dict):
    # 1. Create Company
    company_payload = {
        "name": "CloudScale Systems",
        "domain": "cloudscale.io",
        "industry": "DevOps",
        "description": "Cloud infrastructure automation platform.",
        "country_code": "US"
    }
    comp_resp = await client.post("/api/v1/companies/", json=company_payload, headers=auth_headers)
    assert comp_resp.status_code == 201
    company_data = comp_resp.json()
    company_id = company_data["company_id"]

    # 2. Submit & Analyze Review with PII
    review_payload = {
        "company_id": company_id,
        "source": "G2 Crowd",
        "rating": 5.0,
        "raw_text": "BEST PRODUCT EVER!!! Contact john.doe@example.com for discounts. MUST BUY 100% FIVE STARS RATING!!",
        "reviewer_name": "Verified Buyer"
    }
    analyze_resp = await client.post("/api/v1/reviews/analyze", json=review_payload, headers=auth_headers)
    assert analyze_resp.status_code == 201
    result = analyze_resp.json()

    assert "review" in result
    assert "analysis" in result

    review = result["review"]
    analysis = result["analysis"]

    # Verify PII Sanitization
    assert "[EMAIL REDACTED]" in review["cleaned_text"]
    assert "john.doe@example.com" not in review["cleaned_text"]

    # Verify ML Model Inference
    assert analysis["fake_probability"] > 0.50
    assert analysis["is_suspicious"] is True
    assert analysis["analysis_id"] is not None

    review_id = review["review_id"]

    # 3. Retrieve Persisted Review & Analysis
    get_resp = await client.get(f"/api/v1/reviews/{review_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    retrieved = get_resp.json()

    assert retrieved["review"]["review_id"] == review_id
    assert retrieved["analysis"]["fake_probability"] == analysis["fake_probability"]


@pytest.mark.asyncio
async def test_review_analysis_non_existent_company(client: AsyncClient, auth_headers: dict):
    fake_company_id = str(uuid4())
    review_payload = {
        "company_id": fake_company_id,
        "source": "Trustpilot",
        "rating": 4.0,
        "raw_text": "Great service!"
    }
    resp = await client.post("/api/v1/reviews/analyze", json=review_payload, headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ENTITY_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_non_existent_review(client: AsyncClient, auth_headers: dict):
    fake_review_id = str(uuid4())
    resp = await client.get(f"/api/v1/reviews/{fake_review_id}", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ENTITY_NOT_FOUND"


@pytest.mark.asyncio
async def test_onnx_npu_review_analysis_workflow(client: AsyncClient, auth_headers: dict, monkeypatch):
    from backend.app.config import settings
    monkeypatch.setattr(settings, "ENABLE_NPU", True)

    company_payload = {
        "name": "NPU MicroSystems",
        "domain": "npumicro.com",
        "industry": "Semiconductors",
        "description": "Qualcomm Snapdragon NPU testing company.",
        "country_code": "US"
    }
    comp_resp = await client.post("/api/v1/companies/", json=company_payload, headers=auth_headers)
    assert comp_resp.status_code == 201
    company_id = comp_resp.json()["company_id"]

@pytest.mark.asyncio
async def test_onnx_npu_review_analysis_error_handling(client: AsyncClient, auth_headers: dict, monkeypatch):
    from backend.app.config import settings
    monkeypatch.setattr(settings, "ENABLE_NPU", True)

    company_payload = {
        "name": "NPU Error test",
        "domain": "npuerror.com",
        "industry": "Testing",
        "description": "NPU error handling test.",
        "country_code": "US"
    }
    comp_resp = await client.post("/api/v1/companies/", json=company_payload, headers=auth_headers)
    assert comp_resp.status_code == 201
    company_id = comp_resp.json()["company_id"]

    review_payload = {
        "company_id": company_id,
        "source": "ErrorTest",
        "rating": 1.0,
        "raw_text": "Testing NPU exception path when model dir is invalid."
    }
    
    # Mock OnnxReviewEngine to raise an exception
    def mock_init(*args, **kwargs):
        raise RuntimeError("Simulated NPU session error")

    monkeypatch.setattr("backend.app.ml.onnx_engine.OnnxReviewEngine.__init__", mock_init)

    resp = await client.post("/api/v1/reviews/analyze", json=review_payload, headers=auth_headers)
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "NPU_ACCELERATOR_UNAVAILABLE"


