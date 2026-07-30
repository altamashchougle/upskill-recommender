"""Persistent role-expansion profiles for emerging technology careers."""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def normalize_role_key(value: str) -> str:
    """Produce a stable lookup key for a user-entered career title."""
    return " ".join(str(value or "").strip().lower().split())


ROLE_EXPANSIONS: List[Dict[str, Any]] = [
    {"role": "LLM Engineer", "aliases": ["llm engineer", "large language model engineer"], "subjects": ["Machine Learning", "Programming Languages", "IT & Software"], "skills": [("Python", "critical"), ("Transformers", "critical"), ("LLMs", "critical"), ("Prompt Engineering", "high"), ("RAG", "high"), ("Vector Databases", "high"), ("FastAPI", "medium"), ("LLMOps", "medium")], "next_roles": ["Senior LLM Engineer", "AI Architect", "AI Engineering Manager"]},
    {"role": "Generative AI Engineer", "aliases": ["gen ai engineer", "genai engineer", "generative ai developer"], "subjects": ["Machine Learning", "Programming Languages", "IT & Software"], "skills": [("Python", "critical"), ("Deep Learning", "critical"), ("Transformers", "critical"), ("LLMs", "critical"), ("Prompt Engineering", "high"), ("RAG", "high"), ("Vector Databases", "high"), ("MLOps", "medium")], "next_roles": ["Senior Generative AI Engineer", "AI Architect", "AI Engineering Manager"]},
    {"role": "AI Agent Engineer", "aliases": ["ai agent engineer", "agentic ai engineer", "ai agents engineer"], "subjects": ["Machine Learning", "Programming Languages", "IT & Software"], "skills": [("Python", "critical"), ("LLMs", "critical"), ("Prompt Engineering", "critical"), ("AI Agents", "critical"), ("Tool Calling", "high"), ("RAG", "high"), ("Vector Databases", "high"), ("LLMOps", "medium")], "next_roles": ["Senior AI Agent Engineer", "AI Architect", "AI Engineering Manager"]},
    {"role": "Computer Vision Engineer", "aliases": ["computer vision engineer", "cv engineer", "vision engineer"], "subjects": ["Machine Learning", "Data Science", "Programming Languages"], "skills": [("Python", "critical"), ("Computer Vision", "critical"), ("Deep Learning", "critical"), ("PyTorch", "high"), ("OpenCV", "high"), ("CNNs", "high"), ("Object Detection", "medium"), ("Model Deployment", "medium")], "next_roles": ["Senior Computer Vision Engineer", "AI Architect", "Computer Vision Lead"]},
    {"role": "NLP Engineer", "aliases": ["nlp engineer", "natural language processing engineer"], "subjects": ["Machine Learning", "Data Science", "Programming Languages"], "skills": [("Python", "critical"), ("NLP", "critical"), ("Machine Learning", "critical"), ("Transformers", "high"), ("Deep Learning", "high"), ("PyTorch", "high"), ("Text Classification", "medium"), ("LLMs", "medium")], "next_roles": ["Senior NLP Engineer", "AI Architect", "NLP Lead"]},
    {"role": "AI Safety Engineer", "aliases": ["ai safety engineer", "responsible ai engineer", "ai alignment engineer"], "subjects": ["Machine Learning", "Data Science", "IT & Software"], "skills": [("Python", "critical"), ("Machine Learning", "critical"), ("AI Safety", "critical"), ("Responsible AI", "high"), ("Model Evaluation", "high"), ("Red Teaming", "high"), ("LLMs", "medium"), ("AI Governance", "medium")], "next_roles": ["Senior AI Safety Engineer", "Responsible AI Lead", "AI Governance Architect"]},
    {"role": "Robotics AI Engineer", "aliases": ["robotics ai engineer", "robotics engineer", "robotics ml engineer"], "subjects": ["Machine Learning", "Programming Languages", "IT & Software"], "skills": [("Python", "critical"), ("Robotics", "critical"), ("C++", "high"), ("Computer Vision", "high"), ("ROS", "high"), ("Reinforcement Learning", "high"), ("Sensor Fusion", "medium"), ("SLAM", "medium")], "next_roles": ["Senior Robotics AI Engineer", "Robotics Architect", "Robotics AI Lead"]},
    {"role": "Data Engineer", "aliases": ["data engineer", "data eng"], "subjects": ["Data Science", "IT & Software", "Programming Languages"], "skills": [("SQL", "critical"), ("Python", "critical"), ("ETL", "critical"), ("Data Modeling", "high"), ("Data Warehousing", "high"), ("Apache Spark", "high"), ("Airflow", "medium"), ("Cloud Computing", "medium")], "next_roles": ["Senior Data Engineer", "Data Architect", "Data Engineering Manager"]},
    {"role": "Analytics Engineer", "aliases": ["analytics engineer", "analytics eng"], "subjects": ["Data Science", "Business", "IT & Software"], "skills": [("SQL", "critical"), ("Data Modeling", "critical"), ("Data Warehousing", "high"), ("dbt", "high"), ("BI", "high"), ("Git", "medium"), ("Data Quality", "medium"), ("Python", "medium")], "next_roles": ["Senior Analytics Engineer", "Analytics Architect", "Data Platform Lead"]},
    {"role": "ML Analyst", "aliases": ["ml analyst", "machine learning analyst"], "subjects": ["Data Science", "Machine Learning", "Business"], "skills": [("SQL", "critical"), ("Python", "critical"), ("Statistics", "critical"), ("Data Analysis", "high"), ("Machine Learning", "high"), ("Data Visualization", "high"), ("Scikit-learn", "medium"), ("A/B Testing", "medium")], "next_roles": ["Senior ML Analyst", "Data Scientist", "Analytics Manager"]},
    {"role": "BI Engineer", "aliases": ["bi engineer", "business intelligence engineer"], "subjects": ["Data Science", "Business", "IT & Software"], "skills": [("SQL", "critical"), ("Data Modeling", "critical"), ("Power BI", "high"), ("Tableau", "high"), ("Data Warehousing", "high"), ("ETL", "medium"), ("DAX", "medium"), ("Data Visualization", "medium")], "next_roles": ["Senior BI Engineer", "BI Architect", "Analytics Manager"]},
    {"role": "Backend Engineer", "aliases": ["backend engineer", "back end engineer"], "subjects": ["Web Development", "Programming Languages", "IT & Software"], "skills": [("Python", "critical"), ("SQL", "critical"), ("REST APIs", "critical"), ("Microservices", "high"), ("System Design", "high"), ("Docker", "high"), ("NoSQL", "medium"), ("Unit Testing", "medium")], "next_roles": ["Senior Backend Engineer", "Backend Architect", "Staff Engineer"]},
    {"role": "Cloud Engineer", "aliases": ["cloud engineer"], "subjects": ["IT & Software", "Programming Languages"], "skills": [("Cloud Computing", "critical"), ("AWS", "critical"), ("Linux", "high"), ("Networking", "high"), ("Docker", "high"), ("Kubernetes", "medium"), ("Terraform", "medium"), ("Security", "medium")], "next_roles": ["Senior Cloud Engineer", "Cloud Architect", "Infrastructure Director"]},
    {"role": "Platform Engineer", "aliases": ["platform engineer", "internal platform engineer"], "subjects": ["IT & Software", "Programming Languages"], "skills": [("Linux", "critical"), ("Cloud Computing", "critical"), ("Kubernetes", "critical"), ("Docker", "high"), ("Terraform", "high"), ("CI/CD", "high"), ("Observability", "medium"), ("Networking", "medium")], "next_roles": ["Senior Platform Engineer", "Platform Architect", "Platform Engineering Manager"]},
    {"role": "DevOps Engineer", "aliases": ["devops engineer"], "subjects": ["IT & Software", "Programming Languages"], "skills": [("Docker", "critical"), ("Kubernetes", "critical"), ("CI/CD", "critical"), ("Linux", "high"), ("Terraform", "high"), ("Cloud Computing", "high"), ("Monitoring", "medium"), ("Python", "medium")], "next_roles": ["Senior DevOps Engineer", "Site Reliability Engineer", "Cloud Architect"]},
    {"role": "SRE", "aliases": ["sre", "site reliability engineer"], "subjects": ["IT & Software", "Programming Languages"], "skills": [("Linux", "critical"), ("Kubernetes", "critical"), ("Cloud Computing", "critical"), ("Monitoring", "high"), ("Observability", "high"), ("Incident Response", "high"), ("Terraform", "medium"), ("CI/CD", "medium")], "next_roles": ["Senior SRE", "Reliability Architect", "Platform Engineering Manager"]},
]


class RoleExpansionRepository:
    """SQLite repository for seeded and Gemini-discovered role profiles."""

    def __init__(self, database_path: Optional[str] = None):
        default_path = Path(__file__).resolve().parents[2] / "data" / "role_expansions.sqlite3"
        self.database_path = Path(database_path or os.getenv("ROLE_EXPANSION_DB_PATH", str(default_path)))
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self.seed_profiles()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path), timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS role_profiles (
                    role_key TEXT PRIMARY KEY,
                    canonical_role TEXT NOT NULL,
                    subjects_json TEXT NOT NULL,
                    source TEXT NOT NULL CHECK(source IN ('seeded', 'dynamic')),
                    confidence TEXT,
                    validation_status TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS role_aliases (
                    alias_key TEXT PRIMARY KEY,
                    role_key TEXT NOT NULL REFERENCES role_profiles(role_key)
                );
                CREATE TABLE IF NOT EXISTS role_skills (
                    role_key TEXT NOT NULL REFERENCES role_profiles(role_key),
                    ordinal INTEGER NOT NULL,
                    skill TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('critical', 'high', 'medium')),
                    category TEXT NOT NULL DEFAULT 'domain',
                    PRIMARY KEY(role_key, ordinal)
                );
                CREATE TABLE IF NOT EXISTS role_progression (
                    role_key TEXT NOT NULL REFERENCES role_profiles(role_key),
                    ordinal INTEGER NOT NULL,
                    next_role TEXT NOT NULL,
                    PRIMARY KEY(role_key, ordinal)
                );
            """)

    def seed_profiles(self) -> None:
        for profile in ROLE_EXPANSIONS:
            if not self.get_by_role(profile["role"]):
                self.upsert_profile(profile, source="seeded")

    def get_by_input(self, role_input: str) -> Optional[Dict[str, Any]]:
        alias_key = normalize_role_key(role_input)
        if not alias_key:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role_key FROM role_aliases WHERE alias_key = ?", (alias_key,)
            ).fetchone()
        return self._load_profile(row["role_key"]) if row else None

    def get_by_role(self, canonical_role: str) -> Optional[Dict[str, Any]]:
        return self._load_profile(normalize_role_key(canonical_role))

    def _load_profile(self, role_key: str) -> Optional[Dict[str, Any]]:
        if not role_key:
            return None
        with self._connect() as conn:
            profile = conn.execute(
                "SELECT canonical_role, subjects_json, source, confidence, validation_status, created_at, updated_at FROM role_profiles WHERE role_key = ?",
                (role_key,),
            ).fetchone()
            if not profile:
                return None
            skills = conn.execute(
                "SELECT skill, priority, category FROM role_skills WHERE role_key = ? ORDER BY ordinal", (role_key,)
            ).fetchall()
            next_roles = conn.execute(
                "SELECT next_role FROM role_progression WHERE role_key = ? ORDER BY ordinal", (role_key,)
            ).fetchall()
        return {
            "role": profile["canonical_role"],
            "subjects": json.loads(profile["subjects_json"]),
            "skills": [row["skill"] for row in skills],
            "skill_priorities": {row["skill"]: row["priority"] for row in skills},
            "skill_categories": {row["skill"]: row["category"] for row in skills} if any("category" in row.keys() for row in skills) else {},
            "next_roles": [row["next_role"] for row in next_roles],
            "source": profile["source"],
            "confidence": profile["confidence"],
            "validation_status": profile["validation_status"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"],
        }

    def upsert_profile(self, profile: Dict[str, Any], source: str, aliases: Optional[List[str]] = None) -> Dict[str, Any]:
        role = str(profile["role"]).strip()
        role_key = normalize_role_key(role)
        timestamp = datetime.now(timezone.utc).isoformat()
        role_aliases = list(dict.fromkeys([role, *(profile.get("aliases") or []), *(aliases or [])]))
        skills = profile["skills"]
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """INSERT INTO role_profiles(role_key, canonical_role, subjects_json, source, confidence, validation_status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(role_key) DO UPDATE SET canonical_role=excluded.canonical_role,
                       subjects_json=excluded.subjects_json, source=excluded.source, 
                       confidence=excluded.confidence, validation_status=excluded.validation_status, 
                       updated_at=excluded.updated_at""",
                (role_key, role, json.dumps(profile["subjects"]), source, 
                 profile.get("confidence"), profile.get("validation_status"), timestamp, timestamp),
            )
            conn.execute("DELETE FROM role_skills WHERE role_key = ?", (role_key,))
            conn.execute("DELETE FROM role_progression WHERE role_key = ?", (role_key,))
            
            # handle both (skill, priority) and (skill, priority, category) formats
            skill_records = []
            for ordinal, item in enumerate(skills):
                if isinstance(item, tuple) and len(item) == 3:
                    skill_records.append((role_key, ordinal, item[0], item[1], item[2]))
                elif isinstance(item, tuple) and len(item) == 2:
                    skill_records.append((role_key, ordinal, item[0], item[1], 'domain'))
                else:
                    skill_records.append((role_key, ordinal, item, 'high', 'domain'))
                    
            conn.executemany(
                "INSERT INTO role_skills(role_key, ordinal, skill, priority, category) VALUES (?, ?, ?, ?, ?)",
                skill_records,
            )
            conn.executemany(
                "INSERT INTO role_progression(role_key, ordinal, next_role) VALUES (?, ?, ?)",
                [(role_key, ordinal, next_role) for ordinal, next_role in enumerate(profile["next_roles"])],
            )
            conn.executemany(
                "INSERT OR REPLACE INTO role_aliases(alias_key, role_key) VALUES (?, ?)",
                [(normalize_role_key(alias), role_key) for alias in role_aliases if normalize_role_key(alias)],
            )
        return self.get_by_role(role) or {}


role_expansion_repository = RoleExpansionRepository()
