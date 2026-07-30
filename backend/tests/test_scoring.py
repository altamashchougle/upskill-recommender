"""
Unit tests for TF-IDF vectorizer precomputation and hybrid recommendation scoring.
"""

import pytest
from app.ml.vectorizer import CourseVectorizer
from app.ml.scoring import (
    calculate_quality_score,
    calculate_level_suitability,
    score_and_rank_courses
)


@pytest.fixture
def sample_courses():
    return [
        {
            "title": "Complete Machine Learning & PyTorch Bootcamp",
            "provider": "Udemy",
            "url": "http://example.com/ml",
            "is_paid": True,
            "price": 19.99,
            "num_subscribers": 100000,
            "level": "All Levels",
            "duration": "40 hours",
            "subject": "Machine Learning",
            "description": "Master machine learning, deep learning, and PyTorch from scratch.",
            "popularity_score": 95.0,
            "platform": "udemy",
            "rating": 4.8,
            "skills_covered": ["Python", "Machine Learning", "PyTorch", "Deep Learning"]
        },
        {
            "title": "Beginner HTML and CSS Web Design",
            "provider": "Coursera",
            "url": "http://example.com/web",
            "is_paid": False,
            "price": 0.0,
            "num_subscribers": 5000,
            "level": "Beginner",
            "duration": "10 hours",
            "subject": "Web Development",
            "description": "Learn HTML and CSS for basic frontend web design.",
            "popularity_score": 70.0,
            "platform": "coursera",
            "rating": 4.2,
            "skills_covered": ["HTML", "CSS"]
        }
    ]


def test_vectorizer_precomputation_and_similarity(sample_courses):
    vec = CourseVectorizer(max_features=100)
    assert vec.tfidf_matrix is None
    
    vec.fit(sample_courses)
    assert vec.tfidf_matrix is not None
    assert vec.tfidf_matrix.shape[0] == 2
    
    # Query for machine learning should match first course stronger than second
    sims = vec.compute_similarity("machine learning pytorch")
    assert len(sims) == 2
    assert sims[0] > sims[1]
    assert sims[0] > 0.1


def test_calculate_quality_score():
    course = {"rating": 5.0, "num_subscribers": 1000000, "provider": "Udemy"}
    score = calculate_quality_score(course)
    assert 0.8 < score <= 1.0


def test_calculate_level_suitability():
    course_beg = {"level": "Beginner"}
    course_adv = {"level": "Advanced"}
    
    # User with <=1 skill is beginner
    assert calculate_level_suitability(course_beg, 1) == 1.0
    assert calculate_level_suitability(course_adv, 1) < 0.5
    
    # User with >=5 skills is advanced
    assert calculate_level_suitability(course_adv, 6) == 1.0
    assert calculate_level_suitability(course_beg, 6) == 0.5


def test_score_and_rank_courses(sample_courses):
    vec = CourseVectorizer()
    vec.fit(sample_courses)
    sims = vec.compute_similarity("AI Engineer PyTorch Deep Learning")
    
    ranked, gap = score_and_rank_courses(
        courses=sample_courses,
        tfidf_sims=sims,
        target_role="AI Engineer",
        user_skills=["Python", "SQL"]
    )
    
    assert len(ranked) == 2
    assert ranked[0]["title"] == "Complete Machine Learning & PyTorch Bootcamp"
    assert "why_recommended" in ranked[0]
    assert "skills_gained" in ranked[0]
    assert "skill_gap_addressed" in ranked[0]
    assert ranked[0]["score"] > ranked[1]["score"]
