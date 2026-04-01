"""add chunk embeddings

Revision ID: 0282135a117f
Revises: d19c80c2de8e
Create Date: 2026-04-01 20:22:38.403578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '0282135a117f'
down_revision: Union[str, Sequence[str], None] = 'd19c80c2de8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "document_chunks",
        sa.Column("embedding", Vector(768), nullable=True),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("document_chunks", "embedding") # Remove the embedding column from document_chunks table
