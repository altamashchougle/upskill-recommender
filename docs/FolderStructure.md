# Project Directory Structure

```text
upskill-recommender/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── cache/
│   │   │   └── gemini_cache.py
│   │   ├── data/
│   │   │   ├── loader.py
│   │   │   ├── taxonomy.py
│   │   │   ├── career_understanding.py
│   │   │   └── career_expansion.py
│   │   ├── ml/
│   │   │   ├── scoring.py
│   │   │   └── vectorizer.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── recommender.py
│   │   │   ├── gemini.py
│   │   │   ├── gemini_client.py
│   │   │   └── model_router.py
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── dashboard/
│   │   │   └── onboarding/
│   │   ├── context/
│   │   │   └── AppContext.jsx
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   └── OnboardingPage.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── docs/
│   ├── screenshots/
│   ├── Architecture.md
│   ├── API.md
│   ├── Backend.md
│   ├── Caching.md
│   ├── CareerEngine.md
│   ├── Deployment.md
│   ├── FolderStructure.md
│   ├── Frontend.md
│   ├── LLMOps.md
│   └── Testing.md
└── README.md
```
