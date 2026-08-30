# src/commentscore/visualization/visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

def plot_distribution(labels: list[str]):
    fig, ax = plt.subplots()
    sns.countplot(x=labels, order=["POSITIVE", "NEUTRAL", "NEGATIVE"], ax=ax)
    ax.set_title("Sentiment Distribution")
    ax.set_ylabel("Number of Comments")
    return fig

def generate_wordcloud(comments: list[str], sentiment: str):
    text = " ".join(comments)
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(f"{sentiment} Word Cloud")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig