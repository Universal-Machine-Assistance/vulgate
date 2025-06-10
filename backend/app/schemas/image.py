from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Verse Image Schemas
class VerseImageBase(BaseModel):
    image_type: str = Field(..., description="Type of image: illustration, manuscript, artwork, diagram, photo")
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: int = Field(default=1, description="Order for displaying multiple images")
    is_primary: bool = Field(default=False, description="Mark as primary image for the verse")

class VerseImageCreate(VerseImageBase):
    pass

class VerseImageUpdate(BaseModel):
    image_type: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
    is_primary: Optional[bool] = None

class VerseImageInDBBase(VerseImageBase):
    id: int
    verse_id: int
    image_filename: str
    original_filename: str
    file_path: str
    file_size: int
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    mime_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    uploaded_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True

class VerseImage(VerseImageInDBBase):
    pass

class VerseImageInDB(VerseImageInDBBase):
    pass

# Book Image Schemas  
class BookImageBase(BaseModel):
    chapter_number: Optional[int] = Field(None, description="Chapter number, NULL for book-level images")
    image_type: str = Field(..., description="Type of image: cover, illustration, map, timeline, diagram")
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: int = Field(default=1, description="Order for displaying multiple images")
    is_primary: bool = Field(default=False, description="Primary image for book/chapter")

class BookImageCreate(BookImageBase):
    pass

class BookImageUpdate(BaseModel):
    chapter_number: Optional[int] = None
    image_type: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    display_order: Optional[int] = None
    is_primary: Optional[bool] = None

class BookImageInDBBase(BookImageBase):
    id: int
    book_id: int
    image_filename: str
    original_filename: str
    file_path: str
    file_size: int
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    mime_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    uploaded_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True

class BookImage(BookImageInDBBase):
    pass

class BookImageInDB(BookImageInDBBase):
    pass

# Image Collection Schemas
class ImageCollectionBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    book_id: Optional[int] = None
    chapter_start: Optional[int] = None
    chapter_end: Optional[int] = None
    collection_type: str = Field(..., description="Type: thematic, sequential, artistic_style, historical")
    is_public: bool = Field(default=True)

class ImageCollectionCreate(ImageCollectionBase):
    pass

class ImageCollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    book_id: Optional[int] = None
    chapter_start: Optional[int] = None
    chapter_end: Optional[int] = None
    collection_type: Optional[str] = None
    is_public: Optional[bool] = None

class ImageCollectionInDBBase(ImageCollectionBase):
    id: int
    created_at: datetime
    created_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True

class ImageCollection(ImageCollectionInDBBase):
    pass

class ImageCollectionInDB(ImageCollectionInDBBase):
    pass

# Response schemas with URLs for frontend
class VerseImageResponse(VerseImage):
    image_url: str = Field(..., description="URL to access the image")
    thumbnail_url: Optional[str] = None

class BookImageResponse(BookImage):
    image_url: str = Field(..., description="URL to access the image")  
    thumbnail_url: Optional[str] = None

class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    image_id: int
    image_url: str
    filename: str
    file_size: int

class VerseImagesResponse(BaseModel):
    verse_id: int
    book_abbr: str
    chapter: int
    verse_number: int
    total_images: int
    images: List[VerseImageResponse]

class BookImagesResponse(BaseModel):
    book_id: int
    book_name: str
    book_abbr: str
    chapter_number: Optional[int] = None
    total_images: int
    images: List[BookImageResponse]

class ImageCollectionResponse(ImageCollection):
    image_count: int
    sample_images: List[VerseImageResponse] 