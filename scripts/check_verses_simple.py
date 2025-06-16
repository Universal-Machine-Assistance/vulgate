#!/usr/bin/env python3

import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / "db" / "vulgate.db"

print(f"Checking database: {db_path}")

try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get Gita book ID
    cursor.execute("SELECT id FROM books WHERE source = 'gita'")
    book_result = cursor.fetchone()
    
    if not book_result:
        print("ERROR: Gita book not found!")
        exit(1)
    
    book_id = book_result[0]
    print(f"Gita book ID: {book_id}")
    
    # Count verses in Chapter 1
    cursor.execute("SELECT COUNT(*) FROM verses WHERE book_id = ? AND chapter = 1", (book_id,))
    count = cursor.fetchone()[0]
    print(f"Current verses in Chapter 1: {count}")
    
    # Get all verse numbers
    cursor.execute("SELECT verse_number FROM verses WHERE book_id = ? AND chapter = 1 ORDER BY verse_number", (book_id,))
    existing_verses = [row[0] for row in cursor.fetchall()]
    print(f"Existing verse numbers: {existing_verses}")
    
    # Find missing verses
    missing = []
    for i in range(1, 48):
        if i not in existing_verses:
            missing.append(i)
    
    if missing:
        print(f"Missing verses: {missing}")
        
        # Add missing verses
        for verse_num in missing:
            text = f"Bhagavad Gita Chapter 1, Verse {verse_num}\n\n[Sanskrit text to be added]\n[Transliteration to be added]\n[Translation to be added]\n\nThis is verse {verse_num} of 47 in the first chapter."
            
            cursor.execute("""
                INSERT INTO verses (book_id, chapter, verse_number, text, created_at)
                VALUES (?, 1, ?, ?, datetime('now'))
            """, (book_id, verse_num, text))
            print(f"Added verse {verse_num}")
        
        conn.commit()
        print("All missing verses added!")
    else:
        print("All 47 verses are present!")
    
    # Final count
    cursor.execute("SELECT COUNT(*) FROM verses WHERE book_id = ? AND chapter = 1", (book_id,))
    final_count = cursor.fetchone()[0]
    print(f"Final count: {final_count}/47")
    
    conn.close()
    
    print("\nNow restart the server:")
    print("pkill -f uvicorn && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"Error: {e}") 