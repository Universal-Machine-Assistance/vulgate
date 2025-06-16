#!/usr/bin/env python3
"""
Fix database schema issues for the Vulgate backend
This addresses the column errors seen in the server logs
"""

import sqlite3
from pathlib import Path

def fix_database_schema():
    """Fix missing columns in database tables"""
    
    # Database paths
    main_db = Path(__file__).parent / "db" / "vulgate.db"
    word_cache_db = Path(__file__).parent / "word_cache.db"
    
    print("🔧 Fixing database schema issues...")
    
    # Fix main database
    if main_db.exists():
        print(f"📍 Fixing main database: {main_db}")
        fix_main_database(main_db)
    
    # Fix word cache database
    if word_cache_db.exists():
        print(f"📍 Fixing word cache database: {word_cache_db}")
        fix_word_cache_database(word_cache_db)
    
    print("✅ Database schema fixes completed!")

def fix_main_database(db_path):
    """Fix the main vulgate database"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Add missing columns to books table
        missing_book_columns = [
            ("abbreviation", "VARCHAR(10)"),
            ("updated_at", "DATETIME"),
            ("source", "VARCHAR(50) DEFAULT 'bible'"),
            ("source_id", "VARCHAR(50)")
        ]
        
        for column_name, column_type in missing_book_columns:
            try:
                cursor.execute(f"ALTER TABLE books ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column {column_name} to books table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"ℹ️  Column {column_name} already exists in books table")
                else:
                    print(f"⚠️  Error adding {column_name} to books: {e}")
        
        # Add missing columns to verses table if needed
        missing_verse_columns = [
            ("updated_at", "DATETIME"),
            ("language_code", "VARCHAR(10) DEFAULT 'en'")
        ]
        
        for column_name, column_type in missing_verse_columns:
            try:
                cursor.execute(f"ALTER TABLE verses ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column {column_name} to verses table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"ℹ️  Column {column_name} already exists in verses table")
                else:
                    print(f"⚠️  Error adding {column_name} to verses: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Main database schema updated")
        
    except Exception as e:
        print(f"❌ Error fixing main database: {e}")

def fix_word_cache_database(db_path):
    """Fix the word cache database"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get list of existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Found tables in word cache: {tables}")
        
        # Add missing columns to word_cache table if it exists
        if 'word_cache' in tables:
            missing_word_cache_columns = [
                ("language_code", "VARCHAR(10) DEFAULT 'en'"),
                ("theological_interpretation", "TEXT")
            ]
            
            for column_name, column_type in missing_word_cache_columns:
                try:
                    cursor.execute(f"ALTER TABLE word_cache ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added column {column_name} to word_cache table")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"ℹ️  Column {column_name} already exists in word_cache table")
                    else:
                        print(f"⚠️  Error adding {column_name} to word_cache: {e}")
        
        # Add missing columns to word_verse_relationships table if it exists
        if 'word_verse_relationships' in tables:
            try:
                cursor.execute("ALTER TABLE word_verse_relationships ADD COLUMN language_code VARCHAR(10) DEFAULT 'en'")
                print("✅ Added language_code column to word_verse_relationships table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  Column language_code already exists in word_verse_relationships table")
                else:
                    print(f"⚠️  Error adding language_code to word_verse_relationships: {e}")
        
        # Add missing columns to verse_analysis_cache table if it exists
        if 'verse_analysis_cache' in tables:
            try:
                cursor.execute("ALTER TABLE verse_analysis_cache ADD COLUMN language_code VARCHAR(10) DEFAULT 'en'")
                print("✅ Added language_code column to verse_analysis_cache table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️  Column language_code already exists in verse_analysis_cache table")
                else:
                    print(f"⚠️  Error adding language_code to verse_analysis_cache: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Word cache database schema updated")
        
    except Exception as e:
        print(f"❌ Error fixing word cache database: {e}")

def main():
    print("🔧 Database Schema Fixer")
    print("=" * 30)
    print("This script fixes missing columns that cause server errors")
    print()
    
    fix_database_schema()
    
    print("\n💡 After running this script, restart your server:")
    print("pkill -f uvicorn")
    print("python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main() 