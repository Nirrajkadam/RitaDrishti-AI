import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Trust Dashboard — SentinelX", page_icon="🛡️", layout="wide")

st.title("🛡️ Trust Index Benchmarks & Transparency Badges")

st.subheader("🎯 Multi-Factor Trust Component Benchmark")

categories = ['Sentiment Score', 'Transparency', 'Authenticity', 'Resolution Rate', 'Security Compliance']

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=[85, 92, 95, 88, 90], theta=categories, fill='toself', name='Acme Cloud'))
fig.add_trace(go.Scatterpolar(r=[58, 70, 60, 50, 65], theta=categories, fill='toself', name='FinPay Tech'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🏅 Trust Badges Issued")
col1, col2, col3 = st.columns(3)
with col1:
    st.success("✅ **Acme Cloud**: HIGH TRUST BADGE (88.5/100)")
with col2:
    st.warning("⚡ **FinPay Tech**: MODERATE TRUST BADGE (64.2/100)")
with col3:
    st.error("⛔ **Apex Logistics**: CRITICAL RISK ALERT (38.1/100)")
