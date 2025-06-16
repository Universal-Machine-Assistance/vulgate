#!/usr/bin/env python3
"""Debug why caching is failing"""

import os
import sys
import sqlite3
import json

# Add the same path resolution as the API
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
sys.path.append(project_root)

def debug_cache_failure():
    print("=== DEBUGGING CACHE FAILURE ===")
    
    # Test the exact same path resolution as the API
    print("1. Testing path resolution...")
    api_project_root = os.path.abspath(os.path.join(os.path.dirname("backend/app/api/api_v1/endpoints/dictionary.py"), "../../../../../"))
    cache_db_path = os.path.join(api_project_root, "word_cache.db")
    
    print(f"   API project root: {api_project_root}")
    print(f"   Cache DB path: {cache_db_path}")
    print(f"   Cache DB exists: {os.path.exists(cache_db_path)}")
    print(f"   Current dir: {os.getcwd()}")
    print(f"   Local word_cache.db exists: {os.path.exists('word_cache.db')}")
    
    # Test the exact caching function logic
    print("\n2. Testing cache function logic...")
    
    verse_reference = "DEBUG 1:1"
    language_code = "test"
    literal_translation = "Debug literal"
    dynamic_translation = "Debug dynamic"
    word_alignments = {
        "literal": [{"target_words": ["Debug"], "target_indices": [0], "confidence": 0.9}],
        "dynamic": [{"target_words": ["Debug"], "target_indices": [0], "confidence": 0.9}],
        "method": "debug_test",
        "average_confidence": 0.9
    }
    
    try:
        # Use the exact same path as the API
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        print("   ✅ Database connection successful")
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verse_analysis_cache'")
        table_exists = cursor.fetchone()
        print(f"   Table exists: {table_exists is not None}")
        
        if table_exists:
            # Check table schema
            cursor.execute("PRAGMA table_info(verse_analysis_cache)")
            columns = cursor.fetchall()
            print(f"   Table columns: {[col[1] for col in columns]}")
            
            # Test the exact INSERT from the API
            word_alignments_json = json.dumps(word_alignments)
            translations_data = {
                "literal": literal_translation,
                "dynamic": dynamic_translation
            }
            translations_json = json.dumps(translations_data)
            
            print("   Testing INSERT statement...")
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
                word_alignments.get("method", "unknown"),
                word_alignments.get("average_confidence", 0.0),
                translations_json
            ))
            
            conn.commit()
            print("   ✅ INSERT successful")
            
            # Verify the insert
            cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache WHERE verse_reference = ?", (verse_reference,))
            count = cursor.fetchone()[0]
            print(f"   Records inserted: {count}")
            
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Cache function error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Test if the API is using a different database
    print("\n3. Checking for multiple database files...")
    for root, dirs, files in os.walk("/Users/guillermomolina/dev/vulgate"):
        for file in files:
            if file == "word_cache.db":
                full_path = os.path.join(root, file)
                try:
                    conn = sqlite3.connect(full_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache")
                    count = cursor.fetchone()[0]
                    conn.close()
                    print(f"   Found: {full_path} (records: {count})")
                except:
                    print(f"   Found: {full_path} (error reading)")

if __name__ == "__main__":
    debug_cache_failure() 