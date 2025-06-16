from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.crud.base import CRUDBase
from backend.app.models.verse import Verse
from backend.app.schemas.verse import VerseCreate, VerseUpdate

__all__ = ["crud_verse"]

class CRUDVerse(CRUDBase[Verse, VerseCreate, VerseUpdate]):
    def get_verses(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        book_id: Optional[int] = None,
        chapter: Optional[int] = None,
    ) -> List[Verse]:
        query = db.query(self.model)
        
        if book_id is not None:
            query = query.filter(Verse.book_id == book_id)
        if chapter is not None:
            query = query.filter(Verse.chapter == chapter)
            
        return query.order_by(Verse.verse_number).offset(skip).limit(limit).all()
    
    def search_verses(
        self,
        db: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Verse]:
        search_query = f"%{query}%"
        return (
            db.query(self.model)
            .filter(
                or_(
                    Verse.text.ilike(search_query),
                    Verse.translation.ilike(search_query)
                )
            )
            .order_by(Verse.book_id, Verse.chapter, Verse.verse_number)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_verse_by_reference(
        self,
        db: Session,
        *,
        book_id: int,
        chapter: int,
        verse_number: int,
    ) -> Optional[Verse]:
        return (
            db.query(self.model)
            .filter(
                Verse.book_id == book_id,
                Verse.chapter == chapter,
                Verse.verse_number == verse_number
            )
            .first()
        )
    
    def create_with_words(
        self,
        db: Session,
        *,
        obj_in: VerseCreate,
        word_ids: List[int]
    ) -> Verse:
        verse = self.create(db=db, obj_in=obj_in)
        # Add words to verse
        for position, word_id in enumerate(word_ids):
            db.execute(
                "INSERT INTO verse_words (verse_id, word_id, position) VALUES (:verse_id, :word_id, :position)",
                {"verse_id": verse.id, "word_id": word_id, "position": position}
            )
        db.commit()
        return verse

crud_verse = CRUDVerse(Verse) 