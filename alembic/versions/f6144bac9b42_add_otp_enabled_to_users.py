"""add otp_enabled to users
Revision ID: f6144bac9b42
Revises: d5875ccc4962
Create Date: 2026-07-24 11:11:53.981226
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f6144bac9b42'
down_revision: Union[str, Sequence[str], None] = 'd5875ccc4962'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('otp_enabled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('users', 'otp_enabled')