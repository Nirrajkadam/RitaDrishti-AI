"""
RitaDrishti-AI — Cross-Entity Correlation Engine
Links signals between Consumer Complaints <-> OSINT News <-> Public Reviews.
Identifies root cause events (e.g., negative news headline matching billing complaints and negative review spikes).
"""

import re
from typing import List, Dict, Any


class CorrelationEngine:
    def __init__(self):
        pass

    def correlate_signals(
        self,
        reviews: List[Dict[str, Any]],
        complaints: List[Dict[str, Any]],
        news: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Correlates complaints, news, and reviews to identify linked risk clusters."""
        
        correlated_events = []
        
        # 1. Extract key topic keywords from news headlines
        news_keywords = set()
        for article in news:
            words = re.findall(r'\w{4,}', article.get("headline", "").lower())
            news_keywords.update(words)

        # 2. Match complaints against news keywords
        linked_complaints = []
        for complaint in complaints:
            comp_text = f"{complaint.get('title', '')} {complaint.get('description', '')}".lower()
            matching_terms = [kw for kw in news_keywords if kw in comp_text and kw not in ["company", "service", "about", "their"]]
            if matching_terms:
                linked_complaints.append({
                    "complaint_id": complaint.get("complaint_id", "N/A"),
                    "title": complaint.get("title", ""),
                    "matching_keywords": matching_terms,
                    "severity": complaint.get("severity_level", "medium")
                })

        # 3. Match negative reviews against linked complaints
        linked_reviews = []
        for review in reviews:
            rev_text = review.get("raw_text", "").lower()
            if review.get("rating", 5) <= 2.0:
                matching_terms = [kw for kw in news_keywords if kw in rev_text and kw not in ["company", "service"]]
                if matching_terms:
                    linked_reviews.append({
                        "review_id": review.get("review_id", "N/A"),
                        "matching_keywords": matching_terms,
                        "rating": review.get("rating")
                    })

        # Correlation Risk Cluster
        if linked_complaints or linked_reviews:
            correlated_events.append({
                "cluster_name": "Multi-Source Negative Signal Cluster",
                "linked_news_count": len(news),
                "linked_complaints_count": len(linked_complaints),
                "linked_negative_reviews_count": len(linked_reviews),
                "risk_correlation_confidence": 0.88 if len(linked_complaints) > 0 and len(linked_reviews) > 0 else 0.65,
                "summary": f"Correlated {len(linked_complaints)} consumer complaints and {len(linked_reviews)} negative reviews with OSINT news coverage."
            })

        return {
            "total_correlated_clusters": len(correlated_events),
            "clusters": correlated_events if correlated_events else [
                {
                    "cluster_name": "Normal Operations Baseline",
                    "summary": "No cross-entity correlation anomalies detected between complaints, news, and reviews."
                }
            ]
        }


if __name__ == "__main__":
    engine = CorrelationEngine()
    print(engine.correlate_signals(
        reviews=[{"raw_text": "Server outage lost all my data!", "rating": 1.0}],
        complaints=[{"title": "Data loss outage", "description": "Cloud server went down", "severity_level": "high"}],
        news=[{"headline": "Cloud Outage Impacts Major Software Vendors"}]
    ))
