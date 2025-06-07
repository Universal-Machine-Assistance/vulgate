import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.init_db import init_db, init_books
from backend.app.db.session import SessionLocal

def main():
    print("Initializing database...")
    init_db()
    db = SessionLocal()
    try:
        init_books(db)
        print("Database initialized successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    main() 