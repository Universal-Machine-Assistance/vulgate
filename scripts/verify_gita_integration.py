#!/usr/bin/env python3
"""
Simple script to verify Bhagavad Gita integration
"""

import sqlite3
from pathlib import Path

def verify_integration():
    """Verify the Gita integration was successful"""
    
    db_path = Path(__file__).parent / "db" / "vulgate.db"
    
    if not db_path.exists():
        print("❌ Database not found")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 Verifying Bhagavad Gita Integration")
        print("=" * 50)
        
        # Check for Gita books
        cursor.execute("SELECT id, name, abbreviation, source FROM books WHERE source = 'gita'")
        gita_books = cursor.fetchall()
        
        if gita_books:
            print("✅ Gita books found:")
            for book_id, name, abbrev, source in gita_books:
                print(f"   ID: {book_id}, Name: {name}, Abbreviation: {abbrev}, Source: {source}")
        else:
            print("❌ No Gita books found")
            return False
        
        # Check for Gita verses
        cursor.execute("""
            SELECT COUNT(*) FROM verses v 
            JOIN books b ON v.book_id = b.id 
            WHERE b.source = 'gita'
        """)
        verse_count = cursor.fetchone()[0]
        
        print(f"✅ Gita verses found: {verse_count}")
        
        # Show sample verses
        cursor.execute("""
            SELECT b.name, v.chapter, v.verse_number, 
                   substr(v.text, 1, 100) || '...' as text_preview 
            FROM verses v 
            JOIN books b ON v.book_id = b.id 
            WHERE b.source = 'gita' 
            ORDER BY v.chapter, v.verse_number 
            LIMIT 3
        """)
        
        sample_verses = cursor.fetchall()
        
        if sample_verses:
            print("\n📖 Sample verses:")
            for book_name, chapter, verse_num, text_preview in sample_verses:
                print(f"   {book_name} {chapter}:{verse_num} - {text_preview}")
        
        # Check available sources
        cursor.execute("SELECT DISTINCT source FROM books ORDER BY source")
        sources = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📚 Available text sources: {sources}")
        
        conn.close()
        
        if 'gita' in sources and verse_count > 0:
            print("\n🎉 Bhagavad Gita integration verified successfully!")
            print("\n🧪 Test these endpoints when server is running:")
            print("   curl http://localhost:8000/api/v1/texts/sources")
            print("   curl http://localhost:8000/api/v1/texts/gita/a/2")
            print("   curl http://localhost:8000/api/v1/texts/gita/a/2/47")
            return True
        else:
            print("\n❌ Integration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error checking integration: {e}")
        return False

if __name__ == "__main__":
    verify_integration() 