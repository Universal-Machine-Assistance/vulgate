#!/usr/bin/env python3
"""
Step 9: Verify Newton integration and create test endpoint.
"""

import sqlite3
import json
from pathlib import Path

def verify_newton_data():
    """Verify all Newton data is properly structured."""
    print("🔍 Verifying Newton integration...")
    
    # 1. Check database
    db_path = Path("db/vulgate.db")
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    # Check book entry
    cur.execute("SELECT id, name, abbreviation, source FROM books WHERE source = 'newton'")
    book_row = cur.fetchone()
    if not book_row:
        print("❌ Newton book not found in database")
        conn.close()
        return False
    
    book_id, book_name, abbr, source = book_row
    print(f"✅ Newton book found: {book_name} (ID: {book_id}, abbr: {abbr})")
    
    # Check verses by chapter
    cur.execute("""
        SELECT chapter, COUNT(*) as verse_count, 
               GROUP_CONCAT(DISTINCT section_type) as section_types
        FROM verses 
        WHERE book_id = ? 
        GROUP BY chapter 
        ORDER BY chapter
    """, (book_id,))
    
    chapters = cur.fetchall()
    total_verses = 0
    
    print("\n📖 Chapter breakdown:")
    for chapter, count, types in chapters:
        chapter_names = {
            0: "Title Page", 
            1: "Præfatio", 
            2: "Poetry & Dedication", 
            3: "Definitiones"
        }
        chapter_name = chapter_names.get(chapter, f"Chapter {chapter}")
        print(f"   Chapter {chapter} ({chapter_name}): {count} verses ({types})")
        total_verses += count
    
    print(f"📊 Total Newton verses: {total_verses}")
    
    # Test specific verses
    print("\n🧪 Testing specific verses:")
    test_cases = [(0, 1), (1, 1), (2, 1), (3, 1)]
    
    for chapter, verse in test_cases:
        cur.execute("""
            SELECT text, section_type 
            FROM verses 
            WHERE book_id = ? AND chapter = ? AND verse_number = ?
        """, (book_id, chapter, verse))
        
        row = cur.fetchone()
        if row:
            text_preview = row[0][:100] + "..." if len(row[0]) > 100 else row[0]
            print(f"   ✅ Newton {chapter}:{verse} ({row[1]}): {text_preview}")
        else:
            print(f"   ❌ Newton {chapter}:{verse} not found")
    
    conn.close()
    return True

def create_newton_test_api():
    """Create a simple test API endpoint for Newton."""
    test_api = '''#!/usr/bin/env python3
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
'''
    
    with open("newton_test_api.py", "w", encoding="utf-8") as f:
        f.write(test_api)
    print("✅ Created newton_test_api.py")

def create_integration_summary():
    """Create summary of Newton integration."""
    summary = {
        "newton_integration_status": "complete",
        "database": {
            "book_added": True,
            "columns_added": ["page_image", "section_type", "original_language"],
            "verses_structure": {
                "chapter_0": "Title Page (1 verse)",
                "chapter_1": "Præfatio (2 verses)", 
                "chapter_2": "Poetry & Dedication (4 verses)",
                "chapter_3": "Definitiones (3 verses)"
            }
        },
        "frontend": {
            "css_created": "static/css/newton.css",
            "verse_bridge_updated": True,
            "reference_patterns": ["Newton 1:1", "N 3:2", "Pr 0:1"]
        },
        "api": {
            "test_server": "newton_test_api.py",
            "endpoints": [
                "/newton/test",
                "/newton/chapters", 
                "/newton/{chapter}/{verse}"
            ]
        },
        "next_steps": [
            "Add Newton to main FastAPI backend",
            "Update frontend book selection UI",
            "Add Newton verse display styling",
            "Integrate with translation system",
            "Add more Principia content"
        ]
    }
    
    with open("newton_integration_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("✅ Created newton_integration_summary.json")

if __name__ == "__main__":
    if verify_newton_data():
        create_newton_test_api()
        create_integration_summary()
        print("\n🎉 Newton integration verification complete!")
        print("🧪 Run 'python3 newton_test_api.py' to test the API")
    else:
        print("❌ Newton verification failed") 