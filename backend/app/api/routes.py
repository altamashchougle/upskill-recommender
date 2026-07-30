"""
FastAPI route handlers for Upskill Recommender.
Connects HTTP endpoints to the underlying RecommenderService and Pydantic schemas.
Ensures predictable request validation and response schemas across all endpoints.
"""

from fastapi import APIRouter, Query, HTTPException, Body, Path
from typing import List, Optional
import logging

from app.models.schemas import (
    PlatformsResponse,
    SkillsResponse,
    CareerPathResponse,
    RecommendationResponse,
    RecommendationRequest,
    PersonalizedRoadmapResponse,
    RoadmapRequest,
    AICoursesResponse
)
from app.services.recommender import recommender_service
from app.services.gemini import is_gemini_available
from app.services.model_router import model_router
from app.data.taxonomy import resolve_role_details
from app.data.career_understanding import CareerRoleResolutionError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def root_check():
    return {"message": "Upskill Recommender API"}

@router.get("/health")
def health_check():
    """API health status endpoint."""
    return {
        "status": "healthy",
        "service": "UpskillAI Backend"
    }


@router.get("/ai_status")
@router.get("/api/v1/ai/status")
def get_ai_status():
    """Diagnostic endpoint exposing current Gemini model router state, health statuses, usage, and fallbacks."""
    health_summary = model_router.get_model_health_summary()
    available = model_router.get_available_models()

    # Determine last_error across all models (most recent non-None)
    last_error = None
    for model_data in health_summary.get("models", {}).values():
        if model_data.get("last_error"):
            last_error = model_data["last_error"]

    return {
        "status": "online" if is_gemini_available() else "offline",
        "gemini_configured": is_gemini_available(),
        "active_model": health_summary.get("active_model"),
        "available_models": available,
        "requests_today": health_summary.get("requests_today", 0),
        "fallback_count": health_summary.get("total_fallbacks_triggered", 0),
        "last_error": last_error,
        "router_state": health_summary
    }


@router.get("/platforms", response_model=PlatformsResponse)
def get_platforms():
    """Retrieve distinct learning platforms available in catalog."""
    return {"platforms": recommender_service.get_platforms()}


@router.get("/skills", response_model=SkillsResponse)
def get_skills():
    """Retrieve standardized skills list."""
    return {"skills": recommender_service.get_skills()}


@router.get("/job_roles", response_model=List[str])
def get_job_roles():
    """Retrieve standardized job roles taxonomy."""
    return recommender_service.get_job_roles()


@router.get("/career_path/{job_role}", response_model=CareerPathResponse)
def get_career_path(job_role: str = Path(..., max_length=150, description="Target career job role")):
    """Retrieve required skills, domain subjects, and career progression for a target role."""
    try:
        # The service keeps its non-HTTP fallback metadata for internal callers;
        # the public endpoint explicitly rejects invalid career inputs.
        from app.services.recommender import _require_resolved_role
        _require_resolved_role(job_role)
        return recommender_service.get_career_path(job_role)
    except CareerRoleResolutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)



@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    job_role: str = Query(..., max_length=150, description="Target career job role"),
    user_skills: Optional[str] = Query("", description="Comma-separated current user skills"),
    goal: Optional[str] = Query("", max_length=150, description="Specific learning goal or topic focus"),
    use_ai: Optional[bool] = Query(False, description="Enable Gemini AI metadata and explanation enhancement"),
    top_n: Optional[int] = Query(20, ge=1, le=50, description="Number of recommendations to return")
):
    """Retrieve explainable hybrid course recommendations ranked by skill gap reduction and domain alignment."""
    try:
        skills_list = [s.strip() for s in user_skills.split(",") if s.strip()] if user_skills else []
        recommendations, skill_gap, skill_coverage, preparation_path = recommender_service.get_recommendations(
            job_role=job_role,
            user_skills=skills_list,
            goal=goal or "",
            use_ai=use_ai,
            top_n=top_n
        )
        details = resolve_role_details(goal or job_role)
        return {
            "job_role": job_role,
            "user_skills": skills_list,
            "goal": goal or "",
            "skill_gap": skill_gap,
            "recommendations": recommendations,
            "ai_enhanced": use_ai and is_gemini_available(),
            "confidence": details.get("confidence", "high"),
            "source": details.get("source", "exact"),
            "suggestions": details.get("suggestions", []),
            "message": details.get("message", ""),
            "skill_coverage": skill_coverage,
            "preparation_path": preparation_path
        }
    except CareerRoleResolutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as e:
        logger.error(f"Error computing recommendations for role '{job_role}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations.")


@router.post("/recommendations", response_model=RecommendationResponse)
def post_recommendations(request: RecommendationRequest = Body(...)):
    """Retrieve explainable hybrid course recommendations using structured POST payload."""
    try:
        recommendations, skill_gap, skill_coverage, preparation_path = recommender_service.get_recommendations(
            job_role=request.job_role,
            user_skills=request.user_skills,
            goal=request.goal or "",
            use_ai=request.use_ai,
            top_n=request.top_n
        )
        details = resolve_role_details(request.goal or request.job_role)
        return {
            "job_role": request.job_role,
            "user_skills": request.user_skills,
            "goal": request.goal or "",
            "skill_gap": skill_gap,
            "recommendations": recommendations,
            "ai_enhanced": request.use_ai and is_gemini_available(),
            "confidence": details.get("confidence", "high"),
            "source": details.get("source", "exact"),
            "suggestions": details.get("suggestions", []),
            "message": details.get("message", ""),
            "skill_coverage": skill_coverage,
            "preparation_path": preparation_path
        }
    except CareerRoleResolutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as e:
        logger.error(f"Error computing POST recommendations for role '{request.job_role}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations.")


@router.post("/roadmap", response_model=PersonalizedRoadmapResponse)
def create_roadmap_post(request: RoadmapRequest = Body(...)):
    """Generate a structured, phased personalized learning roadmap given user skills and target role."""
    try:
        roadmap_data = recommender_service.get_roadmap(
            current_role=request.current_role,
            current_skills=request.current_skills,
            target_role=request.target_role,
            skill_gaps=request.skill_gaps,
            recommended_courses=request.recommended_courses
        )
        return roadmap_data
    except CareerRoleResolutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as e:
        logger.error(f"Failed to generate roadmap: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not generate personalized roadmap.")


@router.get("/roadmap", response_model=PersonalizedRoadmapResponse)
def create_roadmap_get(
    current_role: str = Query("Beginner", max_length=150, description="Current career role"),
    target_role: str = Query(..., max_length=150, description="Target career job role"),
    user_skills: Optional[str] = Query("", description="Comma-separated current user skills")
):
    """Generate a structured, phased personalized learning roadmap (GET convenience endpoint)."""
    try:
        skills_list = [s.strip() for s in user_skills.split(",") if s.strip()] if user_skills else []
        roadmap_data = recommender_service.get_roadmap(
            current_role=current_role,
            current_skills=skills_list,
            target_role=target_role
        )
        return roadmap_data
    except CareerRoleResolutionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except Exception as e:
        logger.error(f"Failed to generate roadmap (GET): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not generate personalized roadmap.")


@router.get("/ai_courses", response_model=AICoursesResponse)
def get_ai_courses(
    job_role: str = Query(..., max_length=150, description="Target job role"),
    skills: Optional[str] = Query("", description="Current user skills")
):
    """Generate dynamic course suggestions using Gemini LLM directly."""
    if not is_gemini_available():
        raise HTTPException(status_code=503, detail="Gemini AI is not configured or unavailable.")

    skills_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else []
    courses = recommender_service.get_ai_courses(job_role, skills_list)
    return {"courses": courses}
