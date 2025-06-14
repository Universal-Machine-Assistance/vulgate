import os
import httpx
from typing import List, Dict, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.crud import crud_book, crud_verse
from backend.app.db.models import Book
from backend.app.models.verse import Verse
from backend.app.schemas.book import BookCreate
from backend.app.schemas.verse import VerseCreate


class BhagavadGitaService:
    """Service to interact with Bhagavad Gita RapidAPI and manage local caching"""
    
    def __init__(self):
        self.base_url = "https://bhagavad-gita3.p.rapidapi.com"
        self.api_key = os.getenv("RAPIDAPI_KEY")  # Add this to your .env file
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "bhagavad-gita3.p.rapidapi.com"
        }
    
    async def get_verse(self, chapter: int, verse: int) -> Dict:
        """Fetch a specific verse from the Bhagavad Gita API"""
        if self.api_key is None:
            raise HTTPException(status_code=503, detail="RapidAPI key not configured")
        
        url = f"{self.base_url}/v2/chapters/{chapter}/verses/{verse}/"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Timeout fetching from Bhagavad Gita API")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Verse {chapter}:{verse} not found in Bhagavad Gita")
                raise HTTPException(status_code=503, detail="Error fetching from Bhagavad Gita API")
    
    async def get_chapter(self, chapter: int) -> Dict:
        """Fetch all verses from a specific chapter"""
        if self.api_key is None:
            raise HTTPException(status_code=503, detail="RapidAPI key not configured")
        
        url = f"{self.base_url}/v2/chapters/{chapter}/"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Timeout fetching from Bhagavad Gita API")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Chapter {chapter} not found in Bhagavad Gita")
                raise HTTPException(status_code=503, detail="Error fetching from Bhagavad Gita API")
    
    async def get_all_chapters(self) -> Dict:
        """Fetch information about all chapters"""
        if self.api_key is None:
            raise HTTPException(status_code=503, detail="RapidAPI key not configured")
        
        url = f"{self.base_url}/v2/chapters/"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Timeout fetching from Bhagavad Gita API")
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=503, detail="Error fetching from Bhagavad Gita API")
    
    def get_or_create_gita_book(self, db: Session) -> Book:
        """Get or create the Bhagavad Gita book entry in the database"""
        # Check if Bhagavad Gita book already exists
        gita_book = db.query(Book).filter(
            Book.source == 'gita',
            Book.name == 'Bhagavad Gita'
        ).first()
        
        if not gita_book:
            # Create the Bhagavad Gita book entry
            book_data = BookCreate(
                name="Bhagavad Gita",
                latin_name="Bhagavad Gita",  # Keep original Sanskrit name
                chapter_count=18  # Bhagavad Gita has 18 chapters
            )
            gita_book = crud_book.create(db=db, obj_in=book_data)
            gita_book.source = 'gita'
            gita_book.source_id = 'bhagavad-gita'
            db.commit()
            db.refresh(gita_book)
        
        return gita_book
    
    async def cache_verse_locally(self, db: Session, chapter: int, verse_num: int) -> Verse:
        """Fetch verse from API and cache it locally in the database"""
        # Get or create the Gita book
        gita_book = self.get_or_create_gita_book(db)
        
        # Check if verse already exists locally
        existing_verse = crud_verse.get_verse_by_reference(
            db=db,
            book_id=gita_book.id,
            chapter=chapter,
            verse_number=verse_num
        )
        
        if existing_verse:
            return existing_verse
        
        # Fetch from API
        api_data = await self.get_verse(chapter, verse_num)
        
        # Extract verse text (try different fields from the API response)
        verse_text = ""
        translation = ""
        
        if 'text' in api_data:
            verse_text = api_data['text']
        elif 'slok' in api_data:
            verse_text = api_data['slok']
        
        if 'translation' in api_data:
            translation = api_data['translation']
        elif 'transliteration' in api_data:
            translation = api_data['transliteration']
        
        # Create verse in database
        verse_data = VerseCreate(
            book_id=gita_book.id,
            chapter=chapter,
            verse_number=verse_num,
            text=verse_text,
            translation=translation
        )
        
        new_verse = crud_verse.create(db=db, obj_in=verse_data)
        return new_verse
    
    async def cache_chapter_locally(self, db: Session, chapter: int) -> List[Verse]:
        """Fetch all verses from a chapter and cache them locally"""
        # Get or create the Gita book
        gita_book = self.get_or_create_gita_book(db)
        
        # Fetch chapter data from API
        api_data = await self.get_chapter(chapter)
        
        verses = []
        
        # Handle different API response formats
        verse_list = api_data.get('verses', [])
        if not verse_list and 'results' in api_data:
            verse_list = api_data['results']
        
        for verse_data in verse_list:
            verse_num = verse_data.get('verse_number', verse_data.get('id', 0))
            
            # Check if verse already exists locally
            existing_verse = crud_verse.get_verse_by_reference(
                db=db,
                book_id=gita_book.id,
                chapter=chapter,
                verse_number=verse_num
            )
            
            if existing_verse:
                verses.append(existing_verse)
                continue
            
            # Extract verse text
            verse_text = verse_data.get('text', verse_data.get('slok', ''))
            translation = verse_data.get('translation', verse_data.get('transliteration', ''))
            
            # Create verse in database
            new_verse_data = VerseCreate(
                book_id=gita_book.id,
                chapter=chapter,
                verse_number=verse_num,
                text=verse_text,
                translation=translation
            )
            
            new_verse = crud_verse.create(db=db, obj_in=new_verse_data)
            verses.append(new_verse)
        
        return verses


# Global instance
bhagavad_gita_service = BhagavadGitaService() 