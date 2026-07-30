"""
Resilient Gemini API Client handling model execution, request budgeting,
exponential backoff retries (`Case 1`), daily quota exhaustion (`Case 2`), and fallback switching (`Case 3`).
"""

import time
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.services.model_router import model_router, ModelRouter
from app.services.gemini_cache import gemini_cache, GeminiCache

logger = logging.getLogger(__name__)


class RequestBudget:
    """Tracks and caps Gemini API consumption during a single user request (`Part 9`)."""

    def __init__(self, max_calls: int = 2):
        self.max_calls = max_calls
        self.calls_used = 0
        self.models_used: List[str] = []

    def can_call(self) -> bool:
        return self.calls_used < self.max_calls

    def record_call(self, model_name: str):
        self.calls_used += 1
        if model_name not in self.models_used:
            self.models_used.append(model_name)
        logger.info(f"RequestBudget updated: {self.calls_used}/{self.max_calls} calls used. Models: {self.models_used}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gemini_calls_used": self.calls_used,
            "models_used": self.models_used
        }


class GeminiClient:
    """Orchestrates Google Gemini API communication with retry and priority fallback."""

    def __init__(self, router: ModelRouter = model_router, cache: GeminiCache = gemini_cache):
        self.router = router
        self.cache = cache

    def execute(
        self,
        prompt: str,
        purpose: str = "generation",
        cache_key: Optional[str] = None,
        budget: Optional[RequestBudget] = None
    ) -> Optional[str]:
        """Execute prompt against Gemini priority models with budget control, caching, and retries."""
        # Check cache first (`Part 8 / Case 3`)
        if cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Returning cached Gemini result for purpose '{purpose}' (0 API calls used)")
                return cached_result

        # Check request budget (`Part 9`)
        if budget is not None and not budget.can_call():
            logger.warning(
                f"Request budget limit reached ({budget.calls_used}/{budget.max_calls} calls). "
                f"Skipping live Gemini call for purpose '{purpose}' and using deterministic fallback."
            )
            return None

        available_models = self.router.get_available_models()
        if not available_models:
            logger.warning("No healthy Gemini models available. Attempting final cache lookup or fallback.")
            if cache_key:
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            return None

        total_models = len(available_models)
        for attempt_idx, model_name in enumerate(available_models, start=1):
            logger.info(
                f"\nGEMINI REQUEST START\n"
                f"Attempt: {attempt_idx}/{total_models}\n"
                f"Model: {model_name}\n"
                f"Purpose: {purpose}"
            )

            try:
                # Initialize generative model instance
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                response_text = getattr(response, "text", "") or ""
                if not response_text.strip():
                    raise ValueError("Gemini returned empty response text.")

                # Mark success and record usage
                self.router.mark_success(model_name)
                if budget is not None:
                    budget.record_call(model_name)
                if cache_key:
                    self.cache.set(cache_key, response_text)

                logger.info(
                    f"\nSUCCESS\n"
                    f"Final model: {model_name}\n"
                    f"Total Gemini calls: {budget.calls_used if budget else 1}"
                )
                return response_text

            except Exception as e:
                err_str = str(e).lower()
                is_rate_limit = "429" in err_str or "rate limit" in err_str or "resource_exhausted" in err_str
                is_free_tier_exhausted = "free_tier_requests" in err_str or "daily" in err_str or "quota" in err_str
                is_terminal_key_error = (
                    "api key not valid" in err_str
                    or "permission_denied" in err_str
                    or "invalid_argument: api key" in err_str
                    or "403 permission denied" in err_str
                    or "check your api key" in err_str
                )

                next_model = available_models[attempt_idx] if attempt_idx < total_models else "deterministic fallback"

                # Case 1: Temporary rate limit (retry with exponential backoff before failing over)
                if is_rate_limit and not is_free_tier_exhausted and not is_terminal_key_error:
                    logger.warning(f"Temporary rate limit (429) hit on '{model_name}'. Executing 5-second exponential backoff retry...")
                    time.sleep(5.0)
                    try:
                        response = model.generate_content(prompt)
                        response_text = getattr(response, "text", "") or ""
                        if response_text.strip():
                            self.router.mark_success(model_name)
                            if budget is not None:
                                budget.record_call(model_name)
                            if cache_key:
                                self.cache.set(cache_key, response_text)
                            logger.info(f"\nSUCCESS (After Retry)\nFinal model: {model_name}")
                            return response_text
                    except Exception as retry_err:
                        logger.warning(f"Retry failed on '{model_name}': {retry_err}")

                # Case 2: Terminal API key error -> abort model loop immediately
                if is_terminal_key_error:
                    self.router.mark_unavailable(model_name, cooldown_secs=3600.0, error_msg="Invalid API Key or Permission Denied")
                    logger.warning(f"Terminal API key error detected (`{e}`). Aborting model priority loop immediately without further model retries.")
                    break

                # Case 3: Daily quota exhausted or retry failed -> mark model health status and switch
                if is_free_tier_exhausted:
                    self.router.mark_quota_exceeded(model_name, cooldown_secs=3600.0)
                elif is_rate_limit:
                    self.router.mark_rate_limited(model_name, retry_after_secs=60.0)
                else:
                    self.router.mark_unavailable(model_name, cooldown_secs=300.0, error_msg=str(e)[:150])

                logger.warning(
                    f"\nResult: FAILED\n"
                    f"Reason: {e}\n"
                    f"Switching to: {next_model}"
                )

        # Case 3: All Gemini models exhausted -> check cache again or return None for deterministic fallback
        logger.warning("All prioritized Gemini models failed or quota exhausted. Checking cache for emergency hit.")
        if cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.info("Emergency cache hit successful. Using cached result.")
                return cached_result

        logger.info("Using deterministic rule-based fallback (0 API calls).")
        return None


# Global singleton instance
gemini_client = GeminiClient()
