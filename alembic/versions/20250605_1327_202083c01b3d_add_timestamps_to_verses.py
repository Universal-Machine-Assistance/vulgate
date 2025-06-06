"""add timestamps to verses

Revision ID: 202083c01b3d
Revises: 5f0235d62d55
Create Date: 2025-06-05 13:27:00.000000

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '202083c01b3d'
down_revision: Union[str, None] = '5f0235d62d55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # For SQLite, we need to:
    # 1. Create a new table with the desired schema
    # 2. Copy data from the old table
    # 3. Drop the old table
    # 4. Rename the new table to the original name
    
    # Create new table with timestamp columns
    op.create_table(
        'verses_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.Column('chapter', sa.Integer(), nullable=True),
        sa.Column('verse_number', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('translation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO verses_new (id, book_id, chapter, verse_number, text, translation, created_at)
        SELECT id, book_id, chapter, verse_number, text, translation, CURRENT_TIMESTAMP
        FROM verses
    """)
    
    # Drop old table
    op.drop_table('verses')
    
    # Rename new table to original name
    op.rename_table('verses_new', 'verses')
    
    # Recreate indexes
    op.create_index(op.f('ix_verses_id'), 'verses', ['id'], unique=False)

def downgrade() -> None:
    # Create new table without timestamp columns
    op.create_table(
        'verses_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.Column('chapter', sa.Integer(), nullable=True),
        sa.Column('verse_number', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('translation', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from new table to old table
    op.execute("""
        INSERT INTO verses_old (id, book_id, chapter, verse_number, text, translation)
        SELECT id, book_id, chapter, verse_number, text, translation
        FROM verses
    """)
    
    # Drop new table
    op.drop_table('verses')
    
    # Rename old table to original name
    op.rename_table('verses_old', 'verses')
    
    # Recreate indexes
    op.create_index(op.f('ix_verses_id'), 'verses', ['id'], unique=False)
