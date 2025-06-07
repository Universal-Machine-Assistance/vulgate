from typing import Optional, Dict, Any, List
from datetime import datetime
import json
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.config import settings
from backend.app.models.verse import VerseAnalysis, GrammarBreakdown, InterpretationLayer
from backend.app.schemas.verse import VerseAnalysisResponse, GrammarItem, InterpretationLayer as InterpretationLayerSchema, Verse
from backend.app.db.models import Book

class VulgateAnalyzer:
    def __init__(self, openai_api_key: str = None, database_path: str = None):
        self.openai_api_key = openai_api_key
        self.database_path = database_path or settings.SQLITE_DB_PATH
        self.setup_database()
        
        # Initialize OpenAI client if API key is provided
        if openai_api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=openai_api_key)
        else:
            self.client = None
            print("Warning: No OpenAI API key provided. Some features will be limited.")
    
    def setup_database(self):
        """Set up database tables if they don't exist"""
        db = next(get_db())
        try:
            # Create tables
            VerseAnalysis.__table__.create(bind=db.get_bind(), checkfirst=True)
            GrammarBreakdown.__table__.create(bind=db.get_bind(), checkfirst=True)
            InterpretationLayer.__table__.create(bind=db.get_bind(), checkfirst=True)
        except Exception as e:
            print(f"Error setting up database: {e}")
        finally:
            db.close()
    
    def analyze_verse(self, book: str, chapter: int, verse: int, language: str = "la") -> Optional[VerseAnalysisResponse]:
        """Analyze a verse with caching and language support"""
        db = next(get_db())
        try:
            # Check if analysis exists in database
            existing = db.query(VerseAnalysis).filter(
                VerseAnalysis.book == book,
                VerseAnalysis.chapter == chapter,
                VerseAnalysis.verse == verse,
                VerseAnalysis.language == language
            ).first()
            
            if existing:
                # Convert database model to response schema
                return VerseAnalysisResponse(
                    book=existing.book,
                    chapter=existing.chapter,
                    verse=existing.verse,
                    latin_text=existing.latin_text,
                    grammar_breakdown=[
                        GrammarItem(
                            word=item.word,
                            word_index=item.word_index,
                            meaning=item.meaning,
                            grammar_description=item.grammar_description,
                            part_of_speech=item.part_of_speech,
                            morphology=item.morphology,
                            icon=item.icon,
                            color=item.color,
                            confidence=item.confidence,
                            source=item.source
                        ) for item in existing.grammar_breakdown
                    ],
                    interpretations=[
                        InterpretationLayerSchema(
                            layer_type=layer.layer_type,
                            title=layer.title,
                            points=json.loads(layer.points),
                            icon=layer.icon,
                            color_gradient=layer.color_gradient,
                            confidence=layer.confidence
                        ) for layer in existing.interpretations
                    ]
                )
            
            # If no existing analysis, create new one
            # This would involve calling OpenAI and other analysis services
            # For now, return None to indicate verse not found
            return None
            
        except Exception as e:
            print(f"Error analyzing verse: {e}")
            return None
        finally:
            db.close()
    
    def get_verses_for_word(self, word: str, language: str = "la") -> List[Dict[str, Any]]:
        """Get all verses where a word appears"""
        db = next(get_db())
        try:
            # Query verses containing the word
            verses = db.query(VerseAnalysis).join(
                GrammarBreakdown,
                VerseAnalysis.id == GrammarBreakdown.verse_analysis_id
            ).filter(
                GrammarBreakdown.word == word,
                VerseAnalysis.language == language
            ).all()
            
            return [
                {
                    "verse_reference": f"{verse.book} {verse.chapter}:{verse.verse}",
                    "verse_text": verse.latin_text,
                    "position": next(
                        (item.word_index for item in verse.grammar_breakdown if item.word == word),
                        0
                    )
                }
                for verse in verses
            ]
            
        except Exception as e:
            print(f"Error getting verses for word: {e}")
            return []
        finally:
            db.close()
    
    def get_verses_by_reference(self, book: str, chapter: int, skip: int = 0, limit: int = 100) -> List[Verse]:
        """Get verses for a specific book and chapter with pagination"""
        db = next(get_db())
        try:
            # Get book ID first
            book_record = db.query(Book).filter(Book.abbreviation == book).first()
            if not book_record:
                return []
            
            # Query verses for the given book and chapter
            verses = db.query(Verse).filter(
                Verse.book_id == book_record.id,
                Verse.chapter == chapter
            ).offset(skip).limit(limit).all()
            
            return verses
            
        except Exception as e:
            print(f"Error getting verses by reference: {e}")
            return []
        finally:
            db.close() 