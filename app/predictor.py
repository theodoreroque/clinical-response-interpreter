from app.schemas import PredictResponse


MODEL_VERSION = "mock-0.1.0"
CLARIFICATION_THRESHOLD = 0.70


class MockPredictor:
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

        predicted_answer = "Yes" if scores["YES"] >= scores["NO"] else "No"
        confidence = max(scores.values())

        return PredictResponse(
            predicted_answer=predicted_answer,
            confidence=confidence,
            scores=scores,
            needs_clarification=confidence < CLARIFICATION_THRESHOLD,
            model_version=MODEL_VERSION,
        )


predictor = MockPredictor()

