#!/usr/bin/env python3
"""
Step 5: Load extracted test sections into the database
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("newton_test_data/extracted_sections.json")


def find_database():
    for p in [Path("db/vulgate.db"), Path("vulgate.db"), Path("backend/vulgate.db"), Path("word_cache.db")]:
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None


def get_book_id(cursor):
    cursor.execute("SELECT id FROM books WHERE source='newton'")
    row = cursor.fetchone()
    return row[0] if row else None


def load_sections():
    if not DATA_FILE.exists():
        print("❌ Data file missing. Run step4_simple_pdf_extract.py first")
        return False
    db_path = find_database()
    if not db_path:
        print("❌ Database not found. Run step3_add_database_support.py first")
        return False
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        sections = json.load(f)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    book_id = get_book_id(cur)
    if not book_id:
        print("❌ Newton book missing in database")
        return False
    inserted = 0
    for sec in sections:
        verse_text = f"""Section: {sec['title']}
Type: {sec['section_type'].title()}
Liber: {sec['book_number']}
Page: {sec['page_number']}

{sec['content']}"""
        try:
            cur.execute(
                """
                INSERT INTO verses (book_id, chapter, verse_number, text, section_type, original_language, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'latin', ?, ?)
                """,
                (
                    book_id,
                    sec['book_number'],
                    sec['section_number'],
                    verse_text,
                    sec['section_type'],
                    datetime.now(),
                    datetime.now(),
                ),
            )
            inserted += 1
        except Exception as e:
            print(f"⚠️ Failed to insert section {sec['section_number']}: {e}")
    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} sections into database")
    return True


if __name__ == "__main__":
    if load_sections():
        print("🎉 Step 5 completed! Data loaded into database")
    else:
        print("❌ Step 5 failed")
