#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from datetime import datetime

# Connect to database
db_path = Path("db/vulgate.db")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("🔧 Fixing database schema...")

# Add missing columns (ignore errors if they already exist)
columns_to_add = [
    ("books", "abbreviation", "VARCHAR(10)"),
    ("books", "updated_at", "DATETIME"),
    ("books", "source", "VARCHAR(50) DEFAULT 'bible'"),
    ("books", "source_id", "VARCHAR(50)"),
]

for table, column, column_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
        print(f"✅ Added {column} to {table}")
    except sqlite3.Error as e:
        if "duplicate column name" in str(e).lower():
            print(f"⚠️ Column {column} already exists in {table}")
        else:
            print(f"❌ Error adding {column} to {table}: {e}")

# Update existing books with abbreviations
cursor.execute("UPDATE books SET abbreviation = 'Gn' WHERE name LIKE '%Genesis%' AND (abbreviation IS NULL OR abbreviation = '')")
cursor.execute("UPDATE books SET abbreviation = 'Ex' WHERE name LIKE '%Exodus%' AND (abbreviation IS NULL OR abbreviation = '')")
cursor.execute("UPDATE books SET abbreviation = 'Mt' WHERE name LIKE '%Matthew%' AND (abbreviation IS NULL OR abbreviation = '')")
cursor.execute("UPDATE books SET abbreviation = 'a' WHERE name LIKE '%Gita%' AND (abbreviation IS NULL OR abbreviation = '')")

# Set updated_at for all books
cursor.execute("UPDATE books SET updated_at = ? WHERE updated_at IS NULL", (datetime.now(),))

# Set source for existing books
cursor.execute("UPDATE books SET source = 'bible' WHERE source IS NULL")
cursor.execute("UPDATE books SET source = 'gita' WHERE name LIKE '%Gita%'")

conn.commit()
conn.close()

print("✅ Database schema fixed!")
print("🚀 You can now restart your server") 