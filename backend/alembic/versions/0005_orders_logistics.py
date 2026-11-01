"""Customer orders and operational delivery event timeline.

Revision ID: 0005_orders_logistics
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_orders_logistics"
down_revision = "0004_customer_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicle_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_number", sa.String(24), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="requested"),
        sa.Column("customer_note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vehicle_orders_order_number", "vehicle_orders", ["order_number"], unique=True)
    op.create_index("ix_vehicle_orders_customer_id", "vehicle_orders", ["customer_id"])
    op.create_index("ix_vehicle_orders_car_id", "vehicle_orders", ["car_id"])
    op.create_index("ix_vehicle_orders_status", "vehicle_orders", ["status"])
    op.create_table(
        "order_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("vehicle_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32)),
        sa.Column("public_note", sa.Text()),
        sa.Column("internal_note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_order_events_order_id", "order_events", ["order_id"])
    op.create_index("ix_order_events_actor_id", "order_events", ["actor_id"])
    op.create_table(
        "order_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("vehicle_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("visible_to_customer", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("storage_key", name="uq_order_documents_storage_key"),
    )
    op.create_index("ix_order_documents_order_id", "order_documents", ["order_id"])


def downgrade() -> None:
    op.drop_table("order_documents")
    op.drop_table("order_events")
    op.drop_table("vehicle_orders")
