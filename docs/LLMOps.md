# LLMOps & Gemini Integration

UpskillAI integrates tightly with Google's Gemini API to enrich course recommendations and dynamically understand new career fields.

## Multi-Model Router
To balance speed and cost, the application uses a dynamic `ModelRouter`.
1.  **High Tier (gemini-3.1-pro / gemini-1.5-pro):** Used for complex career taxonomy parsing and exhaustive roadmap generation where deep reasoning is required.
2.  **Fast Tier (gemini-2.5-flash / gemini-1.5-flash):** Used for bulk enhancement tasks, like generating 1-2 sentence explanations for why a specific course fits a user's skill gap.

## Fallback System
The system is built to be resilient. If the Gemini API is rate-limited, times out, or the API key is missing:
*   The API client automatically catches the error.
*   The system gracefully falls back to the local TF-IDF engine.
*   Users will still receive highly accurate course recommendations, simply without the generative textual explanations attached.
