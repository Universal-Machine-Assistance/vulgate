"""add_abbreviation_to_books

Revision ID: 42ac8d495dfa
Revises: 8992f07db535
Create Date: 2024-06-06 23:09:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42ac8d495dfa'
down_revision: Union[str, None] = '8992f07db535'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create new table with abbreviation column
    op.create_table(
        'books_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('latin_name', sa.String(100), nullable=False),
        sa.Column('abbreviation', sa.String(10), nullable=False),
        sa.Column('chapter_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO books_new (id, name, latin_name, chapter_count, created_at, abbreviation)
        SELECT id, name, latin_name, chapter_count, created_at,
        CASE 
            WHEN name = 'Genesis' THEN 'Gn'
            WHEN name = 'Exodus' THEN 'Ex'
            WHEN name = 'Leviticus' THEN 'Lv'
            WHEN name = 'Numbers' THEN 'Nm'
            WHEN name = 'Deuteronomy' THEN 'Dt'
            WHEN name = 'Joshua' THEN 'Jos'
            WHEN name = 'Judges' THEN 'Jgs'
            WHEN name = 'Ruth' THEN 'Ru'
            WHEN name = '1 Samuel' THEN '1Sm'
            WHEN name = '2 Samuel' THEN '2Sm'
            WHEN name = '1 Kings' THEN '1Kgs'
            WHEN name = '2 Kings' THEN '2Kgs'
            WHEN name = '1 Chronicles' THEN '1Chr'
            WHEN name = '2 Chronicles' THEN '2Chr'
            WHEN name = 'Ezra' THEN 'Ezr'
            WHEN name = 'Nehemiah' THEN 'Neh'
            WHEN name = 'Tobit' THEN 'Tb'
            WHEN name = 'Judith' THEN 'Jdt'
            WHEN name = 'Esther' THEN 'Est'
            WHEN name = '1 Maccabees' THEN '1Mc'
            WHEN name = '2 Maccabees' THEN '2Mc'
            WHEN name = 'Job' THEN 'Jb'
            WHEN name = 'Psalms' THEN 'Ps'
            WHEN name = 'Proverbs' THEN 'Prv'
            WHEN name = 'Ecclesiastes' THEN 'Eccl'
            WHEN name = 'Song of Songs' THEN 'Sg'
            WHEN name = 'Wisdom' THEN 'Wis'
            WHEN name = 'Sirach' THEN 'Sir'
            WHEN name = 'Isaiah' THEN 'Is'
            WHEN name = 'Jeremiah' THEN 'Jer'
            WHEN name = 'Lamentations' THEN 'Lam'
            WHEN name = 'Baruch' THEN 'Bar'
            WHEN name = 'Ezekiel' THEN 'Ez'
            WHEN name = 'Daniel' THEN 'Dn'
            WHEN name = 'Hosea' THEN 'Hos'
            WHEN name = 'Joel' THEN 'Jl'
            WHEN name = 'Amos' THEN 'Am'
            WHEN name = 'Obadiah' THEN 'Ob'
            WHEN name = 'Jonah' THEN 'Jon'
            WHEN name = 'Micah' THEN 'Mi'
            WHEN name = 'Nahum' THEN 'Na'
            WHEN name = 'Habakkuk' THEN 'Hab'
            WHEN name = 'Zephaniah' THEN 'Zep'
            WHEN name = 'Haggai' THEN 'Hg'
            WHEN name = 'Zechariah' THEN 'Zec'
            WHEN name = 'Malachi' THEN 'Mal'
            WHEN name = 'Matthew' THEN 'Mt'
            WHEN name = 'Mark' THEN 'Mk'
            WHEN name = 'Luke' THEN 'Lk'
            WHEN name = 'John' THEN 'Jn'
            WHEN name = 'Acts' THEN 'Acts'
            WHEN name = 'Romans' THEN 'Rom'
            WHEN name = '1 Corinthians' THEN '1Cor'
            WHEN name = '2 Corinthians' THEN '2Cor'
            WHEN name = 'Galatians' THEN 'Gal'
            WHEN name = 'Ephesians' THEN 'Eph'
            WHEN name = 'Philippians' THEN 'Phil'
            WHEN name = 'Colossians' THEN 'Col'
            WHEN name = '1 Thessalonians' THEN '1Thes'
            WHEN name = '2 Thessalonians' THEN '2Thes'
            WHEN name = '1 Timothy' THEN '1Tim'
            WHEN name = '2 Timothy' THEN '2Tim'
            WHEN name = 'Titus' THEN 'Ti'
            WHEN name = 'Philemon' THEN 'Phlm'
            WHEN name = 'Hebrews' THEN 'Heb'
            WHEN name = 'James' THEN 'Jas'
            WHEN name = '1 Peter' THEN '1Pt'
            WHEN name = '2 Peter' THEN '2Pt'
            WHEN name = '1 John' THEN '1Jn'
            WHEN name = '2 John' THEN '2Jn'
            WHEN name = '3 John' THEN '3Jn'
            WHEN name = 'Jude' THEN 'Jude'
            WHEN name = 'Revelation' THEN 'Rv'
            ELSE name
        END
        FROM books
    """)
    
    # Drop old table
    op.drop_table('books')
    
    # Rename new table to old table name
    op.rename_table('books_new', 'books')
    
    # Create indexes
    op.create_index(op.f('ix_books_abbreviation'), 'books', ['abbreviation'], unique=True)
    op.create_index(op.f('ix_books_name'), 'books', ['name'], unique=True)
    op.create_index(op.f('ix_books_latin_name'), 'books', ['latin_name'], unique=True)


def downgrade() -> None:
    # Create new table without abbreviation column
    op.create_table(
        'books_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('latin_name', sa.String(100), nullable=False),
        sa.Column('chapter_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO books_new (id, name, latin_name, chapter_count, created_at)
        SELECT id, name, latin_name, chapter_count, created_at
        FROM books
    """)
    
    # Drop old table
    op.drop_table('books')
    
    # Rename new table to old table name
    op.rename_table('books_new', 'books')
    
    # Create indexes
    op.create_index(op.f('ix_books_name'), 'books', ['name'], unique=True)
    op.create_index(op.f('ix_books_latin_name'), 'books', ['latin_name'], unique=True)
