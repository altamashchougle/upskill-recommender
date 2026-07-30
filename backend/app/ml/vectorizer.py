"""
TF-IDF vectorizer engine for computing semantic text similarity across courses.
Pre-computes and caches matrix at application startup for O(1) query performance.
"""

import logging
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class CourseVectorizer:
    """Manages text representation and cosine similarity scoring for courses."""

    def __init__(self, max_features: int = 1500):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
        self.tfidf_matrix = None
        self.courses: List[Dict[str, Any]] = []

    def fit(self, courses: List[Dict[str, Any]]):
        """Fit vectorizer on all course metadata during startup."""
        self.courses = courses
        if not courses:
            logger.warning("No courses provided to CourseVectorizer.fit()")
            return

        corpus = [
            (
                f"{c.get('title', '')} {c.get('subject', '')} {c.get('level', '')} "
                f"{c.get('description', '')} {' '.join(c.get('skills_covered', []))}"
            )
            for c in courses
        ]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        logger.info(f"Fitted TfidfVectorizer with matrix shape {self.tfidf_matrix.shape}")

    def compute_similarity(self, query_text: str) -> List[float]:
        """Compute cosine similarity vector between query text and all fitted courses."""
        if self.tfidf_matrix is None or not self.courses:
            return [0.0] * len(self.courses)

        if not query_text or not query_text.strip():
            return [0.0] * len(self.courses)

        query_vec = self.vectorizer.transform([query_text])
        sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        return sims.tolist()
