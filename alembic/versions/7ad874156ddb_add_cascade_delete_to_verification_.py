"""add cascade delete to verification_tokens
Revision ID: 7ad874156ddb
Revises: 757b943e66ab
Create Date: 2026-07-30 00:14:43.790511
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7ad874156ddb'
down_revision: Union[str, Sequence[str], None] = '757b943e66ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('verification_tokens_user_id_fkey', 'verification_tokens', type_='foreignkey')
    op.create_foreign_key(
        'verification_tokens_user_id_fkey',
        'verification_tokens',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('verification_tokens_user_id_fkey', 'verification_tokens', type_='foreignkey')
    op.create_foreign_key(
        'verification_tokens_user_id_fkey',
        'verification_tokens',
        'users',
        ['user_id'],
        ['id'],
    )