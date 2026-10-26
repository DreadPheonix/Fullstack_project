# Implementation Plan - SMS Spam Detection Pipeline

This project answers one simple question: when a new SMS arrives, should we treat it as normal ham or spam?

The pipeline works in a straight line:

```text
Original and Hugging Face datasets
    -> Parquet dataset
    -> cleaned messages
    -> TF-IDF numbers
    -> trained candidate models
    -> selected model
    -> evaluation report
    -> prediction for a new message
```

## 1. Start With The Data

The original data lives in `Dataset/combined_dataset.csv`. Training also loads four Hugging Face datasets:

- `ucirvine/sms_spam`
- `PrasadAdsul21/Spam-MailClassification-Dataset`
- `Goodmotion/spam-mail`
- `daviiiidcpp1/sms-spam-combined`

After source-specific column mapping, each useful row has two values:

- `text`: the message
- `target`: either `ham` or `spam`

The project contains 10,961 messages. Most are ham, so the classes are not perfectly balanced. That matters because a model could look accurate simply by guessing ham most of the time. For that reason, spam precision, recall, and F1 score are important throughout the workflow.

### `src/data.py`

I can think of this file as the dataset converter. It asks:

> Do I already have a Parquet version of the CSV, and is it still newer than the CSV?

If the answer is no, it reads the CSV and writes `Dataset/combined_dataset.parquet`. If the Parquet file is already current, it leaves it alone. The training and evaluation scripts then use Parquet because it is convenient and generally faster to load.

Run it with:

```powershell
.\.venv\Scripts\python.exe src\data.py
```

## 2. Clean The Messages

### `ml/preprocess.py`

Before a model can learn from messages, the text needs to be made consistent. The `clean_text()` function asks:

> Which parts of this message carry useful language, and which parts are noise caused by formatting?

It then:

1. Rejects non-string values by returning an empty string.
2. Converts HTML entities into normal characters.
3. Converts all text to lowercase.
4. Removes URLs.
5. Removes HTML tags and remaining HTML entities.
6. Replaces punctuation with spaces.
7. Replaces line breaks and repeated whitespace with one space.

For example:

```text
"URGENT! Visit https://example.com NOW!!!"
```

becomes:

```text
"urgent visit now"
```

The same cleaning function is used during training, evaluation, and prediction. That consistency is essential: if training sees one version of the text and prediction sees another, the model is being asked to understand two different languages.

## 3. Train The Models

### `ml/train.py`

The training script follows this conversation with itself:

> I have messages and labels. How do I test whether a model can generalize to messages it has not seen?

It performs these steps:

1. Loads the CSV once for a read-speed comparison.
2. Loads the actual dataset from Parquet.
3. Downloads the four Hugging Face datasets and maps their source-specific columns to `text` and `target`.
4. Combines all rows, removes exact duplicates, and drops invalid rows.
5. Cleans every message with `clean_text()`.
6. Converts labels into numbers: ham is `0`, spam is `1`.
7. Splits the combined data into 80% training data and 20% test data.
8. Uses stratification so both splits keep a similar ham-to-spam ratio.

### Turn Words Into Numbers

Machine-learning models cannot work directly with raw sentences. The `TfidfVectorizer` turns the cleaned messages into numerical feature vectors.

The vectorizer uses:

- Up to 3,000 features
- Single words and two-word combinations, called unigrams and bigrams

The training data is used to fit the vectorizer. The test data is only transformed with that already-fitted vectorizer. This prevents information from the test set leaking into training.

### Compare Candidate Models

The script tests two classical models:

- `MultinomialNB`, which works well with word-count-like text features
- `LogisticRegression`, configured with balanced class weights so spam is not ignored because it is the smaller class

For each candidate, `GridSearchCV` tries several parameter values using five-fold stratified cross-validation:

- Naive Bayes tunes `alpha`.
- Logistic Regression tunes `C`.

The model is mainly judged by spam F1 score. F1 is useful here because it combines precision and recall into one score. We also compare training and test results:

> If the training score is much higher than the test score, the model may have memorized the training messages instead of learning a reusable pattern.

Candidates with an F1 gap greater than 5% are rejected. Among the remaining candidates, the one with the highest test spam F1 score is selected.

The selected model and the fitted vectorizer are saved as:

```text
model/model.pkl
model/vectorizer.pkl
```

Run training with:

```powershell
.\.venv\Scripts\python.exe ml\train.py
```

The `datasets` package is required for the additional training sources.

## 4. Evaluate The Saved Model

### `ml/evaluate.py`

Evaluation asks a slightly different question:

> Now that the model has been saved, how well does that exact model perform on the held-out test messages?

The script repeats the same cleaning and 80/20 stratified split, then loads `model.pkl` and `vectorizer.pkl`. It calculates:

- Accuracy: how many predictions were correct overall
- Precision for spam: how many messages called spam were actually spam
- Recall for spam: how much of the real spam was found
- Spam F1 score: the combined precision and recall score
- A classification report for ham and spam
- A confusion matrix showing the four prediction outcomes
- Train-versus-test accuracy and F1 gaps
- The ham/spam class distribution

It also saves the confusion matrix image to:

```text
model/evaluation.png
```

Run evaluation with:

```powershell
.\.venv\Scripts\python.exe ml\evaluate.py
```

The report prints the actual model class, so there is no need to guess which candidate was selected. The current combined-data artifact uses `LogisticRegression`.

## 5. Predict A New Message

### `app.py` and `user_input.py`

`app.py` is the public prediction service. It loads the model and vectorizer once, exposes the `POST /predict` endpoint, and provides the `predict()` function. `user_input.py` reads a message from the terminal and sends it to that function.

When `predict(message)` is called, it asks:

> Is this input valid, and if it is, what does the trained model believe?

It then:

1. Rejects non-string input.
2. Rejects empty input.
3. Limits the message to 5,000 characters.
4. Cleans the message.
5. Applies the saved TF-IDF vectorizer.
6. Gets the model prediction and probability.
7. Converts `0` and `1` back into `ham` and `spam`.

The normal result looks like this:

```python
{"label": "spam", "confidence": 0.9989}
```

Invalid input returns a predictable result with an error field instead of crashing:

```python
{"label": "ham", "confidence": 0.0, "error": "empty_input"}
```

Example:

```powershell
.\.venv\Scripts\python.exe user_input.py
```

## 6. Complete Verification Checklist

The whole workflow can be checked in this order:

1. Convert or refresh the Parquet dataset with `src\data.py`.
2. Train and save the model with `ml\train.py`.
3. Evaluate the saved artifacts with `ml\evaluate.py`.
4. Confirm the train/test F1 gap stays below 5%.
5. Try normal and suspicious messages through `user_input.py` or the `/predict` endpoint.
6. Confirm the prediction result contains a label and confidence value.
7. Confirm `model\model.pkl`, `model\vectorizer.pkl`, and `model\evaluation.png` exist.
8. Compile the Python files to catch syntax errors:

```powershell
.\.venv\Scripts\python.exe -m py_compile config.py app.py user_input.py ml\preprocess.py ml\train.py ml\evaluate.py src\data.py
```

At the end of the process, the project has three distinct responsibilities:

- Training learns the spam patterns.
- Evaluation measures whether those patterns generalize.
- Prediction uses the saved knowledge on a new message.

That separation keeps the workflow understandable and makes it clear which step to run when the dataset or model changes.
