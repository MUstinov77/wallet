"""Add user api token

Revision ID: 9c7f13bd7f02
Revises: 201d427411ab
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c7f13bd7f02'
down_revision: Union[str, Sequence[str], None] = '201d427411ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column(
            'hashed_api_token',
            sa.String(),
            nullable=False,
            comment="SHA-256 hash of the opaque bearer token issued to the user at signup.",
        ),
    )
    op.create_unique_constraint('uq_users_hashed_api_token', 'users', ['hashed_api_token'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_users_hashed_api_token', 'users', type_='unique')
    op.drop_column('users', 'hashed_api_token')
