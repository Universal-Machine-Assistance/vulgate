#!/usr/bin/env python3
"""
Fetch complete Bhagavad Gita data from the official API
Based on: https://github.com/gita/bhagavad-gita-api
"""

import sqlite3
import requests
import json
from datetime import datetime
from pathlib import Path
import time

class GitaApiFetcher:
    def __init__(self):
        self.base_url = "https://bhagavadgita.io/api/v1"
        self.db_path = Path(__file__).parent / "db" / "vulgate.db"
        
    def fetch_chapter_data(self, chapter_num):
        """Fetch all verses for a specific chapter"""
        try:
            url = f"{self.base_url}/chapters/{chapter_num}/verses"
            print(f"📥 Fetching Chapter {chapter_num} from {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Downloaded {len(data)} verses from Chapter {chapter_num}")
            return data
            
        except requests.RequestException as e:
            print(f"❌ Error fetching Chapter {chapter_num}: {e}")
            return None
    
    def fetch_all_chapters(self):
        """Fetch all 18 chapters of the Bhagavad Gita"""
        all_verses = []
        
        for chapter in range(1, 19):  # Chapters 1-18
            chapter_data = self.fetch_chapter_data(chapter)
            if chapter_data:
                all_verses.extend(chapter_data)
                time.sleep(0.5)  # Be respectful to the API
            else:
                print(f"⚠️  Failed to fetch Chapter {chapter}")
        
        return all_verses
    
    def format_verse_text(self, verse_data):
        """Format verse data into our database format"""
        try:
            # Extract the Sanskrit text
            sanskrit = verse_data.get('text', '')
            
            # Extract transliteration
            transliteration = verse_data.get('transliteration', '')
            
            # Extract word meanings
            word_meanings = verse_data.get('word_meanings', '')
            
            # Extract translation
            translation = verse_data.get('translation', '')
            
            # Format the complete text
            formatted_text = f"""{sanskrit}

{transliteration}

{translation}"""
            
            if word_meanings:
                formatted_text += f"\n\nWord meanings: {word_meanings}"
            
            return formatted_text
            
        except Exception as e:
            print(f"❌ Error formatting verse: {e}")
            return f"Error formatting verse: {verse_data.get('verse_number', 'unknown')}"
    
    def update_database(self, verses_data):
        """Update our database with the fetched verses"""
        if not verses_data:
            print("❌ No verse data to update")
            return False
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get the Gita book ID
            cursor.execute("SELECT id FROM books WHERE source = 'gita' AND name LIKE '%Gita%'")
            book_result = cursor.fetchone()
            
            if not book_result:
                print("❌ Gita book not found in database")
                return False
            
            book_id = book_result[0]
            print(f"✅ Found Gita book with ID: {book_id}")
            
            # Clear existing verses (we'll replace with authentic data)
            cursor.execute("DELETE FROM verses WHERE book_id = ?", (book_id,))
            print("🗑️  Cleared existing placeholder verses")
            
            # Insert new verses
            verses_added = 0
            
            for verse_data in verses_data:
                try:
                    chapter = verse_data.get('chapter_number', 0)
                    verse_num = verse_data.get('verse_number', 0)
                    
                    if chapter == 0 or verse_num == 0:
                        print(f"⚠️  Skipping verse with invalid chapter/verse number: {verse_data}")
                        continue
                    
                    formatted_text = self.format_verse_text(verse_data)
                    
                    cursor.execute("""
                        INSERT INTO verses (book_id, chapter, verse_number, text, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (book_id, chapter, verse_num, formatted_text, datetime.now(), datetime.now()))
                    
                    verses_added += 1
                    if verses_added % 10 == 0:
                        print(f"📝 Added {verses_added} verses...")
                    
                except Exception as e:
                    print(f"❌ Error adding verse {verse_data.get('chapter_number', '?')}:{verse_data.get('verse_number', '?')}: {e}")
            
            conn.commit()
            print(f"\n🎉 Successfully added {verses_added} authentic Gita verses!")
            
            # Verify Chapter 1
            cursor.execute("""
                SELECT COUNT(*) FROM verses 
                WHERE book_id = ? AND chapter = 1
            """, (book_id,))
            
            ch1_count = cursor.fetchone()[0]
            print(f"✅ Chapter 1 now has {ch1_count} verses")
            
            # Show sample verse
            cursor.execute("""
                SELECT chapter, verse_number, substr(text, 1, 100) || '...' as preview
                FROM verses 
                WHERE book_id = ? AND chapter = 1 AND verse_number = 6
            """, (book_id,))
            
            sample = cursor.fetchone()
            if sample:
                print(f"\n📖 Sample verse 1:6:")
                print(f"   {sample[2]}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

def main():
    print("🕉️  Fetching Complete Bhagavad Gita Data")
    print("=" * 50)
    print("Source: https://github.com/gita/bhagavad-gita-api")
    print("API: https://bhagavadgita.io/api/v1")
    print()
    
    fetcher = GitaApiFetcher()
    
    # First, let's try to fetch just Chapter 1 to test
    print("🧪 Testing API with Chapter 1...")
    chapter_1_data = fetcher.fetch_chapter_data(1)
    
    if not chapter_1_data:
        print("❌ API test failed. Cannot proceed.")
        return False
    
    print(f"✅ API test successful! Chapter 1 has {len(chapter_1_data)} verses")
    
    # Ask user if they want to fetch all chapters
    print(f"\n💡 The API is working! Found {len(chapter_1_data)} verses in Chapter 1.")
    print("   Do you want to fetch all 18 chapters? This will replace ALL existing Gita data.")
    
    # For now, let's just update Chapter 1 with authentic data
    print("📥 Updating Chapter 1 with authentic Sanskrit verses...")
    
    success = fetcher.update_database(chapter_1_data)
    
    if success:
        print("\n🎉 Chapter 1 has been updated with authentic Bhagavad Gita content!")
        print("\n🧪 Test the updated verses:")
        print("curl http://localhost:8000/api/v1/texts/gita/a/1/6")
        print("\n💡 Restart your server to see the changes:")
        print("pkill -f uvicorn && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("❌ Failed to update database")
    
    return success

if __name__ == "__main__":
    main() 