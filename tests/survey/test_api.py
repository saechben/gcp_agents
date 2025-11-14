from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from agents.survey.api.main import app, get_follow_up_agent
from agents.survey.core import FollowUpRecommendation


class _DummyFollowUpAgent:
    def __init__(self, *, result: FollowUpRecommendation | None = None, error: Exception | None = None) -> None:
        self._result = result or FollowUpRecommendation(should_ask=True, follow_up_question="Tell me more.")
        self._error = error

    def decide(self, question: str, response: str) -> FollowUpRecommendation:
        if self._error:
            raise self._error
        return self._result


@pytest.fixture()
def client() -> Iterator[TestClient]:
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_followup_endpoint_returns_recommendation(client: TestClient) -> None:
    recommendation = FollowUpRecommendation(should_ask=True, follow_up_question="Why do you feel that way?")
    app.dependency_overrides[get_follow_up_agent] = lambda: _DummyFollowUpAgent(result=recommendation)

    response = client.post(
        "/surveys/followups/decide",
        json={"question": "Q1", "response": "Because I like it"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {"should_ask": True, "follow_up_question": "Why do you feel that way?"}


def test_followup_endpoint_returns_empty_question_when_not_needed(client: TestClient) -> None:
    # Even if the underlying model returns stray text, the validator enforces an empty string when should_ask is false.
    recommendation = FollowUpRecommendation(should_ask=False, follow_up_question="  ignore me  ")
    app.dependency_overrides[get_follow_up_agent] = lambda: _DummyFollowUpAgent(result=recommendation)

    response = client.post(
        "/surveys/followups/decide",
        json={"question": "Q1", "response": "No comment"},
    )

    assert response.status_code == 200
    assert response.json() == {"should_ask": False, "follow_up_question": ""}


def test_followup_endpoint_propagates_agent_validation(client: TestClient) -> None:
    error_agent = _DummyFollowUpAgent(error=ValueError("Both question and response must be provided."))
    app.dependency_overrides[get_follow_up_agent] = lambda: error_agent

    response = client.post(
        "/surveys/followups/decide",
        json={"question": "Q1", "response": "Because"},
    )

    assert response.status_code == 400
    assert "must be provided" in response.json()["detail"]
