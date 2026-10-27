import pathlib
from typing import Any

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import load_config
from ml.preprocess import clean_text, is_routine_transactional_message


BASE_DIR = pathlib.Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend-v2"
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
    title="SMS Shield API",
    description="SMS spam detection and dashboard serving.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class PredictRequest(BaseModel):
    message: str


app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard.html", include_in_schema=False)
def dashboard_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "dashboard.html")


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
    probabilities = MODEL.predict_proba(features)[0]
    if (
        prediction == DATA_CONFIG["class_mapping"]["spam"]
        and is_routine_transactional_message(message)
    ):
        prediction = DATA_CONFIG["class_mapping"]["ham"]

    class_indices = {int(label): index for index, label in enumerate(MODEL.classes_)}
    confidence = float(probabilities[class_indices[prediction]])

    return {
        "label": LABEL_MAP[prediction],
        "confidence": round(confidence, 4),
    }


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

    uvicorn.run(
        "app:app",
        host=CONFIG["app"]["host"],
        port=CONFIG["app"]["port"],
        reload=False,
    )
