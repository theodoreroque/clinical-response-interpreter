from importlib import import_module
from typing import Protocol

from app.schemas import PredictResponse
from app.settings import Settings, get_settings


class Predictor(Protocol):
    model_loaded: bool
    model_version: str

    def predict(self, question: str, response: str) -> PredictResponse:
        ...


def format_prediction(scores: dict[str, float], settings: Settings) -> PredictResponse:
    yes_score = scores.get("YES", 0.0)
    no_score = scores.get("NO", 0.0)
    confidence = max(yes_score, no_score)

    if confidence < settings.clarification_threshold:
        predicted_answer = "Unclear"
        needs_clarification = True
    else:
        predicted_answer = "Yes" if yes_score >= no_score else "No"
        needs_clarification = False

    return PredictResponse(
        predicted_answer=predicted_answer,
        confidence=confidence,
        scores=scores,
        needs_clarification=needs_clarification,
        model_version=settings.model_version,
    )


class MockPredictor:
    model_loaded = True

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_version = settings.model_version

    def predict(self, question: str, response: str) -> PredictResponse:
        text = f"{question} {response}".lower()

        no_terms = (" no", "not", "never", "nope", "nah")
        yes_terms = ("yes", "yeah", "yep", "sure", "absolutely")

        if any(term in text for term in no_terms):
            scores = {"YES": 0.12, "NO": 0.88}
        elif any(term in text for term in yes_terms):
            scores = {"YES": 0.86, "NO": 0.14}
        else:
            scores = {"YES": 0.52, "NO": 0.48}

        return format_prediction(scores, self.settings)


class SpacyPredictor:
    model_loaded = False

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_version = settings.model_version
        self.nlp = self._load_model()
        self.model_loaded = True

    def _load_model(self):
        if self.settings.model_source == "path":
            if not self.settings.model_path:
                raise ValueError("MODEL_PATH is required when MODEL_SOURCE=path")

            import spacy

            return spacy.load(self.settings.model_path)

        if self.settings.model_source != "package":
            raise ValueError(
                "MODEL_SOURCE must be one of: package, path, mock"
            )

        model_package = import_module(self.settings.model_package)
        return model_package.load()

    def predict(self, question: str, response: str) -> PredictResponse:
        doc = self.nlp(f"{question} {response}")
        return format_prediction(dict(doc.cats), self.settings)


def create_predictor(settings: Settings | None = None) -> Predictor:
    resolved_settings = settings or get_settings()
    if resolved_settings.model_source == "mock":
        return MockPredictor(resolved_settings)

    return SpacyPredictor(resolved_settings)
