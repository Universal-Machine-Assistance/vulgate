from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# VerseAnalysis Schemas
class VerseAnalysisBase(BaseModel):
    book_abbreviation: str
    chapter_number: int
    verse_number: int
    grammar_analyzed: bool = False
    theological_analyzed: bool = False
    symbolic_analyzed: bool = False
    cosmological_analyzed: bool = False
    analysis_version: str = "1.0"

class VerseAnalysisCreate(VerseAnalysisBase):
    pass

class VerseAnalysisUpdate(BaseModel):
    grammar_analyzed: Optional[bool] = None
    theological_analyzed: Optional[bool] = None
    symbolic_analyzed: Optional[bool] = None
    cosmological_analyzed: Optional[bool] = None
    analysis_version: Optional[str] = None

class VerseAnalysis(VerseAnalysisBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# GrammarBreakdown Schemas
class GrammarBreakdownBase(BaseModel):
    word: str
    word_index: int
    meaning: str
    grammar_description: str
    part_of_speech: Optional[str] = None
    morphology: Optional[str] = None
    fontawesome_icon: str = "fa-language"
    color_class: str = "text-blue-600"
    confidence: float = 1.0
    source: str = "openai"

class GrammarBreakdownCreate(GrammarBreakdownBase):
    verse_analysis_id: int

class GrammarBreakdownUpdate(BaseModel):
    meaning: Optional[str] = None
    grammar_description: Optional[str] = None
    part_of_speech: Optional[str] = None
    morphology: Optional[str] = None
    fontawesome_icon: Optional[str] = None
    color_class: Optional[str] = None
    confidence: Optional[float] = None
    source: Optional[str] = None

class GrammarBreakdown(GrammarBreakdownBase):
    id: int
    verse_analysis_id: int

    class Config:
        from_attributes = True

# GrammarTranslation Schemas
class GrammarTranslationBase(BaseModel):
    language_code: str
    meaning: str
    grammar_description: str

class GrammarTranslationCreate(GrammarTranslationBase):
    grammar_breakdown_id: int

class GrammarTranslationUpdate(BaseModel):
    meaning: Optional[str] = None
    grammar_description: Optional[str] = None

class GrammarTranslation(GrammarTranslationBase):
    id: int
    grammar_breakdown_id: int

    class Config:
        from_attributes = True

# Combined response schemas
class GrammarBreakdownWithTranslations(GrammarBreakdown):
    translations: List[GrammarTranslation] = []

class VerseAnalysisWithGrammar(VerseAnalysis):
    grammar_items: List[GrammarBreakdownWithTranslations] = []

# Edit request schemas
class EditGrammarRequest(BaseModel):
    word: str
    meaning: str
    grammar_description: str
    part_of_speech: Optional[str] = None
    morphology: Optional[str] = None

class EditTranslationRequest(BaseModel):
    word: str
    language_code: str
    meaning: str
    grammar_description: str 