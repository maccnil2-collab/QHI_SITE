from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.schemas.support import TicketCreate
from app.services.payment_providers import DemoProviderDisabled, TestPaymentSimulator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import base, session as db_session
from app.main import app
from app.core.auth import require_staff
from app.api.auth_routes import _require_test_email_outbox, _require_test_payment_database
from fastapi import HTTPException
from types import SimpleNamespace


def test_support_ticket_requires_valid_contact_and_bounded_content():
    ticket = TicketCreate(name=" Customer ", email=" PERSON@Example.com ", category="complaint", subject="Issue", message="A sufficiently detailed message", locale="tg")
    assert ticket.name == "Customer"
    assert ticket.email == "person@example.com"
    with pytest.raises(ValidationError):
        TicketCreate(name="X", email="bad", category="general", subject=" ", message="short")


def test_demo_payment_provider_never_creates_a_checkout_or_success():
    provider = DemoProviderDisabled()
    with pytest.raises(RuntimeError, match="disabled"):
        provider.create_session(order_reference="QHI-DEMO", amount=Decimal("100"), currency="TJS", idempotency_key="demo-key")
    assert provider.verify_webhook(payload=b"{}", signature="anything") is False
    with pytest.raises(RuntimeError, match="disabled"):
        provider.request_refund(provider_reference="ref", amount=Decimal("1"), idempotency_key="refund-key")


def test_test_payment_tools_require_explicit_flag_nonproduction_and_test_database(monkeypatch):
    class DatabaseName:
        def __init__(self, name):
            self.name = name

        def scalar(self, _statement):
            return self.name

    monkeypatch.setenv("QHI_TEST_PAYMENTS_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    _require_test_payment_database(DatabaseName("qhi_auto_app_test"))
    with pytest.raises(HTTPException) as demo_database:
        _require_test_payment_database(DatabaseName("qhi_auto_demo"))
    assert demo_database.value.status_code == 404
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(HTTPException) as production:
        _require_test_payment_database(DatabaseName("qhi_auto_payment_test"))
    assert production.value.status_code == 404


def test_password_recovery_outbox_is_restricted_to_nonproduction_test_database(monkeypatch):
    class DatabaseName:
        def __init__(self, name):
            self.name = name

        def scalar(self, _statement):
            return self.name

    monkeypatch.setenv("QHI_TEST_EMAIL_OUTBOX_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    _require_test_email_outbox(DatabaseName("qhi_auto_recovery_test"))
    with pytest.raises(HTTPException) as demo_database:
        _require_test_email_outbox(DatabaseName("qhi_auto_demo"))
    assert demo_database.value.status_code == 503
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(HTTPException) as production:
        _require_test_email_outbox(DatabaseName("qhi_auto_recovery_test"))
    assert production.value.status_code == 503


def test_test_payment_simulator_has_explicit_outcomes_and_no_checkout_url():
    provider = TestPaymentSimulator()
    approved = provider.simulate(outcome="approved", idempotency_key="unit-test-approve")
    declined = provider.simulate(outcome="declined", idempotency_key="unit-test-decline")
    assert approved.status == "succeeded" and approved.redirect_url == ""
    assert declined.status == "failed" and declined.redirect_url == ""
    with pytest.raises(ValueError):
        provider.simulate(outcome="unknown", idempotency_key="unit-test-invalid")


def test_support_request_is_stored_numbered_and_staff_only(monkeypatch):
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    monkeypatch.setattr(db_session, "SessionLocal", factory)
    with TestClient(app) as client:
        response = client.post("/api/v1/support/tickets", json={"name":"Test customer","email":"USER@example.test","category":"technical","subject":"Cannot open page","message":"Please help me investigate this page issue.","locale":"en"})
        assert response.status_code == 201
        ticket = response.json()
        assert ticket["ticket_number"].startswith("QHI-")
        assert ticket["email"] == "user@example.test"
        assert ticket["status"] == "open"
        assert client.get("/api/v1/support/tickets").status_code == 401
        monkeypatch.setitem(app.dependency_overrides, require_staff, lambda: SimpleNamespace(customer=SimpleNamespace(id=1)))
        assert client.get("/api/v1/support/tickets").json()[0]["id"] == ticket["id"]
    app.dependency_overrides.pop(require_staff, None)
    engine.dispose()
