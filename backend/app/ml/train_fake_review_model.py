"""
RitaDrishti-AI — Reproducible Fake Review Model Training Pipeline
Trains a scikit-learn Pipeline (ColumnTransformer: TF-IDF + Style Metrics -> LogisticRegression)
and exports a trusted joblib model artifact along with SHA-256 verification checksum.
"""

import os
import re
import hashlib
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, List

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    precision_recall_curve, auc, confusion_matrix
)

# Generic spam keywords
GENERIC_PHRASES = [
    "best product ever", "must buy", "highly recommended 100%", 
    "waste of money", "scam company", "fake service", "five stars rating"
]


def extract_style_features(text: str, rating: float = 3.0) -> List[float]:
    """Extracts 6 numerical text style & entropy features."""
    if not text:
        return [0, 0, 0, 0, 0, 0]
    
    length = len(text)
    words = [w.lower() for w in text.split()]
    word_count = len(words)
    
    upper_ratio = sum(1 for c in text if c.isupper()) / max(1, length)
    excl_count = text.count("!")
    unique_words = set(words)
    ttr = len(unique_words) / max(1, word_count) if word_count > 0 else 0
    extremity = abs(rating - 3.0) / 2.0
    generic_matches = sum(1 for p in GENERIC_PHRASES if p in text.lower())

    return [float(word_count), float(upper_ratio), float(excl_count), float(ttr), float(extremity), float(generic_matches)]


def build_benchmark_dataset() -> pd.DataFrame:
    """Builds a curated, reproducible benchmark dataset of legitimate and deceptive reviews."""
    data = [
        # Legitimate Reviews (Label: 0)
        ("I have used Acme Cloud for 6 months. Uptime is generally good, documentation could improve.", 4.0, 0),
        ("Customer support resolved my billing issue in 24 hours. Reliable enterprise product.", 5.0, 0),
        ("The API response times are around 45ms. Pricing is competitive for small teams.", 4.0, 0),
        ("Decent software but onboarding took slightly longer than expected.", 3.0, 0),
        ("Solid product overall, though the UI dashboard feels a bit dated.", 4.0, 0),
        ("Initial setup was straight forward. Customer support team answered my email.", 4.0, 0),
        ("We integrated their webhook API into our pipeline without major hurdles.", 5.0, 0),
        ("Average experience. The platform works as advertised but lacks advanced analytics.", 3.0, 0),
        ("Refund process took 5 business days, which is standard for international banking.", 3.0, 0),
        ("Good security features and clean role-based access management.", 5.0, 0),
        ("The system experienced minor latency during peak hours yesterday.", 3.0, 0),
        ("Prompt responses from technical support when we ran into configuration issues.", 4.0, 0),
        
        # Deceptive / Fake Reviews (Label: 1)
        ("BEST PRODUCT EVER!!! MUST BUY HIGHLY RECOMMENDED 100% FIVE STARS RATING!!", 5.0, 1),
        ("AMAZING SERVICE 100% LEGIT BEST COMPANY EVER BUY NOW FIVE STARS!!!", 5.0, 1),
        ("TOTAL SCAM COMPANY WASTE OF MONEY FAKE SERVICE NEVER USE THEM AVOID!!!", 1.0, 1),
        ("GREAT PRODUCT BEST PRODUCT EVER MUST BUY 100% PERFECT HIGHLY RECOMMENDED!!", 5.0, 1),
        ("SCAM SCAM SCAM! Horrible fraud company fake service waste of money!!!", 1.0, 1),
        ("PERFECT EXPERIENCE BEST EVER MUST BUY 100% HIGHLY RECOMMENDED FIVE STARS!", 5.0, 1),
        ("Terrible scam company fake service 100% waste of money don't buy!!", 1.0, 1),
        ("BEST EVER EVER BEST PRODUCT MUST BUY 100% HIGHLY RECOMMENDED SUPER QUALITY!!", 5.0, 1),
        ("HORRIBLE FRAUD SCAM WASTE OF MONEY FAKE SERVICE DO NOT BUY EVER!", 1.0, 1),
        ("EXCELLENT BEST PRODUCT EVER MUST BUY 100% RECOMMENDED FIVE STARS RATING!!", 5.0, 1)
    ]
    df = pd.DataFrame(data, columns=["text", "rating", "label"])
    return df


def train_and_evaluate_model() -> Tuple[Pipeline, dict]:
    """Trains scikit-learn Pipeline with ColumnTransformer and returns evaluation metrics."""
    df = build_benchmark_dataset()

    # 1. Deduplication prior to splitting
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    # Extract style metrics DataFrame
    style_features_list = [extract_style_features(t, r) for t, r in zip(df["text"], df["rating"])]
    style_df = pd.DataFrame(style_features_list, columns=["word_count", "upper_ratio", "excl_count", "ttr", "extremity", "generic_matches"])
    
    X = pd.concat([df[["text"]], style_df], axis=1)
    y = df["label"]

    # 2. Stratified train/test split with fixed random seed
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    # 3. ColumnTransformer combining TF-IDF + Scaled Style Features
    preprocessor = ColumnTransformer(
        transformers=[
            ("tfidf", TfidfVectorizer(max_features=200, ngram_range=(1, 2)), "text"),
            ("style", StandardScaler(), ["word_count", "upper_ratio", "excl_count", "ttr", "extremity", "generic_matches"])
        ]
    )

    # 4. Pipeline with LogisticRegression classifier
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(random_state=42, C=1.0))
    ])

    # 5. Fit model
    pipeline.fit(X_train, y_train)

    # 6. Evaluation
    y_pred = pipeline.predict(X_test)
    y_probs = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_probs)
    pr_auc = auc(recall_curve, precision_curve)
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "pr_auc": round(float(pr_auc), 4),
        "confusion_matrix": cm,
        "test_sample_count": len(y_test)
    }

    return pipeline, metrics


def export_artifact_and_model_card(model: Pipeline, metrics: dict):
    """Exports model joblib artifact, SHA-256 checksum file, and MODEL_CARD.md."""
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
    os.makedirs(models_dir, exist_ok=True)

    model_path = os.path.join(models_dir, "fake_review_model.joblib")
    checksum_path = os.path.join(models_dir, "fake_review_model.joblib.sha256")
    card_path = os.path.join(models_dir, "MODEL_CARD.md")

    # Export joblib artifact
    joblib.dump(model, model_path)

    # Compute SHA-256 checksum
    hasher = hashlib.sha256()
    with open(model_path, "rb") as f:
        hasher.update(f.read())
    sha256_hash = hasher.hexdigest()

    with open(checksum_path, "w") as f:
        f.write(sha256_hash + "\n")

    # Write MODEL_CARD.md
    model_card_content = f"""# Model Card: RitaDrishti Prototype Fake Review Classifier

## Model Overview
- **Model Architecture**: Scikit-Learn Pipeline (`ColumnTransformer` combining TF-IDF N-gram vectorizer + `StandardScaler` for 6 text style features -> `LogisticRegression`).
- **Artifact File**: `fake_review_model.joblib`
- **SHA-256 Checksum**: `{sha256_hash}`
- **Release Version**: 1.0.0

## Dataset & Training Scope
- **Training Set Note**: Trained on a curated benchmark seed dataset of 22 representative reviews (12 legitimate, 10 deceptive) designed for pipeline verification and deterministic end-to-end testing.
- **Evaluation Split**: {metrics['test_sample_count']} samples evaluated on test split (`random_state=42`, stratified).
- **Accuracy**: {metrics['accuracy']} | **F1 Score**: {metrics['f1_score']}
- **Production Recommendation**: For production enterprise deployment, replace `train_fake_review_model.py` dataset input with full public fake-review callsets (e.g. Amazon Deceptive Reviews / Yelp Spam Dataset).

## Intended Use
Calculates probability $[0.0, 1.0]$ of deceptive or fraudulent online customer review text based on lexical diversity entropy, character case ratios, exclamation frequency, and generic spam phrase matching.
"""

    with open(card_path, "w") as f:
        f.write(model_card_content)

    print(f"[Model Training Complete]: Artifact saved to {model_path}")
    print(f"[SHA-256 Checksum]: {sha256_hash}")
    print(f"[Metrics]: F1={metrics['f1_score']}, Accuracy={metrics['accuracy']}")


if __name__ == "__main__":
    trained_model, eval_metrics = train_and_evaluate_model()
    export_artifact_and_model_card(trained_model, eval_metrics)
