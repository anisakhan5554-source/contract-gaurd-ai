"""add fulltext search to precedent_clauses

Revision ID: d4543ffb3ac0
Revises: 99c0c09f5576
Create Date: 2026-09-08 02:55:21.900419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4543ffb3ac0'
down_revision: Union[str, None] = '99c0c09f5576'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE precedent_clauses ADD COLUMN text_search tsvector
        GENERATED ALWAYS AS (to_tsvector('english', text)) STORED;
    """)
    op.execute("""
        CREATE INDEX idx_precedent_clauses_text_search 
        ON precedent_clauses USING GIN (text_search);
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_precedent_clauses_text_search;")
    op.execute("ALTER TABLE precedent_clauses DROP COLUMN IF EXISTS text_search;")