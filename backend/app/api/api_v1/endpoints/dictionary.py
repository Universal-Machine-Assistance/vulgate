from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Optional
import os
import sys
import time
import asyncio
from functools import wraps
import sqlite3
import json

# Add the project root to path so we can import enhanced_dictionary
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(project_root)

# Fix: Use the correct path for the main word_cache.db (not the backend subdirectory one)
# Hardcode the correct path since path resolution is tricky
CACHE_DB_PATH = "/Users/guillermomolina/dev/vulgate/word_cache.db"

from backend.app.services.enhanced_dictionary import EnhancedDictionary  # noqa
from backend.app.api.api_v1.endpoints.books import BOOK_ABBREVIATIONS  # Import book abbreviations
from backend.app.services.word_alignment import get_word_aligner
WordInfo = None  # Placeholder to avoid unresolved import

router = APIRouter()

# Rate limiting state
last_openai_call = 0
min_time_between_calls = 1.0  # Minimum 1 second between OpenAI API calls

# Determine analysis DB path relative to project root
ANALYSIS_DB_PATH = os.path.join(project_root, "vulgate_analysis.db")

# Word alignment caching functions
def get_cached_word_alignments(verse_reference: str, language_code: str) -> Optional[dict]:
    """Get cached word alignments from database"""
    try:
        cache_db_path = CACHE_DB_PATH
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT word_alignments_json, alignment_method, alignment_confidence,
                   translations_json, verse_text
            FROM verse_analysis_cache 
            WHERE verse_reference = ? AND language_code = ?
        ''', (verse_reference, language_code))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:  # word_alignments_json exists
            word_alignments = json.loads(result[0])
            translations = json.loads(result[3]) if result[3] else {}  # translations_json is at index 3
            
            return {
                "word_alignments": word_alignments,
                "alignment_method": result[1],
                "alignment_confidence": result[2],
                "translations": {language_code: translations.get("dynamic", "")},  # Frontend format
                "literal_translation": translations.get("literal", ""),
                "dynamic_translation": translations.get("dynamic", ""),
                "detailed_translations": {
                    language_code: {
                        "literal": translations.get("literal", ""),
                        "dynamic": translations.get("dynamic", "")
                    }
                }
            }
        return None
    except Exception as e:
        print(f"Error getting cached word alignments: {e}")
        return None

def cache_word_alignments(verse_reference: str, language_code: str, 
                         literal_translation: str, dynamic_translation: str,
                         word_alignments: dict):
    """Cache word alignments to database"""
    try:
        cache_db_path = CACHE_DB_PATH
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        # Prepare data for caching
        word_alignments_json = json.dumps(word_alignments)
        translations_data = {
            "literal": literal_translation,
            "dynamic": dynamic_translation
        }
        translations_json = json.dumps(translations_data)
        
        # Insert or update cache
        cursor.execute('''
            INSERT OR REPLACE INTO verse_analysis_cache 
            (verse_reference, language_code, verse_text, word_alignments_json, alignment_method, 
             alignment_confidence, translations_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            verse_reference, 
            language_code,
            "",  # verse_text - we'll add this parameter later
            word_alignments_json,
            word_alignments.get("method", "unknown"),
            word_alignments.get("average_confidence", 0.0),
            translations_json
        ))
        
        conn.commit()
        conn.close()
        print(f"💾 Cached word alignments for {verse_reference} ({language_code})")
        
    except Exception as e:
        print(f"Error caching word alignments: {e}")

def rate_limit_openai():
    """Rate limit OpenAI API calls to avoid 429 errors"""
    global last_openai_call
    now = time.time()
    time_since_last = now - last_openai_call
    
    if time_since_last < min_time_between_calls:
        sleep_time = min_time_between_calls - time_since_last
        print(f"Rate limiting: sleeping {sleep_time:.2f}s before next OpenAI call")
        time.sleep(sleep_time)
    
    last_openai_call = time.time()

def retry_on_rate_limit(max_retries=3, base_delay=1.0):
    """Decorator to add exponential backoff retry logic for rate limited functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    if 'openai' in str(func.__name__).lower() or attempt > 0:
                        rate_limit_openai()
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    # run sync functions in a thread to avoid blocking
                    return await asyncio.to_thread(func, *args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            print(f"Rate limit hit on attempt {attempt + 1}, retrying in {delay}s...")
                            await asyncio.sleep(delay)
                            continue
                    raise e
            return None
        return wrapper
    return decorator

def get_enhanced_dictionary(request: Request) -> EnhancedDictionary:
    return request.app.state.enhanced_dictionary

@router.get("/lookup/{word}")
@retry_on_rate_limit()
async def lookup_word(word: str, request: Request):
    """
    Enhanced word lookup with morphological analysis and AI fallback
    """
    try:
        enhanced_dict = get_enhanced_dictionary(request)
        result = enhanced_dict.lookup_word(word)
        
        return {
            "word": word,
            "found": result.source != "not_found",
            "latin": result.latin,
            "definition": result.definition,
            "etymology": result.etymology,
            "partOfSpeech": result.part_of_speech,
            "morphology": result.morphology,
            "pronunciation": result.pronunciation,
            "source": result.source,
            "confidence": result.confidence
        }
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in str(e):
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Dictionary lookup failed: {error_msg}")

@router.post("/lookup/batch")
@retry_on_rate_limit()
async def lookup_words_batch(request: Request):
    """
    Batch lookup for multiple words with proper validation
    """
    try:
        # Get request body
        body = await request.json()
        
        # Validate request format
        if not isinstance(body, dict):
            raise HTTPException(status_code=422, detail="Request body must be a JSON object")
        
        words = body.get("words", [])
        if not isinstance(words, list):
            raise HTTPException(status_code=422, detail="'words' must be an array of strings")
        
        if not words:
            raise HTTPException(status_code=422, detail="'words' array cannot be empty")
        
        if len(words) > 50:  # Reasonable limit
            raise HTTPException(status_code=422, detail="Too many words. Maximum 50 words per batch.")
        
        # Validate each word
        for i, word in enumerate(words):
            if not isinstance(word, str):
                raise HTTPException(status_code=422, detail=f"Word at index {i} must be a string")
            if len(word.strip()) == 0:
                raise HTTPException(status_code=422, detail=f"Word at index {i} cannot be empty")
        
        # Optional parameters (ignore them for now, but don't error)
        include_translations = body.get("include_translations", False)
        include_theological = body.get("include_theological", False)
        
        enhanced_dict = get_enhanced_dictionary(request)
        results = []
        
        # Add small delay between words to avoid rate limiting
        for i, word in enumerate(words):
            if i > 0:  # Don't delay before first word
                await asyncio.sleep(0.1)  # 100ms delay between lookups
                
            result = enhanced_dict.lookup_word(word.strip())
            results.append({
                "word": word,
                "found": result.source != "not_found",
                "latin": result.latin,
                "definition": result.definition,
                "etymology": result.etymology,
                "partOfSpeech": result.part_of_speech,
                "morphology": result.morphology,
                "pronunciation": result.pronunciation,
                "source": result.source,
                "confidence": result.confidence
            })
        
        return {"results": results}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in str(e):
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Batch dictionary lookup failed: {error_msg}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint with rate limiting info
    """
    global last_openai_call
    now = time.time()
    time_since_last = now - last_openai_call
    
    return {
        "status": "healthy",
        "rate_limiting": {
            "min_time_between_calls": min_time_between_calls,
            "time_since_last_call": time_since_last,
            "ready_for_next_call": time_since_last >= min_time_between_calls
        }
    }

@router.get("/stats")
async def get_dictionary_stats(request: Request):
    """
    Get dictionary statistics including cache information
    """
    try:
        enhanced_dict = get_enhanced_dictionary(request)
        
        # Count entries in main dictionary
        main_dict_count = len(enhanced_dict.dictionary)
        
        # Get detailed cache stats
        cache_stats = enhanced_dict.get_cache_stats()
        cached_count = cache_stats['total_cached']
        
        return {
            "main_dictionary_entries": main_dict_count,
            "cached_entries": cached_count,
            "total_available": main_dict_count + cached_count,
            "openai_enabled": enhanced_dict.openai_enabled,
            "cache_file": cache_stats['cache_file'],
            "cache_breakdown_by_source": cache_stats['source_breakdown']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dictionary stats: {str(e)}")

@router.post("/regenerate/{word}")
async def regenerate_word(word: str, request: Request):
    """
    Regenerate/refresh analysis for a specific word by clearing cache and forcing new lookup
    """
    try:
        enhanced_dict = get_enhanced_dictionary(request)
        
        # Clear the word from cache
        was_cached = enhanced_dict.clear_word_cache(word)
        
        # Perform fresh lookup
        result = enhanced_dict.lookup_word(word)
        
        return {
            "word": word,
            "regenerated": True,
            "was_previously_cached": was_cached,
            "found": result.source != "not_found",
            "latin": result.latin,
            "definition": result.definition,
            "etymology": result.etymology,
            "partOfSpeech": result.part_of_speech,
            "morphology": result.morphology,
            "pronunciation": result.pronunciation,
            "source": result.source,
            "confidence": result.confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word regeneration failed: {str(e)}")

@router.post("/cache/clear")
async def clear_entire_cache(request: Request):
    """
    Clear the entire word cache (use with caution - will force regeneration of all cached words)
    """
    try:
        enhanced_dict = get_enhanced_dictionary(request)
        
        conn = sqlite3.connect(enhanced_dict.cache_db)
        cursor = conn.cursor()
        
        # Count before clearing
        cursor.execute('SELECT COUNT(*) FROM word_cache')
        count_before = cursor.fetchone()[0]
        
        # Clear cache
        cursor.execute('DELETE FROM word_cache')
        conn.commit()
        conn.close()
        
        return {
            "cache_cleared": True,
            "words_removed": count_before,
            "message": f"Cleared {count_before} cached words. Fresh analysis will be performed on next lookup."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")

@router.post("/analyze/verse")
@retry_on_rate_limit(max_retries=2, base_delay=2.0)
async def analyze_verse(request: Request):
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        verse_reference = data.get("reference", "").strip()
        include_translations = data.get("include_translations", True)
        include_theological = data.get("include_theological", True)

        # Input validation
        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")
        
        if len(verse_text) > 1000:  # Reasonable limit for a verse
            raise HTTPException(status_code=400, detail="Verse text is too long")

        # Get dictionary instance
        try:
            dictionary = get_enhanced_dictionary(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize dictionary: {str(e)}")

        if not dictionary.openai_enabled:
            return {
                "success": False,
                "error": "OpenAI not enabled on server"
            }

        # Rate limit before making the call
        rate_limit_openai()

        # Analyze verse
        try:
            analysis_data = dictionary.analyze_verse(verse_text, verse_reference)
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=f"Verse analysis failed: {error_msg}")
        
        if not analysis_data.get("success", False):
            error_msg = analysis_data.get("error", "Analysis failed")
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=error_msg)

        # Extract word analysis
        analysis = []
        if "word_analysis" in analysis_data:
            for word_data in analysis_data["word_analysis"]:
                if not isinstance(word_data, dict):
                    continue
                analysis.append({
                    "latin": word_data.get("latin", ""),
                    "definition": word_data.get("definition", ""),
                    "etymology": word_data.get("etymology", ""),
                    "part_of_speech": word_data.get("part_of_speech", ""),
                    "morphology": word_data.get("morphology", ""),
                    "pronunciation": word_data.get("pronunciation", "")
                })

        # Prepare full analysis response
        full_analysis = {
            "word_analysis": analysis
        }

        # Add translations if requested
        if include_translations and "translations" in analysis_data:
            full_analysis["translations"] = analysis_data["translations"]

        # Add theological layer if requested
        if include_theological and "theological_layer" in analysis_data:
            full_analysis["theological_layer"] = analysis_data["theological_layer"]

        return {
            "success": True,
            "analysis": analysis,
            "verse_text": verse_text,
            "verse_reference": verse_reference,
            "full_analysis": full_analysis
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in verse analysis endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")

@router.post("/analyze/verse/complete")
async def analyze_verse_complete(request: Request):
    """
    Complete verse analysis in a single call - returns word analysis, translations, and interpretive layers
    """
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        verse_reference = data.get("reference", "").strip()

        # Input validation
        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")
        
        if len(verse_text) > 1000:  # Reasonable limit for a verse
            raise HTTPException(status_code=400, detail="Verse text is too long")

        # Get dictionary instance
        try:
            dictionary = get_enhanced_dictionary(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize dictionary: {str(e)}")
        if not dictionary.openai_enabled:
            return {"success": False, "error": "OpenAI not enabled on server"}

        
        # Check cache first before any rate limiting
        if verse_reference:
            cached_analysis = dictionary.get_verse_analysis_from_cache(verse_reference)
            if cached_analysis:
                print(f"Returning cached analysis for {verse_reference}")
                return {
                    "success": True,
                    "verse_text": verse_text,
                    "verse_reference": verse_reference,
                    "source": "cache",
                    "word_analysis": cached_analysis.get("word_analysis", []),
                    "translations": cached_analysis.get("translations", {}),
                    "theological_layer": cached_analysis.get("theological_layer", []),
                    "symbolic_layer": cached_analysis.get("symbolic_layer", []),
                    "cosmological_layer": cached_analysis.get("cosmological_layer", [])
                }
        
        # Only rate limit if we need to make OpenAI call - with retry logic
        max_retries = 2
        base_delay = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                rate_limit_openai()
                analysis_data = dictionary.analyze_verse(verse_text, verse_reference)
                break  # Success, exit retry loop
            except Exception as e:
                error_msg = str(e)
                if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit on attempt {attempt + 1}/{max_retries + 1}, retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"Max retries ({max_retries}) exceeded for rate limit")
                        raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
                else:
                    raise HTTPException(status_code=500, detail=f"Verse analysis failed: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail="Unexpected error in analysis retry loop")
        
        if not analysis_data.get("success", False):
            error_msg = analysis_data.get("error", "Analysis failed")
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=error_msg)

        return {
            "success": True,
            "verse_text": verse_text,
            "verse_reference": verse_reference,
            "source": analysis_data.get("source", "openai"),
            "word_analysis": analysis_data.get("word_analysis", []),
            "translations": analysis_data.get("translations", {}),
            "theological_layer": analysis_data.get("theological_layer", []),
            "symbolic_layer": analysis_data.get("symbolic_layer", []),
            "cosmological_layer": analysis_data.get("cosmological_layer", [])
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in complete verse analysis endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")

@router.post("/translate")
async def translate_verse_endpoint(request: Request):
    """
    Translate a verse to a target language with automatic source language detection
    and optional analysis in the target language
    """
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        target_language = data.get("language", "en").strip()
        verse_reference = data.get("reference", "").strip()
        include_analysis = data.get("include_analysis", False)  # New parameter

        # Input validation
        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")
        
        if len(verse_text) > 2000:  # Increased limit for Gita verses with formatting
            raise HTTPException(status_code=400, detail="Verse text is too long")

        # Supported languages
        supported_languages = ["en", "es", "fr", "it", "pt", "de", "la", "sa", "hi"]
        if target_language not in supported_languages:
            raise HTTPException(
                status_code=400, 
                detail=f"Language '{target_language}' not supported. Supported: {', '.join(supported_languages)}"
            )

        # Get dictionary instance
        try:
            dictionary = get_enhanced_dictionary(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize dictionary: {str(e)}")

        if not dictionary.openai_enabled:
            return {
                "success": False,
                "error": "OpenAI not enabled on server"
            }

        # Check cache first
        cache_key = f"{verse_reference}_{dictionary.detect_source_language(verse_text)}_{target_language}"
        if verse_reference:
            cached_translation = dictionary.get_translation_from_cache(cache_key)
            if cached_translation:
                result = {
                    "success": True,
                    "verse_text": verse_text,
                    "verse_reference": verse_reference,
                    "target_language": target_language,
                    "source": "cache",
                    **cached_translation
                }
                
                # Add analysis if requested and not already included
                if include_analysis and "analysis" not in result:
                    try:
                        analysis_data = dictionary.analyze_verse_with_openai(
                            verse_text, 
                            verse_reference, 
                            target_analysis_language=target_language
                        )
                        if analysis_data.get("success"):
                            result["analysis"] = {
                                "word_analysis": analysis_data.get("word_analysis", []),
                                "theological_layer": analysis_data.get("theological_layer", []),
                                "philosophical_layer": analysis_data.get("philosophical_layer", []),
                                "symbolic_layer": analysis_data.get("symbolic_layer", []),
                                "cosmological_layer": analysis_data.get("cosmological_layer", []),
                                "analysis_language": target_language
                            }
                    except Exception as e:
                        print(f"Failed to add analysis to cached translation: {e}")
                
                return result

        # Rate limit before making the call
        rate_limit_openai()

        # Translate verse
        try:
            translation_result = dictionary.translate_verse(verse_text, target_language)
            
            # Parse translation result
            if isinstance(translation_result, str):
                try:
                    translation_data = json.loads(translation_result)
                    
                    # Validate that we have clean translations (not metadata)
                    if "literal" in translation_data and "dynamic" in translation_data:
                        # Check if the translations look like actual translations vs metadata
                        literal = translation_data.get("literal", "")
                        if ("translation:" in literal.lower() or 
                            "json" in literal.lower() or 
                            len(literal) > 500):
                            # This looks like metadata, try to extract actual translations
                            print(f"Detected metadata in translation, attempting to clean up")
                            translation_data = {
                                "literal": "Translation processing error",
                                "dynamic": "Translation processing error",
                                "source_language": dictionary.detect_source_language(verse_text),
                                "error": "OpenAI returned metadata instead of translation"
                            }
                    
                except json.JSONDecodeError:
                    translation_data = {
                        "literal": translation_result,
                        "dynamic": translation_result,
                        "source_language": dictionary.detect_source_language(verse_text)
                    }
            else:
                translation_data = translation_result

            # Determine which translation to use based on request (default to transliteration)
            translation_type = data.get("type", "transliteration")  # Default to transliteration
            
            if translation_type == "dynamic":
                final_translation = translation_data.get("dynamic", translation_data.get("literal", ""))
            elif translation_type == "literal":
                final_translation = translation_data.get("literal", translation_data.get("dynamic", ""))
            else:
                # Default to transliteration (literal for now, but could be enhanced)
                final_translation = translation_data.get("literal", translation_data.get("dynamic", ""))

            # Generate word alignments
            word_aligner = get_word_aligner()
            source_language = translation_data.get("source_language", "unknown")
            
            # Create alignments for both literal and dynamic translations
            literal_alignments_data = None
            dynamic_alignments_data = None
            
            literal_translation = translation_data.get("literal", "")
            dynamic_translation = translation_data.get("dynamic", "")
            
            if literal_translation:
                literal_alignments_data = word_aligner.align_words(
                    verse_text, 
                    literal_translation, 
                    source_language
                )
            
            if dynamic_translation:
                dynamic_alignments_data = word_aligner.align_words(
                    verse_text, 
                    dynamic_translation, 
                    source_language
                )

            # Format alignments for response
            literal_formatted = word_aligner.format_alignment_response(literal_alignments_data) if literal_alignments_data else {"alignments": [], "method": "none", "average_confidence": 0.0}
            dynamic_formatted = word_aligner.format_alignment_response(dynamic_alignments_data) if dynamic_alignments_data else {"alignments": [], "method": "none", "average_confidence": 0.0}

            result = {
                "success": True,
                "verse_text": verse_text,
                "verse_reference": verse_reference,
                "target_language": target_language,
                "translation_type": translation_type,
                "translation": final_translation,
                "literal": literal_translation,
                "dynamic": dynamic_translation,
                "source_language": source_language,
                "source": "openai",
                "word_alignments": {
                    "literal": literal_formatted["alignments"],
                    "dynamic": dynamic_formatted["alignments"],
                    "method": literal_formatted.get("method", "fallback"),
                    "literal_confidence": literal_formatted.get("average_confidence", 0.0),
                    "dynamic_confidence": dynamic_formatted.get("average_confidence", 0.0),
                    "average_confidence": (
                        (literal_formatted.get("average_confidence", 0.0) + 
                         dynamic_formatted.get("average_confidence", 0.0)) / 2
                        if literal_formatted["alignments"] and dynamic_formatted["alignments"] else
                        literal_formatted.get("average_confidence", 0.0) if literal_formatted["alignments"] else
                        dynamic_formatted.get("average_confidence", 0.0) if dynamic_formatted["alignments"] else 0.0
                    )
                }
            }

            # Add analysis if requested
            if include_analysis:
                try:
                    analysis_data = dictionary.analyze_verse_with_openai(
                        verse_text, 
                        verse_reference, 
                        target_analysis_language=target_language
                    )
                    if analysis_data.get("success"):
                        result["analysis"] = {
                            "word_analysis": analysis_data.get("word_analysis", []),
                            "theological_layer": analysis_data.get("theological_layer", []),
                            "philosophical_layer": analysis_data.get("philosophical_layer", []),
                            "symbolic_layer": analysis_data.get("symbolic_layer", []),
                            "cosmological_layer": analysis_data.get("cosmological_layer", []),
                            "analysis_language": target_language
                        }
                except Exception as e:
                    print(f"Failed to add analysis to translation: {e}")
                    result["analysis_error"] = str(e)

            # Cache the result
            if verse_reference:
                cache_data = {
                    "translation": final_translation,
                    "literal": literal_translation,
                    "dynamic": dynamic_translation,
                    "source_language": source_language,
                    "word_alignments": result.get("word_alignments", {})
                }
                if include_analysis and "analysis" in result:
                    cache_data["analysis"] = result["analysis"]
                
                dictionary.save_translation_to_cache(cache_key, cache_data)

            return result

        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=f"Translation failed: {error_msg}")

    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in translate endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")

@router.get("/cache/verse-stats")
async def get_verse_cache_stats(request: Request):
    """
    Get statistics about cached verse analyses
    """
    try:
        enhanced_dict = get_enhanced_dictionary(request)
        
        conn = sqlite3.connect(enhanced_dict.cache_db)
        cursor = conn.cursor()
        
        # Count total cached verses
        cursor.execute('SELECT COUNT(*) FROM verse_analysis_cache')
        total_verses = cursor.fetchone()[0]
        
        # Get recent verses
        cursor.execute('''
            SELECT verse_reference, created_at 
            FROM verse_analysis_cache 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_verses = [{"reference": row[0], "cached_at": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_cached_verses": total_verses,
            "recent_verses": recent_verses,
            "message": f"Working towards complete Vulgate translation - {total_verses} verses analyzed so far"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get verse cache stats: {str(e)}")

@router.get("/word/{word}/verses")
async def get_verses_for_word(word: str):
    """Return all verses that contain the given word (case-sensitive match in stored grammar breakdown)."""
    try:
        conn = sqlite3.connect(ANALYSIS_DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT v.book_abbreviation, v.chapter_number, v.verse_number, v.latin_text, g.word_index
               FROM grammar_breakdowns g
               JOIN verse_analyses v ON v.id = g.verse_analysis_id
               WHERE g.word = ?
               ORDER BY v.book_abbreviation, v.chapter_number, v.verse_number''',
            (word,)
        )
        rows = cursor.fetchall()
        conn.close()

        verses = [
            {
                "verse_reference": f"{b} {c}:{v}",
                "verse_text": text,
                "position": idx
            }
            for b, c, v, text, idx in rows
        ]

        return {
            "word": word,
            "found": len(verses) > 0,
            "verse_count": len(verses),
            "verses": verses
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch verses for word: {str(e)}")

@router.get("/name-occurrences/{word}")
async def get_name_occurrences(word: str):
    """Alias to /word/{word}/verses – provided for backward compatibility with the existing frontend."""
    return await get_verses_for_word(word)

@router.post("/analyze/verse/openai")
async def analyze_verse_openai(request: Request):
    """
    Force OpenAI analysis for a verse (bypass cache) with support for multiple analysis languages
    Now includes word alignments for both literal and dynamic translations
    """
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        verse_reference = data.get("reference", "").strip()
        target_analysis_language = data.get("analysis_language", "en").strip()  # New parameter
        include_translations = data.get("include_translations", True)  # Include translations by default
        
        # Support for multiple languages
        requested_languages = data.get("languages", [])
        multilingual = data.get("multilingual", False)
        all_languages = data.get("all_languages", False)
        
        # Determine which languages to include
        if all_languages:
            target_languages = ["en", "es", "fr", "it", "pt", "de"]  # Common languages
        elif multilingual and requested_languages:
            target_languages = requested_languages
        elif requested_languages:
            target_languages = requested_languages
        else:
            target_languages = [target_analysis_language]
            
        # Always include English if not already included
        if "en" not in target_languages:
            target_languages.append("en")
        
        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")
        
        enhanced_dict = get_enhanced_dictionary(request)
        analysis_data = enhanced_dict.analyze_verse_with_openai(
            verse_text, 
            verse_reference, 
            language_code='la',  # Force Latin as source language
            target_analysis_language=target_analysis_language
        )
        
        if not analysis_data.get("success", False):
            error_msg = analysis_data.get("error", "Analysis failed")
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Prepare base response
        response = {
            "success": True,
            "verse_text": verse_text,
            "verse_reference": verse_reference,
            "analysis_language": target_analysis_language,
            "source_language": analysis_data.get("source_language", "unknown"),
            "word_analysis": analysis_data.get("word_analysis", []),
            "translations": analysis_data.get("translations", {}),
            "theological_layer": analysis_data.get("theological_layer", []),
            "philosophical_layer": analysis_data.get("philosophical_layer", []),  # For Sanskrit texts
            "symbolic_layer": analysis_data.get("symbolic_layer", []),
            "cosmological_layer": analysis_data.get("cosmological_layer", []),
            "source": analysis_data.get("source", "openai_forced")
        }
        
        # Add word alignments if translations are requested
        if include_translations:
            try:
                # Check cache first for word alignments
                cached_alignments = get_cached_word_alignments(verse_reference, target_analysis_language)
                
                if cached_alignments:
                    print(f"📦 Using cached word alignments for {verse_reference} ({target_analysis_language})")
                    response.update(cached_alignments)
                    
                    # Add translations for all other requested languages (not just the cached one)
                    if "translations" not in response:
                        response["translations"] = {}
                    
                    for lang in target_languages:
                        if lang not in response["translations"]:
                            try:
                                lang_result = enhanced_dict.translate_verse(verse_text, lang)
                                if isinstance(lang_result, str):
                                    lang_data = json.loads(lang_result)
                                    response["translations"][lang] = lang_data.get("dynamic", "")
                                else:
                                    response["translations"][lang] = lang_result.get("dynamic", "")
                            except Exception as e:
                                print(f"Failed to get {lang} translation: {e}")
                                response["translations"][lang] = "Translation not available"
                else:
                    print(f"🔄 Generating new word alignments for {verse_reference} ({target_analysis_language})")
                    
                    # Get translations for the verse
                    translation_result = enhanced_dict.translate_verse(verse_text, target_analysis_language)
                    
                    if isinstance(translation_result, str):
                        try:
                            translation_data = json.loads(translation_result)
                        except json.JSONDecodeError:
                            translation_data = {
                                "literal": "Translation not available",
                                "dynamic": "Translation not available",
                                "source_language": enhanced_dict.detect_source_language(verse_text)
                            }
                    else:
                        translation_data = translation_result
                    
                    # Generate word alignments if we have valid translations
                    literal_translation = translation_data.get("literal", "")
                    dynamic_translation = translation_data.get("dynamic", "")
                    # Force Latin for Bible verses (don't rely on auto-detection)
                    source_language = "latin"
                    
                    # Ensure we have valid translations before proceeding
                    if not literal_translation or not dynamic_translation:
                        print(f"⚠️  Missing translations: literal='{literal_translation}', dynamic='{dynamic_translation}'")
                        response["word_alignments_error"] = "Missing translation data"
                    
                    if literal_translation and dynamic_translation:
                        word_aligner = get_word_aligner()
                        
                        # Create alignments for both translations
                        literal_alignments_data = word_aligner.align_words(verse_text, literal_translation, source_language)
                        dynamic_alignments_data = word_aligner.align_words(verse_text, dynamic_translation, source_language)
                        
                        # Format alignments for internal use
                        literal_formatted = word_aligner.format_alignment_response(literal_alignments_data)
                        dynamic_formatted = word_aligner.format_alignment_response(dynamic_alignments_data)
                        
                        # Format alignments for frontend (position-indexed arrays)
                        frontend_alignments = word_aligner.format_alignment_for_frontend(
                            literal_formatted, dynamic_formatted, verse_text
                        )
                        
                        # Add to response
                        response["literal_translation"] = literal_translation
                        response["dynamic_translation"] = dynamic_translation
                        response["word_alignments"] = frontend_alignments
                        
                        # Add translations for all requested languages
                        if "translations" not in response:
                            response["translations"] = {}
                        
                        # Add the primary analysis language translation
                        response["translations"][target_analysis_language] = dynamic_translation
                        
                        # Add translations for all other requested languages
                        for lang in target_languages:
                            if lang != target_analysis_language and lang not in response["translations"]:
                                try:
                                    lang_result = enhanced_dict.translate_verse(verse_text, lang)
                                    if isinstance(lang_result, str):
                                        lang_data = json.loads(lang_result)
                                        response["translations"][lang] = lang_data.get("dynamic", "")
                                    else:
                                        response["translations"][lang] = lang_result.get("dynamic", "")
                                except Exception as e:
                                    print(f"Failed to get {lang} translation: {e}")
                                    response["translations"][lang] = "Translation not available"
                        
                        # Also provide detailed translations for advanced features
                        response["detailed_translations"] = {
                            target_analysis_language: {
                                "literal": literal_translation,
                                "dynamic": dynamic_translation
                            }
                        }
                        
                        # Cache the results for future use
                        cache_word_alignments(
                            verse_reference, 
                            target_analysis_language,
                            literal_translation,
                            dynamic_translation,
                            frontend_alignments
                        )
                
            except Exception as e:
                print(f"Failed to add word alignments to analysis: {e}")
                # Continue without word alignments if they fail
                response["word_alignments_error"] = str(e)
        
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in OpenAI verse analysis endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")

@router.post("/analyze/grammar/relationships")
async def analyze_grammatical_relationships(request: Request):
    """
    Analyze grammatical relationships between words in a Latin sentence
    """
    try:
        data = await request.json()
        sentence = data.get("sentence", "").strip()
        verse_reference = data.get("reference", "").strip()
        
        # Input validation
        if not sentence:
            raise HTTPException(status_code=400, detail="Sentence text is required")
        
        if len(sentence) > 2000:  # Reasonable limit for a sentence
            raise HTTPException(status_code=400, detail="Sentence text is too long")
        
        # Get dictionary instance
        enhanced_dict = get_enhanced_dictionary(request)
        
        # Rate limit before OpenAI call
        rate_limit_openai()
        
        # Analyze grammatical relationships
        analysis_data = enhanced_dict.analyze_grammatical_relationships(sentence, verse_reference)
        
        if not analysis_data.get("success", False):
            error_msg = analysis_data.get("error", "Grammatical analysis failed")
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail=error_msg)
        
        return {
            "success": True,
            "sentence": sentence,
            "verse_reference": verse_reference,
            "words": analysis_data.get("words", []),
            "sentence_structure": analysis_data.get("sentence_structure", {}),
            "morphological_summary": analysis_data.get("morphological_summary", ""),
            "source": analysis_data.get("source", "openai_grammar_analysis")
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in grammatical relationships analysis endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")

@router.get("/books/{book_abbr}")
@retry_on_rate_limit()
async def get_book_info(book_abbr: str, request: Request):
    """
    Get comprehensive book information by abbreviation using OpenAI.
    Returns detailed information about a biblical book including Latin name, 
    author, historical context, themes, and other scholarly details.
    """
    try:
        # Convert abbreviation to book name
        book_names = {
            "Gn": "Genesis", "Ex": "Exodus", "Lev": "Leviticus", "Num": "Numbers", "Dt": "Deuteronomy",
            "Jos": "Joshua", "Jdc": "Judges", "Ru": "Ruth", "1Sm": "1 Samuel", "2Sm": "2 Samuel",
            "1Kgs": "1 Kings", "2Kgs": "2 Kings", "1Chr": "1 Chronicles", "2Chr": "2 Chronicles",
            "Esd": "Ezra", "Neh": "Nehemiah", "Tb": "Tobit", "Jdt": "Judith", "Est": "Esther",
            "1Mc": "1 Maccabees", "2Mc": "2 Maccabees", "Jb": "Job", "Ps": "Psalms", "Pr": "Proverbs",
            "Qo": "Ecclesiastes", "Ct": "Song of Songs", "Sap": "Wisdom", "Si": "Sirach", "Is": "Isaiah",
            "Jer": "Jeremiah", "Lam": "Lamentations", "Ba": "Baruch", "Ez": "Ezekiel", "Dn": "Daniel",
            "Os": "Hosea", "Jl": "Joel", "Am": "Amos", "Ab": "Obadiah", "Jon": "Jonah", "Mi": "Micah",
            "Na": "Nahum", "Ha": "Habakkuk", "So": "Zephaniah", "Ag": "Haggai", "Za": "Zechariah",
            "Mal": "Malachi", "Mt": "Matthew", "Mc": "Mark", "Lc": "Luke", "Jo": "John", "Ac": "Acts",
            "Rm": "Romans", "1Cor": "1 Corinthians", "2Cor": "2 Corinthians", "Ga": "Galatians",
            "Ep": "Ephesians", "Ph": "Philippians", "Col": "Colossians", "1Th": "1 Thessalonians",
            "2Th": "2 Thessalonians", "1Tm": "1 Timothy", "2Tm": "2 Timothy", "Tit": "Titus",
            "Phm": "Philemon", "He": "Hebrews", "Jc": "James", "1Pt": "1 Peter", "2Pt": "2 Peter",
            "1Jo": "1 John", "2Jo": "2 John", "3Jo": "3 John", "Judæ": "Jude", "Ap": "Revelation"
        }
        
        book_name = book_names.get(book_abbr)
        if not book_name:
            raise HTTPException(status_code=404, detail=f"Informatio libri '{book_abbr}' inveniri non potest")
        
        # Get enhanced dictionary to make OpenAI call
        enhanced_dict = get_enhanced_dictionary(request)
        
        if not enhanced_dict.openai_enabled:
            # Return basic info if OpenAI not available
            return {
                "found": True,
                "book_name": book_name,
                "latin_name": f"Liber {book_name}",
                "author": "Traditional authorship",
                "date_written": "Ancient period",
                "historical_context": f"The book of {book_name} is part of the Vulgate Bible.",
                "summary": f"Biblical book of {book_name}",
                "theological_importance": f"The book of {book_name} contains important theological teachings.",
                "literary_genre": "Biblical literature",
                "key_themes": [f"Themes from {book_name}"],
                "symbolism": [f"Symbols from {book_name}"],
                "language_notes": "Latin Vulgate translation",
                "chapter_summaries": {},
                "source": "basic",
                "confidence": 0.3
            }
        
        # Rate limit before OpenAI call
        rate_limit_openai()
        
        # Make OpenAI call to generate comprehensive book information
        import openai
        openai.api_key = enhanced_dict.openai_api_key
        
        prompt = f"""Generate comprehensive scholarly information about the biblical book of {book_name} in JSON format.

Please provide detailed information including:
- Latin name (traditional Vulgate name)
- Author (traditional and critical scholarship views)
- Date written (range with scholarly consensus)
- Historical context (when and why it was written)
- Summary (3-4 sentences covering main content)
- Theological importance (key doctrinal significance)
- Literary genre (biblical literature classification)
- Key themes (3-5 major theological themes)
- Symbolism (important symbolic elements)
- Language notes (specific to Latin Vulgate translation)

Return ONLY valid JSON in this exact format:
{{
  "latin_name": "...",
  "author": "...",
  "date_written": "...",
  "historical_context": "...",
  "summary": "...",
  "theological_importance": "...",
  "literary_genre": "...",
  "key_themes": ["...", "...", "..."],
  "symbolism": ["...", "...", "..."],
  "language_notes": "..."
}}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a biblical scholar expert in the Latin Vulgate Bible. Provide accurate, scholarly information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            book_data = json.loads(content)
            
            # Return the OpenAI-generated information
            return {
                "found": True,
                "book_name": book_name,
                "latin_name": book_data.get("latin_name", f"Liber {book_name}"),
                "author": book_data.get("author", "Traditional authorship"),
                "date_written": book_data.get("date_written", "Ancient period"),
                "historical_context": book_data.get("historical_context", f"The book of {book_name} is part of the Vulgate Bible."),
                "summary": book_data.get("summary", f"Biblical book of {book_name}"),
                "theological_importance": book_data.get("theological_importance", f"The book of {book_name} contains important theological teachings."),
                "literary_genre": book_data.get("literary_genre", "Biblical literature"),
                "key_themes": book_data.get("key_themes", [f"Themes from {book_name}"]),
                "symbolism": book_data.get("symbolism", [f"Symbols from {book_name}"]),
                "language_notes": book_data.get("language_notes", "Latin Vulgate translation"),
                "chapter_summaries": {},
                "source": "openai",
                "confidence": 0.85
            }
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return basic info
            return {
                "found": True,
                "book_name": book_name,
                "latin_name": f"Liber {book_name}",
                "author": "Traditional authorship",
                "date_written": "Ancient period",
                "historical_context": f"The book of {book_name} is part of the Vulgate Bible.",
                "summary": f"Biblical book of {book_name}",
                "theological_importance": f"The book of {book_name} contains important theological teachings.",
                "literary_genre": "Biblical literature",
                "key_themes": [f"Themes from {book_name}"],
                "symbolism": [f"Symbols from {book_name}"],
                "language_notes": "Latin Vulgate translation",
                "chapter_summaries": {},
                "source": "fallback",
                "confidence": 0.3
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        if "rate limit" in str(e).lower() or "429" in str(e):
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Failed to get book info: {str(e)}")

@router.get("/books/")
async def get_all_books(request: Request):
    """
    Get list of all biblical books with basic information.
    """
    try:
        return {
            "found": True,
            "books": [],
            "message": "Book list endpoint available"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get books list: {str(e)}")

@router.get("/books/stats")
async def get_books_stats(request: Request):
    """
    Get statistics about cached book information.
    """
    try:
        return {
            "total_books_cached": 0,
            "openai_enabled": True,
            "message": "Book stats endpoint available"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get books stats: {str(e)}")

@router.post("/lookup/translation")
async def lookup_translation_word(request: Request):
    """
    Lookup a word from a translation (Spanish, Portuguese, French, etc.) 
    and save it to our dictionary for future reference
    """
    try:
        data = await request.json()
        word = data.get("word", "").strip()
        language = data.get("language", "").strip()
        
        if not word:
            raise HTTPException(status_code=400, detail="Word is required")
        
        if not language:
            raise HTTPException(status_code=400, detail="Language is required")
        
        enhanced_dict = get_enhanced_dictionary(request)
        
        # First check if we already have this word in our cache
        cached_result = enhanced_dict.get_from_cache(word, language)
        if cached_result:
            print(f"📦 Found {language} word '{word}' in cache")
            return {
                "word": word,
                "language": language,
                "found": True,
                "definition": cached_result.definition,
                "etymology": cached_result.etymology,
                "partOfSpeech": cached_result.part_of_speech,
                "pronunciation": cached_result.pronunciation,
                "source": cached_result.source,
                "confidence": cached_result.confidence
            }
        
        # If not in cache, try to get translation/definition using OpenAI
        if enhanced_dict.openai_enabled:
            try:
                rate_limit_openai()
                
                # Create a prompt to get word information in the target language
                import openai
                openai.api_key = enhanced_dict.openai_api_key
                
                prompt = f"""Provide detailed information about the {language} word "{word}" in JSON format.

Please include:
- definition: Clear definition in English
- etymology: Word origin and root
- partOfSpeech: Part of speech (noun, verb, adjective, etc.)
- pronunciation: Phonetic pronunciation if available
- examples: 1-2 example sentences in {language}

Return ONLY valid JSON:
{{
    "definition": "English definition",
    "etymology": "Word etymology",
    "partOfSpeech": "part of speech",
    "pronunciation": "pronunciation guide",
    "examples": ["example 1", "example 2"]
}}"""

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a {language} language expert providing detailed word information."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    temperature=0.3
                )
                
                result_text = response.choices[0].message.content
                word_data = json.loads(result_text)
                
                # Create WordInfo object
                from backend.app.services.enhanced_dictionary import WordInfo
                word_info = WordInfo(
                    latin=word,  # Store the foreign word in the latin field for consistency
                    definition=word_data.get("definition", f"Definition for {word} not found"),
                    etymology=word_data.get("etymology", ""),
                    part_of_speech=word_data.get("partOfSpeech", ""),
                    morphology="",
                    pronunciation=word_data.get("pronunciation", ""),
                    source=f"openai_{language}_lookup",
                    confidence=0.8
                )
                
                # Save to cache for future reference
                enhanced_dict.save_to_cache(word_info, language)
                
                print(f"💾 Saved {language} word '{word}' to dictionary")
                
                return {
                    "word": word,
                    "language": language,
                    "found": True,
                    "definition": word_info.definition,
                    "etymology": word_info.etymology,
                    "partOfSpeech": word_info.part_of_speech,
                    "pronunciation": word_info.pronunciation,
                    "examples": word_data.get("examples", []),
                    "source": word_info.source,
                    "confidence": word_info.confidence
                }
                
            except Exception as e:
                print(f"OpenAI lookup failed for {language} word '{word}': {e}")
                # Fall through to basic response
        
        # If OpenAI fails or is not available, provide a basic response and cache it
        basic_definition = f"Foreign word from {language}: {word}"
        
        from backend.app.services.enhanced_dictionary import WordInfo
        basic_info = WordInfo(
            latin=word,
            definition=basic_definition,
            etymology="",
            part_of_speech="unknown",
            morphology="",
            pronunciation="",
            source=f"basic_{language}_fallback",
            confidence=0.3
        )
        
        # Save basic info to cache so we don't keep trying
        enhanced_dict.save_to_cache(basic_info, language)
        
        return {
            "word": word,
            "language": language,
            "found": True,
            "definition": basic_definition,
            "etymology": "",
            "partOfSpeech": "unknown",
            "pronunciation": "",
            "examples": [],
            "source": basic_info.source,
            "confidence": 0.3,
            "note": "Basic fallback definition - word added to dictionary for future enhancement"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Translation word lookup failed: {error_msg}") 
