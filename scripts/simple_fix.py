import sqlite3
import json

# Direct paths
db_path = "/Users/guillermomolina/dev/vulgate/db/vulgate.db" 
json_path = "/Users/guillermomolina/dev/vulgate/gita_verses.json"

try:
    # Load JSON
    with open(json_path, 'r') as f:
        verses = json.load(f)
    
    # Find verse 6
    verse_6 = None
    for v in verses:
        if v.get('chapter_number') == 1 and v.get('verse_number') == 6:
            verse_6 = v
            break
    
    if verse_6:
        print("Found verse 6 in JSON")
        
        # Check transliteration
        transliteration = verse_6.get('transliteration', '')
        if 'yudhāmanyuśhcha' in transliteration:
            print("Transliteration is complete!")
            
            # Format text
            text = f"""Bhagavad Gita Chapter 1, Verse 6

Sanskrit:
{verse_6['text']}

Transliteration:
{verse_6['transliteration']}

Word Meanings:
{verse_6['word_meanings']}

English Translation:
Yudhamanyu the courageous, Uttamauja the valiant, the son of Subhadra (Abhimanyu), and the sons of Draupadi—all of them are great chariot warriors."""
            
            # Update database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Find Gita book
            cursor.execute("SELECT id FROM books WHERE source = 'gita'")
            book_id = cursor.fetchone()[0]
            
            # Update verse
            cursor.execute("""
                UPDATE verses SET text = ? 
                WHERE book_id = ? AND chapter = 1 AND verse_number = 6
            """, (text, book_id))
            
            conn.commit()
            conn.close()
            
            print("Updated verse 6 in database!")
        else:
            print("ERROR: Transliteration still incomplete")
    else:
        print("ERROR: Verse 6 not found")
        
except Exception as e:
    print(f"Error: {e}") 