"""
RitaDrishti-AI — Palantir AIP / Foundry Style Enterprise Control Console
Inspired by Palantir's high-tech, minimalist, enterprise AI design language.
"""

import sys
import os

# Insert root project directory into sys.path to avoid name collision with dashboard/app.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.express as px
from backend.app.ml.nl_query_engine import NaturalLanguageQueryEngine
from backend.app.ml.correlation_engine import CorrelationEngine

# Page Config
st.set_page_config(
    page_title="RitaDrishti AIP // Trust Intelligence Operating System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# PALANTIR DESIGN SYSTEM (CUSTOM CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #080C14 !important;
        color: #E2E8F0 !important;
    }

    /* Main Container */
    .stApp {
        background-color: #080C14 !important;
    }

    /* Top Ticker Status Bar */
    .palantir-ticker {
        background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 10px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #94A3B8;
        letter-spacing: 0.05em;
        margin-bottom: 24px;
    }

    .status-badge {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Hero Header */
    .palantir-hero {
        margin-bottom: 30px;
    }

    .palantir-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin-bottom: 6px;
    }

    .palantir-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        font-weight: 400;
    }

    /* Palantir Glassmorphic Cards */
    .palantir-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }

    .palantir-card:hover {
        border-color: rgba(0, 242, 254, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .palantir-card-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748B;
        margin-bottom: 8px;
    }

    .palantir-metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }

    /* Palantir Alert Cards */
    .alert-critical {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #EF4444;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .alert-warning {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-left: 4px solid #F59E0B;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .alert-info {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid #3B82F6;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .alert-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .alert-desc {
        font-size: 0.88rem;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP STATUS TICKER (PALANTIR FOUNDRY STYLE)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="palantir-ticker">
    <div>RITADRISHTI AIP // ENTERPRISE OPERATING SYSTEM</div>
    <div>NPU ACCELERATION: <span style="color:#38BDF8;">QUALCOMM DIRECTML</span></div>
    <div>VECTOR DB: <span style="color:#38BDF8;">QDRANT HNSW</span></div>
    <div>SYSTEM STATUS: <span class="status-badge">OPERATIONAL</span></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HERO HEADER & COMMAND CONSOLE SEARCH
# -----------------------------------------------------------------------------
st.markdown("""
<div class="palantir-hero">
    <div class="palantir-title">Trust & Risk Intelligence Operating System</div>
    <div class="palantir-subtitle">Real-Time Autonomous Risk Auditing, NLP Fraud Signal Correlation & Multi-Agent Intelligence</div>
</div>
""", unsafe_allow_html=True)

col_cmd1, col_cmd2 = st.columns([3, 2])

with col_cmd1:
    search_keyword = st.text_input("🔍 PALANTIR GLOBAL COMMAND SEARCH", placeholder="Enter Entity Name, Domain, or Vertical (e.g. Acme, Fintech, Cloud)...")

with col_cmd2:
    nl_prompt = st.text_input("🧠 AIP NATURAL LANGUAGE PROMPT", placeholder='e.g., "Show high-risk fintech companies" or "trust score > 80"')

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
    st.info(f"💡 **AIP Query Filter Executed**: Identified {len(filtered_df)} entities matching natural language constraints.")

# -----------------------------------------------------------------------------
# REAL-TIME THREAT & RISK ALERTS (PALANTIR DEFENSE STYLE)
# -----------------------------------------------------------------------------
st.markdown("### 🚨 ACTIVE INTELLIGENCE ALERTS & FRAUD SIGNALS")

alert_col1, alert_col2, alert_col3 = st.columns(3)

with alert_col1:
    st.markdown("""
    <div class="alert-critical">
        <div class="alert-title" style="color: #EF4444;">CRITICAL FRAUD ALERT // APEX LOGISTICS</div>
        <div class="alert-desc">Automated spam review cluster detected. Synthetic review probability spiked to <strong>28.0%</strong> across third-party portals.</div>
    </div>
    """, unsafe_allow_html=True)

with alert_col2:
    st.markdown("""
    <div class="alert-warning">
        <div class="alert-title" style="color: #F59E0B;">TRUST INDEX DEGRADATION // FINPAY TECH</div>
        <div class="alert-desc">Trust Index decreased by <strong>-12.4 pts</strong> due to unresolved payment dispute backlog exceeding threshold limits.</div>
    </div>
    """, unsafe_allow_html=True)

with alert_col3:
    st.markdown("""
    <div class="alert-info">
        <div class="alert-title" style="color: #3B82F6;">TRIANGULATION SIGNAL // APEX LOGISTICS</div>
        <div class="alert-desc">OSINT news coverage correlates with 8 unresolved BBB consumer complaint records (Confidence: 88%).</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# EXECUTIVE METRIC TILES
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown("""
    <div class="palantir-card">
        <div class="palantir-card-header">AVG TRUST INDEX</div>
        <div class="palantir-metric-val" style="color: #34D399;">73.28</div>
        <div style="font-size: 0.8rem; color: #10B981; margin-top: 4px;">▲ +1.8 pts platform baseline</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown("""
    <div class="palantir-card">
        <div class="palantir-card-header">ENTERPRISE RISK METRIC</div>
        <div class="palantir-metric-val" style="color: #F8FAFC;">34.10</div>
        <div style="font-size: 0.8rem; color: #34D399; margin-top: 4px;">▼ -4.2 pts risk mitigation</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown("""
    <div class="palantir-card">
        <div class="palantir-card-header">ACTIVE ANOMALY CLUSTERS</div>
        <div class="palantir-metric-val" style="color: #F59E0B;">03</div>
        <div style="font-size: 0.8rem; color: #EF4444; margin-top: 4px;">1 Critical Fraud Signal</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown("""
    <div class="palantir-card">
        <div class="palantir-card-header">CREWAI AGENT AUDITS</div>
        <div class="palantir-metric-val" style="color: #38BDF8;">850+</div>
        <div style="font-size: 0.8rem; color: #38BDF8; margin-top: 4px;">Autonomous Reports Compiled</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# REAL-TIME TRAJECTORY & CORRELATION TRIANGULATION
# -----------------------------------------------------------------------------
st.write("")
chart_col, corr_col = st.columns([3, 2])

with chart_col:
    st.markdown("### 📈 SENTIMENT TRAJECTORY ANALYSIS")
    trend_data = pd.DataFrame({
        "Month": ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
        "Acme Cloud (High Trust)": [78, 82, 85, 86, 88, 91],
        "FinPay Tech (Moderate)": [70, 68, 65, 62, 60, 64],
        "Apex Logistics (Risk Alert)": [60, 55, 48, 40, 35, 38]
    })
    fig_trend = px.line(trend_data, x="Month", y=["Acme Cloud (High Trust)", "FinPay Tech (Moderate)", "Apex Logistics (Risk Alert)"],
                        markers=True)
    fig_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        font=dict(color='#94A3B8', family='Inter'),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_trend, width="stretch")

with corr_col:
    st.markdown("### 🔗 TRIANGULATION ENGINE")
    st.caption("Complaint ↔ OSINT News ↔ Public Review Signal Correlation")

    # Run Correlation Engine
    corr_engine = CorrelationEngine()
    corr_res = corr_engine.correlate_signals(
        reviews=[{"raw_text": "Outage lost my data", "rating": 1.0}],
        complaints=[{"title": "Unresolved server outage", "severity_level": "high"}],
        news=[{"headline": "Cloud Outage Impacts Regional Providers"}]
    )

    for cluster in corr_res["clusters"]:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); padding: 14px; border-radius: 6px; margin-bottom: 10px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #38BDF8; font-weight: 700;">{cluster['cluster_name'].upper()}</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 4px;">{cluster['summary']}</div>
            <div style="font-size: 0.75rem; color: #64748B; margin-top: 6px;">CORRELATION CONFIDENCE: <strong style="color:#34D399;">{cluster.get('risk_correlation_confidence', 0.90)*100:.1f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ENTERPRISE ENTITY LEADERBOARD
# -----------------------------------------------------------------------------
st.markdown("### 🏆 MONITORED ENTERPRISE ENTITIES")
st.dataframe(filtered_df, width="stretch")
