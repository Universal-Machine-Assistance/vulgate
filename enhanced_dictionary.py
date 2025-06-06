#!/usr/bin/env python3
"""
Enhanced Dictionary with Latin Morphological Analysis and Greb AI Integration

This system provides intelligent Latin word lookup with:
1. Morphological analysis (recognizing conjugations/declensions)
2. Greb AI integration for missing words
3. Local caching to avoid repeated API calls
"""

import json
import os
import re
import unicodedata
import time
import random
from typing import Dict, Any, Optional, List, Tuple
import openai
from dataclasses import dataclass
import sqlite3
from datetime import datetime

# Rate limiting globals
last_openai_call = 0
min_time_between_calls = 1.2  # Minimum 1.2 seconds between OpenAI API calls

def rate_limit_openai():
    """Rate limit OpenAI API calls to avoid 429 errors"""
    global last_openai_call
    now = time.time()
    time_since_last = now - last_openai_call
    
    if time_since_last < min_time_between_calls:
        sleep_time = min_time_between_calls - time_since_last
        time.sleep(sleep_time)
    
    last_openai_call = time.time()

def exponential_backoff_retry(func, max_retries=3, base_delay=1.0):
    """Retry function with exponential backoff for rate limit errors"""
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:  # Add extra delay for retries
                rate_limit_openai()
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for rate limit or quota errors
            if any(term in error_msg for term in ["rate limit", "429", "quota", "too many requests"]):
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Add jitter
                    print(f"Rate limit hit on attempt {attempt + 1}/{max_retries + 1}, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"Max retries ({max_retries}) exceeded for rate limit")
                    raise Exception(f"API quota exceeded after {max_retries} retries. Please try again later.")
            
            # For non-rate-limit errors, don't retry
            raise e
    
    return None

def normalize_latin_word(word: str) -> str:
    """Normalize Latin word by removing accents and converting to lowercase"""
    # Handle common Latin ligatures and characters first
    word = word.lower()
    word = word.replace('æ', 'ae')  # æ ligature -> ae
    word = word.replace('œ', 'oe')  # œ ligature -> oe  
    word = word.replace('ſ', 's')   # long s -> s
    
    # Then normalize Unicode and remove diacritics
    normalized = unicodedata.normalize('NFD', word)
    ascii_word = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ascii_word.strip()

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

class LatinMorphologyAnalyzer:
    """Analyzes Latin word forms to find root words"""
    
    def __init__(self):
        # Common Latin verb endings and their information
        self.verb_endings = {
            # Present tense
            'o': ('1st person singular present', ['are', 'ere', 'ire']),
            'as': ('2nd person singular present', ['are']),
            'at': ('3rd person singular present', ['are', 'ere', 'ire']),
            'amus': ('1st person plural present', ['are', 'ere', 'ire']),
            'atis': ('2nd person plural present', ['are', 'ere', 'ire']),
            'ant': ('3rd person plural present', ['are', 'ere', 'ire']),
            
            # Perfect participles
            'us': ('perfect participle masculine singular', ['us', 'a', 'um']),
            'a': ('perfect participle feminine singular', ['us', 'a', 'um']),
            'um': ('perfect participle neuter singular', ['us', 'a', 'um']),
            'i': ('perfect participle masculine plural', ['us', 'a', 'um']),
            'ae': ('perfect participle feminine plural', ['us', 'a', 'um']),
            'ta': ('perfect participle neuter plural from -tus ending', ['tus', 'ta', 'tum']),
            'ata': ('perfect participle neuter plural from -atus ending', ['atus', 'ata', 'atum']),
        }
        
        # Common noun endings with better coverage
        self.noun_endings = {
            # 1st declension
            'a': ('nominative/ablative singular feminine 1st declension', 'a'),
            'ae': ('genitive/dative singular OR nominative plural 1st declension', 'a'),
            'am': ('accusative singular feminine 1st declension', 'a'),
            'arum': ('genitive plural 1st declension', 'a'),
            'is': ('dative/ablative plural 1st declension', 'a'),
            
            # 2nd declension
            'us': ('nominative singular masculine 2nd declension', 'us'),
            'i': ('genitive singular OR nominative plural 2nd declension', 'us'),
            'um': ('accusative singular OR nominative/accusative neuter 2nd declension', 'us'),
            'o': ('dative/ablative singular 2nd declension', 'us'),
            'orum': ('genitive plural 2nd declension', 'us'),
            'os': ('accusative plural masculine 2nd declension', 'us'),
            
            # Special cases for -ium words (like principium)
            'io': ('dative/ablative singular of -ium noun', 'ium'),
            'ii': ('genitive singular of -ium noun', 'ium'),
            'ium': ('genitive plural of -ium noun', 'ium'),
            
            # 3rd declension
            'is': ('genitive singular 3rd declension', ''),
            'em': ('accusative singular masculine/feminine 3rd declension', ''),
            'e': ('ablative singular 3rd declension', ''),
            'es': ('nominative/accusative plural 3rd declension', ''),
            'ibus': ('dative/ablative plural 3rd declension', ''),
        }
        
        # Special morphological rules for known patterns
        self.special_patterns = {
            # -io ending often comes from -ium nouns (like principium)
            'io': [
                ('ium', 'dative/ablative singular of -ium noun'),
            ],
            # -ii ending comes from -ius or -ium nouns  
            'ii': [
                ('ius', 'genitive singular of -ius noun'),
                ('ium', 'genitive singular of -ium noun'),
            ]
        }
    
    def analyze_word(self, word: str) -> List[Tuple[str, str]]:
        """
        Analyze a Latin word and return possible root forms with morphological info
        Returns list of (root_word, morphology_description) tuples
        """
        word = word.lower().strip()
        candidates = []
        
        # Check special patterns first (like principio -> principium)
        for pattern, transformations in self.special_patterns.items():
            if word.endswith(pattern):
                stem = word[:-len(pattern)]
                for suffix, description in transformations:
                    root_candidate = stem + suffix
                    candidates.append((root_candidate, f"{description} (from {root_candidate})"))
        
        # Try to find verb forms
        for ending, (description, infinitive_endings) in self.verb_endings.items():
            if word.endswith(ending) and len(word) > len(ending):
                stem = word[:-len(ending)]
                
                # Try different infinitive endings
                for inf_ending in infinitive_endings:
                    root_candidates = [
                        stem + inf_ending,  # facere
                        stem + 'ere',       # generic -ere
                        stem + 'are',       # generic -are
                        stem + 'ire',       # generic -ire
                        stem,               # just the stem
                        stem + 'io',        # 1st person like facio
                    ]
                    
                    for candidate in root_candidates:
                        candidates.append((candidate, f"{description} (from {candidate})"))
        
        # Try to find noun forms  
        for ending, (description, nom_ending) in self.noun_endings.items():
            if word.endswith(ending) and len(word) > len(ending):
                stem = word[:-len(ending)]
                if nom_ending:  # Only if we have a clear nominative ending
                    root_word = stem + nom_ending
                    candidates.append((root_word, f"{description} (nominative: {root_word})"))
        
        # Special case for -ta endings (like facta)
        if word.endswith('ta'):
            stem = word[:-2]
            candidates.extend([
                (stem + 'tus', 'neuter plural perfect participle (masculine singular: ' + stem + 'tus)'),
                (stem + 'tum', 'neuter plural perfect participle (neuter singular: ' + stem + 'tum)'),
                (stem + 'ere', 'neuter plural perfect participle (infinitive: ' + stem + 'ere)'),
                (stem + 'o', 'neuter plural perfect participle (1st person: ' + stem + 'o)'),
            ])
        
        # Add the original word as a candidate
        candidates.append((word, 'original form'))
        
        return candidates

class EnhancedDictionary:
    """Enhanced dictionary with morphological analysis and OpenAI integration"""
    
    def __init__(self, dictionary_path: str = "frontend/public/dictionary.json", 
                 openai_api_key: str = None, cache_db: str = "word_cache.db"):
        self.dictionary_path = dictionary_path
        self.cache_db = cache_db
        self.analyzer = LatinMorphologyAnalyzer()
        
        # Print paths for debugging
        print(f"Dictionary path: {os.path.abspath(self.dictionary_path)}")
        print(f"Cache DB path: {os.path.abspath(self.cache_db)}")
        print(f"Project root: {os.getcwd()}")
        
        self.dictionary = self.load_dictionary()
        
        # Set up OpenAI
        if openai_api_key:
            # Use the new OpenAI client for v1.0.0+
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            self.openai_enabled = True
        else:
            self.openai_enabled = False
            print("Greb AI API key not provided. Greb AI fallback disabled.")
        
        # Set up local cache database
        self.setup_cache_db()
    
    def load_dictionary(self) -> Dict[str, Any]:
        """Load the main dictionary"""
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return {}
    
    def setup_cache_db(self):
        """Set up the local cache database"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            # Create word cache table
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create verse analysis cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verse_analysis_cache (
                    verse_reference TEXT PRIMARY KEY,
                    verse_text TEXT,
                    word_analysis_json TEXT,
                    translations_json TEXT,
                    theological_layer_json TEXT,
                    jungian_layer_json TEXT,
                    cosmological_layer_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Cache database initialized successfully")
        except Exception as e:
            print(f"Error setting up cache database: {e}")
    
    def get_from_cache(self, word: str) -> Optional[WordInfo]:
        """Get word from local cache"""
        try:
            normalized_word = normalize_latin_word(word)
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM word_cache WHERE word = ?', (normalized_word,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"Cache HIT for '{word}' (normalized: '{normalized_word}') - using cached result")
                return WordInfo(
                    latin=result[0],
                    definition=result[1],
                    etymology=result[2],
                    part_of_speech=result[3],
                    morphology=result[4],
                    pronunciation=result[5],
                    source=result[6],
                    confidence=result[7]
                )
            else:
                print(f"Cache MISS for '{word}' (normalized: '{normalized_word}') - will lookup and cache")
            return None
        except Exception as e:
            print(f"Cache lookup error for '{word}': {e}")
            return None
    
    def save_to_cache(self, word_info: WordInfo):
        """Save word to local cache"""
        try:
            normalized_word = normalize_latin_word(word_info.latin)
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO word_cache 
                (word, latin, definition, etymology, part_of_speech, morphology, pronunciation, source, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                normalized_word,
                word_info.latin,
                word_info.definition or '',
                word_info.etymology or '',
                word_info.part_of_speech or '',
                word_info.morphology or '',
                word_info.pronunciation or '',
                word_info.source or '',
                word_info.confidence or 0.0
            ))
            conn.commit()
            conn.close()
            print(f"CACHED: '{word_info.latin}' (normalized: '{normalized_word}') saved to database (source: {word_info.source})")
        except Exception as e:
            print(f"Cache save error for '{word_info.latin}': {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            # Count total cached words
            cursor.execute('SELECT COUNT(*) FROM word_cache')
            total_cached = cursor.fetchone()[0]
            
            # Count by source
            cursor.execute('SELECT source, COUNT(*) FROM word_cache GROUP BY source')
            source_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_cached': total_cached,
                'source_breakdown': source_counts,
                'cache_file': os.path.abspath(self.cache_db)
            }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'total_cached': 0, 'source_breakdown': {}, 'cache_file': 'error'}
    
    def clear_word_cache(self, word: str) -> bool:
        """Clear a specific word from cache to force regeneration"""
        normalized_word = normalize_latin_word(word)
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM word_cache WHERE word = ?', (normalized_word,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    
    def query_openai(self, word: str) -> Optional[WordInfo]:
        """Query Greb AI for word definition with rate limiting and retry logic"""
        if not self.openai_enabled:
            return None
        
        def make_openai_call():
            rate_limit_openai()  # Rate limit before each call
            
            prompt = f"""
            Analyze the word "{word}" as a potential Latin word:
            
            IMPORTANT: First determine if this is actually a Latin word or if it's from a Romance language (Spanish, Portuguese, Italian, French, etc.).
            
            If it's NOT a Latin word, respond with:
            {{
                "is_latin": false,
                "actual_language": "language name",
                "definition": "This appears to be a [language] word, not Latin. In [language] it means: [meaning]",
                "etymology": "Romance language etymology if available",
                "part_of_speech": "unknown",
                "morphology": "Not applicable - not a Latin word",
                "pronunciation": ""
            }}
            
            If it IS a Latin word, provide:
            {{
                "is_latin": true,
                "definition": "detailed Latin definition here",
                "etymology": "Latin etymology information here",
                "part_of_speech": "noun, verb, adjective, etc.",
                "morphology": "morphological analysis here",
                "pronunciation": "pronunciation guide here"
            }}
            
            If this is an inflected Latin form, identify the root form and provide analysis.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Latin language expert who can distinguish between Latin and Romance languages. Be precise about whether a word is actually Latin or from a modern Romance language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            return response

        try:
            response = exponential_backoff_retry(make_openai_call, max_retries=2, base_delay=2.0)
            if not response:
                return None
                
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                data = json.loads(content)
                
                # Check if the word is actually Latin
                if not data.get('is_latin', True):
                    # It's not Latin - mark it clearly
                    actual_lang = data.get('actual_language', 'unknown')
                    word_info = WordInfo(
                        latin=word,
                        definition=f"NOT LATIN: {data.get('definition', f'This appears to be a {actual_lang} word, not Latin.')}",
                        etymology=data.get('etymology', f'This is from {actual_lang}, not Latin'),
                        part_of_speech="non-latin",
                        morphology=f"Not applicable - this is {actual_lang}, not Latin",
                        pronunciation=data.get('pronunciation', ''),
                        source="greb",
                        confidence=0.9  # High confidence it's NOT Latin
                    )
                else:
                    # It is Latin
                    word_info = WordInfo(
                        latin=word,
                        definition=data.get('definition', 'Definition provided by Greb AI'),
                        etymology=data.get('etymology', 'Etymology provided by Greb AI'),
                        part_of_speech=data.get('part_of_speech', 'unknown'),
                        morphology=data.get('morphology', 'Analysis provided by Greb AI'),
                        pronunciation=data.get('pronunciation', ''),
                        source="greb",
                        confidence=0.8
                    )
                
                # Cache the result
                self.save_to_cache(word_info)
                return word_info
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                word_info = WordInfo(
                    latin=word,
                    definition=content[:200] if content else "Greb AI analysis available",
                    etymology="Provided by Greb AI",
                    part_of_speech="unknown",
                    morphology="Analysis provided by Greb AI",
                    pronunciation="",
                    source="greb",
                    confidence=0.6
                )
                self.save_to_cache(word_info)
                return word_info
                
        except Exception as e:
            print(f"Greb AI query failed: {e}")
            return None
    
    def lookup_word(self, word: str) -> WordInfo:
        """
        Enhanced word lookup with morphological analysis and AI fallback
        """
        original_word = word
        word = normalize_latin_word(word)  # Normalize for consistent caching
        
        # 1. Check cache first
        cached = self.get_from_cache(original_word)  # Pass original for better logs
        if cached:
            return cached
        
        # 2. Direct dictionary lookup (try both normalized and original)
        dict_entry = None
        if word in self.dictionary:
            dict_entry = self.dictionary[word]
        elif original_word.lower() in self.dictionary:
            dict_entry = self.dictionary[original_word.lower()]
        
        if dict_entry:
            word_info = WordInfo(
                latin=dict_entry['latin'],
                definition=dict_entry['definition'],
                etymology=dict_entry['etymology'],
                part_of_speech=dict_entry['partOfSpeech'],
                morphology=dict_entry.get('morphology', 'Analysis not available'),
                pronunciation=dict_entry.get('pronunciation', ''),
                source="dictionary"
            )
            # Cache dictionary hits too!
            self.save_to_cache(word_info)
            return word_info
        
        # 3. Morphological analysis - try to find root forms
        candidates = self.analyzer.analyze_word(word)
        
        for candidate_word, morphology_desc in candidates:
            if candidate_word in self.dictionary:
                entry = self.dictionary[candidate_word]
                word_info = WordInfo(
                    latin=original_word,  # Keep original word for display
                    definition=f"[{candidate_word}] {entry['definition']}",
                    etymology=entry['etymology'],
                    part_of_speech=entry['partOfSpeech'],
                    morphology=f"{morphology_desc} | {entry.get('morphology', 'Analysis not available')}",
                    pronunciation=entry.get('pronunciation', ''),
                    source="morphological_analysis",
                    confidence=0.9
                )
                
                # Cache this result
                self.save_to_cache(word_info)
                return word_info
        
        # 4. Greb AI fallback
        ai_result = self.query_openai(original_word)  # Use original for AI query
        if ai_result:
            return ai_result
        
        # 5. Return "not found" result and cache it to prevent repeated lookups
        not_found = WordInfo(
            latin=original_word,
            definition="Definition not available",
            etymology="Etymology not available",
            part_of_speech="unknown",
            morphology="Analysis not available",
            source="not_found"
        )
        
        # Cache not_found results too to prevent repeated API calls
        self.save_to_cache(not_found)
        return not_found

    def analyze_verse(self, verse_text: str, verse_reference: str = "") -> Dict[str, Any]:
        """
        Analyze a complete verse with word-by-word translations and interpretive layers
        """
        if not self.openai_enabled:
            return {
                "success": False,
                "error": "Greb AI not enabled"
            }
        
        # Check cache first
        if verse_reference:
            cached_analysis = self.get_verse_analysis_from_cache(verse_reference)
            if cached_analysis:
                print(f"Using cached verse analysis for {verse_reference}")
                return cached_analysis
        
        # Clean up the verse text
        words = [word.strip('.,;:!?"()[]') for word in verse_text.split() if word.strip()]
        
        def make_verse_analysis_call():
            rate_limit_openai()  # Rate limit before call
            
            prompt = f"""Analyze this Latin Vulgate verse with comprehensive interpretive layers:

Verse: "{verse_text}"
Reference: {verse_reference if verse_reference else "Unknown"}

Provide a detailed JSON response with:

1. WORD_ANALYSIS: For each word, provide:
   - latin: the exact word as it appears
   - definition: clear English definition
   - etymology: word origin and development
   - part_of_speech: grammatical category
   - morphology: detailed grammatical analysis (case, number, tense, etc.)
   - pronunciation: approximate pronunciation guide

2. TRANSLATIONS: Complete verse translations in:
   - english: Modern English translation
   - french: French translation
   - spanish: Spanish translation  
   - portuguese: Portuguese translation
   - italian: Italian translation

3. THEOLOGICAL_LAYER: 3-4 key theological insights about this verse

4. JUNGIAN_LAYER: 3-4 Jungian/symbolic interpretations including:
   - Archetypal symbols and their meanings
   - Psychological interpretations of the imagery
   - Collective unconscious themes
   - Individuation process elements

5. COSMOLOGICAL_LAYER: 3-4 cosmological or historical context insights

Format as valid JSON:
{{
    "word_analysis": [
        {{
            "latin": "word",
            "definition": "meaning",
            "etymology": "origin",
            "part_of_speech": "noun/verb/etc",
            "morphology": "detailed grammar",
            "pronunciation": "pronunciation guide"
        }}
    ],
    "translations": {{
        "english": "translation",
        "french": "traduction",
        "spanish": "traducción",
        "portuguese": "tradução", 
        "italian": "traduzione"
    }},
    "theological_layer": [
        "theological insight 1",
        "theological insight 2",
        "theological insight 3"
    ],
    "jungian_layer": [
        "jungian insight 1", 
        "jungian insight 2",
        "jungian insight 3"
    ],
    "cosmological_layer": [
        "cosmological insight 1",
        "cosmological insight 2", 
        "cosmological insight 3"
    ]
}}"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Latin scholar and theologian with expertise in biblical interpretation, etymology, and symbolic analysis. Provide detailed, accurate analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,  # Increased for theological content
                temperature=0.3
            )
            
            return response
        
        try:
            response = exponential_backoff_retry(make_verse_analysis_call, max_retries=2, base_delay=3.0)
            if not response:
                return {"success": False, "error": "Failed to get response after retries"}
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # Cache each word individually
            if "word_analysis" in result:
                for word_data in result["word_analysis"]:
                    word_info = WordInfo(
                        latin=word_data.get("latin", ""),
                        definition=word_data.get("definition", ""),
                        etymology=word_data.get("etymology", ""),
                        part_of_speech=word_data.get("part_of_speech", ""),
                        morphology=word_data.get("morphology", ""),
                        pronunciation=word_data.get("pronunciation", ""),
                        source="greb_verse",
                        confidence=0.95
                    )
                    self.save_to_cache(word_info)
            
            # Save to cache before returning
            if verse_reference:
                self.save_verse_analysis_to_cache(verse_reference, verse_text, result)
            
            return {
                "success": True,
                **result,  # Unpack the full result
                "verse_text": verse_text,
                "verse_reference": verse_reference
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error in verse analysis: {e}")
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            print(f"Error in verse analysis: {e}")
            error_msg = str(e)
            if any(term in error_msg.lower() for term in ["rate limit", "429", "quota", "too many requests"]):
                return {"success": False, "error": "API quota exceeded. Please try again later."}
            return {"success": False, "error": str(e)}

    def get_verse_analysis_from_cache(self, verse_reference: str) -> Optional[Dict[str, Any]]:
        """Get complete verse analysis from cache"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT verse_text, word_analysis_json, translations_json, 
                       theological_layer_json, jungian_layer_json, cosmological_layer_json
                FROM verse_analysis_cache 
                WHERE verse_reference = ?
            ''', (verse_reference,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "success": True,
                    "verse_text": result[0],
                    "word_analysis": json.loads(result[1]) if result[1] else [],
                    "translations": json.loads(result[2]) if result[2] else {},
                    "theological_layer": json.loads(result[3]) if result[3] else [],
                    "jungian_layer": json.loads(result[4]) if result[4] else [],
                    "cosmological_layer": json.loads(result[5]) if result[5] else [],
                    "source": "cache"
                }
            return None
        except Exception as e:
            print(f"Error getting verse analysis from cache: {e}")
            return None

    def save_verse_analysis_to_cache(self, verse_reference: str, verse_text: str, analysis_data: Dict[str, Any]):
        """Save complete verse analysis to cache"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            word_analysis_json = json.dumps(analysis_data.get("word_analysis", []))
            translations_json = json.dumps(analysis_data.get("translations", {}))
            theological_json = json.dumps(analysis_data.get("theological_layer", []))
            jungian_json = json.dumps(analysis_data.get("jungian_layer", []))
            cosmological_json = json.dumps(analysis_data.get("cosmological_layer", []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO verse_analysis_cache 
                (verse_reference, verse_text, word_analysis_json, translations_json, 
                 theological_layer_json, jungian_layer_json, cosmological_layer_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (verse_reference, verse_text, word_analysis_json, translations_json, 
                  theological_json, jungian_json, cosmological_json))
            
            conn.commit()
            conn.close()
            print(f"Verse analysis cached for {verse_reference}")
        except Exception as e:
            print(f"Error saving verse analysis to cache: {e}")

def main():
    """Test the enhanced dictionary"""
    import sys
    
    # Initialize dictionary
    api_key = os.getenv('OPENAI_API_KEY')
    enhanced_dict = EnhancedDictionary(openai_api_key=api_key)
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_dictionary.py <word1> [word2] ...")
        print("Example: python enhanced_dictionary.py facta principio deus")
        return
    
    for word in sys.argv[1:]:
        print(f"\n{'='*60}")
        print(f"Looking up: {word}")
        print('='*60)
        
        result = enhanced_dict.lookup_word(word)
        
        print(f"Latin: {result.latin}")
        print(f"Definition: {result.definition}")
        print(f"Part of Speech: {result.part_of_speech}")
        print(f"Morphology: {result.morphology}")
        print(f"Etymology: {result.etymology}")
        if result.pronunciation:
            print(f"Pronunciation: {result.pronunciation}")
        print(f"Source: {result.source} (confidence: {result.confidence})")

if __name__ == "__main__":
    main() 