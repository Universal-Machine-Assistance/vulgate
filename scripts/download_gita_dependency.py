#!/usr/bin/env python3
"""
Script to download Bhagavad Gita data as a dependency from the official GitHub repository
https://github.com/gita/BhagavadGita
"""

import os
import json
import sqlite3
import requests
import subprocess
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

class GitaDataDownloader:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.db_path = self.project_root / "db" / "vulgate.db"
        self.temp_dir = None
        
    def download_repository(self):
        """Download the Bhagavad Gita repository"""
        print("📥 Downloading Bhagavad Gita repository...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        repo_path = Path(self.temp_dir) / "BhagavadGita"
        
        try:
            # Clone the repository
            result = subprocess.run([
                "git", "clone", 
                "https://github.com/gita/BhagavadGita.git",
                str(repo_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Repository downloaded successfully")
                return repo_path
            else:
                print(f"❌ Git clone failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Git clone timed out")
            return None
        except Exception as e:
            print(f"❌ Error downloading repository: {e}")
            return None
    
    def extract_data_from_sqlite(self, repo_path):
        """Extract data from the repository's SQLite database"""
        print("📊 Extracting data from repository database...")
        
        # Look for SQLite database files
        db_files = list(repo_path.glob("*.sqlite")) + list(repo_path.glob("**/*.sqlite"))
        
        if not db_files:
            print("❌ No SQLite database found in repository")
            return None
            
        db_file = db_files[0]  # Use the first database found
        print(f"📁 Found database: {db_file.name}")
        
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 Found tables: {[table[0] for table in tables]}")
            
            # Extract verses data
            verses_data = []
            
            # Try different possible table structures
            possible_queries = [
                "SELECT * FROM verses ORDER BY chapter_number, verse_number",
                "SELECT * FROM verse ORDER BY chapter, verse_number", 
                "SELECT * FROM slokas ORDER BY chapter, verse",
                "SELECT chapter_number, verse_number, text, transliteration, word_meanings, translation FROM verses",
                "SELECT * FROM chapters",
            ]
            
            for query in possible_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    if results:
                        # Get column names
                        columns = [description[0] for description in cursor.description]
                        print(f"✅ Query successful: {query}")
                        print(f"📊 Found {len(results)} rows with columns: {columns}")
                        
                        # Convert to dictionaries
                        for row in results:
                            verse_dict = dict(zip(columns, row))
                            verses_data.append(verse_dict)
                        break
                        
                except sqlite3.Error as e:
                    continue
            
            conn.close()
            
            if verses_data:
                print(f"✅ Extracted {len(verses_data)} verses from database")
                return verses_data
            else:
                print("❌ No verse data found in database")
                return None
                
        except Exception as e:
            print(f"❌ Error reading database: {e}")
            return None
    
    def try_api_download(self):
        """Try to download data from the Bhagavad Gita API"""
        print("🌐 Attempting to download from Bhagavad Gita API...")
        
        # Try the new API first
        api_urls = [
            "https://bhagavadgita.io/api/v1/chapters",
            "https://vedicscriptures.github.io/data/bhagavad-gita.json"
        ]
        
        for api_url in api_urls:
            try:
                print(f"🔗 Trying: {api_url}")
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Successfully downloaded from {api_url}")
                    return self.process_api_data(data)
                    
            except Exception as e:
                print(f"❌ Failed to download from {api_url}: {e}")
                continue
        
        return None
    
    def process_api_data(self, data):
        """Process API data into our format"""
        verses_data = []
        
        # Handle different API response formats
        if isinstance(data, list):
            # Chapters list format
            for chapter in data:
                chapter_num = chapter.get('chapter_number', chapter.get('id', 0))
                
                # Try to get verses for this chapter
                if 'verses' in chapter:
                    for verse in chapter['verses']:
                        verses_data.append({
                            'chapter_number': chapter_num,
                            'verse_number': verse.get('verse_number', verse.get('id', 0)),
                            'text': verse.get('text', verse.get('sanskrit', '')),
                            'transliteration': verse.get('transliteration', ''),
                            'translation': verse.get('translation', verse.get('meaning', ''))
                        })
        
        elif isinstance(data, dict):
            # Single object format
            if 'chapters' in data:
                for chapter in data['chapters']:
                    chapter_num = chapter.get('chapter_number', chapter.get('id', 0))
                    
                    if 'verses' in chapter:
                        for verse in chapter['verses']:
                            verses_data.append({
                                'chapter_number': chapter_num,
                                'verse_number': verse.get('verse_number', verse.get('id', 0)),
                                'text': verse.get('text', verse.get('sanskrit', '')),
                                'transliteration': verse.get('transliteration', ''),
                                'translation': verse.get('translation', verse.get('meaning', ''))
                            })
        
        return verses_data if verses_data else None
    
    def create_sample_data(self):
        """Create sample Bhagavad Gita data if download fails"""
        print("📝 Creating sample Bhagavad Gita data...")
        
        sample_verses = [
            {
                'chapter_number': 1,
                'verse_number': 1,
                'text': 'धृतराष्ट्र उवाच',
                'transliteration': 'dhṛtarāṣṭra uvāca',
                'translation': 'Dhritarashtra said:'
            },
            {
                'chapter_number': 1,
                'verse_number': 2,
                'text': 'धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः',
                'transliteration': 'dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ',
                'translation': 'On the holy field of Kurukshetra, assembled and eager to fight,'
            },
            {
                'chapter_number': 2,
                'verse_number': 1,
                'text': 'सञ्जय उवाच',
                'transliteration': 'sañjaya uvāca',
                'translation': 'Sanjaya said:'
            },
            {
                'chapter_number': 2,
                'verse_number': 2,
                'text': 'तं तथा कृपयाविष्टमश्रुपूर्णाकुलेक्षणम्',
                'transliteration': 'taṃ tathā kṛpayāviṣṭam aśru-pūrṇākulekṣaṇam',
                'translation': 'Seeing Arjuna filled with compassion, his eyes full of tears,'
            },
            {
                'chapter_number': 3,
                'verse_number': 1,
                'text': 'अर्जुन उवाच',
                'transliteration': 'arjuna uvāca',
                'translation': 'Arjuna said:'
            },
            {
                'chapter_number': 3,
                'verse_number': 2,
                'text': 'ज्यायसी चेत्कर्मणस्ते मता बुद्धिर्जनार्दन',
                'transliteration': 'jyāyasī cet karmaṇas te matā buddhir janārdana',
                'translation': 'If You consider knowledge superior to action, O Janardana,'
            }
        ]
        
        return sample_verses
    
    def integrate_into_database(self, verses_data):
        """Integrate the downloaded data into our database"""
        print("💾 Integrating Bhagavad Gita data into database...")
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if Gita book already exists
            cursor.execute("SELECT id FROM books WHERE source = 'gita' AND name = 'Bhagavad Gita'")
            existing = cursor.fetchone()
            
            if existing:
                print(f"✅ Bhagavad Gita book already exists with ID: {existing[0]}")
                book_id = existing[0]
                
                # Clear existing verses
                cursor.execute("DELETE FROM verses WHERE book_id = ?", (book_id,))
                print("🗑️ Cleared existing verses")
            else:
                # Add the Bhagavad Gita book
                cursor.execute("""
                    INSERT INTO books (name, latin_name, source, source_id, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, ('Bhagavad Gita', 'Bhagavad Gita', 'gita', 'bhagavad_gita', datetime.now()))
                
                book_id = cursor.lastrowid
                print(f"✅ Added Bhagavad Gita book with ID: {book_id}")
            
            # Add verses
            verses_added = 0
            for verse in verses_data:
                chapter = verse.get('chapter_number', verse.get('chapter', 0))
                verse_num = verse.get('verse_number', verse.get('verse', 0))
                
                # Combine text, transliteration, and translation
                text_parts = []
                if verse.get('text'):
                    text_parts.append(verse['text'])
                if verse.get('transliteration'):
                    text_parts.append(verse['transliteration'])
                if verse.get('translation'):
                    text_parts.append(verse['translation'])
                
                combined_text = '\n'.join(text_parts)
                
                if chapter and verse_num and combined_text:
                    cursor.execute("""
                        INSERT INTO verses (book_id, chapter, verse_number, text, created_at) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (book_id, chapter, verse_num, combined_text, datetime.now()))
                    verses_added += 1
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully added {verses_added} verses to database")
            return True
            
        except Exception as e:
            print(f"❌ Error integrating data: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up temporary files")
    
    def run(self):
        """Main execution method"""
        print("🕉️ Bhagavad Gita Data Downloader")
        print("=" * 50)
        
        verses_data = None
        
        try:
            # Method 1: Try downloading from repository
            repo_path = self.download_repository()
            if repo_path:
                verses_data = self.extract_data_from_sqlite(repo_path)
            
            # Method 2: Try API download if repository method failed
            if not verses_data:
                verses_data = self.try_api_download()
            
            # Method 3: Use sample data as fallback
            if not verses_data:
                print("⚠️ Download methods failed, using sample data")
                verses_data = self.create_sample_data()
            
            # Integrate into database
            if verses_data:
                success = self.integrate_into_database(verses_data)
                if success:
                    print("\n🎉 Bhagavad Gita integration completed successfully!")
                    print(f"📊 Total verses processed: {len(verses_data)}")
                    print("\n🧪 Test your integration:")
                    print("curl http://localhost:8000/api/v1/texts/sources")
                    print("curl http://localhost:8000/api/v1/texts/gita/a/2")
                else:
                    print("❌ Failed to integrate data into database")
            else:
                print("❌ No data available to integrate")
                
        finally:
            self.cleanup()

if __name__ == "__main__":
    downloader = GitaDataDownloader()
    downloader.run() 