import argparse
import pathlib
from typing import Any

import joblib

from config import load_config
from ml.preprocess import clean_text

BASE_DIR = pathlib.Path(__file__).parent
CONFIG = load_config()
PATHS = CONFIG["paths"]
DATA_CONFIG = CONFIG["data"]
MODEL_DIR = BASE_DIR / PATHS["model_directory"]
MODEL_PATH = MODEL_DIR / PATHS["model"]
VECTORIZER_PATH = MODEL_DIR / PATHS["vectorizer"]
MAX_MESSAGE_LENGTH = CONFIG["prediction"]["max_message_length"]

MODEL = joblib.load(MODEL_PATH)
VECTORIZER = joblib.load(VECTORIZER_PATH)
LABEL_MAP = {value: label for label, value in DATA_CONFIG["class_mapping"].items()}


def invalid_result(error: str) -> dict[str, Any]:
    return {"label": next(iter(DATA_CONFIG["class_mapping"])), "confidence": 0.0, "error": error}


def predict(message: str) -> dict[str, Any]:
    if not isinstance(message, str):
        return invalid_result("invalid_input")

    if not message.strip():
        return invalid_result("empty_input")

    cleaned = clean_text(message[:MAX_MESSAGE_LENGTH])
    if not cleaned.strip():
        return invalid_result("empty_input")

    features = VECTORIZER.transform([cleaned])
    prediction = int(MODEL.predict(features)[0])
    confidence = float(MODEL.predict_proba(features)[0][prediction])

    return {
        "label": LABEL_MAP[prediction],
        "confidence": round(confidence, 4),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="+", help="Message to classify")
    arguments = parser.parse_args()
    print(predict(" ".join(arguments.message)))
