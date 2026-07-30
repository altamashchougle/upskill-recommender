# Backend Architecture

UpskillAI's backend is built with **FastAPI** to ensure high-performance, asynchronous API delivery.

## Core Structure
*   `api/`: Contains FastAPI route definitions (`routes.py`).
*   `services/`: Core business logic orchestration (`recommender.py`, `gemini.py`).
*   `ml/`: The TF-IDF vectorizer and cosine similarity scoring system (`scoring.py`, `vectorizer.py`).
*   `taxonomy/`: The exhaustive career knowledge graph (`taxonomy.py`, `career_understanding.py`).
*   `models/`: Pydantic validation schemas (`schemas.py`).
*   `cache/`: Local filesystem cache for Gemini LLM responses (`gemini_cache.py`).
*   `data/`: Initial dataset loaders (`loader.py`).

## Key Design Principles
1.  **Fail-Safe ML:** If the Gemini API fails or rate limits, the backend seamlessly falls back to the local TF-IDF engine.
2.  **Stateless API:** The backend handles no sessions; all state is driven by the client, allowing for easy horizontal scaling.
3.  **Strict Taxonomy:** User inputs are aggressively cleaned, normalized, and mapped to a known internal taxonomy before processing.
