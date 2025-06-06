from backend.app.db.base_class import Base
from backend.app.db.session import engine
from backend.app.db.models import *  # noqa

def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 