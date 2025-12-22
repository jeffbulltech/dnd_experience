"""add adventure_template_id to campaigns

Revision ID: add_adventure_template_id
Revises: 0d9db24cfe6c
Create Date: 2025-12-22 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "add_adventure_template_id"
down_revision: str = "0d9db24cfe6c"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("adventure_template_id", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("campaigns", "adventure_template_id")
