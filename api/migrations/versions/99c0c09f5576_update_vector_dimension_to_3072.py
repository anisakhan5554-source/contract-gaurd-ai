"""update vector dimension to 3072

Revision ID: 99c0c09f5576
Revises: c426567c5c79
Create Date: 2026-09-05 10:02:28.774354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import  pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '99c0c09f5576'
down_revision: Union[str, None] = 'c426567c5c79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('clauses', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=3072),
               existing_nullable=True)
    op.alter_column('precedent_clauses', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=3072),
               existing_nullable=True)


def downgrade() -> None:
    op.alter_column('precedent_clauses', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=3072),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               existing_nullable=True)
    op.alter_column('clauses', 'embedding',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=3072),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=1536),
               existing_nullable=True)
