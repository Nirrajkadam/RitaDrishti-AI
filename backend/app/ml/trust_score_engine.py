"""
SentinelX Trust AI — Trust Score Engine
Mathematical Weighting Algorithm for Corporate Trust Index Calculation.

Formula:
Trust Index = (w1 * NormalizedSentiment) + (w2 * TransparencyScore) + (w3 * (1 - AvgFakeProb) * 100) 
              - (w4 * ComplaintPenalty) - (w5 * RiskPenalty)
Where weights sum to 1.0.
"""

from typing import Dict, Any, List


class TrustScoreEngine:
    def __init__(self):
        # Weight Configurations
        self.w_sentiment = 0.35
        self.w_transparency = 0.25
        self.w_authenticity = 0.20
        self.w_complaint_penalty = 0.10
        self.w_risk_penalty = 0.10

    def calculate_trust_score(
        self,
        avg_sentiment_score: float, # [-1.0 to 1.0]
        avg_fake_prob: float,       # [0.0 to 1.0]
        total_reviews: int,
        unresolved_complaints: int,
        verified_status: bool = False,
        overall_risk_score: float = 20.0 # [0 to 100]
    ) -> Dict[str, Any]:
        """Calculates multi-factor Trust Index score [0.00 to 100.00]."""
        
        # 1. Normalized Sentiment Component (Convert [-1, 1] to [0, 100])
        norm_sentiment = ((avg_sentiment_score + 1.0) / 2.0) * 100.0

        # 2. Transparency Score
        transparency = 90.0 if verified_status else 50.0
        if total_reviews >= 50:
            transparency += 10.0
        transparency = min(100.0, transparency)

        # 3. Authenticity Factor (1 - Fake Probability)
        authenticity = (1.0 - avg_fake_prob) * 100.0

        # 4. Complaint Penalty
        complaint_penalty = min(50.0, unresolved_complaints * 5.0)

        # 5. Risk Penalty
        risk_penalty = overall_risk_score * 0.5

        # Raw Trust Index Calculation
        raw_trust = (
            (self.w_sentiment * norm_sentiment) +
            (self.w_transparency * transparency) +
            (self.w_authenticity * authenticity) -
            (self.w_complaint_penalty * complaint_penalty) -
            (self.w_risk_penalty * risk_penalty)
        )

        trust_index = max(0.0, min(100.0, round(float(raw_trust), 2)))

        # Assign Trust Tier
        if trust_index >= 80.0:
            tier = "High Trust"
        elif trust_index >= 60.0:
            tier = "Moderate Trust"
        elif trust_index >= 40.0:
            tier = "Low Trust"
        else:
            tier = "Critical Alert"

        return {
            "trust_index": trust_index,
            "trust_tier": tier,
            "components": {
                "sentiment_factor": round(float(norm_sentiment), 2),
                "transparency_score": round(float(transparency), 2),
                "authenticity_score": round(float(authenticity), 2),
                "complaint_penalty": round(float(complaint_penalty), 2),
                "risk_penalty": round(float(risk_penalty), 2)
            }
        }


if __name__ == "__main__":
    engine = TrustScoreEngine()
    print(engine.calculate_trust_score(
        avg_sentiment_score=0.75,
        avg_fake_prob=0.05,
        total_reviews=120,
        unresolved_complaints=1,
        verified_status=True,
        overall_risk_score=10.0
    ))
