"""add document chunks

Revision ID: e9a5f2d384b1
Revises: c741ec52a801
Create Date: 2026-07-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e9a5f2d384b1"
down_revision: Union[str, Sequence[str], None] = "c741ec52a801"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "document_chunks"

    if table_name not in inspector.get_table_names():
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("chunk_id", sa.String(length=36), nullable=False),
            sa.Column("document_id", sa.Integer(), nullable=False),
            sa.Column("vector_id", sa.String(length=100), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("page_number", sa.Integer(), nullable=True),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column(
                "metadata",
                postgresql.JSONB(astext_type=sa.Text()),
                server_default=sa.text("'{}'::jsonb"),
                nullable=False,
            ),
            sa.Column(
                "search_vector",
                postgresql.TSVECTOR(),
                sa.Computed(
                    "to_tsvector('english'::regconfig, coalesce(content, ''::text))",
                    persisted=True,
                ),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["document_id"],
                ["documents.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    index_names = {
        index["name"]
        for index in inspector.get_indexes(table_name)
    }

    indexes = (
        ("ix_document_chunks_id", ["id"], False, None),
        ("ix_document_chunks_chunk_id", ["chunk_id"], True, None),
        ("ix_document_chunks_document_id", ["document_id"], False, None),
        ("ix_document_chunks_vector_id", ["vector_id"], True, None),
        (
            "ix_document_chunks_search_vector",
            ["search_vector"],
            False,
            "gin",
        ),
    )

    for name, columns, unique, using in indexes:
        if name not in index_names:
            op.create_index(
                name,
                table_name,
                columns,
                unique=unique,
                postgresql_using=using,
            )


def downgrade() -> None:
    op.drop_table("document_chunks")
