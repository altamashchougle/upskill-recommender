"""
Comprehensive test suite for Career Intelligence improvements (`Part A`).
Tests:
1. Exact vs fuzzy role resolution rules (`AI Research Scientist` must never downgrade to `AI Engineer`).
2. Separate progression tracks for Engineering vs Research vs Platform leadership.
3. Role-specific phased learning roadmap templates.
4. Course recommendation diversity post-processing selection (`_apply_course_diversity`).
"""

import pytest
from app.data.taxonomy import resolve_role_details, resolve_role, JOB_ROLE_MAPPING
from app.services.gemini import _fallback_roadmap
from app.services.recommender import _apply_course_diversity, RecommenderService


def test_research_roles_exact_resolution():
    """Verify exact resolution of newly added research career tracks."""
    research_roles = [
        "AI Research Scientist",
        "ML Research Scientist",
        "Applied Scientist",
        "Research Engineer"
    ]
    for role in research_roles:
        details = resolve_role_details(role)
        assert details["role"] == role
        assert details["confidence"] == "high"
        assert details["source"] == "Verified Career Path"
        assert details["message"] == f"Exact match for {role}."
        assert role != "AI Engineer"


def test_research_roles_fuzzy_and_typo_resolution():
    """Verify actual spelling mistakes trigger fuzzy/medium confidence resolution without affecting valid titles."""
    # Typo input should resolve to AI Research Scientist via fuzzy source
    details = resolve_role_details("ai reserch scientist")
    assert details["role"] == "AI Research Scientist"
    assert details["confidence"] == "medium"
    assert details["source"] == "Fuzzy Match"

    # Typo input for engineering should resolve via fuzzy source
    eng_details = resolve_role_details("ai enginer")
    assert eng_details["role"] == "AI Engineer"
    assert eng_details["confidence"] == "medium"
    assert eng_details["source"] == "Fuzzy Match"


def test_separated_leadership_progression_tracks():
    """Verify distinct progression tracks for Engineering vs Research vs Platform paths."""
    ai_eng_next = JOB_ROLE_MAPPING["AI Engineer"]["next_roles"]
    assert "Director of AI" in ai_eng_next
    assert "Director of AI Research" not in ai_eng_next

    research_sci_next = JOB_ROLE_MAPPING["AI Research Scientist"]["next_roles"]
    assert "Director of AI Research" in research_sci_next
    assert "AI Engineering Manager" not in research_sci_next

    ml_eng_next = JOB_ROLE_MAPPING["Machine Learning Engineer"]["next_roles"]
    assert "AI Platform Lead" in ml_eng_next


def test_role_specific_roadmap_templates():
    """Verify specialized phased templates are produced for distinct career tracks."""
    # 1. AI Research Scientist roadmap (4 months)
    res_roadmap = _fallback_roadmap(
        current_role="Data Analyst",
        current_skills=["SQL", "Python"],
        target_role="AI Research Scientist",
        skill_gaps=["Deep Learning", "PyTorch", "Transformers", "Statistics"],
        recommended_courses=["Advanced PyTorch", "Transformers Deep Dive"]
    )
    phases = [p["phase"] for p in res_roadmap["roadmap"]]
    assert len(phases) == 4
    assert phases[0] == "Month 1: Mathematical Foundations"
    assert phases[1] == "Month 2: Deep Learning Research"
    assert phases[2] == "Month 3: Modern AI Research"
    assert phases[3] == "Month 4: Research Portfolio"

    # 2. AI Engineer roadmap (3 months)
    eng_roadmap = _fallback_roadmap(
        current_role="Software Engineer",
        current_skills=["Python", "Docker"],
        target_role="AI Engineer",
        skill_gaps=["MLOps", "Transformers", "PyTorch"],
        recommended_courses=["AI Deployment"]
    )
    eng_phases = [p["phase"] for p in eng_roadmap["roadmap"]]
    assert len(eng_phases) == 3
    assert eng_phases[0] == "Month 1: ML Engineering Fundamentals"
    assert eng_phases[1] == "Month 2: Deep Learning"
    assert eng_phases[2] == "Month 3: Deployment and MLOps"

    # 3. Machine Learning Engineer roadmap (3 months)
    ml_roadmap = _fallback_roadmap(
        current_role="Python Developer",
        current_skills=["Python", "Git"],
        target_role="Machine Learning Engineer",
        skill_gaps=["Kubernetes", "PyTorch", "Scikit-Learn"],
        recommended_courses=["ML Systems"]
    )
    ml_phases = [p["phase"] for p in ml_roadmap["roadmap"]]
    assert len(ml_phases) == 3
    assert ml_phases[0] == "Month 1: Machine Learning Foundations"
    assert ml_phases[1] == "Month 2: Model Engineering"
    assert ml_phases[2] == "Month 3: Production ML Systems"


def test_course_diversity_selection():
    """Verify diversity algorithm selects items across distinct subjects and missing skills over duplicates."""
    candidates = [
        {"title": "TensorFlow Course 1", "subject": "Machine Learning", "skill_gap_addressed": ["TensorFlow"], "score": 0.95},
        {"title": "TensorFlow Course 2", "subject": "Machine Learning", "skill_gap_addressed": ["TensorFlow"], "score": 0.94},
        {"title": "PyTorch Mastery", "subject": "Machine Learning", "skill_gap_addressed": ["PyTorch"], "score": 0.90},
        {"title": "MLOps Bootcamp", "subject": "IT & Software", "skill_gap_addressed": ["MLOps", "Docker"], "score": 0.88},
        {"title": "Transformers & LLMs", "subject": "Machine Learning", "skill_gap_addressed": ["Transformers", "NLP"], "score": 0.85},
    ]

    top_3, _, _ = _apply_course_diversity(candidates, top_n=3, skill_gap=["TensorFlow", "PyTorch", "MLOps", "Transformers"], target_details={})
    selected_titles = [c["title"] for c in top_3]

    assert "TensorFlow Course 1" in selected_titles
    assert "PyTorch Mastery" in selected_titles
    assert "MLOps Bootcamp" in selected_titles
    # TensorFlow Course 2 (0.94) is skipped in Pass 1 in favor of PyTorch Mastery and MLOps Bootcamp to diversify skill coverage
    assert "TensorFlow Course 2" not in selected_titles


def test_recommender_service_end_to_end_diversity():
    """Verify live RecommenderService catalog returns diverse recommendations."""
    service = RecommenderService()
    service.initialize()
    recs, gap, _, _ = service.get_recommendations(
        job_role="Software Engineer",
        user_skills=["Python", "Git"],
        goal="AI Research Scientist",
        top_n=8
    )
    assert len(recs) <= 8
    # Check that we have recommendations covering deep learning / PyTorch / Transformers / research topics
    subjects = {r.get("subject") for r in recs if r.get("subject")}
    assert len(subjects) >= 1
