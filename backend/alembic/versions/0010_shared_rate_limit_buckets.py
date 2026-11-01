"""Add atomic shared rate-limit buckets.

Revision ID: 0010_shared_rate_limit_buckets
Revises: 0009_crm_analytics_indexes
"""
from alembic import op
import sqlalchemy as sa


revision = "0010_shared_rate_limit_buckets"
down_revision = "0009_crm_analytics_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rate_limit_buckets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key_digest", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.CheckConstraint("request_count > 0", name="ck_rate_limit_request_count_positive"),
        sa.UniqueConstraint("key_digest", "window_start", name="uq_rate_limit_key_window"),
    )
    op.create_index("ix_rate_limit_buckets_window_start", "rate_limit_buckets", ["window_start"])


def downgrade() -> None:
    op.drop_index("ix_rate_limit_buckets_window_start", table_name="rate_limit_buckets")
    op.drop_table("rate_limit_buckets")
