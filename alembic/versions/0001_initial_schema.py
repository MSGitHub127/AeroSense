"""Initial schema for family_profiles and averted_actions tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-23 16:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create family_profiles and averted_actions tables."""
    op.create_table(
        "family_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("household_name", sa.String(length=120), nullable=False),
        sa.Column("location_city", sa.String(length=120), nullable=False),
        sa.Column("home_type", sa.String(length=50), nullable=False, server_default="apartment"),
        sa.Column("estimated_baseline_aqi", sa.Integer(), nullable=False, server_default="180"),
        sa.Column("encrypted_details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_family_profiles_session_id", "family_profiles", ["session_id"])
    op.create_index("ix_family_profiles_location_city", "family_profiles", ["location_city"])

    op.create_table(
        "averted_actions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.String(length=36), nullable=False),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("pm25_avoided_ug", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("co2_saved_kg", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["family_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_averted_actions_profile_id", "averted_actions", ["profile_id"])


def downgrade() -> None:
    """Drop family_profiles and averted_actions tables."""
    op.drop_index("ix_averted_actions_profile_id", table_name="averted_actions")
    op.drop_table("averted_actions")
    op.drop_index("ix_family_profiles_location_city", table_name="family_profiles")
    op.drop_index("ix_family_profiles_session_id", table_name="family_profiles")
    op.drop_table("family_profiles")
