"""add source to books

Revision ID: add_source_to_books
Revises: 42ac8d495dfa
Create Date: 2025-01-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_source_to_books'
down_revision = '42ac8d495dfa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add source column to books table
    op.add_column('books', sa.Column('source', sa.String(length=50), nullable=True))
    op.add_column('books', sa.Column('source_id', sa.String(length=50), nullable=True))
    
    # Create index on source column
    op.create_index(op.f('ix_books_source'), 'books', ['source'], unique=False)
    
    # Update existing books to have 'bible' as the default source
    op.execute("UPDATE books SET source = 'bible' WHERE source IS NULL")
    
    # Make source column not nullable after populating existing data
    op.alter_column('books', 'source', nullable=False, server_default='bible')
    
    # Remove unique constraints from name and latin_name columns (they were removed in models.py)
    # These need to be removed because we may have books with same names from different sources
    try:
        op.drop_constraint('books_name_key', 'books', type_='unique')
    except:
        pass  # Constraint might not exist or have different name
    
    try:
        op.drop_constraint('books_latin_name_key', 'books', type_='unique')
    except:
        pass  # Constraint might not exist or have different name


def downgrade() -> None:
    # Remove the source columns
    op.drop_index(op.f('ix_books_source'), table_name='books')
    op.drop_column('books', 'source_id')
    op.drop_column('books', 'source')
    
    # Restore unique constraints
    op.create_unique_constraint('books_name_key', 'books', ['name'])
    op.create_unique_constraint('books_latin_name_key', 'books', ['latin_name']) 