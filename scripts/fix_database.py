import sqlite3
from datetime import datetime

conn = sqlite3.connect('db/vulgate.db')
cursor = conn.cursor()

print("Fixing database schema...")

# Add missing columns to books table
try:
    cursor.execute('ALTER TABLE books ADD COLUMN abbreviation VARCHAR(10)')
    print('Added abbreviation column')
except Exception as e:
    print(f'abbreviation column: {e}')

try:
    cursor.execute('ALTER TABLE books ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP')
    print('Added updated_at column')
except Exception as e:
    print(f'updated_at column: {e}')

# Add Bhagavad Gita book
cursor.execute('''
    INSERT OR REPLACE INTO books 
    (name, latin_name, abbreviation, source, source_id, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (
    'Bhagavad Gita',
    'Bhagavad Gita', 
    'a',
    'gita',
    'bhagavad_gita',
    datetime.now(),
    datetime.now()
))

book_id = cursor.lastrowid
print(f'Created/Updated Bhagavad Gita book with ID: {book_id}')

# Add sample verses
verses = [
    (1, 1, 'धृतराष्ट्र उवाच |\nधर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः |\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ||१||', 'Dhritarashtra said: O Sanjaya, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?'),
    (1, 2, 'सञ्जय उवाच |\nदृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा |\nआचार्यमुपसङ्गम्य राजा वचनमब्रवीत् ||२||', 'Sanjaya said: On observing the Pandava army standing in military formation, King Duryodhana approached his teacher Dronacharya, and spoke the following words.'),
    (3, 1, 'अर्जुन उवाच |\nकिं तद्ब्रह्म किमध्यात्मं किं कर्म पुरुषोत्तम |\nअधिभूतं च किं प्रोक्तमधिदैवं किमुच्यते ||१||', 'Arjuna said: O Supreme Person, what is Brahman? What is the individual soul? What is fruitive activity? What is this material manifestation? And what are the demigods?')
]

for chapter, verse_num, text, translation in verses:
    cursor.execute('''
        INSERT OR REPLACE INTO verses 
        (book_id, chapter, verse_number, text, translation, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (book_id, chapter, verse_num, text, translation, datetime.now(), datetime.now()))

conn.commit()
print(f'Added {len(verses)} sample Bhagavad Gita verses')

# Verify the data
cursor.execute('SELECT COUNT(*) FROM verses WHERE book_id = ?', (book_id,))
count = cursor.fetchone()[0]
print(f'Verification: {count} verses found for Bhagavad Gita')

conn.close()
print('Database setup complete!') 