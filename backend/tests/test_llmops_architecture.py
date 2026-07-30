"""
Comprehensive test suite for Gemini LLMOps Architecture.
Tests:
1. Diagnostic endpoints (`GET /ai_status` and `GET /api/v1/ai/status`) exposing structured router health.
2. Terminal API key error aborting the priority model loop without burning retries across every model.
3. Stateful cooldown state tracking across requests (`429` rate limit cooldown defaults to 60s).
4. Strict enforcement of request budget (`RequestBudget` capped at 2 calls).
5. /ai_status returns active_model, requests_today, fallback_count, and last_error.
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.model_router import ModelRouter
from app.services.gemini_cache import GeminiCache
from app.services.gemini_client import GeminiClient, RequestBudget

# Current model priority chain
MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash"
]


@pytest.fixture
def client_app():
    return TestClient(app)


@pytest.fixture
def clean_router():
    router = ModelRouter()
    router._verified_available_models = list(MODEL_CHAIN)
    router._last_verification_time = time.time()
    return router


@pytest.fixture
def clean_cache():
    cache = GeminiCache()
    cache.clear()
    return cache


@pytest.fixture
def gemini_svc(clean_router, clean_cache):
    return GeminiClient(router=clean_router, cache=clean_cache)


def test_ai_status_diagnostic_endpoints(client_app):
    """Verify both /ai_status and /api/v1/ai/status endpoints return structured health diagnostics."""
    for endpoint in ["/ai_status", "/api/v1/ai/status"]:
        response = client_app.get(endpoint)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "gemini_configured" in data
        assert "active_model" in data
        assert "available_models" in data
        assert "requests_today" in data
        assert "fallback_count" in data
        assert "last_error" in data
        assert "router_state" in data

        router_state = data["router_state"]
        assert "active_model" in router_state
        assert "total_fallbacks_triggered" in router_state
        assert "requests_today" in router_state
        assert "models" in router_state
        # Check that the primary model is tracked inside models dictionary
        assert "gemini-2.5-flash" in router_state["models"]
        assert router_state["models"]["gemini-2.5-flash"]["priority"] == 1


def test_terminal_api_key_error_aborts_loop_immediately(gemini_svc, clean_router):
    """Verify that a terminal API key error breaks the fallback loop after attempt 1 instead of trying all 5 models."""
    def mock_gen_model(model_name):
        mock_instance = MagicMock()
        # Simulate Google API returning invalid API key / permission denied
        mock_instance.generate_content.side_effect = Exception("403 PermissionDenied: API key not valid. Please pass a valid API key.")
        return mock_instance

    with patch("google.generativeai.GenerativeModel", side_effect=mock_gen_model) as mock_cls:
        result = gemini_svc.execute("Test prompt", purpose="test_terminal")

        # Must return None for deterministic offline fallback
        assert result is None
        # Must only call GenerativeModel ONCE (on gemini-2.5-flash) before aborting immediately
        assert mock_cls.call_count == 1
        assert clean_router.health_status["gemini-2.5-flash"]["status"] == "unavailable"
        assert clean_router.health_status["gemini-2.5-flash"]["last_error"] == "Invalid API Key or Permission Denied"
        # The remaining models must NOT have been called or marked unavailable
        assert clean_router.health_status["gemini-3-flash"]["status"] == "healthy"
        assert clean_router.health_status["gemini-3.1-flash-lite"]["status"] == "healthy"


def test_stateful_cooldown_for_rate_limits(gemini_svc, clean_router):
    """Verify that a 429 rate limit sets a 60-second cooldown and skips the degraded model on subsequent calls."""
    mock_success = MagicMock()
    mock_success.text = '{"status": "fallback_success"}'

    def mock_gen_model(model_name):
        mock_instance = MagicMock()
        if model_name == "gemini-2.5-flash":
            mock_instance.generate_content.side_effect = Exception("429 ResourceExhausted: Rate limit exceeded")
        else:
            mock_instance.generate_content.return_value = mock_success
        return mock_instance

    with patch("google.generativeai.GenerativeModel", side_effect=mock_gen_model):
        # First request hits rate limit on primary, fails over to secondary
        res1 = gemini_svc.execute("Prompt 1", purpose="test_burst_1")
        assert res1 == '{"status": "fallback_success"}'
        assert clean_router.health_status["gemini-2.5-flash"]["status"] == "rate_limited"
        assert clean_router.health_status["gemini-2.5-flash"]["last_error"] == "429 Rate Limit Exceeded"
        assert clean_router.fallbacks_triggered == 1

        # Second request must skip gemini-2.5-flash immediately because of stateful cooldown
        available = clean_router.get_available_models()
        assert "gemini-2.5-flash" not in available
        assert available[0] == "gemini-3-flash"


def test_request_budget_enforcement():
    """Verify RequestBudget caps execution at max 2 calls per request."""
    budget = RequestBudget(max_calls=2)
    assert budget.can_call() is True
    budget.record_call("gemini-2.5-flash")
    assert budget.can_call() is True
    budget.record_call("gemini-3-flash")
    assert budget.can_call() is False
    assert budget.to_dict()["gemini_calls_used"] == 2


def test_active_model_tracks_highest_priority_healthy():
    """Verify active_model property returns the highest-priority healthy model."""
    router = ModelRouter()
    router._verified_available_models = list(MODEL_CHAIN)
    router._last_verification_time = time.time()

    # Initially, primary model is active
    assert router.active_model == "gemini-2.5-flash"

    # Mark primary as quota exceeded
    router.mark_quota_exceeded("gemini-2.5-flash")
    assert router.active_model == "gemini-3-flash"

    # Mark secondary as rate limited too
    router.mark_rate_limited("gemini-3-flash")
    assert router.active_model == "gemini-3.1-flash-lite"
