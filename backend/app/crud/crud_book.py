from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.crud.base import CRUDBase
from backend.app.db.models import Book
from backend.app.schemas.book import BookCreate, BookUpdate

__all__ = ["crud_book"]

class CRUDBook(CRUDBase[Book, BookCreate, BookUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Book]:
        return db.query(self.model).filter(Book.name == name).first()
    
    def get_by_latin_name(self, db: Session, *, latin_name: str) -> Optional[Book]:
        return db.query(self.model).filter(Book.latin_name == latin_name).first()

crud_book = CRUDBook(Book) 