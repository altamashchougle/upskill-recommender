"""
Explainable hybrid scoring engine for upskilling recommendations.
Calculates multi-criteria scores across TF-IDF similarity, skill gap reduction,
career domain relevance, course quality, and difficulty level suitability.
"""

import math
import logging
from typing import List, Dict, Any, Tuple, Set
from app.data.taxonomy import (
    get_target_skills,
    get_relevant_subjects,
    resolve_role,
    normalize_skill_name,
    skill_matches_text,
    expand_text_with_skill_synonyms,
    DOMAIN_ONTOLOGY,
)

logger = logging.getLogger(__name__)


def _collect_possessed_skills(user_skills: List[str], current_role: str = "") -> Set[str]:
    """Build normalized set of skills the user already has (explicit + current role baseline)."""
    possessed: Set[str] = set()
    for skill in user_skills:
        if skill.strip():
            possessed.add(normalize_skill_name(skill))

    if current_role and current_role.strip():
        resolved = resolve_role(current_role)
        if resolved:
            for skill in get_target_skills(resolved):
                possessed.add(normalize_skill_name(skill))
    return possessed


def compute_skill_gap(
    target_role: str,
    user_skills: List[str],
    current_role: str = "",
) -> Tuple[List[str], List[str]]:
    """Compute required career skills and missing skill gap for a career transition.

    Gap = target_role_skills - (user_skills ∪ current_role_baseline_skills)

    Returns: (skill_gap, required_skills)
    """
    required = get_target_skills(target_role)
    possessed = _collect_possessed_skills(user_skills, current_role)
    gap = [s for s in required if normalize_skill_name(s) not in possessed]

    logger.info(
        "Skill Gap Audit -> Target: '%s' | Current Role: '%s' | Required: %s | "
        "Current Skills: %s | Possessed (incl. role baseline): %s | Missing/Gap: %s",
        target_role,
        current_role or "(none)",
        required,
        list(user_skills),
        sorted(possessed),
        gap,
    )
    return gap, required


def _build_course_text(course: Dict[str, Any]) -> str:
    """Build normalized searchable text for a course."""
    base = (
        f"{course.get('title', '')} {course.get('description', '')} "
        f"{course.get('subject', '')} {' '.join(course.get('skills_covered', []))}"
    )
    return expand_text_with_skill_synonyms(base)


def _calculate_current_role_penalty(
    course_text: str,
    course_subject: str,
    current_role: str,
    target_role: str,
    skill_gap: List[str],
    addressed: List[str],
) -> float:
    """Penalize courses that reinforce the user's current role or mismatch the target domain."""
    resolved_target = resolve_role(target_role) or target_role
    resolved_current = resolve_role(current_role) if current_role else None
    course_subject_lower = course_subject.lower()
    penalty = 0.0

    # 1. Absolute domain mismatch penalties regardless of addressed skills
    if resolved_target in {"AI Engineer", "Machine Learning Engineer", "Data Scientist"}:
        finance_markers = ["financial analyst", "finance", "accounting", "cfa", "investment banking"]
        if any(marker in course_text for marker in finance_markers):
            penalty += 0.5

        marketing_markers = ["marketing", "seo", "google ads", "social media marketing", "content marketing"]
        if course_subject_lower == "marketing" or any(marker in course_text for marker in marketing_markers):
            penalty += 0.5

        design_markers = ["graphic design", "photoshop", "illustrator", "figma", "typography"]
        if course_subject_lower == "design" or any(marker in course_text for marker in design_markers):
            penalty += 0.5

    if resolved_target == "Data Scientist":
        if course_subject_lower == "web development" or any(m in course_text for m in ["frontend", "react", "angular", "vue.js", "html and css"]):
            penalty += 0.4

    if resolved_target == "Backend Developer" and resolved_current == "Frontend Developer":
        if course_subject_lower == "design" or (course_subject_lower == "web development" and not any(k in course_text for k in ["backend", "api", "node", "python", "sql", "database"])):
            penalty += 0.35

    if resolved_target == "Autonomous Driving Engineer":
        if any(m in course_text for m in ["medical image", "medical imaging", "mri", "healthcare"]):
            penalty += 0.8
        if any(m in course_text for m in ["finance", "accounting", "banking"]):
            penalty += 0.8

    if resolved_target == "LLM Engineer":
        if any(m in course_text for m in ["electrical transformer", "power grid", "electricity"]):
            penalty += 0.8

    if not resolved_current or resolved_current == resolved_target:
        return min(0.9, penalty)

    # 2. If the course directly addresses the skill gap and has no major domain mismatch, allow it
    if addressed and penalty == 0.0:
        return 0.0

    current_subjects = {s.lower() for s in get_relevant_subjects(resolved_current)}
    target_subjects = {s.lower() for s in get_relevant_subjects(resolved_target)}

    if course_subject_lower in current_subjects and course_subject_lower not in target_subjects:
        penalty += 0.35

    current_skills = get_target_skills(resolved_current)
    current_only_hits = [
        s for s in current_skills
        if normalize_skill_name(s) not in {normalize_skill_name(g) for g in skill_gap}
        and skill_matches_text(s, course_text)
    ]
    if current_only_hits and not addressed:
        penalty += min(0.25, 0.08 * len(current_only_hits))

    return min(0.9, penalty)

def calculate_domain_alignment(course_text: str, target_role: str, skill_gap: List[str]) -> float:
    """Calculate domain alignment based on DOMAIN_ONTOLOGY (returns 0.0 to 1.0)."""
    resolved_target = resolve_role(target_role) or target_role
    course_text_lower = course_text.lower()
    
    ontology = DOMAIN_ONTOLOGY.get(resolved_target, None)
    
    if not ontology:
        # Fallback to legacy skill gap counting if no ontology
        addressed = [s for s in skill_gap if skill_matches_text(s, course_text)]
        if skill_gap:
            return min(1.0, len(addressed) / max(1, min(3, len(skill_gap))))
        return 0.5
        
    primary_hits = sum(1 for kw in ontology["primary"] if kw in course_text_lower)
    secondary_hits = sum(1 for kw in ontology["secondary"] if kw in course_text_lower)
    generic_hits = sum(1 for kw in ontology["generic"] if kw in course_text_lower)
    
    negative_hits = sum(1 for kw in ontology.get("negative", []) if kw in course_text_lower)
    
    score = (primary_hits * 0.4) + (secondary_hits * 0.2) + (generic_hits * 0.05)
    
    if negative_hits > 0:
        score = max(0.0, score - (negative_hits * 0.3))
        
    return min(1.0, score)


def calculate_quality_score(course: Dict[str, Any]) -> float:
    """Calculate normalized quality score based on rating and subscriber volume (0 to 1)."""
    rating = float(course.get("rating", 0.0))
    rating_norm = min(1.0, max(0.0, rating / 5.0))

    subs = int(course.get("num_subscribers", 0))
    if subs <= 0:
        popularity_norm = 0.5 if course.get("provider") == "Coursera" else 0.2
    else:
        popularity_norm = min(1.0, math.log10(max(10, subs)) / 6.0)

    return round(0.7 * rating_norm + 0.3 * popularity_norm, 4)


def calculate_level_suitability(course: Dict[str, Any], user_skills_count: int) -> float:
    """Evaluate how suitable the course level is given user's existing skill count."""
    level = str(course.get("level", "All Levels")).lower()

    if user_skills_count <= 1:
        if "beginner" in level or "all levels" in level:
            return 1.0
        elif "intermediate" in level:
            return 0.6
        else:
            return 0.3
    elif user_skills_count <= 4:
        if "intermediate" in level or "all levels" in level:
            return 1.0
        elif "beginner" in level:
            return 0.8
        else:
            return 0.7
    else:
        if "advanced" in level or "intermediate" in level:
            return 1.0
        elif "all levels" in level:
            return 0.8
        else:
            return 0.5


def generate_explanation(
    course: Dict[str, Any],
    skill_gap_addressed: List[str],
    target_role: str,
    score: float
) -> str:
    """Generate human-readable, explainable recommendation rationale with domain specifics."""
    resolved_target = resolve_role(target_role) or target_role
    ontology = DOMAIN_ONTOLOGY.get(resolved_target, None)
    
    course_text = _build_course_text(course).lower()
    
    if ontology:
        primary_hits = [kw for kw in ontology["primary"] if kw in course_text]
        if primary_hits:
            return f"Highly aligned with {target_role} domain, specifically covering {primary_hits[0]}."
        
        secondary_hits = [kw for kw in ontology["secondary"] if kw in course_text]
        if secondary_hits:
            return f"Aligned with {target_role} domain, incorporating elements of {secondary_hits[0]}."

    if skill_gap_addressed:
        skills_str = ", ".join(skill_gap_addressed[:3])
        return f"Recommended because it teaches {skills_str}, a missing skill for {target_role}."

    subject = course.get("subject", "technology")
    skills_covered = course.get("skills_covered", [])
    if skills_covered:
        return (
            f"Recommended because it builds core competencies ({', '.join(skills_covered[:3])}) "
            f"essential for succeeding as a {target_role}."
        )

    return (
        f"Recommended because it is a top-rated ({course.get('rating', 4.5)}★) course in {subject} "
        f"aligned with your target goal of becoming a {target_role}."
    )


def score_and_rank_courses(
    courses: List[Dict[str, Any]],
    tfidf_sims: List[float],
    target_role: str,
    user_skills: List[str],
    goal: str = "",
    top_n: int = 20,
    current_role: str = "",
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Score all courses using hybrid weights and return top ranked explainable items along with skill gap."""
    skill_gap, required_skills = compute_skill_gap(target_role, user_skills, current_role)
    relevant_subjects = get_relevant_subjects(target_role)
    relevant_subjects_lower = {s.lower() for s in relevant_subjects}

    scored_items = []
    for idx, course in enumerate(courses):
        s_tfidf = float(tfidf_sims[idx]) if idx < len(tfidf_sims) else 0.0
        course_text = _build_course_text(course)

        addressed = [s for s in skill_gap if skill_matches_text(s, course_text)]
        if skill_gap:
            s_gap = min(1.0, len(addressed) / max(1, min(3, len(skill_gap))))
        else:
            s_gap = 0.5

        course_subject = str(course.get("subject", "")).lower()
        if any(subj in course_subject or course_subject in subj for subj in relevant_subjects_lower):
            s_relevance = 1.0
        elif skill_gap and any(skill_matches_text(g, course_text) for g in skill_gap[:5]):
            s_relevance = 0.85
        else:
            s_relevance = 0.15

        s_quality = calculate_quality_score(course)
        s_level = calculate_level_suitability(course, len(user_skills))
        
        # New Domain Alignment Calculation
        s_domain_alignment = calculate_domain_alignment(course_text, target_role, skill_gap)

        current_penalty = _calculate_current_role_penalty(
            course_text=course_text,
            course_subject=course_subject,
            current_role=current_role,
            target_role=target_role,
            skill_gap=skill_gap,
            addressed=addressed,
        )

        # Hybrid formula: TF-IDF (20%), Skill Gap (30%), Domain Alignment (25%), Quality (15%), Level (10%)
        raw_score = (
            0.20 * s_tfidf +
            0.30 * s_gap +
            0.25 * s_domain_alignment +
            0.15 * s_quality +
            0.10 * s_level
        )
        final_score = round(max(0.0, raw_score - current_penalty), 4)

        skills_gained = list(course.get("skills_covered", []))
        if not skills_gained and addressed:
            skills_gained = addressed

        why_recommended = generate_explanation(course, addressed, target_role, final_score)
        ranking_explanation = {
            "course_title": course.get("title", ""),
            "s_tfidf": round(s_tfidf, 4),
            "s_gap": round(s_gap, 4),
            "s_domain_alignment": round(s_domain_alignment, 4),
            "s_quality": round(s_quality, 4),
            "s_level": round(s_level, 4),
            "s_current_role_penalty": round(current_penalty, 4),
            "final_score": final_score,
            "skill_gap_addressed": addressed,
        }

        item = {
            **course,
            "course": course,
            "score": final_score,
            "why_recommended": why_recommended,
            "skills_gained": skills_gained[:8],
            "skill_gap_addressed": addressed,
            "ranking_explanation": ranking_explanation,
        }
        scored_items.append(item)

    scored_items.sort(key=lambda x: x["score"], reverse=True)

    # Deduplicate by course title (keep highest-scoring entry)
    seen_titles: set = set()
    deduped: list = []
    for item in scored_items:
        title_key = item.get("title", "").strip().lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            deduped.append(item)

    return deduped[:top_n], skill_gap
