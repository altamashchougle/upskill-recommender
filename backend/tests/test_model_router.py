"""
Comprehensive test suite for Gemini Model Router (`model_router.py`),
Gemini Client (`gemini_client.py`), Request Budgeting, Caching, and Fallback Routing.
"""

import time
import pytest
from unittest.mock import MagicMock, patch
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
def clean_router():
    router = ModelRouter()
    # Force mock verification to return standard priority models
    router._verified_available_models = list(MODEL_CHAIN)
    router._last_verification_time = time.time()
    return router


@pytest.fixture
def clean_cache():
    cache = GeminiCache()
    cache.clear()
    return cache


@pytest.fixture
def client(clean_router, clean_cache):
    return GeminiClient(router=clean_router, cache=clean_cache)


def test_primary_model_succeeds(client, clean_router):
    """Test 1: Primary model succeeds -> Only primary called."""
    mock_response = MagicMock()
    mock_response.text = '{"status": "primary_success"}'

    with patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_instance

        result = client.execute("Hello Gemini", purpose="test_primary")

        assert result == '{"status": "primary_success"}'
        mock_model_cls.assert_called_once_with("gemini-2.5-flash")
        assert clean_router.health_status["gemini-2.5-flash"]["status"] == "healthy"
        assert clean_router.requests_today == 1


def test_primary_quota_failure_falls_back_to_secondary(client, clean_router):
    """Test 2: Primary quota failure -> Secondary model called."""
    mock_response_sec = MagicMock()
    mock_response_sec.text = '{"status": "secondary_success"}'

    def mock_gen_model(model_name):
        mock_instance = MagicMock()
        if model_name == "gemini-2.5-flash":
            mock_instance.generate_content.side_effect = Exception("429 Resource Exhausted / daily free tier quota exceeded")
        elif model_name == "gemini-3-flash":
            mock_instance.generate_content.return_value = mock_response_sec
        return mock_instance

    with patch("google.generativeai.GenerativeModel", side_effect=mock_gen_model) as mock_cls:
        result = client.execute("Hello Gemini", purpose="test_secondary")

        assert result == '{"status": "secondary_success"}'
        assert clean_router.health_status["gemini-2.5-flash"]["status"] == "quota_exceeded"
        assert clean_router.health_status["gemini-3-flash"]["status"] == "healthy"
        assert mock_cls.call_count == 2


def test_primary_and_secondary_failure_calls_third(client, clean_router):
    """Test 3: Primary and secondary failure -> Third model called."""
    mock_response_third = MagicMock()
    mock_response_third.text = '{"status": "third_success"}'

    def mock_gen_model(model_name):
        mock_instance = MagicMock()
        if model_name in ["gemini-2.5-flash", "gemini-3-flash"]:
            mock_instance.generate_content.side_effect = Exception("429 Resource Exhausted / daily free tier quota exceeded")
        elif model_name == "gemini-3.1-flash-lite":
            mock_instance.generate_content.return_value = mock_response_third
        return mock_instance

    with patch("google.generativeai.GenerativeModel", side_effect=mock_gen_model) as mock_cls:
        result = client.execute("Hello Gemini", purpose="test_third")

        assert result == '{"status": "third_success"}'
        assert clean_router.health_status["gemini-2.5-flash"]["status"] == "quota_exceeded"
        assert clean_router.health_status["gemini-3-flash"]["status"] == "quota_exceeded"
        assert clean_router.health_status["gemini-3.1-flash-lite"]["status"] == "healthy"
        assert mock_cls.call_count == 3


def test_all_models_fail_returns_none_for_deterministic_fallback(client, clean_router):
    """Test 4: All models fail -> Deterministic fallback triggered (execute returns None)."""
    with patch("google.generativeai.GenerativeModel") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("503 Service Unavailable")
        mock_cls.return_value = mock_instance

        result = client.execute("Hello Gemini", purpose="test_all_fail")

        assert result is None
        # Verify all models marked unavailable
        for model_name in MODEL_CHAIN:
            assert clean_router.health_status[model_name]["status"] == "unavailable"


def test_cache_hit_zero_gemini_calls(client, clean_cache):
    """Test 5: Cache hit -> Zero Gemini API calls made."""
    clean_cache.set("test_hash_key_123", '{"cached": "roadmap_data"}')

    with patch("google.generativeai.GenerativeModel") as mock_cls:
        result = client.execute("Hello Gemini", purpose="test_cache", cache_key="test_hash_key_123")

        assert result == '{"cached": "roadmap_data"}'
        assert mock_cls.call_count == 0  # Zero API calls!
        assert clean_cache.hits == 1


def test_rate_limit_cooldown_skips_unavailable_models(client, clean_router):
    """Test 6: Rate limit cooldown -> Unavailable models skipped."""
    clean_router.mark_rate_limited("gemini-2.5-flash", retry_after_secs=600.0)
    clean_router.mark_quota_exceeded("gemini-3-flash", cooldown_secs=3600.0)

    available = clean_router.get_available_models()
    assert "gemini-2.5-flash" not in available
    assert "gemini-3-flash" not in available
    assert available[0] == "gemini-3.1-flash-lite"


def test_maximum_request_budget_enforcement(client):
    """Test 7: Maximum request budget -> Never exceed 2 Gemini calls."""
    budget = RequestBudget(max_calls=2)
    mock_response = MagicMock()
    mock_response.text = '{"status": "ok"}'

    with patch("google.generativeai.GenerativeModel") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = mock_response
        mock_cls.return_value = mock_instance

        # Call 1 -> allowed
        res1 = client.execute("Prompt 1", purpose="call_1", budget=budget)
        assert res1 == '{"status": "ok"}'
        assert budget.calls_used == 1

        # Call 2 -> allowed
        res2 = client.execute("Prompt 2", purpose="call_2", budget=budget)
        assert res2 == '{"status": "ok"}'
        assert budget.calls_used == 2

        # Call 3 -> stopped immediately by budget check before any API attempt!
        res3 = client.execute("Prompt 3", purpose="call_3", budget=budget)
        assert res3 is None
        assert budget.calls_used == 2  # Still 2!
        assert mock_cls.call_count == 2  # API invoked exactly twice!
