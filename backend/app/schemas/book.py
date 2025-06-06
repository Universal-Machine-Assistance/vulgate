from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# Shared properties
class BookBase(BaseModel):
    name: str
    latin_name: str
    chapter_count: Optional[int] = 0

# Properties to receive on book creation
class BookCreate(BookBase):
    pass

# Properties to receive on book update
class BookUpdate(BookBase):
    name: Optional[str] = None
    latin_name: Optional[str] = None
    chapter_count: Optional[int] = None

# Properties shared by models stored in DB
class BookInDBBase(BookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Book(BookInDBBase):
    pass

# Properties stored in DB
class BookInDB(BookInDBBase):
    pass 