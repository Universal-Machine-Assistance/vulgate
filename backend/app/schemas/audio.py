from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AudioBase(BaseModel):
    file_path: str
    duration: Optional[float] = Field(None, ge=0)
    recording_type: Optional[str] = None  # 'verse' or 'word'
    quality_rating: Optional[int] = Field(None, ge=1, le=5)

class AudioCreate(AudioBase):
    verse_id: Optional[int] = None
    word_id: Optional[int] = None

class AudioUpdate(AudioBase):
    file_path: Optional[str] = None
    duration: Optional[float] = None
    recording_type: Optional[str] = None
    quality_rating: Optional[int] = None
    verse_id: Optional[int] = None
    word_id: Optional[int] = None

class AudioInDBBase(AudioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AudioRecording(AudioInDBBase):
    pass

class AudioInDB(AudioInDBBase):
    pass 