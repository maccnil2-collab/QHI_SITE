"""Add structured specifications and verifiable price/source fields.

Revision ID: 0012_structured_vehicle_specs
Revises: 0011_demo_inventory_support
"""
from alembic import op
import sqlalchemy as sa


revision = "0012_structured_vehicle_specs"
down_revision = "0011_demo_inventory_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = (
        ("fuel_type", sa.String(32)),
        ("torque_nm", sa.Integer()),
        ("acceleration_0_100_s", sa.Numeric(5, 2)),
        ("max_speed_kmh", sa.Integer()),
        ("seats", sa.Integer()),
        ("doors", sa.Integer()),
        ("length_mm", sa.Integer()),
        ("width_mm", sa.Integer()),
        ("height_mm", sa.Integer()),
        ("wheelbase_mm", sa.Integer()),
        ("advantages", sa.Text()),
        ("specification_source", sa.Text()),
        ("price_usd", sa.Numeric(14, 2)),
        ("price_tjs", sa.Numeric(14, 2)),
        ("price_note", sa.String(500)),
        ("price_source", sa.Text()),
    )
    for name, column_type in columns:
        op.add_column("cars", sa.Column(name, column_type, nullable=True))
    op.create_index("ix_cars_fuel_type", "cars", ["fuel_type"])


def downgrade() -> None:
    op.drop_index("ix_cars_fuel_type", table_name="cars")
    for name in (
        "price_source", "price_note", "price_tjs", "price_usd",
        "specification_source", "advantages", "wheelbase_mm", "height_mm",
        "width_mm", "length_mm", "doors", "seats", "max_speed_kmh",
        "acceleration_0_100_s", "torque_nm", "fuel_type",
    ):
        op.drop_column("cars", name)
