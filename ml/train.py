import pathlib
import sys
import time

import joblib
import pandas as pd
from datasets import load_dataset as hf_load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from config import load_config
from ml.preprocess import clean_text


BASE_DIR = pathlib.Path(__file__).parent.parent
CONFIG = load_config()
PATHS = CONFIG["paths"]
DATA_CONFIG = CONFIG["data"]
TRAINING_CONFIG = CONFIG["training"]
DATASET_DIR = BASE_DIR / PATHS["dataset_directory"]
MODEL_DIR = BASE_DIR / PATHS["model_directory"]
TEXT_COLUMN = DATA_CONFIG["text_column"]
TARGET_COLUMN = DATA_CONFIG["target_column"]


def load_dataset() -> pd.DataFrame:
    local_datasets = []
    for local_source in PATHS["local_datasets"]:
        csv_path = DATASET_DIR / local_source["csv"]
        parquet_path = DATASET_DIR / local_source["parquet"]
        if not parquet_path.exists():
            raise FileNotFoundError(f"Missing Parquet dataset: {parquet_path}. Run src\\data.py first.")

        csv_start = time.perf_counter()
        pd.read_csv(csv_path)
        csv_time = (time.perf_counter() - csv_start) * 1000
        parquet_start = time.perf_counter()
        local = pd.read_parquet(parquet_path)
        parquet_time = (time.perf_counter() - parquet_start) * 1000
        local = normalize_dataframe(local, local_source["parquet"])
        print(f"  {local_source['parquet']}: {len(local)} usable samples")
        print(f"    CSV: {csv_time:.2f} ms | Parquet: {parquet_time:.2f} ms")
        local_datasets.append(local)

    additional_datasets = []
    for dataset_name in DATA_CONFIG["datasets"]:
        loaded = hf_load_dataset(dataset_name)
        splits = loaded.items() if hasattr(loaded, "items") else [("default", loaded)]
        split_frames = []
        for split_name, split in splits:
            split_frame = split.to_pandas()
            text_column = next((column for column in DATA_CONFIG["text_columns"] if column in split_frame.columns), None)
            label_column = next((column for column in DATA_CONFIG["label_columns"] if column in split_frame.columns), None)
            if text_column is None or label_column is None:
                raise ValueError(
                    f"Dataset '{dataset_name}' split '{split_name}' must contain a text and label column. "
                    f"Found: {list(split_frame.columns)}"
                )

            normalized = pd.DataFrame(
                {
                    TEXT_COLUMN: split_frame[text_column],
                    TARGET_COLUMN: split_frame[label_column].map(normalize_label),
                }
            )
            split_frames.append(normalized)

        additional = pd.concat(split_frames, ignore_index=True)
        additional = additional.dropna(subset=[TARGET_COLUMN, TEXT_COLUMN])
        print(f"  {dataset_name}: {len(additional)} usable samples")
        additional_datasets.append(additional)

    combined = pd.concat([*local_datasets, *additional_datasets], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=[DATA_CONFIG["target_column"], DATA_CONFIG["text_column"]]
    ).reset_index(drop=True)
    print(f"  Combined unique samples: {len(combined)}")
    return combined


def normalize_dataframe(frame: pd.DataFrame, source_name: str) -> pd.DataFrame:
    text_column = next((column for column in DATA_CONFIG["text_columns"] if column in frame.columns), None)
    label_column = next((column for column in DATA_CONFIG["label_columns"] if column in frame.columns), None)
    if text_column is None or label_column is None:
        raise ValueError(
            f"Dataset '{source_name}' must contain a text and label column. Found: {list(frame.columns)}"
        )
    normalized = pd.DataFrame(
        {
            TEXT_COLUMN: frame[text_column],
            TARGET_COLUMN: frame[label_column].map(normalize_label),
        }
    )
    return normalized.dropna(subset=[TARGET_COLUMN, TEXT_COLUMN])


def normalize_label(label) -> str | None:
    if pd.isna(label):
        return None

    normalized = str(label).strip().lower()
    for label, values in DATA_CONFIG["labels"].items():
        if normalized in values:
            return label
    return None


def prepare_data(dataset: pd.DataFrame):
    messages = dataset[TEXT_COLUMN].apply(clean_text)
    labels = dataset[TARGET_COLUMN].map(DATA_CONFIG["class_mapping"])

    total = len(labels)
    spam_count = int(labels.sum())
    ham_count = total - spam_count

    print("\nClass Imbalance Report:")
    print(f"  Total Samples: {total}")
    print(f"  Ham: {ham_count} ({ham_count / total:.2%})")
    print(f"  Spam: {spam_count} ({spam_count / total:.2%})")

    return train_test_split(
        messages,
        labels,
        test_size=TRAINING_CONFIG["test_size"],
        random_state=TRAINING_CONFIG["random_state"],
        stratify=labels,
    )


def find_best_models(training_features, training_labels, validation_splitter):
    naive_bayes_search = GridSearchCV(
        MultinomialNB(),
        param_grid={"alpha": TRAINING_CONFIG["naive_bayes_alpha"]},
        cv=validation_splitter,
        scoring="f1",
        n_jobs=1,
    )
    naive_bayes_search.fit(training_features, training_labels)

    logistic_regression_search = GridSearchCV(
        LogisticRegression(
            class_weight="balanced",
            max_iter=TRAINING_CONFIG["max_iter"],
            random_state=TRAINING_CONFIG["random_state"],
        ),
        param_grid={"C": TRAINING_CONFIG["logistic_regression_c"]},
        cv=validation_splitter,
        scoring="f1",
        n_jobs=1,
    )
    logistic_regression_search.fit(training_features, training_labels)

    return [
        ("MultinomialNB", naive_bayes_search.best_estimator_, naive_bayes_search.best_params_),
        ("LogisticRegression", logistic_regression_search.best_estimator_, logistic_regression_search.best_params_),
    ]


def choose_model(candidates, training_features, test_features, training_labels, test_labels):
    selected_model = None
    selected_name = ""
    selected_f1 = -1.0

    print("\nModel Candidate Evaluation:")
    for name, model, parameters in candidates:
        train_predictions = model.predict(training_features)
        test_predictions = model.predict(test_features)

        train_accuracy = accuracy_score(training_labels, train_predictions)
        test_accuracy = accuracy_score(test_labels, test_predictions)
        train_f1 = f1_score(training_labels, train_predictions, pos_label=1)
        test_f1 = f1_score(test_labels, test_predictions, pos_label=1)
        f1_gap = abs(train_f1 - test_f1)
        accuracy_gap = abs(train_accuracy - test_accuracy)

        print(f"\nModel: {name}")
        print(f"  Best Parameters: {parameters}")
        print(f"  Train Accuracy: {train_accuracy:.4f} | Test Accuracy: {test_accuracy:.4f} (Gap: {accuracy_gap:.4f})")
        print(f"  Train Spam F1: {train_f1:.4f} | Test Spam F1: {test_f1:.4f} (Gap: {f1_gap:.4f})")

        if f1_gap > TRAINING_CONFIG["overfitting_gap_limit"]:
            print(f"  Warning: Generalization gap ({f1_gap:.4f}) exceeds 5%. Rejected due to overfitting.")
            continue

        if test_f1 > selected_f1:
            selected_model = model
            selected_name = name
            selected_f1 = test_f1

    if selected_model is None:
        selected_model = candidates[0][1]
        selected_name = candidates[0][0]
        selected_f1 = f1_score(test_labels, selected_model.predict(test_features), pos_label=1)

    print(f"\nSelected Best Model: {selected_name} with Test Spam F1: {selected_f1:.4f}")
    return selected_model


def run_training() -> None:
    dataset = load_dataset()
    train_messages, test_messages, train_labels, test_labels = prepare_data(dataset)

    vectorizer = TfidfVectorizer(
        max_features=TRAINING_CONFIG["max_features"],
        ngram_range=tuple(TRAINING_CONFIG["ngram_range"]),
    )
    train_features = vectorizer.fit_transform(train_messages)
    test_features = vectorizer.transform(test_messages)

    validation_splitter = StratifiedKFold(
        n_splits=TRAINING_CONFIG["validation_folds"],
        shuffle=True,
        random_state=TRAINING_CONFIG["random_state"],
    )
    candidates = find_best_models(train_features, train_labels, validation_splitter)
    model = choose_model(candidates, train_features, test_features, train_labels, test_labels)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / PATHS["model"]
    vectorizer_path = MODEL_DIR / PATHS["vectorizer"]
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print(f"Saved model to {model_path}")
    print(f"Saved vectorizer to {vectorizer_path}")


if __name__ == "__main__":
    run_training()
