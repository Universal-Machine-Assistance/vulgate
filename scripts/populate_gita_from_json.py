#!/usr/bin/env python3
"""
Populate Bhagavad Gita database from gita_verses.json file
This will replace placeholder text with actual verse content
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def find_database():
    """Find the database file in common locations"""
    possible_paths = [
        Path("db/vulgate.db"),
        Path("vulgate.db"),
        Path("backend/vulgate.db"),
        Path("../db/vulgate.db"),
        Path("../vulgate.db")
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def format_verse_text(verse_data):
    """Format verse data into readable text"""
    text_parts = []
    
    # Add chapter and verse header
    text_parts.append(f"Bhagavad Gita Chapter {verse_data['chapter_number']}, Verse {verse_data['verse_number']}")
    text_parts.append("")
    
    # Add Sanskrit text
    if verse_data.get('text'):
        text_parts.append("Sanskrit:")
        text_parts.append(verse_data['text'].strip())
        text_parts.append("")
    
    # Add transliteration
    if verse_data.get('transliteration'):
        text_parts.append("Transliteration:")
        text_parts.append(verse_data['transliteration'].strip())
        text_parts.append("")
    
    # Add word meanings
    if verse_data.get('word_meanings'):
        text_parts.append("Word Meanings:")
        text_parts.append(verse_data['word_meanings'].strip())
        text_parts.append("")
    
    # Add basic English translation for known verses
    translations = {
        6: "Yudhamanyu the courageous, Uttamauja the valiant, the son of Subhadra (Abhimanyu), and the sons of Draupadi—all of them are great chariot warriors.",
        1: "Dhritarashtra said: O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?",
        2: "Sanjaya said: On observing the Pandava army standing in military formation, King Duryodhana approached his teacher Dronacharya, and spoke the following words."
    }
    
    if verse_data['verse_number'] in translations:
        text_parts.append("English Translation:")
        text_parts.append(translations[verse_data['verse_number']])
    
    return "\n".join(text_parts)

def main():
    print("📖 Populating Bhagavad Gita database from JSON file...")
    
    # Find database
    db_path = find_database()
    if not db_path:
        print("❌ Database file not found. Tried common locations.")
        return False
    
    print(f"✅ Found database: {db_path}")
    
    # Find JSON file
    json_path = Path("gita_verses.json")
    if not json_path.exists():
        print("❌ gita_verses.json not found")
        return False
    
    print(f"✅ Found JSON file: {json_path}")
    
    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            verses_data = json.load(f)
        
        print(f"📊 Loaded {len(verses_data)} verses from JSON")
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find or create Gita book
        cursor.execute("SELECT id FROM books WHERE source = 'gita'")
        book_result = cursor.fetchone()
        
        if not book_result:
            print("📝 Creating Bhagavad Gita book entry...")
            cursor.execute("""
                INSERT INTO books (name, latin_name, abbreviation, source, source_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Bhagavad Gita', 'Bhagavad Gita', 'a', 'gita', 'bhagavad_gita', datetime.now(), datetime.now()))
            book_id = cursor.lastrowid
            print(f"✅ Created Gita book with ID: {book_id}")
        else:
            book_id = book_result[0]
            print(f"✅ Found existing Gita book with ID: {book_id}")
        
        # Process verses
        verses_processed = 0
        chapter_1_count = 0
        
        for verse_data in verses_data:
            chapter = verse_data.get('chapter_number')
            verse_num = verse_data.get('verse_number')
            
            if not chapter or not verse_num:
                continue
            
            # Format the verse text
            formatted_text = format_verse_text(verse_data)
            
            # Insert or update verse
            cursor.execute("""
                INSERT OR REPLACE INTO verses (book_id, chapter, verse_number, text, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (book_id, chapter, verse_num, formatted_text, datetime.now(), datetime.now()))
            
            verses_processed += 1
            if chapter == 1:
                chapter_1_count += 1
            
            # Show progress for verse 6 specifically
            if chapter == 1 and verse_num == 6:
                print(f"🎯 Updated Chapter 1, Verse 6 with complete transliteration")
        
        conn.commit()
        
        print(f"✅ Successfully processed {verses_processed} verses")
        print(f"📊 Chapter 1 now has {chapter_1_count} verses")
        
        # Verify verse 6 specifically
        cursor.execute("""
            SELECT text FROM verses 
            WHERE book_id = ? AND chapter = 1 AND verse_number = 6
        """, (book_id,))
        
        result = cursor.fetchone()
        if result:
            text = result[0]
            if 'yudhāmanyuśhcha' in text:
                print("✅ Verse 6 now has complete transliteration!")
            else:
                print("⚠️ Verse 6 transliteration may still be incomplete")
            
            print(f"📝 Verse 6 preview: {text[:200]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database successfully populated!")
        print("🔗 Test it at: http://localhost:8000/api/v1/texts/gita/a/1/6")
    else:
        print("\n❌ Failed to populate database") 