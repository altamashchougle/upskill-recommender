"""
Adversarial test suite for Upskill Recommender.
Covers exhaustive role resolution, invalid input handling, typo/alias resilience,
and complete career transition gap/scoring validation without current-role bias or invalid role invention.
"""

import pytest
from app.data.taxonomy import (
    resolve_role,
    suggest_closest_roles,
    get_target_skills,
    get_relevant_subjects,
    expand_text_with_skill_synonyms,
)
from app.services.recommender import recommender_service


class TestValidRoleResolution:
    """Test 20+ valid role resolutions across aliases, abbreviations, and canonical names."""

    @pytest.mark.parametrize("input_role,expected_canonical", [
        ("AI Engineer", "AI Engineer"),
        ("ai eng", "AI Engineer"),
        ("artificial intelligence engineer", "AI Engineer"),
        ("ai dev", "AI Engineer"),
        ("Machine Learning Engineer", "Machine Learning Engineer"),
        ("ml eng", "Machine Learning Engineer"),
        ("ml engineer", "Machine Learning Engineer"),
        ("Data Scientist", "Data Scientist"),
        ("data sci", "Data Scientist"),
        ("data science", "Data Scientist"),
        ("Data Analyst", "Data Analyst"),
        ("bi analyst", "Data Analyst"),
        ("Business Analyst", "Business Analyst"),
        ("ba", "Business Analyst"),
        ("Software Engineer", "Software Engineer"),
        ("swe", "Software Engineer"),
        ("sde", "Software Engineer"),
        ("programmer", "Software Engineer"),
        ("Frontend Developer", "Frontend Developer"),
        ("fe dev", "Frontend Developer"),
        ("Backend Developer", "Backend Developer"),
        ("be dev", "Backend Developer"),
        ("Full Stack Developer", "Full Stack Developer"),
        ("fs dev", "Full Stack Developer"),
        ("DevOps Engineer", "DevOps Engineer"),
        ("sre", "SRE"),
        ("Product Manager", "Product Manager"),
        ("pm", "Product Manager"),
        ("Graphic Designer", "Graphic Designer"),
        ("UX Designer", "UX Designer"),
        ("ui/ux", "UX Designer"),
        ("QA Engineer", "QA Engineer"),
        ("qa tester", "QA Engineer"),
        ("Cybersecurity Analyst", "Cybersecurity Analyst"),
        ("Cloud Engineer", "Cloud Engineer"),
    ])
    def test_valid_role_mappings(self, input_role, expected_canonical):
        assert resolve_role(input_role) == expected_canonical


class TestInvalidRoleRejection:
    """Test 20+ invalid inputs and generic words that should return None instead of arbitrary matching."""

    @pytest.mark.parametrize("invalid_role", [
        "",
        "   ",
        "engineer",
        "developer",
        "analyst",
        "manager",
        "designer",
        "specialist",
        "dev",
        "architect",
        "lead",
        "senior",
        "director",
        "junior",
        "xyz",
        "foo bar",
        "123459",
        "senior xyz",
        "lead abc",
        "a",
    ])
    def test_invalid_and_generic_roles_return_none(self, invalid_role):
        assert resolve_role(invalid_role) is None


class TestFuzzyAndTypoResilience:
    """Test 20+ typo, partial, and fuzzy/alias queries."""

    @pytest.mark.parametrize("query,expected", [
        ("machine learning dev", "Machine Learning Engineer"),
        ("python engineer", "Python Developer"),
        ("web dev", "Full Stack Developer"),
        ("software dev", "Software Engineer"),
        ("frontend dev", "Frontend Developer"),
        ("backend dev", "Backend Developer"),
        ("fullstack dev", "Full Stack Developer"),
        ("cloud architect", "Cloud Engineer"),
        ("coder", "Software Engineer"),
        ("ui/ux designer", "UX Designer"),
        ("security analyst", "Cybersecurity Analyst"),
        ("data analysis", "Data Analyst"),
        ("quality assurance", "QA Engineer"),
        ("site reliability engineer", "SRE"),
        ("graphic design", "Graphic Designer"),
        ("product mgr", "Product Manager"),
        ("ai/ml engineer", "AI Engineer"),
        ("ml/ai engineer", "Machine Learning Engineer"),
        ("front end dev", "Frontend Developer"),
        ("back end dev", "Backend Developer"),
    ])
    def test_fuzzy_and_alias_queries(self, query, expected):
        assert resolve_role(query) == expected


class TestCareerPathSafety:
    """Verify career path generation never invents 'Senior {role}' or 'Lead {role}' for unknown inputs."""

    def test_unknown_role_career_path_suggests_alternatives(self):
        path = recommender_service.get_career_path("xyz_unresolvable_role")
        assert path["current_role"] == "xyz_unresolvable_role"
        assert "Senior xyz_unresolvable_role" not in path.get("next_roles", [])
        assert len(path["next_roles"]) > 0
        # Ensure suggestions are canonical roles
        assert any(r in path["next_roles"] for r in ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"])

    def test_generic_engineer_career_path_suggests_alternatives(self):
        path = recommender_service.get_career_path("engineer")
        assert "Senior engineer" not in path.get("next_roles", [])
        assert len(path["next_roles"]) > 0


class TestAdversarialCareerTransitions:
    """Test realistic and adversarial career transitions verifying gap calculation and recommendation quality."""

    def test_scenario_data_analyst_to_ai_engineer_no_finance_bias(self):
        """Problem 1: Data Analyst transitioning to AI Engineer must not get Finance/Excel courses."""
        recs, gap, _, _ = recommender_service.get_recommendations(
            job_role="Data Analyst",
            user_skills=["SQL", "Excel", "Tableau", "Power BI"],
            goal="AI Engineer",
            top_n=10
        )
        assert "PyTorch" in gap or "Deep Learning" in gap or "Machine Learning" in gap
        assert "Excel" not in gap
        assert "Tableau" not in gap

        finance_markers = ["financial analyst", "cfa", "investment banking", "excel analytics for finance"]
        for r in recs:
            title_desc = f"{r.get('title', '')} {r.get('description', '')}".lower()
            assert not any(m in title_desc for m in finance_markers), f"Irrelevant course found: {r['title']}"

    def test_scenario_ba_to_data_scientist(self):
        """Verify Business Analyst to Data Scientist gap covers ML/Python and rejects invalid role invention."""
        path = recommender_service.get_career_path("ba")
        assert path["current_role"] == "Business Analyst"
        assert "Senior Business Analyst" in path["next_roles"]

        recs, gap, _, _ = recommender_service.get_recommendations(
            job_role="ba",
            user_skills=["SQL", "Excel"],
            goal="Data Scientist",
            top_n=8
        )
        assert "Machine Learning" in gap
        assert len(recs) > 0

    def test_scenario_software_engineer_to_devops(self):
        recs, gap, _, _ = recommender_service.get_recommendations(
            job_role="Software Engineer",
            user_skills=["Python", "Git", "SQL"],
            goal="DevOps Engineer",
            top_n=8
        )
        assert "Docker" in gap or "Kubernetes" in gap or "CI/CD" in gap

    def test_scenario_qa_to_full_stack(self):
        recs, gap, _, _ = recommender_service.get_recommendations(
            job_role="qa tester",
            user_skills=["Automated Testing", "Selenium", "Python"],
            goal="Full Stack Developer",
            top_n=8
        )
        assert "React" in gap or "Node.js" in gap or "JavaScript" in gap
