"""
RitaDrishti-AI — Real ML Fake Review Classifier & Feature Extraction Engine

Loads trained scikit-learn Pipeline artifact (ColumnTransformer: TF-IDF + Style Metrics -> LogisticRegression),
validates SHA-256 checksum, and performs real model inference.
"""

import os
import hashlib
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

from backend.app.core.exceptions import ServiceUnavailableError

GENERIC_PHRASES = [
    "best product ever", "must buy", "highly recommended 100%", 
    "waste of money", "scam company", "fake service", "five stars rating"
]


class FakeReviewEngine:
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
        
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "fake_review_model.joblib")
        self.checksum_path = os.path.join(model_dir, "fake_review_model.joblib.sha256")
        self._model = None
        self._load_and_verify_model()

    def _load_and_verify_model(self):
        """Loads and verifies SHA-256 hash of the trained joblib model artifact."""
        if not os.path.exists(self.model_path):
            raise ServiceUnavailableError(
                code="MODEL_ARTIFACT_MISSING",
                message=f"Trained model artifact not found at {self.model_path}. Please run train_fake_review_model.py first."
            )
        
        if os.path.exists(self.checksum_path):
            with open(self.checksum_path, "r") as f:
                expected_sha256 = f.read().strip()
            
            hasher = hashlib.sha256()
            with open(self.model_path, "rb") as f:
                hasher.update(f.read())
            actual_sha256 = hasher.hexdigest()

            if actual_sha256 != expected_sha256:
                raise ServiceUnavailableError(
                    code="MODEL_ARTIFACT_INVALID",
                    message="Model artifact SHA-256 checksum verification failed."
                )

        try:
            self._model = joblib.load(self.model_path)
        except Exception as e:
            raise ServiceUnavailableError(
                code="MODEL_LOAD_FAILED",
                message=f"Failed to load fake review model artifact: {str(e)}"
            )

    def extract_style_features(self, text: str, rating: float = 3.0) -> Dict[str, float]:
        """Extracts engineered numerical text style & entropy features."""
        if not text:
            return {
                "word_count": 0.0,
                "upper_ratio": 0.0,
                "excl_count": 0.0,
                "ttr": 0.0,
                "extremity": 0.0,
                "generic_matches": 0.0
            }

        length = len(text)
        words = [w.lower() for w in text.split()]
        word_count = float(len(words))
        
        upper_ratio = sum(1 for c in text if c.isupper()) / max(1.0, float(length))
        excl_count = float(text.count("!"))
        unique_words = set(words)
        ttr = float(len(unique_words)) / max(1.0, word_count) if word_count > 0 else 0.0
        extremity = float(abs(rating - 3.0) / 2.0)
        generic_matches = float(sum(1 for phrase in GENERIC_PHRASES if phrase in text.lower()))

        return {
            "word_count": word_count,
            "upper_ratio": upper_ratio,
            "excl_count": excl_count,
            "ttr": ttr,
            "extremity": extremity,
            "generic_matches": generic_matches
        }

    def predict_fake_probability(self, text: str, rating: float = 3.0, is_verified: bool = False) -> Dict[str, Any]:
        """
        Calculates fake review probability using the trained Pipeline artifact.
        Returns probability score, suspicion classification, and extracted feature vector.
        """
        if self._model is None:
            self._load_and_verify_model()

        feats = self.extract_style_features(text, rating)

        input_df = pd.DataFrame([{
            "text": text,
            "word_count": feats["word_count"],
            "upper_ratio": feats["upper_ratio"],
            "excl_count": feats["excl_count"],
            "ttr": feats["ttr"],
            "extremity": feats["extremity"],
            "generic_matches": feats["generic_matches"]
        }])

        try:
            probabilities = self._model.predict_proba(input_df)[0]
            fake_prob = float(probabilities[1])
        except Exception as e:
            raise ServiceUnavailableError(
                code="MODEL_INFERENCE_FAILED",
                message=f"Model inference execution failed: {str(e)}"
            )

        fake_prob_rounded = round(min(0.9999, max(0.0001, fake_prob)), 4)
        is_suspicious = fake_prob_rounded >= 0.50

        return {
            "fake_probability": fake_prob_rounded,
            "is_suspicious": is_suspicious,
            "features": {
                "word_count": int(feats["word_count"]),
                "uppercase_ratio": round(feats["upper_ratio"], 3),
                "exclamation_marks": int(feats["excl_count"]),
                "lexical_diversity_ttr": round(feats["ttr"], 3),
                "rating_extremity": round(feats["extremity"], 2),
                "generic_phrase_matches": int(feats["generic_matches"]),
                "is_verified": is_verified
            },
            "model": "ColumnTransformer + LogisticRegression Pipeline (v1.0.0)"
        }
