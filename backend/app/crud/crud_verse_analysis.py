from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.crud.base import CRUDBase
from backend.app.models.verse_analysis import (
    VerseAnalysis, 
    GrammarBreakdown, 
    GrammarTranslation,
    InterpretationLayer,
    LayerTranslation
)
from backend.app.schemas.verse_analysis import (
    VerseAnalysisCreate, 
    VerseAnalysisUpdate,
    GrammarBreakdownCreate,
    GrammarBreakdownUpdate,
    GrammarTranslationCreate,
    GrammarTranslationUpdate
)

class CRUDVerseAnalysis(CRUDBase[VerseAnalysis, VerseAnalysisCreate, VerseAnalysisUpdate]):
    def get_by_reference(
        self, db: Session, *, book_abbreviation: str, chapter_number: int, verse_number: int
    ) -> Optional[VerseAnalysis]:
        return db.query(VerseAnalysis).filter(
            VerseAnalysis.book_abbreviation == book_abbreviation,
            VerseAnalysis.chapter_number == chapter_number,
            VerseAnalysis.verse_number == verse_number,
        ).first()

    def get_with_grammar(
        self, db: Session, *, verse_analysis_id: int
    ) -> Optional[VerseAnalysis]:
        return db.query(VerseAnalysis).filter(
            VerseAnalysis.id == verse_analysis_id
        ).first()

class CRUDGrammarBreakdown(CRUDBase[GrammarBreakdown, GrammarBreakdownCreate, GrammarBreakdownUpdate]):
    def get_by_verse_analysis(
        self, db: Session, *, verse_analysis_id: int
    ) -> List[GrammarBreakdown]:
        return db.query(GrammarBreakdown).filter(
            GrammarBreakdown.verse_analysis_id == verse_analysis_id
        ).order_by(GrammarBreakdown.word_index).all()

    def update_meaning(
        self, db: Session, *, grammar_id: int, meaning: str, grammar_description: str
    ) -> Optional[GrammarBreakdown]:
        grammar_item = db.query(GrammarBreakdown).filter(GrammarBreakdown.id == grammar_id).first()
        if grammar_item:
            grammar_item.meaning = meaning
            grammar_item.grammar_description = grammar_description
            grammar_item.source = "manual"  # Mark as manually edited
            db.commit()
            db.refresh(grammar_item)
        return grammar_item

    def update_by_word_and_verse(
        self, db: Session, *, verse_analysis_id: int, word: str, updates: Dict[str, Any]
    ) -> Optional[GrammarBreakdown]:
        grammar_item = db.query(GrammarBreakdown).filter(
            GrammarBreakdown.verse_analysis_id == verse_analysis_id,
            GrammarBreakdown.word == word
        ).first()
        if grammar_item:
            for field, value in updates.items():
                if hasattr(grammar_item, field):
                    setattr(grammar_item, field, value)
            grammar_item.source = "manual"  # Mark as manually edited
            db.commit()
            db.refresh(grammar_item)
        return grammar_item

class CRUDGrammarTranslation(CRUDBase[GrammarTranslation, GrammarTranslationCreate, GrammarTranslationUpdate]):
    def get_by_grammar_and_language(
        self, db: Session, *, grammar_breakdown_id: int, language_code: str
    ) -> Optional[GrammarTranslation]:
        return db.query(GrammarTranslation).filter(
            GrammarTranslation.grammar_breakdown_id == grammar_breakdown_id,
            GrammarTranslation.language_code == language_code
        ).first()

    def create_or_update_translation(
        self, db: Session, *, grammar_breakdown_id: int, language_code: str, 
        meaning: str, grammar_description: str
    ) -> GrammarTranslation:
        translation = self.get_by_grammar_and_language(
            db, grammar_breakdown_id=grammar_breakdown_id, language_code=language_code
        )
        if translation:
            translation.meaning = meaning
            translation.grammar_description = grammar_description
            db.commit()
            db.refresh(translation)
        else:
            translation_data = GrammarTranslationCreate(
                grammar_breakdown_id=grammar_breakdown_id,
                language_code=language_code,
                meaning=meaning,
                grammar_description=grammar_description
            )
            translation = self.create(db=db, obj_in=translation_data)
        return translation

# Create instances
verse_analysis = CRUDVerseAnalysis(VerseAnalysis)
grammar_breakdown = CRUDGrammarBreakdown(GrammarBreakdown)
grammar_translation = CRUDGrammarTranslation(GrammarTranslation) 