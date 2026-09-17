"""
RitaDrishti-AI — Executive Dashboard & Global Control Console
"""

import sys
import os

# Ensure backend directory is in Python path for streamlit execution
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import streamlit as st
import pandas as pd
import plotly.express as px
from app.ml.nl_query_engine import NaturalLanguageQueryEngine
from app.ml.correlation_engine import CorrelationEngine

st.set_page_config(
    page_title="RitaDrishti-AI — Trust Intelligence Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# TOP HEADER & GLOBAL SEARCH BAR
# -----------------------------------------------------------------------------
st.title("🛡️ RitaDrishti-AI — Executive Trust & Risk Intelligence Dashboard")

col_search1, col_search2 = st.columns([3, 2])

with col_search1:
    search_keyword = st.text_input("🔍 Global Search Bar", placeholder="Search Company Name, Domain, or Industry (e.g. Acme, Fintech, Cloud)...")

with col_search2:
    nl_prompt = st.text_input("🧠 Natural Language Query", placeholder='e.g., "Show high-risk fintech companies" or "trust score > 80"')

# Dataset Mock
dataset = [
    {"Company": "Acme Cloud Solutions", "Domain": "acmecloud.io", "Industry": "Cloud SaaS", "Trust Score": 88.5, "Risk Level": "Low", "Fake Review %": "2.5%", "Status": "Verified"},
    {"Company": "FinPay Tech", "Domain": "finpay.com", "Industry": "Fintech", "Trust Score": 64.2, "Risk Level": "Medium", "Fake Review %": "12.0%", "Status": "Verified"},
    {"Company": "Apex Logistics", "Domain": "apexlogistics.net", "Industry": "Supply Chain", "Trust Score": 38.1, "Risk Level": "Severe", "Fake Review %": "28.0%", "Status": "Unverified"},
    {"Company": "Nova Health Solutions", "Domain": "novahealth.org", "Industry": "Healthcare", "Trust Score": 91.0, "Risk Level": "Low", "Fake Review %": "1.2%", "Status": "Verified"},
    {"Company": "CyberShield Software", "Domain": "cybershield.io", "Industry": "Cybersecurity", "Trust Score": 84.6, "Risk Level": "Low", "Fake Review %": "3.8%", "Status": "Verified"}
]
df = pd.DataFrame(dataset)

# Filter Dataset based on search
filtered_df = df.copy()
if search_keyword:
    filtered_df = filtered_df[
        filtered_df["Company"].str.contains(search_keyword, case=False) |
        filtered_df["Domain"].str.contains(search_keyword, case=False) |
        filtered_df["Industry"].str.contains(search_keyword, case=False)
    ]

if nl_prompt:
    nl_engine = NaturalLanguageQueryEngine()
    parsed_res = nl_engine.execute_nl_search(nl_prompt, [
        {"name": row["Company"], "industry": row["Industry"], "trust_score": row["Trust Score"], "risk_level": row["Risk Level"], "verified_status": (row["Status"]=="Verified")}
        for _, row in df.iterrows()
    ])
    matching_names = [r["name"] for r in parsed_res]
    filtered_df = filtered_df[filtered_df["Company"].isin(matching_names)]
    st.info(f"💡 **Natural Language Filter Applied**: Found {len(filtered_df)} matching entities.")

# -----------------------------------------------------------------------------
# REAL-TIME ACTIVE ALERTS BANNER
# -----------------------------------------------------------------------------
st.subheader("🚨 Real-Time Active Risk & Fraud Alerts")

alert_col1, alert_col2, alert_col3 = st.columns(3)

with alert_col1:
    st.error("""
    🔴 **FRAUD ALERT**: Apex Logistics  
    **Signal**: High Fake Review Cluster Detected (>28.0% probability)  
    *Action Required: Escalate to Fraud Prevention*
    """)

with alert_col2:
    st.warning("""
    🟡 **TRUST SCORE DROP**: FinPay Tech  
    **Signal**: Trust Index decreased by -12.4 pts (Unresolved disputes backlog)  
    *Action Required: Audit Customer Resolution Desk*
    """)

with alert_col3:
    st.info("""
    🔵 **CORRELATION ANOMALY**: Apex Logistics  
    **Signal**: News headline matches 8 unresolved BBB complaints  
    *Action Required: Compliance Audit Review*
    """)

st.divider()

# -----------------------------------------------------------------------------
# EXECUTIVE DASHBOARD KPI CARDS
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Avg Platform Trust Score", "73.28 / 100", "+1.8 pts")
with kpi2:
    st.metric("Avg Enterprise Risk Score", "34.10 / 100", "-4.2 pts")
with kpi3:
    st.metric("Active Fraud Alerts", "3 Alerts", "1 Critical")
with kpi4:
    st.metric("Net Positive Sentiment", "+68.4%", "Stable Trend")

st.divider()

# -----------------------------------------------------------------------------
# SENTIMENT TREND & CORRELATION ENGINE SECTION
# -----------------------------------------------------------------------------
chart_col, corr_col = st.columns([3, 2])

with chart_col:
    st.subheader("📈 Real-Time Sentiment Trend Timeline (6-Month Historical)")
    trend_data = pd.DataFrame({
        "Month": ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
        "Acme Cloud (Positive)": [78, 82, 85, 86, 88, 91],
        "FinPay Tech (Moderate)": [70, 68, 65, 62, 60, 64],
        "Apex Logistics (Risk Spike)": [60, 55, 48, 40, 35, 38]
    })
    fig_trend = px.line(trend_data, x="Month", y=["Acme Cloud (Positive)", "FinPay Tech (Moderate)", "Apex Logistics (Risk Spike)"],
                        markers=True, title="Sentiment Score Trajectory Across Monitored Brands")
    st.plotly_chart(fig_trend, width="stretch")

with corr_col:
    st.subheader("🔗 Cross-Entity Correlation Engine")
    st.markdown("**Complaint ↔ OSINT News ↔ Public Review Triangulation**")

    # Run Correlation Engine
    corr_engine = CorrelationEngine()
    corr_res = corr_engine.correlate_signals(
        reviews=[{"raw_text": "Outage lost my data", "rating": 1.0}],
        complaints=[{"title": "Unresolved server outage", "severity_level": "high"}],
        news=[{"headline": "Cloud Outage Impacts Regional Providers"}]
    )

    for cluster in corr_res["clusters"]:
        st.write(f"• **Cluster**: {cluster['cluster_name']}")
        st.caption(f"Details: {cluster['summary']}")
        st.caption(f"Confidence: {cluster.get('risk_correlation_confidence', 0.90)*100:.1f}%")

st.divider()

# -----------------------------------------------------------------------------
# EXECUTIVE TRUST LEADERBOARD TABLE
# -----------------------------------------------------------------------------
st.subheader("🏆 Enterprise Trust & Risk Leaderboard")
st.dataframe(filtered_df, width="stretch")
