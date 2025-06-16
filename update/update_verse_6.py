#!/usr/bin/env python3
"""
Update Bhagavad Gita Chapter 1, Verse 6 with correct data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def update_verse_6():
    """Update verse 6 with corrected data from JSON file"""
    
    print("🔧 Updating Bhagavad Gita Chapter 1, Verse 6...")
    
    # Find database
    project_root = Path(__file__).parent
    # Try multiple possible database locations
    possible_db_paths = [
        project_root / "db" / "vulgate.db",
        project_root / "vulgate.db",
        project_root / "backend" / "vulgate.db"
    ]
    
    db_path = None
    for path in possible_db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path or not db_path.exists():
        print(f"❌ Database not found. Tried: {[str(p) for p in possible_db_paths]}")
        return False
    
    print(f"✅ Found database at: {db_path}")
    
    # Load JSON data for verse 6
    json_path = project_root / "gita_verses.json"
    if not json_path.exists():
        print(f"❌ JSON file not found at {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            verses_data = json.load(f)
        
        # Find verse 6
        verse_6 = None
        for verse in verses_data:
            if verse.get('chapter_number') == 1 and verse.get('verse_number') == 6:
                verse_6 = verse
                break
        
        if not verse_6:
            print("❌ Verse 6 not found in JSON data")
            return False
        
        print("✅ Found verse 6 in JSON data")
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find Gita book
        cursor.execute("SELECT id FROM books WHERE source = 'gita' AND name = 'Bhagavad Gita'")
        book_result = cursor.fetchone()
        
        if not book_result:
            print("❌ Gita book not found in database")
            return False
        
        book_id = book_result[0]
        print(f"✅ Found Gita book with ID: {book_id}")
        
        # Format the complete verse text
        formatted_text = f"""Chapter 1, Verse 6

{verse_6['text']}

Transliteration:
{verse_6['transliteration']}

Word Meanings:
{verse_6['word_meanings']}

English Translation:
Yudhamanyu the courageous, Uttamauja the valiant, the son of Subhadra (Abhimanyu), and the sons of Draupadi—all of them are great chariot warriors."""

        # Update the verse in database
        cursor.execute("""
            UPDATE verses 
            SET text = ?, updated_at = ?
            WHERE book_id = ? AND chapter = 1 AND verse_number = 6
        """, (formatted_text, datetime.now(), book_id))
        
        if cursor.rowcount == 0:
            # Insert if doesn't exist
            cursor.execute("""
                INSERT INTO verses (book_id, chapter, verse_number, text, created_at, updated_at)
                VALUES (?, 1, 6, ?, ?, ?)
            """, (book_id, formatted_text, datetime.now(), datetime.now()))
            print("➕ Inserted new verse 6")
        else:
            print("🔄 Updated existing verse 6")
        
        conn.commit()
        
        # Verify the update
        cursor.execute("""
            SELECT text FROM verses 
            WHERE book_id = ? AND chapter = 1 AND verse_number = 6
        """, (book_id,))
        
        result = cursor.fetchone()
        if result:
            print("✅ Verification successful")
            print(f"📝 Updated text preview: {result[0][:200]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating verse 6: {e}")
        return False

if __name__ == "__main__":
    success = update_verse_6()
    if success:
        print("\n🎉 Verse 6 updated successfully!")
        print("🔗 Test it at: http://localhost:8000/api/v1/texts/gita/a/1/6")
    else:
        print("\n❌ Failed to update verse 6") 