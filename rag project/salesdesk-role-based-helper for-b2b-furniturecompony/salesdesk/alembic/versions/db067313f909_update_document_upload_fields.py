"""update document upload fields

Revision ID: db067313f909
Revises: 
Create Date: 2026-07-11 15:57:44.031658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db067313f909'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    document_status = sa.Enum(
        'UPLOADED',
        'PROCESSING',
        'READY',
        'FAILED',
        'ARCHIVED',
        name='document_status',
    )
    document_status.create(op.get_bind(), checkfirst=True)

    op.add_column('documents', sa.Column('original_filename', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('stored_filename', sa.String(), nullable=True))
    op.add_column('documents', sa.Column('file_extension', sa.String(length=20), nullable=True))
    op.add_column('documents', sa.Column('mime_type', sa.String(length=150), nullable=True))
    op.add_column('documents', sa.Column('size_bytes', sa.BigInteger(), nullable=True))
    op.add_column('documents', sa.Column('checksum_sha256', sa.String(length=64), nullable=True))
    op.add_column(
        'documents',
        sa.Column(
            'status',
            document_status,
            server_default='UPLOADED',
            nullable=False,
        ),
    )
    op.add_column('documents', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

    op.execute(
        """
        UPDATE documents
        SET
            original_filename = COALESCE(original_filename, document_name),
            stored_filename = COALESCE(stored_filename, 'legacy_' || id::text),
            file_extension = COALESCE(file_extension, ''),
            mime_type = COALESCE(mime_type, 'application/octet-stream'),
            size_bytes = COALESCE(size_bytes, 0),
            checksum_sha256 = COALESCE(checksum_sha256, repeat('0', 56) || lpad(id::text, 8, '0')),
            updated_at = COALESCE(updated_at, created_at, now())
        """
    )

    op.alter_column('documents', 'original_filename', nullable=False)
    op.alter_column('documents', 'stored_filename', nullable=False)
    op.alter_column('documents', 'file_extension', nullable=False)
    op.alter_column('documents', 'mime_type', nullable=False)
    op.alter_column('documents', 'size_bytes', nullable=False)
    op.alter_column('documents', 'checksum_sha256', nullable=False)
    op.create_index(op.f('ix_documents_checksum_sha256'), 'documents', ['checksum_sha256'], unique=False)
    op.create_unique_constraint('uq_documents_stored_filename', 'documents', ['stored_filename'])
    op.alter_column('documents', 'status', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_documents_stored_filename', 'documents', type_='unique')
    op.drop_index(op.f('ix_documents_checksum_sha256'), table_name='documents')
    op.drop_column('documents', 'updated_at')
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'status')
    op.drop_column('documents', 'checksum_sha256')
    op.drop_column('documents', 'size_bytes')
    op.drop_column('documents', 'mime_type')
    op.drop_column('documents', 'file_extension')
    op.drop_column('documents', 'stored_filename')
    op.drop_column('documents', 'original_filename')
    sa.Enum(name='document_status').drop(op.get_bind(), checkfirst=True)
