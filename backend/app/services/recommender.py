"""
Recommender orchestration service connecting data loaders, ML vectorizer,
hybrid scoring engine, and optional Gemini LLM enhancement.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from app.data.loader import get_all_courses
from app.data.taxonomy import JOB_ROLE_MAPPING, COMMON_SKILLS, get_target_skills, get_relevant_subjects, resolve_role, suggest_closest_roles, resolve_role_details, normalize_and_deduplicate_skills, expand_text_with_skill_synonyms
from app.data.career_understanding import CareerRoleResolutionError, career_understanding_service, is_baseline_role
from app.ml.vectorizer import CourseVectorizer
from app.ml.scoring import score_and_rank_courses, compute_skill_gap
from app.services.gemini import (
    enhance_course,
    enhance_course_explanations,
    batch_enhance_courses,
    generate_ai_courses,
    generate_personalized_roadmap
)
from app.services.gemini_client import RequestBudget

logger = logging.getLogger(__name__)


def _require_resolved_role(role: str, field_name: str = "target role") -> Dict[str, Any]:
    """Resolve a role or raise a route-safe error instead of using generic skills."""
    details = resolve_role_details(role)
    if details.get("role"):
        return details
    
    # Auto-resolve generic queries to the most likely specific career path
    if details.get("suggestions") and details.get("confidence") != "none":
        details["role"] = details["suggestions"][0]
        return details

    status_code = 503 if details.get("source") == "parser_unavailable" else 422
    raise CareerRoleResolutionError(details.get("message") or f"Invalid {field_name}.", status_code)


def _apply_course_diversity(candidates: List[Dict[str, Any]], top_n: int, skill_gap: List[str], target_details: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str, str]:
    """Select up to top_n courses from ranked candidates ensuring diverse coverage of missing skills and subjects."""
    if not candidates:
        return [], "Coverage: 0 skills.", ""

    selected: List[Dict[str, Any]] = []
    selected_titles: set = set()
    covered_skills: set = set()
    covered_subjects: set = set()
    
    # Task 5: Skill coverage optimization. Track exactly which skills are taught
    # and aggressively penalize/skip courses that duplicate already-covered skills.
    for c in candidates:
        if len(selected) >= top_n:
            break
        title = c.get("title", "")
        if title in selected_titles:
            continue

        addressed = set(c.get("skill_gap_addressed", []))
        subject = c.get("subject", "general").lower()
        
        # If the course only addresses skills we already covered, and we have enough courses, skip it
        # unless it provides a new subject and we are still building the list.
        new_skills_covered = addressed - covered_skills
        if not new_skills_covered and subject in covered_subjects and len(selected) > 0:
            continue

        selected.append(c)
        selected_titles.add(title)
        covered_skills.update(addressed)
        covered_subjects.add(subject)

    # Pass 2: Fill remaining slots if needed, ignoring overlap constraints
    if len(selected) < top_n:
        for c in candidates:
            if len(selected) >= top_n:
                break
            title = c.get("title", "")
            if title not in selected_titles:
                selected.append(c)
                selected_titles.add(title)

    # Compute skill coverage
    required_skills = set(target_details.get("required_skills", []))
    covered = set()
    for c in selected:
        covered.update(set(c.get("skill_gap_addressed", [])))
    
    coverage_score = f"{len(covered.intersection(required_skills))}/{len(required_skills)}"
    skill_coverage_str = f"Coverage: {coverage_score} skills."
    
    # Compute preparation path for missing domain courses
    categories = target_details.get("skill_categories", {})
    domain_skills = {s for s, cat in categories.items() if cat == "domain"}
    domain_covered = covered.intersection(domain_skills)
    
    preparation_path = ""
    if domain_skills and len(domain_covered) / len(domain_skills) < 0.5:
        missing_domain = list(domain_skills - domain_covered)
        preparation_path = (
            "Direct courses unavailable. Recommended preparation path: "
            f"Focus on {', '.join(missing_domain[:3])}. Consider alternative projects or domain-specific documentation."
        )

    return selected[:top_n], skill_coverage_str, preparation_path


class RecommenderService:
    """Core service for orchestrating upskilling recommendations and career paths."""

    def __init__(self):
        self.courses: List[Dict[str, Any]] = []
        self.vectorizer = CourseVectorizer(max_features=1500)
        self._is_initialized = False

    def initialize(self):
        """Load courses and pre-compute TF-IDF matrix once at startup."""
        logger.info("Initializing RecommenderService catalog and vectorizer...")
        self.courses = get_all_courses()
        self.vectorizer.fit(self.courses)
        self._is_initialized = True
        logger.info(f"RecommenderService initialized with {len(self.courses)} courses.")

    def get_platforms(self) -> List[str]:
        """Get distinct list of platforms."""
        return sorted(list({c.get("provider", "Unknown") for c in self.courses}))

    def get_skills(self) -> List[str]:
        """Get standard skill taxonomy."""
        return COMMON_SKILLS

    def get_job_roles(self) -> List[str]:
        """Get standardized job roles mapping keys."""
        return sorted(list(JOB_ROLE_MAPPING.keys()))

    def get_career_path(self, job_role: str) -> Dict[str, Any]:
        """Retrieve structured career path and skill requirements for a job role."""
        if not job_role or not job_role.strip():
            target_skills = get_target_skills(job_role)
            return {
                "current_role": job_role or "Beginner",
                "subjects": get_relevant_subjects(job_role),
                "required_skills": target_skills,
                "skills": target_skills,
                "next_roles": ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"],
                "confidence": "none",
                "source": "unresolved",
                "suggestions": ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"],
                "message": "Please enter your current role."
            }

        details = resolve_role_details(job_role)
        resolved = details.get("role")
        if resolved and resolved in JOB_ROLE_MAPPING:
            data = JOB_ROLE_MAPPING[resolved]
            return {
                "current_role": resolved,
                "subjects": data["subjects"],
                "required_skills": data["skills"],
                "skills": data["skills"],
                "next_roles": data["next_roles"],
                "confidence": details.get("confidence", "high"),
                "source": details.get("source", "exact"),
                "suggestions": details.get("suggestions", data["next_roles"]),
                "message": details.get("message", f"Resolved to {resolved}.")
            }

        if resolved:
            expanded = career_understanding_service.lookup(resolved)
            if expanded:
                return {
                    "current_role": expanded["role"],
                    "subjects": expanded["subjects"],
                    "required_skills": expanded["skills"],
                    "skills": expanded["skills"],
                    "skill_categories": expanded.get("skill_categories", {}),
                    "next_roles": expanded["next_roles"],
                    "confidence": details.get("confidence", "medium"),
                    "source": details.get("source", "expansion"),
                    "suggestions": details.get("suggestions", expanded["next_roles"]),
                    "message": details.get("message", f"Resolved to {expanded['role']}.")
                }

        job_role_clean = job_role.strip().lower()
        for role, data in JOB_ROLE_MAPPING.items():
            if role.lower() == job_role_clean:
                return {
                    "current_role": role,
                    "subjects": data["subjects"],
                    "required_skills": data["skills"],
                    "skills": data["skills"],
                    "next_roles": data["next_roles"],
                    "confidence": "high",
                    "source": "exact",
                    "suggestions": data["next_roles"],
                    "message": f"Exact match for {role}."
                }

        # If not resolved to a canonical role, suggest closest roles without inventing Senior/Lead roles
        suggestions = details.get("suggestions") or suggest_closest_roles(job_role)
        target_skills = get_target_skills(job_role)
        relevant_subjects = get_relevant_subjects(job_role)
        return {
            "current_role": job_role.strip(),
            "subjects": relevant_subjects,
            "required_skills": target_skills,
            "skills": target_skills,
            "next_roles": suggestions,
            "confidence": details.get("confidence", "none"),
            "source": details.get("source", "unresolved"),
            "suggestions": suggestions,
            "message": details.get("message", "Please clarify your target role.")
        }

    def get_recommendations(
        self, job_role: str, user_skills: List[str], goal: str = "", use_ai: bool = False, top_n: int = 10
    ) -> Tuple[List[Dict[str, Any]], List[str], str, str]:
        """
        End-to-end pipeline fetching ranked hybrid course recommendations.
        Returns: (recommendations, skill_gap, skill_coverage, preparation_path)
        """
        if not self._is_initialized:
            self.initialize()

        # Determine and validate the effective target before calling the
        # unchanged scoring pipeline. This prevents generic fallback skills
        # from being treated as a genuine career mapping.
        raw_target_role = goal.strip() if goal.strip() else job_role
        target_details = _require_resolved_role(raw_target_role)
        target_role = target_details["role"]
        current_role = job_role.strip() if goal.strip() and job_role.strip() else ""
        if current_role and not is_baseline_role(current_role):
            current_details = _require_resolved_role(current_role, field_name="current role")
            current_role = current_details["role"]

        # Normalize and deduplicate skills right at the entry boundary
        cleaned_skills = normalize_and_deduplicate_skills(user_skills)

        # Build semantic query from target role + missing skills only (never current role)
        skill_gap, required_skills = compute_skill_gap(target_role, cleaned_skills, current_role)
        query_parts = [target_role, " ".join(skill_gap)]
        base_query_text = " ".join([p for p in query_parts if p.strip()])
        query_text = expand_text_with_skill_synonyms(base_query_text)
        logger.info(
            "User Profile -> Current Role: '%s' | Target Role: '%s' | Required Skills: %s | "
            "Current Skills: %s | Skill Gap: %s | Query: '%s'",
            job_role,
            target_role,
            required_skills,
            cleaned_skills,
            skill_gap,
            query_text,
        )

        tfidf_sims = self.vectorizer.compute_similarity(query_text)
        candidate_courses, gap = score_and_rank_courses(
            courses=self.courses,
            tfidf_sims=tfidf_sims,
            target_role=target_role,
            user_skills=cleaned_skills,
            goal=goal,
            top_n=max(top_n * 3, 35),
            current_role=current_role,
        )
        
        # Recommendation Quality Gates
        filtered_candidates = []
        for c in candidate_courses:
            if c.get("ranking_explanation", {}).get("s_domain_alignment", 1.0) >= 0.40:
                filtered_candidates.append(c)
                
        if len(filtered_candidates) < 8:
            logger.info("Fewer than 8 aligned courses found, bypassing domain alignment filter")
            filtered_candidates = candidate_courses
            
        ranked_courses, skill_coverage, preparation_path = _apply_course_diversity(filtered_candidates, top_n, gap, target_details)

        if use_ai:
            logger.info("Batch enhancing top recommended courses with Gemini AI explanations (Max 2 budget)...")
            budget = RequestBudget(max_calls=2)
            top_slice = ranked_courses[:min(5, len(ranked_courses))]
            enhanced_top = batch_enhance_courses(
                courses=top_slice,
                user_skills=user_skills,
                target_role=target_role,
                skill_gaps=gap,
                budget=budget
            )
            for i, enc in enumerate(enhanced_top):
                if i < len(ranked_courses):
                    ranked_courses[i] = enc

        return ranked_courses, gap, skill_coverage, preparation_path

    def get_ai_courses(self, job_role: str, user_skills: List[str]) -> List[Dict[str, Any]]:
        """Generate entirely fresh AI course recommendations via Gemini."""
        return generate_ai_courses(job_role, user_skills)

    def get_roadmap(
        self,
        current_role: str,
        current_skills: List[str],
        target_role: str,
        skill_gaps: Optional[List[str]] = None,
        recommended_courses: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate structured personalized learning roadmap."""
        if not self._is_initialized:
            self.initialize()

        target_details = _require_resolved_role(target_role)
        target_role = target_details["role"]
        if current_role and not is_baseline_role(current_role):
            current_role = _require_resolved_role(current_role, field_name="current role")["role"]

        if skill_gaps is None:
            skill_gaps, _ = compute_skill_gap(target_role, current_skills, current_role)

        if recommended_courses is None or not recommended_courses:
            recs, _, _, _ = self.get_recommendations(
                current_role or target_role,
                current_skills,
                goal=target_role if current_role else "",
                top_n=5,
            )
            recommended_courses = [r.get("title", "") for r in recs if r.get("title")]

        return generate_personalized_roadmap(
            current_role=current_role,
            current_skills=current_skills,
            target_role=target_role,
            skill_gaps=skill_gaps,
            recommended_courses=recommended_courses
        )


# Global singleton instance managed across lifecycle
recommender_service = RecommenderService()
