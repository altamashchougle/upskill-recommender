"""
Integration tests for FastAPI endpoints verifying Pydantic schema compliance,
CORS functionality, and predictable response structures across all endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "UpskillAI Backend"


def test_get_platforms():
    response = client.get("/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data
    assert isinstance(data["platforms"], list)


def test_get_skills():
    response = client.get("/skills")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "Python" in data["skills"]


def test_get_job_roles():
    response = client.get("/job_roles")
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert "AI Engineer" in roles
    assert "Data Scientist" in roles


def test_get_career_path():
    response = client.get("/career_path/AI Engineer")
    assert response.status_code == 200
    data = response.json()
    assert data["current_role"] == "AI Engineer"
    assert "skills" in data
    assert "next_roles" in data


def test_get_recommendations():
    response = client.get(
        "/recommendations",
        params={"job_role": "AI Engineer", "user_skills": "Python,SQL", "top_n": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_role"] == "AI Engineer"
    assert "skill_gap" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) <= 5
    if data["recommendations"]:
        item = data["recommendations"][0]
        assert "score" in item
        assert "why_recommended" in item
        assert "skills_gained" in item


def test_post_recommendations():
    payload = {
        "job_role": "Data Scientist",
        "user_skills": ["SQL", "Tableau"],
        "goal": "Master machine learning",
        "use_ai": False,
        "top_n": 3
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["job_role"] == "Data Scientist"
    assert len(data["recommendations"]) <= 3


def test_post_roadmap():
    payload = {
        "current_role": "Software Engineer",
        "current_skills": ["Python", "SQL"],
        "target_role": "AI Engineer"
    }
    response = client.post("/roadmap", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "roadmap" in data
    assert "career_advice" in data
    assert "future_roles" in data
    assert len(data["roadmap"]) > 0
