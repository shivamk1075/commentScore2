# import joblib
# import numpy as np
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
# MODEL_DIR = BASE_DIR / "models"

# vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
# model = joblib.load(MODEL_DIR / "SGDClassifier_model.pkl")

# def classify_comments(comments: list[str]):
#     """Returns labels and the top positive/negative comment strings."""
#     if not comments:
#         return [], None, None

#     X = vectorizer.transform(comments)
#     preds = model.predict(X)
#     scores = model.decision_function(X) 
    
#     label_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
#     labels = [label_map[p] for p in preds]
    
#     # Identify highest confidence scores for Highlights
#     top_pos_comment, top_neg_comment = None, None
    
#     pos_idx = np.argmax(scores[:, 2])
#     neg_idx = np.argmax(scores[:, 0])
    
#     if labels[pos_idx] == "POSITIVE":
#         top_pos_comment = comments[pos_idx]
#     if labels[neg_idx] == "NEGATIVE":
#         top_neg_comment = comments[neg_idx]

#     return labels, top_pos_comment, top_neg_comment

import joblib
import numpy as np
import streamlit as st
from pathlib import Path
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, TextClassificationPipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = BASE_DIR / "models"

# --- 1. Fast Mode: SGD Classifier ---
@st.cache_resource
def load_sgd():
    # Updated to look inside the "sgd" folder
    vectorizer = joblib.load(MODEL_DIR / "sgd" / "tfidf_vectorizer.pkl")
    model = joblib.load(MODEL_DIR / "sgd" / "SGDClassifier_model.pkl")
    return vectorizer, model

def classify_fast(comments: list[str]):
    vectorizer, model = load_sgd()
    X = vectorizer.transform(comments)
    preds = model.predict(X)
    label_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    return [label_map[p] for p in preds]

# --- 2. Full Mode: DistilBERT (TensorFlow) ---
@st.cache_resource
def load_distilbert():
    # Updated to look at the new "distilbert" folder
    model_path = str(MODEL_DIR / "distilbert")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = TFAutoModelForSequenceClassification.from_pretrained(model_path)
    
    pipeline = TextClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        return_all_scores=False,
        framework="tf", 
        device=-1 
    )
    return pipeline

def classify_full(comments: list[str]):
    pipeline = load_distilbert()
    
    # Added truncation=True and max_length=512 to prevent crashes on long HN comments
    results = pipeline(
        comments, 
        batch_size=16, 
        truncation=True, 
        max_length=128
    )
    
    return [res["label"] for res in results]

# --- 3. Unified Entry Point ---
def classify_comments(comments: list[str], mode: str = "Fast"):
    if not comments: return []
    return classify_full(comments) if mode == "Full" else classify_fast(comments)