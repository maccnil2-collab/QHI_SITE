"""Persist customer-visible order notifications.

Revision ID: 0007_customer_notifications
"""
from alembic import op
import sqlalchemy as sa


revision = "0007_customer_notifications"
down_revision = "0006_crm"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("vehicle_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("order_events.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True)),
    )
    op.create_index(
        "ix_customer_notifications_customer_created",
        "customer_notifications",
        ["customer_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_customer_notifications_customer_created", table_name="customer_notifications")
    op.drop_table("customer_notifications")
