from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import verses, words, audio, books, users, dictionary, analysis

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(verses.router, prefix="/verses", tags=["verses"])
api_router.include_router(words.router, prefix="/words", tags=["words"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dictionary.router, prefix="/dictionary", tags=["dictionary"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"]) 