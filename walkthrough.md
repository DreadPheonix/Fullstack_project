# Walkthrough - SMS Spam Detection ML Pipeline

Built and verified the lightweight Machine Learning pipeline for SMS Spam Detection in accordance with all constraints.

## 1. Accomplished Work

### Core ML Architecture & Files (`ml/` & root)
- **`ml/preprocess.py`**: Clean text normalization function (`clean_text`) removing URLs, HTML tags, punctuation, and extra whitespace.
- **`ml/train.py`**: Combines the original corpus with four Hugging Face spam datasets, normalizes their schemas, removes exact duplicates, vectorizes with `TfidfVectorizer(max_features=3000, ngram_range=(1,2))`, tunes `MultinomialNB` and `LogisticRegression` with 5-fold `StratifiedKFold` `GridSearchCV`, checks overfitting (F1 gap < 5%), and serializes the selected model.
- **`ml/evaluate.py`**: Comprehensive evaluation report generation, confusion matrix computation, class imbalance metrics, and chart generation (`model/evaluation.png`).
- **`app.py`**: Exposes the `predict(message: str) -> dict` function and Flask `POST /predict` endpoint. Pre-loads model and vectorizer at module import time.
- **`user_input.py`**: Reads a message from the terminal and sends it to the app for classification.

### Zero-Comments Compliance
- Checked all codebase files (`ml/preprocess.py`, `ml/train.py`, `ml/evaluate.py`, `app.py`, `user_input.py`).
- **Zero code comments** (no inline comments, no block comments, no docstrings) present across all files.

---

## 2. Evaluation Results & Performance Metrics

### Class Imbalance Report
- **Total Samples**: 10,961
- **Ham Messages**: 8,555 (78.05%)
- **Spam Messages**: 2,406 (21.95%)

### Model Comparison & Generalization Check

| Candidate Model | Best Hyperparameters | Train Acc | Test Acc | Train Spam F1 | Test Spam F1 | Generalization F1 Gap | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MultinomialNB** | `alpha=0.01` | **95.62%** | **94.98%** | **0.9011** | **0.8882** | **0.0129 (1.29%)** | **SELECTED** |
| LogisticRegression | `C=1.5`, `class_weight='balanced'` | 96.51% | 94.71% | 0.9236 | 0.8861 | 0.0376 (3.76%) | Passed |

- **Chosen Model after adding the four datasets**: `LogisticRegression` with `C=1.5`. It achieved a combined-data test Spam F1 of `0.9126` with a generalization gap of `0.0100`.

### Detailed Classification Metrics (Test Set)
- **Overall Accuracy**: **94.98%**
- **Spam Precision**: **86.88%**
- **Spam Recall**: **90.85%**
- **Spam F1-Score**: **0.8882**

### Confusion Matrix
```
               Predicted Ham   Predicted Spam
Actual Ham          1646             66
Actual Spam           44            437
```

---

## 3. Verification & Performance Benchmarks

### Serialization File Sizes (`model/`)
- `model.pkl`: **0.09 MB**
- `vectorizer.pkl`: **0.11 MB**
- **Combined Size**: **0.20 MB** (Target < a few MB: **Passed**)

### Inference Latency & Function Signature (`app.py`)
- Signature: `predict(message: str) -> dict` returning `{"label": "spam" | "ham", "confidence": float}`
- **Single message prediction latency**: **1.99 ms** (Target < 50ms: **Passed**)

### Sample Predictions Tested
```python
predict("Hey, are we still meeting for lunch today at 1 PM?")
# -> {'label': 'ham', 'confidence': 0.9908}

predict("URGENT! You have won a 1000 cash prize! Call 08000123456 NOW to claim your reward!")
# -> {'label': 'spam', 'confidence': 1.0}
```
