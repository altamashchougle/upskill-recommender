# Upskill Recommender


An intelligent system that provides AI-powered course and career path recommendations to help users upskill effectively based on their current role and career goals.

## Table of Contents

- [About The Project](#about-the-project)
  - [Key Features](#key-features)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## About The Project

In a rapidly evolving job market, knowing which skills to learn next is a major challenge. The Upskill Recommender solves this by leveraging AI to analyze a user's profile and career aspirations, delivering a personalized roadmap for professional growth.

### Key Features

✨ **AI-Powered Insights:** Utilizes Large Language Models (via Gemini API) for smart recommendations.
🎯 **Career Path Suggestions:** Maps out potential career trajectories and the skills required.
🔍 **Advanced Filtering & Real-time Search:** Easily find the most relevant courses and skills.
📱 **Beautiful Responsive UI:** A clean and modern user interface that works on any device.

### Built With

This project is built with a modern tech stack:

*   **Backend:**
    *   [Python](https://www.python.org/)
    *   [FastAPI](https://fastapi.tiangolo.com/)
    *   [Scikit-learn](https://scikit-learn.org/)
    *   [Pandas](https://pandas.pydata.org/)
*   **Frontend:**
    *   [Vite](https://vitejs.dev/)
    *   [React](https://reactjs.org/) (or your framework of choice)
*   **AI:**
    *   [Google Gemini](https://ai.google.dev/)

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

Ensure you have the following installed:
*   Python 3.9+
*   Node.js & npm (or your preferred package manager)

### Installation

1.  **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/upskill-recommender.git
    cd upskill-recommender
    ```

2.  **Setup Backend**
    ```sh
    # Navigate to the backend directory (if you have one)
    # cd backend 

    # Create and activate a virtual environment
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Setup Frontend**
    ```sh
    # Navigate to the frontend directory
    cd frontend

    # Install npm packages
    npm install
    ```

4.  **Environment Variables**
    *   In the root of the backend directory, create a `.env` file and add your API key:
        ```
        GEMINI_API_KEY="your-api-key"
        ```
    *   In the `frontend` directory, create a `.env.local` file to point to your local backend:
        ```
        VITE_API_URL="http://127.0.0.1:8000"
        ```

## Usage

1.  **Run the Backend Server**
    In your backend directory, with the virtual environment activated:
    ```sh
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`. You can explore the interactive docs at `http://127.0.0.1:8000/docs`.

2.  **Run the Frontend App**
    In a separate terminal, from the `frontend` directory:
    ```sh
    npm run dev
    ```
    Open http://localhost:5173 (or the port specified by Vite) in your browser to see the application.

## Deployment

This application is ready for deployment on modern hosting platforms. For detailed, step-by-step instructions on deploying the frontend to Netlify and the backend to services like Railway or Render, please see our complete guide:

➡️ **Deployment Guide (DEPLOYMENT.md)**





