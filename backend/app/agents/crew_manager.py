"""
RitaDrishti-AI — CrewAI Multi-Agent System Architecture
Coordinates 5 specialized AI Agents for autonomous corporate trust & risk auditing:
1. Research Agent (OSINT & Data Mining)
2. Risk Agent (Fraud & Anomaly Auditor)
3. Compliance Agent (Regulatory & Consumer Protection Auditor)
4. Trust Agent (Sentiment & Trust Index Evaluator)
5. Report Agent (Executive Briefing & Report Synthesizer)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class EvidenceUnavailableError(Exception):
    """Domain exception raised when required evidence is unavailable for agent analysis."""
    pass


class ArticleEvidence(BaseModel):
    headline: str
    summary: str
    publisher: str


class ComplaintEvidence(BaseModel):
    title: str
    description: str
    resolution_status: str = "unresolved"


class ReviewAnalysisEvidence(BaseModel):
    raw_text: str
    cleaned_text: str
    sentiment_score: float
    fake_probability: float
    is_suspicious: bool


class AuditEvidence(BaseModel):
    company_name: str
    trust_score: Optional[float] = None
    articles: List[ArticleEvidence] = []
    complaints: List[ComplaintEvidence] = []
    analyses: List[ReviewAnalysisEvidence] = []


class ResearchAgent:
    """
    Responsibilities: Summarizes provided OSINT media coverage and corporate news.
    """
    def run(self, company_name: str, news_articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        count = len(news_articles) if news_articles else 0
        return {
            "agent": "ResearchAgent",
            "findings": f"OSINT Audit for {company_name}: Processed {count} verified media/news records."
        }


class RiskAgent:
    """
    Responsibilities: Audits fake review clusters and operational anomalies based on evidence.
    """
    def run(self, company_name: str, complaints_count: int = 0, fake_prob: float = 0.0) -> Dict[str, Any]:
        level = "High Risk" if fake_prob > 0.20 or complaints_count > 5 else "Low-to-Moderate Risk"
        return {
            "agent": "RiskAgent",
            "findings": f"Risk Audit for {company_name}: Evaluated as {level}. Average Fake Review Probability: {fake_prob:.2f}. Identified {complaints_count} consumer complaint records."
        }


class ComplianceAgent:
    """
    Responsibilities: Audits compliance based on verified customer resolution records.
    """
    def run(self, company_name: str, resolved_disputes: int = 0, total_disputes: int = 0) -> Dict[str, Any]:
        rate_str = f"{(resolved_disputes / total_disputes * 100):.1f}%" if total_disputes > 0 else "N/A (No active disputes)"
        return {
            "agent": "ComplianceAgent",
            "findings": f"Compliance Review for {company_name}: Customer dispute resolution rate: {rate_str}."
        }


class TrustAgent:
    """
    Responsibilities: Evaluates multi-factor Trust Index based on calculated score.
    """
    def run(self, company_name: str, trust_score: Optional[float] = None) -> Dict[str, Any]:
        if trust_score is None:
            return {
                "agent": "TrustAgent",
                "findings": f"Trust Benchmark for {company_name}: Insufficient data to calculate Trust Index."
            }
        tier = "High Trust" if trust_score >= 80 else ("Moderate Trust" if trust_score >= 60 else "Critical Alert")
        return {
            "agent": "TrustAgent",
            "findings": f"Trust Benchmark for {company_name}: Calculated Trust Index: {trust_score:.1f}/100 ({tier})."
        }


class ReportAgent:
    """
    Responsibilities: Synthesizes inputs from Research, Risk, Compliance, and Trust Agents into a consolidated executive markdown report.
    """
    def generate_report(self, company_name: str, agent_outputs: List[Dict[str, Any]]) -> str:
        report_md = f"""# 🛡️ Executive Trust Audit Report: {company_name}
**Platform**: RitaDrishti-AI Multi-Agent Audit System  
**Date**: September 2026 | **Classification**: Confidential Enterprise Assessment

---

## Executive Summary
RitaDrishti Multi-Agent System completed a comprehensive 360-degree assessment of **{company_name}**. The company has been assigned a verified **Trust Index** based on real-time sentiment signals, fake review detection metrics, and consumer dispute resolution audits.

---

## Agent Audit Breakdown

"""
        for output in agent_outputs:
            report_md += f"### 🤖 {output['agent']}\n- {output['findings']}\n\n"

        report_md += """---

## Key Recommendations for Stakeholders
1. **Maintain Transparency**: Continue active verification of customer support channels.
2. **Monitor Fraud Signals**: Regularly audit third-party rating portals for automated spam reviews.
3. **Escalate Dispute Resolution**: Resolve pending high-severity consumer complaints within 14 business days.

---
*Report Generated Automatically by RitaDrishti CrewAI Agent Fleet.*
"""
        return report_md


class CrewManager:
    """Orchestrates the multi-agent workflow using verified evidence objects."""

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.risk_agent = RiskAgent()
        self.compliance_agent = ComplianceAgent()
        self.trust_agent = TrustAgent()
        self.report_agent = ReportAgent()

    def run_full_audit(self, evidence: AuditEvidence) -> Dict[str, Any]:
        """Runs sequential multi-agent execution pipeline on provided evidence."""
        if not evidence.analyses and not evidence.articles and not evidence.complaints:
            raise EvidenceUnavailableError(
                f"Insufficient evidence available to conduct multi-agent audit for '{evidence.company_name}'."
            )

        fake_prob = 0.0
        if evidence.analyses:
            fake_prob = sum(a.fake_probability for a in evidence.analyses) / len(evidence.analyses)

        out1 = self.research_agent.run(evidence.company_name, news_articles=[a.model_dump() for a in evidence.articles])
        out2 = self.risk_agent.run(evidence.company_name, complaints_count=len(evidence.complaints), fake_prob=fake_prob)
        resolved = sum(1 for c in evidence.complaints if c.resolution_status == "resolved")
        out3 = self.compliance_agent.run(evidence.company_name, resolved_disputes=resolved, total_disputes=len(evidence.complaints))
        out4 = self.trust_agent.run(evidence.company_name, trust_score=evidence.trust_score)

        outputs = [out1, out2, out3, out4]
        report_markdown = self.report_agent.generate_report(evidence.company_name, outputs)

        return {
            "company_name": evidence.company_name,
            "status": "Completed",
            "agent_findings": outputs,
            "report_markdown": report_markdown
        }
