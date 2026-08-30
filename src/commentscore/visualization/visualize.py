# src/visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

def plot_distribution(labels: list[str]) -> None:
    """
    Bar chart of POSITIVE / NEUTRAL / NEGATIVE counts.
    """
    sns.countplot(x=labels, order=["POSITIVE","NEUTRAL","NEGATIVE"])
    plt.title("Sentiment Distribution")
    plt.ylabel("Number of Comments")
    plt.show()

def generate_wordcloud(comments: list[str], sentiment: str) -> None:
    """
    Display word cloud for comments of a given sentiment.
    """
    text = " ".join(comments)
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    plt.figure(figsize=(10,5))
    plt.title(f"{sentiment} Word Cloud")
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()
