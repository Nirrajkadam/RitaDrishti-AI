"""
RitaDrishti-AI — Natural Language Query Engine
Parses human natural language queries (e.g., "Show high-risk fintech companies") into structured search parameters.
"""

import re
from typing import Dict, Any, List


class NaturalLanguageQueryEngine:
    def __init__(self):
        self.industries = ["fintech", "cloud", "saas", "supply chain", "logistics", "healthcare", "cybersecurity"]
        self.risk_levels = ["low", "medium", "high", "severe"]
        self.trust_tiers = ["high trust", "moderate trust", "low trust", "critical alert"]

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parses natural language query text into structured database filter parameters."""
        q_lower = query.lower()

        extracted_industry = None
        for ind in self.industries:
            if ind in q_lower:
                extracted_industry = ind
                break

        extracted_risk = None
        for r in self.risk_levels:
            if r in q_lower:
                extracted_risk = r.capitalize()
                break

        extracted_tier = None
        for t in self.trust_tiers:
            if t in q_lower:
                extracted_tier = t.title()
                break

        verified_only = "verified" in q_lower

        # Trust score numeric extraction (e.g., "trust score > 80")
        min_trust = None
        match_gt = re.search(r'trust\s*(?:score)?\s*(?:>|greater than|above)\s*(\d+)', q_lower)
        if match_gt:
            min_trust = float(match_gt.group(1))

        match_lt = re.search(r'trust\s*(?:score)?\s*(?:<|less than|below)\s*(\d+)', q_lower)
        max_trust = float(match_lt.group(1)) if match_lt else None

        return {
            "original_query": query,
            "filters": {
                "industry": extracted_industry,
                "risk_level": extracted_risk,
                "trust_tier": extracted_tier,
                "verified_only": verified_only,
                "min_trust_score": min_trust,
                "max_trust_score": max_trust
            }
        }

    def execute_nl_search(self, query: str, companies_dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters input companies dataset based on parsed natural language query."""
        parsed = self.parse_query(query)
        f = parsed["filters"]

        results = []
        for comp in companies_dataset:
            # Match Industry
            if f["industry"] and f["industry"].lower() not in comp.get("industry", "").lower():
                continue
            # Match Risk Level
            if f["risk_level"] and comp.get("risk_level", "").lower() != f["risk_level"].lower():
                continue
            # Match Verified Status
            if f["verified_only"] and not comp.get("verified_status", False):
                continue
            # Match Trust Score Bounds
            score = comp.get("trust_score", 0.0)
            if f["min_trust_score"] and score < f["min_trust_score"]:
                continue
            if f["max_trust_score"] and score > f["max_trust_score"]:
                continue

            results.append(comp)

        return results


if __name__ == "__main__":
    engine = NaturalLanguageQueryEngine()
    print(engine.parse_query("Show high-risk fintech companies with trust score > 60"))
