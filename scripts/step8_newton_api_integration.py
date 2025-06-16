#!/usr/bin/env python3
"""
Step 8: Add Newton API integration.
Updates backend routes to handle Newton book requests.
"""

import os
from pathlib import Path

def find_backend_files():
    """Locate backend API files."""
    backend_files = []
    
    # Common backend locations
    for pattern in ["app/*.py", "backend/*.py", "*.py"]:
        if pattern == "*.py":
            # Check root level Python files that might be APIs
            for f in Path(".").glob(pattern):
                if any(term in f.name.lower() for term in ['app', 'main', 'api', 'run']):
                    backend_files.append(f)
        else:
            backend_files.extend(Path(".").glob(pattern))
    
    return [f for f in backend_files if f.is_file() and f.stat().st_size > 100]

def update_api_routes():
    """Add Newton support to API routes."""
    backend_files = find_backend_files()
    
    if not backend_files:
        print("ℹ️  No backend files found. Creating basic API snippet...")
        create_newton_api_snippet()
        return
    
    for file_path in backend_files:
        print(f"🔄 Checking {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for Flask routes or similar API patterns
            if ('route(' in content or '@app.' in content or 'fastapi' in content.lower()) and 'newton' not in content.lower():
                print(f"   📝 Adding Newton support to {file_path}")
                
                # Add Newton book mapping if not present
                newton_mapping = '''
# Newton book mapping
NEWTON_CHAPTERS = {
    0: "Title Page",
    1: "Præfatio",
    2: "Poetry & Dedication", 
    3: "Definitiones"
}

def format_newton_reference(chapter, verse):
    """Format Newton reference for display."""
    chapter_name = NEWTON_CHAPTERS.get(chapter, f"Chapter {chapter}")
    return f"Newton {chapter}:{verse} ({chapter_name})"
'''
                
                # Insert Newton mapping near other book mappings or imports
                if 'from flask import' in content or 'import flask' in content:
                    # Find a good insertion point after imports
                    lines = content.split('\n')
                    insert_idx = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('from ') or line.strip().startswith('import '):
                            insert_idx = i + 1
                    
                    lines.insert(insert_idx, newton_mapping)
                    content = '\n'.join(lines)
                
                # Add Newton case to book routing if pattern is found
                if 'elif book ==' in content or 'if book ==' in content:
                    # Find book routing section and add Newton
                    gita_pattern = "book == 'gita'"
                    newton_case = '''elif book == 'newton':
        # Handle Newton Principia requests
        book_name = "Newton - Principia"
        chapter_name = NEWTON_CHAPTERS.get(int(chapter), f"Chapter {chapter}")'''
                    
                    if gita_pattern in content and 'newton' not in content:
                        content = content.replace(gita_pattern, gita_pattern + '\n    ' + newton_case)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ Updated {file_path}")
                
        except Exception as e:
            print(f"   ⚠️  Error updating {file_path}: {e}")

def create_newton_api_snippet():
    """Create a Newton API integration snippet."""
    snippet = '''# Newton API Integration Snippet
# Add this to your main API file

from flask import Flask, jsonify, request
import sqlite3

# Newton chapter mapping
NEWTON_CHAPTERS = {
    0: "Title Page",
    1: "Præfatio", 
    2: "Poetry & Dedication",
    3: "Definitiones"
}

@app.route('/api/v1/books/newton/chapters')
def newton_chapters():
    """Get Newton chapters list."""
    return jsonify({
        "book": "newton",
        "name": "Philosophiae Naturalis Principia Mathematica",
        "chapters": [
            {"number": k, "name": v, "verse_count": get_newton_verse_count(k)}
            for k, v in NEWTON_CHAPTERS.items()
        ]
    })

@app.route('/api/v1/books/newton/<int:chapter>/<int:verse>')
def get_newton_verse(chapter, verse):
    """Get specific Newton verse."""
    conn = sqlite3.connect('db/vulgate.db')
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

def get_newton_verse_count(chapter):
    """Get verse count for Newton chapter."""
    conn = sqlite3.connect('db/vulgate.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM verses v
        JOIN books b ON v.book_id = b.id
        WHERE b.source = 'newton' AND v.chapter = ?
    """, (chapter,))
    count = cur.fetchone()[0]
    conn.close()
    return count
'''
    
    with open("newton_api_snippet.py", "w", encoding="utf-8") as f:
        f.write(snippet)
    print("✅ Created newton_api_snippet.py")

if __name__ == "__main__":
    update_api_routes() 