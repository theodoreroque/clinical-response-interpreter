from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.predictor import create_predictor
from app.schemas import HealthResponse, PredictRequest, PredictResponse
from app.settings import get_settings


app = FastAPI(title="Clinical Response Interpreter")
settings = get_settings()
predictor = create_predictor(settings)
static_dir = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        predictor_loaded=predictor.model_loaded,
        model_source=settings.model_source,
        model_package=settings.model_package,
        model_path=settings.model_path,
        model_version=predictor.model_version,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    return predictor.predict(payload.question, payload.response)
