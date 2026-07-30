"""
Pydantic schemas for API request validation and response formatting.
Provides strong typing, documentation, and serialization guarantees across ML and Gemini AI workflows.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Course(BaseModel):
    """Standardized representation of a learning course across providers."""
    title: str
    provider: str
    url: str
    is_paid: bool
    price: float
    num_subscribers: int
    level: str
    duration: str
    subject: str
    description: str
    popularity_score: float
    platform: str
    rating: float
    university: Optional[str] = ""
    skills_covered: List[str] = Field(default_factory=list)
    ai_enhanced: Optional[bool] = False
    ai_description: Optional[str] = None
    ai_learning_outcomes: Optional[List[str]] = None
    ai_why_fit: Optional[str] = Field(None, description="AI explanation of why this course fits the user")
    ai_gap_solved: Optional[str] = Field(None, description="AI explanation of specific skill gap solved")
    ai_expected_outcome: Optional[str] = Field(None, description="AI explanation of expected competency outcome")


class RecommendationExplanation(BaseModel):
    """Explainable recommendation metadata for a single course."""
    score: float = Field(..., description="Hybrid recommendation score between 0 and 1")
    why_recommended: str = Field(..., description="Human-readable explanation of why this course was selected")
    skills_gained: List[str] = Field(..., description="Key skills taught by this course")
    skill_gap_addressed: List[str] = Field(..., description="Specific target career skills missing from user that this course teaches")
    ai_why_fit: Optional[str] = Field(None, description="AI explanation of why this course fits the user")
    ai_gap_solved: Optional[str] = Field(None, description="AI explanation of specific skill gap solved")
    ai_expected_outcome: Optional[str] = Field(None, description="AI explanation of expected competency outcome")
    ranking_explanation: Optional[dict] = Field(None, description="Detailed subscore breakdown for debugging and verification")


class RecommendationItem(Course, RecommendationExplanation):
    """Combined recommendation item containing full course metadata and explanation.
    Inherits top-level Course fields for backwards compatibility with existing UI,
    while also exposing explainability scores and skill gap mappings.
    """
    course: Optional[Course] = None  # Nested course object for structured consumption


class RecommendationRequest(BaseModel):
    """Request schema for course recommendations via POST endpoint."""
    job_role: str = Field(..., max_length=150, description="Target career job role")
    user_skills: List[str] = Field(default_factory=list, description="Current user skills")
    goal: Optional[str] = Field("", max_length=150, description="Specific learning goal or topic focus")
    use_ai: Optional[bool] = Field(False, description="Enable Gemini AI metadata and explanation enhancement")
    top_n: Optional[int] = Field(20, ge=1, le=50, description="Number of recommendations to return")


class CareerPathResponse(BaseModel):
    """Representation of a target career progression path."""
    current_role: str
    subjects: List[str]
    required_skills: List[str] = Field(alias="skills", default_factory=list)
    next_roles: List[str]
    confidence: Optional[str] = Field("high", description="Confidence level of role resolution (high, medium, low, none)")
    source: Optional[str] = Field("exact", description="Source of resolution (exact, alias, fuzzy, extracted, unresolved)")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Clarification suggestions if confidence is low")
    message: Optional[str] = Field("", description="Human-readable clarification or status message")

    model_config = {"populate_by_name": True}


class RecommendationResponse(BaseModel):
    """Response schema for course recommendation queries."""
    job_role: str
    user_skills: List[str]
    goal: str
    skill_gap: List[str] = Field(description="List of required career skills missing from user's current skillset")
    recommendations: List[RecommendationItem]
    ai_enhanced: bool
    confidence: Optional[str] = Field("high", description="Confidence level of role resolution (high, medium, low, none)")
    source: Optional[str] = Field("exact", description="Source of resolution (exact, alias, fuzzy, extracted, unresolved)")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="Clarification suggestions if confidence is low")
    message: Optional[str] = Field("", description="Human-readable clarification or status message")
    skill_coverage: Optional[str] = Field(None, description="Explainable metric showing skill coverage of recommendations")
    preparation_path: Optional[str] = Field(None, description="Recommended preparation path if direct domain courses are unavailable")


class AICoursesResponse(BaseModel):
    """Response schema for dynamic AI-generated course list."""
    courses: List[Course]


class RoadmapPhase(BaseModel):
    """A single phase in a structured personalized learning roadmap."""
    phase: str = Field(..., description="Name of the roadmap phase (e.g., 'Phase 1: Foundation')")
    duration: str = Field(..., description="Estimated duration of this phase (e.g., '4-6 weeks')")
    skills_to_learn: List[str] = Field(..., description="Skills focused on during this phase")
    recommended_actions: str = Field(..., description="Actionable study steps and projects for this phase")


class PersonalizedRoadmapResponse(BaseModel):
    """Complete personalized learning roadmap and career advice."""
    roadmap: List[RoadmapPhase]
    career_advice: str = Field(..., description="Strategic career guidance tailored to user's transition")
    future_roles: List[str] = Field(..., description="Potential future roles accessible after completing this roadmap")


class RoadmapRequest(BaseModel):
    """Request payload for generating a personalized learning roadmap."""
    current_role: str = Field("Beginner", max_length=150, description="User's current career role")
    current_skills: List[str] = Field(default_factory=list, description="User's current skills")
    target_role: str = Field(..., max_length=150, description="Target career job role")
    skill_gaps: Optional[List[str]] = Field(default_factory=list, description="Pre-computed missing skills")
    recommended_courses: Optional[List[str]] = Field(default_factory=list, description="Titles of top recommended courses")


class PlatformsResponse(BaseModel):
    """Response schema for available learning platforms."""
    platforms: List[str]


class SkillsResponse(BaseModel):
    """Response schema for available skills."""
    skills: List[str]
