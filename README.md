# 🛡️ SentinelX Trust AI — AI-Powered Trust & Risk Intelligence Platform

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL 18](https://img.shields.io/badge/PostgreSQL-18-336791.svg)](https://www.postgresql.org/)
[![Qdrant Vector DB](https://img.shields.io/badge/Qdrant-v1.8.0-red.svg)](https://qdrant.tech/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-orange.svg)](https://www.crewai.com/)
[![Qualcomm Snapdragon AI](https://img.shields.io/badge/Qualcomm-Snapdragon_NPU-purple.svg)](https://www.qualcomm.com/)

---

## 📌 Executive Summary
**SentinelX Trust AI** is an enterprise-grade Trust Intelligence and Risk Intelligence Platform. It ingests unstructured customer reviews, consumer complaints, and public news articles, applies NLP sentiment analysis and fake review detection, indexes vector embeddings for Retrieval-Augmented Generation (RAG), and orchestrates autonomous **CrewAI Multi-Agents** to generate real-time Trust Scores and executive risk audit reports.

---

## 🌟 Key Platform Features

* **🕷️ Multi-Source Ingestion Layer**: Scrapy spiders & Playwright headless browser scrapers for reviews, BBB complaints, and news feeds.
* **🧹 PII Redaction & ETL Pipeline**: Automatically redacts emails, phone numbers, and payment details; deduplicates raw content using MinHash hashing.
* **🧠 AI & ML Intelligence Engine**:
  * **Sentiment Analysis**: Hybrid VADER + DistilBERT Transformer pipeline.
  * **Fake Review Classifier**: XGBoost + LightGBM model trained on lexical diversity (TTR), uppercase ratios, and extreme sentiment features.
  * **Trust Index Engine**: Multi-factor weighted trust algorithm yielding $0-100$ scores and trust badges.
  * **Risk Prediction**: Anomaly detection flagging fraud risk, regulatory risk, and reputational risk.
* **⚡ Vector RAG System**: SentenceTransformers (`all-MiniLM-L6-v2`) + FAISS/Qdrant HNSW vector search + Ollama Llama 3 LLM.
* **🤖 Multi-Agent AI Auditor (CrewAI)**: 5 specialized agents (*Research, Risk, Compliance, Trust, Report Agents*) collaborating to compile executive markdown audit briefs.
* **📱 Qualcomm Snapdragon NPU Acceleration**: ONNX Runtime with DirectML/QNN Execution Providers for low-latency, zero-cost on-device inference on Snapdragon Copilot+ PCs.
* **📊 Multi-Page Streamlit Dashboard**: 7 visual pages (Overview, Sentiment Deep-Dive, Risk Matrix, Trust Benchmarks, AI Chat, Reports, Admin).
* **🐳 Single-Command Docker Deployment**: Containerized FastAPI, Streamlit, PostgreSQL, Qdrant, and Ollama via `docker-compose up`.

---

## 🏗️ System Architecture

```text
[ Data Sources ] -> [ Scrapy / Playwright ETL ] -> [ PostgreSQL 18 DB ]
                                                          │
          ┌───────────────────────────────────────────────┴───────────────────────────────┐
          ▼                                               ▼                               ▼
[ ML Analytics Core ]                           [ Qdrant Vector Store ]        [ CrewAI Multi-Agent Fleet ]
(DistilBERT + XGBoost)                          (SentenceTransformers)         (5 Autonomous AI Agents)
          │                                               │                               │
          ▼                                               ▼                               ▼
[ Qualcomm Snapdragon NPU ]                     [ Ollama Llama3 RAG ]          [ Executive Audit Brief ]
          │                                               │                               │
          └───────────────────────────────────────────────┼───────────────────────────────┘
                                                          ▼
                                            [ FastAPI REST Gateway ]
                                                          │
                                                          ▼
                                            [ Streamlit Web Dashboard ]
```

---

## 🚀 Quickstart Guide

### 1. Local Python Setup
```bash
# Navigate to directory
cd D:\sentinelx-trust-ai

# Activate Virtual Environment
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Launch FastAPI Backend Server
```bash
python backend/app/main.py
```
* API Documentation: `http://localhost:8000/docs`

### 3. Launch Streamlit Multi-Page Dashboard
```bash
streamlit run dashboard/app.py
```
* Dashboard URL: `http://localhost:8501`

### 4. Run via Docker Compose (Recommended)
```bash
docker-compose up --build -d
```

---

## 💻 Tech Stack Overview
* **Languages**: Python 3.11, SQL, HTML/CSS
* **Frameworks**: FastAPI, Streamlit, Scrapy, Playwright
* **AI/ML & NLP**: PyTorch, Transformers (DistilBERT), Scikit-learn, XGBoost, LightGBM, VADER
* **Generative AI & RAG**: CrewAI, Ollama (Llama 3), SentenceTransformers, FAISS, Qdrant
* **Hardware Acceleration**: Qualcomm ONNX Runtime, DirectML, QNN
* **Databases**: PostgreSQL 18 (AsyncSQLAlchemy + asyncpg), Qdrant Vector DB
* **DevOps**: Docker, Docker Compose, Git

---

## 📜 License & Author
Developed by **Niraj Kadam** (CDAC PG-DBDA & Computer Science Graduate).  
Targeted for **Qualcomm Snapdragon AI Challenge**, **AI/ML Engineer**, **Data Engineer**, and **GenAI Engineer** roles.
