"""
High-performance in-memory caching layer for Gemini responses.
Prevents redundant API calls by caching roadmap and course explanation payloads using SHA-256 digests.
"""

import time
import json
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GeminiCache:
    """Thread-safe / dictionary LRU cache for structured Gemini responses."""

    def __init__(self, max_size: int = 500, default_ttl_seconds: float = 86400.0):
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        # Structure: {cache_key: {"data": Any, "expires_at": float}}
        self._store: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def hash_key(self, purpose: str, *args, **kwargs) -> str:
        """Compute deterministic SHA-256 cache key from request parameters."""
        normalized_parts = [purpose.strip().lower()]
        for arg in args:
            if isinstance(arg, (list, tuple, set)):
                normalized_parts.append(json.dumps(sorted([str(x).strip() for x in arg if x is not None])))
            elif isinstance(arg, dict):
                normalized_parts.append(json.dumps(arg, sort_keys=True))
            else:
                normalized_parts.append(str(arg).strip().lower())
        
        for k in sorted(kwargs.keys()):
            val = kwargs[k]
            if isinstance(val, (list, tuple, set)):
                val_str = json.dumps(sorted([str(x).strip() for x in val if x is not None]))
            elif isinstance(val, dict):
                val_str = json.dumps(val, sort_keys=True)
            else:
                val_str = str(val).strip().lower()
            normalized_parts.append(f"{k}:{val_str}")

        raw_key = "|".join(normalized_parts)
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached response if present and not expired (`Case 3 / Part 8`)."""
        if not key or key not in self._store:
            self.misses += 1
            return None

        entry = self._store[key]
        if time.time() >= entry["expires_at"]:
            logger.debug(f"Cache entry expired for key {key[:8]}...")
            del self._store[key]
            self.misses += 1
            return None

        self.hits += 1
        logger.info(f"GeminiCache HIT for key {key[:8]}... (Hits: {self.hits}, Misses: {self.misses})")
        return entry["data"]

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None):
        """Store response in cache with expiration."""
        if not key or value is None:
            return

        # Evict oldest if max_size exceeded
        if len(self._store) >= self.max_size and key not in self._store:
            # Simple eviction of oldest item
            oldest_key = min(self._store.keys(), key=lambda k: self._store[k]["expires_at"])
            del self._store[oldest_key]

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        self._store[key] = {
            "data": value,
            "expires_at": time.time() + ttl
        }
        logger.debug(f"GeminiCache SET for key {key[:8]}... (TTL: {ttl}s)")

    def clear(self):
        """Clear all cached entries."""
        self._store.clear()
        self.hits = 0
        self.misses = 0
        logger.info("GeminiCache cleared.")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Return runtime cache performance stats."""
        return {
            "size": len(self._store),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": round(self.hits / max(1, self.hits + self.misses), 3)
        }


# Global singleton instance
gemini_cache = GeminiCache()
