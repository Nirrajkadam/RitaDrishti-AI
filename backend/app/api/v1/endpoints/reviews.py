"""
RitaDrishti-AI — Reviews API & Real-Time ML Analysis Endpoint

Authenticated vertical workflow:
Sanitizes raw text -> Runs ML inference -> Atomically persists review + AI analysis -> Returns structured payload.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.sanitizer import sanitize_text
from backend.app.core.exceptions import EntityNotFoundError, AuthenticationError
from backend.app.db.models import UserModel
from backend.app.db.repositories import ReviewRepository, CompanyRepository
from backend.app.db.schemas import ReviewCreate, ReviewWithAnalysisResponse, ReviewResponse, AIAnalysisResponse
from backend.app.ml.fake_review_engine import FakeReviewEngine
from backend.app.ml.sentiment_engine import SentimentEngine

router = APIRouter()

fake_engine = FakeReviewEngine()
sentiment_engine = SentimentEngine()


@router.post("/analyze", response_model=ReviewWithAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_and_persist_review(
    review_in: ReviewCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits, sanitizes, analyzes, and persists a review with ML fake review classification.
    Authenticated endpoint.
    """
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(review_in.company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{review_in.company_id}' not found.")

    # 1. PII Sanitization
    cleaned_text = sanitize_text(review_in.raw_text)

    # 2. Model Inference
    fake_audit = fake_engine.predict_fake_probability(
        text=cleaned_text,
        rating=review_in.rating,
        is_verified=False
    )

    # 3. Sentiment Analysis
    sentiment = sentiment_engine.analyze_sentiment(cleaned_text)
    sentiment_score = float(sentiment.get("polarity", 0.0))
    sentiment_label = str(sentiment.get("label", "neutral"))

    # 4. Atomic Transactional Persistence
    review_repo = ReviewRepository(db)
    review_obj, analysis_obj = await review_repo.create_review_with_analysis(
        company_id=review_in.company_id,
        user_id=current_user.user_id,
        source=review_in.source,
        rating=review_in.rating,
        raw_text=review_in.raw_text,
        cleaned_text=cleaned_text,
        reviewer_name=review_in.reviewer_name or "Anonymous",
        fake_probability=fake_audit["fake_probability"],
        is_suspicious=fake_audit["is_suspicious"],
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        feature_metrics=fake_audit["features"],
        model_version=fake_audit["model"]
    )

    return ReviewWithAnalysisResponse(
        review=ReviewResponse.model_validate(review_obj),
        analysis=AIAnalysisResponse.model_validate(analysis_obj)
    )


@router.get("/{review_id}", response_model=ReviewWithAnalysisResponse)
async def get_review_by_id(
    review_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves review and its ML analysis details by review_id.
    Authenticated endpoint.
    """
    review_repo = ReviewRepository(db)
    result = await review_repo.get_review_with_analysis(review_id)
    if not result:
        raise EntityNotFoundError(f"Review with ID '{review_id}' not found.")

    review_obj, analysis_obj = result
    return ReviewWithAnalysisResponse(
        review=ReviewResponse.model_validate(review_obj),
        analysis=AIAnalysisResponse.model_validate(analysis_obj)
    )
