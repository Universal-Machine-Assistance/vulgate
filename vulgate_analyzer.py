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
        self.database_path = database_path
        self.setup_database()
        
        # Set up OpenAI
        if openai_api_key:
            # Update to use new OpenAI client
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            self.openai_enabled = True
        else:
            self.openai_enabled = False
            print("OpenAI API key not provided. Analysis features disabled.")
        
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
                source TEXT DEFAULT 'openai',
                FOREIGN KEY(verse_analysis_id) REFERENCES verse_analyses(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grammar_translations (
                id INTEGER PRIMARY KEY,
                grammar_breakdown_id INTEGER,
                language_code TEXT NOT NULL,
                meaning TEXT NOT NULL,
                grammar_description TEXT NOT NULL,
                FOREIGN KEY(grammar_breakdown_id) REFERENCES grammar_breakdowns(id)
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
                source TEXT DEFAULT 'openai',
                FOREIGN KEY(verse_analysis_id) REFERENCES verse_analyses(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS layer_translations (
                id INTEGER PRIMARY KEY,
                interpretation_layer_id INTEGER,
                language_code TEXT NOT NULL,
                title TEXT NOT NULL,
                points TEXT NOT NULL,
                FOREIGN KEY(interpretation_layer_id) REFERENCES interpretation_layers(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_progress (
                id INTEGER PRIMARY KEY,
                total_unique_words INTEGER DEFAULT 0,
                analyzed_words INTEGER DEFAULT 0,
                cached_words INTEGER DEFAULT 0,
                total_verses INTEGER DEFAULT 0,
                grammar_analyzed_verses INTEGER DEFAULT 0,
                theological_analyzed_verses INTEGER DEFAULT 0,
                symbolic_analyzed_verses INTEGER DEFAULT 0,
                cosmological_analyzed_verses INTEGER DEFAULT 0,
                supported_languages TEXT DEFAULT '["en", "es", "fr", "pt", "it"]',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version TEXT DEFAULT '1.0'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_verse_grammar(self, verse_text: str) -> List[GrammarItem]:
        """Analyze grammar of a verse using OpenAI"""
        if not self.openai_enabled:
            return []
        
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
            return []
        
        try:
            prompt = f"""
            Analyze the Latin verse from {book} {chapter}:{verse}: "{verse_text}"
            
            Provide three distinct interpretation layers:
            
            1. THEOLOGICAL LAYER: Focus on religious meaning, divine attributes, salvation themes
            2. SYMBOLIC (JUNGIAN) LAYER: Focus on archetypal symbols, psychological meanings, universal patterns  
            3. COSMOLOGICAL-HISTORICAL LAYER: Focus on creation themes, historical context, ancient worldview
            
            Return JSON format:
            {{
                "interpretations": [
                    {{
                        "layer_type": "theological",
                        "title": "Brief descriptive title",
                        "points": ["point 1", "point 2", "point 3"]
                    }},
                    {{
                        "layer_type": "symbolic", 
                        "title": "Brief descriptive title",
                        "points": ["point 1", "point 2", "point 3"]
                    }},
                    {{
                        "layer_type": "cosmological",
                        "title": "Brief descriptive title", 
                        "points": ["point 1", "point 2", "point 3"]
                    }}
                ]
            }}
            
            Keep each point concise but meaningful. Focus on scholarly insights.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a biblical scholar expert in theology, psychology, and ancient history."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
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
            
            return interpretation_layers
            
        except Exception as e:
            print(f"Interpretation analysis failed: {e}")
            return []
    
    def analyze_verse_complete(self, book: str, chapter: int, verse: int, verse_text: str) -> VerseAnalysisResult:
        """Complete analysis of a verse including grammar and interpretations"""
        
        print(f"Analyzing {book} {chapter}:{verse} - {verse_text[:50]}...")
        
        # Analyze grammar
        grammar_breakdown = self.analyze_verse_grammar(verse_text)
        
        # Analyze interpretation layers  
        interpretations = self.analyze_interpretation_layers(verse_text, book, chapter, verse)
        
        # Create result
        result = VerseAnalysisResult(
            book=book,
            chapter=chapter,
            verse=verse,
            latin_text=verse_text,
            grammar_breakdown=grammar_breakdown,
            interpretations=interpretations,
            analysis_complete=(len(grammar_breakdown) > 0 and len(interpretations) == 3)
        )
        
        # Save to database
        self.save_analysis_to_db(result)
        
        return result
    
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
                     part_of_speech, morphology, fontawesome_icon, color_class, confidence, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    verse_analysis_id, grammar_item.word, grammar_item.word_index,
                    grammar_item.meaning, grammar_item.grammar_description,
                    grammar_item.part_of_speech, grammar_item.morphology,
                    grammar_item.icon, grammar_item.color, 
                    grammar_item.confidence, grammar_item.source
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