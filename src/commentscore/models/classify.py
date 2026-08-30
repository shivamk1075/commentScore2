import os
import joblib
import requests
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = BASE_DIR / "models"

# Fetch the URL securely from the environment
MODAL_API_URL = os.getenv("MODAL_API_URL")

# --- 1. Fast Mode: SGD Classifier ---
@st.cache_resource
def load_sgd():
    vectorizer = joblib.load(MODEL_DIR / "sgd" / "tfidf_vectorizer.pkl")
    model = joblib.load(MODEL_DIR / "sgd" / "SGDClassifier_model.pkl")
    return vectorizer, model

def classify_fast(comments: list[str]):
    vectorizer, model = load_sgd()
    X = vectorizer.transform(comments)
    preds = model.predict(X)
    label_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    return [label_map[p] for p in preds]

# --- 2. Full Mode: DistilBERT ---
def classify_full(comments: list[str]):
    if not MODAL_API_URL:
        st.error("Configuration Error: MODAL_API_URL is missing.")
        return ["ERROR"] * len(comments)

    try:
        response = requests.post(MODAL_API_URL, json={"comments": comments}, timeout=30)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {e}")
        return ["ERROR"] * len(comments)

# --- 3. Unified Entry Point ---
def classify_comments(comments: list[str], mode: str = "Fast"):
    if not comments: 
        return []
    return classify_full(comments) if mode == "Full" else classify_fast(comments)