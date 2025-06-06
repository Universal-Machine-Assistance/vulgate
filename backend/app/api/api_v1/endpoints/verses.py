from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.verse import Verse, VerseCreate, VerseUpdate
from backend.app.crud import crud_verse
from backend.app.api.api_v1.endpoints.books import BOOK_ABBREVIATIONS

router = APIRouter()

@router.get("/", response_model=List[Verse])
def read_verses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    book_id: Optional[int] = None,
    chapter: Optional[int] = None,
):
    """
    Retrieve verses with optional filtering by book and chapter.
    """
    verses = crud_verse.get_verses(
        db, skip=skip, limit=limit, book_id=book_id, chapter=chapter
    )
    return verses

@router.post("/", response_model=Verse)
def create_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_in: VerseCreate,
):
    """
    Create new verse.
    """
    verse = crud_verse.create(db=db, obj_in=verse_in)
    return verse

@router.get("/{verse_id}", response_model=Verse)
def read_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_id: int,
):
    """
    Get verse by ID.
    """
    verse = crud_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    return verse

@router.put("/{verse_id}", response_model=Verse)
def update_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_id: int,
    verse_in: VerseUpdate,
):
    """
    Update verse.
    """
    verse = crud_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    verse = crud_verse.update(db=db, db_obj=verse, obj_in=verse_in)
    return verse

@router.delete("/{verse_id}")
def delete_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_id: int,
):
    """
    Delete verse.
    """
    verse = crud_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="Verse not found")
    verse = crud_verse.remove(db=db, id=verse_id)
    return {"status": "success"}

@router.get("/search/", response_model=List[Verse])
def search_verses(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 100,
):
    """
    Search verses by text content.
    """
    verses = crud_verse.search_verses(
        db=db, query=query, skip=skip, limit=limit
    )
    return verses

@router.get("/by-reference/{abbr}/{chapter}", response_model=List[Verse])
def read_verses_by_reference(
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
    Get verses by book abbreviation and chapter.

    This endpoint allows you to retrieve verses using the traditional book abbreviation
    and chapter number (e.g., 'Gn/1' for Genesis chapter 1).

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
    - GET /api/v1/verses/by-reference/Gn/1 - Get Genesis chapter 1
    - GET /api/v1/verses/by-reference/Ex/1 - Get Exodus chapter 1
    - GET /api/v1/verses/by-reference/Mt/1 - Get Matthew chapter 1
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

@router.get("/by-reference/{abbr}/{chapter}/{verse}", response_model=Verse)
def read_verse_by_reference(
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
    Get a specific verse by book abbreviation, chapter, and verse number.

    This endpoint allows you to retrieve a specific verse using the traditional book abbreviation,
    chapter number, and verse number (e.g., 'Gn/1/1' for Genesis chapter 1 verse 1).

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
    - GET /api/v1/verses/by-reference/Gn/1/1 - Get Genesis 1:1
    - GET /api/v1/verses/by-reference/Ex/1/1 - Get Exodus 1:1
    - GET /api/v1/verses/by-reference/Mt/1/1 - Get Matthew 1:1
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
            detail=f"Verse not found: {abbr} {chapter}:{verse}"
        )
    
    return verse_obj 