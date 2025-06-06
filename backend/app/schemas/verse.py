from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# Shared properties
class VerseBase(BaseModel):
    book_id: int
    chapter: int
    verse_number: int
    text: str
    translation: Optional[str] = None

# Properties to receive on verse creation
class VerseCreate(VerseBase):
    pass

# Properties to receive on verse update
class VerseUpdate(VerseBase):
    book_id: Optional[int] = None
    chapter: Optional[int] = None
    verse_number: Optional[int] = None
    text: Optional[str] = None

# Properties shared by models stored in DB
class VerseInDBBase(VerseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Verse(VerseInDBBase):
    pass

# Properties stored in DB
class VerseInDB(VerseInDBBase):
    pass

# Additional schemas for verse relationships
class VerseWithWords(Verse):
    words: List["Word"] = []

class VerseWithAudio(Verse):
    audio_recordings: List["AudioRecording"] = []

# Import at the end to avoid circular imports
from backend.app.schemas.word import Word
from backend.app.schemas.audio import AudioRecording 