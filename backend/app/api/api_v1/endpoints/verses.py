from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.schemas.verse import Verse, VerseCreate, VerseUpdate
from backend.app.crud import crud_verse
from backend.app.api.api_v1.endpoints.books import BOOK_ABBREVIATIONS
# from backend.app.api.api_v1.endpoints.images import upload_verse_image
# from backend.app.api.api_v1.endpoints.analysis import get_verse_analysis

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

@router.get("/{abbr}/{chapter}/{verse}/images")
def get_verse_images_by_reference(
    abbr: str = Path(..., description="Book abbreviation"),
    chapter: int = Path(..., description="Chapter number"),
    verse: int = Path(..., description="Verse number"),
    db: Session = Depends(deps.get_db)
):
    """
    Get all images for a specific verse by book abbreviation, chapter, and verse number.
    This endpoint returns the actual saved images from the database.
    """
    from backend.app.db.models import VerseImage, Book, Verse
    
    # Find the verse
    verse_obj = db.query(Verse).join(Book).filter(
        Book.name.ilike(f"%{abbr}%"),
        Verse.chapter == chapter,
        Verse.verse_number == verse
    ).first()
    
    if not verse_obj:
        return {
            "verse_id": None,
            "book_abbr": abbr,
            "chapter": chapter,
            "verse_number": verse,
            "total_images": 0,
            "images": []
        }
    
    # Get images ordered by display_order and creation date
    images = db.query(VerseImage).filter(
        VerseImage.verse_id == verse_obj.id
    ).order_by(VerseImage.display_order, VerseImage.created_at).all()
    
    # Convert to response format with URLs
    image_responses = []
    for img in images:
        image_url = f"/api/v1/images/verses/{img.id}"
        thumbnail_url = f"/api/v1/images/verses/{img.id}/thumbnail"
        
        image_response = {
            "id": img.id,
            "verse_id": img.verse_id,
            "image_filename": img.image_filename,
            "original_filename": img.original_filename,
            "file_size": img.file_size,
            "image_type": img.image_type,
            "caption": img.caption,
            "alt_text": img.alt_text,
            "display_order": img.display_order,
            "is_primary": img.is_primary,
            "image_width": img.image_width,
            "image_height": img.image_height,
            "mime_type": img.mime_type,
            "created_at": img.created_at,
            "updated_at": img.updated_at,
            "image_url": image_url,
            "thumbnail_url": thumbnail_url
        }
        image_responses.append(image_response)
    
    return {
        "verse_id": verse_obj.id,
        "book_abbr": abbr,
        "chapter": chapter,
        "verse_number": verse,
        "total_images": len(image_responses),
        "images": image_responses
    }

@router.post("/{abbr}/{chapter}/{verse}/images")
async def upload_verse_images_by_reference(
    abbr: str = Path(..., description="Book abbreviation"),
    chapter: int = Path(..., description="Chapter number"),
    verse: int = Path(..., description="Verse number"),
    files: List[UploadFile] = File(None, description="Image files to upload (multiple)"),
    file: Optional[UploadFile] = File(None, description="Single image file to upload"),
    image_type: str = Form("illustration", description="Type of image"),
    caption: Optional[str] = Form(None, description="Image caption"),
    alt_text: Optional[str] = Form(None, description="Alt text for accessibility"),
    db: Session = Depends(deps.get_db)
):
    """
    Upload images for a specific verse by book abbreviation, chapter, and verse number.
    This endpoint actually saves images to the database and filesystem.
    """
    from backend.app.db.models import VerseImage, Book, Verse
    from pathlib import Path as PathlibPath
    import os
    import uuid
    import shutil
    import mimetypes
    from PIL import Image
    
    # Configuration
    IMAGES_BASE_PATH = PathlibPath("static/images")
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Ensure directories exist
    os.makedirs(IMAGES_BASE_PATH / "verses", exist_ok=True)
    
    def validate_image_file(file: UploadFile) -> tuple[bool, str]:
        """Validate uploaded image file"""
        file_ext = PathlibPath(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        return True, "Valid file"
    
    def get_image_dimensions(file_path: PathlibPath) -> tuple[int, int]:
        """Get image dimensions"""
        try:
            with Image.open(file_path) as img:
                return img.size
        except Exception:
            return 0, 0
    
    uploaded_results = []
    
    # Handle both single file and multiple files
    files_to_process = []
    if file is not None:
        files_to_process.append(file)
    if files is not None:
        files_to_process.extend(files)
    
    if not files_to_process:
        return {
            "success": False,
            "message": "No files provided for upload",
            "verse": f"{abbr} {chapter}:{verse}",
            "successful_uploads": [],
            "failed_uploads": []
        }
    
    # Find the verse
    verse_obj = db.query(Verse).join(Book).filter(
        Book.name.ilike(f"%{abbr}%"),
        Verse.chapter == chapter,
        Verse.verse_number == verse
    ).first()
    
    if not verse_obj:
        return {
            "success": False,
            "message": f"Verse {abbr} {chapter}:{verse} not found",
            "verse": f"{abbr} {chapter}:{verse}",
            "successful_uploads": [],
            "failed_uploads": []
        }
    
    for i, file_item in enumerate(files_to_process):
        try:
            # Validate file
            is_valid, error_msg = validate_image_file(file_item)
            if not is_valid:
                uploaded_results.append({
                    "success": False,
                    "filename": file_item.filename,
                    "error": error_msg
                })
                continue
            
            # Generate unique filename
            file_ext = PathlibPath(file_item.filename).suffix.lower()
            unique_filename = f"verse_{abbr}_{chapter}_{verse}_{uuid.uuid4().hex[:8]}{file_ext}"
            
            # Create directory structure
            verse_dir = IMAGES_BASE_PATH / "verses" / abbr / str(chapter)
            verse_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = verse_dir / unique_filename
            
            # Save the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file_item.file, buffer)
            
            # Get file info
            file_size = file_path.stat().st_size
            width, height = get_image_dimensions(file_path)
            mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            
            # Create database record
            verse_image = VerseImage(
                verse_id=verse_obj.id,
                image_filename=unique_filename,
                original_filename=file_item.filename,
                file_path=str(file_path),
                file_size=file_size,
                image_type=image_type,
                caption=caption,
                alt_text=alt_text,
                is_primary=False,
                image_width=width,
                image_height=height,
                mime_type=mime_type
            )
            
            db.add(verse_image)
            db.commit()
            db.refresh(verse_image)
            
            # Generate URL
            image_url = f"/api/v1/images/verses/{verse_image.id}"
            
            uploaded_results.append({
                "success": True,
                "filename": file_item.filename,
                "message": f"Successfully uploaded {file_item.filename}",
                "image_id": verse_image.id,
                "image_url": image_url,
                "size": file_size,
                "content_type": mime_type
            })
            
        except Exception as e:
            # Clean up file if database operation fails
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            uploaded_results.append({
                "success": False,
                "filename": file_item.filename,
                "error": str(e)
            })
    
    successful_uploads = [r for r in uploaded_results if r["success"]]
    failed_uploads = [r for r in uploaded_results if not r["success"]]
    
    return {
        "success": len(successful_uploads) > 0,
        "message": f"Uploaded {len(successful_uploads)} of {len(files_to_process)} files",
        "verse": f"{abbr} {chapter}:{verse}",
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads
    }

@router.get("/analysis/{abbr}/{chapter}/{verse}")
async def get_verse_analysis_by_reference(
    abbr: str = Path(..., description="Book abbreviation"),
    chapter: int = Path(..., description="Chapter number"),
    verse: int = Path(..., description="Verse number"),
):
    """
    Get analysis for a specific verse by book abbreviation, chapter, and verse number.
    This is a convenience endpoint that matches the frontend's expected URL pattern.
    """
    # For now, return empty response until we fix the analysis endpoint
    return {
        "found": False,
        "message": "Analysis endpoint not yet implemented for this path"
    }