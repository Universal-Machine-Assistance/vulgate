from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.db.base_class import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    latin_name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    verses = relationship("Verse", back_populates="book") 