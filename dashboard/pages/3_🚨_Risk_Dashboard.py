import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Risk Dashboard — SentinelX", page_icon="🚨", layout="wide")

st.title("🚨 Enterprise Risk & Anomaly Matrix")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚠️ Fraud & Compliance Risk Breakdown")
    risk_df = pd.DataFrame({
        "Risk Category": ["Fraud Risk", "Regulatory Risk", "Reputational Risk", "Operational Risk"],
        "Risk Score": [35, 20, 48, 15]
    })
    fig = px.bar(risk_df, x="Risk Category", y="Risk Score", color="Risk Category")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🚩 Anomaly Signals Detected")
    st.warning("⚠️ **Apex Logistics**: Sudden +45% spike in 1-star delivery complaints.")
    st.error("🚨 **FinPay Tech**: 3 unresolved billing dispute escalation notices flagged.")
    st.info("ℹ️ **Acme Cloud**: Zero high-severity anomalies detected in last 30 days.")
