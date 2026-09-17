"""
SentinelX Trust AI — Streamlit Dashboard Entrypoint
"""

import streamlit as st

st.set_page_config(
    page_title="SentinelX Trust AI Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ SentinelX Trust AI — Trust Intelligence Platform")
st.markdown("""
Welcome to **SentinelX Trust AI**, an enterprise-grade AI/ML platform for **Trust Intelligence, Fraud Detection, Multi-Agent Auditing, and RAG Copilot Intelligence**.

### 📌 Navigation Quick Guide:
* **🏠 Home**: Platform overview & top company trust leaderboard.
* **🏢 Company Analysis**: Real-time sentiment, word clouds, fake review signals.
* **🚨 Risk Dashboard**: Anomaly detection, fraud risk matrix & complaint severity.
* **🛡️ Trust Dashboard**: Trust Index benchmarks, transparency badges & peer comparisons.
* **💬 AI Trust Chat**: RAG-powered vector search chatbot for instant QA.
* **📄 Executive Reports**: Multi-Agent CrewAI audit report generator.
* **⚙️ Admin Panel**: System health metrics, scraper triggers, and database controls.
""")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Companies Audited", "1,240", delta="+12 this week")
with col2:
    st.metric("Avg Platform Trust Score", "74.8 / 100", delta="+2.1 pts")
with col3:
    st.metric("Fake Reviews Filtered", "14,890", delta="98.4% Accuracy")
with col4:
    st.metric("Multi-Agent Audits Run", "850+", delta="Ollama Llama 3")

st.divider()
st.info("👈 Select a page from the sidebar to start exploring SentinelX Trust AI.")
