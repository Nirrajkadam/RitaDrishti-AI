"""
SentinelX Trust AI — Reviews API & Real-Time ML Analysis Endpoint
"""

from fastapi import APIRouter, HTTPException
from app.db.schemas import ReviewCreate
from app.ml.sentiment_engine import SentimentEngine
from app.ml.fake_review_engine import FakeReviewEngine
from app.ingestion.etl_pipeline import DataCleaningPipeline

router = APIRouter()

sentiment_engine = SentimentEngine()
fake_engine = FakeReviewEngine()
cleaner = DataCleaningPipeline()

@router.post("/analyze")
async def analyze_single_review(review: ReviewCreate):
    """
    Ingests and analyzes a review in real-time.
    Applies ETL cleaning, sentiment classification, and fake review detection.
    """
    cleaned_text = cleaner.clean_text(review.raw_text)
    sentiment = sentiment_engine.analyze_sentiment(cleaned_text)
    fake_audit = fake_engine.predict_fake_probability(cleaned_text, rating=review.rating)

    return {
        "company_id": review.company_id,
        "source": review.source,
        "rating": review.rating,
        "raw_text": review.raw_text,
        "cleaned_text": cleaned_text,
        "sentiment_analysis": sentiment,
        "fake_review_detection": fake_audit
    }
