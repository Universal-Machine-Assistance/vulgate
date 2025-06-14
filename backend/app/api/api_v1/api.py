from fastapi import APIRouter
from backend.app.api.api_v1.endpoints import verses, words, audio, books, users, dictionary, analysis, themes, images, texts

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(verses.router, prefix="/verses", tags=["verses"])
api_router.include_router(texts.router, prefix="/texts", tags=["texts"])  # New unified texts endpoint
api_router.include_router(words.router, prefix="/words", tags=["words"])
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dictionary.router, prefix="/dictionary", tags=["dictionary"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])
api_router.include_router(images.router, prefix="/images", tags=["images"]) 