"""
AI-Driven Lexicon Builder

This system:
1. Queries OpenAI for entire phrases/verses
2. Parses structured responses to extract individual word definitions  
3. Implements quality scoring for incoming data
4. Builds a learning database that improves over time
5. Uses algorithms to determine if new data is better than existing data
"""

import json
import sqlite3
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from backend.app.core.config import settings
import hashlib
import re
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

@dataclass
class WordDefinition:
    """Enhanced word definition with quality metrics"""
    latin: str
    definition: str
    etymology: str
    part_of_speech: str
    morphology: str = ""
    pronunciation: str = ""
    source: str = "ai_learning"
    confidence: float = 0.0
    quality_score: float = 0.0
    usage_context: str = ""
    verse_reference: str = ""
    created_at: str = ""
    updated_at: str = ""
    definition_hash: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.definition_hash:
            self.definition_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate hash for definition uniqueness"""
        content = f"{self.latin}{self.definition}{self.etymology}{self.part_of_speech}{self.morphology}"
        return hashlib.md5(content.encode()).hexdigest()

@dataclass
class VerseAnalysisRequest:
    """Request for verse analysis"""
    verse_text: str
    verse_reference: str
    context: str = ""
    target_quality: float = 0.8

@dataclass
class VerseAnalysisResponse:
    """Response from verse analysis"""
    success: bool
    verse_text: str
    verse_reference: str
    word_definitions: List[WordDefinition]
    overall_quality: float
    processing_time: float
    source: str = "ai_learning"
    error_message: str = ""

class QualityAnalyzer:
    """Analyzes and scores definition quality"""
    
    @staticmethod
    def calculate_definition_quality(definition: WordDefinition, context: str = "") -> float:
        """Calculate quality score for a definition (0.0 to 1.0)"""
        score = 0.0
        
        # Length and completeness (0.3 max)
        if definition.definition and len(definition.definition) > 10:
            score += 0.1
        if definition.etymology and len(definition.etymology) > 5:
            score += 0.1
        if definition.morphology and len(definition.morphology) > 3:
            score += 0.1
        
        # Part of speech accuracy (0.2 max)
        valid_pos = ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'participle']
        if definition.part_of_speech.lower() in valid_pos:
            score += 0.2
        
        # Latin validity (0.2 max)
        if definition.latin and re.match(r'^[a-zA-Z\-āēīōūĀĒĪŌŪ]+$', definition.latin):
            score += 0.1
        if len(definition.latin) > 2:
            score += 0.1
        
        # Context relevance (0.2 max)
        if context and definition.usage_context:
            # Simple keyword matching for now
            context_words = set(context.lower().split())
            usage_words = set(definition.usage_context.lower().split())
            overlap = len(context_words.intersection(usage_words))
            if overlap > 0:
                score += min(0.2, overlap * 0.05)
        
        # Confidence bonus (0.1 max)
        if definition.confidence > 0:
            score += min(0.1, definition.confidence * 0.1)
            
        return min(1.0, score)
    
    @staticmethod
    def compare_definitions(existing: WordDefinition, new: WordDefinition, context: str = "") -> Dict[str, Any]:
        """Compare two definitions and determine which is better"""
        existing_quality = QualityAnalyzer.calculate_definition_quality(existing, context)
        new_quality = QualityAnalyzer.calculate_definition_quality(new, context)
        
        # Update quality scores
        existing.quality_score = existing_quality
        new.quality_score = new_quality
        
        comparison = {
            "existing_quality": existing_quality,
            "new_quality": new_quality,
            "winner": "new" if new_quality > existing_quality else "existing",
            "improvement": new_quality - existing_quality,
            "recommendation": "replace" if new_quality > existing_quality + 0.1 else "keep"
        }
        
        # Additional factors
        if existing.source == "dictionary" and new.source == "ai_learning":
            comparison["winner"] = "existing"  # Prefer dictionary over AI
            comparison["recommendation"] = "keep"
        elif new.source == "dictionary" and existing.source == "ai_learning":
            comparison["winner"] = "new"  # Dictionary trumps AI
            comparison["recommendation"] = "replace"
            
        return comparison

class AILexiconBuilder:
    """Main AI-driven lexicon building system"""
    
    def __init__(self, database_path: str = None, openai_api_key: str = None):
        self.database_path = database_path or f"{settings.SQLITE_DB_PATH}_ai_lexicon.db"
        self.openai_enabled = bool(OPENAI_AVAILABLE and openai_api_key)
        
        if self.openai_enabled and openai_api_key:
            self.openai_client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                organization=os.getenv("OPENAI_ORG_ID") or None
            )
        else:
            self.openai_client = None
            
        self.quality_analyzer = QualityAnalyzer()
        self.setup_database()
    
    def setup_database(self):
        """Setup the learning database schema"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Word definitions with quality metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_word_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    latin TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    etymology TEXT,
                    part_of_speech TEXT,
                    morphology TEXT,
                    pronunciation TEXT,
                    source TEXT DEFAULT 'ai_learning',
                    confidence REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 0.0,
                    usage_context TEXT,
                    verse_reference TEXT,
                    definition_hash TEXT UNIQUE,
                    created_at TEXT,
                    updated_at TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # Verse analysis history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verse_analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verse_text TEXT NOT NULL,
                    verse_reference TEXT NOT NULL,
                    analysis_request TEXT,
                    analysis_response TEXT,
                    overall_quality REAL,
                    processing_time REAL,
                    word_count INTEGER,
                    successful_extractions INTEGER,
                    created_at TEXT,
                    source TEXT DEFAULT 'ai_learning'
                )
            ''')
            
            # Quality improvement tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_latin TEXT,
                    old_definition_hash TEXT,
                    new_definition_hash TEXT,
                    quality_improvement REAL,
                    improvement_reason TEXT,
                    created_at TEXT
                )
            ''')
            
            # Learning statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    verses_analyzed INTEGER DEFAULT 0,
                    words_extracted INTEGER DEFAULT 0,
                    quality_improvements INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.0,
                    openai_calls INTEGER DEFAULT 0,
                    processing_time_total REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    async def analyze_verse_with_ai(self, request: VerseAnalysisRequest) -> VerseAnalysisResponse:
        """Analyze entire verse with AI and extract word definitions"""
        if not self.openai_enabled:
            return VerseAnalysisResponse(
                success=False,
                verse_text=request.verse_text,
                verse_reference=request.verse_reference,
                word_definitions=[],
                overall_quality=0.0,
                processing_time=0.0,
                error_message="OpenAI not available"
            )
        
        start_time = time.time()
        
        try:
            # Construct detailed prompt for word-by-word analysis
            prompt = f"""
REPLY **ONLY** following the template blocks below – do not omit or rename any heading,
do not add commentary outside the blocks.  Replace each […] with your content.

📖 {request.verse_reference} (VULGATA)
Latin:
"{request.verse_text}"

🌍 Translations:
Language\tTranslation
English\t[…]
Español\t[…]
Italiano\t[…]
Português\t[…]
Русский\t[…]

🧠 Grammar Breakdown:
[…   one explanation per line – keep order as in the verse …]

🔍 Interpretation of {request.verse_reference}
✝️ 1. Theological View
[…]

🧠 2. Symbolic (Jungian) View
[…]

🌍 3. Cosmological-Historical View
[…]

🧾 Summary Table
Layer\tWaters Represent\tDry Land Symbolizes\tDivine Act
Theology\t[…]\t[…]\t[…]
Jungian\t[…]\t[…]\t[…]
Ancient World\t[…]\t[…]\t[…]
""".strip()
            
            response = await self._call_openai(prompt)
            
            if not response:
                raise Exception("No response from OpenAI")
            
            # Parse the response
            analysis_data = self._parse_ai_response(response)
            word_definitions = self._extract_word_definitions(
                analysis_data, request.verse_reference, request.verse_text
            )
            
            # Calculate overall quality
            overall_quality = self._calculate_overall_quality(word_definitions, request.verse_text)
            
            processing_time = time.time() - start_time
            
            # Store in database
            await self._store_verse_analysis(request, word_definitions, overall_quality, processing_time)
            
            return VerseAnalysisResponse(
                success=True,
                verse_text=request.verse_text,
                verse_reference=request.verse_reference,
                word_definitions=word_definitions,
                overall_quality=overall_quality,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return VerseAnalysisResponse(
                success=False,
                verse_text=request.verse_text,
                verse_reference=request.verse_reference,
                word_definitions=[],
                overall_quality=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _call_openai(self, prompt: str) -> str:
        """Make OpenAI API call with rate limiting"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Latin scholar and lexicographer. Provide accurate, detailed word analysis in the requested JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return ""
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract JSON"""
        try:
            # Clean up response
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            return {}
    
    def _extract_word_definitions(self, analysis_data: Dict[str, Any], verse_ref: str, verse_text: str) -> List[WordDefinition]:
        """Extract word definitions from parsed AI response"""
        definitions = []
        
        verse_analysis = analysis_data.get("verse_analysis", {})
        word_defs = verse_analysis.get("word_definitions", [])
        
        for word_data in word_defs:
            if not isinstance(word_data, dict):
                continue
                
            try:
                definition = WordDefinition(
                    latin=word_data.get("latin", ""),
                    definition=word_data.get("definition", ""),
                    etymology=word_data.get("etymology", ""),
                    part_of_speech=word_data.get("part_of_speech", ""),
                    morphology=word_data.get("morphology", ""),
                    pronunciation=word_data.get("pronunciation", ""),
                    confidence=float(word_data.get("confidence", 0.0)),
                    usage_context=word_data.get("usage_context", ""),
                    verse_reference=verse_ref,
                    source="ai_learning"
                )
                
                # Calculate quality score
                definition.quality_score = self.quality_analyzer.calculate_definition_quality(
                    definition, verse_text
                )
                
                definitions.append(definition)
                
            except Exception as e:
                print(f"Error processing word definition: {e}")
                continue
        
        return definitions
    
    def _calculate_overall_quality(self, definitions: List[WordDefinition], verse_text: str) -> float:
        """Calculate overall quality for the verse analysis"""
        if not definitions:
            return 0.0
        
        total_quality = sum(d.quality_score for d in definitions)
        avg_quality = total_quality / len(definitions)
        
        # Bonus for completeness (analyzing all words in verse)
        verse_words = len(verse_text.split())
        analyzed_words = len(definitions)
        completeness_bonus = min(0.1, (analyzed_words / verse_words) * 0.1)
        
        return min(1.0, avg_quality + completeness_bonus)
    
    async def _store_verse_analysis(self, request: VerseAnalysisRequest, definitions: List[WordDefinition], 
                                   overall_quality: float, processing_time: float):
        """Store verse analysis results in database"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Store verse analysis
            cursor.execute('''
                INSERT INTO verse_analysis_history 
                (verse_text, verse_reference, analysis_request, analysis_response, 
                 overall_quality, processing_time, word_count, successful_extractions, created_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.verse_text,
                request.verse_reference,
                json.dumps(asdict(request)),
                json.dumps([asdict(d) for d in definitions]),
                overall_quality,
                processing_time,
                len(request.verse_text.split()),
                len(definitions),
                datetime.now().isoformat(),
                "ai_learning"
            ))
            
            # Store/update individual word definitions
            for definition in definitions:
                await self._store_or_update_definition(definition, conn)
            
            # Update daily stats
            await self._update_learning_stats(len(definitions), overall_quality, processing_time, 1, conn)
            
            conn.commit()
    
    async def _store_or_update_definition(self, definition: WordDefinition, conn: sqlite3.Connection):
        """Store or update word definition with quality comparison"""
        cursor = conn.cursor()
        
        # Check for existing definition
        cursor.execute('''
            SELECT * FROM ai_word_definitions 
            WHERE latin = ? AND is_active = 1
            ORDER BY quality_score DESC LIMIT 1
        ''', (definition.latin,))
        
        existing_row = cursor.fetchone()
        
        if existing_row:
            # Compare with existing
            existing_def = self._row_to_definition(existing_row)
            comparison = self.quality_analyzer.compare_definitions(
                existing_def, definition, definition.usage_context
            )
            
            if comparison["recommendation"] == "replace":
                # Mark old as inactive
                cursor.execute('''
                    UPDATE ai_word_definitions SET is_active = 0 WHERE id = ?
                ''', (existing_row[0],))
                
                # Insert new definition
                self._insert_definition(definition, cursor)
                
                # Record improvement
                cursor.execute('''
                    INSERT INTO quality_improvements 
                    (word_latin, old_definition_hash, new_definition_hash, 
                     quality_improvement, improvement_reason, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    definition.latin,
                    existing_def.definition_hash,
                    definition.definition_hash,
                    comparison["improvement"],
                    f"Quality improved from {comparison['existing_quality']:.2f} to {comparison['new_quality']:.2f}",
                    datetime.now().isoformat()
                ))
            else:
                # Just increment usage count of existing
                cursor.execute('''
                    UPDATE ai_word_definitions SET usage_count = usage_count + 1 WHERE id = ?
                ''', (existing_row[0],))
        else:
            # No existing definition, insert new
            self._insert_definition(definition, cursor)
    
    def _insert_definition(self, definition: WordDefinition, cursor: sqlite3.Cursor):
        """Insert new definition into database"""
        cursor.execute('''
            INSERT INTO ai_word_definitions 
            (latin, definition, etymology, part_of_speech, morphology, pronunciation,
             source, confidence, quality_score, usage_context, verse_reference,
             definition_hash, created_at, updated_at, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            definition.latin, definition.definition, definition.etymology,
            definition.part_of_speech, definition.morphology, definition.pronunciation,
            definition.source, definition.confidence, definition.quality_score,
            definition.usage_context, definition.verse_reference, definition.definition_hash,
            definition.created_at, definition.updated_at, 1
        ))
    
    def _row_to_definition(self, row) -> WordDefinition:
        """Convert database row to WordDefinition object"""
        return WordDefinition(
            latin=row[1],
            definition=row[2],
            etymology=row[3] or "",
            part_of_speech=row[4] or "",
            morphology=row[5] or "",
            pronunciation=row[6] or "",
            source=row[7],
            confidence=row[8],
            quality_score=row[9],
            usage_context=row[10] or "",
            verse_reference=row[11] or "",
            definition_hash=row[12],
            created_at=row[13],
            updated_at=row[14]
        )
    
    async def _update_learning_stats(self, words_extracted: int, avg_quality: float, 
                                   processing_time: float, openai_calls: int, conn: sqlite3.Connection):
        """Update daily learning statistics"""
        cursor = conn.cursor()
        today = datetime.now().date().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO learning_stats 
            (date, verses_analyzed, words_extracted, average_quality, 
             processing_time_total, openai_calls)
            VALUES (
                ?,
                COALESCE((SELECT verses_analyzed FROM learning_stats WHERE date = ?), 0) + 1,
                COALESCE((SELECT words_extracted FROM learning_stats WHERE date = ?), 0) + ?,
                ?,
                COALESCE((SELECT processing_time_total FROM learning_stats WHERE date = ?), 0) + ?,
                COALESCE((SELECT openai_calls FROM learning_stats WHERE date = ?), 0) + ?
            )
        ''', (today, today, today, words_extracted, avg_quality, today, processing_time, today, openai_calls))
    
    def get_best_definition(self, latin_word: str) -> Optional[WordDefinition]:
        """Get the highest quality definition for a word"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ai_word_definitions 
                WHERE latin = ? AND is_active = 1
                ORDER BY quality_score DESC, usage_count DESC LIMIT 1
            ''', (latin_word,))
            
            row = cursor.fetchone()
            return self._row_to_definition(row) if row else None
    
    def get_learning_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get learning statistics for the past N days"""
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    SUM(verses_analyzed) as total_verses,
                    SUM(words_extracted) as total_words,
                    SUM(quality_improvements) as total_improvements,
                    AVG(average_quality) as avg_quality,
                    SUM(openai_calls) as total_calls,
                    SUM(processing_time_total) as total_time
                FROM learning_stats 
                WHERE date BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            stats = cursor.fetchone()
            
            # Get top quality words
            cursor.execute('''
                SELECT latin, quality_score, usage_count 
                FROM ai_word_definitions 
                WHERE is_active = 1 
                ORDER BY quality_score DESC, usage_count DESC 
                LIMIT 10
            ''', ())
            
            top_words = cursor.fetchall()
            
            return {
                "period_days": days,
                "total_verses_analyzed": stats[0] or 0,
                "total_words_extracted": stats[1] or 0,
                "total_quality_improvements": stats[2] or 0,
                "average_quality": round(stats[3] or 0, 3),
                "total_openai_calls": stats[4] or 0,
                "total_processing_time": round(stats[5] or 0, 2),
                "top_quality_words": [
                    {"latin": row[0], "quality": round(row[1], 3), "usage": row[2]}
                    for row in top_words
                ]
            } 
            