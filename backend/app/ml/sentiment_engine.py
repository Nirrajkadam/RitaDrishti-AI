"""
RitaDrishti-AI — Sentiment Analysis Engine
Theory: Combines Lexicon-Based VADER sentiment with Transformer-based (DistilBERT) deep contextual embeddings.
Feature Engineering: Text normalization, emoji decoding, negation handling, intensity boosting.
Model Selection: VADER (fast low-latency fallback) + DistilBERT (fine-grained contextual sentiment).
Evaluation Metrics: Precision, Recall, F1-Score, ROC-AUC.
"""

from typing import Dict, Any, Union
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentEngine:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.transformer_enabled = False
        try:
            from transformers import pipeline
            self.classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", top_k=None)
            self.transformer_enabled = True
        except Exception:
            self.transformer_enabled = False

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyzes sentiment of input review text.
        Returns label ('positive', 'negative', 'neutral') and normalized score [-1.0, 1.0].
        """
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0, "confidence": 0.5, "method": "fallback"}

        # 1. Calculate VADER score
        vader_scores = self.vader.polarity_scores(text)
        compound = vader_scores['compound']

        # 2. Calculate Transformer score if available
        if self.transformer_enabled:
            try:
                outputs = self.classifier(text[:512])[0]
                pos_score = next((item['score'] for item in outputs if item['label'].upper() == 'POSITIVE'), 0.5)
                neg_score = next((item['score'] for item in outputs if item['label'].upper() == 'NEGATIVE'), 0.5)
                
                # Hybrid Score (-1.0 to 1.0)
                hybrid_score = (pos_score - neg_score) * 0.7 + compound * 0.3
                hybrid_score = max(-1.0, min(1.0, hybrid_score))

                label = "positive" if hybrid_score > 0.15 else ("negative" if hybrid_score < -0.15 else "neutral")
                return {
                    "label": label,
                    "score": round(float(hybrid_score), 4),
                    "confidence": round(float(max(pos_score, neg_score)), 4),
                    "method": "Hybrid DistilBERT + VADER",
                    "vader_compound": round(compound, 4)
                }
            except Exception as e:
                pass

        # VADER Fallback
        label = "positive" if compound >= 0.05 else ("negative" if compound <= -0.05 else "neutral")
        return {
            "label": label,
            "score": round(float(compound), 4),
            "confidence": round(abs(float(compound)), 4),
            "method": "VADER Lexicon",
            "vader_compound": round(compound, 4)
        }


if __name__ == "__main__":
    engine = SentimentEngine()
    print(engine.analyze_sentiment("The platform is fast, secure, and highly reliable!"))
    print(engine.analyze_sentiment("Terrible experience. Payments failed and zero support."))
