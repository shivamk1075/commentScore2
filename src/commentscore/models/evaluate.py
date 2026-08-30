# src/evaluate.py
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def evaluate_comments(true_labels: list[str], pred_labels: list[str]) -> None:
    """
    Print accuracy, classification report and confusion matrix.
    """
    acc = accuracy_score(true_labels, pred_labels)
    print(f"Accuracy: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(true_labels, pred_labels, digits=4))
    
    cm = confusion_matrix(true_labels, pred_labels,
                          labels=["POSITIVE","NEUTRAL","NEGATIVE"])
    print("Confusion Matrix:")
    print(cm)

if __name__ == "__main__":
    # Example: replace with your test split
    y_true = ["POSITIVE","NEGATIVE","NEUTRAL","POSITIVE"]
    y_pred = ["POSITIVE","NEUTRAL","NEUTRAL","POSITIVE"]
    evaluate_comments(y_true, y_pred)
