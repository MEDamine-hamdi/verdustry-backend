"""add email_verified to users
Revision ID: 7216f5198bb8
Revises: f6144bac9b42
Create Date: 2026-07-24 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7216f5198bb8'
down_revision: Union[str, Sequence[str], None] = 'f6144bac9b42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('users', 'email_verified')