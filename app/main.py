import streamlit as st
import matplotlib.pyplot as plt
from commentscore.data.data_fetch import fetch_comments
from commentscore.features.preprocess import preprocess_comments
from commentscore.models.classify import classify_comments
from commentscore.models.aggregate import aggregate_video_sentiment
from commentscore.visualization.visualize import plot_distribution, generate_wordcloud

st.title("YouTube Comment Sentiment Analyzer")
video_id = st.text_input("Enter YouTube Video ID:")

if st.button("Analyze Video"):
    if not video_id:
        st.error("Please enter a valid Video ID.")
    else:
        with st.spinner("Fetching comments..."):
            raw_comments = fetch_comments(video_id, max_results=100)
            
        if not raw_comments:
            st.warning("No comments found or API limit reached.")
        else:
            with st.spinner("Processing and classifying sentiments..."):
                cleaned_comments = preprocess_comments(raw_comments)
                labels = classify_comments(cleaned_comments)
                final_verdict = aggregate_video_sentiment(cleaned_comments, labels)
            
            st.success(f"Video Verdict: {final_verdict}")
            
            st.subheader("Sentiment Distribution")
            fig_dist = plot_distribution(labels)
            st.pyplot(fig_dist)