"""
RitaDrishti-AI — Behaviorally Asserted Endpoint Function Unit & Integration Tests
Directly tests endpoint logic with real database state and full assertions.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.db.repositories import CompanyRepository, UserRepository, ReviewRepository
from backend.app.db.schemas import AuditReportRequest, ReviewCreate, CompanyCreate
from backend.app.api.v1.endpoints import (
    alerts, search, risk, trust, reports, reviews, companies
)


@pytest.mark.asyncio
async def test_asserted_alerts_endpoint_functions(db_session: AsyncSession):
    # Create user & company
    u_repo = UserRepository(db_session)
    user = await u_repo.create_user("alert_user@example.com", "alert_user", "Pass123!", "Alert User")
    c_repo = CompanyRepository(db_session)
    comp = await c_repo.create_company("Alert Corp", f"alert_{uuid4().hex[:6]}.com", "Security")

    # Add high fake probability review
    r_repo = ReviewRepository(db_session)
    await r_repo.create_review_with_analysis(
        company_id=comp.company_id,
        user_id=user.user_id,
        source="Trustpilot",
        rating=5.0,
        raw_text="BEST PRODUCT EVER SCAM 100% BUY NOW",
        cleaned_text="BEST PRODUCT EVER SCAM 100% BUY NOW",
        reviewer_name="Spammer",
        fake_probability=0.92,
        is_suspicious=True,
        sentiment_score=0.8,
        sentiment_label="positive",
        feature_metrics={"word_count": 7},
        model_version="v1.0.0"
    )

    # Call get_active_alerts with assertions
    active = await alerts.get_active_alerts(db=db_session)
    assert len(active) >= 1
    assert active[0]["type"] == "Fraud Alert"
    assert active[0]["company_name"] == "Alert Corp"
    assert active[0]["severity"] == "CRITICAL"
    assert "Suspicious Review Cluster" in active[0]["title"]

    # Call get_alerts_summary with assertions
    summary = await alerts.get_alerts_summary(db=db_session)
    assert summary["total_active_alerts"] >= 1
    assert summary["critical_count"] >= 1


@pytest.mark.asyncio
async def test_asserted_search_risk_and_trust_endpoint_functions(db_session: AsyncSession):
    u_repo = UserRepository(db_session)
    user = await u_repo.create_user("search_user@example.com", "search_user", "Pass123!", "Search User")
    c_repo = CompanyRepository(db_session)
    comp = await c_repo.create_company("FinTech Innovations", f"fintech_{uuid4().hex[:6]}.com", "Fintech")

    r_repo = ReviewRepository(db_session)
    await r_repo.create_review_with_analysis(
        company_id=comp.company_id,
        user_id=user.user_id,
        source="G2",
        rating=4.0,
        raw_text="Good financial platform.",
        cleaned_text="Good financial platform.",
        reviewer_name="Analyst",
        fake_probability=0.05,
        is_suspicious=False,
        sentiment_score=0.6,
        sentiment_label="positive",
        feature_metrics={"word_count": 3},
        model_version="v1.0.0"
    )

    # Search functions
    glob_res = await search.global_search(q="FinTech", db=db_session)
    assert glob_res["count"] >= 1
    assert glob_res["results"][0]["name"] == "FinTech Innovations"

    nl_res = await search.natural_language_search(prompt="Show Fintech companies", db=db_session)
    assert nl_res["count"] >= 1
    assert nl_res["results"][0]["name"] == "FinTech Innovations"


    # Risk score function
    risk_res = await risk.get_risk_score(company_id=comp.company_id, db=db_session)
    assert risk_res.company_id == comp.company_id
    assert risk_res.risk_level in ["Low", "Moderate", "High", "Severe"]

    # Trust score function
    trust_res = await trust.get_trust_score(company_id=comp.company_id, db=db_session)
    assert trust_res.company_id == comp.company_id
    assert trust_res.trust_tier in ["High Trust", "Moderate Trust", "Low Trust", "Critical Alert"]


@pytest.mark.asyncio
async def test_asserted_reports_and_reviews_endpoint_functions(db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "ENABLE_CREWAI", True)

    u_repo = UserRepository(db_session)
    user = await u_repo.create_user("report_user@example.com", "report_user", "Pass123!", "Report User")
    c_repo = CompanyRepository(db_session)
    comp = await c_repo.create_company("Audit Target Corp", f"audit_{uuid4().hex[:6]}.com", "Cloud")

    rev_in = ReviewCreate(
        company_id=comp.company_id,
        source="Trustpilot",
        rating=5.0,
        raw_text="Awesome service! Contact sales@audit.com or 555-999-0000."
    )

    # Analyze review endpoint function
    rev_res = await reviews.analyze_and_persist_review(review_in=rev_in, current_user=user, db=db_session)
    assert rev_res.review.company_id == comp.company_id
    assert "[EMAIL REDACTED]" in rev_res.review.cleaned_text
    rev_id = rev_res.review.review_id

    # Get review by ID endpoint function
    get_rev = await reviews.get_review_by_id(review_id=rev_id, current_user=user, db=db_session)
    assert get_rev.review.review_id == rev_id

    # Generate executive report endpoint function
    rep_req = AuditReportRequest(company_id=comp.company_id)
    rep_res = await reports.generate_executive_report(req=rep_req, current_user=user, db=db_session)
    assert rep_res["company_name"] == "Audit Target Corp"
    assert "report_markdown" in rep_res


@pytest.mark.asyncio
async def test_asserted_company_endpoint_functions(db_session: AsyncSession):
    u_repo = UserRepository(db_session)
    user = await u_repo.create_user("company_user@example.com", "company_user", "Pass123!", "Company User")

    comp_in = CompanyCreate(
        name="Direct Comp Corp",
        domain=f"direct_{uuid4().hex[:6]}.com",
        industry="Hardware",
        description="Hardware manufacturing"
    )

    created = await companies.create_company(company_in=comp_in, current_user=user, db=db_session)
    assert created.name == "Direct Comp Corp"

    fetched = await companies.get_company(company_id=created.company_id, db=db_session)
    assert fetched.company_id == created.company_id

    listed = await companies.list_companies(limit=10, offset=0, db=db_session)
    assert len(listed) >= 1
