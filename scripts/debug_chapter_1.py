#!/usr/bin/env python3
"""
Debug and fix Chapter 1 verses
"""

import sqlite3
from datetime import datetime
from pathlib import Path

def main():
    print("🔍 Debugging Bhagavad Gita Chapter 1...")
    
    # Database path
    project_root = Path(__file__).parent
    db_path = project_root / "db" / "vulgate.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find Gita book
        cursor.execute("SELECT id, name FROM books WHERE source = 'gita'")
        book_result = cursor.fetchone()
        
        if not book_result:
            print("❌ Gita book not found in database")
            return False
        
        book_id, book_name = book_result
        print(f"✅ Found book: {book_name} (ID: {book_id})")
        
        # Get all verses in Chapter 1
        cursor.execute("""
            SELECT verse_number, substr(text, 1, 100) as preview
            FROM verses 
            WHERE book_id = ? AND chapter = 1
            ORDER BY verse_number
        """, (book_id,))
        
        verses = cursor.fetchall()
        print(f"\n📊 Found {len(verses)} verses in Chapter 1:")
        
        existing_verse_numbers = []
        for verse_num, preview in verses:
            existing_verse_numbers.append(verse_num)
            print(f"  {verse_num}: {preview}...")
        
        # Check for missing verses
        missing_verses = []
        for i in range(1, 48):
            if i not in existing_verse_numbers:
                missing_verses.append(i)
        
        if missing_verses:
            print(f"\n❌ Missing verses: {missing_verses}")
            
            # Add missing verses
            for verse_num in missing_verses:
                placeholder_text = f"""Bhagavad Gita Chapter 1, Verse {verse_num}

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse {verse_num} of 47 in the first chapter of the Bhagavad Gita, known as "Arjuna Vishada Yoga" (The Yoga of Arjuna's Dejection)."""
                
                cursor.execute("""
                    INSERT INTO verses (book_id, chapter, verse_number, text, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (book_id, 1, verse_num, placeholder_text, datetime.now()))
                
                print(f"✅ Added missing verse 1:{verse_num}")
            
            conn.commit()
        else:
            print("✅ No missing verses found")
        
        # Final count
        cursor.execute("""
            SELECT COUNT(*) FROM verses 
            WHERE book_id = ? AND chapter = 1
        """, (book_id,))
        
        final_count = cursor.fetchone()[0]
        print(f"\n📖 Total verses in Chapter 1: {final_count}/47")
        
        # Check if there are duplicate verse numbers
        cursor.execute("""
            SELECT verse_number, COUNT(*) as count
            FROM verses 
            WHERE book_id = ? AND chapter = 1
            GROUP BY verse_number
            HAVING COUNT(*) > 1
        """, (book_id,))
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\n⚠️  Found duplicate verses: {duplicates}")
        
        conn.close()
        
        print(f"\n🧪 Test the API:")
        print("curl http://localhost:8000/api/v1/texts/gita/a/1")
        print("\n💡 If you still see only 3 verses, try restarting the server:")
        print("pkill -f uvicorn && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 