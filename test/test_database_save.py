#!/usr/bin/env python3

import sqlite3
import os
from vulgate_analyzer import VulgateAnalyzer

# Test database saving and loading of macronized text
print("="*70)
print("TESTING DATABASE SAVE/LOAD OF MACRONIZED TEXT")
print("="*70)

# Initialize analyzer
analyzer = VulgateAnalyzer(database_path="test_macron_db.db")

# Test verses
test_verses = [
    {
        "book": "Dt", 
        "chapter": 1, 
        "verse": 3,
        "text": "Quadragesimo anno, undecimo mense, prima die mensis, locutus est Moyses ad filios Israel omnia quae praeceperat illi Dominus, ut diceret eis:"
    },
    {
        "book": "Gn", 
        "chapter": 1, 
        "verse": 1,
        "text": "In principio creavit Deus caelum et terram"
    }
]

for test_verse in test_verses:
    print(f"\n📖 Testing {test_verse['book']} {test_verse['chapter']}:{test_verse['verse']}")
    print(f"Original: {test_verse['text']}")
    
    # Analyze the verse (this should macronize and save to DB)
    result = analyzer.analyze_verse_complete(
        test_verse['book'], 
        test_verse['chapter'], 
        test_verse['verse'], 
        test_verse['text']
    )
    
    print(f"Analysis result:")
    print(f"  - Latin text: {result.latin_text}")
    print(f"  - Macronized: {result.macronized_text}")
    print(f"  - Original: {result.original_text}")
    
    # Now check what's actually in the database
    print(f"\n🗄️  Database verification:")
    conn = sqlite3.connect("test_macron_db.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT book_abbreviation, chapter_number, verse_number, latin_text, macronized_text, original_text
        FROM verse_analyses
        WHERE book_abbreviation = ? AND chapter_number = ? AND verse_number = ?
    ''', (test_verse['book'], test_verse['chapter'], test_verse['verse']))
    
    db_result = cursor.fetchone()
    if db_result:
        book, chapter, verse, latin_text, macronized_text, original_text = db_result
        print(f"  ✅ Found in database:")
        print(f"    - Latin text: {latin_text}")
        print(f"    - Macronized: {macronized_text}")
        print(f"    - Original: {original_text}")
        
        # Check if macronized text is different from original
        if macronized_text and macronized_text != original_text:
            print(f"  ✅ Macronization was applied and saved!")
        elif macronized_text == original_text:
            print(f"  ⚠️  Macronized text is same as original (may be normal)")
        else:
            print(f"  ❌ No macronized text in database")
    else:
        print(f"  ❌ Verse not found in database!")
    
    conn.close()
    
    # Test loading from database
    print(f"\n🔄 Testing load from database:")
    # Clear the analyzer's memory and load fresh from DB
    analyzer2 = VulgateAnalyzer(database_path="test_macron_db.db")
    loaded_result = analyzer2.analyze_verse_complete(
        test_verse['book'], 
        test_verse['chapter'], 
        test_verse['verse'], 
        test_verse['text']
    )
    
    print(f"  - Loaded Latin text: {loaded_result.latin_text}")
    print(f"  - Loaded Macronized: {loaded_result.macronized_text}")
    print(f"  - Loaded Original: {loaded_result.original_text}")
    
    print("-" * 70)

print(f"\n🧹 Cleaning up test database...")
if os.path.exists("test_macron_db.db"):
    os.remove("test_macron_db.db")
    print("✅ Test database removed")

print(f"\n✨ Database save/load test complete!") 