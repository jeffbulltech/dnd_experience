"""Add character_drafts table for builder workflow.

Revision ID: e6c0d1b4c2f2
Revises: 20241109_01_initial_schema
Create Date: 2025-02-09 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e6c0d1b4c2f2"
down_revision: str | None = "20241109_01_initial_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "character_drafts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_id", sa.Integer(), sa.ForeignKey("characters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("current_step", sa.String(length=50), nullable=True),
        sa.Column("starting_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("allow_feats", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("variant_flags", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("step_data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_character_drafts_user_id", "character_drafts", ["user_id"])
    op.create_index("ix_character_drafts_status", "character_drafts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_character_drafts_status", table_name="character_drafts")
    op.drop_index("ix_character_drafts_user_id", table_name="character_drafts")
    op.drop_table("character_drafts")

