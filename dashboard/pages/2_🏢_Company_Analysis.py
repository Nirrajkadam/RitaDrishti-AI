import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.express as px
from backend.app.ml.sentiment_engine import SentimentEngine
from backend.app.ml.fake_review_engine import FakeReviewEngine

st.set_page_config(page_title="Company Analysis — RitaDrishti-AI", page_icon="🏢", layout="wide")

st.title("🏢 Company Sentiment & Signal Analysis")

company = st.selectbox("Select Target Company", ["Acme Cloud Solutions", "FinPay Tech", "Apex Logistics"])

st.subheader(f"Detailed Analysis for {company}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Net Sentiment Score", "+0.72", "Positive Trend")
with col2:
    st.metric("Fake Review Probability", "4.8%", "Low Fraud Risk")
with col3:
    st.metric("Total Reviews Analyzed", "450", "Scrapy & Playwright")

# Interactive Sentiment Tester
st.divider()
st.subheader("🧪 Live Sentiment & Fake Review Inspector")
user_text = st.text_area("Paste a review text to analyze in real-time:", 
                         "Outstanding cloud uptime and superb customer support! Highly recommended.")

if st.button("Run ML Inspection"):
    s_engine = SentimentEngine()
    f_engine = FakeReviewEngine()

    s_res = s_engine.analyze_sentiment(user_text)
    f_res = f_engine.predict_fake_probability(user_text)

    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.success(f"**Sentiment**: {s_res['label'].upper()} (Score: {s_res['score']})")
        st.caption(f"Method: {s_res['method']}")
    with res_col2:
        if f_res['is_suspicious']:
            st.error(f"**Fake Review Signal**: SUSPICIOUS (Prob: {f_res['fake_probability']})")
        else:
            st.info(f"**Fake Review Signal**: LEGITIMATE (Prob: {f_res['fake_probability']})")
        st.json(f_res['features'])
