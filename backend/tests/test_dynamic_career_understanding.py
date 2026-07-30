"""Tests for persisted expansion roles and Gemini-only emerging-role parsing."""

import json

import pytest
from fastapi.testclient import TestClient

from app.api.routes import router
from app.data import career_understanding
from app.data.career_expansion import RoleExpansionRepository
from app.data.career_understanding import CareerUnderstandingService
from app.data.taxonomy import get_target_skills, resolve_role_details
from app.main import app
from app.ml.scoring import compute_skill_gap
import app.services.recommender as recommender_module


@pytest.fixture
def isolated_role_store(tmp_path, monkeypatch):
    database_path = tmp_path / "role-expansions.sqlite3"
    repository = RoleExpansionRepository(str(database_path))
    service = CareerUnderstandingService(repository)
    monkeypatch.setattr(career_understanding, "career_understanding_service", service)
    monkeypatch.setattr(recommender_module, "career_understanding_service", service)
    return repository, service, database_path


def test_known_role_stays_verified_without_parser(monkeypatch, isolated_role_store):
    _, service, _ = isolated_role_store
    monkeypatch.setattr(service, "parse_and_cache", lambda _: pytest.fail("known roles must not call Gemini"))

    details = resolve_role_details("AI Engineer")

    assert details["role"] == "AI Engineer"
    assert details["confidence"] == "high"
    assert details["source"] == "Verified Career Path"


def test_seeded_expansion_role_has_medium_confidence_and_priorities(isolated_role_store):
    repository, _, _ = isolated_role_store

    details = resolve_role_details("AI Agent Engineer")
    profile = repository.get_by_input("AI Agent Engineer")

    assert details["role"] == "AI Agent Engineer"
    assert details["confidence"] == "medium"
    assert details["source"] == "expansion"
    assert profile["skill_priorities"]["Python"] == "critical"
    assert "LLMs" in get_target_skills("AI Agent Engineer")


def test_emerging_role_is_parsed_persisted_and_reused(monkeypatch, isolated_role_store):
    _, service, database_path = isolated_role_store
    parser_response = {
        "valid_role": True,
        "canonical_role": "Quantum AI Engineer",
        "required_skills": [
            {"skill": "Python", "priority": "critical", "category": "foundation"},
            {"skill": "Machine Learning", "priority": "critical", "category": "foundation"},
            {"skill": "Quantum Computing", "priority": "high", "category": "domain"},
        ],
        "career_progression": ["Senior Quantum AI Engineer", "Quantum AI Architect"],
        "passes_validation": True,
    }
    monkeypatch.setattr(career_understanding, "is_gemini_available", lambda: True)
    execute = monkeypatch.setattr(
        career_understanding, "_execute_gemini", lambda *args, **kwargs: json.dumps(parser_response)
    )

    first = resolve_role_details("Quantum AI Engineer")
    gap, required = compute_skill_gap("Quantum AI Engineer", ["Python"])

    assert first["confidence"] == "medium-high"
    assert first["source"] == "AI Validated Career Path"
    assert "Quantum Computing" in required
    assert "Quantum Computing" in gap

    reloaded = CareerUnderstandingService(RoleExpansionRepository(str(database_path)))
    monkeypatch.setattr(career_understanding, "career_understanding_service", reloaded)
    monkeypatch.setattr(recommender_module, "career_understanding_service", reloaded)
    monkeypatch.setattr(career_understanding, "_execute_gemini", lambda *args, **kwargs: pytest.fail("cached role called Gemini"))

    second = resolve_role_details("Quantum AI Engineer")
    assert second["role"] == "Quantum AI Engineer"
    assert second["confidence"] == "medium-high"


def test_invalid_or_parser_rejected_role_returns_422_without_scoring(monkeypatch, isolated_role_store):
    _, service, _ = isolated_role_store
    parser_calls = []
    monkeypatch.setattr(service, "parse_and_cache", lambda role: parser_calls.append(role) or None)
    assert resolve_role_details("banana")["role"] is None
    assert parser_calls == []

    client = TestClient(app)
    response = client.get("/career_path/banana")
    assert response.status_code == 422

    parsed_response = client.get("/career_path/Quantum%20AI%20Engineer")
    assert parsed_response.status_code == 422
    assert parser_calls == ["Quantum AI Engineer"]
