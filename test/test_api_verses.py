#!/usr/bin/env python3
"""
Test the API to see what verses are actually being returned
"""

import requests
import json

def test_gita_api():
    print("🧪 Testing Gita API endpoints...")
    
    base_url = "http://localhost:8000/api/v1/texts"
    
    try:
        # Test the chapter endpoint
        print("\n📖 Testing Chapter 1 endpoint...")
        response = requests.get(f"{base_url}/gita/a/1")
        
        if response.status_code == 200:
            verses = response.json()
            print(f"✅ API returned {len(verses)} verses")
            
            # Show verse numbers
            verse_numbers = [v['verse_number'] for v in verses]
            print(f"📊 Verse numbers: {sorted(verse_numbers)}")
            
            # Show first few verses
            print("\n📝 First 5 verses:")
            for i, verse in enumerate(verses[:5]):
                print(f"  {verse['verse_number']}: {verse['text'][:100]}...")
            
            if len(verses) < 47:
                print(f"\n⚠️  Only {len(verses)} verses returned, expected 47")
                print("🔍 Missing verse numbers:")
                all_expected = set(range(1, 48))
                returned = set(verse_numbers)
                missing = sorted(all_expected - returned)
                print(f"   {missing}")
            else:
                print(f"\n✅ All {len(verses)} verses returned!")
                
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running?")
        print("   Start with: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_database_direct():
    print("\n🗄️  Testing database directly...")
    
    import sqlite3
    from pathlib import Path
    
    try:
        # Database path
        db_path = Path(__file__).parent / "db" / "vulgate.db"
        
        if not db_path.exists():
            print(f"❌ Database not found at {db_path}")
            return
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get Gita book
        cursor.execute("SELECT id, name FROM books WHERE source = 'gita'")
        book_result = cursor.fetchone()
        
        if not book_result:
            print("❌ Gita book not found in database")
            return
        
        book_id, book_name = book_result
        print(f"✅ Found book: {book_name} (ID: {book_id})")
        
        # Count verses in Chapter 1
        cursor.execute("""
            SELECT COUNT(*) FROM verses 
            WHERE book_id = ? AND chapter = 1
        """, (book_id,))
        
        count = cursor.fetchone()[0]
        print(f"📊 Database has {count} verses in Chapter 1")
        
        # Get verse numbers
        cursor.execute("""
            SELECT verse_number FROM verses 
            WHERE book_id = ? AND chapter = 1
            ORDER BY verse_number
        """, (book_id,))
        
        verse_numbers = [row[0] for row in cursor.fetchall()]
        print(f"📝 Verse numbers in DB: {verse_numbers[:10]}{'...' if len(verse_numbers) > 10 else ''}")
        
        if len(verse_numbers) < 47:
            missing = []
            for i in range(1, 48):
                if i not in verse_numbers:
                    missing.append(i)
            print(f"⚠️  Missing verses: {missing}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_database_direct()
    test_gita_api() 