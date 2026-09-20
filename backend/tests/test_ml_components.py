"""
RitaDrishti-AI — Machine Learning Components Unit Tests
"""

import pytest
from backend.app.ml.trust_score_engine import TrustScoreEngine
from backend.app.ml.risk_prediction import RiskPredictionEngine
from backend.app.ml.correlation_engine import CorrelationEngine
from backend.app.ml.nl_query_engine import NaturalLanguageQueryEngine
from backend.app.ml.sentiment_engine import SentimentEngine
from backend.app.ml.train_fake_review_model import train_and_evaluate_model, build_benchmark_dataset, extract_style_features


def test_trust_score_engine():
    engine = TrustScoreEngine()
    result = engine.calculate_trust_score(
        avg_sentiment_score=0.8,
        avg_fake_prob=0.02,
        total_reviews=100,
        unresolved_complaints=0,
        verified_status=True,
        overall_risk_score=10.0
    )
    assert "trust_index" in result
    assert result["trust_index"] > 70.0
    assert result["trust_tier"] in ["High Trust", "Moderate Trust"]


def test_risk_prediction_engine():
    engine = RiskPredictionEngine()
    result = engine.evaluate_risk(
        fake_review_ratio=0.30,
        unresolved_complaints=6,
        critical_complaints=2,
        negative_sentiment_ratio=0.60,
        negative_news_count=3
    )
    assert "overall_risk_score" in result
    assert result["risk_level"] in ["High", "Severe"]
    assert len(result["anomaly_signals"]) > 0


def test_correlation_engine():
    engine = CorrelationEngine()
    reviews = [{"raw_text": "Outage lost my data", "rating": 1.0}]
    complaints = [{"title": "Data loss outage", "description": "Cloud server down", "severity_level": "high"}]
    news = [{"headline": "Outage impacts cloud software"}]

    result = engine.correlate_signals(reviews=reviews, complaints=complaints, news=news)
    assert result["total_correlated_clusters"] >= 1
    assert "clusters" in result


def test_nl_query_engine():
    engine = NaturalLanguageQueryEngine()
    parsed = engine.parse_query("Show high-risk fintech companies with trust score > 60")
    assert parsed["filters"]["industry"] == "fintech"
    assert parsed["filters"]["risk_level"] == "High"
    assert parsed["filters"]["min_trust_score"] == 60.0

    companies = [
        {"name": "FinPay", "industry": "fintech", "risk_level": "High", "trust_score": 85.0},
        {"name": "Acme", "industry": "cloud", "risk_level": "Low", "trust_score": 90.0}
    ]
    matched = engine.execute_nl_search("Show high-risk fintech companies", companies)
    assert len(matched) == 1
    assert matched[0]["name"] == "FinPay"


def test_sentiment_engine():
    engine = SentimentEngine()
    pos = engine.analyze_sentiment("Excellent service!")
    assert pos["label"] == "positive"
    assert pos["score"] > 0.0

    neg = engine.analyze_sentiment("Horrible scam company!")
    assert neg["label"] == "negative"
    assert neg["score"] < 0.0

    empty = engine.analyze_sentiment("")
    assert empty["label"] == "neutral"


def test_model_training_pipeline_execution(tmp_path):
    df = build_benchmark_dataset()
    assert len(df) > 0
    feats = extract_style_features("TEST REVIEW TEXT", 5.0)
    assert len(feats) == 6

    pipeline, metrics = train_and_evaluate_model()
    assert pipeline is not None
    assert "accuracy" in metrics
    assert "f1_score" in metrics

    from backend.app.ml.train_fake_review_model import export_artifact_and_model_card
    export_artifact_and_model_card(pipeline, metrics, output_dir=tmp_path)
    assert (tmp_path / "fake_review_model.joblib").exists()
    assert (tmp_path / "fake_review_model.joblib.sha256").exists()
    assert (tmp_path / "MODEL_CARD.md").exists()
