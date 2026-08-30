# src/preprocess.py

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure NLTK resources are downloaded
nltk.download("stopwords")
nltk.download("wordnet")

# Initialize stop-words and lemmatizer
STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_comment(text: str) -> str:
    """
    Lowercase, strip URLs and non-alphabetic chars,
    tokenize, remove stop-words, lemmatize, and rejoin.
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(tok) for tok in tokens if tok not in STOP_WORDS]
    return " ".join(tokens)

def preprocess_comments(comments: list[str]) -> list[str]:
    """
    Apply clean_comment to a list of raw comments.
    """
    return [clean_comment(c) for c in comments]

if __name__ == "__main__":
    # Quick test
    sample = [
        "This video is GREAT!!! Thanks 😊 https://youtu.be/xyz",
        "I didn't like the part about Windows 11."
    ]
    print(preprocess_comments(sample))
