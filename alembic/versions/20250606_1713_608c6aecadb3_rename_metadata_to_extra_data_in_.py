"""Rename metadata to extra_data in analysis_history and analysis_queue

Revision ID: 608c6aecadb3
Revises: d731b48adffd
Create Date: 2025-06-06 17:13:39.153422+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '608c6aecadb3'
down_revision: Union[str, None] = 'd731b48adffd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata column to extra_data in analysis_history table
    with op.batch_alter_table('analysis_history') as batch_op:
        batch_op.alter_column('metadata', new_column_name='extra_data')
    
    # Rename metadata column to extra_data in analysis_queue table
    with op.batch_alter_table('analysis_queue') as batch_op:
        batch_op.alter_column('metadata', new_column_name='extra_data')


def downgrade() -> None:
    # Revert extra_data column back to metadata in analysis_history table
    with op.batch_alter_table('analysis_history') as batch_op:
        batch_op.alter_column('extra_data', new_column_name='metadata')
    
    # Revert extra_data column back to metadata in analysis_queue table
    with op.batch_alter_table('analysis_queue') as batch_op:
        batch_op.alter_column('extra_data', new_column_name='metadata')
