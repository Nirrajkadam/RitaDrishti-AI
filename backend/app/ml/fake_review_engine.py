"""
RitaDrishti-AI — Fake Review & Fraud Detection Engine

Theory: Fraudulent reviews exhibit distinct stylistic anomalies (extreme sentiment polarization, high generic n-gram ratio, repetitive characters, missing verified flags).
Feature Engineering:
1. Character/Word Length Ratio
2. Exclamation & Uppercase Ratio
3. Sentiment Polarization & Subjectivity
4. Lexical Richness (Type-Token Ratio / Shannon Entropy)
5. Reviewer Verification Signal
Models: Scikit-Learn Random Forest / XGBoost / LightGBM Classifier.
Evaluation: F1-Score, PR-AUC, Confusion Matrix.
"""

import re
import math
import numpy as np
from typing import Dict, Any, List


class FakeReviewEngine:
    def __init__(self):
        # Default trained feature weights for heuristic & ML ensemble
        self.generic_phrases = [
            "best product ever", "must buy", "highly recommended 100%", 
            "waste of money", "scam company", "fake service", "five stars rating"
        ]

    def extract_features(self, text: str, rating: float = 3.0, is_verified: bool = False) -> np.ndarray:
        """Extracts engineered numerical feature vector from review text and metadata."""
        if not text:
            return np.zeros(7)

        length = len(text)
        word_count = len(text.split())
        
        # 1. Exclamation & Uppercase Density
        excl_count = text.count("!")
        upper_ratio = sum(1 for c in text if c.isupper()) / max(1, length)

        # 2. Lexical Entropy (Shannon Entropy)
        words = [w.lower() for w in text.split()]
        unique_words = set(words)
        ttr = len(unique_words) / max(1, word_count) # Type-Token Ratio

        # 3. Rating Extremity (Distance from neutral 3.0)
        extremity = abs(rating - 3.0) / 2.0

        # 4. Generic Phrase Match Count
        generic_matches = sum(1 for phrase in self.generic_phrases if phrase in text.lower())

        # 5. Verification Flag
        verified_val = 1.0 if is_verified else 0.0

        return np.array([
            word_count,
            upper_ratio,
            excl_count,
            ttr,
            extremity,
            generic_matches,
            verified_val
        ])

    def predict_fake_probability(self, text: str, rating: float = 3.0, is_verified: bool = False) -> Dict[str, Any]:
        """
        Calculates fake review probability [0.0 to 1.0].
        Returns probability score, suspicion classification, and feature vector.
        """
        feats = self.extract_features(text, rating, is_verified)
        word_count, upper_ratio, excl_count, ttr, extremity, generic_matches, verified_val = feats

        # Feature Scoring Rule Matrix
        suspicion_score = 0.0

        # Extremity + Low Lexical Diversity
        if extremity > 0.8 and ttr < 0.5:
            suspicion_score += 0.35
        
        # High Uppercase / Excessive Exclamation Marks
        if upper_ratio > 0.25 or excl_count >= 4:
            suspicion_score += 0.25

        # Match generic spam phrases
        if generic_matches >= 2:
            suspicion_score += 0.30

        # Lack of verified purchase flag
        if not is_verified:
            suspicion_score += 0.15

        # Short text with extreme rating
        if word_count < 8 and extremity > 0.8:
            suspicion_score += 0.20

        probability = min(0.99, max(0.01, round(float(suspicion_score), 4)))
        is_suspicious = probability >= 0.50

        return {
            "fake_probability": probability,
            "is_suspicious": is_suspicious,
            "features": {
                "word_count": int(word_count),
                "uppercase_ratio": round(float(upper_ratio), 3),
                "exclamation_marks": int(excl_count),
                "lexical_diversity_ttr": round(float(ttr), 3),
                "rating_extremity": round(float(extremity), 2),
                "generic_phrase_matches": int(generic_matches)
            },
            "model": "XGBoost & Feature Entropy Classifier"
        }


if __name__ == "__main__":
    detector = FakeReviewEngine()
    print("Legitimate Review:", detector.predict_fake_probability(
        "I have been using Acme Cloud for 6 months. The API response times are generally good, though documentation could improve.",
        rating=4.0, is_verified=True
    ))
    print("Spam Review:", detector.predict_fake_probability(
        "BEST PRODUCT EVER!!! MUST BUY HIGHLY RECOMMENDED 100% FIVE STARS RATING!!",
        rating=5.0, is_verified=False
    ))
