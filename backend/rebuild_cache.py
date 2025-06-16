#!/usr/bin/env python3
"""Rebuild the word alignment cache"""

import sqlite3
import json
import requests
import time

def rebuild_cache():
    """Rebuild the word alignment cache by clearing and regenerating"""
    
    print("=== REBUILDING WORD ALIGNMENT CACHE ===")
    
    # 1. Clear existing cache
    print("1. Clearing existing cache...")
    try:
        conn = sqlite3.connect("word_cache.db")
        cursor = conn.cursor()
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache")
        existing_count = cursor.fetchone()[0]
        print(f"   Found {existing_count} existing records")
        
        # Clear cache
        cursor.execute("DELETE FROM verse_analysis_cache")
        conn.commit()
        conn.close()
        print("   ✅ Cache cleared")
        
    except Exception as e:
        print(f"   ❌ Error clearing cache: {e}")
        return
    
    # 2. Test verses to rebuild cache for
    test_verses = [
        {"verse": "In princīpio creāvit Deus cælum, et terram.", "reference": "Gn 1:1", "language": "es"},
        {"verse": "In princīpio creāvit Deus cælum, et terram.", "reference": "Gn 1:1", "language": "en"},
        {"verse": "In princīpio creāvit Deus cælum, et terram.", "reference": "Gn 1:1", "language": "fr"},
    ]
    
    print(f"2. Rebuilding cache for {len(test_verses)} verse/language combinations...")
    
    api_url = "http://127.0.0.1:8000/api/v1/dictionary/analyze/verse/openai"
    
    for i, verse_data in enumerate(test_verses):
        print(f"   Processing {i+1}/{len(test_verses)}: {verse_data['reference']} ({verse_data['language']})")
        
        try:
            # Make API call
            response = requests.post(api_url, json={
                "verse": verse_data["verse"],
                "reference": verse_data["reference"], 
                "analysis_language": verse_data["language"],
                "include_translations": True
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "word_alignments" in result:
                    print(f"      ✅ Generated word alignments")
                else:
                    print(f"      ⚠️  No word alignments in response")
            else:
                print(f"      ❌ API error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(2)
    
    # 3. Check final cache state
    print("3. Checking final cache state...")
    try:
        conn = sqlite3.connect("word_cache.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM verse_analysis_cache")
        final_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT verse_reference, language_code, alignment_method,
                   CASE WHEN word_alignments_json IS NULL THEN 'NULL' ELSE 'HAS_DATA' END
            FROM verse_analysis_cache
        """)
        records = cursor.fetchall()
        
        conn.close()
        
        print(f"   Final cache count: {final_count}")
        if records:
            print("   Cache contents:")
            for record in records:
                print(f"      {record[0]} ({record[1]}) - Method: {record[2]}, Data: {record[3]}")
        else:
            print("   ❌ Cache is still empty - caching mechanism is broken")
            
    except Exception as e:
        print(f"   ❌ Error checking cache: {e}")

if __name__ == "__main__":
    rebuild_cache() 