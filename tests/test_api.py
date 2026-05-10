from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "model_loaded": True,
        "model_version": "mock-0.1.0",
    }


def test_predict_yes_like_response() -> None:
    response = client.post(
        "/predict",
        json={
            "question": "Have you used drugs other than those required for medical reasons?",
            "response": "Yes, I have.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["predicted_answer"] == "Yes"
    assert body["confidence"] == 0.86
    assert body["scores"] == {"YES": 0.86, "NO": 0.14}
    assert body["needs_clarification"] is False
    assert body["model_version"] == "mock-0.1.0"


def test_predict_no_like_response() -> None:
    response = client.post(
        "/predict",
        json={
            "question": "Have you had medical problems as a result of your drug use?",
            "response": "No, never.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["predicted_answer"] == "No"
    assert body["confidence"] == 0.88
    assert body["scores"] == {"YES": 0.12, "NO": 0.88}
    assert body["needs_clarification"] is False
    assert body["model_version"] == "mock-0.1.0"


def test_predict_requires_question() -> None:
    response = client.post(
        "/predict",
        json={"response": "Yes, I have."},
    )

    assert response.status_code == 422


def test_predict_requires_response() -> None:
    response = client.post(
        "/predict",
        json={"question": "Have you used drugs?"},
    )

    assert response.status_code == 422


def test_predict_rejects_empty_question() -> None:
    response = client.post(
        "/predict",
        json={"question": "", "response": "Yes, I have."},
    )

    assert response.status_code == 422


def test_predict_rejects_empty_response() -> None:
    response = client.post(
        "/predict",
        json={"question": "Have you used drugs?", "response": ""},
    )

    assert response.status_code == 422

