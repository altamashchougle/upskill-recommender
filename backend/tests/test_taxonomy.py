"""
Unit tests for career role taxonomy and skill gap computation.
"""

import pytest
from app.data.taxonomy import (
    JOB_ROLE_MAPPING,
    get_target_skills,
    get_relevant_subjects,
    categorize_course_subject,
    resolve_role,
    skill_matches_text,
    extract_skills_from_text,
)
from app.ml.scoring import compute_skill_gap


def test_get_target_skills_exact_match():
    skills = get_target_skills("AI Engineer")
    assert "Python" in skills
    assert "PyTorch" in skills
    assert "Transformers" in skills
    assert "Machine Learning" in skills
    assert "Deep Learning" in skills
    assert "MLOps" in skills
    assert "NLP" in skills
    assert "Computer Vision" in skills


def test_resolve_role_data_analyst_not_data_scientist():
    """'data analyst' must resolve to Data Analyst, not Data Scientist."""
    assert resolve_role("data analyst") == "Data Analyst"
    assert resolve_role("Data Analyst") == "Data Analyst"


def test_resolve_role_ai_engineer():
    assert resolve_role("AI engineer") == "AI Engineer"
    assert resolve_role("ai engineer") == "AI Engineer"


def test_resolve_role_software_developer():
    assert resolve_role("Software Developer") == "Software Engineer"


def test_get_target_skills_fuzzy_match():
    skills = get_target_skills("Lead Data Scientist")
    assert "Python" in skills
    assert "Statistics" in skills


def test_get_relevant_subjects():
    subjects = get_relevant_subjects("AI Engineer")
    assert "Machine Learning" in subjects
    assert "Data Science" in subjects


def test_categorize_course_subject():
    subj = categorize_course_subject("Deep Learning with PyTorch", "Learn neural networks", "python, pytorch")
    assert subj == "Machine Learning"

    subj_web = categorize_course_subject("Full Stack React and Node", "Build responsive web apps", "javascript, react")
    assert subj_web == "Web Development"


def test_skill_synonym_matching():
    assert skill_matches_text("Machine Learning", "Complete ML bootcamp for beginners")
    assert skill_matches_text("Deep Learning", "Introduction to neural networks")
    assert skill_matches_text("NLP", "natural language processing with transformers")


def test_extract_skills_from_text():
    skills = extract_skills_from_text("Python for Machine Learning and Deep Learning with PyTorch")
    assert "Python" in skills
    assert "Machine Learning" in skills
    assert "Deep Learning" in skills
    assert "PyTorch" in skills


def test_compute_skill_gap():
    user_skills = ["Python", "SQL", "Git"]
    gap, required = compute_skill_gap("AI Engineer", user_skills)

    assert "Python" not in gap
    assert "SQL" not in gap
    assert "PyTorch" in gap
    assert "Deep Learning" in gap
    assert "MLOps" in gap
    assert len(required) > len(gap)


def test_compute_skill_gap_with_current_role_baseline():
    """Data Analyst baseline skills should reduce the gap when transitioning to AI Engineer."""
    gap, required = compute_skill_gap("AI Engineer", [], current_role="Data Analyst")

    assert "Python" not in gap
    assert "SQL" not in gap
    assert "Excel" not in gap
    assert "Power BI" not in gap
    assert "Tableau" not in gap
    assert "Machine Learning" in gap
    assert "Deep Learning" in gap
    assert "PyTorch" in gap
    assert "TensorFlow" in gap
    assert "MLOps" in gap
    assert "NLP" in gap
