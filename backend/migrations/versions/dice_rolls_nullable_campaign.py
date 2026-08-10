"""make dice_rolls.campaign_id nullable

Revision ID: dice_rolls_nullable_campaign
Revises: add_adventure_template_id
Create Date: 2026-08-09 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "dice_rolls_nullable_campaign"
down_revision: str = "add_adventure_template_id"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("dice_rolls", "campaign_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("dice_rolls", "campaign_id", existing_type=sa.Integer(), nullable=False)
