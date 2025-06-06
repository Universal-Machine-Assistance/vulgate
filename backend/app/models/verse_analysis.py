from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class VerseAnalysis(Base):
    """Main verse analysis with metadata"""
    __tablename__ = "verse_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    book_abbreviation = Column(String(10), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    verse_number = Column(Integer, nullable=False)
    
    # Analysis status
    grammar_analyzed = Column(Boolean, default=False)
    theological_analyzed = Column(Boolean, default=False)
    symbolic_analyzed = Column(Boolean, default=False)
    cosmological_analyzed = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analysis_version = Column(String(10), default="1.0")
    
    # Relationships
    grammar_items = relationship("GrammarBreakdown", back_populates="verse_analysis")
    interpretations = relationship("InterpretationLayer", back_populates="verse_analysis")

class GrammarBreakdown(Base):
    """Grammar analysis for individual words in a verse"""
    __tablename__ = "grammar_breakdowns"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_analysis_id = Column(Integer, ForeignKey("verse_analyses.id"))
    
    # Word information
    word = Column(String(100), nullable=False)
    word_index = Column(Integer, nullable=False)  # Position in verse
    
    # Grammar analysis
    meaning = Column(Text, nullable=False)
    grammar_description = Column(Text, nullable=False)
    part_of_speech = Column(String(50))
    morphology = Column(Text)
    
    # UI elements
    fontawesome_icon = Column(String(50), default="fa-language")
    color_class = Column(String(50), default="text-blue-600")
    
    # Analysis metadata
    confidence = Column(Float, default=1.0)
    source = Column(String(50), default="openai")  # openai, dictionary, manual
    
    # Relationships
    verse_analysis = relationship("VerseAnalysis", back_populates="grammar_items")
    translations = relationship("GrammarTranslation", back_populates="grammar_item")

class GrammarTranslation(Base):
    """Multi-language translations for grammar breakdowns"""
    __tablename__ = "grammar_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    grammar_breakdown_id = Column(Integer, ForeignKey("grammar_breakdowns.id"))
    
    language_code = Column(String(5), nullable=False)  # en, es, fr, pt, it
    meaning = Column(Text, nullable=False)
    grammar_description = Column(Text, nullable=False)
    
    # Relationships
    grammar_item = relationship("GrammarBreakdown", back_populates="translations")

class InterpretationLayer(Base):
    """Interpretation layers for verses (Theological, Symbolic, Cosmological)"""
    __tablename__ = "interpretation_layers"
    
    id = Column(Integer, primary_key=True, index=True)
    verse_analysis_id = Column(Integer, ForeignKey("verse_analyses.id"))
    
    layer_type = Column(String(20), nullable=False)  # theological, symbolic, cosmological
    
    # Layer content (in base language - typically English)
    title = Column(String(200), nullable=False)
    points = Column(Text, nullable=False)  # JSON array of interpretation points
    
    # UI elements
    fontawesome_icon = Column(String(50), nullable=False)
    color_gradient = Column(String(100), nullable=False)  # CSS gradient classes
    
    # Analysis metadata
    confidence = Column(Float, default=1.0)
    source = Column(String(50), default="openai")
    
    # Relationships
    verse_analysis = relationship("VerseAnalysis", back_populates="interpretations")
    translations = relationship("LayerTranslation", back_populates="interpretation_layer")

class LayerTranslation(Base):
    """Multi-language translations for interpretation layers"""
    __tablename__ = "layer_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    interpretation_layer_id = Column(Integer, ForeignKey("interpretation_layers.id"))
    
    language_code = Column(String(5), nullable=False)
    title = Column(String(200), nullable=False)
    points = Column(Text, nullable=False)  # JSON array of translated points
    
    # Relationships
    interpretation_layer = relationship("InterpretationLayer", back_populates="translations")

class AnalysisProgress(Base):
    """Track overall analysis progress"""
    __tablename__ = "analysis_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Word analysis progress
    total_unique_words = Column(Integer, default=0)
    analyzed_words = Column(Integer, default=0)
    cached_words = Column(Integer, default=0)
    
    # Verse analysis progress
    total_verses = Column(Integer, default=0)
    grammar_analyzed_verses = Column(Integer, default=0)
    theological_analyzed_verses = Column(Integer, default=0)
    symbolic_analyzed_verses = Column(Integer, default=0)
    cosmological_analyzed_verses = Column(Integer, default=0)
    
    # Language coverage
    supported_languages = Column(Text, default='["en", "es", "fr", "pt", "it"]')  # JSON array
    
    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(String(10), default="1.0") 