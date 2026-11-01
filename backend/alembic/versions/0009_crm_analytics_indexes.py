"""Add indexes for bounded CRM date-range analytics.

Revision ID: 0009_crm_analytics_indexes
"""
from alembic import op


revision = "0009_crm_analytics_indexes"
down_revision = "0008_order_document_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_crm_leads_created_at", "crm_leads", ["created_at"])
    op.create_index("ix_vehicle_orders_created_at", "vehicle_orders", ["created_at"])
    op.create_index("ix_price_quotes_created_at", "price_quotes", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_price_quotes_created_at", table_name="price_quotes")
    op.drop_index("ix_vehicle_orders_created_at", table_name="vehicle_orders")
    op.drop_index("ix_crm_leads_created_at", table_name="crm_leads")
