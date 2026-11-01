import pytest

from app.schemas.orders import OrderEventOut, OrderOut, StaffOrderEventOut, StaffOrderOut
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
    assert "customer" in StaffOrderOut.model_fields
    assert "email_normalized" in StaffOrderOut.model_fields["customer"].annotation.model_fields

def test_sqlalchemy_model_relationships_configure():
    from sqlalchemy.orm import configure_mappers

    configure_mappers()


def test_staff_order_contact_and_private_events_are_staff_only():
    from datetime import datetime, timezone

    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    source = {
        "id": 3, "order_number": "QHI-2026-ABC123", "status": "in_transit",
        "customer_note": "Please call before delivery", "customer_id": 8,
        "customer": {"id": 8, "full_name": "Customer Name", "email_normalized": "customer@example.test", "phone": "+992900000000"},
        "car": {"id": 5, "slug": "sample-ev", "brand": "Sample", "model": "EV", "year": 2026},
        "events": [{"id": 10, "event_type": "status_changed", "status": "in_transit", "public_note": "Vehicle departed", "internal_note": "Supplier tracking ref private", "created_at": created}],
        "created_at": created, "updated_at": created,
    }
    staff = StaffOrderOut.model_validate(source)
    customer = OrderOut.model_validate(source)
    assert staff.customer.email_normalized == "customer@example.test"
    assert staff.events[0].internal_note == "Supplier tracking ref private"
    assert "customer" not in OrderOut.model_fields
    assert "internal_note" not in OrderEventOut.model_fields
    assert customer.events[0].public_note == "Vehicle departed"
