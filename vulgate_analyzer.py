#!/usr/bin/env python3
"""
Comprehensive Vulgate Analysis System

This system provides:
1. Grammar breakdown with OpenAI analysis and FontAwesome icons
2. Three interpretation layers (Theological, Symbolic, Cosmological)
3. Multi-language translation support
4. Progress tracking for the entire Vulgate
"""

import json
import os
import re
import sqlite3
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import openai
from datetime import datetime
from enhanced_dictionary import EnhancedDictionary

@dataclass
class GrammarItem:
    word: str
    word_index: int
    meaning: str
    grammar_description: str
    part_of_speech: str
    morphology: str
    icon: str
    color: str
    confidence: float
    source: str

@dataclass
class InterpretationLayer:
    layer_type: str  # theological, symbolic, cosmological
    title: str
    points: List[str]
    icon: str
    color_gradient: str
    confidence: float

@dataclass
class VerseAnalysisResult:
    book: str
    chapter: int
    verse: int
    latin_text: str
    grammar_breakdown: List[GrammarItem]
    interpretations: List[InterpretationLayer]
    analysis_complete: bool

class VulgateAnalyzer:
    """Comprehensive analyzer for Vulgate verses"""
    
    def __init__(self, openai_api_key: str = None, database_path: str = "vulgate_analysis.db"):
        """Initialize the Vulgate analyzer with OpenAI API key and database path"""
        self.database_path = database_path
        self.setup_database()
        
        # Set up OpenAI
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            self.openai_enabled = True
        else:
            self.openai_enabled = False
            print("OpenAI API key not provided. Analysis features disabled.")
        
        # Initialize enhanced dictionary with same database path
        self.dictionary = EnhancedDictionary(
            dictionary_path="latin_dictionary.json",
            openai_api_key=openai_api_key,
            cache_db=database_path
        )
        
        # FontAwesome icon mappings for different word types
        self.grammar_icons = {
            'verb': 'fa-running',
            'noun': 'fa-cube',
            'adjective': 'fa-palette',
            'adverb': 'fa-bolt',
            'preposition': 'fa-link',
            'conjunction': 'fa-plus',
            'pronoun': 'fa-user',
            'interjection': 'fa-exclamation',
            'participle': 'fa-star',
            'infinitive': 'fa-infinity',
            'subjunctive': 'fa-question',
            'imperative': 'fa-exclamation-triangle',
            'default': 'fa-language'
        }
        
        # Color classes for different word types
        self.grammar_colors = {
            'verb': 'text-blue-600',
            'noun': 'text-green-600', 
            'adjective': 'text-purple-600',
            'adverb': 'text-orange-600',
            'preposition': 'text-gray-600',
            'conjunction': 'text-pink-600',
            'pronoun': 'text-red-600',
            'participle': 'text-indigo-600',
            'default': 'text-blue-600'
        }
        
        # Interpretation layer configurations
        self.layer_configs = {
            'theological': {
                'icon': 'fa-cross',
                'gradient': 'from-yellow-400 to-amber-400',
                'border': 'border-yellow-300'
            },
            'symbolic': {
                'icon': 'fa-brain', 
                'gradient': 'from-pink-400 to-rose-400',
                'border': 'border-pink-300'
            },
            'cosmological': {
                'icon': 'fa-globe',
                'gradient': 'from-blue-400 to-cyan-400', 
                'border': 'border-blue-300'
            }
        }
    
    def setup_database(self):
        """Set up SQLite database for storing analyses"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Create tables for verse analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verse_analyses (
                id INTEGER PRIMARY KEY,
                book_abbreviation TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                verse_number INTEGER NOT NULL,
                latin_text TEXT NOT NULL,
                grammar_analyzed BOOLEAN DEFAULT FALSE,
                theological_analyzed BOOLEAN DEFAULT FALSE,
                symbolic_analyzed BOOLEAN DEFAULT FALSE,
                cosmological_analyzed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book_abbreviation, chapter_number, verse_number)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grammar_breakdowns (
                id INTEGER PRIMARY KEY,
                verse_analysis_id INTEGER,
                word TEXT NOT NULL,
                word_index INTEGER NOT NULL,
                meaning TEXT NOT NULL,
                grammar_description TEXT NOT NULL,
                part_of_speech TEXT,
                morphology TEXT,
                fontawesome_icon TEXT DEFAULT 'fa-language',
                color_class TEXT DEFAULT 'text-blue-600',
                confidence REAL DEFAULT 1.0,
                FOREIGN KEY(verse_analysis_id) REFERENCES verse_analyses(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interpretation_layers (
                id INTEGER PRIMARY KEY,
                verse_analysis_id INTEGER,
                layer_type TEXT NOT NULL,
                title TEXT NOT NULL,
                points TEXT NOT NULL,
                fontawesome_icon TEXT NOT NULL,
                color_gradient TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                FOREIGN KEY(verse_analysis_id) REFERENCES verse_analyses(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS word_cache (
                id INTEGER PRIMARY KEY,
                word TEXT NOT NULL UNIQUE,
                definition TEXT NOT NULL,
                etymology TEXT,
                part_of_speech TEXT,
                morphology TEXT,
                pronunciation TEXT,
                source TEXT DEFAULT 'dictionary',
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_verse_grammar(self, verse_text: str) -> List[GrammarItem]:
        """Analyze grammar of a verse using OpenAI"""
        if not self.openai_enabled:
            print("OpenAI disabled, skipping grammar analysis")
            return []
        
        print(f"Making OpenAI call for grammar analysis of verse: {verse_text[:50]}...")
        
        try:
            words = verse_text.split()
            
            prompt = f"""
            Analyze the Latin verse: "{verse_text}"
            
            For each word, provide detailed grammatical analysis:
            
            Return JSON format:
            {{
                "grammar_analysis": [
                    {{
                        "word": "word here",
                        "word_index": 0,
                        "meaning": "English meaning",
                        "grammar_description": "detailed grammatical analysis",
                        "part_of_speech": "noun/verb/adjective/etc",
                        "morphology": "case, number, gender, tense, etc"
                    }}
                ]
            }}
            
            Be thorough and scholarly in your analysis. Consider:
            - Verb tenses, moods, voices
            - Noun cases, numbers, genders
            - Adjective agreements
            - Particle and conjunction functions
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Latin scholar. Provide detailed, accurate grammatical analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            data = json.loads(content)
            grammar_items = []
            
            for item in data.get('grammar_analysis', []):
                pos = item.get('part_of_speech', 'default').lower()
                
                grammar_item = GrammarItem(
                    word=item.get('word', ''),
                    word_index=item.get('word_index', 0),
                    meaning=item.get('meaning', ''),
                    grammar_description=item.get('grammar_description', ''),
                    part_of_speech=pos,
                    morphology=item.get('morphology', ''),
                    icon=self.grammar_icons.get(pos, self.grammar_icons['default']),
                    color=self.grammar_colors.get(pos, self.grammar_colors['default']),
                    confidence=0.9,
                    source='openai'
                )
                grammar_items.append(grammar_item)
            
            return grammar_items
            
        except Exception as e:
            print(f"Grammar analysis failed: {e}")
            return []
    
    def analyze_interpretation_layers(self, verse_text: str, book: str, chapter: int, verse: int) -> List[InterpretationLayer]:
        """Generate the three interpretation layers for a verse"""
        if not self.openai_enabled:
            print("OpenAI disabled, skipping interpretation analysis")
            return []
        
        print(f"Making OpenAI call for interpretation analysis of {book} {chapter}:{verse}")
        
        try:
            prompt = f"""
            Analyze this Latin verse from {book} {chapter}:{verse}:
            "{verse_text}"
            
            Provide three distinct layers of interpretation in this exact JSON format:
            {{
                "interpretations": [
                    {{
                        "layer_type": "theological",
                        "title": "Theological View",
                        "points": [
                            "Point about divine action",
                            "Point about spiritual meaning",
                            "Point about religious significance"
                        ]
                    }},
                    {{
                        "layer_type": "symbolic",
                        "title": "Jungian-Campbell Symbolic Analysis",
                        "points": [
                            "Jungian archetypal analysis (identify specific archetypes: Anima/Animus, Shadow, Self, Mother, Father, Wise Old Man/Woman, Hero, etc.)",
                            "Campbell's Hero's Journey stage identification and mythological pattern analysis",
                            "Cross-cultural mythological parallels and comparative mythology insights",
                            "Individuation process elements and psychological transformation themes",
                            "Collective unconscious manifestations and depth psychology insights",
                            "Sacred symbolism, numerology, and cosmic/geometric significance"
                        ]
                    }},
                    {{
                        "layer_type": "cosmological",
                        "title": "Cosmological-Historical View",
                        "points": [
                            "Point about ancient context",
                            "Point about historical significance",
                            "Point about cultural meaning"
                        ]
                    }}
                ]
            }}
            
            For the symbolic layer, draw from Jung's archetypal psychology, Campbell's monomyth and comparative mythology, and cross-cultural mythological patterns. Focus on scholarly depth and psychological insight.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a biblical scholar expert in theology, Jungian depth psychology, Joseph Campbell's comparative mythology, archetypal symbolism, the Hero's Journey monomyth, cross-cultural mythological patterns, and ancient history. You excel at identifying archetypal symbols, mythological parallels, and psychological transformation themes in sacred texts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,  # Increased for expanded symbolic analysis
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            print(f"OpenAI response: {content}")  # Debug log
            
            try:
                data = json.loads(content)
                interpretation_layers = []
                
                for item in data.get('interpretations', []):
                    layer_type = item.get('layer_type', '')
                    config = self.layer_configs.get(layer_type, self.layer_configs['theological'])
                    
                    layer = InterpretationLayer(
                        layer_type=layer_type,
                        title=item.get('title', ''),
                        points=item.get('points', []),
                        icon=config['icon'],
                        color_gradient=config['gradient'],
                        confidence=0.85
                    )
                    interpretation_layers.append(layer)
                
                print(f"Generated {len(interpretation_layers)} interpretation layers")  # Debug log
                return interpretation_layers
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse OpenAI response as JSON: {e}")
                print(f"Raw response: {content}")
                return []
            
        except Exception as e:
            print(f"Interpretation analysis failed: {e}")
            return []
    
    def analyze_verse_complete(self, book: str, chapter: int, verse: int, verse_text: str) -> VerseAnalysisResult:
        """Analyze a verse completely, including grammar and interpretations"""
        # First check if we have this analysis in the database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, grammar_analyzed, theological_analyzed, symbolic_analyzed, cosmological_analyzed
            FROM verse_analyses
            WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
        ''', (book, chapter, verse))
        
        result = cursor.fetchone()
        
        if result:
            verse_id, grammar_analyzed, theological_analyzed, symbolic_analyzed, cosmological_analyzed = result
            
            # If we have a complete analysis, return it
            if all([grammar_analyzed, theological_analyzed, symbolic_analyzed, cosmological_analyzed]):
                return self._load_analysis_from_db(verse_id)
            
            # If we have partial analysis, complete the missing parts
            grammar_items = []
            if not grammar_analyzed:
                grammar_items = self.analyze_verse_grammar(verse_text)
            else:
                cursor.execute('''
                    SELECT word, word_index, meaning, grammar_description, part_of_speech,
                           morphology, fontawesome_icon, color_class, confidence, source
                    FROM grammar_breakdowns
                    WHERE verse_analysis_id = ?
                    ORDER BY word_index
                ''', (verse_id,))
                for row in cursor.fetchall():
                    grammar_items.append(GrammarItem(*row))
            
            interpretations = []
            if not all([theological_analyzed, symbolic_analyzed, cosmological_analyzed]):
                interpretations = self.analyze_interpretation_layers(verse_text, book, chapter, verse)
            else:
                cursor.execute('''
                    SELECT layer_type, title, points, fontawesome_icon, color_gradient, confidence, source
                    FROM interpretation_layers
                    WHERE verse_analysis_id = ?
                ''', (verse_id,))
                for row in cursor.fetchall():
                    points = json.loads(row[2])  # points is stored as JSON string
                    interpretations.append(InterpretationLayer(
                        layer_type=row[0],
                        title=row[1],
                        points=points,
                        icon=row[3],
                        color_gradient=row[4],
                        confidence=row[5]
                    ))
            
            analysis = VerseAnalysisResult(
                book=book,
                chapter=chapter,
                verse=verse,
                latin_text=verse_text,
                grammar_breakdown=grammar_items,
                interpretations=interpretations,
                analysis_complete=True
            )
            
            # Save the updated analysis
            self.save_analysis_to_db(analysis)
            return analysis
        
        # If no analysis exists, create a new one
        grammar_items = self.analyze_verse_grammar(verse_text)
        interpretations = self.analyze_interpretation_layers(verse_text, book, chapter, verse)
        
        analysis = VerseAnalysisResult(
            book=book,
            chapter=chapter,
            verse=verse,
            latin_text=verse_text,
            grammar_breakdown=grammar_items,
            interpretations=interpretations,
            analysis_complete=True
        )
        
        self.save_analysis_to_db(analysis)
        return analysis

    def _load_analysis_from_db(self, verse_id: int) -> VerseAnalysisResult:
        """Load a complete analysis from the database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Get verse info
        cursor.execute('''
            SELECT book_abbreviation, chapter_number, verse_number, latin_text
            FROM verse_analyses
            WHERE id = ?
        ''', (verse_id,))
        book, chapter, verse, latin_text = cursor.fetchone()
        
        # Get grammar breakdown
        cursor.execute('''
            SELECT word, word_index, meaning, grammar_description, part_of_speech,
                   morphology, fontawesome_icon, color_class, confidence, source
            FROM grammar_breakdowns
            WHERE verse_analysis_id = ?
            ORDER BY word_index
        ''', (verse_id,))
        grammar_items = [GrammarItem(*row) for row in cursor.fetchall()]
        
        # Get interpretations
        cursor.execute('''
            SELECT layer_type, title, points, fontawesome_icon, color_gradient, confidence, source
            FROM interpretation_layers
            WHERE verse_analysis_id = ?
        ''', (verse_id,))
        interpretations = []
        for row in cursor.fetchall():
            points = json.loads(row[2])  # points is stored as JSON string
            interpretations.append(InterpretationLayer(
                layer_type=row[0],
                title=row[1],
                points=points,
                icon=row[3],
                color_gradient=row[4],
                confidence=row[5]
            ))
        
        return VerseAnalysisResult(
            book=book,
            chapter=chapter,
            verse=verse,
            latin_text=latin_text,
            grammar_breakdown=grammar_items,
            interpretations=interpretations,
            analysis_complete=True
        )
    
    def save_analysis_to_db(self, analysis: VerseAnalysisResult):
        """Save analysis results to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            # Insert or update verse analysis
            cursor.execute('''
                INSERT OR REPLACE INTO verse_analyses 
                (book_abbreviation, chapter_number, verse_number, latin_text, 
                 grammar_analyzed, theological_analyzed, symbolic_analyzed, cosmological_analyzed, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis.book, analysis.chapter, analysis.verse, analysis.latin_text,
                len(analysis.grammar_breakdown) > 0,
                any(i.layer_type == 'theological' for i in analysis.interpretations),
                any(i.layer_type == 'symbolic' for i in analysis.interpretations),
                any(i.layer_type == 'cosmological' for i in analysis.interpretations),
                datetime.utcnow()
            ))
            
            verse_analysis_id = cursor.lastrowid
            
            # Save grammar breakdown
            for grammar_item in analysis.grammar_breakdown:
                cursor.execute('''
                    INSERT INTO grammar_breakdowns 
                    (verse_analysis_id, word, word_index, meaning, grammar_description, 
                     part_of_speech, morphology, fontawesome_icon, color_class, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    verse_analysis_id, grammar_item.word, grammar_item.word_index,
                    grammar_item.meaning, grammar_item.grammar_description,
                    grammar_item.part_of_speech, grammar_item.morphology,
                    grammar_item.icon, grammar_item.color, 
                    grammar_item.confidence
                ))
            
            # Save interpretation layers
            for interpretation in analysis.interpretations:
                cursor.execute('''
                    INSERT INTO interpretation_layers 
                    (verse_analysis_id, layer_type, title, points, fontawesome_icon, color_gradient, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    verse_analysis_id, interpretation.layer_type, interpretation.title,
                    json.dumps(interpretation.points), interpretation.icon,
                    interpretation.color_gradient, interpretation.confidence
                ))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error saving analysis to database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_analysis_progress(self) -> Dict[str, Any]:
        """Get overall analysis progress statistics"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            # Count verse analyses
            cursor.execute('SELECT COUNT(*) FROM verse_analyses')
            total_analyzed = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE grammar_analyzed = TRUE')
            grammar_complete = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE theological_analyzed = TRUE')
            theological_complete = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE symbolic_analyzed = TRUE')
            symbolic_complete = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE cosmological_analyzed = TRUE')
            cosmological_complete = cursor.fetchone()[0]
            
            # Estimate total verses in Vulgate (approximately 31,000)
            total_verses_estimate = 31000
            
            return {
                'verse_analysis': {
                    'total_verses_estimate': total_verses_estimate,
                    'analyzed_verses': total_analyzed,
                    'grammar_complete': grammar_complete,
                    'theological_complete': theological_complete,
                    'symbolic_complete': symbolic_complete,
                    'cosmological_complete': cosmological_complete,
                    'completion_percentage': round((total_analyzed / total_verses_estimate) * 100, 2)
                },
                'remaining_work': {
                    'verses_to_analyze': total_verses_estimate - total_analyzed,
                    'grammar_remaining': total_verses_estimate - grammar_complete,
                    'theological_remaining': total_verses_estimate - theological_complete,
                    'symbolic_remaining': total_verses_estimate - symbolic_complete,
                    'cosmological_remaining': total_verses_estimate - cosmological_complete
                }
            }
            
        except Exception as e:
            print(f"Error getting progress: {e}")
            return {}
        finally:
            conn.close()

def main():
    """Test the analyzer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vulgate_analyzer.py <verse_text>")
        print("Example: python vulgate_analyzer.py 'In principio creavit Deus caelum et terram'")
        return
    
    verse_text = sys.argv[1]
    api_key = os.getenv('OPENAI_API_KEY')
    
    analyzer = VulgateAnalyzer(openai_api_key=api_key)
    result = analyzer.analyze_verse_complete("Gn", 1, 1, verse_text)
    
    print(f"\n{'='*80}")
    print(f"ANALYSIS COMPLETE: {result.book} {result.chapter}:{result.verse}")
    print(f"{'='*80}")
    
    print(f"\nLatin: {result.latin_text}")
    
    print(f"\nGrammar Breakdown ({len(result.grammar_breakdown)} words):")
    for item in result.grammar_breakdown:
        print(f"  {item.word} [{item.icon}] = {item.meaning} ({item.grammar_description})")
    
    print(f"\nInterpretation Layers ({len(result.interpretations)} layers):")
    for layer in result.interpretations:
        print(f"  {layer.layer_type.upper()} [{layer.icon}]: {layer.title}")
        for point in layer.points:
            print(f"    • {point}")

if __name__ == "__main__":
    main() 