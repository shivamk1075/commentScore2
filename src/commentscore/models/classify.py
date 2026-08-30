# src/classify.py
import joblib


import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import tqdm

nltk.download('stopwords')
nltk.download('wordnet')

def preprocess(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    tokens = text.split()
    lemmatizer = WordNetLemmatizer()
    stops = set(stopwords.words('english'))
    stops.remove('not')  # keep 'not' for sentiment
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stops]
    return ' '.join(tokens)


# # Load the vectorizer and SGDClassifier model
# vectorizer = joblib.load(r"C:\Users\natur\Desktop\Technologies\Projects\Ranking-YT-Tutorials\Github version\SDGClassifier\src\tfidf_vectorizer.pkl")
# model = joblib.load(r"C:\Users\natur\Desktop\Technologies\Projects\Ranking-YT-Tutorials\Github version\SDGClassifier\src\SGDClassifier_model.pkl")
# Load the vectorizer and SGDClassifier model
vectorizer = joblib.load("src/tfidf_vectorizer.pkl")
model = joblib.load("src/SGDClassifier_model.pkl")

def classify_comments(comments: list[str]) -> list[str]:
    """
    Given a list of cleaned comment strings, return a list of sentiment labels.
    """
    # Preprocess comments if needed (should match training preprocessing!)
    # If your vectorizer expects already-cleaned text, just use as is.
    # finalcomments = [preprocess(comment) for comment in comments]
    X = vectorizer.transform(comments)
    preds = model.predict(X)
    # Map numeric predictions to sentiment labels (adjust as needed)
    label_map = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    return [label_map[p] for p in preds]

if __name__ == "__main__":
    # Quick check
    samples = [
        "this video is fantastic and very helpful",
        "i did not find this useful at all"
    ]
    labels = classify_comments(samples)
    print(list(zip(samples, labels)))
