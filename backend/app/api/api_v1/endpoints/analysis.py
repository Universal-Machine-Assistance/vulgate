from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
import os
import sys
import json

# Add the project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(project_root)

from vulgate_analyzer import VulgateAnalyzer, VerseAnalysisResult

router = APIRouter()

# Initialize the analyzer (singleton pattern)
_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        database_path = os.path.join(project_root, "vulgate_analysis.db")
        
        print(f"Analysis DB path: {database_path}")
        print(f"Project root: {project_root}")
        
        _analyzer = VulgateAnalyzer(
            openai_api_key=openai_api_key,
            database_path=database_path
        )
    return _analyzer

@router.post("/analyze/verse")
async def analyze_verse(
    book: str,
    chapter: int, 
    verse: int,
    verse_text: str,
    background_tasks: BackgroundTasks
):
    """
    Analyze a single verse completely (grammar + interpretations)
    """
    try:
        analyzer = get_analyzer()
        
        # Run analysis in background to avoid timeout
        def run_analysis():
            result = analyzer.analyze_verse_complete(book, chapter, verse, verse_text)
            print(f"Completed analysis for {book} {chapter}:{verse}")
        
        background_tasks.add_task(run_analysis)
        
        return {
            "message": f"Analysis started for {book} {chapter}:{verse}",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/verse/{book}/{chapter}/{verse}")
async def get_verse_analysis(book: str, chapter: int, verse: int, language: str = "en"):
    """
    Get analysis results for a specific verse in the requested language
    """
    try:
        analyzer = get_analyzer()
        
        # Get analysis from database
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        # Get verse analysis
        cursor.execute('''
            SELECT * FROM verse_analyses 
            WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
        ''', (book, chapter, verse))
        
        verse_row = cursor.fetchone()
        if not verse_row:
            return {"found": False, "message": "Verse analysis not found"}
        
        verse_analysis_id = verse_row[0]
        
        # Get grammar breakdown
        cursor.execute('''
            SELECT word, word_index, meaning, grammar_description, part_of_speech, 
                   morphology, fontawesome_icon, color_class, confidence, source
            FROM grammar_breakdowns 
            WHERE verse_analysis_id = ?
            ORDER BY word_index
        ''', (verse_analysis_id,))
        
        grammar_rows = cursor.fetchall()
        grammar_breakdown = []
        
        for row in grammar_rows:
            grammar_breakdown.append({
                "word": row[0],
                "word_index": row[1],
                "meaning": row[2],
                "grammar_description": row[3],
                "part_of_speech": row[4],
                "morphology": row[5],
                "icon": row[6],
                "color": row[7],
                "confidence": row[8],
                "source": row[9]
            })
        
        # Get interpretation layers
        cursor.execute('''
            SELECT layer_type, title, points, fontawesome_icon, color_gradient, confidence
            FROM interpretation_layers 
            WHERE verse_analysis_id = ?
        ''', (verse_analysis_id,))
        
        layer_rows = cursor.fetchall()
        interpretations = []
        
        for row in layer_rows:
            interpretations.append({
                "layer_type": row[0],
                "title": row[1],
                "points": json.loads(row[2]),
                "icon": row[3],
                "color_gradient": row[4],
                "confidence": row[5]
            })
        
        conn.close()
        
        return {
            "found": True,
            "book": verse_row[1],
            "chapter": verse_row[2],
            "verse": verse_row[3],
            "latin_text": verse_row[4],
            "grammar_analyzed": bool(verse_row[5]),
            "theological_analyzed": bool(verse_row[6]),
            "symbolic_analyzed": bool(verse_row[7]),
            "cosmological_analyzed": bool(verse_row[8]),
            "grammar_breakdown": grammar_breakdown,
            "interpretations": interpretations,
            "language": language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get verse analysis: {str(e)}")

@router.get("/progress")
async def get_analysis_progress():
    """
    Get overall analysis progress for the entire Vulgate
    """
    try:
        analyzer = get_analyzer()
        progress = analyzer.get_analysis_progress()
        
        return progress
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@router.get("/stats")
async def get_analysis_stats():
    """
    Get detailed analysis statistics
    """
    try:
        analyzer = get_analyzer()
        
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        # Get counts by analysis type
        cursor.execute('SELECT COUNT(*) FROM verse_analyses')
        total_verses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE grammar_analyzed = TRUE')
        grammar_complete = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE theological_analyzed = TRUE')
        theological_complete = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE symbolic_analyzed = TRUE')
        symbolic_complete = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM verse_analyses WHERE cosmological_analyzed = TRUE')
        cosmological_complete = cursor.fetchone()[0]
        
        # Get word counts
        cursor.execute('SELECT COUNT(DISTINCT word) FROM grammar_breakdowns')
        analyzed_words = cursor.fetchone()[0]
        
        conn.close()
        
        # Estimate totals
        total_verses_estimate = 31000
        total_words_estimate = 783000  # Approximate word count in Vulgate
        
        return {
            "verse_analysis": {
                "total_verses_estimate": total_verses_estimate,
                "analyzed_verses": total_verses,
                "grammar_complete": grammar_complete,
                "theological_complete": theological_complete,
                "symbolic_complete": symbolic_complete,
                "cosmological_complete": cosmological_complete,
                "completion_percentage": round((total_verses / total_verses_estimate) * 100, 2) if total_verses_estimate > 0 else 0
            },
            "word_analysis": {
                "total_words_estimate": total_words_estimate,
                "analyzed_words": analyzed_words,
                "completion_percentage": round((analyzed_words / total_words_estimate) * 100, 2) if total_words_estimate > 0 else 0
            },
            "remaining_work": {
                "verses_to_analyze": max(0, total_verses_estimate - total_verses),
                "words_to_analyze": max(0, total_words_estimate - analyzed_words),
                "grammar_remaining": max(0, total_verses_estimate - grammar_complete),
                "theological_remaining": max(0, total_verses_estimate - theological_complete),
                "symbolic_remaining": max(0, total_verses_estimate - symbolic_complete),
                "cosmological_remaining": max(0, total_verses_estimate - cosmological_complete)
            },
            "openai_enabled": analyzer.openai_enabled
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis stats: {str(e)}")

@router.post("/analyze/batch")
async def analyze_verses_batch(
    verses: List[dict],  # [{"book": "Gn", "chapter": 1, "verse": 1, "text": "..."}]
    background_tasks: BackgroundTasks
):
    """
    Analyze multiple verses in batch
    """
    try:
        analyzer = get_analyzer()
        
        def run_batch_analysis():
            for verse_data in verses:
                try:
                    result = analyzer.analyze_verse_complete(
                        verse_data["book"],
                        verse_data["chapter"], 
                        verse_data["verse"],
                        verse_data["text"]
                    )
                    print(f"Completed batch analysis for {verse_data['book']} {verse_data['chapter']}:{verse_data['verse']}")
                except Exception as e:
                    print(f"Failed to analyze {verse_data['book']} {verse_data['chapter']}:{verse_data['verse']}: {e}")
        
        background_tasks.add_task(run_batch_analysis)
        
        return {
            "message": f"Batch analysis started for {len(verses)} verses",
            "status": "processing",
            "verse_count": len(verses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/languages/supported")
async def get_supported_languages():
    """
    Get list of supported languages for translations
    """
    return {
        "supported_languages": [
            {"code": "en", "name": "English", "flag": "🇺🇸"},
            {"code": "es", "name": "Spanish", "flag": "🇪🇸"},
            {"code": "fr", "name": "French", "flag": "🇫🇷"},
            {"code": "pt", "name": "Portuguese", "flag": "🇵🇹"},
            {"code": "it", "name": "Italian", "flag": "🇮🇹"}
        ],
        "default_language": "en"
    }

@router.get("/health")
async def health_check():
    """
    Health check for the analysis system
    """
    try:
        analyzer = get_analyzer()
        
        return {
            "status": "healthy",
            "openai_enabled": analyzer.openai_enabled,
            "database_connected": True,
            "version": "1.0"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "1.0"
        } 