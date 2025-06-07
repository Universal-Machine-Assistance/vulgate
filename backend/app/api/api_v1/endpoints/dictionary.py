from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Optional
import os
import sys
import time
import asyncio
from functools import wraps
import sqlite3

# Add the project root to path so we can import enhanced_dictionary
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(project_root)

from backend.app.services.enhanced_dictionary import EnhancedDictionary  # noqa
WordInfo = None  # Placeholder to avoid unresolved import

router = APIRouter()

# Rate limiting state
last_openai_call = 0
min_time_between_calls = 1.0  # Minimum 1 second between OpenAI API calls

# Determine analysis DB path relative to project root
ANALYSIS_DB_PATH = os.path.join(project_root, "vulgate_analysis.db")

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
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            print(f"Rate limit hit on attempt {attempt + 1}, retrying in {delay}s...")
                            if asyncio.iscoroutinefunction(func):
                                await asyncio.sleep(delay)
                            else:
                                time.sleep(delay)
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
                    "jungian_layer": cached_analysis.get("jungian_layer", []),
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
            "jungian_layer": analysis_data.get("jungian_layer", []),
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
    Translate a Latin verse to a target language
    """
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        target_language = data.get("language", "en").strip()

        # Input validation
        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")
        
        if len(verse_text) > 1000:  # Reasonable limit for a verse
            raise HTTPException(status_code=400, detail="Verse text is too long")

        # Get dictionary instance
        enhanced_dict = get_enhanced_dictionary(request)
        
        # Translate the verse
        translation = enhanced_dict.translate_verse(verse_text, target_language)
        
        # Check if translation was successful
        if translation.startswith("Translation to") and ("failed" in translation or "not available" in translation):
            return {
                "success": False,
                "error": translation,
                "verse": verse_text,
                "language": target_language
            }
        
        return {
            "success": True,
            "translation": translation,
            "verse": verse_text,
            "language": target_language
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        error_msg = str(e)
        print(f"Error in translate endpoint: {e}")
        if "rate limit" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="Translation quota exceeded. Please try again later.")
        raise HTTPException(status_code=500, detail=f"Translation failed: {error_msg}")

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
    """Direct call to Greb AI verse analysis (no cache). Mirrors /analyze/verse but returns full layers.
    This endpoint exists solely to satisfy the current frontend expectations."""
    try:
        data = await request.json()
        verse_text = data.get("verse", "").strip()
        verse_reference = data.get("reference", "").strip()

        if not verse_text:
            raise HTTPException(status_code=400, detail="Verse text is required")

        dictionary = get_enhanced_dictionary(request)
        if not dictionary.openai_enabled:
            raise HTTPException(status_code=503, detail="Greb AI not enabled")

        # Always call OpenAI – skip cache and force enhanced analysis
        rate_limit_openai()
        analysis_data = dictionary.analyze_verse_with_openai(verse_text, verse_reference)

        if not analysis_data.get("success", False):
            raise HTTPException(status_code=500, detail=analysis_data.get("error", "Analysis failed"))

        return analysis_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 