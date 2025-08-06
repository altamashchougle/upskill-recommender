# Upskill Recommender

A lightweight web app that helps users discover relevant free online courses based on their current job role.

## Tech Stack
- Backend: FastAPI (Python)
- ML: scikit-learn, pandas
- Data: JSON/CSV (sample provided)

## Setup (Backend)
1. Create and activate a virtual environment (if not already):
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Mac/Linux
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```
   uvicorn backend.main:app --reload
   ```
4. Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

## Next Steps
- Add ML logic for smarter recommendations
- Build a React frontend