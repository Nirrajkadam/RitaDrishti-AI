"""
Unit tests for CrewAI Multi-Agent Fleet
"""

import pytest
from backend.app.agents.crew_manager import (
    ResearchAgent, RiskAgent, ComplianceAgent, TrustAgent, ReportAgent, CrewManager
)


def test_research_agent():
    agent = ResearchAgent()
    res = agent.run("Acme Cloud")
    assert res["agent"] == "ResearchAgent"
    assert "Acme Cloud" in res["findings"]


def test_risk_agent():
    agent = RiskAgent()
    res = agent.run("Acme Cloud", complaints_count=10, fake_prob=0.35)
    assert res["agent"] == "RiskAgent"
    assert "High Risk" in res["findings"]


def test_compliance_agent():
    agent = ComplianceAgent()
    res = agent.run("Acme Cloud")
    assert res["agent"] == "ComplianceAgent"


def test_trust_agent():
    agent = TrustAgent()
    res = agent.run("Acme Cloud", trust_score=85.0)
    assert res["agent"] == "TrustAgent"
    assert "High Trust" in res["findings"]


def test_crew_manager_full_audit():
    crew = CrewManager()
    res = crew.run_full_audit("Acme Cloud")
    assert res["company_name"] == "Acme Cloud"
    assert res["status"] == "Completed"
    assert len(res["agent_findings"]) == 4
    assert "# 🛡️ Executive Trust Audit Report: Acme Cloud" in res["report_markdown"]
