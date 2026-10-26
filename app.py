import pathlib
from typing import Any

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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
LABEL_MAP = {value: label for label, value in DATA_CONFIG["class_mapping"].items()}

MODEL = joblib.load(MODEL_PATH)
VECTORIZER = joblib.load(VECTORIZER_PATH)
app = FastAPI(
    title="Spam Detection API",
    description="Detect whether a message is spam or ham using a trained ML model.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class PredictRequest(BaseModel):
    message: str


def invalid_result(error: str) -> dict[str, Any]:
    default_label = next(iter(DATA_CONFIG["class_mapping"]))
    return {"label": default_label, "confidence": 0.0, "error": error}


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


@app.get("/")
def status_route() -> dict[str, str]:
    return {"status": "ready", "endpoint": "/predict"}


@app.get("/health")
def health_route() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/predict")
def predict_route(payload: PredictRequest) -> dict[str, Any]:
    result = predict(payload.message)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


if __name__ == "__main__":
    import uvicorn

    app_config = CONFIG["app"]
    uvicorn.run("app:app", host=app_config["host"], port=app_config["port"], reload=False)
