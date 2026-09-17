import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Home — RitaDrishti-AI", page_icon="🏠", layout="wide")

st.title("🏠 Platform Overview & Trust Leaderboard")

data = [
    {"Company": "Acme Cloud Solutions", "Industry": "Cloud SaaS", "Trust Score": 88.5, "Risk Level": "Low", "Fake Review %": "2.5%", "Status": "Verified"},
    {"Company": "FinPay Tech", "Industry": "Fintech", "Trust Score": 64.2, "Risk Level": "Medium", "Fake Review %": "12.0%", "Status": "Verified"},
    {"Company": "Apex Logistics", "Industry": "Supply Chain", "Trust Score": 38.1, "Risk Level": "Severe", "Fake Review %": "28.0%", "Status": "Unverified"},
    {"Company": "Nova Health Solutions", "Industry": "Healthcare", "Trust Score": 91.0, "Risk Level": "Low", "Fake Review %": "1.2%", "Status": "Verified"},
    {"Company": "CyberShield Software", "Industry": "Cybersecurity", "Trust Score": 84.6, "Risk Level": "Low", "Fake Review %": "3.8%", "Status": "Verified"}
]
df = pd.DataFrame(data)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🏆 Top Ranked Companies by Trust Index")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("📊 Trust Score Distribution")
    fig = px.bar(df, x="Company", y="Trust Score", color="Risk Level",
                 color_discrete_map={"Low": "green", "Medium": "orange", "Severe": "red"})
    st.plotly_chart(fig, use_container_width=True)
