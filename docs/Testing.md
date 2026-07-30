# Testing Strategy

UpskillAI implements a comprehensive testing suite ensuring both deterministic logic and non-deterministic LLM behavior remain stable.

## Backend Tests (`pytest`)
*   **Unit Tests:** Validate taxonomy lookups, string normalization, and hybrid ML scoring logic.
*   **Integration Tests:** Validate FastAPI endpoint responses and error handling.
*   **Adversarial LLM Tests:** A unique suite (`test_adversarial.py`) that strictly tests the resilience of the Gemini parsers against edge cases, hallucinations, and invalid JSON structures.

## Running Tests
Navigate to the backend directory and run:
```bash
poetry run pytest
```
