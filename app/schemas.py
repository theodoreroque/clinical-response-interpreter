from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    question: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    predicted_answer: str
    confidence: float
    scores: dict[str, float]
    needs_clarification: bool
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str

