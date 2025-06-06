import re
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.db.models import Book, Verse, Word, VerseWord
from backend.app.db.session import SessionLocal, engine
from backend.app.db.base_class import Base

def parse_vulgate_line(line: str) -> tuple[str, int, int, str]:
    """Parse a line from the Vulgate text file.
    Expected format: 'Book Chapter Verse Text' with variable spacing
    Returns: (book_name, chapter, verse, text)"""
    # Remove extra spaces and normalize
    line = ' '.join(line.strip().split())
    
    # Print detailed information about the line
    print(f"\nAttempting to parse line: '{line}'")
    print(f"Line length: {len(line)}")
    print(f"First 50 chars: '{line[:50]}'")
    
    # Match pattern like "Ap 6 17 quóniam venit dies magnus iræ ipsórum..."
    match = re.match(r'^(\w+)\s+(\d+)\s+(\d+)\s+(.+)$', line)
    if not match:
        print(f"Failed to match pattern. Line parts:")
        parts = line.split()
        print(f"Number of parts: {len(parts)}")
        print(f"Parts: {parts}")
        raise ValueError(f"Invalid line format: {line}")
    
    book_name, chapter, verse, text = match.groups()
    return book_name, int(chapter), int(verse), text.strip()

def get_or_create_book(db: Session, name: str) -> Book:
    """Get or create a book in the database."""
    book = db.query(Book).filter(Book.name == name).first()
    if not book:
        book = Book(
            name=name,
            latin_name=name,  # We'll update this later if needed
            chapter_count=0  # We'll update this after processing all verses
        )
        db.add(book)
        db.commit()
        db.refresh(book)
    return book

def process_vulgate_file(file_path: str, db: Session):
    """Process the Vulgate text file and populate the database."""
    # Dictionary to track chapter counts per book
    book_chapters = {}
    # Dictionary to track word frequencies
    word_frequencies = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            try:
                book_name, chapter, verse, text = parse_vulgate_line(line)
                
                # Update book chapter count
                if book_name not in book_chapters:
                    book_chapters[book_name] = set()
                book_chapters[book_name].add(chapter)
                
                # Get or create book
                book = get_or_create_book(db, book_name)
                
                # Check if verse already exists
                existing_verse = db.query(Verse).filter(
                    Verse.book_id == book.id,
                    Verse.chapter == chapter,
                    Verse.verse_number == verse
                ).first()
                
                if existing_verse:
                    verse_obj = existing_verse
                else:
                    # Create verse only if it doesn't exist
                    verse_obj = Verse(
                        book_id=book.id,
                        chapter=chapter,
                        verse_number=verse,
                        text=text
                    )
                    db.add(verse_obj)
                    db.flush()  # Flush to get verse.id
                
                # Process words
                words = re.findall(r'\b\w+\b', text.lower())
                seen_word_ids = set()
                for position, word_text in enumerate(words, 1):
                    # Update word frequency
                    word_frequencies[word_text] = word_frequencies.get(word_text, 0) + 1
                    
                    # Get or create word
                    word = db.query(Word).filter(Word.latin_text == word_text).first()
                    if not word:
                        word = Word(latin_text=word_text)
                        db.add(word)
                        db.flush()
                    
                    # Only insert the first occurrence of each word in this verse
                    if word.id in seen_word_ids:
                        continue
                    seen_word_ids.add(word.id)
                    
                    # Check if verse-word relationship already exists
                    existing_verse_word = db.query(VerseWord).filter(
                        VerseWord.verse_id == verse_obj.id,
                        VerseWord.word_id == word.id
                    ).first()
                    
                    if not existing_verse_word:
                        # Create verse-word relationship only if it doesn't exist
                        verse_word = VerseWord(
                            verse_id=verse_obj.id,
                            word_id=word.id,
                            position=position
                        )
                        db.add(verse_word)
                
                # Commit every 100 verses to avoid memory issues
                if verse % 100 == 0:
                    db.commit()
                    
            except ValueError as e:
                print(f"Error processing line: {e}")
                continue
    
    # Update book chapter counts
    for book_name, chapters in book_chapters.items():
        book = db.query(Book).filter(Book.name == book_name).first()
        if book:
            book.chapter_count = len(chapters)
    
    # Update word frequencies
    for word_text, frequency in word_frequencies.items():
        word = db.query(Word).filter(Word.latin_text == word_text).first()
        if word:
            word.frequency = frequency
    
    # Final commit
    db.commit()

def reset_database():
    """Drop all tables and recreate them."""
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

def main():
    vulgate_file = Path("/Users/guillermomolina/dev/vulgate/source/vulgate_with_accents.txt")
    if not vulgate_file.exists():
        print(f"Error: Vulgate file not found at {vulgate_file}")
        return
    
    # Reset database before migration
    reset_database()
    
    db = SessionLocal()
    try:
        print("Starting Vulgate migration...")
        process_vulgate_file(str(vulgate_file), db)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 