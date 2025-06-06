from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class WordBase(BaseModel):
    latin_text: str
    dictionary_entry: Optional[str] = None
    frequency: Optional[int] = Field(default=0, ge=0)
    difficulty_level: Optional[int] = Field(default=1, ge=1, le=5)

# Properties to receive on word creation
class WordCreate(WordBase):
    pass

# Properties to receive on word update
class WordUpdate(WordBase):
    latin_text: Optional[str] = None
    dictionary_entry: Optional[str] = None
    frequency: Optional[int] = None
    difficulty_level: Optional[int] = None

# Properties shared by models stored in DB
class WordInDBBase(WordBase):
    id: int
    created_at: Optional[datetime] = None  # Provided by DB if column exists
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Word(WordInDBBase):
    pass

# Properties stored in DB
class WordInDB(WordInDBBase):
    pass

# Additional schemas for relationships
class WordWithAudio(Word):
    audio_recordings: List["AudioRecording"] = []

# Import at the end to avoid circular dependencies
from backend.app.schemas.audio import AudioRecording    # noqa: E402 