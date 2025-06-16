import sqlite3
from datetime import datetime

print("🔧 Fixing database schema...")

# Connect to database
conn = sqlite3.connect('db/vulgate.db')
cursor = conn.cursor()

# Add missing columns (ignore errors if they already exist)
columns_to_add = [
    "ALTER TABLE books ADD COLUMN abbreviation VARCHAR(10)",
    "ALTER TABLE books ADD COLUMN updated_at DATETIME", 
    "ALTER TABLE books ADD COLUMN source VARCHAR(50) DEFAULT 'bible'",
    "ALTER TABLE books ADD COLUMN source_id VARCHAR(50)"
]

for sql in columns_to_add:
    try:
        cursor.execute(sql)
        print(f"✅ Added column: {sql.split()[-2]}")
    except sqlite3.Error as e:
        if "duplicate column" in str(e):
            print(f"⚠️ Column {sql.split()[-2]} already exists")
        else:
            print(f"❌ Error: {e}")

# Update existing books with proper values
updates = [
    "UPDATE books SET abbreviation = 'a' WHERE name LIKE '%Gita%'",
    "UPDATE books SET source = 'gita' WHERE name LIKE '%Gita%'", 
    "UPDATE books SET source = 'bible' WHERE source IS NULL",
    "UPDATE books SET updated_at = ? WHERE updated_at IS NULL"
]

for update in updates[:-1]:
    cursor.execute(update)
    print(f"✅ Updated: {update[:50]}...")

# Handle the datetime update separately
cursor.execute(updates[-1], (datetime.now(),))
print("✅ Updated timestamps")

conn.commit()
conn.close()

print("\n🎉 Database schema fixed!")
print("🚀 Now restart your server:")
print("python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000") 