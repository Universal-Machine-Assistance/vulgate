from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from backend.app.core.config import settings
from backend.app.api.api_v1.api import api_router
from backend.app.services.enhanced_dictionary import EnhancedDictionary  # noqa

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("Starting up and loading dictionary...")
    print("DEBUG OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
    # Instantiate the service-layer EnhancedDictionary (uses settings for DB path and env var for OpenAI key)
    app.state.enhanced_dictionary = EnhancedDictionary()
    print("Dictionary loaded.")
    yield
    # Clean up the ML models and release the resources
    print("Shutting down.")

app = FastAPI(
    title="Vulgate API",
    description="API for the Vulgate Bible study and recording application",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS - specifically allow localhost:3000 for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Common alternative port
        "*"  # Allow all for development - remove in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for audio storage
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Vulgate API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 