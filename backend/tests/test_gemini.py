"""
Unit and mocked integration tests for Gemini LLM service.
Verifies JSON parsing, Pydantic schema compliance, robust error handling,
and deterministic rule-based fallbacks without calling live external APIs.
"""

import json
import pytest
from unittest.mock import MagicMock
from app.services import gemini
from app.models.schemas import PersonalizedRoadmapResponse


@pytest.fixture
def sample_roadmap_json_str():
    return json.dumps({
        "roadmap": [
            {
                "phase": "Phase 1: Foundation",
                "duration": "4 weeks",
                "skills_to_learn": ["Python", "SQL"],
                "recommended_actions": "Complete basic exercises."
            },
            {
                "phase": "Phase 2: Advanced",
                "duration": "6 weeks",
                "skills_to_learn": ["Machine Learning", "PyTorch"],
                "recommended_actions": "Build neural network models."
            },
            {
                "phase": "Phase 3: Portfolio",
                "duration": "4 weeks",
                "skills_to_learn": ["MLOps"],
                "recommended_actions": "Deploy capstone API."
            }
        ],
        "career_advice": "Focus on consistent hands-on coding and project execution.",
        "future_roles": ["AI Engineer", "ML Engineer", "Data Scientist"]
    })


@pytest.fixture
def mock_course():
    return {
        "title": "Machine Learning with PyTorch",
        "description": "Learn deep neural networks and PyTorch from scratch.",
        "subject": "Machine Learning",
        "level": "Intermediate",
        "skills_covered": ["Python", "PyTorch", "Deep Learning"]
    }


def test_parse_gemini_json_clean_and_fenced(sample_roadmap_json_str):
    # Fenced with ```json
    fenced = f"```json\n{sample_roadmap_json_str}\n```"
    parsed = gemini._parse_gemini_json(fenced)
    assert isinstance(parsed, dict)
    assert "roadmap" in parsed
    assert len(parsed["roadmap"]) == 3

    # Fenced with just ```
    fenced_simple = f"```\n{sample_roadmap_json_str}\n```"
    parsed_simple = gemini._parse_gemini_json(fenced_simple)
    assert parsed_simple["career_advice"] == "Focus on consistent hands-on coding and project execution."


def test_successful_roadmap_generation_mocked(monkeypatch, sample_roadmap_json_str):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = sample_roadmap_json_str
    mock_model.generate_content.return_value = mock_response

    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.generate_personalized_roadmap(
        current_role="Software Engineer",
        current_skills=["Python"],
        target_role="AI Engineer",
        skill_gaps=["PyTorch", "MLOps"],
        recommended_courses=["Machine Learning with PyTorch"]
    )

    # Verify Pydantic validation passes without error
    validated = PersonalizedRoadmapResponse.model_validate(result)
    assert len(validated.roadmap) == 3
    assert validated.roadmap[0].phase == "Phase 1: Foundation"
    assert "AI Engineer" in validated.future_roles
    mock_model.generate_content.assert_called_once()


def test_invalid_gemini_json_fallback(monkeypatch):
    """If Gemini returns malformed JSON, verify graceful fallback execution."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Here is your roadmap: {malformed json missing closing braces..."
    mock_model.generate_content.return_value = mock_response

    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.generate_personalized_roadmap(
        current_role="Data Analyst",
        current_skills=["SQL", "Excel"],
        target_role="Data Scientist",
        skill_gaps=["Python", "Machine Learning"],
        recommended_courses=["Data Science Bootcamp"]
    )

    validated = PersonalizedRoadmapResponse.model_validate(result)
    assert len(validated.roadmap) == 3
    assert validated.roadmap[0].phase == "Phase 1: Foundation & Core Gaps"
    assert "Python" in validated.roadmap[0].skills_to_learn
    assert "Machine Learning" in validated.roadmap[1].skills_to_learn


def test_gemini_json_missing_roadmap_key_fallback(monkeypatch):
    """Verify fallback if Gemini returns JSON but without 'roadmap' list key."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({"career_advice": "Good luck!"})
    mock_model.generate_content.return_value = mock_response
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.generate_personalized_roadmap(
        current_role="Student",
        current_skills=[],
        target_role="AI Engineer",
        skill_gaps=["PyTorch"],
        recommended_courses=[]
    )
    validated = PersonalizedRoadmapResponse.model_validate(result)
    assert len(validated.roadmap) == 3


def test_enhance_course_exception_fallback(monkeypatch, mock_course):
    """Verify enhance_course gracefully catches generate_content exceptions."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.enhance_course(mock_course.copy())
    assert result["ai_enhanced"] is False
    assert result["title"] == "Machine Learning with PyTorch"


def test_api_failure_exception_fallback(monkeypatch):
    """Simulate network timeout or rate limit exception raised by model.generate_content."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("429 ResourceExhausted: Rate limit exceeded")

    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.generate_personalized_roadmap(
        current_role="Beginner",
        current_skills=[],
        target_role="AI Engineer",
        skill_gaps=["Python", "PyTorch"],
        recommended_courses=[]
    )

    validated = PersonalizedRoadmapResponse.model_validate(result)
    assert validated.roadmap[0].phase == "Month 1: ML Engineering Fundamentals"
    assert "Python" in validated.roadmap[0].skills_to_learn


def test_missing_api_key_or_model_unset(monkeypatch, mock_course):
    """Verify all service functions behave deterministically when gemini_model is None."""
    monkeypatch.setattr("app.services.gemini.gemini_model", None)
    assert not gemini.is_gemini_available()

    # Roadmap fallback
    roadmap = gemini.generate_personalized_roadmap(
        current_role="Student",
        current_skills=["C++"],
        target_role="AI Engineer",
        skill_gaps=["Python", "Deep Learning"],
        recommended_courses=["Deep Learning Specialization"]
    )
    validated = PersonalizedRoadmapResponse.model_validate(roadmap)
    assert len(validated.roadmap) == 3

    # Course explanations fallback
    explained = gemini.enhance_course_explanations(
        course=mock_course.copy(),
        user_skills=["Python"],
        target_role="AI Engineer",
        skill_gaps=["PyTorch", "Deep Learning"]
    )
    assert explained["ai_why_fit"] is not None
    assert "Directly addresses" in explained["ai_gap_solved"]
    assert explained["ai_expected_outcome"] is not None

    # Enhance course offline
    enhanced = gemini.enhance_course(mock_course.copy())
    assert enhanced["title"] == "Machine Learning with PyTorch"

    # AI courses generator when offline
    courses = gemini.generate_ai_courses("AI Engineer", ["Python"])
    assert courses == []


def test_enhance_course_explanations_successful_mock(monkeypatch, mock_course):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "ai_why_fit": "Fits your Python background while teaching critical neural network skills.",
        "ai_gap_solved": "Solves gap in PyTorch framework mastery.",
        "ai_expected_outcome": "Build production neural network models independently."
    })
    mock_model.generate_content.return_value = mock_response

    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.enhance_course_explanations(
        course=mock_course.copy(),
        user_skills=["Python"],
        target_role="AI Engineer",
        skill_gaps=["PyTorch"]
    )
    assert result["ai_enhanced"] is True
    assert result["ai_why_fit"] == "Fits your Python background while teaching critical neural network skills."
    assert result["ai_gap_solved"] == "Solves gap in PyTorch framework mastery."


def test_enhance_course_explanations_exception_fallback(monkeypatch, mock_course):
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.enhance_course_explanations(
        course=mock_course.copy(),
        user_skills=["Python"],
        target_role="AI Engineer",
        skill_gaps=["PyTorch"]
    )
    # Should fall back to rule-based strings generated before API call
    assert "ai_why_fit" in result
    assert "ai_gap_solved" in result
    assert "ai_expected_outcome" in result


def test_enhance_course_mocked(monkeypatch, mock_course):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "ai_description": "Comprehensive deep learning course teaching PyTorch.",
        "ai_learning_outcomes": ["Master PyTorch tensors", "Build CNNs", "Deploy ML models"]
    })
    mock_model.generate_content.return_value = mock_response
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    result = gemini.enhance_course(mock_course.copy())
    assert result["ai_enhanced"] is True
    assert result["ai_description"] == "Comprehensive deep learning course teaching PyTorch."
    assert len(result["ai_learning_outcomes"]) == 3


def test_generate_ai_courses_mocked(monkeypatch):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "courses": [
            {
                "title": "AI Specialization",
                "provider": "Coursera",
                "url": "https://www.coursera.org",
                "is_paid": False,
                "price": 0.0,
                "num_subscribers": 10000,
                "level": "Intermediate",
                "duration": "4 weeks",
                "subject": "Machine Learning",
                "description": "Learn AI.",
                "popularity_score": 90.0,
                "platform": "coursera",
                "rating": 4.9,
                "university": "Stanford",
                "skills_covered": ["Python", "PyTorch"],
                "ai_enhanced": True
            }
        ]
    })
    mock_model.generate_content.return_value = mock_response
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    courses = gemini.generate_ai_courses("AI Engineer", ["Python"])
    assert len(courses) == 1
    assert courses[0]["title"] == "AI Specialization"


def test_generate_ai_courses_exception_fallback(monkeypatch):
    """Verify generate_ai_courses gracefully returns empty list on exception."""
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    monkeypatch.setattr("app.services.gemini.gemini_model", mock_model)

    courses = gemini.generate_ai_courses("AI Engineer", ["Python"])
    assert courses == []
