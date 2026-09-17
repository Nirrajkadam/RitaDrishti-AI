import streamlit as st
from app.agents.crew_manager import CrewManager

st.set_page_config(page_title="Executive Reports — SentinelX", page_icon="📄", layout="wide")

st.title("📄 Multi-Agent Executive Audit Reports")

company = st.selectbox("Select Company for Audit Report Generation", ["Acme Cloud Solutions", "FinPay Tech", "Apex Logistics"])

if st.button("🚀 Trigger CrewAI Multi-Agent Fleet Audit"):
    with st.spinner(f"Launching Research, Risk, Compliance, Trust & Report Agents for {company}..."):
        crew = CrewManager()
        audit_res = crew.run_full_audit(company)
        
    st.success("✅ Multi-Agent Audit Completed Successfully!")
    st.markdown(audit_res["report_markdown"])
    
    st.download_button(
        label="📥 Download Executive Audit Report (.md)",
        data=audit_res["report_markdown"],
        file_name=f"{company.lower().replace(' ', '_')}_trust_report.md",
        mime="text/markdown"
    )
