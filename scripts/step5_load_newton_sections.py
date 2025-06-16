#!/usr/bin/env python3
"""
Step 5: Load the extracted sample sections into the database as verses.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

def find_database():
    for db in ["db/vulgate.db", "vulgate.db", "word_cache.db",
               "backend/vulgate.db"]:
        p = Path(db)
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None

def newton_book_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM books WHERE source = 'newton'")
    row = cur.fetchone()
    return row[0] if row else None

def load_sections():
    data_path = Path("newton_test_data/extracted_sections.json")
    if not data_path.exists():
        print("❌ Run step4_simple_pdf_extract.py first.")
        return

    db_path = find_database()
    if not db_path:
        print("❌ Database not found.")
        return

    conn = sqlite3.connect(str(db_path))
    book_id = newton_book_id(conn)
    if not book_id:
        print("❌ Newton book missing (run Step 3).")
        conn.close()
        return

    with open(data_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    cur = conn.cursor()
    inserted = 0
    for s in sections:
        text = (f"Section: {s['title']}\nType: {s['section_type'].title()}\n"
                f"Liber: {s['book_number']}\nPage: {s['page_number']}\n\n{s['content']}")
        cur.execute("""
            INSERT INTO verses (
                book_id, chapter, verse_number, text,
                section_type, original_language,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book_id, s["book_number"], s["section_number"], text,
            s["section_type"], "latin",
            datetime.now(), datetime.now()
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted} sample sections into the database.")

if __name__ == "__main__":
    load_sections() 