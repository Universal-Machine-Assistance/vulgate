#!/usr/bin/env python3
"""
Script to populate word-verse relationships in the database.
This ensures the word occurrence lookup functionality works properly.
"""

import sys
import os
import re
import time
from typing import List, Dict
from sqlalchemy.orm import Session

# Add the backend app to the path
sys.path.append('.')
sys.path.append('./backend')

from backend.app.db.session import SessionLocal
from backend.app.db.models import Book, Verse, Word, VerseWord

def normalize_word(word: str) -> str:
    """Normalize a Latin word for consistent storage"""
    # Remove punctuation and convert to lowercase
    word = re.sub(r'[^\w]', '', word.lower())
    return word

def extract_words_from_text(text: str) -> List[str]:
    """Extract normalized words from verse text"""
    # Find all words (sequences of letters)
    words = re.findall(r'\b[a-zA-Zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]+\b', text)
    return [normalize_word(word) for word in words if len(word) > 1]

def populate_word_relationships():
    """Populate word-verse relationships for all verses in the database"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting word-verse relationship population...")
        print("=" * 60)
        
        # Get all verses
        verses = db.query(Verse).join(Book).all()
        total_verses = len(verses)
        
        if total_verses == 0:
            print("❌ No verses found in database. Please run the Vulgate migration first.")
            return
        
        print(f"📖 Found {total_verses} verses to process")
        
        # Statistics
        words_created = 0
        relationships_created = 0
        verses_processed = 0
        
        for i, verse in enumerate(verses, 1):
            try:
                # Extract words from verse text
                words_in_verse = extract_words_from_text(verse.text)
                
                # Track word positions in this verse
                word_positions = {}
                position = 1
                
                for word_text in words_in_verse:
                    if not word_text:
                        continue
                    
                    # Get or create word
                    word = db.query(Word).filter(Word.latin_text == word_text).first()
                    if not word:
                        word = Word(
                            latin_text=word_text,
                            frequency=1,
                            difficulty_level=1
                        )
                        db.add(word)
                        db.flush()  # Get the ID
                        words_created += 1
                    else:
                        # Update frequency
                        word.frequency += 1
                    
                    # Track first occurrence position for this word in this verse
                    if word_text not in word_positions:
                        word_positions[word_text] = position
                        position += 1
                    
                    # Check if relationship already exists
                    existing_relationship = db.query(VerseWord).filter(
                        VerseWord.verse_id == verse.id,
                        VerseWord.word_id == word.id
                    ).first()
                    
                    if not existing_relationship:
                        # Create verse-word relationship
                        verse_word = VerseWord(
                            verse_id=verse.id,
                            word_id=word.id,
                            position=word_positions[word_text],
                            is_highlighted=0
                        )
                        db.add(verse_word)
                        relationships_created += 1
                
                verses_processed += 1
                
                # Commit every 100 verses to avoid memory issues
                if i % 100 == 0:
                    db.commit()
                    print(f"   ✅ Processed {i}/{total_verses} verses...")
                
                # Progress indicator every 1000 verses
                if i % 1000 == 0:
                    print(f"📊 Progress: {i}/{total_verses} verses - {words_created} words created, {relationships_created} relationships")
                    
            except Exception as e:
                print(f"   ❌ Error processing verse {verse.id}: {e}")
                continue
        
        # Final commit
        db.commit()
        
        print("\n" + "=" * 60)
        print("📊 POPULATION COMPLETE")
        print("=" * 60)
        print(f"📖 Verses processed: {verses_processed}")
        print(f"📝 Words created: {words_created}")
        print(f"🔗 Relationships created: {relationships_created}")
        
        # Final statistics
        total_words = db.query(Word).count()
        total_relationships = db.query(VerseWord).count()
        
        print(f"\n💾 FINAL DATABASE STATISTICS:")
        print(f"📚 Total books: {db.query(Book).count()}")
        print(f"📖 Total verses: {total_verses}")
        print(f"📝 Total words: {total_words}")
        print(f"🔗 Total word-verse relationships: {total_relationships}")
        
        # Show some examples
        print(f"\n🎯 EXAMPLE WORD OCCURRENCES:")
        example_words = ['deus', 'et', 'in', 'dominus']
        
        for word_text in example_words:
            word = db.query(Word).filter(Word.latin_text == word_text).first()
            if word:
                count = db.query(VerseWord).filter(VerseWord.word_id == word.id).count()
                print(f"   '{word_text}': {count} occurrences")
        
        print(f"\n🎉 Word-verse relationship population completed!")
        print("🔍 You can now use the word lookup API to find all occurrences of any word")
        
    except Exception as e:
        print(f"❌ Fatal error during population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_relationships():
    """Verify that word relationships are working correctly"""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verifying word relationships...")
        
        # Test a few common words
        test_words = ['deus', 'et', 'in', 'dominus', 'jesus']
        
        for word_text in test_words:
            word = db.query(Word).filter(Word.latin_text == word_text).first()
            if word:
                # Get verses for this word
                verse_words = db.query(VerseWord, Verse, Book).join(
                    Verse, VerseWord.verse_id == Verse.id
                ).join(
                    Book, Verse.book_id == Book.id
                ).filter(
                    VerseWord.word_id == word.id
                ).limit(3).all()
                
                print(f"\n📝 Word: '{word_text}' (frequency: {word.frequency})")
                for verse_word, verse, book in verse_words:
                    reference = f"{book.name} {verse.chapter}:{verse.verse_number}"
                    print(f"   📖 {reference}: {verse.text[:80]}...")
                    
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--verify-only':
        verify_relationships()
    else:
        populate_word_relationships()
        verify_relationships()

if __name__ == "__main__":
    main() 