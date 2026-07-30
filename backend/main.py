"""
Root entry point for Uvicorn server (`uvicorn main:app --reload`).
Delegates to modular architecture inside `app/main.py`.
"""

from app.main import app
from app.services.recommender import recommender_service
from app.services.gemini import enhance_course, generate_ai_courses, is_gemini_available

# For backwards compatibility if imported directly by test runner or external tools
__all__ = ["app", "recommender_service"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)