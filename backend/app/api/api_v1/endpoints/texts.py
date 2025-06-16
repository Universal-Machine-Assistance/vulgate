from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.verse import Verse
from backend.app.db.models import Book, Verse as VerseModel
from backend.app.crud import crud_verse, crud_book
from backend.app.api.api_v1.endpoints.books import BOOK_ABBREVIATIONS

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

# Note: Bhagavad Gita endpoints are now handled by the unified endpoints below
# This provides a consistent API structure for both Bible and Gita

# Old Gita endpoint removed - now handled by unified /{source}/{book_abbr}/{chapter}/{verse} endpoint

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

@router.get("/{source}/{book_abbr}/{chapter}", response_model=List[Verse])
async def get_chapter_verses(
    *,
    db: Session = Depends(deps.get_db),
    source: str = Path(
        ...,
        description="Text source (bible or gita)",
        example="bible"
    ),
    book_abbr: str = Path(
        ...,
        description="Book abbreviation (e.g., 'Gn' for Genesis, 'a' for Bhagavad Gita)",
        example="Gn"
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
    Get verses from a chapter of any text source.
    
    Supports both Bible and Bhagavad Gita with unified structure:
    - Bible: /api/v1/texts/bible/Gn/1 (Genesis Chapter 1)
    - Gita: /api/v1/texts/gita/a/1 (Bhagavad Gita Chapter 1)
    
    The 'a' abbreviation for Gita maintains consistency with the book/chapter/verse structure.
    """
    
    if source not in ["bible", "gita"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source '{source}'. Must be 'bible' or 'gita'"
        )
    
    # Get the book by source and handle abbreviation logic
    if source == "bible":
        # For Bible, use the existing BOOK_ABBREVIATIONS mapping
        book_id = BOOK_ABBREVIATIONS.get(book_abbr)
        if not book_id:
            raise HTTPException(
                status_code=404,
                detail=f"Book abbreviation '{book_abbr}' not found for Bible"
            )
        book = db.query(Book).filter(Book.id == book_id).first()
    elif source == "gita":
        # For Gita, book_abbr should be "a" and we look for the Gita book
        if book_abbr != "a":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Gita book identifier: {book_abbr} (should be 'a')"
            )
        book = db.query(Book).filter(
            Book.source == "gita",
            Book.name == "Bhagavad Gita"
        ).first()
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book '{book_abbr}' not found for source '{source}'"
        )
    
    # Get verses from the database
    verses = db.query(VerseModel).filter(
        VerseModel.book_id == book.id,
        VerseModel.chapter == chapter
    ).order_by(VerseModel.verse_number).offset(skip).limit(limit).all()
    
    if not verses:
        raise HTTPException(
            status_code=404,
            detail=f"No verses found for {source} {book_abbr} chapter {chapter}"
        )
    
    return verses

@router.get("/{source}/{book_abbr}/{chapter}/{verse}", response_model=Verse)
async def get_specific_verse(
    *,
    db: Session = Depends(deps.get_db),
    source: str = Path(
        ...,
        description="Text source (bible or gita)",
        example="bible"
    ),
    book_abbr: str = Path(
        ...,
        description="Book abbreviation (e.g., 'Gn' for Genesis, 'a' for Bhagavad Gita)",
        example="Gn"
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
    Get a specific verse from any text source.
    
    Examples:
    - Bible: /api/v1/texts/bible/Gn/1/1 (Genesis 1:1)
    - Gita: /api/v1/texts/gita/a/1/1 (Bhagavad Gita Chapter 1, Verse 1)
    """
    
    if source not in ["bible", "gita"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source '{source}'. Must be 'bible' or 'gita'"
        )
    
    # Get the book by source and handle abbreviation logic
    if source == "bible":
        # For Bible, use the existing BOOK_ABBREVIATIONS mapping
        book_id = BOOK_ABBREVIATIONS.get(book_abbr)
        if not book_id:
            raise HTTPException(
                status_code=404,
                detail=f"Book abbreviation '{book_abbr}' not found for Bible"
            )
        book = db.query(Book).filter(Book.id == book_id).first()
    elif source == "gita":
        # For Gita, book_abbr should be "a" and we look for the Gita book
        if book_abbr != "a":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid Gita book identifier: {book_abbr} (should be 'a')"
            )
        book = db.query(Book).filter(
            Book.source == "gita",
            Book.name == "Bhagavad Gita"
        ).first()
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book '{book_abbr}' not found for source '{source}'"
        )
    
    # Get the specific verse
    verse_obj = db.query(VerseModel).filter(
        VerseModel.book_id == book.id,
        VerseModel.chapter == chapter,
        VerseModel.verse_number == verse
    ).first()
    
    if not verse_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Verse {source} {book_abbr} {chapter}:{verse} not found"
        )
    
    return verse_obj 