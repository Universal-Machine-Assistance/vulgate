from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.verse import Verse
from backend.app.schemas.book import Book
from backend.app.crud import crud_verse, crud_book
from backend.app.api.api_v1.endpoints.books import BOOK_ABBREVIATIONS
from backend.app.services.bhagavad_gita_service import bhagavad_gita_service

router = APIRouter()

# Bible endpoints (existing functionality)
@router.get("/bible/{abbr}/{chapter}", response_model=List[Verse])
async def get_bible_chapter(
    *,
    db: Session = Depends(deps.get_db),
    abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
    chapter: int = Path(
        ...,
        ge=1,
        description="Chapter number",
        example=1
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of verses to skip",
        example=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of verses to return",
        example=100
    ),
):
    """
    Get verses from a Bible book by abbreviation and chapter.

    This endpoint allows you to retrieve verses using the traditional book abbreviation
    and chapter number (e.g., '/bible/Gn/1' for Genesis chapter 1).

    Common book abbreviations:
    - Gn: Genesis
    - Ex: Exodus
    - Lev: Leviticus
    - Num: Numbers
    - Dt: Deuteronomy
    - Mt: Matthew
    - Mc: Mark
    - Lc: Luke
    - Jo: John
    - Ac: Acts
    - Ap: Revelation

    Example URLs:
    - GET /api/v1/texts/bible/Gn/1 - Get Genesis chapter 1
    - GET /api/v1/texts/bible/Mt/1 - Get Matthew chapter 1
    """
    book_id = BOOK_ABBREVIATIONS.get(abbr)
    if not book_id:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis."
        )
    
    verses = crud_verse.get_verses(
        db=db,
        skip=skip,
        limit=limit,
        book_id=book_id,
        chapter=chapter
    )
    
    if not verses:
        raise HTTPException(
            status_code=404,
            detail=f"No verses found for {abbr} chapter {chapter}"
        )
    
    return verses

@router.get("/bible/{abbr}/{chapter}/{verse}", response_model=Verse)
async def get_bible_verse(
    *,
    db: Session = Depends(deps.get_db),
    abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
    chapter: int = Path(
        ...,
        ge=1,
        description="Chapter number",
        example=1
    ),
    verse: int = Path(
        ...,
        ge=1,
        description="Verse number",
        example=1
    ),
):
    """
    Get a specific verse from the Bible by book abbreviation, chapter, and verse number.

    Example URLs:
    - GET /api/v1/texts/bible/Gn/1/1 - Get Genesis 1:1
    - GET /api/v1/texts/bible/Mt/5/3 - Get Matthew 5:3
    """
    book_id = BOOK_ABBREVIATIONS.get(abbr)
    if not book_id:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis."
        )
    
    verse_obj = crud_verse.get_verse_by_reference(
        db=db,
        book_id=book_id,
        chapter=chapter,
        verse_number=verse
    )
    
    if not verse_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Verse {abbr} {chapter}:{verse} not found"
        )
    
    return verse_obj

# Bhagavad Gita endpoints using unified structure (gita/a/chapter/verse)
@router.get("/gita/a/{chapter}", response_model=List[Verse])
async def get_gita_chapter(
    *,
    db: Session = Depends(deps.get_db),
    chapter: int = Path(
        ...,
        ge=1,
        le=18,
        description="Chapter number (1-18)",
        example=1
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of verses to skip",
        example=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of verses to return",
        example=100
    ),
):
    """
    Get verses from a Bhagavad Gita chapter using unified structure.

    The Bhagavad Gita has 18 chapters. This endpoint fetches verses from the specified chapter,
    caching them locally for faster subsequent access. Uses 'a' as the book abbreviation
    to maintain consistency with the Bible structure.

    Example URLs:
    - GET /api/v1/texts/gita/a/1 - Get Bhagavad Gita chapter 1
    - GET /api/v1/texts/gita/a/2 - Get Bhagavad Gita chapter 2
    """
    try:
        # Check if we have cached verses locally first
        gita_book = bhagavad_gita_service.get_or_create_gita_book(db)
        
        existing_verses = crud_verse.get_verses(
            db=db,
            skip=skip,
            limit=limit,
            book_id=gita_book.id,
            chapter=chapter
        )
        
        if existing_verses:
            return existing_verses
        
        # If no cached verses, fetch from API and cache
        verses = await bhagavad_gita_service.cache_chapter_locally(db, chapter)
        
        # Apply pagination to the fetched verses
        return verses[skip:skip + limit]
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching Bhagavad Gita chapter {chapter}: {str(e)}")

@router.get("/gita/a/{chapter}/{verse}", response_model=Verse)
async def get_gita_verse(
    *,
    db: Session = Depends(deps.get_db),
    chapter: int = Path(
        ...,
        ge=1,
        le=18,
        description="Chapter number (1-18)",
        example=1
    ),
    verse: int = Path(
        ...,
        ge=1,
        description="Verse number",
        example=1
    ),
):
    """
    Get a specific verse from the Bhagavad Gita using unified structure.

    Uses 'a' as the book abbreviation to maintain consistency with Bible structure.

    Example URLs:
    - GET /api/v1/texts/gita/a/1/1 - Get Bhagavad Gita chapter 1, verse 1
    - GET /api/v1/texts/gita/a/2/47 - Get Bhagavad Gita chapter 2, verse 47
    """
    try:
        # Try to get from local cache first
        gita_book = bhagavad_gita_service.get_or_create_gita_book(db)
        
        existing_verse = crud_verse.get_verse_by_reference(
            db=db,
            book_id=gita_book.id,
            chapter=chapter,
            verse_number=verse
        )
        
        if existing_verse:
            return existing_verse
        
        # If not cached, fetch from API and cache
        verse_obj = await bhagavad_gita_service.cache_verse_locally(db, chapter, verse)
        return verse_obj
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching Bhagavad Gita verse {chapter}:{verse}: {str(e)}")

# Unified endpoints for both sources
@router.get("/sources", response_model=List[str])
async def get_available_sources():
    """
    Get a list of available text sources.
    
    Returns:
    - bible: The Vulgate Bible
    - gita: The Bhagavad Gita
    """
    return ["bible", "gita"]

@router.get("/sources/{source}/info")
async def get_source_info(
    source: str = Path(..., description="Source name: 'bible' or 'gita'"),
    db: Session = Depends(deps.get_db)
):
    """
    Get information about a specific text source.
    """
    if source == "bible":
        bible_books = db.query(crud_book.model).filter(
            crud_book.model.source == 'bible'
        ).count()
        return {
            "source": "bible",
            "name": "Vulgate Bible",
            "description": "The Latin Vulgate Bible by Saint Jerome",
            "books_count": bible_books,
            "language": "Latin",
            "abbreviations": list(BOOK_ABBREVIATIONS.keys())
        }
    elif source == "gita":
        return {
            "source": "gita",
            "name": "Bhagavad Gita",
            "description": "The sacred Hindu scripture",
            "books_count": 1,
            "chapters_count": 18,
            "language": "Sanskrit",
            "note": "Fetched from RapidAPI and cached locally"
        }
    else:
        raise HTTPException(status_code=404, detail="Source not found. Available sources: 'bible', 'gita'")

# Legacy compatibility endpoints (redirect to new structure)
@router.get("/by-reference/{abbr}/{chapter}", response_model=List[Verse])
async def legacy_get_verses_by_reference(
    abbr: str,
    chapter: int, 
    db: Session = Depends(deps.get_db),
    skip: int = Query(default=0),
    limit: int = Query(default=100)
):
    """Legacy endpoint - redirects to /bible/{abbr}/{chapter}"""
    return await get_bible_chapter(
        db=db, abbr=abbr, chapter=chapter, skip=skip, limit=limit
    )

@router.get("/by-reference/{abbr}/{chapter}/{verse}", response_model=Verse)
async def legacy_get_verse_by_reference(
    abbr: str,
    chapter: int,
    verse: int,
    db: Session = Depends(deps.get_db)
):
    """Legacy endpoint - redirects to /bible/{abbr}/{chapter}/{verse}"""
    return await get_bible_verse(db=db, abbr=abbr, chapter=chapter, verse=verse) 