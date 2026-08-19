"""add document_chunks table for RAG assistant

Revision ID: a1b2c3d4e5f6
Revises: 0d648b210f35
Create Date: 2026-08-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0d648b210f35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_ref", sa.String(length=255), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_document_chunks_source_type", "document_chunks", ["source_type"])
    op.create_index("ix_document_chunks_company_id", "document_chunks", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_document_chunks_company_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_source_type", table_name="document_chunks")
    op.drop_table("document_chunks")
