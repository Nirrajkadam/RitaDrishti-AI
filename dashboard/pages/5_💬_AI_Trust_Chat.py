import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from backend.app.rag.rag_engine import RAGEngine

st.set_page_config(page_title="AI Trust Chat — RitaDrishti-AI", page_icon="💬", layout="wide")

st.title("💬 RAG-Powered AI Trust Copilot")
st.markdown("Ask questions about any company's reviews, complaints, news, and risk posture. Powered by **SentenceTransformers + Qdrant/FAISS + Ollama (Llama 3)**.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am RitaDrishti AI Trust Copilot. How can I assist with your corporate risk and trust audit today?"}
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask a question (e.g., 'What are the main complaints against FinPay Tech?'):"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Retrieving vector embeddings & generating answer via Llama 3..."):
        rag = RAGEngine()
        res = rag.generate_rag_response(prompt)
        answer = res["answer"]

    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
