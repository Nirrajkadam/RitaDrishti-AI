"""
RitaDrishti-AI — Risk Prediction Engine
Calculates multi-dimensional Risk Metrics: Fraud Risk, Regulatory Risk, Reputational Risk, and Overall Risk Score.
Employs anomaly detection principles to flag sudden spikes in negative complaints or fake reviews.
"""

from typing import Dict, Any, List


class RiskPredictionEngine:
    def __init__(self):
        pass

    def evaluate_risk(
        self,
        fake_review_ratio: float,      # [0.0 to 1.0]
        unresolved_complaints: int,
        critical_complaints: int,
        negative_sentiment_ratio: float,# [0.0 to 1.0]
        negative_news_count: int
    ) -> Dict[str, Any]:
        """Evaluates corporate risk metrics and returns anomaly signals."""
        
        # 1. Fraud Risk (Driven by fake review density & unresolved billing complaints)
        fraud_risk = (fake_review_ratio * 60.0) + min(40.0, unresolved_complaints * 4.0)

        # 2. Regulatory Risk (Driven by critical regulatory/legal complaints)
        regulatory_risk = min(100.0, critical_complaints * 25.0 + negative_news_count * 10.0)

        # 3. Reputational Risk (Driven by negative sentiment & news coverage)
        reputational_risk = (negative_sentiment_ratio * 70.0) + min(30.0, negative_news_count * 15.0)

        # Overall Risk Score (Weighted average)
        overall_risk = (0.40 * fraud_risk) + (0.35 * reputational_risk) + (0.25 * regulatory_risk)
        overall_risk = max(0.0, min(100.0, round(float(overall_risk), 2)))

        # Assign Risk Level
        if overall_risk >= 75.0:
            level = "Severe"
        elif overall_risk >= 50.0:
            level = "High"
        elif overall_risk >= 25.0:
            level = "Medium"
        else:
            level = "Low"

        # Signal Anomaly Detection
        signals = []
        if fake_review_ratio > 0.20:
            signals.append("High Fake Review Cluster Detected (>20%)")
        if critical_complaints > 0:
            signals.append(f"{critical_complaints} Critical Legal/Regulatory Complaints Flagged")
        if negative_sentiment_ratio > 0.50:
            signals.append("Dominant Negative Sentiment Trend (>50%)")
        if unresolved_complaints > 5:
            signals.append("Backlog of Unresolved Consumer Complaints")

        return {
            "overall_risk_score": overall_risk,
            "risk_level": level,
            "sub_scores": {
                "fraud_risk": round(float(min(100.0, fraud_risk)), 2),
                "regulatory_risk": round(float(min(100.0, regulatory_risk)), 2),
                "reputational_risk": round(float(min(100.0, reputational_risk)), 2)
            },
            "anomaly_signals": signals if signals else ["No severe anomalies detected"]
        }


if __name__ == "__main__":
    engine = RiskPredictionEngine()
    print(engine.evaluate_risk(
        fake_review_ratio=0.25,
        unresolved_complaints=8,
        critical_complaints=2,
        negative_sentiment_ratio=0.60,
        negative_news_count=3
    ))
