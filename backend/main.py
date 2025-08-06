from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
import os
import re
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://admirable-maamoul-860c44.netlify.app",
        "http://localhost:5173",  # React dev server
        "http://localhost:3000",  # Alternative dev server
        "https://*.netlify.app",  # Netlify domains
        "https://*.vercel.app",   # Vercel domains
        "https://*.railway.app",  # Railway domains
        "https://*.render.com",   # Render domains
        "https://*.herokuapp.com", # Heroku domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini API (you'll need to set your API key)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Use flash model for better rate limits
        print("✅ Gemini AI is configured and ready!")
    except Exception as e:
        print(f"❌ Gemini API configuration failed: {e}")
        gemini_model = None
else:
    print("⚠️  GEMINI_API_KEY not set. AI features will be disabled.")
    gemini_model = None

# Load both Udemy and Coursera courses
UDEMY_PATH = os.path.join(os.path.dirname(__file__), "data/udemy_courses.csv")
COURSERA_PATH = os.path.join(os.path.dirname(__file__), "data/Coursera.csv")

# Enhanced job role to subject mapping with skills
JOB_ROLE_MAPPING = {
    "Software Engineer": {
        "subjects": ["Web Development", "Programming Languages", "Software Engineering"],
        "skills": ["Python", "JavaScript", "Java", "React", "Node.js", "SQL", "Git", "Docker"],
        "next_roles": ["Senior Software Engineer", "Full Stack Developer", "Backend Engineer", "DevOps Engineer"]
    },
    "Data Scientist": {
        "subjects": ["Data Science", "Machine Learning", "Business Analytics"],
        "skills": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "Scikit-learn", "TensorFlow"],
        "next_roles": ["Senior Data Scientist", "ML Engineer", "Data Engineer", "AI Engineer"]
    },
    "Product Manager": {
        "subjects": ["Business", "Product Management", "Marketing"],
        "skills": ["Product Strategy", "User Research", "Agile", "SQL", "Analytics", "Leadership", "Communication"],
        "next_roles": ["Senior Product Manager", "Product Director", "VP Product", "Entrepreneur"]
    },
    "Digital Marketer": {
        "subjects": ["Marketing", "Business", "Digital Marketing"],
        "skills": ["SEO", "Google Ads", "Social Media", "Analytics", "Content Marketing", "Email Marketing"],
        "next_roles": ["Marketing Manager", "Digital Marketing Director", "Growth Hacker", "Marketing Consultant"]
    },
    "Graphic Designer": {
        "subjects": ["Design", "Graphic Design", "Web Design"],
        "skills": ["Photoshop", "Illustrator", "InDesign", "UI/UX", "Typography", "Color Theory"],
        "next_roles": ["Senior Designer", "Art Director", "UX Designer", "Creative Director"]
    },
    "Business Analyst": {
        "subjects": ["Business", "Business Analytics", "Data Science"],
        "skills": ["SQL", "Excel", "Tableau", "Power BI", "Business Intelligence", "Requirements Analysis"],
        "next_roles": ["Senior Business Analyst", "Data Analyst", "Product Manager", "Business Intelligence Manager"]
    },
    "DevOps Engineer": {
        "subjects": ["IT & Software", "Software Engineering", "Web Development"],
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Python", "Shell Scripting"],
        "next_roles": ["Senior DevOps Engineer", "Site Reliability Engineer", "Cloud Architect", "DevOps Manager"]
    },
    "UX Designer": {
        "subjects": ["Design", "Web Design", "User Experience"],
        "skills": ["Figma", "Sketch", "User Research", "Prototyping", "Information Architecture", "Usability Testing"],
        "next_roles": ["Senior UX Designer", "UX Manager", "Product Designer", "UX Director"]
    },
    "Data Analyst": {
        "subjects": ["Data Science", "Business Analytics", "Business"],
        "skills": ["SQL", "Excel", "Python", "Tableau", "Power BI", "Statistics", "Data Visualization"],
        "next_roles": ["Senior Data Analyst", "Business Intelligence Analyst", "Data Scientist", "Analytics Manager"]
    },
    "Project Manager": {
        "subjects": ["Business", "Project Management", "Leadership"],
        "skills": ["Agile", "Scrum", "JIRA", "Risk Management", "Leadership", "Communication", "Budgeting"],
        "next_roles": ["Senior Project Manager", "Program Manager", "Project Director", "Portfolio Manager"]
    },
    "Frontend Developer": {
        "subjects": ["Web Development", "Programming Languages", "Design"],
        "skills": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "Responsive Design"],
        "next_roles": ["Senior Frontend Developer", "Full Stack Developer", "Frontend Architect", "UI Developer"]
    },
    "Backend Developer": {
        "subjects": ["Web Development", "Programming Languages", "Software Engineering"],
        "skills": ["Python", "Java", "Node.js", "SQL", "APIs", "Database Design", "Server Management"],
        "next_roles": ["Senior Backend Developer", "Full Stack Developer", "Backend Architect", "API Developer"]
    },
    "Full Stack Developer": {
        "subjects": ["Web Development", "Programming Languages", "Software Engineering"],
        "skills": ["HTML", "CSS", "JavaScript", "Python", "Node.js", "SQL", "React", "APIs"],
        "next_roles": ["Senior Full Stack Developer", "Tech Lead", "Software Architect", "Engineering Manager"]
    },
    "Mobile Developer": {
        "subjects": ["Mobile Development", "Programming Languages", "Software Engineering"],
        "skills": ["Swift", "Kotlin", "React Native", "Flutter", "Mobile UI", "App Store", "Firebase"],
        "next_roles": ["Senior Mobile Developer", "Mobile Architect", "iOS/Android Lead", "Mobile Engineering Manager"]
    },
    "AI Engineer": {
        "subjects": ["Machine Learning", "Data Science", "Programming Languages"],
        "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "NLP", "Computer Vision"],
        "next_roles": ["Senior AI Engineer", "ML Engineer", "AI Research Scientist", "AI Product Manager"]
    },
    "Cybersecurity Analyst": {
        "subjects": ["IT & Software", "Network & Security", "Software Engineering"],
        "skills": ["Network Security", "Penetration Testing", "SIEM", "Incident Response", "Compliance", "Cryptography"],
        "next_roles": ["Senior Security Analyst", "Security Engineer", "Security Manager", "CISO"]
    },
    "Cloud Engineer": {
        "subjects": ["IT & Software", "Software Engineering", "Web Development"],
        "skills": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Linux", "Networking"],
        "next_roles": ["Senior Cloud Engineer", "Cloud Architect", "DevOps Engineer", "Cloud Manager"]
    },
    "QA Engineer": {
        "subjects": ["Software Engineering", "IT & Software", "Web Development"],
        "skills": ["Manual Testing", "Automated Testing", "Selenium", "JIRA", "Test Planning", "API Testing"],
        "next_roles": ["Senior QA Engineer", "Test Lead", "QA Manager", "Test Automation Engineer"]
    }
}

# Common skills for skill extraction
COMMON_SKILLS = [
    "Python", "JavaScript", "Java", "React", "Node.js", "SQL", "Git", "Docker", "AWS", "Machine Learning",
    "Data Science", "HTML", "CSS", "Angular", "Vue.js", "PHP", "C++", "C#", "Ruby", "Go", "Rust",
    "Swift", "Kotlin", "Flutter", "React Native", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
    "Tableau", "Power BI", "Excel", "Agile", "Scrum", "JIRA", "Figma", "Sketch", "Photoshop", "Illustrator",
    "SEO", "Google Ads", "Social Media", "Content Marketing", "Email Marketing", "Analytics", "Leadership"
]

def enhance_course_with_gemini(course):
    """Enhance course data using Gemini AI"""
    if not gemini_model:
        return course
    
    try:
        prompt = f"""
        Analyze this course and provide enhanced information:
        Title: {course['title']}
        Subject: {course['subject']}
        Level: {course['level']}
        Duration: {course['duration']}
        
        Please provide:
        1. A detailed description (2-3 sentences)
        2. Key skills taught (comma-separated)
        3. Difficulty level (Beginner/Intermediate/Advanced)
        4. Target audience
        5. Learning outcomes (3-4 points)
        
        Format as JSON:
        {{
            "description": "...",
            "skills": ["skill1", "skill2"],
            "difficulty": "...",
            "target_audience": "...",
            "learning_outcomes": ["outcome1", "outcome2", "outcome3"]
        }}
        """
        
        response = gemini_model.generate_content(prompt)
        # Parse the response and enhance the course
        # For now, we'll just add a note that Gemini is available
        course['ai_enhanced'] = True
        return course
    except Exception as e:
        print(f"Gemini API error: {e}")
        return course

def fetch_courses_with_gemini(job_role, skills=None):
    """Fetch courses using Gemini API"""
    if not gemini_model:
        return []
    
    try:
        prompt = f"""
        Find 5 relevant online courses for someone who wants to become a {job_role}.
        Skills they have: {skills or 'None specified'}
        
        Please provide courses from platforms like Coursera, edX, Udemy, etc.
        For each course, provide:
        - Course title
        - Platform (Coursera, edX, Udemy, etc.)
        - URL (if available)
        - Price (Free/Paid)
        - Duration
        - Level (Beginner/Intermediate/Advanced)
        - Key skills covered
        
        Format as a list of courses with these details.
        """
        
        response = gemini_model.generate_content(prompt)
        # Parse the response and convert to course format
        # This is a simplified version - you'd need to parse the response properly
        return []
    except Exception as e:
        print(f"Gemini API error: {e}")
        return []

def load_udemy_courses():
    """Load and process Udemy courses"""
    try:
        df = pd.read_csv(UDEMY_PATH)
        courses = []
        for _, row in df.iterrows():
            course = {
                "title": row["course_title"],
                "provider": "Udemy",
                "url": row["url"],
                "is_paid": bool(row["is_paid"] == True or row["is_paid"] == "True"),
                "price": row["price"],
                "num_subscribers": row["num_subscribers"],
                "level": row["level"],
                "duration": f"{row['content_duration']} hours",
                "subject": row["subject"],
                "description": f"{row['level']} course in {row['subject']} with {row['num_lectures']} lectures. {row['num_subscribers']} students enrolled.",
                "popularity_score": row["num_subscribers"] * (1 + row["num_reviews"] / 1000),
                "platform": "udemy",
                "rating": min(5.0, max(1.0, row.get("num_reviews", 0) / max(row["num_subscribers"], 1) * 10 + 3.5))
            }
            courses.append(course)
        return courses
    except Exception as e:
        print(f"Error loading Udemy courses: {e}")
        return []

def load_coursera_courses():
    """Load and process Coursera courses"""
    try:
        df = pd.read_csv(COURSERA_PATH)
        courses = []
        
        for _, row in df.iterrows():
            title = row.get("course_name", row.get("title", row.get("name", "Unknown Course")))
            url = row.get("course_url", row.get("url", ""))
            price = row.get("price", row.get("course_price", 0))
            level = row.get("level", row.get("difficulty", "All Levels"))
            subject = row.get("subject", row.get("category", "General"))
            duration = row.get("duration", row.get("course_duration", "Unknown"))
            
            if isinstance(duration, str) and "hour" not in duration.lower():
                duration = f"{duration} hours"
            elif not isinstance(duration, str):
                duration = f"{duration} hours"
            
            course = {
                "title": title,
                "provider": "Coursera",
                "url": url,
                "is_paid": price > 0 if isinstance(price, (int, float)) else True,
                "price": price if isinstance(price, (int, float)) else 0,
                "num_subscribers": row.get("enrolled", row.get("students", 0)),
                "level": level,
                "duration": duration,
                "subject": subject,
                "description": f"{level} course in {subject} on Coursera. {duration} duration.",
                "popularity_score": row.get("enrolled", 0) * 1.1,
                "platform": "coursera",
                "rating": min(5.0, max(1.0, row.get("rating", 4.2)))
            }
            courses.append(course)
        return courses
    except Exception as e:
        print(f"Error loading Coursera courses: {e}")
        return []

# Load all courses
print("Loading Udemy courses...")
udemy_courses = load_udemy_courses()
print(f"Loaded {len(udemy_courses)} Udemy courses")

print("Loading Coursera courses...")
coursera_courses = load_coursera_courses()
print(f"Loaded {len(coursera_courses)} Coursera courses")

# Combine all courses
courses = udemy_courses + coursera_courses
print(f"Total courses loaded: {len(courses)}")

# Extract unique job roles from subject and level
job_roles = sorted(list(set([c["subject"] for c in courses] + [c["level"] for c in courses])))

# Prepare course corpus for ML (title + subject + level + description)
def course_corpus(courses):
    return [f"{c['title']} {c['subject']} {c['level']} {c['description']}" for c in courses]

corpus = course_corpus(courses)
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X = vectorizer.fit_transform(corpus)

def extract_skills_from_text(text):
    """Extract skills from text using common skills list"""
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills

def get_relevant_subjects_and_skills(job_role, user_skills=None):
    """Get relevant subjects and skills for a job role"""
    if job_role in JOB_ROLE_MAPPING:
        role_data = JOB_ROLE_MAPPING[job_role]
        return role_data["subjects"], role_data["skills"]
    
    job_role_lower = job_role.lower()
    relevant_subjects = []
    relevant_skills = []
    
    for role, data in JOB_ROLE_MAPPING.items():
        if any(word in job_role_lower for word in role.lower().split()):
            relevant_subjects.extend(data["subjects"])
            relevant_skills.extend(data["skills"])
    
    if not relevant_subjects:
        relevant_subjects = ["Web Development", "Programming Languages", "Business", "Data Science"]
    if not relevant_skills:
        relevant_skills = ["Python", "JavaScript", "SQL", "Leadership"]
    
    return list(set(relevant_subjects)), list(set(relevant_skills))

def calculate_skill_match(course, user_skills):
    """Calculate how well a course matches user skills"""
    if not user_skills:
        return 0
    
    course_text = f"{course['title']} {course['description']}".lower()
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    matches = sum(1 for skill in user_skills_lower if skill in course_text)
    return matches / len(user_skills) if user_skills else 0

@app.get("/")
def read_root():
    return {
        "message": "Upskill Recommender API is running!", 
        "total_courses": len(courses),
        "gemini_available": gemini_model is not None
    }

@app.get("/job_roles", response_model=List[str])
def get_job_roles():
    return job_roles

@app.get("/platforms")
def get_platforms():
    """Get available platforms"""
    platforms = list(set([c["provider"] for c in courses]))
    return {"platforms": platforms}

@app.get("/skills")
def get_skills():
    """Get available skills"""
    return {"skills": COMMON_SKILLS}

@app.get("/career_path/{job_role}")
def get_career_path(job_role: str):
    """Get career path suggestions for a job role"""
    job_role_lower = job_role.lower()
    
    # Check if we have a predefined mapping
    if job_role in JOB_ROLE_MAPPING:
        role_data = JOB_ROLE_MAPPING[job_role]
        return {
            "current_role": job_role,
            "next_roles": role_data["next_roles"],
            "required_skills": role_data["skills"],
            "relevant_subjects": role_data["subjects"]
        }
    
    # For custom roles, generate intelligent career paths
    next_roles = []
    required_skills = []
    relevant_subjects = []
    
    # Analyze the job role and suggest career progression
    if any(word in job_role_lower for word in ["engineer", "developer", "programmer"]):
        next_roles = ["Senior " + job_role, "Tech Lead", "Software Architect", "Engineering Manager"]
        required_skills = ["Leadership", "System Design", "Architecture", "Team Management", "Advanced Programming"]
        relevant_subjects = ["Software Engineering", "Computer Science", "System Design"]
    elif any(word in job_role_lower for word in ["analyst", "data"]):
        next_roles = ["Senior " + job_role, "Data Scientist", "Business Intelligence Manager", "Analytics Director"]
        required_skills = ["Advanced Analytics", "Machine Learning", "Statistics", "Business Intelligence", "Leadership"]
        relevant_subjects = ["Data Science", "Business Analytics", "Statistics"]
    elif any(word in job_role_lower for word in ["manager", "lead", "director"]):
        next_roles = ["Senior " + job_role, "Director", "VP", "C-Level Executive"]
        required_skills = ["Strategic Planning", "Leadership", "Business Strategy", "Financial Management", "Team Building"]
        relevant_subjects = ["Business", "Management", "Leadership"]
    elif any(word in job_role_lower for word in ["designer", "ux", "ui"]):
        next_roles = ["Senior " + job_role, "Design Lead", "Creative Director", "UX Director"]
        required_skills = ["Design Systems", "User Research", "Prototyping", "Leadership", "Design Strategy"]
        relevant_subjects = ["Design", "User Experience", "Visual Design"]
    elif any(word in job_role_lower for word in ["marketing", "marketer"]):
        next_roles = ["Senior " + job_role, "Marketing Manager", "Marketing Director", "CMO"]
        required_skills = ["Digital Marketing", "Analytics", "Strategy", "Leadership", "Campaign Management"]
        relevant_subjects = ["Marketing", "Digital Marketing", "Business"]
    elif any(word in job_role_lower for word in ["scientist", "researcher"]):
        next_roles = ["Senior " + job_role, "Research Lead", "Research Director", "Chief Scientist"]
        required_skills = ["Advanced Research", "Methodology", "Leadership", "Publication", "Grant Writing"]
        relevant_subjects = ["Research", "Science", "Methodology"]
    elif any(word in job_role_lower for word in ["consultant", "advisor"]):
        next_roles = ["Senior " + job_role, "Principal Consultant", "Partner", "Managing Director"]
        required_skills = ["Client Management", "Business Development", "Strategy", "Leadership", "Industry Expertise"]
        relevant_subjects = ["Business", "Consulting", "Strategy"]
    elif any(word in job_role_lower for word in ["sales", "account"]):
        next_roles = ["Senior " + job_role, "Sales Manager", "Sales Director", "VP of Sales"]
        required_skills = ["Sales Strategy", "Team Management", "Business Development", "Leadership", "Customer Success"]
        relevant_subjects = ["Sales", "Business", "Customer Success"]
    elif any(word in job_role_lower for word in ["support", "help", "customer"]):
        next_roles = ["Senior " + job_role, "Support Manager", "Customer Success Manager", "Support Director"]
        required_skills = ["Customer Success", "Process Improvement", "Leadership", "Analytics", "Team Management"]
        relevant_subjects = ["Customer Service", "Business", "Process Management"]
    elif any(word in job_role_lower for word in ["admin", "coordinator", "assistant"]):
        next_roles = ["Senior " + job_role, "Manager", "Director", "VP"]
        required_skills = ["Leadership", "Process Management", "Strategic Planning", "Team Management", "Business Acumen"]
        relevant_subjects = ["Business", "Management", "Administration"]
    else:
        # Generic career progression for unknown roles
        next_roles = ["Senior " + job_role, "Lead " + job_role, "Manager", "Director"]
        required_skills = ["Leadership", "Strategic Thinking", "Communication", "Problem Solving", "Industry Expertise"]
        relevant_subjects = ["Business", "Leadership", "Industry-specific Skills"]
    
    return {
        "current_role": job_role,
        "next_roles": next_roles,
        "required_skills": required_skills,
        "relevant_subjects": relevant_subjects
    }

@app.get("/ai_courses")
def get_ai_courses(
    job_role: str = Query(..., description="Job role to find courses for"),
    skills: Optional[str] = Query(None, description="User skills")
):
    """Get AI-generated course recommendations using Gemini"""
    if not gemini_model:
        return {"error": "Gemini API not configured", "courses": []}
    
    try:
        ai_courses = fetch_courses_with_gemini(job_role, skills)
        return {"courses": ai_courses, "source": "Gemini AI"}
    except Exception as e:
        return {"error": str(e), "courses": []}

@app.get("/recommendations")
def get_recommendations(
    job_role: str = Query(..., description="Current job role"),
    paid: Optional[bool] = Query(None, description="Set to true for paid, false for free, omit for all"),
    platform: Optional[str] = Query(None, description="Filter by platform (Udemy, Coursera, or omit for all)"),
    user_skills: Optional[str] = Query(None, description="Comma-separated list of user skills"),
    goal: Optional[str] = Query(None, description="User's learning goal"),
    use_ai: Optional[bool] = Query(False, description="Use AI to enhance recommendations")
):
    # Filter by paid/free if specified
    filtered_courses = [c for c in courses if (paid is None or c["is_paid"] == paid)]
    
    # Filter by platform if specified
    if platform:
        filtered_courses = [c for c in filtered_courses if c["provider"].lower() == platform.lower()]
    
    if not filtered_courses:
        return {"job_role": job_role, "recommendations": []}
    
    # Parse user skills
    skills_list = []
    if user_skills:
        skills_list = [skill.strip() for skill in user_skills.split(",") if skill.strip()]
    
    # Get relevant subjects and skills for the job role
    relevant_subjects, relevant_skills = get_relevant_subjects_and_skills(job_role, skills_list)
    
    # Recompute corpus and X for filtered courses
    filtered_corpus = course_corpus(filtered_courses)
    X_filtered = vectorizer.transform(filtered_corpus)
    job_role_vec = vectorizer.transform([job_role])
    similarities = cosine_similarity(job_role_vec, X_filtered).flatten()
    
    # Combine similarity with subject relevance, popularity, and skill matching
    scored_courses = []
    for i, course in enumerate(filtered_courses):
        similarity_score = similarities[i]
        subject_bonus = 0.3 if course["subject"] in relevant_subjects else 0
        popularity_bonus = min(course["popularity_score"] / 10000, 0.2)
        
        # Skill matching bonus
        skill_bonus = 0
        if skills_list:
            skill_match = calculate_skill_match(course, skills_list)
            skill_bonus = skill_match * 0.4
        
        # Goal-based bonus
        goal_bonus = 0
        if goal and goal.lower() in course["title"].lower():
            goal_bonus = 0.3
        
        final_score = similarity_score + subject_bonus + popularity_bonus + skill_bonus + goal_bonus
        scored_courses.append((course, final_score))
    
    # Sort by final score and return top recommendations
    scored_courses.sort(key=lambda x: x[1], reverse=True)
    recommended = [course for course, score in scored_courses if score > 0][:8]
    
    # Enhance with AI if requested
    if use_ai and gemini_model:
        for course in recommended:
            course = enhance_course_with_gemini(course)
    
    return {
        "job_role": job_role,
        "recommendations": recommended,
        "total_filtered": len(filtered_courses),
        "relevant_skills": relevant_skills,
        "skill_match_count": len([c for c in recommended if calculate_skill_match(c, skills_list) > 0]),
        "ai_enhanced": use_ai and gemini_model is not None
    }