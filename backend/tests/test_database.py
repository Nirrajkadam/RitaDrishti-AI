"""
RitaDrishti-AI — Database Repositories Unit Tests
"""

import pytest
from uuid import uuid4
from backend.app.db.repositories import UserRepository, CompanyRepository, ReviewRepository
from backend.app.core.security import verify_password


@pytest.mark.asyncio
async def test_user_repository_crud(db_session):
    repo = UserRepository(db_session)
    user = await repo.create_user(
        email="dev@ritadrishti.ai",
        username="devuser",
        password="SecurePassword123!",
        full_name="Dev User"
    )
    assert user.user_id is not None
    assert user.username == "devuser"
    assert verify_password("SecurePassword123!", user.hashed_password)

    fetched_by_user = await repo.get_user_by_username("devuser")
    assert fetched_by_user is not None
    assert fetched_by_user.email == "dev@ritadrishti.ai"

    fetched_by_email = await repo.get_user_by_email("dev@ritadrishti.ai")
    assert fetched_by_email is not None
    assert fetched_by_email.user_id == user.user_id


@pytest.mark.asyncio
async def test_company_repository_crud(db_session):
    repo = CompanyRepository(db_session)
    company = await repo.create_company(
        name="Acme Cloud",
        domain="acmecloud.io",
        industry="Cloud SaaS",
        description="Cloud provider",
        country_code="US"
    )
    assert company.company_id is not None
    assert company.domain == "acmecloud.io"

    fetched = await repo.get_by_id(company.company_id)
    assert fetched is not None
    assert fetched.name == "Acme Cloud"

    fetched_domain = await repo.get_by_domain("acmecloud.io")
    assert fetched_domain is not None
    assert fetched_domain.company_id == company.company_id

    all_companies = await repo.list_companies()
    assert len(all_companies) == 1


@pytest.mark.asyncio
async def test_review_repository_atomic_transaction(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user(email="reviewer@test.com", username="reviewer", password="Password123!")

    comp_repo = CompanyRepository(db_session)
    company = await comp_repo.create_company(name="Test Corp", domain="testcorp.com", industry="Tech")

    review_repo = ReviewRepository(db_session)
    review_obj, analysis_obj = await review_repo.create_review_with_analysis(
        company_id=company.company_id,
        user_id=user.user_id,
        source="Trustpilot",
        rating=5.0,
        raw_text="Excellent service and quick support!",
        cleaned_text="Excellent service and quick support!",
        reviewer_name="Jane Doe",
        fake_probability=0.05,
        is_suspicious=False,
        sentiment_score=0.85,
        sentiment_label="positive",
        feature_metrics={"word_count": 5},
        model_version="v1.0.0"
    )

    assert review_obj.review_id is not None
    assert analysis_obj.analysis_id is not None
    assert analysis_obj.review_id == review_obj.review_id
    assert analysis_obj.fake_probability == 0.05

    fetched_pair = await review_repo.get_review_with_analysis(review_obj.review_id)
    assert fetched_pair is not None
    r, a = fetched_pair
    assert r.review_id == review_obj.review_id
    assert a.analysis_id == analysis_obj.analysis_id
