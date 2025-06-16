import sqlite3
from datetime import datetime

print("📖 Fixing Bhagavad Gita verse 1:1...")

# Connect to database
conn = sqlite3.connect('db/vulgate.db')
cursor = conn.cursor()

# Get the Gita book ID
cursor.execute("SELECT id FROM books WHERE source = 'gita' AND name LIKE '%Gita%'")
book_result = cursor.fetchone()

if book_result:
    book_id = book_result[0]
    
    # Check current verse 1:1
    cursor.execute("SELECT id, text FROM verses WHERE book_id = ? AND chapter = 1 AND verse_number = 1", (book_id,))
    current_verse = cursor.fetchone()
    
    if current_verse:
        print(f"Current verse 1:1: {current_verse[1][:100]}...")
        
        # The complete verse 1:1 with the actual Sanskrit text
        complete_verse_1_1 = """धृतराष्ट्र उवाच
धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥

dhṛitarāśhtra uvācha
dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ
māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya

Dhritarashtra said:
O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?"""

        # Update the verse
        cursor.execute("""
            UPDATE verses 
            SET text = ?, updated_at = ?
            WHERE book_id = ? AND chapter = 1 AND verse_number = 1
        """, (complete_verse_1_1, datetime.now(), book_id))
        
        print("✅ Updated verse 1:1 with complete Sanskrit text")
        
        # Also fix verse 1:2 if it exists but is incomplete
        cursor.execute("SELECT id, text FROM verses WHERE book_id = ? AND chapter = 1 AND verse_number = 2", (book_id,))
        verse_1_2 = cursor.fetchone()
        
        if not verse_1_2:
            # Add verse 1:2 if it doesn't exist
            verse_1_2_text = """तत्किं कर्मणि घोरे मां नियोजयसि केशव।
व्यामिश्रेणेव वाक्येन बुद्धिं मोहयसीव मे॥

tat kiṃ karmaṇi ghore māṃ niyojayasi keśava
vyāmiśreṇeva vākyena buddhiṃ mohayasīva me

Then why do You engage me in this terrible action, O Keshava? With confusing words You seem to bewilder my intelligence."""

            cursor.execute("""
                INSERT INTO verses (book_id, chapter, verse_number, text, created_at) 
                VALUES (?, ?, ?, ?, ?)
            """, (book_id, 1, 2, verse_1_2_text, datetime.now()))
            
            print("✅ Added complete verse 1:2")
    
    else:
        # Create verse 1:1 if it doesn't exist
        complete_verse_1_1 = """धृतराष्ट्र उवाच
धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥

dhṛitarāśhtra uvācha
dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ
māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya

Dhritarashtra said:
O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?"""

        cursor.execute("""
            INSERT INTO verses (book_id, chapter, verse_number, text, created_at) 
            VALUES (?, ?, ?, ?, ?)
        """, (book_id, 1, 1, complete_verse_1_1, datetime.now()))
        
        print("✅ Created complete verse 1:1")
    
    conn.commit()
    print("\n🎉 Verse 1:1 fixed!")
    print("\n🧪 Test the updated verse:")
    print("curl http://localhost:8000/api/v1/texts/gita/a/1/1")
    
else:
    print("❌ Gita book not found")

conn.close() 