"""
RitaDrishti-AI — ML Engine & Sanitizer Unit Tests
"""

import pytest
import os
import tempfile
from backend.app.ml.fake_review_engine import FakeReviewEngine
from backend.app.core.sanitizer import sanitize_text
from backend.app.core.exceptions import ServiceUnavailableError


def test_pii_sanitization():
    raw = "Contact john.doe@example.com or call +1-555-123-4567. Card: 4111111111111111 SSN: 123-45-6789."
    sanitized = sanitize_text(raw)
    assert "[EMAIL REDACTED]" in sanitized
    assert "[PHONE REDACTED]" in sanitized
    assert "[CARD REDACTED]" in sanitized
    assert "[SSN REDACTED]" in sanitized
    assert "john.doe@example.com" not in sanitized


def test_fake_review_engine_legitimate_inference():
    engine = FakeReviewEngine()
    text = "We have been using Acme Cloud for 6 months. Performance is reliable and support is responsive."
    result = engine.predict_fake_probability(text, rating=4.0, is_verified=True)
    
    assert "fake_probability" in result
    assert result["fake_probability"] < 0.50
    assert result["is_suspicious"] is False
    assert "features" in result


def test_fake_review_engine_deceptive_inference():
    engine = FakeReviewEngine()
    text = "BEST PRODUCT EVER!!! MUST BUY HIGHLY RECOMMENDED 100% FIVE STARS RATING!!"
    result = engine.predict_fake_probability(text, rating=5.0, is_verified=False)

    assert "fake_probability" in result
    assert result["fake_probability"] > 0.50
    assert result["is_suspicious"] is True


def test_fake_review_engine_missing_artifact_raises_503():
    with tempfile.TemporaryDirectory() as empty_dir:
        with pytest.raises(ServiceUnavailableError) as exc_info:
            FakeReviewEngine(model_dir=empty_dir)
        assert exc_info.value.code == "MODEL_ARTIFACT_MISSING"
        assert exc_info.value.status_code == 503
