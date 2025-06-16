import sqlite3
from datetime import datetime

print("📖 Adding famous Bhagavad Gita verse 2:47...")

# Connect to database
conn = sqlite3.connect('db/vulgate.db')
cursor = conn.cursor()

# Get the Gita book ID
cursor.execute("SELECT id FROM books WHERE source = 'gita' AND name LIKE '%Gita%'")
book_result = cursor.fetchone()

if book_result:
    book_id = book_result[0]
    
    # Check if verse 2:47 already exists
    cursor.execute("SELECT id FROM verses WHERE book_id = ? AND chapter = 2 AND verse_number = 47", (book_id,))
    existing = cursor.fetchone()
    
    if existing:
        print("⚠️ Verse 2:47 already exists")
    else:
        # Add the famous karma yoga verse
        verse_text = """कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥

karmaṇy evādhikāras te mā phaleṣu kadācana
mā karma-phala-hetur bhūr mā te saṅgo 'stv akarmaṇi

You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty."""

        cursor.execute("""
            INSERT INTO verses (book_id, chapter, verse_number, text, created_at) 
            VALUES (?, ?, ?, ?, ?)
        """, (book_id, 2, 47, verse_text, datetime.now()))
        
        print("✅ Added Bhagavad Gita 2:47 - The famous karma yoga verse!")
        
        # Also add a few more key verses while we're at it
        additional_verses = [
            (2, 11, """अशोच्यानन्वशोचस्त्वं प्रज्ञावादांश्च भाषसे।
गतासूनगतासूंश्च नानुशोचन्ति पण्डिताः॥

aśocyān anvaśocas tvaṃ prajñā-vādāṃś ca bhāṣase
gatāsūn agatāsūṃś ca nānuśocanti paṇḍitāḥ

You grieve for those who are not to be grieved for, yet you speak words of wisdom. The wise grieve neither for the living nor for the dead."""),
            
            (4, 7, """यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥

yadā yadā hi dharmasya glānir bhavati bhārata
abhyutthānam adharmasya tadātmānaṃ sṛjāmy aham

Whenever and wherever there is a decline in religious practice, O descendant of Bharata, and a predominant rise of irreligion—at that time I descend Myself."""),
            
            (4, 8, """परित्राणाय साधूनां विनाशाय च दुष्कृताम्।
धर्मसंस्थापनार्थाय सम्भवामि युगे युगे॥

paritrāṇāya sādhūnāṃ vināśāya ca duṣkṛtām
dharma-saṃsthāpanārthāya sambhavāmi yuge yuge

To deliver the pious and to annihilate the miscreants, as well as to reestablish the principles of religion, I Myself appear, millennium after millennium.""")
        ]
        
        for chapter, verse_num, text in additional_verses:
            cursor.execute("SELECT id FROM verses WHERE book_id = ? AND chapter = ? AND verse_number = ?", 
                         (book_id, chapter, verse_num))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO verses (book_id, chapter, verse_number, text, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                """, (book_id, chapter, verse_num, text, datetime.now()))
                print(f"✅ Added verse {chapter}:{verse_num}")
    
    conn.commit()
    print(f"\n🎉 Verses added successfully!")
    print("\n🧪 Test the new verses:")
    print("curl http://localhost:8000/api/v1/texts/gita/a/2/47")
    print("curl http://localhost:8000/api/v1/texts/gita/a/4/7")
    print("curl http://localhost:8000/api/v1/texts/gita/a/4/8")
    
else:
    print("❌ Gita book not found")

conn.close() 