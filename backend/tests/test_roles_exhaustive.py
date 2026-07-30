"""
Exhaustive tests covering all job role categories, confidence scores, aliases, and fuzzy resolution.
"""

import pytest
from app.data.taxonomy import resolve_role_details, JOB_ROLE_MAPPING


class TestExhaustiveRoleResolution:
    @pytest.mark.parametrize("canonical_role", list(JOB_ROLE_MAPPING.keys()))
    def test_all_canonical_roles_resolve_exact(self, canonical_role):
        details = resolve_role_details(canonical_role)
        assert details["role"] == canonical_role
        assert details["confidence"] == "high"
        assert details["source"] == "Verified Career Path"
        assert len(JOB_ROLE_MAPPING[canonical_role]["skills"]) > 0

    @pytest.mark.parametrize("query,expected_role", [
        ("ML Engineer", "Machine Learning Engineer"),
        ("Python Dev", "Python Developer"),
        ("JS Developer", "Frontend Developer"),
        ("Web Developer", "Full Stack Developer"),
        ("Cloud Architect", "Cloud Engineer"),
        ("Sec Analyst", "Cybersecurity Analyst"),
        ("BI Analyst", "Data Analyst"),
        ("Product Owner", "Product Manager"),
        ("DevOps Specialist", "DevOps Engineer"),
        ("Test Engineer", "QA Engineer"),
        ("UX Researcher", "UX Designer"),
        ("UI Designer", "UX Designer"),
        ("Graphic Artist", "Graphic Designer"),
    ])
    def test_known_aliases_resolve_high_confidence(self, query, expected_role):
        details = resolve_role_details(query)
        assert details["role"] == expected_role
        assert details["confidence"] == "high"
        assert details["source"] == "Verified Career Path"

    @pytest.mark.parametrize("query,expected_role", [
        ("Senior Machine Learning Developer", "Machine Learning Engineer"),
        ("Lead Python Backend Architect", "Python Developer"),
        ("Principal Data Science Specialist", "Data Scientist"),
        ("Junior Web Frontend Dev", "Frontend Developer"),
        ("Cloud Infrastructure Specialist", "Cloud Engineer"),
        ("Director of Product Management", "Product Manager"),
    ])
    def test_multi_word_and_seniority_fuzzy_resolution(self, query, expected_role):
        details = resolve_role_details(query)
        assert details["role"] == expected_role
        assert details["confidence"] in ["high", "medium"]
        assert details["source"] in ["Fuzzy Match", "Verified Career Path"]

    @pytest.mark.parametrize("invalid_query", [
        "",
        "   ",
        "xyz123",
        "intern",
        "manager",
        "assistant",
        "asdfghjkl",
        "finance",
        "accounting consultant",
    ])
    def test_completely_invalid_or_unrelated_queries(self, invalid_query):
        details = resolve_role_details(invalid_query)
        assert details["confidence"] in ["low", "none"]
        assert isinstance(details["suggestions"], list)
