"""add document access roles

Revision ID: f4c8a7b6d210
Revises: e9a5f2d384b1
Create Date: 2026-07-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f4c8a7b6d210"
down_revision: Union[str, Sequence[str], None] = "e9a5f2d384b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "document_access_roles"

    if table_name not in inspector.get_table_names():
        op.create_table(
            table_name,
            sa.Column("document_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.CheckConstraint(
                "role IN ('admin', 'sales', 'manager')",
                name="ck_document_access_roles_valid_role",
            ),
            sa.ForeignKeyConstraint(
                ["document_id"],
                ["documents.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("document_id", "role"),
        )

    inspector = sa.inspect(bind)
    index_names = {
        index["name"]
        for index in inspector.get_indexes(table_name)
    }
    if "ix_document_access_roles_role" not in index_names:
        op.create_index(
            "ix_document_access_roles_role",
            table_name,
            ["role"],
            unique=False,
        )

    op.execute(
        """
        INSERT INTO document_access_roles (document_id, role)
        SELECT
            documents.id,
            lower(btrim(split_roles.role))
        FROM documents
        CROSS JOIN LATERAL regexp_split_to_table(
            coalesce(documents.allowed_roles, ''),
            ','
        ) AS split_roles(role)
        WHERE lower(btrim(split_roles.role))
            IN ('admin', 'sales', 'manager')
        ON CONFLICT (document_id, role) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_table("document_access_roles")
