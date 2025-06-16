#!/usr/bin/env python3
"""
Step 3: Add Newton support to database
Simple database migration to add required columns and the Newton book.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def find_database():
    possible = [
        Path("db/vulgate.db"),
        Path("vulgate.db"),
        Path("backend/vulgate.db"),
        Path("word_cache.db"),
    ]
    for p in possible:
        if p.exists() and p.stat().st_size > 1000:
            print(f"✅ Found database: {p}")
            return p
    print("❌ No database found in expected locations")
    return None


def add_columns_and_book(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    # Add columns
    try:
        cur.execute("ALTER TABLE verses ADD COLUMN page_image TEXT")
        print("✅ Added page_image column")
    except sqlite3.OperationalError:
        print("ℹ️ page_image column already exists")
    try:
        cur.execute("ALTER TABLE verses ADD COLUMN section_type TEXT DEFAULT 'verse'")
        print("✅ Added section_type column")
    except sqlite3.OperationalError:
        print("ℹ️ section_type column already exists")
    try:
        cur.execute("ALTER TABLE verses ADD COLUMN original_language TEXT DEFAULT 'latin'")
        print("✅ Added original_language column")
    except sqlite3.OperationalError:
        print("ℹ️ original_language column already exists")

    # Insert Newton book
    now = datetime.now()
    cur.execute(
        """
        INSERT OR IGNORE INTO books
            (name, latin_name, abbreviation, chapter_count, source, source_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Philosophiae Naturalis Principia Mathematica",
            "Philosophiae Naturalis Principia Mathematica",
            "Newton",
            3,
            "newton",
            "principia_1687",
            now,
            now,
        ),
    )
    cur.execute("SELECT id FROM books WHERE source='newton'")
    row = cur.fetchone()
    if row:
        print(f"✅ Newton book added with ID: {row[0]}")
    else:
        print("❌ Failed to add Newton book")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    db = find_database()
    if db:
        add_columns_and_book(db)
        print("🎉 Step 3 completed! Run step4_simple_pdf_extract.py next")
    else:
        print("❌ Step 3 failed. Database not found")
