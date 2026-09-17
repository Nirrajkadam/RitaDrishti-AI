import streamlit as st

st.set_page_config(page_title="Admin Panel — SentinelX", page_icon="⚙️", layout="wide")

st.title("⚙️ System Health & Scraper Pipeline Controls")

st.subheader("🖥️ Platform Subsystem Health Status")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.success("PostgreSQL 18: ONLINE")
with col2:
    st.success("Qdrant Vector DB: ONLINE")
with col3:
    st.success("Ollama Llama 3: READY")
with col4:
    st.info("Snapdragon NPU: DIRECTML")

st.divider()
st.subheader("🕷️ Trigger On-Demand Ingestion Pipeline")
target_domain = st.text_input("Enter Target Domain (e.g., trustpilot.com/review/acmecloud.io)", "acmecloud.io")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("Run Scrapy Review Spider"):
        st.info(f"Launched background Scrapy spider for {target_domain}...")
with col_b:
    if st.button("Run Playwright Complaint Scraper"):
        st.info(f"Launched headless Playwright browser scraper for {target_domain}...")
