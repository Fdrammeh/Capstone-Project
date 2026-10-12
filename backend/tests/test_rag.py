from backend.rag import retrieve, ask_travel_question


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

