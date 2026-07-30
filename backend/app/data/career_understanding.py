"""Gemini-backed parser for technology roles outside the verified taxonomy."""

import re
from typing import Any, Dict, List, Optional

from app.data.career_expansion import RoleExpansionRepository, role_expansion_repository
from app.services.gemini import _execute_gemini, _parse_gemini_json, is_gemini_available
from app.services.gemini_cache import gemini_cache


class CareerRoleResolutionError(ValueError):
    def __init__(self, detail: str, status_code: int = 422):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


_TECH_TERMS = {
    "ai", "agent", "analytics", "backend", "cloud", "computer", "data", "devops", "engineer",
    "frontend", "generative", "infrastructure", "llm", "machine", "ml", "nlp", "platform",
    "robotics", "security", "software", "sre", "technology", "vision",
}
_ROLE_TERMS = {
    "analyst", "architect", "developer", "engineer", "manager", "researcher", "scientist",
    "specialist", "sre",
}
_KNOWN_TAXONOMY_TERMS = {
    "ai", "artificial", "applied", "backend", "business", "cloud", "cybersecurity", "data",
    "developer", "devops", "digital", "engineer", "frontend", "full", "graphic", "infrastructure",
    "learning", "machine", "manager", "marketing", "ml", "product", "python", "qa", "quality", "science",
    "research", "scientist", "security", "software", "stack", "ux", "web",
}
_BASELINE_INPUTS = {"beginner", "student", "student / beginner", "student/beginner", "new graduate"}
_ALLOWED_PRIORITIES = {"critical", "high", "medium"}


def is_baseline_role(role: str) -> bool:
    return " ".join(str(role or "").strip().lower().split()) in _BASELINE_INPUTS


def is_plausible_technology_role(role: str) -> bool:
    words = set(re.findall(r"[a-z0-9+#]+", str(role or "").lower()))
    return 2 <= len(words) <= 8 and bool(words & _TECH_TERMS) and bool(words & _ROLE_TERMS)


def should_parse_before_fuzzy_match(role: str) -> bool:
    """Protect an emerging modifier such as 'Quantum' from broad fuzzy collapse."""
    words = set(re.findall(r"[a-z0-9+#]+", str(role or "").lower()))
    ignored = _ROLE_TERMS | {"senior", "lead", "junior", "principal", "staff", "of", "and", "the"}
    return is_plausible_technology_role(role) and bool(words - _KNOWN_TAXONOMY_TERMS - ignored)


def derive_subjects(skills: List[str]) -> List[str]:
    text = " ".join(skills).lower()
    subjects: List[str] = []
    if any(term in text for term in ["machine learning", "deep learning", "llm", "transformer", "vision", "nlp", "model"]):
        subjects.append("Machine Learning")
    if any(term in text for term in ["data", "sql", "statistics", "analytics", "warehouse"]):
        subjects.append("Data Science")
    if any(term in text for term in ["python", "java", "c++", "api", "software", "programming"]):
        subjects.append("Programming Languages")
    if any(term in text for term in ["cloud", "docker", "kubernetes", "linux", "terraform", "security", "devops", "observability"]):
        subjects.append("IT & Software")
    return subjects or ["IT & Software", "Programming Languages"]


class CareerUnderstandingService:
    """Resolves cached expansion roles and persists safely parsed emerging roles."""

    def __init__(self, repository: RoleExpansionRepository = role_expansion_repository):
        self.repository = repository

    def lookup(self, role_input: str) -> Optional[Dict[str, Any]]:
        return self.repository.get_by_input(role_input)

    def parse_and_cache(self, role_input: str) -> Optional[Dict[str, Any]]:
        if not is_plausible_technology_role(role_input):
            return None
        if not is_gemini_available():
            raise CareerRoleResolutionError(
                "Gemini career parsing is unavailable; retry this emerging role later.", status_code=503
            )

        cache_key = gemini_cache.hash_key("career_role_parser", role_input)
        prompt = f"""
You are a career parser and validator. Analyze this technology career role input:
Role input: {role_input!r}

Check the following:
1. Does the role represent a real industry position?
2. Are extracted skills relevant?
3. Are skills logically connected?
4. Does career progression make sense?
5. Is the domain learning path viable?

Return JSON only in exactly this shape:
{{
  "valid_role": true,
  "canonical_role": "Title Case technology role",
  "required_skills": [
    {{
      "skill": "skill name",
      "priority": "critical|high|medium",
      "category": "foundation|domain|tool|production"
    }}
  ],
  "career_progression": ["next role"],
  "passes_validation": true
}}

Rules: reject nonsense and non-technology careers with valid_role=false and passes_validation=false. For a valid role return 3-12 distinct technical skills and 2-4 realistic technology progression roles. Categorize each skill accurately into foundation, domain, tool, or production. Do not return Markdown.
"""
        try:
            response_text = _execute_gemini(prompt, purpose="career_role_parser", cache_key=cache_key)
            data = _parse_gemini_json(response_text or "")
        except Exception as exc:
            raise CareerRoleResolutionError("Could not validate this emerging career role.") from exc

        profile = self._validate_parser_response(data)
        if not profile:
            return None
        return self.repository.upsert_profile(profile, source="dynamic", aliases=[role_input])

    @staticmethod
    def _validate_parser_response(data: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(data, dict) or data.get("valid_role") is not True:
            return None
        
        # New multi-step validation requirement from prompt
        is_approved = data.get("passes_validation") is True

        role = str(data.get("canonical_role", "")).strip()
        requirements = data.get("required_skills")
        progression = data.get("career_progression")
        if not is_plausible_technology_role(role) or not isinstance(requirements, list) or not isinstance(progression, list):
            return None
        if not 3 <= len(requirements) <= 12 or not 2 <= len(progression) <= 4:
            return None

        skills = []
        seen = set()
        for item in requirements:
            if not isinstance(item, dict):
                return None
            skill = str(item.get("skill", "")).strip()
            priority = str(item.get("priority", "")).strip().lower()
            category = str(item.get("category", "domain")).strip().lower()
            
            if not 2 <= len(skill) <= 60 or priority not in _ALLOWED_PRIORITIES or skill.lower() in seen:
                return None
            seen.add(skill.lower())
            # Store tuple of (skill, priority, category)
            skills.append((skill, priority, category))
            
        next_roles = [str(value).strip() for value in progression]
        if any(not 2 <= len(value) <= 80 for value in next_roles) or len(set(value.lower() for value in next_roles)) != len(next_roles):
            return None
            
        return {
            "role": role, 
            "subjects": derive_subjects([skill for skill, _, _ in skills]), 
            "skills": skills, 
            "next_roles": next_roles,
            "validation_status": "approved" if is_approved else "pending"
        }


career_understanding_service = CareerUnderstandingService()
