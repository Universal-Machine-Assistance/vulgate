#!/usr/bin/env python3
"""Direct database test to bypass path issues"""

import sqlite3
import json

def test_direct_db():
    print("=== DIRECT DATABASE TEST ===")
    
    # Use the exact database path
    cache_db_path = "word_cache.db"
    
    try:
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        # Test the exact INSERT statement from the code
        verse_reference = "Gn 1:1"
        language_code = "es"
        word_alignments_json = json.dumps({"test": "data"})
        translations_json = json.dumps({"literal": "test", "dynamic": "test"})
        
        print("1. Testing INSERT...")
        cursor.execute('''
            INSERT OR REPLACE INTO verse_analysis_cache 
            (verse_reference, language_code, verse_text, word_alignments_json, alignment_method, 
             alignment_confidence, translations_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            verse_reference, 
            language_code,
            "",  # verse_text
            word_alignments_json,
            "test_method",
            0.5,
            translations_json
        ))
        
        conn.commit()
        print("✅ INSERT successful!")
        
        print("2. Testing SELECT...")
        cursor.execute('''
            SELECT word_alignments_json, alignment_method, alignment_confidence,
                   translations_json, verse_text
            FROM verse_analysis_cache 
            WHERE verse_reference = ? AND language_code = ?
        ''', (verse_reference, language_code))
        
        result = cursor.fetchone()
        if result:
            print("✅ SELECT successful!")
            print(f"   Word alignments: {result[0]}")
            print(f"   Method: {result[1]}")
            print(f"   Confidence: {result[2]}")
        else:
            print("❌ SELECT failed - no results")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_direct_db() 