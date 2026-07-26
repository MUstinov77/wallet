"""Add wallet balance non-negative check

Revision ID: 201d427411ab
Revises: c387d4f4c37d
Create Date: 2026-07-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '201d427411ab'
down_revision: Union[str, Sequence[str], None] = 'c387d4f4c37d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_wallets_balance_non_negative",
        "wallets",
        "balance >= 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_wallets_balance_non_negative", "wallets", type_="check")
