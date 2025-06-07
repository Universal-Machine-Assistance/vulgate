from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.services.vulgate_analyzer import VulgateAnalyzer
from backend.app.schemas.verse import VerseAnalysisResponse, Verse

router = APIRouter()

@router.get("/{book}/{chapter}/{verse}", response_model=VerseAnalysisResponse)
def analyze_verse(
    book: str,
    chapter: int,
    verse: int,
    language: str = "la",
    db: Session = Depends(get_db)
):
    """Analyze a verse with caching and language support"""
    try:
        analyzer = VulgateAnalyzer(
            openai_api_key=settings.OPENAI_API_KEY,
            database_path=settings.SQLITE_DB_PATH
        )
        
        # Get analysis with specified language
        analysis = analyzer.analyze_verse(book, chapter, verse, language)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Verse not found")
            
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/words/{word}/verses")
def get_word_verses(
    word: str,
    language: str = "la",
    db: Session = Depends(get_db)
):
    """Get all verses where a word appears"""
    try:
        analyzer = VulgateAnalyzer(
            openai_api_key=settings.OPENAI_API_KEY,
            database_path=settings.SQLITE_DB_PATH
        )
        
        # Get verses for the word in specified language
        verses = analyzer.dictionary.get_verses_for_word(word, language)
        
        return verses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-reference/{book}/{chapter}", response_model=List[Verse])
def get_verses_by_reference(
    book: str,
    chapter: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get verses for a specific book and chapter with pagination"""
    try:
        analyzer = VulgateAnalyzer(
            openai_api_key=settings.OPENAI_API_KEY,
            database_path=settings.SQLITE_DB_PATH
        )
        
        verses = analyzer.get_verses_by_reference(book, chapter, skip, limit)
        
        if not verses:
            raise HTTPException(status_code=404, detail="No verses found")
            
        return verses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 