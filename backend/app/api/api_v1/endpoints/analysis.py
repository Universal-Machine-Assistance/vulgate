from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional, List, Dict, Any
import os
import sys
import json
import uuid
from datetime import datetime

# Add the project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(project_root)

from vulgate_analyzer import VulgateAnalyzer, VerseAnalysisResult
from backend.app.models import AnalysisHistory, EditSession, FieldEdit, AnalysisQueue
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db

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

async def log_analysis_history(
    db: Session,
    verse_id: int,
    action_type: str,
    target_field: str,
    old_value: str = None,
    new_value: str = None,
    change_source: str = "user",
    target_identifier: str = None,
    user_id: int = None,
    extra_data: Dict[str, Any] = None,
    confidence_score: float = None
):
    """Log an entry to the analysis history table"""
    history_entry = AnalysisHistory(
        verse_id=verse_id,
        action_type=action_type,
        target_field=target_field,
        target_identifier=target_identifier,
        old_value=old_value,
        new_value=new_value,
        change_source=change_source,
        user_id=user_id,
        extra_data=extra_data,
        confidence_score=confidence_score
    )
    db.add(history_entry)
    db.commit()
    return history_entry

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

        # Check if this verse was already analyzed
        existing = await get_verse_analysis(book, chapter, verse)
        if existing.get("found"):
            return {
                "message": f"Analysis retrieved from cache for {book} {chapter}:{verse}",
                "status": "cached",
                **existing,
            }

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

@router.put("/grammar/edit")
async def edit_grammar_breakdown(
    book: str,
    chapter: int,
    verse: int,
    word: str,
    meaning: str,
    grammar_description: str,
    part_of_speech: Optional[str] = None,
    morphology: Optional[str] = None
):
    """
    Edit grammar breakdown for a specific word in a verse
    """
    try:
        analyzer = get_analyzer()
        
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        # Get verse analysis ID
        cursor.execute('''
            SELECT id FROM verse_analyses 
            WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
        ''', (book, chapter, verse))
        
        verse_row = cursor.fetchone()
        if not verse_row:
            raise HTTPException(status_code=404, detail="Verse analysis not found")
        
        verse_analysis_id = verse_row[0]
        
        # Update grammar breakdown
        update_query = '''
            UPDATE grammar_breakdowns 
            SET meaning = ?, grammar_description = ?, part_of_speech = ?, 
                morphology = ?, source = 'manual'
            WHERE verse_analysis_id = ? AND word = ?
        '''
        
        cursor.execute(update_query, (
            meaning, grammar_description, part_of_speech, 
            morphology, verse_analysis_id, word
        ))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Grammar breakdown not found for this word")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Grammar breakdown for '{word}' updated successfully",
            "word": word,
            "meaning": meaning,
            "grammar_description": grammar_description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit grammar breakdown: {str(e)}")

@router.put("/translation/edit")
async def edit_translation(
    book: str,
    chapter: int,
    verse: int,
    word: str,
    language_code: str,
    meaning: str,
    grammar_description: str
):
    """
    Edit or create translation for a specific word's grammar breakdown
    """
    try:
        analyzer = get_analyzer()
        
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        # Get grammar breakdown ID
        cursor.execute('''
            SELECT gb.id FROM grammar_breakdowns gb
            JOIN verse_analyses va ON gb.verse_analysis_id = va.id
            WHERE va.book_abbreviation = ? AND va.chapter_number = ? 
                AND va.verse_number = ? AND gb.word = ?
        ''', (book, chapter, verse, word))
        
        grammar_row = cursor.fetchone()
        if not grammar_row:
            raise HTTPException(status_code=404, detail="Grammar breakdown not found for this word")
        
        grammar_breakdown_id = grammar_row[0]
        
        # Check if translation already exists
        cursor.execute('''
            SELECT id FROM grammar_translations 
            WHERE grammar_breakdown_id = ? AND language_code = ?
        ''', (grammar_breakdown_id, language_code))
        
        translation_row = cursor.fetchone()
        
        if translation_row:
            # Update existing translation
            cursor.execute('''
                UPDATE grammar_translations 
                SET meaning = ?, grammar_description = ?
                WHERE id = ?
            ''', (meaning, grammar_description, translation_row[0]))
        else:
            # Create new translation
            cursor.execute('''
                INSERT INTO grammar_translations 
                (grammar_breakdown_id, language_code, meaning, grammar_description)
                VALUES (?, ?, ?, ?)
            ''', (grammar_breakdown_id, language_code, meaning, grammar_description))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Translation for '{word}' in {language_code} updated successfully",
            "word": word,
            "language_code": language_code,
            "meaning": meaning,
            "grammar_description": grammar_description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit translation: {str(e)}")

@router.get("/queue")
async def get_analysis_queue():
    """
    Get list of verses in analysis queue/recent activity
    """
    try:
        analyzer = get_analyzer()
        
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        # Get recent analyses (last 20 processed)
        cursor.execute('''
            SELECT book_abbreviation, chapter_number, verse_number,
                   grammar_analyzed, theological_analyzed, symbolic_analyzed, 
                   cosmological_analyzed, created_at, updated_at
            FROM verse_analyses 
            ORDER BY updated_at DESC 
            LIMIT 20
        ''')
        
        rows = cursor.fetchall()
        
        queue_items = []
        for row in rows:
            status = "Complete"
            if not row[3]:  # grammar_analyzed
                status = "Pending Grammar"
            elif not row[4]:  # theological_analyzed
                status = "Pending Theological"
            elif not row[5]:  # symbolic_analyzed
                status = "Pending Symbolic"
            elif not row[6]:  # cosmological_analyzed
                status = "Pending Cosmological"
            
            queue_items.append({
                "reference": f"{row[0]} {row[1]}:{row[2]}",
                "book": row[0],
                "chapter": row[1],
                "verse": row[2],
                "status": status,
                "grammar_complete": bool(row[3]),
                "theological_complete": bool(row[4]),
                "symbolic_complete": bool(row[5]),
                "cosmological_complete": bool(row[6]),
                "created_at": row[7],
                "updated_at": row[8]
            })
        
        conn.close()
        
        return {
            "queue_items": queue_items,
            "total_items": len(queue_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis queue: {str(e)}")

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

<<<<<<< HEAD
@router.get("/queue")
async def get_analysis_queue(limit: int = 100):
    """Return a simple queue of verses that have been analyzed recently or still pending completion.
    This is a lightweight implementation that lists the latest verse_analyses rows ordered by
    updated_at descending.  The frontend mainly needs the structure – refine later as needed."""
    try:
=======
# History Tracking Endpoints

@router.get("/history/{book}/{chapter}/{verse}")
async def get_verse_history(
    book: str, 
    chapter: int, 
    verse: int,
    db: Session = Depends(get_db)
):
    """Get complete history for a specific verse"""
    try:
        # First get the verse ID from the main database
>>>>>>> be9be0b69f7bdd421411eb30642a61ef0b751ec0
        analyzer = get_analyzer()
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
<<<<<<< HEAD

        cursor.execute(
            '''SELECT book_abbreviation, chapter_number, verse_number, 
                      grammar_analyzed, theological_analyzed, symbolic_analyzed, cosmological_analyzed, 
                      created_at, updated_at
               FROM verse_analyses
               ORDER BY updated_at DESC
               LIMIT ?''',
            (limit,)
        )

        rows = cursor.fetchall()
        queue_items = []
        for row in rows:
            book, chapter, verse, grammar_done, theo_done, symb_done, cosmo_done, created, updated = row
            status = "complete" if all([grammar_done, theo_done, symb_done, cosmo_done]) else "pending"
            queue_items.append({
                "reference": f"{book} {chapter}:{verse}",
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "status": status,
                "grammar_complete": bool(grammar_done),
                "theological_complete": bool(theo_done),
                "symbolic_complete": bool(symb_done),
                "cosmological_complete": bool(cosmo_done),
                "created_at": created,
                "updated_at": updated
            })
        conn.close()

        return {"queue_items": queue_items, "count": len(queue_items)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue: {str(e)}")


@router.get("/history/{book}/{chapter}/{verse}")
async def get_analysis_history(book: str, chapter: int, verse: int):
    """Placeholder endpoint for analysis change history.  Returns empty history for now so the
    frontend can render gracefully instead of receiving 404 errors.  Extend in the future to
    pull real audit data once it is being captured."""
    return {"found": False, "history": []} 
=======
        
        cursor.execute('''
            SELECT id FROM verse_analyses 
            WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
        ''', (book, chapter, verse))
        
        verse_row = cursor.fetchone()
        if not verse_row:
            return {"found": False, "history": []}
        
        verse_analysis_id = verse_row[0]
        conn.close()
        
        # Get history from the new database
        history_entries = db.query(AnalysisHistory).filter(
            AnalysisHistory.verse_id == verse_analysis_id
        ).order_by(AnalysisHistory.created_at.desc()).all()
        
        history_data = []
        for entry in history_entries:
            history_data.append({
                "id": entry.id,
                "action_type": entry.action_type,
                "target_field": entry.target_field,
                "target_identifier": entry.target_identifier,
                "old_value": entry.old_value,
                "new_value": entry.new_value,
                "change_source": entry.change_source,
                "created_at": entry.created_at,
                "confidence_score": entry.confidence_score,
                "review_status": entry.review_status,
                "extra_data": entry.extra_data
            })
        
        return {
            "found": True,
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "history": history_data,
            "total_changes": len(history_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get verse history: {str(e)}")

@router.get("/history/recent")
async def get_recent_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent history across all verses"""
    try:
        recent_entries = db.query(AnalysisHistory).order_by(
            AnalysisHistory.created_at.desc()
        ).limit(limit).all()
        
        history_data = []
        for entry in recent_entries:
            history_data.append({
                "id": entry.id,
                "verse_id": entry.verse_id,
                "action_type": entry.action_type,
                "target_field": entry.target_field,
                "target_identifier": entry.target_identifier,
                "change_source": entry.change_source,
                "created_at": entry.created_at,
                "confidence_score": entry.confidence_score,
                "review_status": entry.review_status
            })
        
        return {
            "history": history_data,
            "total_entries": len(history_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent history: {str(e)}")

# Global Edit Mode Endpoints

@router.post("/edit/session/create")
async def create_edit_session(
    book: str,
    chapter: int,
    verse: int,
    db: Session = Depends(get_db)
):
    """Create a new global edit session for a verse"""
    try:
        # Get verse data from main database
        analyzer = get_analyzer()
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, latin_text FROM verse_analyses 
            WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
        ''', (book, chapter, verse))
        
        verse_row = cursor.fetchone()
        if not verse_row:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        verse_analysis_id, verse_text = verse_row
        
        # Get grammar breakdown
        cursor.execute('''
            SELECT word, meaning, grammar_description, part_of_speech, morphology
            FROM grammar_breakdowns 
            WHERE verse_analysis_id = ?
            ORDER BY word_index
        ''', (verse_analysis_id,))
        
        grammar_rows = cursor.fetchall()
        
        # Get interpretation layers
        cursor.execute('''
            SELECT layer_type, title, points
            FROM interpretation_layers 
            WHERE verse_analysis_id = ?
        ''', (verse_analysis_id,))
        
        layer_rows = cursor.fetchall()
        conn.close()
        
        # Create edit session
        session_token = str(uuid.uuid4())
        
        # Build session data
        session_data = {
            "verse_text": verse_text,
            "grammar_breakdown": [
                {
                    "word": row[0],
                    "meaning": row[1],
                    "grammar_description": row[2],
                    "part_of_speech": row[3],
                    "morphology": row[4]
                }
                for row in grammar_rows
            ],
            "interpretation_layers": [
                {
                    "layer_type": row[0],
                    "title": row[1],
                    "points": json.loads(row[2])
                }
                for row in layer_rows
            ]
        }
        
        edit_session = EditSession(
            verse_id=verse_analysis_id,
            session_token=session_token,
            session_data=session_data
        )
        
        db.add(edit_session)
        db.commit()
        
        # Create field edits for each editable element
        field_edits = []
        
        # Verse text
        verse_edit = FieldEdit(
            edit_session_id=edit_session.id,
            field_type="verse_text",
            field_identifier="main",
            current_value=verse_text
        )
        field_edits.append(verse_edit)
        
        # Grammar breakdown fields
        for i, grammar_item in enumerate(session_data["grammar_breakdown"]):
            word_edit = FieldEdit(
                edit_session_id=edit_session.id,
                field_type="word_definition",
                field_identifier=f"{grammar_item['word']}_{i}",
                current_value=grammar_item["meaning"]
            )
            field_edits.append(word_edit)
            
            grammar_edit = FieldEdit(
                edit_session_id=edit_session.id,
                field_type="grammar_description",
                field_identifier=f"{grammar_item['word']}_{i}",
                current_value=grammar_item["grammar_description"]
            )
            field_edits.append(grammar_edit)
        
        # Interpretation layers
        for layer in session_data["interpretation_layers"]:
            for i, point in enumerate(layer["points"]):
                point_edit = FieldEdit(
                    edit_session_id=edit_session.id,
                    field_type="theological_point",
                    field_identifier=f"{layer['layer_type']}_{i}",
                    current_value=point
                )
                field_edits.append(point_edit)
        
        db.add_all(field_edits)
        db.commit()
        
        return {
            "session_token": session_token,
            "session_id": edit_session.id,
            "verse_data": session_data,
            "editable_fields": len(field_edits)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create edit session: {str(e)}")

@router.get("/edit/session/{session_token}")
async def get_edit_session(
    session_token: str,
    db: Session = Depends(get_db)
):
    """Get edit session data"""
    try:
        edit_session = db.query(EditSession).filter(
            EditSession.session_token == session_token,
            EditSession.is_active == True
        ).first()
        
        if not edit_session:
            raise HTTPException(status_code=404, detail="Edit session not found")
        
        field_edits = db.query(FieldEdit).filter(
            FieldEdit.edit_session_id == edit_session.id
        ).all()
        
        fields_data = []
        for field in field_edits:
            fields_data.append({
                "id": field.id,
                "field_type": field.field_type,
                "field_identifier": field.field_identifier,
                "current_value": field.current_value,
                "is_modified": field.is_modified,
                "ai_suggested_value": field.ai_suggested_value,
                "confidence_score": field.confidence_score
            })
        
        return {
            "session_id": edit_session.id,
            "verse_id": edit_session.verse_id,
            "session_data": edit_session.session_data,
            "fields": fields_data,
            "created_at": edit_session.created_at,
            "updated_at": edit_session.updated_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get edit session: {str(e)}")

@router.put("/edit/field/{field_id}")
async def update_field(
    field_id: int,
    new_value: str,
    db: Session = Depends(get_db)
):
    """Update a specific field in an edit session"""
    try:
        field_edit = db.query(FieldEdit).filter(FieldEdit.id == field_id).first()
        
        if not field_edit:
            raise HTTPException(status_code=404, detail="Field not found")
        
        old_value = field_edit.current_value
        field_edit.current_value = new_value
        field_edit.is_modified = True
        field_edit.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log the change
        await log_analysis_history(
            db=db,
            verse_id=field_edit.edit_session.verse_id,
            action_type="edit",
            target_field=field_edit.field_type,
            target_identifier=field_edit.field_identifier,
            old_value=old_value,
            new_value=new_value,
            change_source="user"
        )
        
        return {
            "success": True,
            "field_id": field_id,
            "old_value": old_value,
            "new_value": new_value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update field: {str(e)}")

@router.post("/edit/field/{field_id}/ai-suggest")
async def get_ai_suggestion(
    field_id: int,
    context: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate AI suggestion for a field"""
    try:
        field_edit = db.query(FieldEdit).filter(FieldEdit.id == field_id).first()
        
        if not field_edit:
            raise HTTPException(status_code=404, detail="Field not found")
        
        analyzer = get_analyzer()
        
        # Generate AI suggestion based on field type
        if field_edit.field_type == "word_definition":
            word = field_edit.field_identifier.split('_')[0]
            # Use existing Greb AI functionality
            ai_response = await analyzer.get_greb_ai_definition(word, context or "")
            suggested_value = ai_response.get("definition", field_edit.current_value)
            confidence = ai_response.get("confidence", 0.5)
        elif field_edit.field_type == "theological_point":
            # Generate theological interpretation
            suggested_value = f"AI theological insight for {field_edit.field_identifier}"
            confidence = 0.7
        else:
            suggested_value = field_edit.current_value
            confidence = 0.5
        
        field_edit.ai_suggested_value = suggested_value
        field_edit.confidence_score = confidence
        
        db.commit()
        
        return {
            "field_id": field_id,
            "suggested_value": suggested_value,
            "confidence_score": confidence,
            "current_value": field_edit.current_value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI suggestion: {str(e)}")

@router.post("/edit/session/{session_token}/save")
async def save_edit_session(
    session_token: str,
    db: Session = Depends(get_db)
):
    """Save all changes from an edit session back to the main database"""
    try:
        edit_session = db.query(EditSession).filter(
            EditSession.session_token == session_token,
            EditSession.is_active == True
        ).first()
        
        if not edit_session:
            raise HTTPException(status_code=404, detail="Edit session not found")
        
        # Get all modified fields
        modified_fields = db.query(FieldEdit).filter(
            FieldEdit.edit_session_id == edit_session.id,
            FieldEdit.is_modified == True
        ).all()
        
        if not modified_fields:
            return {"message": "No changes to save", "changes_applied": 0}
        
        # Apply changes to main database
        analyzer = get_analyzer()
        import sqlite3
        conn = sqlite3.connect(analyzer.database_path)
        cursor = conn.cursor()
        
        changes_applied = 0
        
        for field in modified_fields:
            if field.field_type == "verse_text":
                cursor.execute('''
                    UPDATE verse_analyses 
                    SET latin_text = ? 
                    WHERE id = ?
                ''', (field.current_value, edit_session.verse_id))
                changes_applied += 1
                
            elif field.field_type == "word_definition":
                word = field.field_identifier.split('_')[0]
                cursor.execute('''
                    UPDATE grammar_breakdowns 
                    SET meaning = ?, source = 'manual'
                    WHERE verse_analysis_id = ? AND word = ?
                ''', (field.current_value, edit_session.verse_id, word))
                changes_applied += 1
                
            elif field.field_type == "grammar_description":
                word = field.field_identifier.split('_')[0]
                cursor.execute('''
                    UPDATE grammar_breakdowns 
                    SET grammar_description = ?, source = 'manual'
                    WHERE verse_analysis_id = ? AND word = ?
                ''', (field.current_value, edit_session.verse_id, word))
                changes_applied += 1
                
            elif field.field_type == "theological_point":
                # Handle theological layer updates
                layer_info = field.field_identifier.split('_')
                layer_type = layer_info[0]
                point_index = int(layer_info[1])
                
                # Get current points
                cursor.execute('''
                    SELECT points FROM interpretation_layers 
                    WHERE verse_analysis_id = ? AND layer_type = ?
                ''', (edit_session.verse_id, layer_type))
                
                row = cursor.fetchone()
                if row:
                    points = json.loads(row[0])
                    if point_index < len(points):
                        points[point_index] = field.current_value
                        
                        cursor.execute('''
                            UPDATE interpretation_layers 
                            SET points = ?
                            WHERE verse_analysis_id = ? AND layer_type = ?
                        ''', (json.dumps(points), edit_session.verse_id, layer_type))
                        changes_applied += 1
        
        conn.commit()
        conn.close()
        
        # Mark session as inactive
        edit_session.is_active = False
        db.commit()
        
        # Log the save action
        await log_analysis_history(
            db=db,
            verse_id=edit_session.verse_id,
            action_type="edit_session_save",
            target_field="multiple",
            new_value=f"Applied {changes_applied} changes",
            change_source="user",
            extra_data={"session_token": session_token, "changes_count": changes_applied}
        )
        
        return {
            "success": True,
            "changes_applied": changes_applied,
            "session_closed": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save edit session: {str(e)}")

# Enhanced Queue Management

@router.get("/queue/enhanced")
async def get_enhanced_queue(
    db: Session = Depends(get_db)
):
    """Get enhanced analysis queue with history tracking"""
    try:
        queue_items = db.query(AnalysisQueue).order_by(
            AnalysisQueue.priority.desc(),
            AnalysisQueue.created_at.desc()
        ).all()
        
        queue_data = []
        for item in queue_items:
            queue_data.append({
                "id": item.id,
                "verse_id": item.verse_id,
                "priority": item.priority,
                "analysis_type": item.analysis_type,
                "request_source": item.request_source,
                "status": item.status,
                "created_at": item.created_at,
                "started_at": item.started_at,
                "completed_at": item.completed_at,
                "error_message": item.error_message,
                "extra_data": item.extra_data
            })
        
        return {
            "queue_items": queue_data,
            "total_items": len(queue_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced queue: {str(e)}")

@router.post("/queue/add")
async def add_to_queue(
    verse_id: int,
    analysis_type: str = "complete",
    priority: int = 0,
    request_source: str = "user",
    extra_data: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Add a verse to the analysis queue"""
    try:
        queue_item = AnalysisQueue(
            verse_id=verse_id,
            priority=priority,
            analysis_type=analysis_type,
            request_source=request_source,
            extra_data=extra_data
        )
        
        db.add(queue_item)
        db.commit()
        
        return {
            "success": True,
            "queue_id": queue_item.id,
            "message": f"Added verse {verse_id} to {analysis_type} analysis queue"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to queue: {str(e)}") 
>>>>>>> be9be0b69f7bdd421411eb30642a61ef0b751ec0
