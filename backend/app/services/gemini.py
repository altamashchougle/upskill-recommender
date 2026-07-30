"""
Gemini LLM business logic service for AI-enhanced course explanations, dynamic course generation,
and structured personalized learning roadmaps.
Separated from API communication (`gemini_client.py`), model routing (`model_router.py`), and caching (`gemini_cache.py`).
Includes proxy support for legacy monkeypatch compatibility during unit tests (`test_gemini.py`).
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from app.services.model_router import model_router, GEMINI_MODEL_PRIORITY
from app.services.gemini_cache import gemini_cache
from app.services.gemini_client import gemini_client, RequestBudget
from app.data.taxonomy import resolve_role, JOB_ROLE_MAPPING

logger = logging.getLogger(__name__)


class _GeminiProxy:
    """Proxy class to represent production Gemini router/client state while supporting legacy monkeypatching."""
    pass


# Global singleton target for backward compatibility / test monkeypatching
gemini_model = _GeminiProxy()


def initialize_gemini() -> bool:
    """Initialize or verify Gemini AI availability and models from environment."""
    global gemini_model
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    logger.info(f"GEMINI_API_KEY exists: {bool(api_key)}")
    logger.info(f"Key length: {len(api_key)}")

    available = model_router._verify_available_models(force=True)
    if available:
        logger.info(f"Gemini AI integration initialized successfully. Prioritized available models: {available}")
        if gemini_model is None:
            gemini_model = _GeminiProxy()
        return True
    else:
        logger.info("GEMINI_API_KEY not configured or no models verified. Running in deterministic ML mode.")
        if gemini_model is None:
            gemini_model = _GeminiProxy()
        return False


# Initialize immediately upon module load
initialize_gemini()


def is_gemini_available() -> bool:
    """Check if Gemini models are active and configured (`Part 5`), respecting test monkeypatches."""
    global gemini_model
    if gemini_model is None:
        return False
    if not isinstance(gemini_model, _GeminiProxy):
        # Directly monkeypatched by test to a mock object
        return True
    return len(model_router.get_available_models()) > 0


def _execute_gemini(
    prompt: str,
    purpose: str = "generation",
    cache_key: Optional[str] = None,
    budget: Optional[RequestBudget] = None
) -> Optional[str]:
    """Execute prompt via gemini_client or direct monkeypatched gemini_model."""
    global gemini_model
    if gemini_model is None:
        return None
    if not isinstance(gemini_model, _GeminiProxy):
        # Directly monkeypatched mock object during unit test (`test_gemini.py`)
        try:
            response = gemini_model.generate_content(prompt)
            return getattr(response, "text", "") or ""
        except Exception as e:
            logger.warning(f"Monkeypatched gemini_model execution failed: {e}")
            raise

    return gemini_client.execute(
        prompt=prompt,
        purpose=purpose,
        cache_key=cache_key,
        budget=budget
    )


def _parse_gemini_json(response_text: str) -> Dict[str, Any]:
    """Parse JSON cleanly from Gemini response, stripping markdown fences or conversational preambles."""
    if not response_text or not isinstance(response_text, str):
        return {}
    text = response_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, (dict, list)) else {}
    except json.JSONDecodeError:
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        arr_start = text.find("[")
        arr_end = text.rfind("]")

        if obj_start != -1 and obj_end != -1 and (arr_start == -1 or obj_start < arr_start):
            try:
                data = json.loads(text[obj_start : obj_end + 1])
                return data if isinstance(data, (dict, list)) else {}
            except Exception:
                pass
        elif arr_start != -1 and arr_end != -1:
            try:
                data = json.loads(text[arr_start : arr_end + 1])
                return data if isinstance(data, (dict, list)) else {}
            except Exception:
                pass
        raise


def _fallback_roadmap(
    current_role: str,
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    recommended_courses: List[str]
) -> Dict[str, Any]:
    """Generate deterministic, high-quality structured learning roadmap fallback when Gemini is unavailable (`Part 4`)."""
    gaps = skill_gaps if skill_gaps else ["Core Domain Skills", "System Architecture", "Advanced Tools"]
    courses_str = ", ".join(recommended_courses[:2]) if recommended_courses else f"top {target_role} courses"
    resolved = resolve_role(target_role) or target_role

    future_roles = JOB_ROLE_MAPPING.get(resolved, {}).get("next_roles") or [f"Senior {target_role}", f"Lead {target_role}", f"{target_role} Architect"]

    if resolved in {"AI Research Scientist", "ML Research Scientist", "Applied Scientist", "Research Engineer"}:
        roadmap_phases = [
            {
                "phase": "Month 1: Mathematical Foundations",
                "duration": "4 weeks",
                "skills_to_learn": ["Linear Algebra", "Probability", "Statistics", "Optimization"],
                "recommended_actions": f"Enroll in {courses_str}. Master core mathematical foundations and probability."
            },
            {
                "phase": "Month 2: Deep Learning Research",
                "duration": "4 weeks",
                "skills_to_learn": ["PyTorch", "Neural Networks", "CNN", "Transformers"],
                "recommended_actions": "Deep dive into PyTorch and custom neural network architectures."
            },
            {
                "phase": "Month 3: Modern AI Research",
                "duration": "4 weeks",
                "skills_to_learn": ["LLMs", "Diffusion Models", "Reinforcement Learning"],
                "recommended_actions": "Study advanced models and reinforcement learning techniques."
            },
            {
                "phase": "Month 4: Research Portfolio",
                "duration": "4 weeks",
                "skills_to_learn": ["Papers", "Reproduction studies", "Open source contributions"],
                "recommended_actions": "Reproduce a state-of-the-art research paper and prepare a portfolio."
            }
        ]
    elif resolved == "AI Engineer":
        roadmap_phases = [
            {
                "phase": "Month 1: ML Engineering Fundamentals",
                "duration": "4 weeks",
                "skills_to_learn": gaps[:max(1, len(gaps)//3)] or ["Python for AI", "Data Pipelines", "API Integration"],
                "recommended_actions": f"Enroll in {courses_str}. Build robust data processing pipelines and core AI engineering workflows."
            },
            {
                "phase": "Month 2: Deep Learning",
                "duration": "4 weeks",
                "skills_to_learn": gaps[max(1, len(gaps)//3):max(2, 2*len(gaps)//3)] or ["Transformers", "PyTorch", "Fine-tuning"],
                "recommended_actions": "Integrate pretrained transformer models and fine-tune specialized models on domain datasets."
            },
            {
                "phase": "Month 3: Deployment and MLOps",
                "duration": "4 weeks",
                "skills_to_learn": gaps[max(2, 2*len(gaps)//3):] or ["Model Serving", "Docker", "LLMOps"],
                "recommended_actions": "Deploy scalable AI models to production using Docker, FastAPI, and cloud serving platforms with monitoring."
            },
        ]
    elif resolved == "Machine Learning Engineer":
        roadmap_phases = [
            {
                "phase": "Month 1: Machine Learning Foundations",
                "duration": "4 weeks",
                "skills_to_learn": gaps[:max(1, len(gaps)//3)] or ["Feature Engineering", "Scikit-Learn", "Model Evaluation"],
                "recommended_actions": f"Enroll in {courses_str}. Master feature engineering, model selection, and validation strategies."
            },
            {
                "phase": "Month 2: Model Engineering",
                "duration": "4 weeks",
                "skills_to_learn": gaps[max(1, len(gaps)//3):max(2, 2*len(gaps)//3)] or ["Deep Learning", "Distributed Training", "PyTorch"],
                "recommended_actions": "Scale training routines using PyTorch, GPU acceleration, and distributed model optimization techniques."
            },
            {
                "phase": "Month 3: Production ML Systems",
                "duration": "4 weeks",
                "skills_to_learn": gaps[max(2, 2*len(gaps)//3):] or ["ML Pipelines", "Kubernetes", "Model Deployment"],
                "recommended_actions": "Build end-to-end automated ML training and inference pipelines with continuous CI/CD deployment."
            }
        ]
    elif resolved == "LLM Engineer":
        roadmap_phases = [
            {
                "phase": "Month 1: NLP Foundations",
                "duration": "4 weeks",
                "skills_to_learn": ["Transformers", "Attention", "Embeddings"],
                "recommended_actions": f"Enroll in {courses_str}. Understand the core mechanics of attention and word embeddings."
            },
            {
                "phase": "Month 2: LLM Application Engineering",
                "duration": "4 weeks",
                "skills_to_learn": ["RAG", "Vector Databases", "Prompt Engineering"],
                "recommended_actions": "Build advanced retrieval-augmented generation systems using vector databases."
            },
            {
                "phase": "Month 3: LLMOps",
                "duration": "4 weeks",
                "skills_to_learn": ["Evaluation", "Monitoring", "Deployment"],
                "recommended_actions": "Deploy and evaluate language models in production environments."
            }
        ]
    elif resolved == "Autonomous Driving Engineer":
        roadmap_phases = [
            {
                "phase": "Month 1: Robotics Foundations",
                "duration": "4 weeks",
                "skills_to_learn": ["C++", "Python", "Linear Algebra", "Data Structures", "Control Systems"],
                "recommended_actions": f"Enroll in {courses_str}. Master foundational mathematics and robust C++ programming."
            },
            {
                "phase": "Month 2: Computer Vision + Perception",
                "duration": "4 weeks",
                "skills_to_learn": ["Computer Vision", "Deep Learning", "Object Detection", "OpenCV", "Sensor Fusion"],
                "recommended_actions": "Build perception systems utilizing deep learning and sensor fusion."
            },
            {
                "phase": "Month 3: Planning + Control",
                "duration": "4 weeks",
                "skills_to_learn": ["ROS", "SLAM", "Path Planning", "Motion Control", "LiDAR", "Radar"],
                "recommended_actions": "Develop algorithms for trajectory planning and motion control."
            },
            {
                "phase": "Month 4: Simulation + Deployment",
                "duration": "4 weeks",
                "skills_to_learn": ["CARLA Simulation", "Embedded Systems", "Real-time Systems", "Deployment"],
                "recommended_actions": "Test control systems in CARLA simulators and deploy to embedded architectures."
            }
        ]
    elif resolved == "Quantum ML Engineer":
        roadmap_phases = [
            {
                "phase": "Month 1: Quantum Computing Foundations",
                "duration": "4 weeks",
                "skills_to_learn": ["Quantum Computing", "Qubits", "Quantum Mechanics"],
                "recommended_actions": f"Enroll in {courses_str}. Grasp the fundamentals of quantum states."
            },
            {
                "phase": "Month 2: Quantum Algorithms",
                "duration": "4 weeks",
                "skills_to_learn": ["Shor's Algorithm", "Grover's Algorithm", "Quantum Circuits"],
                "recommended_actions": "Implement core quantum algorithms."
            },
            {
                "phase": "Month 3: Quantum ML Frameworks",
                "duration": "4 weeks",
                "skills_to_learn": ["Qiskit", "PennyLane", "Quantum Neural Networks"],
                "recommended_actions": "Train machine learning models on simulated quantum frameworks."
            },
            {
                "phase": "Month 4: Research Projects",
                "duration": "4 weeks",
                "skills_to_learn": ["VQA", "Quantum Optimization", "Research"],
                "recommended_actions": "Apply quantum algorithms to complex optimization research problems."
            }
        ]
    else:
        phase1_skills = gaps[:max(1, len(gaps)//2)]
        phase2_skills = gaps[max(1, len(gaps)//2):] if len(gaps) > 1 else gaps
        roadmap_phases = [
            {
                "phase": "Phase 1: Foundation & Core Gaps",
                "duration": "4-6 weeks",
                "skills_to_learn": phase1_skills,
                "recommended_actions": f"Enroll in {courses_str}. Build small hands-on exercises practicing {', '.join(phase1_skills[:3])}."
            },
            {
                "phase": "Phase 2: Advanced Mastery & Integration",
                "duration": "6-8 weeks",
                "skills_to_learn": phase2_skills,
                "recommended_actions": f"Complete end-to-end projects implementing {', '.join(phase2_skills[:3])}. Contribute to open-source or internal tools."
            },
            {
                "phase": "Phase 3: Real-World Portfolio & Interview Readiness",
                "duration": "3-4 weeks",
                "skills_to_learn": [f"{target_role} System Design", "Production Deployment", "Best Practices"],
                "recommended_actions": f"Prepare a capstone portfolio demonstrating transition from {current_role} to {target_role}. Practice technical interviews."
            }
        ]

    return {
        "roadmap": roadmap_phases,
        "career_advice": f"Leverage your background in {current_role} (especially {', '.join(current_skills[:3]) if current_skills else 'your existing foundations'}) while systematically closing gaps in {', '.join(gaps[:3])}. Focus on shipping real projects rather than just watching video tutorials.",
        "future_roles": future_roles
    }


def generate_personalized_roadmap(
    current_role: str,
    current_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    recommended_courses: List[str],
    budget: Optional[RequestBudget] = None
) -> Dict[str, Any]:
    """Generate a comprehensive, structured personalized learning roadmap using Gemini LLM (`CALL 1`) or fallback."""
    logger.info("GEMINI REQUEST STARTED: generate_personalized_roadmap")
    if not is_gemini_available():
        logger.info("USING FALLBACK: Gemini model unavailable for generate_personalized_roadmap")
        return _fallback_roadmap(current_role, current_skills, target_role, skill_gaps, recommended_courses)

    cache_key = gemini_cache.hash_key(
        "roadmap",
        current_role,
        current_skills,
        target_role,
        skill_gaps,
        recommended_courses[:5]
    )

    resolved = resolve_role(target_role) or target_role
    role_instruction = ""
    if resolved in {"AI Research Scientist", "ML Research Scientist", "Applied Scientist", "Research Engineer", "Autonomous Driving Engineer", "Quantum ML Engineer", "AI Engineer"}:
        role_instruction = "\nIMPORTANT: Structure the roadmap into exactly 4 phases tailored to the specific domain requirements."
    elif resolved in {"Machine Learning Engineer", "LLM Engineer"}:
        role_instruction = "\nIMPORTANT: Structure the roadmap into exactly 3 phases tailored to the specific domain requirements."
    else:
        role_instruction = "\nIMPORTANT: Structure the roadmap into 3-4 phases highly specific to the domain of the target role."

    prompt = f"""
Create a detailed, actionable personalized learning roadmap for a professional upskilling career transition.
Current Role: {current_role}
Current Skills: {', '.join(current_skills) if current_skills else 'None specified'}
Target Career Role: {target_role}
Identified Skill Gaps: {', '.join(skill_gaps) if skill_gaps else 'General domain mastery'}
Recommended Courses: {', '.join(recommended_courses[:5]) if recommended_courses else 'Standard online curriculum'}{role_instruction}

Return ONLY valid JSON exactly matching this schema (no markdown formatting outside JSON block):
{{
  "roadmap": [
    {{
      "phase": "Month 1: [Domain Specific Title, e.g. Programming + AI Foundations]",
      "duration": "4-6 weeks",
      "skills_to_learn": ["Specific Skill 1", "Specific Skill 2", "Specific Skill 3"],
      "recommended_actions": "Actionable study steps and hands-on practice recommendations."
    }},
    {{
      "phase": "Month 2: [Domain Specific Title, e.g. Computer Vision and Deep Learning]",
      "duration": "6-8 weeks",
      "skills_to_learn": ["Specific Skill 4", "Specific Skill 5"],
      "recommended_actions": "Deep dive coursework and end-to-end portfolio building."
    }}
  ],
  "career_advice": "Two sentences of strategic career advice on bridging from {current_role} to {target_role}.",
  "future_roles": ["Senior {target_role}", "Lead {target_role}", "{target_role} Architect"]
}}
"""
    try:
        response_text = _execute_gemini(
            prompt=prompt,
            purpose="generate_personalized_roadmap",
            cache_key=cache_key,
            budget=budget
        )
        if not response_text:
            logger.info("USING FALLBACK: No response text returned from gemini_client")
            return _fallback_roadmap(current_role, current_skills, target_role, skill_gaps, recommended_courses)

        data = _parse_gemini_json(response_text)
        if isinstance(data, dict) and "roadmap" in data and isinstance(data["roadmap"], list) and len(data["roadmap"]) > 0:
            return data
        logger.warning("Gemini returned JSON but missing 'roadmap' list or invalid format, using fallback.")
        return _fallback_roadmap(current_role, current_skills, target_role, skill_gaps, recommended_courses)
    except Exception as e:
        logger.warning(f"Gemini roadmap generation failed ({type(e).__name__}: {e}). Using deterministic fallback.")
        return _fallback_roadmap(current_role, current_skills, target_role, skill_gaps, recommended_courses)


def batch_enhance_courses(
    courses: List[Dict[str, Any]],
    user_skills: List[str],
    target_role: str,
    skill_gaps: List[str],
    budget: Optional[RequestBudget] = None
) -> List[Dict[str, Any]]:
    """
    Batch enhance up to 5 top recommended courses in a single Gemini API request (`CALL 2 / Part 7`).
    Replaces individual per-course loops to keep total request budget below <= 2 calls.
    """
    for course in courses:
        addressed = course.get("skill_gap_addressed", [])
        skills_str = ", ".join(addressed) if addressed else ", ".join(course.get("skills_covered", [])[:3])
        course["ai_why_fit"] = course.get("why_recommended", f"Teaches core {course.get('subject', 'technology')} competencies aligned with {target_role}.")
        course["ai_gap_solved"] = f"Directly addresses: {skills_str}" if skills_str else f"Provides foundational preparation for {target_role}."
        course["ai_expected_outcome"] = f"Gain practical mastery over {skills_str or course.get('subject', 'key domain tools')} to accelerate your career transition."
        if "ai_description" not in course:
            course["ai_description"] = course.get("description", "")
        if "ai_learning_outcomes" not in course:
            course["ai_learning_outcomes"] = [f"Master {s}" for s in course.get("skills_covered", [])[:3]]

    if not courses:
        return courses

    logger.info("GEMINI REQUEST STARTED: batch_enhance_courses")
    if not is_gemini_available() or (budget is not None and not budget.can_call()):
        logger.info("USING FALLBACK: Gemini unavailable or request budget exceeded for batch_enhance_courses")
        return courses

    batch_target = courses[:min(5, len(courses))]
    batch_payload = []
    for idx, c in enumerate(batch_target):
        batch_payload.append({
            "course_id": str(idx),
            "title": c.get("title", ""),
            "skills": c.get("skills_covered", [])[:4],
            "description": (c.get("description") or "")[:200]
        })

    cache_key = gemini_cache.hash_key(
        "batch_courses",
        target_role,
        user_skills,
        skill_gaps,
        [c.get("title") for c in batch_target]
    )

    prompt = f"""
Analyze these {len(batch_payload)} online courses for a professional transitioning to {target_role}.
User Current Skills: {', '.join(user_skills) if user_skills else 'Beginner'}
User Missing Skill Gaps: {', '.join(skill_gaps) if skill_gaps else 'Domain fundamentals'}
Courses Summary:
{json.dumps(batch_payload, indent=2)}

Return ONLY valid JSON array with exactly {len(batch_payload)} objects matching this structure:
[
  {{
    "course_id": "0",
    "why_fit": "Why this specific course fits the user's background and target goal (1-2 sentences).",
    "skills_solved": ["Skill 1", "Skill 2"],
    "expected_outcome": "Practical competency gained and what they will be able to demonstrate after completion."
  }}
]
"""
    try:
        response_text = _execute_gemini(
            prompt=prompt,
            purpose="batch_enhance_courses",
            cache_key=cache_key,
            budget=budget
        )
        if not response_text:
            return courses

        parsed_list = _parse_gemini_json(response_text)
        if isinstance(parsed_list, dict) and "courses" in parsed_list:
            parsed_list = parsed_list["courses"]

        if isinstance(parsed_list, list):
            for item in parsed_list:
                if not isinstance(item, dict):
                    continue
                cid_str = str(item.get("course_id", "")).strip()
                if cid_str.isdigit() and int(cid_str) < len(courses):
                    idx = int(cid_str)
                    courses[idx]["ai_enhanced"] = True
                    courses[idx]["ai_why_fit"] = item.get("why_fit", courses[idx]["ai_why_fit"])
                    solved = item.get("skills_solved", [])
                    if solved:
                        courses[idx]["ai_gap_solved"] = f"Directly addresses: {', '.join(solved) if isinstance(solved, list) else str(solved)}"
                    courses[idx]["ai_expected_outcome"] = item.get("expected_outcome", courses[idx]["ai_expected_outcome"])
    except Exception as e:
        logger.warning(f"Batch course enhancement failed: {e}. Preserving rule-enhanced defaults.")

    return courses


def enhance_course(course: Dict[str, Any]) -> Dict[str, Any]:
    """Single course enhancement wrapper (`enhance_course`) kept for backward compatibility and single unit tests."""
    logger.info("GEMINI REQUEST STARTED: enhance_course")
    if not is_gemini_available():
        if "ai_description" not in course:
            course["ai_description"] = course.get("description", "")
        if "ai_learning_outcomes" not in course:
            course["ai_learning_outcomes"] = [f"Master {s}" for s in course.get("skills_covered", [])[:3]]
        return course

    prompt = f"""
Analyze this online course and return structured JSON only:
Title: {course.get('title')}
Description: {course.get('description')}
Subject: {course.get('subject')}
Level: {course.get('level')}

Return exactly this JSON structure (no markdown formatting outside JSON block):
{{
    "ai_description": "A concise 2-sentence professional overview of what this course teaches and its career value.",
    "ai_learning_outcomes": [
        "Outcome 1: specific skill or concept mastered",
        "Outcome 2: practical application or tool learned",
        "Outcome 3: career competency gained"
    ]
}}
"""
    try:
        response_text = _execute_gemini(prompt=prompt, purpose="enhance_course")
        if not response_text:
            raise ValueError("No response text")
        data = _parse_gemini_json(response_text)
        if not isinstance(data, dict):
            raise ValueError("Expected dictionary from Gemini response")
        course["ai_enhanced"] = True
        course["ai_description"] = data.get("ai_description", course.get("description", ""))
        course["ai_learning_outcomes"] = data.get("ai_learning_outcomes", [])
    except Exception as e:
        logger.warning(f"Gemini course enhancement failed: {e}")
        course["ai_enhanced"] = False
        if "ai_description" not in course:
            course["ai_description"] = course.get("description", "")
        if "ai_learning_outcomes" not in course:
            course["ai_learning_outcomes"] = [f"Master {s}" for s in course.get("skills_covered", [])[:3]]
    return course


def enhance_course_explanations(
    course: Dict[str, Any],
    user_skills: List[str],
    target_role: str,
    skill_gaps: List[str]
) -> Dict[str, Any]:
    """Single course explanation wrapper kept for backward compatibility and single unit tests."""
    addressed = course.get("skill_gap_addressed", [])
    skills_str = ", ".join(addressed) if addressed else ", ".join(course.get("skills_covered", [])[:3])
    course["ai_why_fit"] = course.get("why_recommended", f"Teaches core {course.get('subject', 'technology')} competencies aligned with {target_role}.")
    course["ai_gap_solved"] = f"Directly addresses: {skills_str}" if skills_str else f"Provides foundational preparation for {target_role}."
    course["ai_expected_outcome"] = f"Gain practical mastery over {skills_str or course.get('subject', 'key domain tools')} to accelerate your career transition."

    if not is_gemini_available():
        return course

    prompt = f"""
Analyze how this course helps a professional transition to {target_role}.
Course Title: {course.get('title')}
Course Description: {course.get('description')}
Course Subject: {course.get('subject')}
User Current Skills: {', '.join(user_skills) if user_skills else 'Beginner'}
User Missing Skill Gaps: {', '.join(skill_gaps) if skill_gaps else 'Domain fundamentals'}

Return ONLY valid JSON with exactly these 3 fields:
{{
  "ai_why_fit": "Why this specific course fits the user's background and target goal (1-2 sentences).",
  "ai_gap_solved": "What exact skill gap from their missing competencies this course solves.",
  "ai_expected_outcome": "Expected practical outcome and what competency they will be able to demonstrate after completion."
}}
"""
    try:
        response_text = _execute_gemini(prompt=prompt, purpose="enhance_course_explanations")
        if not response_text:
            raise ValueError("No response text")
        data = _parse_gemini_json(response_text)
        if not isinstance(data, dict):
            raise ValueError("Expected dictionary from Gemini explanation response")
        course["ai_enhanced"] = True
        course["ai_why_fit"] = data.get("ai_why_fit", course["ai_why_fit"])
        course["ai_gap_solved"] = data.get("ai_gap_solved", course["ai_gap_solved"])
        course["ai_expected_outcome"] = data.get("ai_expected_outcome", course["ai_expected_outcome"])
    except Exception as e:
        logger.warning(f"Gemini course explanation enhancement failed: {e}")
    return course


def generate_ai_courses(job_role: str, user_skills: List[str], budget: Optional[RequestBudget] = None) -> List[Dict[str, Any]]:
    """Generate dynamic AI-recommended courses tailored to user role and skills."""
    logger.info("GEMINI REQUEST STARTED: generate_ai_courses")
    if not is_gemini_available() or (budget is not None and not budget.can_call()):
        logger.info("USING FALLBACK: Gemini unavailable or request budget exceeded for generate_ai_courses")
        return []

    skills_str = ", ".join(user_skills) if user_skills else "none specified"
    cache_key = gemini_cache.hash_key("generate_ai_courses", job_role, user_skills)
    prompt = f"""
The user wants to become a: {job_role}
Their current skills: {skills_str}

Suggest exactly 3 ideal online courses (can be real popular courses from Coursera, Udemy, or edX) that directly bridge their skill gap to become a successful {job_role}.

Return ONLY valid JSON with this exact schema:
{{
  "courses": [
    {{
      "title": "Exact Course Title",
      "provider": "Coursera or Udemy or edX",
      "url": "https://www.coursera.org or https://www.udemy.com",
      "is_paid": false,
      "price": 0,
      "num_subscribers": 50000,
      "level": "Intermediate",
      "duration": "20 hours",
      "subject": "Domain Subject",
      "description": "Why this course is essential for {job_role}.",
      "popularity_score": 90.0,
      "platform": "coursera",
      "rating": 4.8,
      "university": "Offering University if any",
      "skills_covered": ["Skill1", "Skill2", "Skill3"],
      "ai_enhanced": true,
      "ai_description": "Detailed AI insight into why this course closes their gap.",
      "ai_learning_outcomes": ["Master X", "Build Y", "Apply Z"],
      "ai_why_fit": "Why this course fits their current skill level.",
      "ai_gap_solved": "Exact missing skills this course teaches.",
      "ai_expected_outcome": "Practical competency gained."
    }}
  ]
}}
"""
    try:
        response_text = _execute_gemini(
            prompt=prompt,
            purpose="generate_ai_courses",
            cache_key=cache_key,
            budget=budget
        )
        if not response_text:
            return []
        data = _parse_gemini_json(response_text)
        if isinstance(data, dict):
            return data.get("courses", [])[:3]
        elif isinstance(data, list):
            return data[:3]
        return []
    except Exception as e:
        logger.warning(f"Gemini AI courses generation failed: {e}")
        return []
