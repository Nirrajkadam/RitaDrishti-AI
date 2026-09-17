"""
SentinelX Trust AI — Ingestion ETL & Cleaning Pipeline
Cleans raw text, strips HTML tags, redacts PII (emails, phone numbers, cards), deduplicates text, and normalizes fields.
"""

import re
import hashlib
from typing import Dict, List, Any


class DataCleaningPipeline:
    def __init__(self):
        # PII Regex Patterns
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.card_pattern = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        self.html_pattern = re.compile(r'<[^>]+>')

    def clean_text(self, text: str) -> str:
        """Strips HTML, redacts PII, removes noise, and normalizes whitespace."""
        if not text:
            return ""

        # 1. Strip HTML tags
        text = self.html_pattern.sub('', text)

        # 2. Redact PII
        text = self.email_pattern.sub('[REDACTED_EMAIL]', text)
        text = self.phone_pattern.sub('[REDACTED_PHONE]', text)
        text = self.card_pattern.sub('[REDACTED_CARD]', text)

        # 3. Normalize whitespace & punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def compute_text_hash(self, text: str) -> str:
        """Computes MD5 hash of normalized text for instant duplicate detection."""
        clean_str = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        return hashlib.md5(clean_str.encode('utf-8')).hexdigest()

    def deduplicate_records(self, records: List[Dict[str, Any]], text_key: str = "raw_text") -> List[Dict[str, Any]]:
        """Removes exact and near-duplicate text records from ingestion stream."""
        seen_hashes = set()
        unique_records = []

        for record in records:
            raw = record.get(text_key, "")
            if not raw:
                continue

            text_hash = self.compute_text_hash(raw)
            if text_hash not in seen_hashes:
                seen_hashes.add(text_hash)
                record["cleaned_text"] = self.clean_text(raw)
                record["content_hash"] = text_hash
                unique_records.append(record)

        return unique_records


class ETLPipeline:
    def __init__(self):
        self.cleaner = DataCleaningPipeline()

    def process_raw_reviews(self, raw_reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Runs ETL transform process on ingested raw reviews."""
        cleaned = self.cleaner.deduplicate_records(raw_reviews, text_key="raw_text")
        for item in cleaned:
            # Ensure rating bounds
            rating = item.get("rating", 3.0)
            item["rating"] = max(1.0, min(5.0, float(rating)))
        return cleaned


if __name__ == "__main__":
    sample = [
        {"raw_text": "Great service! Contact me at user@example.com or 555-123-4567.", "rating": 5},
        {"raw_text": "Great service! Contact me at user@example.com or 555-123-4567.", "rating": 5}, # Duplicate
        {"raw_text": "<b>Horrible refund policy!</b> Never using them again.", "rating": 1}
    ]
    etl = ETLPipeline()
    processed = etl.process_raw_reviews(sample)
    print(f"Processed {len(processed)} unique items:")
    for p in processed:
        print(" ->", p["cleaned_text"])
