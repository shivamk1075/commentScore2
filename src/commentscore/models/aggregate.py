# src/aggregate.py

import pandas as pd
from typing import List

def aggregate_video_sentiment(comments: List[str],
                              labels: List[str]) -> str:
    """
    Given a list of cleaned comments and their corresponding
    sentiment labels, return a video‐level label:
    'Useful', 'Partially Useful', or 'Not Useful'.
    """
    df = pd.DataFrame({
        "comment": comments,
        "sentiment": labels
    })
    # Compute normalized counts
    prop = df.sentiment.value_counts(normalize=True)
    
    if prop.get("POSITIVE", 0) > 1.25*prop.get("NEGATIVE", 0):
        return "Useful"
    # if prop.get("NEGATIVE", 0) > 0.5:
        return "Not Useful"
    return "Partially Useful"

if __name__ == "__main__":
    # Quick smoke test
    sample_comments = ["good", "bad", "okay", "awesome", "terrible"]
    sample_labels   = ["POSITIVE", "NEGATIVE", "NEUTRAL", "POSITIVE", "NEGATIVE"]
    print(aggregate_video_sentiment(sample_comments, sample_labels))
    # Expect "Partially Useful" since POS=2/5, NEG=2/5
