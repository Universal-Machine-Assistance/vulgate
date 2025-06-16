#!/usr/bin/env python3
"""
Step 3: Add Newton support to database.
Adds new columns to the verses table and inserts the Newton book entry.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def find_database():
    """Locate the existing database file."""
    for db in ["db/vulgate.db", "vulgate.db", "word_cache.db",
               "backend/vulgate.db"]:
        p = Path(db)
        if p.exists() and p.stat().st_size > 1000:
            print(f"✅ Found database: {p}")
            return p
    print("❌ No database found")
    return None

def add_columns_and_book(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    print("🔄 Adding support columns…")
    try:
        cur.execute("ALTER TABLE verses ADD COLUMN page_image TEXT")
        print("✅ Added page_image column")
    except sqlite3.OperationalError:
        print("ℹ️  page_image column already exists")

    try:
        cur.execute("ALTER TABLE verses ADD COLUMN section_type TEXT DEFAULT 'verse'")
        print("✅ Added section_type column")
    except sqlite3.OperationalError:
        print("ℹ️  section_type column already exists")

    try:
        cur.execute("ALTER TABLE verses ADD COLUMN original_language TEXT DEFAULT 'latin'")
        print("✅ Added original_language column")
    except sqlite3.OperationalError:
        print("ℹ️  original_language column already exists")

    print("🔄 Inserting Newton book entry…")
    now = datetime.now()
    cur.execute("""
        INSERT OR IGNORE INTO books (
            name, latin_name, abbreviation, chapter_count,
            source, source_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Philosophiae Naturalis Principia Mathematica",
        "Philosophiae Naturalis Principia Mathematica",
        "Newton",
        3,
        "newton",
        "principia_1687",
        now, now
    ))
    conn.commit()
    conn.close()
    print("✅ Step 3 finished!")

if __name__ == "__main__":
    db = find_database()
    if db:
        add_columns_and_book(db) 