import pytest
from app.ml.scoring import calculate_domain_alignment, score_and_rank_courses
from app.services.recommender import RecommenderService
from app.data.taxonomy import DOMAIN_ONTOLOGY, expand_text_with_skill_synonyms

def test_domain_alignment_autonomous_driving():
    # Primary hits
    text_good = "Master autonomous vehicle technology with ROS and sensor fusion using C++ and LiDAR."
    score_good = calculate_domain_alignment(text_good, "Autonomous Driving Engineer", [])
    assert score_good >= 0.8
    
    # Generic hits only
    text_generic = "Learn Python and Machine Learning for general AI programming."
    score_generic = calculate_domain_alignment(text_generic, "Autonomous Driving Engineer", [])
    assert score_generic < 0.4
    
def test_domain_alignment_llm_engineer():
    text_good = "Build advanced RAG pipelines with vector databases, embeddings, and prompt engineering using LangChain."
    score_good = calculate_domain_alignment(text_good, "LLM Engineer", [])
    assert score_good >= 0.8

def test_negative_filtering_in_scoring():
    courses = [
        {
            "title": "Medical Image Processing",
            "description": "Learn MRI and medical imaging healthcare applications.",
            "subject": "Healthcare",
            "skills_covered": ["Computer Vision", "Deep Learning"],
            "rating": 4.8,
            "num_subscribers": 10000
        },
        {
            "title": "Self Driving Cars with ROS",
            "description": "Master autonomous vehicles.",
            "subject": "Engineering",
            "skills_covered": ["ROS", "C++"],
            "rating": 4.8,
            "num_subscribers": 10000
        }
    ]
    
    # Give high TFIDF to both
    tfidf_sims = [0.8, 0.8]
    
    ranked, gap = score_and_rank_courses(
        courses=courses,
        tfidf_sims=tfidf_sims,
        target_role="Autonomous Driving Engineer",
        user_skills=["Python"],
    )
    
    # Self Driving should be ranked much higher due to negative domain filtering on the first one
    assert ranked[0]["title"] == "Self Driving Cars with ROS"
    assert ranked[1]["title"] == "Medical Image Processing"
    
    # Ensure domain penalty worked
    assert ranked[1]["ranking_explanation"]["s_current_role_penalty"] >= 0.8

def test_search_query_expansion():
    # Test skill synonyms expansion
    text = "Building a RAG pipeline"
    expanded = expand_text_with_skill_synonyms(text)
    assert "retrieval augmented generation" in expanded
    
    text2 = "Sensor fusion in autonomous driving"
    expanded2 = expand_text_with_skill_synonyms(text2)
    assert "lidar" in expanded2
    assert "radar" in expanded2

def test_quality_gates():
    svc = RecommenderService()
    svc.initialize()
    
    # Test a scenario that should trigger the fallback or filter poorly aligned courses
    recs, gap, cov, path = svc.get_recommendations(
        job_role="Data Entry",
        user_skills=["Excel"],
        goal="Autonomous Driving Engineer",
        top_n=5
    )
    
    assert len(recs) > 0
    # The top recommended courses for Autonomous Driving Engineer should contain primary keywords
    top_course = recs[0]
    course_text = (top_course.get("title", "") + " " + top_course.get("description", "")).lower()
    
    # Ideally should be a robotics/autonomous driving course or at least computer vision
    assert calculate_domain_alignment(course_text, "Autonomous Driving Engineer", gap) > 0.1
