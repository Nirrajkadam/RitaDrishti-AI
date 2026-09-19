"""
Unit tests for data cleaning & ETL pipeline
"""

import pytest
from backend.app.ingestion.etl_pipeline import DataCleaningPipeline, ETLPipeline


def test_data_cleaning_pipeline_pii_redaction():
    cleaner = DataCleaningPipeline()
    raw = "<p>Contact me at user@test.com or +1 555-123-4567. Card: 4111 2222 3333 4444</p>"
    cleaned = cleaner.clean_text(raw)
    assert "<p>" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_PHONE]" in cleaned
    assert "[REDACTED_CARD]" in cleaned


def test_data_cleaning_empty_text():
    cleaner = DataCleaningPipeline()
    assert cleaner.clean_text("") == ""


def test_deduplicate_records():
    cleaner = DataCleaningPipeline()
    records = [
        {"raw_text": "Great service!", "rating": 5},
        {"raw_text": "Great service!", "rating": 5},
        {"raw_text": "Another review", "rating": 4},
        {"raw_text": ""}
    ]
    unique = cleaner.deduplicate_records(records)
    assert len(unique) == 2
    assert unique[0]["cleaned_text"] == "Great service!"
    assert unique[1]["cleaned_text"] == "Another review"


def test_etl_pipeline_process_raw_reviews():
    etl = ETLPipeline()
    records = [
        {"raw_text": "Excellent cloud platform", "rating": 10},  # clamped to 5.0
        {"raw_text": "Poor uptime", "rating": -2}  # clamped to 1.0
    ]
    processed = etl.process_raw_reviews(records)
    assert len(processed) == 2
    assert processed[0]["rating"] == 5.0
    assert processed[1]["rating"] == 1.0
