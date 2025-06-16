#!/usr/bin/env python3
"""
Script to create local Bhagavad Gita database
This replaces the RapidAPI approach with local data storage
"""

import sqlite3
import json
from datetime import datetime

# Sample Bhagavad Gita data - Chapter 1, first few verses
# This is a minimal dataset to get started - can be expanded later
GITA_DATA = {
    "chapters": [
        {
            "chapter_number": 1,
            "name": "Arjuna Vishada Yoga",
            "name_transliterated": "Arjuna Vishada Yoga",
            "name_translated": "The Yoga of Arjuna's Dejection",
            "verses_count": 47,
            "chapter_summary": "The first chapter of the Bhagavad Gita - Arjuna Vishada Yoga introduces the setup, the setting, the characters and the circumstances that led to the epic battle of Kurukshetra, fought between the Pandavas and the Kauravas."
        }
    ],
    "verses": [
        {
            "chapter_number": 1,
            "verse_number": 1,
            "text": "धृतराष्ट्र उवाच |\nधर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः |\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ||१||",
            "transliteration": "dhritarashtra uvacha\ndharma-kshetre kuru-kshetre samavetaa yuyutsavah\nmaamakaah paandavash-chaiva kim-akurvata sanjaya",
            "word_meanings": "dhritarashtra uvacha—Dhritarashtra said; dharma-kshetre—in the place of dharma; kuru-kshetre—in the land of the Kurus; samavetaah—having gathered; yuyutsavah—desiring to fight; maamakaah—my sons; paandavaah—the sons of Pandu; cha—and; eva—certainly; kim—what; akurvata—did they do; sanjaya—O Sanjaya",
            "translation": "Dhritarashtra said: O Sanjaya, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do?"
        },
        {
            "chapter_number": 1,
            "verse_number": 2,
            "text": "सञ्जय उवाच |\nदृष्ट्वा तु पाण्डवानीकं व्यूढं दुर्योधनस्तदा |\nआचार्यमुपसङ्गम्य राजा वचनमब्रवीत् ||२||",
            "transliteration": "sanjaya uvacha\ndrishtvaa tu paandavaaniikam vyoodham duryodhanas-tadaa\naacharyam-upasangamya raajaa vachanam-abraveet",
            "word_meanings": "sanjaya uvacha—Sanjaya said; drishtvaa—on seeing; tu—but; paandava-aniikam—the Pandava army; vyoodham—arranged in a military formation; duryodhanah—King Duryodhana; tadaa—at that time; aacharyam—the teacher; upasangamya—approaching; raajaa—the king; vachanam—words; abraveet—spoke",
            "translation": "Sanjaya said: On observing the Pandava army standing in military formation, King Duryodhana approached his teacher Dronacharya, and spoke the following words."
        },
        {
            "chapter_number": 1,
            "verse_number": 3,
            "text": "पश्यैतां पाण्डुपुत्राणामाचार्य महतीं चमूम् |\nव्यूढां द्रुपदपुत्रेण तव शिष्येण धीमता ||३||",
            "transliteration": "pashyaitaam paandu-putraanaam-aachaarya mahateem chamoom\nvyoodhaam drupada-putrena tava shishyena dhiimataa",
            "word_meanings": "pashya—behold; etaam—this; paandu-putraanaam—of the sons of Pandu; aachaarya—O teacher; mahateem—mighty; chamoom—army; vyoodhaam—arrayed; drupada-putrena—by the son of Drupada; tava—your; shishyena—disciple; dhii-mataa—intelligent",
            "translation": "Duryodhana said: Behold, O teacher, this mighty army of the sons of Pandu, so expertly arranged by your intelligent disciple, the son of Drupada."
        }
    ]
}

def create_gita_database():
    """Create and populate the Bhagavad Gita database"""
    
    # Connect to the main database
    conn = sqlite3.connect('db/vulgate.db')
    cursor = conn.cursor()
    
    try:
        # Add the Bhagavad Gita as a "book" in our system
        # Using "a" as the abbreviation to maintain consistency with our unified API
        cursor.execute("""
            INSERT OR REPLACE INTO books 
            (name, latin_name, abbreviation, source, source_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Bhagavad Gita",
            "Bhagavad Gita", 
            "a",
            "gita",
            "bhagavad_gita",
            datetime.now(),
            datetime.now()
        ))
        
        book_id = cursor.lastrowid
        print(f"Created Bhagavad Gita book with ID: {book_id}")
        
        # Add verses
        for verse_data in GITA_DATA["verses"]:
            cursor.execute("""
                INSERT OR REPLACE INTO verses 
                (book_id, chapter, verse_number, text, translation, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                book_id,
                verse_data["chapter_number"],
                verse_data["verse_number"],
                verse_data["text"],
                verse_data["translation"],
                datetime.now(),
                datetime.now()
            ))
        
        conn.commit()
        print(f"Added {len(GITA_DATA['verses'])} verses to the database")
        
        # Verify the data
        cursor.execute("""
            SELECT COUNT(*) FROM verses 
            WHERE book_id = ? 
        """, (book_id,))
        
        count = cursor.fetchone()[0]
        print(f"Verification: {count} verses found in database")
        
        return True
        
    except Exception as e:
        print(f"Error creating Gita database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def expand_gita_data():
    """
    Function to expand the Gita data with more verses
    This can be called later to add more chapters and verses
    """
    # This is where we can add more chapters and verses
    # For now, we'll keep it simple with just a few verses
    pass

if __name__ == "__main__":
    print("Creating local Bhagavad Gita database...")
    success = create_gita_database()
    
    if success:
        print("✅ Bhagavad Gita database created successfully!")
        print("You can now access Gita verses via: /api/v1/texts/gita/a/1/1")
    else:
        print("❌ Failed to create Bhagavad Gita database") 