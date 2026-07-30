"""
Exhaustive tests covering skill normalization, acronym expansion, deduplication, and parsing.
"""

import pytest
from app.data.taxonomy import normalize_and_deduplicate_skills, SKILL_SYNONYMS


class TestExhaustiveSkillsNormalization:
    def test_empty_or_whitespace_skills(self):
        assert normalize_and_deduplicate_skills([]) == []
        assert normalize_and_deduplicate_skills(["", "   ", "\n", None]) == []

    @pytest.mark.parametrize("raw_list,expected_subset", [
        (["ML", "Machine Learning"], ["Machine Learning"]),
        (["Deep Learning", "DL", "Neural Networks"], ["Deep Learning", "Neural Networks"]),
        (["NLP", "Natural Language Processing"], ["Natural Language Processing"]),
        (["CV", "Computer Vision"], ["Computer Vision"]),
        (["JS", "JavaScript", "ECMAScript"], ["JavaScript"]),
        (["TS", "TypeScript"], ["TypeScript"]),
        (["PyTorch", "pytorch", "PYTORCH"], ["PyTorch"]),
        (["TensorFlow", "TF", "tensorflow"], ["TensorFlow"]),
        (["AWS", "Amazon Web Services"], ["Amazon Web Services"]),
        (["GCP", "Google Cloud Platform"], ["Google Cloud Platform"]),
        (["K8s", "Kubernetes"], ["Kubernetes"]),
        (["CI/CD", "Continuous Integration"], ["Continuous Integration"]),
    ])
    def test_synonym_and_acronym_deduplication(self, raw_list, expected_subset):
        normalized = normalize_and_deduplicate_skills(raw_list)
        for expected in expected_subset:
            assert expected in normalized
        # Verify no duplicates
        assert len(normalized) == len(set(normalized))

    def test_mixed_delimiters_and_case_normalization(self):
        raw = ["python, machine learning", "SQL; Docker", "   Git  , AWS "]
        normalized = normalize_and_deduplicate_skills(raw)
        assert "Python" in normalized
        assert "Machine Learning" in normalized
        assert "SQL" in normalized
        assert "Docker" in normalized
        assert "Git" in normalized
        assert "Amazon Web Services" in normalized or "AWS" in normalized
        assert len(normalized) == len(set(normalized))

    def test_order_preservation_and_cleanliness(self):
        raw = ["React", "Node.js", "Express", "React", "MongoDB"]
        normalized = normalize_and_deduplicate_skills(raw)
        assert normalized[:2] == ["React", "Node.js"]
        assert len(normalized) == 4
