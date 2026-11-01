from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import require_staff
from app.db import base, session as db_session
from app.main import app
from app.models import CRMLead, Car, Customer, PricingTariff, PriceQuote, VehicleOrder
from app.schemas.crm import LeadCreate
from app.services.crm import transition_lead


def test_public_lead_requires_a_contact_channel_and_normalizes_email():
    lead = LeadCreate(name="  Customer  ", email=" PERSON@Example.com ", preferred_locale="tg")
    assert lead.name == "Customer"
    assert lead.email == "person@example.com"
    assert lead.preferred_locale == "tg"
    with pytest.raises(ValidationError):
        LeadCreate(name="Customer")


def test_lead_workflow_records_contact_and_terminal_outcomes():
    assert transition_lead("new", "contacted") == "contacted"
    assert transition_lead("contacted", "converted") == "converted"
    with pytest.raises(ValueError):
        transition_lead("converted", "new")
    with pytest.raises(ValueError):
        transition_lead("unknown", "new")


@pytest.fixture
def analytics_client(monkeypatch):
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db_session, "SessionLocal", session_factory)
    with session_factory() as db:
        manager = Customer(email_normalized="manager@example.test", password_hash="unused", full_name="Manager", role="manager")
        car = Car(slug="crm-analytics-ev", brand="Test", model="EV", year=2026, price_cny=Decimal("10000"))
        tariff = PricingTariff(name="Test tariff", effective_on=datetime(2026, 10, 1).date())
        db.add_all([manager, car, tariff])
        db.flush()
        db.add_all([
            CRMLead(name="A", email="a@example.test", preferred_locale="en", source="website", status="new", assigned_manager_id=manager.id, created_at=datetime(2026, 10, 3)),
            CRMLead(name="B", email="b@example.test", preferred_locale="ru", source="referral", status="converted", assigned_manager_id=manager.id, created_at=datetime(2026, 10, 10)),
            CRMLead(name="C", email="c@example.test", preferred_locale="tg", source="website", status="qualified", created_at=datetime(2026, 10, 20)),
            CRMLead(name="Old", email="old@example.test", preferred_locale="en", source="website", status="new", created_at=datetime(2026, 9, 30)),
        ])
        db.add_all([
            VehicleOrder(order_number="QHI-2026-ANA001", customer_id=manager.id, car_id=car.id, status="requested", created_at=datetime(2026, 10, 5)),
            VehicleOrder(order_number="QHI-2026-ANA002", customer_id=manager.id, car_id=car.id, status="in_transit", created_at=datetime(2026, 10, 25)),
            VehicleOrder(order_number="QHI-2026-ANA003", customer_id=manager.id, car_id=car.id, status="requested", created_at=datetime(2026, 9, 30)),
        ])
        db.add_all([
            PriceQuote(tariff_id=tariff.id, tariff_name="Test tariff", effective_on=tariff.effective_on, price_cny=Decimal("10000"), cny_to_tjs=Decimal("1"), shipping_tjs=Decimal("10"), customs_rate=Decimal("0.1"), customs_basis="vehicle_value", additional_tjs=Decimal("0"), paperwork_tjs=Decimal("0"), car_tjs=Decimal("10000"), customs_tjs=Decimal("1000"), total_tjs=Decimal("11010"), created_at=datetime(2026, 10, 15)),
            PriceQuote(tariff_id=tariff.id, tariff_name="Test tariff", effective_on=tariff.effective_on, price_cny=Decimal("20000"), cny_to_tjs=Decimal("1"), shipping_tjs=Decimal("10"), customs_rate=Decimal("0.1"), customs_basis="vehicle_value", additional_tjs=Decimal("0"), paperwork_tjs=Decimal("0"), car_tjs=Decimal("20000"), customs_tjs=Decimal("2000"), total_tjs=Decimal("22010"), created_at=datetime(2026, 9, 30)),
        ])
        db.commit()

    context = SimpleNamespace(customer=manager)
    monkeypatch.setitem(app.dependency_overrides, require_staff, lambda: context)
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(require_staff, None)
    engine.dispose()


def test_crm_analytics_reports_date_bounded_funnel_workload_orders_and_estimates(analytics_client):
    response = analytics_client.get("/api/v1/crm/analytics?from_date=2026-10-01&to_date=2026-10-31")

    assert response.status_code == 200
    data = response.json()
    assert data["leads_created"] == 3
    assert data["leads_by_status"] == {"new": 1, "converted": 1, "qualified": 1}
    assert data["leads_by_source"] == {"website": 2, "referral": 1}
    assert data["converted_leads"] == 1
    assert data["conversion_rate_percent"] == "33.33"
    assert data["unassigned_leads"] == 1
    assert data["manager_workload"] == [{"manager_id": 1, "manager_name": "Manager", "assigned_leads": 2, "active_leads": 1}]
    assert data["orders_created"] == 2
    assert data["orders_by_status"] == {"requested": 1, "in_transit": 1}
    assert data["quotes_created"] == 1
    assert data["quoted_total_tjs"] == "11010.00"


def test_crm_analytics_rejects_invalid_or_overlong_periods(analytics_client):
    reversed_period = analytics_client.get("/api/v1/crm/analytics?from_date=2026-10-02&to_date=2026-10-01")
    long_period = analytics_client.get("/api/v1/crm/analytics?from_date=2024-01-01&to_date=2026-01-01")
    future_period = analytics_client.get("/api/v1/crm/analytics?to_date=9999-12-31")

    assert reversed_period.status_code == 422
    assert long_period.status_code == 422
    assert future_period.status_code == 422
