from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import sqlite3
import os
from dataclasses import dataclass
from backend.app.core.config import settings
from backend.app.models.verse_analysis import VerseAnalysis, GrammarBreakdown, InterpretationLayer

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

@dataclass
class WordInfo:
    latin: str
    definition: str
    etymology: str
    part_of_speech: str
    morphology: str = ""
    pronunciation: str = ""
    source: str = "dictionary"
    confidence: float = 1.0
    theological_interpretation: str = ""

class EnhancedDictionary:
    """Enhanced dictionary with morphological analysis and OpenAI integration"""
    
    def __init__(self, database_path: str = None, openai_model: str = None):
        self.database_path = database_path or settings.SQLITE_DB_PATH
        self.cache_db = self.database_path  # For compatibility with existing code
        self.cache_db_path = self.database_path  # For new translation cache methods
        self.dictionary = {}  # Basic dictionary placeholder
        self.setup_database()
        # Check if OpenAI API key is available
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            self.openai_enabled = bool(OPENAI_AVAILABLE and api_key and api_key.strip())
            if self.openai_enabled:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.openai_client = None
            # choose model (default cheap)
            self.openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        except AttributeError:
            self.openai_enabled = False
            self.openai_client = None
        
        print(f"OpenAI enabled: {self.openai_enabled}")
    
    def setup_database(self):
        """Set up the local cache database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Create word cache table with language support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word_cache (
                    word TEXT PRIMARY KEY,
                    latin TEXT,
                    definition TEXT,
                    etymology TEXT,
                    part_of_speech TEXT,
                    morphology TEXT,
                    pronunciation TEXT,
                    source TEXT,
                    confidence REAL,
                    theological_interpretation TEXT,
                    language_code TEXT DEFAULT 'la',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create word-verse relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word_verse_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    verse_reference TEXT NOT NULL,
                    verse_text TEXT,
                    position INTEGER,
                    language_code TEXT DEFAULT 'la',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(word, verse_reference, position, language_code)
                )
            ''')
            
            # Create verse analysis cache table with language support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verse_analysis_cache (
                    verse_reference TEXT,
                    language_code TEXT,
                    verse_text TEXT,
                    word_analysis_json TEXT,
                    translations_json TEXT,
                    theological_layer_json TEXT,
                    jungian_layer_json TEXT,
                    cosmological_layer_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (verse_reference, language_code)
                )
            ''')
            
            # Create indexes for efficient lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_cache_language ON word_cache(language_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_verse_language ON word_verse_relationships(language_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_verse_analysis_language ON verse_analysis_cache(language_code)')
            
            conn.commit()
            conn.close()
            print("Cache database initialized successfully")
        except Exception as e:
            print(f"Error setting up cache database: {e}")
    
    def get_from_cache(self, word: str, language_code: str = 'la') -> Optional[WordInfo]:
        """Get word from local cache"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT word, latin, definition, etymology, part_of_speech, 
                       morphology, pronunciation, source, confidence, theological_interpretation 
                FROM word_cache 
                WHERE word = ? AND language_code = ?
            ''', (word, language_code))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"Cache HIT for '{word}' in {language_code} - using cached result")
                return WordInfo(
                    latin=result[1],
                    definition=result[2],
                    etymology=result[3],
                    part_of_speech=result[4],
                    morphology=result[5],
                    pronunciation=result[6],
                    source=result[7],
                    confidence=result[8],
                    theological_interpretation=result[9] or ""
                )
            else:
                print(f"Cache MISS for '{word}' in {language_code} - will lookup and cache")
            return None
        except Exception as e:
            print(f"Cache lookup error for '{word}': {e}")
            return None
    
    def save_to_cache(self, word_info: WordInfo, language_code: str = 'la'):
        """Save word to local cache"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO word_cache 
                (word, latin, definition, etymology, part_of_speech, morphology, 
                 pronunciation, source, confidence, theological_interpretation, language_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                word_info.latin,
                word_info.latin,
                word_info.definition or '',
                word_info.etymology or '',
                word_info.part_of_speech or '',
                word_info.morphology or '',
                word_info.pronunciation or '',
                word_info.source or '',
                word_info.confidence or 0.0,
                word_info.theological_interpretation or '',
                language_code
            ))
            conn.commit()
            conn.close()
            print(f"CACHED: '{word_info.latin}' saved to database in {language_code}")
        except Exception as e:
            print(f"Cache save error for '{word_info.latin}': {e}")
    
    def get_verses_for_word(self, word: str, language_code: str = 'la') -> List[Dict[str, Any]]:
        """Get all verses where a word appears"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT verse_reference, verse_text, position 
                FROM word_verse_relationships 
                WHERE word = ? AND language_code = ?
                ORDER BY verse_reference
            ''', (word, language_code))
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "verse_reference": row[0],
                    "verse_text": row[1],
                    "position": row[2]
                }
                for row in results
            ]
        except Exception as e:
            print(f"Error getting verses for word '{word}': {e}")
            return []
    
    def add_word_verse_relationship(self, word: str, verse_reference: str, verse_text: str, position: int = 0, language_code: str = 'la'):
        """Add a word-verse relationship to track where words appear"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO word_verse_relationships 
                (word, verse_reference, verse_text, position, language_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (word, verse_reference, verse_text, position, language_code))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error adding word-verse relationship for '{word}' in {verse_reference}: {e}")
    
    def get_verse_analysis_from_cache(self, verse_reference: str, language_code: str = 'la') -> Optional[Dict[str, Any]]:
        """Get complete verse analysis from cache"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT verse_text, word_analysis_json, translations_json, 
                       theological_layer_json, jungian_layer_json, cosmological_layer_json
                FROM verse_analysis_cache 
                WHERE verse_reference = ? AND language_code = ?
            ''', (verse_reference, language_code))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "success": True,
                    "verse_text": result[0],
                    "word_analysis": json.loads(result[1]) if result[1] else [],
                    "translations": json.loads(result[2]) if result[2] else {},
                    "theological_layer": json.loads(result[3]) if result[3] else [],
                    "symbolic_layer": json.loads(result[4]) if result[4] else [],
                    "cosmological_layer": json.loads(result[5]) if result[5] else [],
                    "source": "cache"
                }
            return None
        except Exception as e:
            print(f"Error getting verse analysis from cache: {e}")
            return None
    
    def save_verse_analysis_to_cache(self, verse_reference: str, verse_text: str, analysis_data: Dict[str, Any], language_code: str = 'la'):
        """Save complete verse analysis to cache"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            word_analysis_json = json.dumps(analysis_data.get("word_analysis", []))
            translations_json = json.dumps(analysis_data.get("translations", {}))
            theological_json = json.dumps(analysis_data.get("theological_layer", []))
            jungian_json = json.dumps(analysis_data.get("symbolic_layer", []))
            cosmological_json = json.dumps(analysis_data.get("cosmological_layer", []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO verse_analysis_cache 
                (verse_reference, language_code, verse_text, word_analysis_json, translations_json, 
                 theological_layer_json, jungian_layer_json, cosmological_layer_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (verse_reference, language_code, verse_text, word_analysis_json, translations_json, 
                  theological_json, jungian_json, cosmological_json))
            
            conn.commit()
            conn.close()
            print(f"Verse analysis cached for {verse_reference}")
        except Exception as e:
            print(f"Error saving verse analysis to cache: {e}")
    
    def analyze_verse(self, verse_text: str, verse_reference: str = "", language_code: str = 'la') -> Dict[str, Any]:
        """Analyze a verse with caching and language support"""
        # Check cache first
        if verse_reference:
            cached_analysis = self.get_verse_analysis_from_cache(verse_reference, language_code)
            if cached_analysis:
                print(f"Using cached verse analysis for {verse_reference}")
                return cached_analysis
        
        # If no cached analysis, provide basic word analysis
        print(f"No cached analysis for {verse_reference}, providing basic word analysis")
        words = verse_text.split()
        word_analysis = []
        
        for i, word in enumerate(words):
            # Clean the word (remove punctuation)
            clean_word = word.strip('.,;:!?()[]"\'')
            if clean_word:
                word_info = self.lookup_word(clean_word, language_code)
                word_analysis.append({
                    "latin": word_info.latin,
                    "definition": word_info.definition,
                    "etymology": word_info.etymology,
                    "part_of_speech": word_info.part_of_speech,
                    "morphology": word_info.morphology,
                    "pronunciation": word_info.pronunciation,
                    "source": word_info.source,
                    "confidence": word_info.confidence
                })
                
                # Track word-verse relationship
                if verse_reference:
                    self.add_word_verse_relationship(clean_word, verse_reference, verse_text, i, language_code)
        
        return {
            "success": True,
            "word_analysis": word_analysis,
            "translations": {},
            "theological_layer": [],
            "symbolic_layer": [],
            "cosmological_layer": [],
            "source": "basic_analysis"
        }
    
    def lookup_word(self, word: str, language_code: str = 'la') -> WordInfo:
        """Lookup a word with fallback to basic response"""
        # First check cache
        cached = self.get_from_cache(word, language_code)
        if cached:
            return cached
        
        # If not in cache, return basic response
        basic_info = WordInfo(
            latin=word,
            definition=f"Definition for {word} not found",
            etymology="",
            part_of_speech="unknown",
            source="not_found",
            confidence=0.0
        )
        
        # Cache the basic response to avoid repeated lookups
        self.save_to_cache(basic_info, language_code)
        return basic_info
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about cached words"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Count total cached words
            cursor.execute('SELECT COUNT(*) FROM word_cache')
            total_cached = cursor.fetchone()[0]
            
            # Count by source
            cursor.execute('SELECT source, COUNT(*) FROM word_cache GROUP BY source')
            source_breakdown = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_cached': total_cached,
                'cache_file': self.database_path,
                'source_breakdown': source_breakdown
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {
                'total_cached': 0,
                'cache_file': self.database_path,
                'source_breakdown': {}
            }
    
    def clear_word_cache(self, word: str, language_code: str = 'la') -> bool:
        """Clear a specific word from cache"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM word_cache WHERE word = ? AND language_code = ?', (word, language_code))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            return rows_affected > 0
        except Exception as e:
            print(f"Error clearing word cache for '{word}': {e}")
            return False
    
    def get_words_for_verse(self, verse_reference: str, language_code: str = 'la') -> List[str]:
        """Get all words tracked for a specific verse"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT word 
                FROM word_verse_relationships 
                WHERE verse_reference = ? AND language_code = ?
                ORDER BY position
            ''', (verse_reference, language_code))
            words = [row[0] for row in cursor.fetchall()]
            conn.close()
            return words
        except Exception as e:
            print(f"Error getting words for verse '{verse_reference}': {e}")
            return []
    
    def query_openai_with_context(self, word: str, verse: str, language_code: str = 'la') -> WordInfo:
        """Query OpenAI with verse context for enhanced word analysis"""
        if not self.openai_enabled or not self.openai_client:
            return self.lookup_word(word, language_code)
        
        try:
            prompt = f"""
            Analyze the Latin word "{word}" in the context of this Vulgate verse: "{verse}"
            
            Please provide:
            1. The lemma (dictionary form)
            2. Detailed definition in context
            3. Part of speech
            4. Morphological analysis (case, number, gender, tense, mood, etc.)
            5. Etymology if notable
            6. Theological or biblical significance if applicable
            
            Respond in JSON format:
            {{
                "latin": "lemma form",
                "definition": "detailed definition",
                "part_of_speech": "noun/verb/adjective/etc",
                "morphology": "detailed morphological analysis",
                "etymology": "etymology if notable",
                "theological_interpretation": "theological significance if any"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:-3].strip()
            
            result_data = json.loads(result_text)
            
            word_info = WordInfo(
                latin=result_data.get("latin", word),
                definition=result_data.get("definition", ""),
                etymology=result_data.get("etymology", ""),
                part_of_speech=result_data.get("part_of_speech", ""),
                morphology=result_data.get("morphology", ""),
                pronunciation="",
                source="openai_context",
                confidence=0.9,
                theological_interpretation=result_data.get("theological_interpretation", "")
            )
            
            # Cache the result
            self.save_to_cache(word_info, language_code)
            return word_info
            
        except Exception as e:
            print(f"OpenAI context query failed for '{word}': {e}")
            # Fallback to basic lookup
            return self.lookup_word(word, language_code)
    
    def analyze_verse_with_openai(self, verse_text: str, verse_reference: str = "", language_code: str = 'la', target_analysis_language: str = 'en') -> Dict[str, Any]:
        """Perform comprehensive verse analysis using OpenAI with support for multiple analysis languages"""
        if not self.openai_enabled or not self.openai_client:
            return self.analyze_verse(verse_text, verse_reference, language_code)
        
        # Detect source language
        source_language = self.detect_source_language(verse_text)
        
        # Language mapping for analysis output
        analysis_language_names = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "it": "Italian",
            "pt": "Portuguese",
            "de": "German",
            "la": "Latin",
            "sa": "Sanskrit", 
            "hi": "Hindi"
        }
        
        analysis_lang_name = analysis_language_names.get(target_analysis_language, "English")
        source_lang_name = analysis_language_names.get(source_language, source_language)
        
        # Check cache first with language-specific key
        cache_key = f"{verse_reference}_{source_language}_{target_analysis_language}"
        if verse_reference:
            cached_analysis = self.get_verse_analysis_from_cache(cache_key)
            if cached_analysis:
                print(f"Using cached analysis for {verse_reference} in {analysis_lang_name}")
                return cached_analysis
        
        try:
            # Create language-specific prompt
            if source_language == "sanskrit":
                # For Sanskrit (Gita) text
                prompt = f"""
Perform a comprehensive analysis of this Sanskrit verse from the Bhagavad Gita: "{verse_text}"
Reference: {verse_reference}

IMPORTANT: Provide ALL analysis in {analysis_lang_name}. Do not use English unless specifically requested.

Please provide:
1. Word-by-word analysis with Sanskrit word, transliteration, definition, and grammatical analysis
2. Philosophical interpretation focusing on Vedantic philosophy and Hindu tradition
3. Symbolic analysis combining:
   - Jungian archetypal symbols (Anima/Animus, Shadow, Self, Mother, Father, Hero, etc.)
   - Joseph Campbell's Hero's Journey stages and mythological patterns
   - Cross-cultural mythological parallels
   - Collective unconscious themes and individuation process elements
4. Cosmological interpretation relating to dharma, karma, and cosmic order

Respond in JSON format with ALL text in {analysis_lang_name}:
{{
    "word_analysis": [
        {{
            "sanskrit": "sanskrit word",
            "transliteration": "romanized form", 
            "definition": "definition in {analysis_lang_name}",
            "part_of_speech": "part of speech in {analysis_lang_name}",
            "morphology": "grammatical analysis in {analysis_lang_name}"
        }}
    ],
    "philosophical_layer": ["philosophical insight 1 in {analysis_lang_name}", "philosophical insight 2 in {analysis_lang_name}"],
    "symbolic_layer": ["jungian archetypal insight 1 in {analysis_lang_name}", "campbell mythological insight 2 in {analysis_lang_name}"],
    "cosmological_layer": ["cosmological insight 1 in {analysis_lang_name}", "cosmological insight 2 in {analysis_lang_name}"]
}}
"""
            else:
                # For Latin (Bible) text
                prompt = f"""
Perform a comprehensive analysis of this Vulgate Latin verse: "{verse_text}"
Reference: {verse_reference}

IMPORTANT: Provide ALL analysis in {analysis_lang_name}. Do not use English unless specifically requested.

Please provide:
1. Word-by-word analysis with lemma, definition, part of speech, and morphology
2. Theological interpretation focusing on Catholic doctrine and tradition
3. Symbolic analysis combining:
   - Jungian archetypal symbols (Anima/Animus, Shadow, Self, Mother, Father, Hero, etc.)
   - Joseph Campbell's Hero's Journey stages and mythological patterns
   - Cross-cultural mythological parallels
   - Collective unconscious themes and individuation process elements
4. Cosmological interpretation relating to creation, divine order, and sacred geometry

Respond in JSON format with ALL text in {analysis_lang_name}:
{{
    "word_analysis": [
        {{
            "latin": "word lemma",
            "definition": "definition in {analysis_lang_name}",
            "part_of_speech": "part of speech in {analysis_lang_name}",
            "morphology": "morphological analysis in {analysis_lang_name}"
        }}
    ],
    "theological_layer": ["theological insight 1 in {analysis_lang_name}", "theological insight 2 in {analysis_lang_name}"],
    "symbolic_layer": ["jungian archetypal insight 1 in {analysis_lang_name}", "campbell mythological insight 2 in {analysis_lang_name}"],
    "cosmological_layer": ["cosmological insight 1 in {analysis_lang_name}", "cosmological insight 2 in {analysis_lang_name}"]
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": f"You are a multilingual scholar specializing in religious texts. Always provide analysis in {analysis_lang_name} as requested, never default to English unless specifically asked."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2500
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:-3].strip()
            
            analysis_data = json.loads(result_text)
            
            # Prepare result with appropriate layer names
            layer_names = {
                "sanskrit": ["philosophical_layer", "symbolic_layer", "cosmological_layer"],
                "latin": ["theological_layer", "symbolic_layer", "cosmological_layer"]
            }
            
            layers = layer_names.get(source_language, ["theological_layer", "symbolic_layer", "cosmological_layer"])
            
            # Save to cache with language-specific key
            full_result = {
                "success": True,
                "word_analysis": analysis_data.get("word_analysis", []),
                "translations": {},  # Will be filled by separate translation method
                layers[0]: analysis_data.get(layers[0], analysis_data.get("theological_layer", [])),
                "symbolic_layer": analysis_data.get("symbolic_layer", []),
                "cosmological_layer": analysis_data.get("cosmological_layer", []),
                "source": f"openai_analysis_{target_analysis_language}",
                "analysis_language": target_analysis_language,
                "source_language": source_language
            }
            
            if verse_reference:
                self.save_verse_analysis_to_cache(cache_key, verse_text, full_result, language_code)
                
                # Track word-verse relationships
                for i, word_data in enumerate(analysis_data.get("word_analysis", [])):
                    word_key = "sanskrit" if source_language == "sanskrit" else "latin"
                    if word_key in word_data:
                        self.add_word_verse_relationship(
                            word_data[word_key], verse_reference, verse_text, i, language_code
                        )
            
            return full_result
            
        except Exception as e:
            print(f"OpenAI verse analysis failed for '{verse_reference}' in {analysis_lang_name}: {e}")
            # Fallback to basic analysis
            return self.analyze_verse(verse_text, verse_reference, language_code)
    
    def translate_verse(self, verse_text: str, target_language: str = "en") -> str:
        """Translate verse to target language using OpenAI with proper source language detection"""
        if not self.openai_enabled or not self.openai_client:
            return f"Translation to {target_language} not available (OpenAI not enabled)"
        
        # Detect source language based on text content
        source_language = self.detect_source_language(verse_text)
        
        # Language mapping with expanded options
        language_names = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "it": "Italian",
            "pt": "Portuguese",
            "de": "German",
            "la": "Latin",
            "sa": "Sanskrit", 
            "hi": "Hindi"
        }
        
        target_lang_name = language_names.get(target_language, target_language)
        source_lang_name = language_names.get(source_language, source_language)
        
        # Create appropriate prompt based on source language
        if source_language == "sanskrit":
            # For Sanskrit (Gita) text
            prompt = f"""
Translate this Sanskrit verse to {target_lang_name}.

Sanskrit: {verse_text}

Provide two translations:
1. Literal: word-for-word translation
2. Dynamic: natural, flowing translation

Return ONLY valid JSON (no explanations):
{{
    "literal": "literal {target_lang_name} translation",
    "dynamic": "natural {target_lang_name} translation", 
    "source_language": "sanskrit"
}}
"""
        else:
            # For Latin (Bible) text
            prompt = f"""
Translate this Latin verse to {target_lang_name}.

Latin: {verse_text}

Provide two translations:
1. Literal: word-for-word translation  
2. Dynamic: natural, flowing translation

Return ONLY valid JSON (no explanations):
{{
    "literal": "literal {target_lang_name} translation",
    "dynamic": "natural {target_lang_name} translation",
    "source_language": "latin"
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a precise translator. Return ONLY valid JSON with translations in {target_lang_name}. No explanations, no extra text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            translation_text = response.choices[0].message.content.strip()
            
            # Validate that we got a proper JSON response
            try:
                translation_json = json.loads(translation_text)
                # Ensure we have the required fields
                if "literal" not in translation_json or "dynamic" not in translation_json:
                    raise ValueError("Missing required translation fields")
                return translation_text
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, create a proper JSON response
                return json.dumps({
                    "literal": translation_text,
                    "dynamic": translation_text,
                    "source_language": source_language,
                    "full_response": translation_text
                })
                
        except Exception as e:
            error_msg = f"Translation to {target_language} failed: {str(e)}"
            print(f"OpenAI translation error: {e}")
            return json.dumps({
                "literal": error_msg,
                "dynamic": error_msg,
                "source_language": source_language,
                "error": str(e)
            })

    def detect_source_language(self, text: str) -> str:
        """Detect if the source text is Sanskrit or Latin"""
        # Check for Devanagari script (Sanskrit)
        devanagari_chars = any('\u0900' <= char <= '\u097F' for char in text)
        
        # Check for Sanskrit-specific indicators (both Devanagari and transliteration)
        sanskrit_indicators = [
            'संस्कृत', 'Sanskrit', 'श्लोक', 'अध्याय', 'भगवद्गीता',
            'लिप्यन्तरण', 'Transliteration', '।।', 'उवाच', 'uvācha'
        ]
        
        # Check for Sanskrit transliteration patterns (common Sanskrit words/endings)
        sanskrit_transliteration_patterns = [
            'uvācha', 'arjunaḥ', 'kṛiṣhṇa', 'bhagavān', 'dharma', 'karma', 'yoga',
            'saṅkhye', 'rathopastha', 'upāviśhat', 'visṛijya', 'chāpaṁ', 'mānasaḥ',
            'sañjaya', 'dhṛitarāṣhṭra', 'pāṇḍava', 'kaurava', 'kurukṣhetra',
            'śhaṅkha', 'dadhmau', 'bhīma', 'vṛikodara', 'dhanañjaya', 'hṛiṣhīkeśha',
            'ṁ', 'ḥ', 'ṛi', 'ṣh', 'ñ', 'ā', 'ī', 'ū', 'ē', 'ō'  # Sanskrit diacritical marks
        ]
        
        has_sanskrit_indicators = any(indicator in text for indicator in sanskrit_indicators)
        has_sanskrit_transliteration = any(pattern in text for pattern in sanskrit_transliteration_patterns)
        
        # Also check for multiple Sanskrit diacritical marks (strong indicator of Sanskrit transliteration)
        diacritical_count = sum(1 for char in text if char in 'ṁḥṛiṣhñāīūēō')
        has_many_diacriticals = diacritical_count >= 3
        
        if devanagari_chars or has_sanskrit_indicators or has_sanskrit_transliteration or has_many_diacriticals:
            return "sanskrit"
        else:
            return "latin"

    def analyze_grammatical_relationships(self, sentence: str, verse_reference: str = "") -> Dict[str, Any]:
        """Analyze grammatical relationships between words in a Latin sentence"""
        if not self.openai_enabled or not self.openai_client:
            return {"success": False, "error": "OpenAI not enabled"}
        
        try:
            prompt = f"""
            Perform detailed morphosyntactic analysis of this Latin sentence: "{sentence}"
            Reference: {verse_reference if verse_reference else "Unknown"}
            
            For each word, provide:
            1. Complete morphological analysis (case, number, gender, tense, mood, voice, person, declension/conjugation)
            2. Grammatical function and relationships to other words
            3. Detailed explanation of WHY the word has that specific ending
            4. Subject-verb agreement analysis
            5. Case usage explanations
            
            Return a JSON response with:
            {{
                "words": [
                    {{
                        "word": "word as it appears",
                        "lemma": "dictionary form",
                        "position": 0,
                        "part_of_speech": "noun/verb/adjective/etc",
                        "morphology": {{
                            "case": "nominative/accusative/etc (for nouns/adjectives)",
                            "number": "singular/plural",
                            "gender": "masculine/feminine/neuter (for nouns/adjectives)",
                            "tense": "present/perfect/etc (for verbs)",
                            "mood": "indicative/subjunctive/etc (for verbs)",
                            "voice": "active/passive (for verbs)",
                            "person": "1st/2nd/3rd (for verbs)",
                            "declension": "1st/2nd/3rd/etc (for nouns)",
                            "conjugation": "1st/2nd/3rd/4th (for verbs)"
                        }},
                        "grammatical_function": "subject/direct_object/predicate/etc",
                        "ending_explanation": "Detailed explanation of why this word has this specific ending",
                        "relationships": [
                            {{
                                "type": "subject_of|object_of|modifies|governed_by|agrees_with|etc",
                                "target_word": "related word",
                                "target_position": 1,
                                "description": "detailed explanation of the relationship and agreement"
                            }}
                        ]
                    }}
                ],
                "sentence_structure": {{
                    "main_verb": {{
                        "word": "verb form",
                        "person": "1st/2nd/3rd",
                        "number": "singular/plural",
                        "subject": "subject that agrees with this verb"
                    }},
                    "subject": {{
                        "word": "subject",
                        "case": "nominative",
                        "agrees_with_verb": "explanation of subject-verb agreement"
                    }},
                    "objects": [
                        {{
                            "word": "object",
                            "case": "accusative/dative/etc",
                            "function": "direct_object/indirect_object/etc"
                        }}
                    ],
                    "prepositional_phrases": [
                        {{
                            "phrase": "full phrase",
                            "preposition": "preposition",
                            "object": "object of preposition",
                            "case_required": "case required by preposition",
                            "function": "temporal/locative/etc modifier"
                        }}
                    ]
                }},
                "morphological_summary": "Overall explanation of how the grammatical endings work together in this sentence"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a Latin morphosyntax expert specializing in detailed grammatical analysis. You excel at explaining WHY each Latin word has its specific ending, including declensions, conjugations, case usage, and subject-verb agreement. Provide comprehensive morphological breakdowns and clear explanations of grammatical relationships."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith('```'):
                result_text = result_text[3:-3].strip()
            
            analysis_data = json.loads(result_text)
            
            return {
                "success": True,
                "sentence": sentence,
                "verse_reference": verse_reference,
                "words": analysis_data.get("words", []),
                "sentence_structure": analysis_data.get("sentence_structure", {}),
                "morphological_summary": analysis_data.get("morphological_summary", ""),
                "source": "openai_grammar_analysis"
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error in grammatical analysis: {e}")
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            print(f"Grammatical analysis failed for '{sentence}': {e}")
            return {"success": False, "error": str(e)}

    def save_translation_to_cache(self, cache_key: str, translation_data: Dict[str, Any]) -> None:
        """Save translation data to cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Create translation cache table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translation_cache (
                    cache_key TEXT PRIMARY KEY,
                    translation_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Save translation data as JSON
            cursor.execute('''
                INSERT OR REPLACE INTO translation_cache (cache_key, translation_data)
                VALUES (?, ?)
            ''', (cache_key, json.dumps(translation_data)))
            
            conn.commit()
            conn.close()
            print(f"Translation cached with key: {cache_key}")
            
        except Exception as e:
            print(f"Failed to save translation to cache: {e}")

    def get_translation_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get translation data from cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT translation_data FROM translation_cache 
                WHERE cache_key = ?
            ''', (cache_key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            print(f"Failed to get translation from cache: {e}")
            return None 