"""
Taxonomy definitions for career roles, subjects, and skills.
Provides skill gap analysis maps and subject mappings.
"""

import re
from typing import List, Dict, Any, Optional, Set, Union

# Standardized Career Role Mapping with subjects, required skills, and next career progression steps
JOB_ROLE_MAPPING: Dict[str, Dict[str, Any]] = {
    "AI Engineer": {
        "subjects": ["Machine Learning", "Data Science", "Programming Languages", "IT & Software"],
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "MLOps", "NLP", "Computer Vision", "Transformers", "SQL"],
        "next_roles": ["Senior AI Engineer", "AI Architect", "AI Engineering Manager", "Director of AI"],
    },
    "AI Research Scientist": {
        "subjects": ["Machine Learning", "Data Science", "Mathematics", "Statistics"],
        "skills": ["Machine Learning", "Deep Learning", "PyTorch", "Mathematics", "Statistics", "Transformers", "LLMs", "Computer Vision", "NLP", "TensorFlow", "MLOps", "Cloud Computing"],
        "next_roles": ["Senior Research Scientist", "Principal Research Scientist", "Research Lead", "Director of AI Research"],
    },
    "ML Research Scientist": {
        "subjects": ["Machine Learning", "Data Science", "Research Methodology"],
        "skills": ["Deep Learning", "PyTorch", "Research Methodology", "Model Training", "Experimentation", "Transformers", "Paper Implementation", "Machine Learning", "Statistics"],
        "next_roles": ["Senior ML Research Scientist", "Principal ML Researcher", "Research Lead"],
    },
    "Applied Scientist": {
        "subjects": ["Machine Learning", "Data Science", "Statistics"],
        "skills": ["Machine Learning", "Statistics", "Experiment Design", "Data Analysis", "Deep Learning", "Python", "SQL", "A/B Testing"],
        "next_roles": ["Senior Applied Scientist", "Principal Applied Scientist", "Head of Applied Science"],
    },
    "Research Engineer": {
        "subjects": ["Machine Learning", "IT & Software", "Programming Languages"],
        "skills": ["PyTorch", "Deep Learning", "Distributed Training", "C++", "Python", "Transformers", "Model Optimization", "Linux"],
        "next_roles": ["Senior Research Engineer", "Principal Research Engineer", "Research Engineering Lead"],
    },
    "Data Scientist": {
        "subjects": ["Data Science", "Machine Learning", "Programming Languages", "Business"],
        "skills": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Scikit-learn", "Data Visualization", "Deep Learning", "A/B Testing"],
        "next_roles": ["Senior Data Scientist", "Lead Data Scientist", "Head of Data Science", "Chief Data Officer"],
    },
    "Software Engineer": {
        "subjects": ["Programming Languages", "Web Development", "IT & Software"],
        "skills": ["Python", "Java", "JavaScript", "C++", "Data Structures", "Algorithms", "Git", "SQL", "System Design", "Docker"],
        "next_roles": ["Senior Software Engineer", "Staff Engineer", "Principal Architect", "Engineering Manager"],
    },
    "Python Developer": {
        "subjects": ["Programming Languages", "Web Development", "Data Science"],
        "skills": ["Python", "Django", "FastAPI", "Flask", "SQL", "REST APIs", "Git", "Unit Testing", "Docker", "Object-Oriented Programming"],
        "next_roles": ["Senior Python Developer", "Lead Backend Engineer", "Python Architect"],
    },
    "Data Analyst": {
        "subjects": ["Data Science", "Business", "IT & Software"],
        "skills": ["SQL", "Excel", "Tableau", "Power BI", "Python", "Data Visualization", "Statistics", "Data Cleaning", "Pandas"],
        "next_roles": ["Senior Data Analyst", "Data Scientist", "Analytics Manager", "Business Intelligence Lead"],
    },
    "Machine Learning Engineer": {
        "subjects": ["Machine Learning", "Data Science", "IT & Software", "Programming Languages"],
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "MLOps", "Docker", "Kubernetes", "Model Deployment", "SQL"],
        "next_roles": ["Senior ML Engineer", "ML Architect", "AI Platform Lead"],
    },
    "Frontend Developer": {
        "subjects": ["Web Development", "Design"],
        "skills": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Vue.js", "Responsive Design", "Git", "UI/UX", "State Management"],
        "next_roles": ["Senior Frontend Developer", "Lead Frontend Architect", "Full Stack Developer"],
    },
    "Backend Developer": {
        "subjects": ["Web Development", "Programming Languages", "IT & Software"],
        "skills": ["Python", "Node.js", "Java", "SQL", "NoSQL", "REST APIs", "GraphQL", "Docker", "Microservices", "Git"],
        "next_roles": ["Senior Backend Developer", "Backend Architect", "Staff Engineer"],
    },
    "Full Stack Developer": {
        "subjects": ["Web Development", "Programming Languages", "IT & Software"],
        "skills": ["JavaScript", "Python", "React", "Node.js", "HTML", "CSS", "SQL", "Git", "REST APIs", "Docker"],
        "next_roles": ["Senior Full Stack Developer", "Lead Web Architect", "VP of Engineering"],
    },
    "DevOps Engineer": {
        "subjects": ["IT & Software", "Programming Languages"],
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "Python", "Bash", "Monitoring", "Cloud Computing"],
        "next_roles": ["Senior DevOps Engineer", "Site Reliability Engineer (SRE)", "Cloud Architect"],
    },
    "Cloud Engineer": {
        "subjects": ["IT & Software", "Programming Languages"],
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux", "Networking", "Security"],
        "next_roles": ["Senior Cloud Engineer", "Cloud Architect", "Infrastructure Director"],
    },
    "Product Manager": {
        "subjects": ["Business", "Marketing", "Design"],
        "skills": ["Product Strategy", "Agile", "Scrum", "User Research", "Data Analysis", "Roadmapping", "A/B Testing", "Leadership", "JIRA"],
        "next_roles": ["Senior Product Manager", "Group Product Manager", "VP of Product", "Chief Product Officer"],
    },
    "Digital Marketer": {
        "subjects": ["Marketing", "Business"],
        "skills": ["SEO", "Google Ads", "Content Marketing", "Social Media", "Email Marketing", "Google Analytics", "Copywriting", "Branding"],
        "next_roles": ["Senior Growth Marketer", "Marketing Director", "Chief Marketing Officer (CMO)"],
    },
    "Graphic Designer": {
        "subjects": ["Design"],
        "skills": ["Photoshop", "Illustrator", "Figma", "Typography", "Color Theory", "Layout Design", "Branding", "Visual Design"],
        "next_roles": ["Senior Designer", "Art Director", "Creative Director"],
    },
    "UX Designer": {
        "subjects": ["Design", "Web Development"],
        "skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Usability Testing", "UI Design", "Information Architecture", "Design Systems"],
        "next_roles": ["Senior UX Designer", "Lead UX Researcher", "Head of Design"],
    },
    "Cybersecurity Analyst": {
        "subjects": ["IT & Software", "Programming Languages"],
        "skills": ["Network Security", "Penetration Testing", "SIEM", "Incident Response", "Cryptography", "Linux", "Vulnerability Assessment", "Compliance"],
        "next_roles": ["Senior Security Analyst", "Security Engineer", "Security Architect", "CISO"],
    },
    "QA Engineer": {
        "subjects": ["IT & Software", "Programming Languages", "Web Development"],
        "skills": ["Automated Testing", "Selenium", "Python", "Manual Testing", "JIRA", "API Testing", "Test Planning", "CI/CD"],
        "next_roles": ["Senior QA Engineer", "Lead Test Automation Engineer", "QA Manager"],
    },
    "Business Analyst": {
        "subjects": ["Business", "Data Science"],
        "skills": ["SQL", "Excel", "Requirement Gathering", "Data Analysis", "Process Modeling", "Tableau", "JIRA", "Stakeholder Management"],
        "next_roles": ["Senior Business Analyst", "Product Owner", "Business Operations Lead"],
    },
    "LLM Engineer": {
        "subjects": ["Machine Learning", "Data Science", "Programming Languages"],
        "skills": ["Transformers", "RAG", "Vector Databases", "Prompt Engineering", "LLMOps", "Python", "PyTorch", "LangChain"],
        "next_roles": ["Senior LLM Engineer", "LLM Architect", "Head of AI"],
    },
    "Autonomous Driving Engineer": {
        "subjects": ["Machine Learning", "Programming Languages", "IT & Software"],
        "skills": ["C++", "Python", "ROS", "Computer Vision", "Sensor Fusion", "SLAM", "LiDAR", "Path Planning", "Deep Learning"],
        "next_roles": ["Senior Autonomous Driving Engineer", "Perception Lead", "Robotics Architect"],
    },
    "Quantum ML Engineer": {
        "subjects": ["Machine Learning", "Data Science", "Programming Languages"],
        "skills": ["Quantum Computing", "Qiskit", "Quantum Algorithms", "Python", "Linear Algebra", "Machine Learning", "PyTorch"],
        "next_roles": ["Senior Quantum ML Engineer", "Quantum Research Scientist", "Quantum Architect"],
    },
}

COMMON_SKILLS = [
    "Python", "JavaScript", "Java", "React", "Node.js", "SQL", "Git", "Docker", "AWS", "Machine Learning",
    "Data Science", "HTML", "CSS", "TypeScript", "Deep Learning", "PyTorch", "TensorFlow", "Pandas", "NumPy",
    "Scikit-learn", "Tableau", "Power BI", "Excel", "Agile", "Scrum", "JIRA", "Figma", "Photoshop", "Illustrator",
    "SEO", "Google Ads", "Kubernetes", "MLOps", "REST APIs", "C++", "C#", "Linux", "CI/CD",
    "NLP", "Computer Vision", "Statistics", "Model Deployment", "Neural Networks", "Transformers",
]

DOMAIN_ONTOLOGY: Dict[str, Dict[str, List[str]]] = {
    "Autonomous Driving Engineer": {
        "primary": ["computer vision", "sensor fusion", "lidar", "radar", "path planning", "control systems", "ros", "kalman filter", "c++", "deep learning"],
        "secondary": ["robotics", "simulink"],
        "generic": ["python", "machine learning", "ai", "programming", "software"],
        "negative": ["web development", "react", "html", "css", "frontend"]
    },
    "AI Research Scientist": {
        "primary": ["research papers", "transformers", "llms", "pytorch", "deep learning", "nlp", "computer vision", "research", "paper reproduction"],
        "secondary": ["machine learning", "neural networks", "statistics", "mathematics"],
        "generic": ["python", "data science", "programming"],
        "negative": ["frontend", "web development", "react", "css"]
    },
    "LLM Engineer": {
        "primary": ["rag", "vector database", "embeddings", "langchain", "llmops", "prompt engineering", "transformers", "large language models", "llm"],
        "secondary": ["nlp", "deep learning", "pytorch", "python"],
        "generic": ["machine learning", "ai", "programming", "software engineering"],
        "negative": ["frontend", "css", "html", "react"]
    },
    "Robotics Engineer": {
        "primary": ["ros", "robotics", "slam", "control systems", "embedded", "c++", "kinematics", "motion planning", "lidar"],
        "secondary": ["computer vision", "python", "electronics", "hardware"],
        "generic": ["engineering", "programming"],
        "negative": ["frontend", "react", "css", "html", "web design"]
    },
    "Quantum ML Engineer": {
        "primary": ["qiskit", "quantum algorithms", "quantum circuits", "quantum computing", "pennylane", "qubits"],
        "secondary": ["machine learning", "linear algebra", "physics", "python"],
        "generic": ["ai", "programming", "software"],
        "negative": ["frontend", "web development", "react", "css"]
    },
    "Data Scientist": {
        "primary": ["data science", "statistics", "pandas", "machine learning", "eda", "visualization", "jupyter"],
        "secondary": ["python", "r", "sql", "predictive modeling"],
        "generic": ["data", "analytics", "programming", "math"],
        "negative": ["frontend", "backend routing", "css", "html"]
    },
    "Data Analyst": {
        "primary": ["sql", "excel", "tableau", "power bi", "data analysis", "reporting"],
        "secondary": ["python", "statistics", "pandas", "dashboards"],
        "generic": ["data", "analytics", "business"],
        "negative": ["deep learning", "neural networks", "kubernetes", "docker"]
    },
    "Machine Learning Engineer": {
        "primary": ["machine learning", "scikit-learn", "xgboost", "model deployment", "mlops", "sagemaker"],
        "secondary": ["python", "statistics", "data engineering", "deep learning"],
        "generic": ["programming", "software", "data", "ai"],
        "negative": ["frontend", "css", "html", "ui design", "ux"]
    },
    "DevOps Engineer": {
        "primary": ["kubernetes", "docker", "ci/cd", "terraform", "jenkins", "aws", "gcp", "azure", "infrastructure"],
        "secondary": ["linux", "bash", "python", "networking"],
        "generic": ["operations", "cloud", "deployment"],
        "negative": ["ui design", "frontend", "data science"]
    },
    "AI Engineer": {
        "primary": ["deep learning", "neural networks", "tensorflow", "pytorch", "transformers", "llms"],
        "secondary": ["machine learning", "python", "model deployment", "mlops"],
        "generic": ["programming", "software", "data", "ai"],
        "negative": ["web development", "frontend", "react", "css", "html", "seo"]
    }
}

# Common spelling mistakes and typos mapped to canonical roles (treated as fuzzy/medium confidence)
ROLE_TYPOS: Dict[str, str] = {
    "ai reserch scientist": "AI Research Scientist",
    "ai enginer": "AI Engineer",
    "machin learning engineer": "Machine Learning Engineer",
    "data scienist": "Data Scientist",
    "softwere developer": "Software Engineer",
    "pyhton developer": "Python Developer",
    "backend devloper": "Backend Developer",
}

# Alternate role names mapped to canonical taxonomy keys
ROLE_ALIASES: Dict[str, str] = {
    # AI / ML Research & Engineering
    "ai research scientist": "AI Research Scientist",
    "ai research sci": "AI Research Scientist",
    "ai researcher": "AI Research Scientist",
    "artificial intelligence researcher": "AI Research Scientist",
    "artificial intelligence research scientist": "AI Research Scientist",
    "ml research scientist": "ML Research Scientist",
    "ml research sci": "ML Research Scientist",
    "ml researcher": "ML Research Scientist",
    "machine learning research scientist": "ML Research Scientist",
    "machine learning researcher": "ML Research Scientist",
    "applied scientist": "Applied Scientist",
    "applied ml scientist": "Applied Scientist",
    "applied ai scientist": "Applied Scientist",
    "research engineer": "Research Engineer",
    "ai research engineer": "Research Engineer",
    "ml research engineer": "Research Engineer",
    "ai engineer": "AI Engineer",
    "artificial intelligence engineer": "AI Engineer",
    "artificial intelligence": "AI Engineer",
    "ai eng": "AI Engineer",
    "ai dev": "AI Engineer",
    "ai": "AI Engineer",
    "machine learning engineer": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "ml eng": "Machine Learning Engineer",
    "machine learning eng": "Machine Learning Engineer",
    "ml dev": "Machine Learning Engineer",
    "machine learning dev": "Machine Learning Engineer",
    "machine learning developer": "Machine Learning Engineer",
    "ml developer": "Machine Learning Engineer",
    "ml": "Machine Learning Engineer",
    "ai developer": "AI Engineer",
    "ai/ml engineer": "AI Engineer",
    "ml/ai engineer": "Machine Learning Engineer",
    # Data
    "data scientist": "Data Scientist",
    "data science": "Data Scientist",
    "data sci": "Data Scientist",
    "ds": "Data Scientist",
    "data analyst": "Data Analyst",
    "data analysis": "Data Analyst",
    "bi analyst": "Data Analyst",
    "business analyst": "Business Analyst",
    "ba": "Business Analyst",
    # Software / Web
    "software developer": "Software Engineer",
    "software engineer": "Software Engineer",
    "swe": "Software Engineer",
    "sde": "Software Engineer",
    "programmer": "Software Engineer",
    "coder": "Software Engineer",
    "python developer": "Python Developer",
    "python dev": "Python Developer",
    "python engineer": "Python Developer",
    "web developer": "Full Stack Developer",
    "web dev": "Full Stack Developer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "full stack dev": "Full Stack Developer",
    "fullstack dev": "Full Stack Developer",
    "fs dev": "Full Stack Developer",
    "frontend developer": "Frontend Developer",
    "frontend dev": "Frontend Developer",
    "fe dev": "Frontend Developer",
    "front end developer": "Frontend Developer",
    "front end dev": "Frontend Developer",
    "backend developer": "Backend Developer",
    "backend dev": "Backend Developer",
    "be dev": "Backend Developer",
    "back end developer": "Backend Developer",
    "back end dev": "Backend Developer",
    # DevOps / Cloud
    "devops engineer": "DevOps Engineer",
    "devops": "DevOps Engineer",
    "cloud engineer": "Cloud Engineer",
    "cloud dev": "Cloud Engineer",
    "cloud architect": "Cloud Engineer",
    # Design / Product / Marketing
    "product manager": "Product Manager",
    "pm": "Product Manager",
    "product mgr": "Product Manager",
    "digital marketer": "Digital Marketer",
    "marketing": "Digital Marketer",
    "graphic designer": "Graphic Designer",
    "graphic design": "Graphic Designer",
    "ux designer": "UX Designer",
    "ui/ux designer": "UX Designer",
    "ui/ux": "UX Designer",
    "ux": "UX Designer",
    "ui designer": "UX Designer",
    # QA / Cyber
    "qa engineer": "QA Engineer",
    "qa": "QA Engineer",
    "qa tester": "QA Engineer",
    "quality assurance": "QA Engineer",
    "test engineer": "QA Engineer",
    "cybersecurity analyst": "Cybersecurity Analyst",
    "cybersecurity": "Cybersecurity Analyst",
    "security engineer": "Cybersecurity Analyst",
    "security analyst": "Cybersecurity Analyst",
    "sec analyst": "Cybersecurity Analyst",
    "js developer": "Frontend Developer",
    "javascript developer": "Frontend Developer",
    "ux researcher": "UX Designer",
    "graphic artist": "Graphic Designer",
    "product owner": "Product Manager",
    "devops specialist": "DevOps Engineer",
}

# Skill synonyms used for gap matching and course metadata normalization
SKILL_SYNONYMS: Dict[str, List[str]] = {
    "machine learning": ["ml", "scikit-learn", "sklearn", "scikit learn"],
    "deep learning": ["neural network", "neural networks", "deep neural", "deep neural network"],
    "natural language processing": ["nlp", "text mining", "language model", "transformer", "transformers", "llm", "bert", "gpt"],
    "computer vision": ["opencv", "image recognition", "object detection"],
    "tensorflow": ["tensor flow"],
    "pytorch": ["torch", "py torch"],
    "mlops": ["model deployment", "model serving", "ml pipeline", "ml pipelines"],
    "data visualization": ["data visualisation", "d3.js", "plotly", "matplotlib", "seaborn"],
    "statistics": ["statistical", "probability", "inferential statistics"],
    "artificial intelligence": ["artificial-intelligence"],
    "model deployment": ["deploy model", "serving models", "production ml", "production machine learning"],
    "sensor fusion": ["lidar", "radar", "perception", "multi sensor fusion"],
    "ros": ["robot operating system", "robotics middleware"],
    "autonomous driving": ["self driving", "adas", "autonomous vehicles"],
    "rag": ["retrieval augmented generation"],
}

ROLE_STOP_WORDS = {"of", "in", "or", "to", "at", "by", "for", "and", "the", "with", "a", "an", "senior", "lead", "junior"}
ROLE_WORD_ALIASES = {"developer": "engineer", "programmer": "engineer", "dev": "developer"}
ROLE_GENERIC_TOKENS = {"engineer", "developer", "analyst", "manager", "designer", "specialist", "dev", "programmer", "architect", "lead", "senior", "director"}


def _role_tokens(role: str) -> Set[str]:
    """Tokenize a role string for overlap-based matching."""
    tokens: Set[str] = set()
    for word in role.lower().split():
        if len(word) < 2 or word in ROLE_STOP_WORDS:
            continue
        tokens.add(word)
        if word in ROLE_WORD_ALIASES:
            tokens.add(ROLE_WORD_ALIASES[word])
    return tokens


def resolve_role(job_role: str) -> Optional[str]:
    """Resolve free-text role input to the closest canonical taxonomy role."""
    if not job_role or not job_role.strip():
        return None

    job_role_clean = job_role.strip().lower()
    if job_role_clean in ROLE_TYPOS:
        return ROLE_TYPOS[job_role_clean]
    if job_role_clean in ROLE_ALIASES:
        return ROLE_ALIASES[job_role_clean]

    for role in JOB_ROLE_MAPPING:
        if role.lower() == job_role_clean:
            return role

    # Exact persisted profiles outrank fuzzy matches to broadly named verified
    # roles (for example, Backend Engineer must not become Backend Developer).
    try:
        from app.data.career_understanding import career_understanding_service
        profile = career_understanding_service.lookup(job_role_clean)
        if profile:
            return profile["role"]
    except Exception:
        pass

    query_tokens = _role_tokens(job_role_clean)
    if not query_tokens:
        return None

    query_domain_tokens = query_tokens - ROLE_GENERIC_TOKENS

    best_role: Optional[str] = None
    best_score = 0
    best_full_match = False

    for role in JOB_ROLE_MAPPING:
        role_tokens = _role_tokens(role)
        overlap = len(query_tokens & role_tokens)
        full_match = query_tokens == role_tokens
        
        # If the query had domain tokens (e.g. 'xyz engineer'), require at least one domain token match
        if query_domain_tokens:
            role_domain_tokens = role_tokens - ROLE_GENERIC_TOKENS
            if not (query_domain_tokens & role_domain_tokens):
                continue
        else:
            # If query has ONLY generic tokens (e.g. 'engineer'), do not resolve arbitrarily to a specific role
            return None

        if overlap > best_score or (overlap == best_score and full_match and not best_full_match):
            best_score = overlap
            best_role = role
            best_full_match = full_match
        elif overlap == best_score and overlap > 0 and best_role:
            if overlap == len(role_tokens) and overlap > len(_role_tokens(best_role) & query_tokens):
                best_role = role

    if best_score > 0:
        return best_role

    # Persisted expansion profiles are deliberately checked only after the
    # verified taxonomy, aliases, and fuzzy matching above.
    try:
        from app.data.career_understanding import career_understanding_service
        profile = career_understanding_service.lookup(job_role)
        if profile:
            return profile["role"]
    except Exception:
        # Role resolution must retain the verified taxonomy's deterministic
        # behavior when the optional persistent store cannot be read.
        pass
    return None


def suggest_closest_roles(job_role: str, top_k: int = 4) -> List[str]:
    """Suggest closest canonical roles when exact resolution fails or input is unmapped."""
    if not job_role or not job_role.strip():
        return ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"][:top_k]

    job_role_clean = job_role.strip().lower()
    query_tokens = _role_tokens(job_role_clean)
    
    scored_candidates = []
    for role in JOB_ROLE_MAPPING:
        role_tokens = _role_tokens(role)
        overlap = len(query_tokens & role_tokens)
        # Also check substring containment
        sub_bonus = 1 if (job_role_clean in role.lower() or role.lower() in job_role_clean) else 0
        score = overlap * 2 + sub_bonus
        if score > 0:
            scored_candidates.append((score, role))
            
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    suggestions = [c[1] for c in scored_candidates[:top_k]]
    
    if not suggestions:
        return ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"][:top_k]
    return suggestions


def resolve_role_details(job_role: str) -> Dict[str, Any]:
    """Exhaustive confidence-based role resolution handling empty, generic, typo, abbreviations, invalid, long sentences, and multiple roles."""
    if not job_role or not str(job_role).strip():
        return {
            "role": None,
            "confidence": "none",
            "source": "unresolved",
            "suggestions": ["AI Engineer", "Software Engineer", "Data Scientist", "Full Stack Developer"],
            "message": "Please enter your current role."
        }

    raw_clean = str(job_role).strip()
    job_role_clean = raw_clean.lower()
    
    # Strip seniority prefixes to improve base role matching
    seniority_prefixes = ["senior ", "junior ", "lead ", "principal ", "staff ", "chief ", "sr ", "sr. ", "jr ", "jr. "]
    for prefix in seniority_prefixes:
        if job_role_clean.startswith(prefix):
            job_role_clean = job_role_clean[len(prefix):].strip()
            break

    # Category 8: Multiple roles (e.g. 'data analyst/software developer' or 'python developer and data analyst')
    for sep in ["/", " and ", " & ", ", "]:
        if sep in job_role_clean:
            pieces = [p.strip() for p in job_role_clean.split(sep) if p.strip()]
            resolved_pieces = []
            for p in pieces:
                res = resolve_role(p)
                if res and res not in resolved_pieces:
                    resolved_pieces.append(res)
            if len(resolved_pieces) >= 1:
                primary = resolved_pieces[0]
                msg = f"Multiple roles detected ({', '.join(resolved_pieces)}). Using {primary} as primary role." if len(resolved_pieces) > 1 else f"Resolved role to {primary}."
                return {
                    "role": primary,
                    "confidence": "medium",
                    "source": "extracted",
                    "suggestions": resolved_pieces if len(resolved_pieces) > 1 else suggest_closest_roles(primary),
                    "message": msg
                }

    # Category 6: Long sentence inputs
    if len(job_role_clean.split()) > 5 or any(kw in job_role_clean for kw in ["working as", "transition into", "transition to", "become", "target role", "looking for", "want to be", "currently a"]):
        target_markers = ["transition into ", "transition to ", "become a ", "become an ", "become ", "target role is ", "target role ", "looking to be ", "looking for ", "want to be a ", "want to be an ", "want to be "]
        current_markers = ["working as a ", "working as an ", "working as ", "currently working as a ", "currently working as an ", "currently working as ", "currently a ", "currently an ", "i am a ", "i am an "]
        
        extracted_role = None
        for marker in target_markers:
            if marker in job_role_clean:
                after = job_role_clean.split(marker, 1)[1]
                words = after.split()[:4]
                for n in [4, 3, 2, 1]:
                    candidate = " ".join(words[:n])
                    res = resolve_role(candidate)
                    if res:
                        extracted_role = res
                        break
                if extracted_role:
                    break

        if not extracted_role:
            for marker in current_markers:
                if marker in job_role_clean:
                    after = job_role_clean.split(marker, 1)[1]
                    words = after.split()[:4]
                    for n in [4, 3, 2, 1]:
                        candidate = " ".join(words[:n])
                        res = resolve_role(candidate)
                        if res:
                            extracted_role = res
                            break
                    if extracted_role:
                        break

        if not extracted_role:
            for role in JOB_ROLE_MAPPING:
                if role.lower() in job_role_clean:
                    extracted_role = role
                    break

        if extracted_role:
            return {
                "role": extracted_role,
                "confidence": "medium",
                "source": "extracted",
                "suggestions": suggest_closest_roles(extracted_role),
                "message": f"Extracted role '{extracted_role}' from natural language input."
            }

    # Category 2: Generic inputs (engineer, developer, analyst, manager, student, programmer, data, tech, etc.)
    domain_map = {
        "engineer": ["AI Engineer", "Software Engineer", "Machine Learning Engineer", "DevOps Engineer"],
        "developer": ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer"],
        "analyst": ["Data Analyst", "Business Analyst", "Cybersecurity Analyst"],
        "manager": ["Product Manager"],
        "designer": ["UX Designer", "Graphic Designer"],
        "data": ["Data Scientist", "Data Analyst", "Machine Learning Engineer"],
        "student": ["Software Engineer", "Data Scientist", "AI Engineer", "Full Stack Developer"],
        "programmer": ["Software Engineer", "Python Developer", "Full Stack Developer"],
        "tech": ["Software Engineer", "Data Scientist", "Cloud Engineer", "DevOps Engineer"],
    }
    if job_role_clean in domain_map or job_role_clean in ROLE_GENERIC_TOKENS:
        suggs = domain_map.get(job_role_clean, suggest_closest_roles(job_role_clean))
        return {
            "role": None,
            "confidence": "low",
            "source": "unresolved",
            "suggestions": suggs,
            "message": f"Which {raw_clean} path do you mean?" if job_role_clean in domain_map else f"Please specify your target domain for {raw_clean}."
        }

    # Category 3 & 4: Exact or Alias or Typo resolution
    for role in JOB_ROLE_MAPPING:
        if role.lower() == job_role_clean:
            return {
                "role": role,
                "confidence": "high",
                "source": "Verified Career Path",
                "suggestions": JOB_ROLE_MAPPING[role]["next_roles"],
                "message": f"Exact match for {role}."
            }

    if job_role_clean in ROLE_TYPOS:
        canonical = ROLE_TYPOS[job_role_clean]
        return {
            "role": canonical,
            "confidence": "medium",
            "source": "Fuzzy Match",
            "suggestions": JOB_ROLE_MAPPING[canonical]["next_roles"],
            "message": f"Fuzzy matched '{raw_clean}' to {canonical}."
        }

    if job_role_clean in ROLE_ALIASES:
        canonical = ROLE_ALIASES[job_role_clean]
        return {
            "role": canonical,
            "confidence": "high",
            "source": "Verified Career Path",
            "suggestions": JOB_ROLE_MAPPING[canonical]["next_roles"],
            "message": f"Resolved '{raw_clean}' to {canonical}."
        }

    # Seeded expansion roles and previously parsed dynamic roles are checked
    # before generic fuzzy matching so they never collapse into a broad role.
    try:
        from app.data.career_understanding import career_understanding_service
        profile = career_understanding_service.lookup(raw_clean)
        if profile:
            dynamic = profile.get("source") == "dynamic"
            is_approved = profile.get("validation_status") == "approved"
            return {
                "role": profile["role"],
                "confidence": "medium-high" if is_approved else ("low" if dynamic else "medium"),
                "source": "AI Validated Career Path" if is_approved else ("dynamic_cache" if dynamic else "expansion"),
                "suggestions": profile.get("next_roles", []),
                "message": (
                    f"Loaded AI Validated Career Path: {profile['role']}."
                    if is_approved else (f"Loaded the cached emerging role {profile['role']}." if dynamic else f"Expanded role match for {profile['role']}.")
                ),
            }
    except Exception:
        pass

    # An unfamiliar technology modifier (for example, "Quantum AI Engineer")
    # is eligible for parsing before its generic "AI Engineer" overlap can
    # collapse it into a verified role. Established fuzzy wording stays intact.
    try:
        from app.data.career_understanding import career_understanding_service, should_parse_before_fuzzy_match
        if should_parse_before_fuzzy_match(raw_clean):
            profile = career_understanding_service.parse_and_cache(raw_clean)
            if profile:
                is_approved = profile.get("validation_status") == "approved"
                return {
                    "role": profile["role"],
                    "confidence": "medium-high" if is_approved else "low",
                    "source": "AI Validated Career Path" if is_approved else "dynamic_cache",
                    "suggestions": profile.get("next_roles", []),
                    "message": f"Parsed and cached emerging role {profile['role']}.",
                }
            return {
                "role": None,
                "confidence": "none",
                "source": "unresolved",
                "suggestions": suggest_closest_roles(job_role),
                "message": "No matching career found.",
            }
    except Exception as exc:
        status_code = getattr(exc, "status_code", 422)
        if status_code == 503:
            return {
                "role": None,
                "confidence": "none",
                "source": "parser_unavailable",
                "suggestions": suggest_closest_roles(job_role),
                "message": getattr(exc, "detail", "Gemini career parsing is unavailable."),
            }

    resolved = resolve_role(job_role)
    if resolved and resolved in JOB_ROLE_MAPPING:
        return {
            "role": resolved,
            "confidence": "medium",
            "source": "Fuzzy Match",
            "suggestions": JOB_ROLE_MAPPING[resolved]["next_roles"],
            "message": f"Fuzzy matched '{raw_clean}' to {resolved}."
        }

    # Category 5: Parse plausible emerging technology roles only after all
    # verified and seeded options have been exhausted.
    try:
        from app.data.career_understanding import career_understanding_service, is_plausible_technology_role
        if is_plausible_technology_role(raw_clean):
            profile = career_understanding_service.parse_and_cache(raw_clean)
            if profile:
                is_approved = profile.get("validation_status") == "approved"
                return {
                    "role": profile["role"],
                    "confidence": "medium-high" if is_approved else "low",
                    "source": "AI Validated Career Path" if is_approved else "dynamic_cache",
                    "suggestions": profile.get("next_roles", []),
                    "message": f"Parsed and cached emerging role {profile['role']}.",
                }
    except Exception as exc:
        status_code = getattr(exc, "status_code", 422)
        detail = getattr(exc, "detail", "Could not validate this emerging career role.")
        return {
            "role": None,
            "confidence": "none",
            "source": "parser_unavailable" if status_code == 503 else "unresolved",
            "suggestions": suggest_closest_roles(job_role),
            "message": detail,
        }

    # Category 6: Completely invalid inputs (xyz, banana, etc.)
    return {
        "role": None,
        "confidence": "none",
        "source": "unresolved",
        "suggestions": suggest_closest_roles(job_role),
        "message": "No matching career found."
    }


def normalize_skill_name(skill: str) -> str:
    """Normalize a skill label for comparison."""
    return skill.strip().lower()


def normalize_and_deduplicate_skills(skills_input: Union[str, List[str]]) -> List[str]:
    """Normalize, clean, and deduplicate user skill inputs, expanding short acronyms."""
    if not skills_input:
        return []

    if isinstance(skills_input, str):
        items = [s.strip() for s in re.split(r'[,;\n]+', skills_input) if s.strip()]
    elif isinstance(skills_input, list):
        items = []
        for s in skills_input:
            if s and str(s).strip():
                for sub in re.split(r'[,;\n]+', str(s)):
                    if sub.strip():
                        items.append(sub.strip())
    else:
        return []

    acronym_map = {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "ml": "Machine Learning",
        "machine learning": "Machine Learning",
        "dl": "Deep Learning",
        "deep learning": "Deep Learning",
        "ai": "Artificial Intelligence",
        "artificial intelligence": "Artificial Intelligence",
        "tf": "TensorFlow",
        "tensorflow": "TensorFlow",
        "nlp": "Natural Language Processing",
        "cv": "Computer Vision",
        "k8s": "Kubernetes",
        "aws": "AWS",
        "gcp": "GCP",
        "sql": "SQL",
        "python": "Python",
        "py": "Python",
        "react": "React",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "docker": "Docker",
        "c++": "C++",
        "c#": "C#",
        "css": "CSS",
        "html": "HTML",
        "git": "Git",
        "jira": "JIRA",
    }

    seen_lower = set()
    cleaned = []
    for item in items:
        if len(item) < 2 and item.upper() not in {"C", "R"}:
            continue
        item_lower = item.lower()
        if item_lower in acronym_map:
            canonical = acronym_map[item_lower]
        else:
            canonical = item
        
        canon_lower = canonical.lower()
        if canon_lower not in seen_lower:
            seen_lower.add(canon_lower)
            cleaned.append(canonical)

    return cleaned


def skill_search_terms(skill: str) -> List[str]:
    """Return normalized skill plus synonym phrases for text matching."""
    base = normalize_skill_name(skill)
    terms = [base]
    for canonical, aliases in SKILL_SYNONYMS.items():
        if base == canonical or base in aliases:
            terms.append(canonical)
            terms.extend(aliases)
    if base in SKILL_SYNONYMS:
        terms.extend(SKILL_SYNONYMS[base])
    return list(dict.fromkeys(terms))


def skill_matches_text(skill: str, text: str) -> bool:
    """Check whether a skill (or synonym) appears in text using word-aware matching."""
    text_lower = text.lower()
    for term in skill_search_terms(skill):
        if len(term) <= 3:
            pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
            if re.search(pattern, text_lower):
                return True
        elif term in text_lower:
            return True
    return False


def _term_present_in_text(term: str, text: str) -> bool:
    """Check if a term appears in text using word-boundary matching for short terms."""
    if len(term) <= 3:
        pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        return bool(re.search(pattern, text))
    return term in text


def expand_text_with_skill_synonyms(text: str) -> str:
    """Append canonical skill phrases to course text to improve gap matching.

    Uses word-boundary matching for short synonym terms (e.g. 'ml', 'nlp')
    to prevent false positives like 'ann' matching inside 'planning'.
    """
    expanded = text.lower()
    for canonical, aliases in SKILL_SYNONYMS.items():
        if _term_present_in_text(canonical, expanded) or any(
            _term_present_in_text(alias, expanded) for alias in aliases
        ):
            expanded += f" {canonical}"
            expanded += " " + " ".join(aliases)
    return expanded


def extract_skills_from_text(text: str) -> List[str]:
    """Extract known skills from unstructured course text."""
    text_lower = text.lower()
    found: List[str] = []
    for skill in COMMON_SKILLS:
        if skill_matches_text(skill, text_lower):
            found.append(skill)
    return found[:12]


def categorize_course_subject(title: str, description: str, skills_text: str) -> str:
    """Assign a categorical subject to a course based on semantic keyword density."""
    text = f"{title} {description} {skills_text}".lower()

    categories = [
        ("Machine Learning", ["machine learning", "deep learning", "neural network", "artificial intelligence", "tensorflow", "pytorch", "mlops", "nlp", "computer vision"]),
        ("Data Science", ["data science", "data analysis", "statistics", "data visualization", "pandas", "numpy", "big data", "tableau"]),
        ("Web Development", ["web development", "html", "css", "javascript", "react", "angular", "vue", "frontend", "backend", "full stack", "node.js", "django", "fastapi"]),
        ("Programming Languages", ["python programming", "java programming", "c++ programming", "c# programming", "golang", "rust programming", "ruby programming", "coding", "data structures", "algorithms"]),
        ("Design", ["design", "photoshop", "illustrator", "figma", "ui/ux", "graphic design", "user experience", "typography"]),
        ("Marketing", ["marketing", "seo", "social media", "advertising", "branding", "content marketing", "digital marketing"]),
        ("Business", ["business", "management", "finance", "accounting", "entrepreneurship", "strategy", "leadership", "project management"]),
        ("IT & Software", ["cloud", "aws", "azure", "devops", "docker", "kubernetes", "linux", "networking", "cybersecurity", "security"]),
    ]

    for category, keywords in categories:
        if any(kw in text for kw in keywords):
            return category

    return "General"


def get_target_skills(job_role: str) -> List[str]:
    """Retrieve required target skills for a specific career role."""
    if not job_role:
        return ["Python", "JavaScript", "SQL", "Git", "Problem Solving"]

    resolved = resolve_role(job_role)
    if resolved and resolved in JOB_ROLE_MAPPING:
        return JOB_ROLE_MAPPING[resolved]["skills"]

    try:
        from app.data.career_understanding import career_understanding_service
        profile = career_understanding_service.lookup(job_role)
        if not profile and resolved:
            profile = career_understanding_service.lookup(resolved)
        if profile:
            return profile["skills"]
    except Exception:
        pass

    return ["Python", "JavaScript", "SQL", "Git", "Problem Solving"]


def get_relevant_subjects(job_role: str) -> List[str]:
    """Retrieve relevant domain subjects for a specific career role."""
    if not job_role:
        return ["Programming Languages", "Web Development", "Data Science", "IT & Software"]

    resolved = resolve_role(job_role)
    if resolved and resolved in JOB_ROLE_MAPPING:
        return JOB_ROLE_MAPPING[resolved]["subjects"]

    try:
        from app.data.career_understanding import career_understanding_service
        profile = career_understanding_service.lookup(job_role)
        if not profile and resolved:
            profile = career_understanding_service.lookup(resolved)
        if profile:
            return profile["subjects"]
    except Exception:
        pass

    return ["Programming Languages", "Web Development", "Data Science", "IT & Software"]
