"""add thumbnail_path to files

Revision ID: 001
Revises:
Create Date: 2025-12-16 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add thumbnail_path column to files table
    op.add_column('files', sa.Column('thumbnail_path', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    # Remove thumbnail_path column from files table
    op.drop_column('files', 'thumbnail_path')
