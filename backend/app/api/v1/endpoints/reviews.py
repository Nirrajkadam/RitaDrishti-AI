"""
RitaDrishti-AI — Reviews API & Real-Time ML Analysis Endpoint

Authenticated vertical workflow:
Sanitizes raw text -> Runs ML inference -> Atomically persists review + AI analysis -> Returns structured payload.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.app.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.sanitizer import sanitize_text
from backend.app.core.exceptions import EntityNotFoundError, AuthenticationError, ServiceUnavailableError
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
    Authenticated endpoint. PII is redacted before storage.
    """
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(review_in.company_id)
    if not company:
        raise EntityNotFoundError(f"Company with ID '{review_in.company_id}' not found.")

    # 1. PII Sanitization (Redact emails, phone numbers, credit cards, SSNs)
    cleaned_text = sanitize_text(review_in.raw_text)

    # 2. Model Inference (Scikit-Learn baseline or ONNX/QNN NPU hardware acceleration)
    npu_metadata = {}
    if settings.ENABLE_NPU:
        from pathlib import Path
        from backend.app.ml.onnx_engine import OnnxReviewEngine

        onnx_dir = Path("backend/app/ml/artifacts/onnx")
        if not onnx_dir.exists() or not (onnx_dir / "tokenizer.json").exists():
            onnx_dir = Path("backend/app/ml")

        try:
            onnx_engine = OnnxReviewEngine(onnx_dir)
            onnx_score = onnx_engine.score(cleaned_text)
            fake_prob = float(onnx_score["fake_probability"])
            is_suspicious = fake_prob >= 0.5
            npu_metadata = {
                "accelerator_mode": "npu",
                "onnx_model": onnx_engine.info_dict.get("model", "unknown"),
                "active_execution_provider": onnx_engine.info.active_providers[0] if onnx_engine.info.active_providers else "CPUExecutionProvider",
                "npu_accelerated": onnx_engine.info.npu_active,
                "accelerator_label": onnx_engine.info.label,
            }
            fake_audit = {
                "fake_probability": fake_prob,
                "is_suspicious": is_suspicious,
                "model": f"ONNX-Transformer ({onnx_engine.info.label})",
                "features": {
                    "onnx_fake_prob": round(fake_prob, 4),
                    **npu_metadata
                }
            }
        except Exception as err:
            raise ServiceUnavailableError(
                code="NPU_ACCELERATOR_UNAVAILABLE",
                message=f"NPU hardware acceleration is enabled (ENABLE_NPU=true), but ONNX execution failed: {err}"
            )
    else:
        fake_audit = fake_engine.predict_fake_probability(
            text=cleaned_text,
            rating=review_in.rating,
            is_verified=False
        )

    # 3. Sentiment Analysis
    sentiment = sentiment_engine.analyze_sentiment(cleaned_text)
    sentiment_score = float(sentiment.get("score", 0.0))
    sentiment_label = str(sentiment.get("label", "neutral"))

    # 4. Atomic Transactional Persistence (Ensure stored raw_text is sanitized as well)
    review_repo = ReviewRepository(db)
    review_obj, analysis_obj = await review_repo.create_review_with_analysis(
        company_id=review_in.company_id,
        user_id=current_user.user_id,
        source=review_in.source,
        rating=review_in.rating,
        raw_text=cleaned_text,  # Redacted PII persisted
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
