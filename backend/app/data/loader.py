"""
Data loader module for ingesting, cleaning, and standardizing course catalog CSV datasets.
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any
from app.data.taxonomy import categorize_course_subject, extract_skills_from_text

logger = logging.getLogger(__name__)

# Locate dataset CSV files reliably from backend/data/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
UDEMY_PATH = os.path.join(BASE_DIR, "udemy_courses.csv")
COURSERA_PATH = os.path.join(BASE_DIR, "Coursera.csv")


def _safe_float(val: Any, default: float = 0.0) -> float:
    if pd.isna(val) or val is None:
        return default
    if isinstance(val, str) and val.strip().lower() in {"nan", "none", "null", ""}:
        return default
    try:
        res = float(val)
        if pd.isna(res):
            return default
        return res
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    if pd.isna(val) or val is None:
        return default
    if isinstance(val, str) and val.strip().lower() in {"nan", "none", "null", ""}:
        return default
    try:
        res = float(val)
        if pd.isna(res):
            return default
        return int(res)
    except (ValueError, TypeError):
        return default


def _safe_str(val: Any, default: str = "") -> str:
    if pd.isna(val) or val is None:
        return default
    s = str(val).strip()
    if s.lower() in {"nan", "none", "null"}:
        return default
    return s


def load_udemy_courses() -> List[Dict[str, Any]]:
    """Load and standardize Udemy courses from CSV."""
    if not os.path.exists(UDEMY_PATH):
        logger.warning(f"Udemy dataset not found at {UDEMY_PATH}")
        return []

    try:
        df = pd.read_csv(UDEMY_PATH)
        courses = []
        for _, row in df.iterrows():
            try:
                title = _safe_str(row.get("course_title"), "Unknown Title")
                if not title or title == "Unknown Title":
                    continue
                raw_subject = _safe_str(row.get("subject"), "General")
                level = _safe_str(row.get("level"), "All Levels")
                num_reviews = _safe_int(row.get("num_reviews"), 0)
                num_subscribers = max(_safe_int(row.get("num_subscribers"), 1), 1)

                # Rating approximation formula using review-to-subscriber ratio quality signal
                review_ratio = num_reviews / num_subscribers
                rating = round(min(5.0, max(3.0, 3.5 + review_ratio * 5)), 1)

                num_lectures = _safe_int(row.get("num_lectures"), 0)
                description = (
                    f"{level} course in {raw_subject} "
                    f"with {num_lectures} lectures. {num_subscribers} students enrolled."
                )
                skills_covered = extract_skills_from_text(f"{title} {raw_subject} {description}")
                subject = categorize_course_subject(title, description, " ".join(skills_covered))

                content_dur = _safe_str(row.get("content_duration"), "Unknown")
                course = {
                    "title": title,
                    "provider": "Udemy",
                    "url": _safe_str(row.get("url"), ""),
                    "is_paid": bool(row.get("is_paid", True) in [True, "True", "true", 1]),
                    "price": _safe_float(row.get("price"), 0.0),
                    "num_subscribers": num_subscribers,
                    "level": level,
                    "duration": f"{content_dur} hours",
                    "subject": subject,
                    "description": description,
                    "popularity_score": float(num_subscribers * (1 + num_reviews / 1000)),
                    "platform": "udemy",
                    "rating": rating,
                    "university": "",
                    "skills_covered": skills_covered,
                    "ai_enhanced": False,
                }
                courses.append(course)
            except Exception as row_err:
                logger.debug(f"Skipping malformed Udemy row: {row_err}")
                continue
        logger.info(f"Loaded {len(courses)} Udemy courses")
        return courses
    except Exception as e:
        logger.error(f"Failed to load Udemy courses from {UDEMY_PATH}: {e}")
        return []


def load_coursera_courses() -> List[Dict[str, Any]]:
    """Load and standardize Coursera courses from CSV according to actual column schema."""
    if not os.path.exists(COURSERA_PATH):
        logger.warning(f"Coursera dataset not found at {COURSERA_PATH}")
        return []

    try:
        df = pd.read_csv(COURSERA_PATH)
        courses = []
        for _, row in df.iterrows():
            try:
                title = _safe_str(row.get("Course Name"), "Unknown Course")
                if not title or title == "Unknown Course":
                    continue
                url = _safe_str(row.get("Course URL"), "")
                level = _safe_str(row.get("Difficulty Level"), "All Levels")
                description = _safe_str(row.get("Course Description"), f"{level} course on Coursera.")
                skills_text = _safe_str(row.get("Skills"), "")
                university = _safe_str(row.get("University"), "")

                rating = round(min(5.0, max(0.0, _safe_float(row.get("Course Rating"), 0.0))), 1)

                # Parse skills: separated by mixed delimiters or double spaces
                skills_list = [
                    s.strip()
                    for s in skills_text.replace("  ", ",").split(",")
                    if s.strip() and len(s.strip()) > 1
                ]

                # Categorize domain subject
                subject = categorize_course_subject(title, description, skills_text)

                short_desc = description[:500] if description else f"{level} course on Coursera."

                course = {
                    "title": title,
                    "provider": "Coursera",
                    "url": url,
                    "is_paid": False,
                    "price": 0.0,
                    "num_subscribers": 0,
                    "level": level,
                    "duration": "Self-paced",
                    "subject": subject,
                    "description": short_desc,
                    "popularity_score": float(rating * 100),
                    "platform": "coursera",
                    "rating": rating,
                    "university": university,
                    "skills_covered": skills_list[:10],
                    "ai_enhanced": False,
                }
                courses.append(course)
            except Exception as row_err:
                logger.debug(f"Skipping malformed Coursera row: {row_err}")
                continue
        logger.info(f"Loaded {len(courses)} Coursera courses")
        return courses
    except Exception as e:
        logger.error(f"Failed to load Coursera courses from {COURSERA_PATH}: {e}")
        return []


def get_all_courses() -> List[Dict[str, Any]]:
    """Load all courses across both catalogs and return unified dataset."""
    udemy = load_udemy_courses()
    coursera = load_coursera_courses()
    combined = udemy + coursera
    logger.info(f"Total courses loaded into memory catalog: {len(combined)}")
    return combined
