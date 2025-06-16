#!/usr/bin/env python3
"""
Add word alignment caching to the existing database schema
"""

import sqlite3
import os

def add_word_alignment_cache():
    """Add word alignment caching columns to verse_analysis_cache table"""
    
    # Path to the word cache database
    cache_db_path = "word_cache.db"
    
    if not os.path.exists(cache_db_path):
        print(f"❌ Database {cache_db_path} not found. Creating it...")
        # Create the database if it doesn't exist
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        # Create the verse_analysis_cache table with word alignment support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verse_analysis_cache (
                verse_reference TEXT,
                language_code TEXT,
                verse_text TEXT,
                word_analysis_json TEXT,
                translations_json TEXT,
                theological_layer_json TEXT,
                jungian_layer_json TEXT,
                cosmological_layer_json TEXT,
                word_alignments_json TEXT,
                alignment_method TEXT,
                alignment_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (verse_reference, language_code)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Created new database with word alignment support")
        return
    
    try:
        conn = sqlite3.connect(cache_db_path)
        cursor = conn.cursor()
        
        # Check if word alignment columns exist
        cursor.execute("PRAGMA table_info(verse_analysis_cache)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add word alignment columns if they don't exist
        if 'word_alignments_json' not in columns:
            cursor.execute('ALTER TABLE verse_analysis_cache ADD COLUMN word_alignments_json TEXT')
            print("✅ Added word_alignments_json column")
        else:
            print("ℹ️  word_alignments_json column already exists")
            
        if 'alignment_method' not in columns:
            cursor.execute('ALTER TABLE verse_analysis_cache ADD COLUMN alignment_method TEXT')
            print("✅ Added alignment_method column")
        else:
            print("ℹ️  alignment_method column already exists")
            
        if 'alignment_confidence' not in columns:
            cursor.execute('ALTER TABLE verse_analysis_cache ADD COLUMN alignment_confidence REAL')
            print("✅ Added alignment_confidence column")
        else:
            print("ℹ️  alignment_confidence column already exists")
        
        # Create index for efficient lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_verse_analysis_alignment 
            ON verse_analysis_cache(verse_reference, language_code)
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Word alignment caching schema updated successfully")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")

if __name__ == "__main__":
    add_word_alignment_cache() 