# AI Climate Risk Assistant

An intelligent decision-support system to assess local climate risks and provide role-based safety guidance using AI.

## 🌍 Overview

This project:
- Fetches real-time weather and air quality data
- Scores climate risks (heat, flood, air pollution)
- Explains *why* risks are high or moderate
- Compares your risk with nearby areas
- Generates dynamic safety recommendations using RAG
- Personalizes advice for students, farmers, hospitals, and urban residents

## 🚀 Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **AI:** RAG (Retrieval-Augmented Generation)
- **Models:** Compatible with IBM Granite
- **Vector DB:** Chroma
- **Real-Time APIs:** Weather & AQI

## 🧠 Features

- Explainable AI risk assessment
- Community risk comparison
- Role-specific safety guidance
- Clean, actionable UI

## 🛠 Run Locally

```bash
git clone https://github.com/Hemanthrouth26/AI-Climate-Risk-Assistant.git
cd AI-Climate-Risk-Assistant
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python infra/init_embeddings.py
uvicorn app.backend.main:app --reload
streamlit run app/frontend/streamlit_app.py
