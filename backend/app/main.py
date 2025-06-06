from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from backend.app.core.config import settings
from backend.app.api.api_v1.api import api_router
from enhanced_dictionary import EnhancedDictionary

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    print("Starting up and loading dictionary...")
    openai_api_key = os.getenv('OPENAI_API_KEY')
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    dictionary_path = os.path.join(project_root, "frontend/public/dictionary.json")
    if not os.path.exists(dictionary_path):
        # Fallback to repository root dictionary
        dictionary_path = os.path.join(project_root, "latin_dictionary.json")
    cache_db = os.path.join(project_root, "word_cache.db")
    
    app.state.enhanced_dictionary = EnhancedDictionary(
        dictionary_path=dictionary_path,
        openai_api_key=openai_api_key,
        cache_db=cache_db
    )
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