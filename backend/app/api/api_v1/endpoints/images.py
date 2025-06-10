from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Path, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from pathlib import Path as PathlibPath
from PIL import Image
import mimetypes

from backend.app.db.session import get_db
from backend.app.db.models import VerseImage, BookImage, Verse, Book, ImageCollection
from backend.app.schemas.image import (
    VerseImageCreate, VerseImageUpdate, VerseImageResponse, VerseImagesResponse,
    BookImageCreate, BookImageUpdate, BookImageResponse, BookImagesResponse,
    ImageUploadResponse, ImageCollectionCreate, ImageCollectionResponse
)

router = APIRouter()

# Configuration
IMAGES_BASE_PATH = PathlibPath("static/images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
THUMBNAIL_SIZE = (200, 200)

# Ensure directories exist
os.makedirs(IMAGES_BASE_PATH / "verses", exist_ok=True)
os.makedirs(IMAGES_BASE_PATH / "books", exist_ok=True)
os.makedirs(IMAGES_BASE_PATH / "thumbnails", exist_ok=True)

def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded image file"""
    # Check file extension
    file_ext = PathlibPath(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size (this is approximate as file might be read in chunks)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
    
    return True, "Valid file"

def create_thumbnail(image_path: PathlibPath, thumbnail_path: PathlibPath) -> bool:
    """Create thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

def get_image_dimensions(image_path: PathlibPath) -> tuple[int, int]:
    """Get image dimensions"""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return 0, 0

# VERSE IMAGE ENDPOINTS

@router.post("/verses/{book_abbr}/{chapter}/{verse}/upload", response_model=ImageUploadResponse)
async def upload_verse_image(
    book_abbr: str = Path(..., description="Book abbreviation"),
    chapter: int = Path(..., description="Chapter number"),
    verse: int = Path(..., description="Verse number"),
    file: UploadFile = File(..., description="Image file to upload"),
    image_type: str = Form(..., description="Type of image"),
    caption: Optional[str] = Form(None, description="Image caption"),
    alt_text: Optional[str] = Form(None, description="Alt text for accessibility"),
    is_primary: bool = Form(False, description="Mark as primary image"),
    db: Session = Depends(get_db)
):
    """Upload an image for a specific verse"""
    
    # Validate file
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Find the verse
    verse_obj = db.query(Verse).join(Book).filter(
        Book.name.ilike(f"%{book_abbr}%"),
        Verse.chapter == chapter,
        Verse.verse_number == verse
    ).first()
    
    if not verse_obj:
        raise HTTPException(status_code=404, detail=f"Verse {book_abbr} {chapter}:{verse} not found")
    
    # Generate unique filename
    file_ext = PathlibPath(file.filename).suffix.lower()
    unique_filename = f"verse_{book_abbr}_{chapter}_{verse}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    # Create directory structure
    verse_dir = IMAGES_BASE_PATH / "verses" / book_abbr / str(chapter)
    verse_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = verse_dir / unique_filename
    thumbnail_dir = IMAGES_BASE_PATH / "thumbnails" / "verses" / book_abbr / str(chapter)
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_path = thumbnail_dir / f"thumb_{unique_filename}"
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        width, height = get_image_dimensions(file_path)
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        # Create thumbnail
        create_thumbnail(file_path, thumbnail_path)
        
        # If this is marked as primary, unmark other primary images for this verse
        if is_primary:
            db.query(VerseImage).filter(
                VerseImage.verse_id == verse_obj.id,
                VerseImage.is_primary == True
            ).update({"is_primary": False})
        
        # Create database record
        verse_image = VerseImage(
            verse_id=verse_obj.id,
            image_filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            image_type=image_type,
            caption=caption,
            alt_text=alt_text,
            is_primary=is_primary,
            image_width=width,
            image_height=height,
            mime_type=mime_type
        )
        
        db.add(verse_image)
        db.commit()
        db.refresh(verse_image)
        
        # Generate URL
        image_url = f"/api/v1/images/verses/{verse_image.id}"
        
        return ImageUploadResponse(
            success=True,
            message="Image uploaded successfully",
            image_id=verse_image.id,
            image_url=image_url,
            filename=unique_filename,
            file_size=file_size
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if file_path.exists():
            file_path.unlink()
        if thumbnail_path.exists():
            thumbnail_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@router.get("/verses/{book_abbr}/{chapter}/{verse}", response_model=VerseImagesResponse)
def get_verse_images(
    book_abbr: str = Path(..., description="Book abbreviation"),
    chapter: int = Path(..., description="Chapter number"),
    verse: int = Path(..., description="Verse number"),
    db: Session = Depends(get_db)
):
    """Get all images for a specific verse"""
    
    # Find the verse
    verse_obj = db.query(Verse).join(Book).filter(
        Book.name.ilike(f"%{book_abbr}%"),
        Verse.chapter == chapter,
        Verse.verse_number == verse
    ).first()
    
    if not verse_obj:
        raise HTTPException(status_code=404, detail=f"Verse {book_abbr} {chapter}:{verse} not found")
    
    # Get images ordered by display_order and creation date
    images = db.query(VerseImage).filter(
        VerseImage.verse_id == verse_obj.id
    ).order_by(VerseImage.display_order, VerseImage.created_at).all()
    
    # Convert to response format with URLs
    image_responses = []
    for img in images:
        image_url = f"/api/v1/images/verses/{img.id}"
        thumbnail_url = f"/api/v1/images/verses/{img.id}/thumbnail"
        
        image_response = VerseImageResponse(
            **img.__dict__,
            image_url=image_url,
            thumbnail_url=thumbnail_url
        )
        image_responses.append(image_response)
    
    return VerseImagesResponse(
        verse_id=verse_obj.id,
        book_abbr=book_abbr,
        chapter=chapter,
        verse_number=verse,
        total_images=len(image_responses),
        images=image_responses
    )

@router.get("/verses/{image_id}")
async def get_verse_image_file(
    image_id: int = Path(..., description="Image ID"),
    thumbnail: bool = Query(False, description="Return thumbnail version"),
    db: Session = Depends(get_db)
):
    """Get the actual image file"""
    
    image = db.query(VerseImage).filter(VerseImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if thumbnail:
        # Return thumbnail
        thumbnail_path = PathlibPath(image.file_path).parent.parent.parent / "thumbnails" / "verses" / PathlibPath(image.file_path).parent.name / PathlibPath(image.file_path).parent.parent.name / f"thumb_{image.image_filename}"
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        file_path = thumbnail_path
    else:
        # Return original image
        file_path = PathlibPath(image.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(
        path=str(file_path),
        media_type=image.mime_type,
        filename=image.original_filename
    )

@router.delete("/verses/{image_id}")
def delete_verse_image(
    image_id: int = Path(..., description="Image ID"),
    db: Session = Depends(get_db)
):
    """Delete a verse image"""
    
    image = db.query(VerseImage).filter(VerseImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete files
    file_path = PathlibPath(image.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete thumbnail
    thumbnail_path = file_path.parent.parent.parent / "thumbnails" / "verses" / file_path.parent.name / file_path.parent.parent.name / f"thumb_{image.image_filename}"
    if thumbnail_path.exists():
        thumbnail_path.unlink()
    
    # Delete database record
    db.delete(image)
    db.commit()
    
    return {"success": True, "message": "Image deleted successfully"}

# BOOK IMAGE ENDPOINTS

@router.post("/books/{book_abbr}/upload", response_model=ImageUploadResponse)
async def upload_book_image(
    book_abbr: str = Path(..., description="Book abbreviation"),
    file: UploadFile = File(..., description="Image file to upload"),
    image_type: str = Form(..., description="Type of image"),
    chapter_number: Optional[int] = Form(None, description="Chapter number (NULL for book-level)"),
    caption: Optional[str] = Form(None, description="Image caption"),
    alt_text: Optional[str] = Form(None, description="Alt text for accessibility"),
    is_primary: bool = Form(False, description="Mark as primary image"),
    db: Session = Depends(get_db)
):
    """Upload an image for a book or specific chapter"""
    
    # Validate file
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Find the book
    book = db.query(Book).filter(Book.name.ilike(f"%{book_abbr}%")).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_abbr} not found")
    
    # Generate unique filename
    file_ext = PathlibPath(file.filename).suffix.lower()
    chapter_suffix = f"_ch{chapter_number}" if chapter_number else "_book"
    unique_filename = f"book_{book_abbr}{chapter_suffix}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    # Create directory structure
    book_dir = IMAGES_BASE_PATH / "books" / book_abbr
    book_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = book_dir / unique_filename
    thumbnail_dir = IMAGES_BASE_PATH / "thumbnails" / "books" / book_abbr
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_path = thumbnail_dir / f"thumb_{unique_filename}"
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        width, height = get_image_dimensions(file_path)
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        # Create thumbnail
        create_thumbnail(file_path, thumbnail_path)
        
        # If this is marked as primary, unmark other primary images for this book/chapter
        if is_primary:
            db.query(BookImage).filter(
                BookImage.book_id == book.id,
                BookImage.chapter_number == chapter_number,
                BookImage.is_primary == True
            ).update({"is_primary": False})
        
        # Create database record
        book_image = BookImage(
            book_id=book.id,
            chapter_number=chapter_number,
            image_filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            image_type=image_type,
            caption=caption,
            alt_text=alt_text,
            is_primary=is_primary,
            image_width=width,
            image_height=height,
            mime_type=mime_type
        )
        
        db.add(book_image)
        db.commit()
        db.refresh(book_image)
        
        # Generate URL
        image_url = f"/api/v1/images/books/{book_image.id}"
        
        return ImageUploadResponse(
            success=True,
            message="Image uploaded successfully",
            image_id=book_image.id,
            image_url=image_url,
            filename=unique_filename,
            file_size=file_size
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if file_path.exists():
            file_path.unlink()
        if thumbnail_path.exists():
            thumbnail_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@router.get("/books/{book_abbr}", response_model=BookImagesResponse)
def get_book_images(
    book_abbr: str = Path(..., description="Book abbreviation"),
    chapter: Optional[int] = Query(None, description="Specific chapter (NULL for book-level images)"),
    db: Session = Depends(get_db)
):
    """Get all images for a book or specific chapter"""
    
    # Find the book
    book = db.query(Book).filter(Book.name.ilike(f"%{book_abbr}%")).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"Book {book_abbr} not found")
    
    # Build query
    query = db.query(BookImage).filter(BookImage.book_id == book.id)
    if chapter is not None:
        query = query.filter(BookImage.chapter_number == chapter)
    
    # Get images ordered by display_order and creation date
    images = query.order_by(BookImage.display_order, BookImage.created_at).all()
    
    # Convert to response format with URLs
    image_responses = []
    for img in images:
        image_url = f"/api/v1/images/books/{img.id}"
        thumbnail_url = f"/api/v1/images/books/{img.id}/thumbnail"
        
        image_response = BookImageResponse(
            **img.__dict__,
            image_url=image_url,
            thumbnail_url=thumbnail_url
        )
        image_responses.append(image_response)
    
    return BookImagesResponse(
        book_id=book.id,
        book_name=book.name,
        book_abbr=book_abbr,
        chapter_number=chapter,
        total_images=len(image_responses),
        images=image_responses
    )

@router.get("/books/{image_id}")
async def get_book_image_file(
    image_id: int = Path(..., description="Image ID"),
    thumbnail: bool = Query(False, description="Return thumbnail version"),
    db: Session = Depends(get_db)
):
    """Get the actual book image file"""
    
    image = db.query(BookImage).filter(BookImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if thumbnail:
        # Return thumbnail
        file_path_obj = PathlibPath(image.file_path)
        thumbnail_path = IMAGES_BASE_PATH / "thumbnails" / "books" / file_path_obj.parent.name / f"thumb_{image.image_filename}"
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        file_path = thumbnail_path
    else:
        # Return original image
        file_path = PathlibPath(image.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(
        path=str(file_path),
        media_type=image.mime_type,
        filename=image.original_filename
    )

@router.delete("/books/{image_id}")
def delete_book_image(
    image_id: int = Path(..., description="Image ID"),
    db: Session = Depends(get_db)
):
    """Delete a book image"""
    
    image = db.query(BookImage).filter(BookImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete files
    file_path = PathlibPath(image.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete thumbnail
    file_path_obj = PathlibPath(image.file_path)
    thumbnail_path = IMAGES_BASE_PATH / "thumbnails" / "books" / file_path_obj.parent.name / f"thumb_{image.image_filename}"
    if thumbnail_path.exists():
        thumbnail_path.unlink()
    
    # Delete database record
    db.delete(image)
    db.commit()
    
    return {"success": True, "message": "Image deleted successfully"}

# UTILITY ENDPOINTS

@router.get("/stats")
def get_image_stats(db: Session = Depends(get_db)):
    """Get statistics about images in the system"""
    
    verse_image_count = db.query(VerseImage).count()
    book_image_count = db.query(BookImage).count()
    
    # Get counts by image type
    verse_types = db.query(VerseImage.image_type, db.func.count(VerseImage.id)).group_by(VerseImage.image_type).all()
    book_types = db.query(BookImage.image_type, db.func.count(BookImage.id)).group_by(BookImage.image_type).all()
    
    return {
        "total_verse_images": verse_image_count,
        "total_book_images": book_image_count,
        "total_images": verse_image_count + book_image_count,
        "verse_image_types": {img_type: count for img_type, count in verse_types},
        "book_image_types": {img_type: count for img_type, count in book_types}
    } 