"""
Upskill Recommender Application Entry Point (Module).
Configures FastAPI, CORS middleware, startup lifecycle, and router inclusion.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from app.api.routes import router
from app.services.recommender import recommender_service
from app.services.gemini import initialize_gemini

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler: Initializes datasets and pre-computes TF-IDF vectors."""
    logger.info("Starting Upskill Recommender backend application lifecycle...")
    initialize_gemini()
    recommender_service.initialize()
    yield
    logger.info("Shutting down Upskill Recommender backend...")


app = FastAPI(
    title="Upskill Recommender API",
    description="AI-powered course recommendation engine for career upskilling with explainable hybrid scoring",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration supporting multi-environment deployment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)
