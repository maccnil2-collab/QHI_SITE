import pytest

from app.schemas.orders import OrderOut, StaffOrderEventOut, StaffOrderOut
from app.services.orders import transition_order


def test_order_workflow_allows_expected_forward_logistics_steps():
    status = "requested"
    for target in ("confirmed", "sourcing", "purchased", "in_transit", "customs", "ready_for_delivery", "delivered"):
        status = transition_order(status, target)
    assert status == "delivered"


def test_terminal_orders_cannot_be_reopened_or_cancelled():
    for status in ("delivered", "cancelled"):
        with pytest.raises(ValueError):
            transition_order(status, "requested")


def test_internal_staff_notes_are_excluded_from_customer_order_contract():
    assert "internal_note" not in OrderOut.model_fields
    assert "internal_note" in StaffOrderEventOut.model_fields
    assert "customer_id" not in OrderOut.model_fields
    assert "customer_id" in StaffOrderOut.model_fields

def test_sqlalchemy_model_relationships_configure():
    from sqlalchemy.orm import configure_mappers

    configure_mappers()
