"""add password reset otps

Revision ID: c741ec52a801
Revises: 80ad75aec9dc
Create Date: 2026-07-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c741ec52a801"
down_revision: Union[str, Sequence[str], None] = "80ad75aec9dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = "password_reset_otps"

    if table_name not in inspector.get_table_names():
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("otp_digest", sa.String(length=64), nullable=False),
            sa.Column(
                "attempts",
                sa.Integer(),
                server_default="0",
                nullable=False,
            ),
            sa.Column(
                "expires_at",
                sa.DateTime(timezone=True),
                nullable=False,
            ),
            sa.Column(
                "verified_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "used_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    index_names = {
        index["name"]
        for index in inspector.get_indexes(table_name)
    }

    if "ix_password_reset_otps_id" not in index_names:
        op.create_index(
            op.f("ix_password_reset_otps_id"),
            table_name,
            ["id"],
            unique=False,
        )

    if "ix_password_reset_otps_user_id" not in index_names:
        op.create_index(
            op.f("ix_password_reset_otps_user_id"),
            table_name,
            ["user_id"],
            unique=False,
        )

    op.alter_column(
        table_name,
        "attempts",
        existing_type=sa.Integer(),
        server_default=sa.text("0"),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_password_reset_otps_user_id"),
        table_name="password_reset_otps",
    )
    op.drop_index(
        op.f("ix_password_reset_otps_id"),
        table_name="password_reset_otps",
    )
    op.drop_table("password_reset_otps")
