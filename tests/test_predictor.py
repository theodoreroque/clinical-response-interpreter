from app.predictor import format_prediction
from app.settings import Settings


def test_format_prediction_returns_yes_when_yes_score_is_highest() -> None:
    settings = Settings(model_version="test-version")

    result = format_prediction({"YES": 0.91, "NO": 0.09}, settings)

    assert result.predicted_answer == "Yes"
    assert result.confidence == 0.91
    assert result.scores == {"YES": 0.91, "NO": 0.09}
    assert result.needs_clarification is False
    assert result.model_version == "test-version"


def test_format_prediction_returns_no_when_no_score_is_highest() -> None:
    settings = Settings(model_version="test-version")

    result = format_prediction({"YES": 0.22, "NO": 0.78}, settings)

    assert result.predicted_answer == "No"
    assert result.confidence == 0.78
    assert result.scores == {"YES": 0.22, "NO": 0.78}
    assert result.needs_clarification is False
    assert result.model_version == "test-version"


def test_format_prediction_returns_unclear_below_threshold() -> None:
    settings = Settings(
        clarification_threshold=0.70,
        model_version="test-version",
    )

    result = format_prediction({"YES": 0.52, "NO": 0.48}, settings)

    assert result.predicted_answer == "Unclear"
    assert result.confidence == 0.52
    assert result.scores == {"YES": 0.52, "NO": 0.48}
    assert result.needs_clarification is True
    assert result.model_version == "test-version"
