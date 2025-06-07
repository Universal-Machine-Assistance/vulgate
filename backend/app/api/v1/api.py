from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import verses, words, books, analysis, dictionary

api_router = APIRouter()

# Use the unified endpoints under api_v1 to prevent path duplication
api_router.include_router(verses.router, prefix="/verses", tags=["verses"])
api_router.include_router(words.router, prefix="/words", tags=["words"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(dictionary.router, prefix="/dictionary", tags=["dictionary"]) 