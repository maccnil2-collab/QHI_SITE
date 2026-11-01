"""Add stored document size and checksum metadata.

Revision ID: 0008_order_document_integrity
"""
from alembic import op
import sqlalchemy as sa


revision = "0008_order_document_integrity"
down_revision = "0007_customer_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("order_documents", sa.Column("byte_size", sa.Integer(), nullable=True))
    op.add_column("order_documents", sa.Column("sha256", sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column("order_documents", "sha256")
    op.drop_column("order_documents", "byte_size")
