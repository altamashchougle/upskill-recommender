# Caching System

To minimize latency and reduce Gemini API costs, UpskillAI implements a robust local caching system.

## Mechanisms
*   `gemini_cache.py`: A filesystem-backed cache that intercepts outgoing Gemini requests.
*   **Key Generation:** The cache generates a SHA-256 hash based on the exact prompt sent to the LLM.
*   **Storage:** Responses are stored as JSON files in `.cache/gemini/`.
*   **Operation:** Before calling the Gemini API, the system checks for a cache hit. If found, it immediately returns the JSON payload, reducing a 3-4 second network call to ~5 milliseconds.
*   **Safety:** The cache handles corrupted JSON files gracefully, automatically invalidating them and triggering a fresh network request if a file is unreadable.
