"""Add hashed, expiring single-use account action tokens.

Revision ID: 0014_account_action_tokens
Revises: 0013_order_payment_ledger
"""
from alembic import op
import sqlalchemy as sa


revision = "0014_account_action_tokens"
down_revision = "0013_order_payment_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_action_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(32), nullable=False),
        sa.Column("token_digest", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    for column in ("customer_id", "purpose", "token_digest", "expires_at", "created_at"):
        op.create_index(f"ix_account_action_tokens_{column}", "account_action_tokens", [column], unique=column == "token_digest")


def downgrade() -> None:
    op.drop_table("account_action_tokens")
