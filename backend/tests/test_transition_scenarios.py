"""
Scenario tests for career transition recommendations.
Verifies that recommendations target missing skills, not the user's current role.
"""

import pytest
from app.data.loader import load_udemy_courses
from app.ml.vectorizer import CourseVectorizer
from app.ml.scoring import score_and_rank_courses, compute_skill_gap
from app.services.recommender import RecommenderService


@pytest.fixture(scope="module")
def udemy_catalog():
    courses = load_udemy_courses()
    vectorizer = CourseVectorizer(max_features=1500)
    vectorizer.fit(courses)
    return courses, vectorizer


def _rank_transition(courses, vectorizer, current_role, target_role, user_skills=None, top_n=10):
    user_skills = user_skills or []
    gap, _ = compute_skill_gap(target_role, user_skills, current_role)
    query = f"{target_role} {' '.join(gap)}"
    sims = vectorizer.compute_similarity(query)
    ranked, _ = score_and_rank_courses(
        courses=courses,
        tfidf_sims=sims,
        target_role=target_role,
        user_skills=user_skills,
        current_role=current_role,
        top_n=top_n,
    )
    return ranked, gap


def _assert_no_finance_analyst_courses(ranked):
    finance_hits = [
        r["title"] for r in ranked
        if any(kw in r["title"].lower() for kw in ["financial analyst", "python for finance"])
        and not any(ok in r["title"].lower() for ok in ["statistics", "machine learning", "data science"])
    ]
    assert not finance_hits, f"Finance/analyst courses should not rank highly: {finance_hits}"


def test_scenario_data_analyst_to_ai_engineer(udemy_catalog):
    courses, vectorizer = udemy_catalog
    ranked, gap = _rank_transition(courses, vectorizer, "Data Analyst", "AI Engineer")

    assert "Machine Learning" in gap
    assert "Deep Learning" in gap
    _assert_no_finance_analyst_courses(ranked[:5])
    assert (
        ranked[0].get("skill_gap_addressed")
        or ranked[0]["subject"] in {"Machine Learning", "Data Science", "IT & Software"}
    )


def test_scenario_software_developer_to_ml_engineer(udemy_catalog):
    courses, vectorizer = udemy_catalog
    ranked, gap = _rank_transition(courses, vectorizer, "Software Developer", "Machine Learning Engineer")

    assert "Machine Learning" in gap
    assert "Deep Learning" in gap
    _assert_no_finance_analyst_courses(ranked[:5])


def test_scenario_python_developer_to_data_scientist(udemy_catalog):
    courses, vectorizer = udemy_catalog
    ranked, gap = _rank_transition(courses, vectorizer, "Python Developer", "Data Scientist")

    assert "Statistics" in gap or "Machine Learning" in gap
    _assert_no_finance_analyst_courses(ranked[:5])
    top_subjects = {r.get("subject") for r in ranked[:5]}
    assert top_subjects & {"Machine Learning", "Data Science", "Programming Languages"}


def test_recommender_service_transition():
    service = RecommenderService()
    service.initialize()

    ranked, gap, _, _ = service.get_recommendations(
        job_role="data analyst",
        user_skills=[],
        goal="AI engineer",
        top_n=10,
    )

    assert "Machine Learning" in gap
    assert "Deep Learning" in gap
    assert "Python" not in gap
    assert "SQL" not in gap

    top_titles = [r["title"].lower() for r in ranked[:5]]
    assert not any("financial analyst" in t for t in top_titles)
