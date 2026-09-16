"""
Pytest tests for the Sales Lead Qualifier API.

Design decision: the LLM call is mocked so tests pass with NO API key
and NO network. We patch app.llm.call_llm before the TestClient is created
so the mock is in place for all requests.
"""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Fixed analysis payload that the mock LLM will return
MOCK_ANALYSIS = {
    "lead_summary": "Test lead summary.",
    "relevant_products": [{"name": "Identity & SSO", "why": "Customer needs SSO."}],
    "customer_needs": ["Single sign-on", "Enterprise security"],
    "recommended_next_step": "Schedule a technical demo.",
    "follow_up_questions": [
        "How many users need SSO access?",
        "Which IdP are you currently using?",
        "What is your go-live timeline?",
    ],
    "lead_score": 75,
    "priority": "High",
    "score_rationale": "Strong enterprise fit with clear buying signals.",
}


@pytest.fixture(scope="module")
def client():
    """
    Create the TestClient with GROQ_API_KEY set so llm.py doesn't raise
    at import time, and with call_llm mocked so no real API call is made.
    """
    import os
    os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")

    with patch("app.llm.call_llm", return_value=MOCK_ANALYSIS):
        from app.main import app
        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------
def test_health_returns_200(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert isinstance(data["api_key_configured"], bool)


# ---------------------------------------------------------------------------
# 2. POST with too-short requirement returns 422
# ---------------------------------------------------------------------------
def test_create_lead_short_requirement_returns_422(client):
    res = client.post(
        "/api/leads",
        json={
            "company_name": "Acme Corp",
            "contact_email": "test@acme.com",
            "requirement_text": "hi",  # only 2 chars, min is 20
        },
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 3. POST with valid input persists a row and returns expected keys
# ---------------------------------------------------------------------------
def test_create_lead_valid_persists_and_returns_keys(client):
    with patch("app.llm.call_llm", return_value=MOCK_ANALYSIS):
        res = client.post(
            "/api/leads",
            json={
                "company_name": "Globex Industries",
                "contact_email": "hank@globex.com",
                "requirement_text": (
                    "We need enterprise single sign-on for 500 employees "
                    "across 10 internal tools. Budget approved, Q1 rollout."
                ),
            },
        )
    assert res.status_code == 201
    data = res.json()

    # Check all expected top-level keys are present
    for key in ("id", "company_name", "contact_email", "requirement_text",
                 "retrieved_context", "ai_analysis", "lead_score", "priority",
                 "status", "created_at"):
        assert key in data, f"Missing key: {key}"

    assert data["company_name"] == "Globex Industries"
    assert data["lead_score"] == 75
    assert data["priority"] == "High"
    assert isinstance(data["retrieved_context"], list)
    assert isinstance(data["ai_analysis"], dict)


# ---------------------------------------------------------------------------
# 4. Retrieval returns entries ordered by descending score for SSO query
# ---------------------------------------------------------------------------
def test_retrieval_sso_query_ordered_by_score():
    from app.retrieval import search
    results = search("we need single sign-on for our enterprise customers", k=3)
    assert len(results) >= 1

    # Results must be ordered descending by relevance_score
    scores = [r["relevance_score"] for r in results]
    assert scores == sorted(scores, reverse=True), "Results not sorted descending"

    # The Identity & SSO product must be the top result for this query
    assert results[0]["name"] == "Identity & SSO", (
        f"Expected 'Identity & SSO' as top hit, got '{results[0]['name']}'"
    )


# ---------------------------------------------------------------------------
# 5. GET /api/leads/9999 returns 404
# ---------------------------------------------------------------------------
def test_get_nonexistent_lead_returns_404(client):
    res = client.get("/api/leads/9999")
    assert res.status_code == 404
