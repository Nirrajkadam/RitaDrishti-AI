"""
RitaDrishti-AI — Real-Time Alerts API Endpoints
Provides real-time alert notifications for Trust Score drops, Fraud signals, and Correlation Anomaly clusters.
"""

from fastapi import APIRouter
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

MOCK_ALERTS = [
    {
        "alert_id": "ALT-1001",
        "type": "Fraud Alert",
        "company_name": "Apex Logistics",
        "severity": "CRITICAL",
        "title": "High Fake Review Cluster Detected",
        "message": "Automated spam cluster detected. Fake review probability spiked to 28.0%.",
        "timestamp": "2026-09-17T21:45:00Z",
        "action_required": "Escalate to Fraud Prevention Team"
    },
    {
        "alert_id": "ALT-1002",
        "type": "Trust Score Drop",
        "company_name": "FinPay Tech",
        "severity": "WARNING",
        "title": "Trust Index Dropped -12.4 Points",
        "message": "Unresolved customer dispute backlog increased by 15%. Trust Index decreased from 76.6 to 64.2.",
        "timestamp": "2026-09-17T20:30:00Z",
        "action_required": "Audit Customer Resolution Desk"
    },
    {
        "alert_id": "ALT-1003",
        "type": "Correlation Anomaly",
        "company_name": "Apex Logistics",
        "severity": "HIGH",
        "title": "Complaints <-> News Correlation Triggered",
        "message": "Negative news coverage regarding shipment delays correlates directly with 8 unresolved BBB complaints.",
        "timestamp": "2026-09-17T19:15:00Z",
        "action_required": "Review Regulatory Compliance Audit"
    }
]

@router.get("/", response_model=List[Dict[str, Any]])
async def get_active_alerts():
    """Retrieve all real-time active system alerts."""
    return MOCK_ALERTS

@router.get("/summary")
async def get_alerts_summary():
    """Get count summary of active alerts by severity."""
    critical = sum(1 for a in MOCK_ALERTS if a["severity"] == "CRITICAL")
    high = sum(1 for a in MOCK_ALERTS if a["severity"] == "HIGH")
    warning = sum(1 for a in MOCK_ALERTS if a["severity"] == "WARNING")
    return {
        "total_active_alerts": len(MOCK_ALERTS),
        "critical_count": critical,
        "high_count": high,
        "warning_count": warning
    }
