from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.services.enhanced_dictionary import EnhancedDictionary

router = APIRouter()

@router.get("/{word}/verses")
def get_word_verses(
    word: str,
    language: str = "la",
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all verses where a word appears"""
    try:
        dictionary = EnhancedDictionary(database_path=settings.SQLITE_DB_PATH)
        verses = dictionary.get_verses_for_word(word, language)
        return verses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{word}/definition")
def get_word_definition(
    word: str,
    language: str = "la",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get word definition from cache or generate new one"""
    try:
        dictionary = EnhancedDictionary(database_path=settings.SQLITE_DB_PATH)
        definition = dictionary.get_from_cache(word, language)
        if not definition:
            raise HTTPException(status_code=404, detail="Word not found")
        return definition
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 