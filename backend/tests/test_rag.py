
from unittest.mock import patch
from requests.exceptions import ConnectionError
from backend.rag import retrieve, ask_travel_question
from fastapi.testclient import TestClient
from backend.main import app


def test_retrieve_finds_travel_documents():
    """Check that retrieval finds relevant Chicago travel information."""
    chunks = retrieve(
        "What are some popular attractions in Chicago?",
        n_results=3
    )

    assert len(chunks) > 0
    assert "text" in chunks[0]
    assert "source" in chunks[0]
    assert "distance" in chunks[0]


def test_ask_travel_question_returns_answer_and_sources():
    """Check that a travel question returns an answer and its sources."""
    result = ask_travel_question(
        "What are some popular attractions in Chicago?"
    )

    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0
    assert isinstance(result["sources"], list)
    assert len(result["sources"]) > 0


def test_unrelated_question_uses_guardrail():
    """Check that an unrelated question receives the fallback answer."""
    result = ask_travel_question(
        "What is the capital of Japan?"
    )

    assert "enough relevant information" in result["answer"].lower()
    assert result["sources"] == []




def test_ask_handles_ollama_unavailable():
    """Check that /ask handles an Ollama connection failure gracefully."""
    client = TestClient(app)

    # Register a test user. If the user already exists, continue.
    client.post(
        "/auth/register",
        json={
            "username": "rag_failure_test_user",
            "email": "rag_failure_test_user@example.com",
            "password": "TestPassword123!",
        },
    )

    # Log in to obtain an access token.
    login_response = client.post(
        "/auth/token",
        data={
            "username": "rag_failure_test_user",
            "password": "TestPassword123!",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Simulate Ollama being unavailable.
    with patch(
        "backend.rag.requests.post",
        side_effect=ConnectionError("Ollama is unavailable"),
    ):
        response = client.post(
            "/ask",
            json={"question": "What can I visit in Chicago?"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert "temporarily unavailable" in response.json()["answer"].lower()
