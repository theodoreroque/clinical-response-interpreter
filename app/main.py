from fastapi import FastAPI

from app.predictor import create_predictor
from app.schemas import HealthResponse, PredictRequest, PredictResponse
from app.settings import get_settings


app = FastAPI(title="Clinical Response Interpreter")
settings = get_settings()
predictor = create_predictor(settings)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=predictor.model_loaded,
        model_version=predictor.model_version,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    return predictor.predict(payload.question, payload.response)
