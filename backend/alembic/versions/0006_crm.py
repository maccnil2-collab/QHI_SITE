"""Customer relationship management records.

Revision ID: 0006_crm
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_crm"
down_revision = "0005_orders_logistics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("assigned_manager_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254)),
        sa.Column("phone", sa.String(32)),
        sa.Column("preferred_locale", sa.String(2), nullable=False, server_default="ru"),
        sa.Column("source", sa.String(40), nullable=False, server_default="website"),
        sa.Column("status", sa.String(24), nullable=False, server_default="new"),
        sa.Column("message", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_crm_leads_customer_id", "crm_leads", ["customer_id"])
    op.create_index("ix_crm_leads_assigned_manager_id", "crm_leads", ["assigned_manager_id"])
    op.create_index("ix_crm_leads_email", "crm_leads", ["email"])
    op.create_index("ix_crm_leads_phone", "crm_leads", ["phone"])
    op.create_index("ix_crm_leads_status", "crm_leads", ["status"])
    op.create_table(
        "crm_interactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_crm_interactions_lead_id", "crm_interactions", ["lead_id"])
    op.create_index("ix_crm_interactions_actor_id", "crm_interactions", ["actor_id"])


def downgrade() -> None:
    op.drop_table("crm_interactions")
    op.drop_table("crm_leads")
