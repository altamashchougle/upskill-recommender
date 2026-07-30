"""
Centralized Gemini Model Router for production-grade LLM orchestration.
Maintains model priority order, runtime health tracking, and automatic fallback switching.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)

GEMINI_MODEL_PRIORITY = [
    {
        "name": "gemini-2.5-flash",
        "priority": 1,
        "purpose": "primary production model"
    },
    {
        "name": "gemini-3-flash",
        "priority": 2,
        "purpose": "next-gen fast fallback"
    },
    {
        "name": "gemini-3.1-flash-lite",
        "priority": 3,
        "purpose": "lightweight secondary fallback"
    },
    {
        "name": "gemini-3.5-flash-lite",
        "priority": 4,
        "purpose": "low-cost emergency fallback"
    },
    {
        "name": "gemini-3.6-flash",
        "priority": 5,
        "purpose": "latest generation final fallback"
    }
]


class ModelRouter:
    """Manages Gemini model priority, health state, and automatic availability routing."""

    def __init__(self):
        # Runtime health tracker: {model_name: {"status": str, "retry_after": Optional[float], "failures": int}}
        # Status options: "healthy", "rate_limited", "quota_exceeded", "unavailable"
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.fallbacks_triggered = 0
        self.requests_today = 0
        self._verified_available_models: Optional[List[str]] = None
        self._last_verification_time: float = 0.0
        self._verification_ttl: float = 300.0  # 5 minutes verification cache

        # Initialize health tracker for all priority models
        for item in GEMINI_MODEL_PRIORITY:
            self.health_status[item["name"]] = {
                "status": "healthy",
                "retry_after": None,
                "failures": 0,
                "requests_served": 0,
                "last_error": None,
                "purpose": item["purpose"]
            }

    @property
    def active_model(self) -> Optional[str]:
        """Return the highest-priority healthy model currently available."""
        available = self.get_available_models()
        return available[0] if available else None

    def _verify_available_models(self, force: bool = False) -> List[str]:
        """Check which models from GEMINI_MODEL_PRIORITY actually exist and are available for the API key."""
        now = time.time()
        if not force and self._verified_available_models is not None and (now - self._last_verification_time) < self._verification_ttl:
            return self._verified_available_models

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            if self._verified_available_models is not None and len(self._verified_available_models) > 0:
                return self._verified_available_models
            logger.info("GEMINI_API_KEY not found or unset. Defaulting to priority models for offline/test routing.")
            self._verified_available_models = [item["name"] for item in GEMINI_MODEL_PRIORITY]
            self._last_verification_time = now
            return self._verified_available_models

        try:
            genai.configure(api_key=api_key)
            supported_models = []
            for m in genai.list_models():
                if "generateContent" in getattr(m, "supported_generation_methods", []):
                    # Normalize model name by removing 'models/' prefix if present
                    clean_name = m.name.replace("models/", "").strip()
                    supported_models.append(clean_name)

            verified = []
            for item in GEMINI_MODEL_PRIORITY:
                model_name = item["name"]
                if model_name in supported_models or f"models/{model_name}" in supported_models:
                    verified.append(model_name)
                else:
                    pass

            # If genai.list_models() returned models, use intersection. If list was unexpectedly empty despite key,
            # fall back to allowing all priority models to be tried dynamically.
            if verified:
                self._verified_available_models = verified
            else:
                self._verified_available_models = [item["name"] for item in GEMINI_MODEL_PRIORITY]

            self._last_verification_time = now
            logger.info(f"Verified available Gemini models: {self._verified_available_models}")
            return self._verified_available_models

        except Exception as e:
            logger.warning(f"Could not query genai.list_models() for verification ({e}). Assuming priority models available.")
            self._verified_available_models = [item["name"] for item in GEMINI_MODEL_PRIORITY]
            self._last_verification_time = now
            return self._verified_available_models

    def get_available_models(self) -> List[str]:
        """Return prioritized list of models that exist and are currently healthy/recovered."""
        verified_models = self._verify_available_models()
        now = time.time()
        available = []

        for item in GEMINI_MODEL_PRIORITY:
            model_name = item["name"]
            if model_name not in verified_models:
                continue

            health = self.health_status.get(model_name, {"status": "healthy", "retry_after": None})
            status = health.get("status", "healthy")
            retry_after = health.get("retry_after")

            if status == "healthy":
                available.append(model_name)
            elif retry_after and now >= retry_after:
                # Cooldown expired, recover model to healthy
                logger.info(f"Cooldown expired for model '{model_name}'. Resetting status to healthy.")
                health["status"] = "healthy"
                health["retry_after"] = None
                available.append(model_name)
            else:
                logger.debug(f"Skipping model '{model_name}' due to status '{status}' (cooldown until {retry_after})")

        return available

    def mark_rate_limited(self, model_name: str, retry_after_secs: float = 60.0):
        """Mark a model as temporarily rate-limited (`Case 1`)."""
        if model_name in self.health_status:
            self.health_status[model_name]["status"] = "rate_limited"
            self.health_status[model_name]["retry_after"] = time.time() + retry_after_secs
            self.health_status[model_name]["failures"] += 1
            self.health_status[model_name]["last_error"] = "429 Rate Limit Exceeded"
            self.fallbacks_triggered += 1
            logger.warning(f"Model '{model_name}' marked RATE_LIMITED. Cooldown: {retry_after_secs}s.")

    def mark_quota_exceeded(self, model_name: str, cooldown_secs: float = 3600.0):
        """Mark a model as quota exceeded / daily limit reached (`Case 2`)."""
        if model_name in self.health_status:
            self.health_status[model_name]["status"] = "quota_exceeded"
            self.health_status[model_name]["retry_after"] = time.time() + cooldown_secs
            self.health_status[model_name]["failures"] += 1
            self.health_status[model_name]["last_error"] = "Quota Exceeded / Free Tier Exhausted"
            self.fallbacks_triggered += 1
            logger.warning(f"Model '{model_name}' marked QUOTA_EXCEEDED. Cooldown: {cooldown_secs}s.")

    def mark_unavailable(self, model_name: str, cooldown_secs: float = 300.0, error_msg: str = "Unavailable"):
        """Mark a model as general error/unavailable."""
        if model_name in self.health_status:
            self.health_status[model_name]["status"] = "unavailable"
            self.health_status[model_name]["retry_after"] = time.time() + cooldown_secs
            self.health_status[model_name]["failures"] += 1
            self.health_status[model_name]["last_error"] = error_msg
            self.fallbacks_triggered += 1
            logger.warning(f"Model '{model_name}' marked UNAVAILABLE ({error_msg}). Cooldown: {cooldown_secs}s.")

    def mark_success(self, model_name: str):
        """Reset a model to healthy state upon successful generation."""
        if model_name in self.health_status:
            self.health_status[model_name]["status"] = "healthy"
            self.health_status[model_name]["retry_after"] = None
            self.health_status[model_name]["requests_served"] += 1
            self.requests_today += 1

    def get_model_health_summary(self) -> Dict[str, Any]:
        """Return runtime health status for all models."""
        summary = {
            "active_model": self.active_model,
            "total_fallbacks_triggered": self.fallbacks_triggered,
            "requests_today": self.requests_today,
            "models": {}
        }
        for item in GEMINI_MODEL_PRIORITY:
            name = item["name"]
            health = self.health_status.get(name, {})
            status_data = {
                "status": health.get("status", "healthy"),
                "priority": item.get("priority", 1),
                "purpose": item.get("purpose", ""),
                "requests_served": health.get("requests_served", 0),
                "failures": health.get("failures", 0),
                "last_error": health.get("last_error")
            }
            if health.get("retry_after"):
                status_data["retry_after"] = round(health["retry_after"], 2)
                status_data["cooldown_remaining"] = max(0.0, round(health["retry_after"] - time.time(), 2))
            summary[name] = status_data
            summary["models"][name] = status_data
        return summary


# Global singleton instance
model_router = ModelRouter()
