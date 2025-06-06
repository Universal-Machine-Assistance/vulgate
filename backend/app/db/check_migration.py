from sqlalchemy import func
from backend.app.db.session import SessionLocal
from backend.app.db.models import Book, Verse, Word, VerseWord

def check_migration():
    db = SessionLocal()
    try:
        # Count books
        book_count = db.query(func.count(Book.id)).scalar()
        print(f"\nTotal books: {book_count}")
        
        # List books with verse counts
        books = db.query(Book).all()
        for book in books:
            verse_count = db.query(func.count(Verse.id)).filter(Verse.book_id == book.id).scalar()
            print(f"Book: {book.name}, Verses: {verse_count}, Chapters: {book.chapter_count}")
        
        # Count words and verse-word relationships
        word_count = db.query(func.count(Word.id)).scalar()
        verse_word_count = db.query(func.count(VerseWord.verse_id)).scalar()
        print(f"\nTotal words: {word_count}")
        print(f"Total verse-word relationships: {verse_word_count}")
        
        # Show some sample verses
        print("\nSample verses:")
        verses = db.query(Verse).join(Book).limit(5).all()
        for verse in verses:
            print(f"{verse.book.name} {verse.chapter}:{verse.verse_number} - {verse.text[:50]}...")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_migration() 