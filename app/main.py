from fastapi import FastAPI

from app.predictor import MODEL_VERSION, predictor
from app.schemas import HealthResponse, PredictRequest, PredictResponse


app = FastAPI(title="Clinical Response Interpreter")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_version=MODEL_VERSION,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    return predictor.predict(payload.question, payload.response)

