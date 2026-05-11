from pydantic import BaseModel, Field, ConfigDict


class PredictRequest(BaseModel):
    question: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_answer: str
    confidence: float
    scores: dict[str, float]
    needs_clarification: bool
    model_version: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    predictor_loaded: bool
    model_source: str
    model_package: str
    model_path: str | None
    model_version: str
