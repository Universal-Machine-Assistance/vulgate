from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Table, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base_class import Base

# Association table for word relationships
word_relationships = Table(
    'word_relationships',
    Base.metadata,
    Column('word_id', Integer, ForeignKey('words.id'), primary_key=True),
    Column('related_word_id', Integer, ForeignKey('words.id'), primary_key=True),
    Column('relationship_type', String(50)),  # e.g., 'synonym', 'antonym', 'related'
)

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    latin_name = Column(String(100), unique=True, index=True)
    chapter_count = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    verses = relationship("Verse", back_populates="book")

class Verse(Base):
    __tablename__ = "verses"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    chapter = Column(Integer)
    verse_number = Column(Integer)
    text = Column(Text)
    translation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    book = relationship("Book", back_populates="verses")
    words = relationship("Word", secondary="verse_words", back_populates="verses")
    audio_recordings = relationship("AudioRecording", back_populates="verse")
    analysis_history = relationship("AnalysisHistory", back_populates="verse")

class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True, index=True)
    latin_text = Column(String(100), index=True)
    dictionary_entry = Column(Text, nullable=True)
    frequency = Column(Integer, default=0)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale for learning priority
    
    verses = relationship("Verse", secondary="verse_words", back_populates="words")
    related_words = relationship(
        "Word",
        secondary=word_relationships,
        primaryjoin=id==word_relationships.c.word_id,
        secondaryjoin=id==word_relationships.c.related_word_id,
        backref="related_to"
    )
    audio_recordings = relationship("AudioRecording", back_populates="word")

class VerseWord(Base):
    __tablename__ = "verse_words"
    
    verse_id = Column(Integer, ForeignKey("verses.id"), primary_key=True)
    word_id = Column(Integer, ForeignKey("words.id"), primary_key=True)
    position = Column(Integer)  # Position in the verse
    is_highlighted = Column(Integer, default=0)  # For marking important words

class AudioRecording(Base):
    __tablename__ = "audio_recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255))
    duration = Column(Float)  # Duration in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verse_id = Column(Integer, ForeignKey("verses.id"), nullable=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=True)
    recording_type = Column(String(50))  # 'verse' or 'word'
    quality_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    verse = relationship("Verse", back_populates="audio_recordings")
    word = relationship("Word", back_populates="audio_recordings")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    proficiency_level = Column(Integer, default=0)  # 0-5 scale
    last_reviewed = Column(DateTime(timezone=True), server_default=func.now())
    review_count = Column(Integer, default=0)

    user = relationship("User", back_populates="progress")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    progress = relationship("UserProgress", back_populates="user")

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"))
    action_type = Column(String(50))  # 'analysis', 'edit', 'regenerate', 'ai_generate'
    target_field = Column(String(100))  # 'verse_text', 'word_definition', 'theological_layer', etc.
    target_identifier = Column(String(200), nullable=True)  # word or specific identifier
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_source = Column(String(50))  # 'user', 'ai', 'automated', 'greb_ai'
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional context data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence_score = Column(Float, nullable=True)  # For AI-generated changes
    review_status = Column(String(20), default='unreviewed')  # 'unreviewed', 'approved', 'rejected'
    
    verse = relationship("Verse", back_populates="analysis_history")
    user = relationship("User")

class EditSession(Base):
    __tablename__ = "edit_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_token = Column(String(255), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    session_data = Column(JSON, nullable=True)  # Store current edit state
    
    verse = relationship("Verse")
    user = relationship("User")
    field_edits = relationship("FieldEdit", back_populates="edit_session")

class FieldEdit(Base):
    __tablename__ = "field_edits"
    
    id = Column(Integer, primary_key=True, index=True)
    edit_session_id = Column(Integer, ForeignKey("edit_sessions.id"))
    field_type = Column(String(50))  # 'verse_text', 'word_definition', 'theological_point', etc.
    field_identifier = Column(String(200))  # word, layer index, etc.
    current_value = Column(Text)
    is_modified = Column(Boolean, default=False)
    ai_suggested_value = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    edit_session = relationship("EditSession", back_populates="field_edits")

class AnalysisQueue(Base):
    __tablename__ = "analysis_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_id = Column(Integer, ForeignKey("verses.id"))
    priority = Column(Integer, default=0)  # Higher numbers = higher priority
    analysis_type = Column(String(50))  # 'complete', 'grammar', 'theological', 'regenerate'
    request_source = Column(String(50))  # 'user', 'automated', 'batch'
    status = Column(String(20), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional request data
    
    verse = relationship("Verse") 