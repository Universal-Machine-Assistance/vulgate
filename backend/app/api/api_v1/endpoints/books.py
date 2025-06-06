from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.schemas.book import Book, BookCreate, BookUpdate
from backend.app.crud import crud_book

router = APIRouter()

# Common book IDs and names for reference
COMMON_BOOKS = {
    1: "Genesis",
    2: "Exodus",
    3: "Leviticus",
    4: "Numbers",
    5: "Deuteronomy",
    # Add more common books as needed
}

# Traditional abbreviations for books (matching database values)
BOOK_ABBREVIATIONS = {
    "Gn": 1,    # Genesis
    "Ex": 2,    # Exodus
    "Lev": 3,   # Leviticus
    "Num": 4,   # Numbers
    "Dt": 5,    # Deuteronomy
    "Jos": 6,   # Joshua
    "Jdc": 7,   # Judges
    "Ru": 8,    # Ruth
    "Esd": 9,   # Ezra
    "Neh": 10,  # Nehemiah
    "Tb": 11,   # Tobit
    "Jdt": 12,  # Judith
    "Est": 13,  # Esther
    "Jb": 14,   # Job
    "Ps": 15,   # Psalms
    "Pr": 16,   # Proverbs
    "Qo": 17,   # Ecclesiastes
    "Ct": 18,   # Song of Songs
    "Sap": 19,  # Wisdom
    "Si": 20,   # Sirach
    "Is": 21,   # Isaiah
    "Jer": 22,  # Jeremiah
    "Lam": 23,  # Lamentations
    "Ba": 24,   # Baruch
    "Ez": 25,   # Ezekiel
    "Dn": 26,   # Daniel
    "Os": 27,   # Hosea
    "Jl": 28,   # Joel
    "Am": 29,   # Amos
    "Ab": 30,   # Obadiah
    "Jon": 31,  # Jonah
    "Mi": 32,   # Micah
    "Na": 33,   # Nahum
    "Ha": 34,   # Habakkuk
    "So": 35,   # Zephaniah
    "Ag": 36,   # Haggai
    "Za": 37,   # Zechariah
    "Mal": 38,  # Malachi
    "Mt": 39,   # Matthew
    "Mc": 40,   # Mark
    "Lc": 41,   # Luke
    "Jo": 42,   # John
    "Ac": 43,   # Acts
    "Rm": 44,   # Romans
    "Ga": 45,   # Galatians
    "Ep": 46,   # Ephesians
    "Ph": 47,   # Philippians
    "Col": 48,  # Colossians
    "Tit": 49,  # Titus
    "Phm": 50,  # Philemon
    "He": 51,   # Hebrews
    "Jc": 52,   # James
    "Judæ": 53, # Jude
    "Ap": 54,   # Revelation
}

@router.get("/", response_model=List[Book])
def read_books(
    db: Session = Depends(deps.get_db),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
        example=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return",
        example=100
    ),
):
    """
    Retrieve a list of books from the Vulgate Bible.

    This endpoint returns a paginated list of books. You can use the skip and limit parameters
    to control pagination.

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
    - GET /api/v1/books/ - Get first 100 books
    - GET /api/v1/books/?skip=100&limit=50 - Get books 101-150
    """
    books = crud_book.get_multi(db, skip=skip, limit=limit)
    return books

@router.post("/", response_model=Book)
def create_book(
    *,
    db: Session = Depends(deps.get_db),
    book_in: BookCreate,
):
    """
    Create a new book in the Vulgate Bible.

    This endpoint creates a new book with the following required fields:
    - name: The English name of the book (e.g., "Genesis")
    - latin_name: The Latin name of the book (e.g., "Liber Genesis")
    - chapter_count: Optional number of chapters in the book

    Example request body:
    ```json
    {
        "name": "Genesis",
        "latin_name": "Liber Genesis",
        "chapter_count": 50
    }
    ```
    """
    book = crud_book.get_by_name(db, name=book_in.name)
    if book:
        raise HTTPException(
            status_code=400,
            detail="A book with this name already exists",
        )
    book = crud_book.create(db=db, obj_in=book_in)
    return book

@router.get("/{book_id}", response_model=Book)
def read_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to retrieve",
        example=1
    ),
):
    """
    Get a specific book by its ID.

    This endpoint returns detailed information about a single book.
    
    Common book IDs:
    - 1: Genesis
    - 2: Exodus
    - 3: Leviticus
    - 4: Numbers
    - 5: Deuteronomy

    Example URLs:
    - GET /api/v1/books/1 - Get Genesis
    - GET /api/v1/books/2 - Get Exodus
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=Book)
def update_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to update",
        example=1
    ),
    book_in: BookUpdate,
):
    """
    Update an existing book.

    This endpoint allows updating any of the following fields:
    - name: The English name of the book
    - latin_name: The Latin name of the book
    - chapter_count: Number of chapters in the book

    All fields are optional during update.

    Example request body:
    ```json
    {
        "name": "Updated Genesis",
        "latin_name": "Liber Genesis Updated",
        "chapter_count": 51
    }
    ```
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = crud_book.update(db=db, db_obj=book, obj_in=book_in)
    return book

@router.delete("/{book_id}")
def delete_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to delete",
        example=1
    ),
):
    """
    Delete a book.

    This endpoint permanently deletes a book from the database.
    Use with caution as this operation cannot be undone.

    Example URLs:
    - DELETE /api/v1/books/1 - Delete Genesis
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = crud_book.remove(db=db, id=book_id)
    return {"status": "success"}

@router.get("/abbr/{abbr}", response_model=Book)
def read_book_by_abbreviation(
    *,
    db: Session = Depends(deps.get_db),
    abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
):
    """
    Get a book by its traditional abbreviation.

    This endpoint allows you to retrieve a book using its traditional abbreviation
    as used in the Vulgate Bible.

    Common abbreviations:
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
    - GET /api/v1/books/abbr/Gn - Get Genesis
    - GET /api/v1/books/abbr/Ex - Get Exodus
    - GET /api/v1/books/abbr/Mt - Get Matthew
    """
    book_id = BOOK_ABBREVIATIONS.get(abbr)
    if not book_id:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis."
        )
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book 