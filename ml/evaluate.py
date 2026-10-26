import pathlib
import sys

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from config import load_config
from ml.preprocess import clean_text
from ml.train import load_dataset as load_training_dataset


BASE_DIR = pathlib.Path(__file__).parent.parent
CONFIG = load_config()
PATHS = CONFIG["paths"]
DATA_CONFIG = CONFIG["data"]
TRAINING_CONFIG = CONFIG["training"]
MODEL_PATH = BASE_DIR / PATHS["model_directory"] / PATHS["model"]
VECTORIZER_PATH = BASE_DIR / PATHS["model_directory"] / PATHS["vectorizer"]
EVALUATION_PLOT_PATH = BASE_DIR / PATHS["model_directory"] / PATHS["evaluation_plot"]
PREVIOUS_METRICS = CONFIG["evaluation"]["previous_metrics"]
CLASS_NAMES = list(DATA_CONFIG["class_mapping"])


def load_test_data():
    dataset = load_training_dataset().dropna(
        subset=[DATA_CONFIG["target_column"], DATA_CONFIG["text_column"]]
    )
    messages = dataset[DATA_CONFIG["text_column"]].apply(clean_text)
    labels = dataset[DATA_CONFIG["target_column"]].map(DATA_CONFIG["class_mapping"])

    split = train_test_split(
        messages,
        labels,
        test_size=TRAINING_CONFIG["test_size"],
        random_state=TRAINING_CONFIG["random_state"],
        stratify=labels,
    )
    return split, labels


def calculate_metrics(model, vectorizer, split):
    train_messages, test_messages, train_labels, test_labels = split
    train_features = vectorizer.transform(train_messages)
    test_features = vectorizer.transform(test_messages)
    train_predictions = model.predict(train_features)
    test_predictions = model.predict(test_features)

    return {
        "train_accuracy": accuracy_score(train_labels, train_predictions),
        "test_accuracy": accuracy_score(test_labels, test_predictions),
        "train_f1": f1_score(train_labels, train_predictions, pos_label=1),
        "test_f1": f1_score(test_labels, test_predictions, pos_label=1),
        "precision": precision_score(test_labels, test_predictions, pos_label=1),
        "recall": recall_score(test_labels, test_predictions, pos_label=1),
        "confusion_matrix": confusion_matrix(test_labels, test_predictions),
        "test_labels": test_labels,
        "test_predictions": test_predictions,
    }


def print_report(model, labels, metrics) -> None:
    total = len(labels)
    spam_count = int(labels.sum())
    ham_count = total - spam_count
    previous = PREVIOUS_METRICS

    print("EVALUATION REPORT")
    print(
        f"Data Source: {len(PATHS['local_datasets'])} local Parquet datasets + "
        f"{len(DATA_CONFIG['datasets'])} configured Hugging Face datasets"
    )
    print(f"Class Imbalance Note: Total={total}, Ham={ham_count} ({ham_count / total:.2%}), Spam={spam_count} ({spam_count / total:.2%})")
    print(f"Model Type: {type(model).__name__}")
    print("Metric Comparison (Previous baseline vs current combined-data model):")
    print(f"  Accuracy:  {previous['accuracy']:.4f} -> {metrics['test_accuracy']:.4f} (Diff: {metrics['test_accuracy'] - previous['accuracy']:+.4f})")
    print(f"  Precision: {previous['precision']:.4f} -> {metrics['precision']:.4f} (Diff: {metrics['precision'] - previous['precision']:+.4f})")
    print(f"  Recall:    {previous['recall']:.4f} -> {metrics['recall']:.4f} (Diff: {metrics['recall'] - previous['recall']:+.4f})")
    print(f"  Spam F1:   {previous['f1']:.4f} -> {metrics['test_f1']:.4f} (Diff: {metrics['test_f1'] - previous['f1']:+.4f})")
    print("Train vs Test Comparison (Generalization Check):")
    print(f"  Train Accuracy: {metrics['train_accuracy']:.4f} | Test Accuracy: {metrics['test_accuracy']:.4f} (Gap: {abs(metrics['train_accuracy'] - metrics['test_accuracy']):.4f})")
    print(f"  Train Spam F1:  {metrics['train_f1']:.4f} | Test Spam F1:  {metrics['test_f1']:.4f} (Gap: {abs(metrics['train_f1'] - metrics['test_f1']):.4f})")
    print("Classification Report:")
    print(classification_report(metrics["test_labels"], metrics["test_predictions"], target_names=CLASS_NAMES))
    print("Confusion Matrix:")
    print(metrics["confusion_matrix"])


def save_confusion_matrix(confusion) -> None:
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        confusion,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
    )
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(EVALUATION_PLOT_PATH)
    plt.close()


def run_evaluation() -> None:
    split, labels = load_test_data()
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    metrics = calculate_metrics(model, vectorizer, split)

    print_report(model, labels, metrics)
    save_confusion_matrix(metrics["confusion_matrix"])


if __name__ == "__main__":
    run_evaluation()
