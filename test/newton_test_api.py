#!/usr/bin/env python3
"""
Newton Test API - Simple standalone test server
Run with: python3 newton_test_api.py
"""

from flask import Flask, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

NEWTON_CHAPTERS = {
    0: "Title Page",
    1: "Præfatio", 
    2: "Poetry & Dedication",
    3: "Definitiones"
}

def get_db_connection():
    """Get database connection."""
    db_path = Path("db/vulgate.db")
    return sqlite3.connect(str(db_path))

@app.route('/newton/test')
def newton_test():
    """Test Newton data availability."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get Newton book info
    cur.execute("SELECT id, name FROM books WHERE source = 'newton'")
    book = cur.fetchone()
    
    if not book:
        return jsonify({"error": "Newton book not found"}), 404
    
    book_id, book_name = book
    
    # Get chapter summary
    cur.execute("""
        SELECT chapter, COUNT(*) as verse_count
        FROM verses 
        WHERE book_id = ? 
        GROUP BY chapter 
        ORDER BY chapter
    """, (book_id,))
    
    chapters = []
    for chapter, count in cur.fetchall():
        chapters.append({
            "number": chapter,
            "name": NEWTON_CHAPTERS.get(chapter, f"Chapter {chapter}"),
            "verse_count": count
        })
    
    conn.close()
    
    return jsonify({
        "book": book_name,
        "abbreviation": "Newton",
        "source": "newton", 
        "chapters": chapters,
        "total_chapters": len(chapters),
        "status": "active"
    })

@app.route('/newton/<int:chapter>/<int:verse>')
def get_newton_verse(chapter, verse):
    """Get specific Newton verse."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT v.text, v.section_type, b.name
        FROM verses v
        JOIN books b ON v.book_id = b.id
        WHERE b.source = 'newton' AND v.chapter = ? AND v.verse_number = ?
    """, (chapter, verse))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Verse not found"}), 404
    
    return jsonify({
        "reference": f"Newton {chapter}:{verse}",
        "chapter_name": NEWTON_CHAPTERS.get(chapter, f"Chapter {chapter}"),
        "text": row[0],
        "section_type": row[1],
        "book": row[2],
        "source": "newton",
        "language": "latin"
    })

@app.route('/newton/chapters')
def newton_chapters():
    """Get all Newton chapters."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT chapter, COUNT(*) as verse_count
        FROM verses v
        JOIN books b ON v.book_id = b.id
        WHERE b.source = 'newton'
        GROUP BY chapter
        ORDER BY chapter
    """)
    
    chapters = []
    for chapter, count in cur.fetchall():
        chapters.append({
            "number": chapter,
            "name": NEWTON_CHAPTERS.get(chapter, f"Chapter {chapter}"),
            "verse_count": count
        })
    
    conn.close()
    
    return jsonify({
        "book": "Philosophiae Naturalis Principia Mathematica",
        "chapters": chapters
    })

if __name__ == '__main__':
    print("🚀 Starting Newton Test API...")
    print("📖 Test endpoints:")
    print("   GET /newton/test - Overall status")
    print("   GET /newton/chapters - Chapter list") 
    print("   GET /newton/0/1 - Title page")
    print("   GET /newton/1/1 - First preface verse")
    print("   GET /newton/3/1 - First definition")
    app.run(debug=True, port=5001)
