from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)

def test_health_is_available_without_database_credentials():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "not_configured"}

def test_catalog_fails_closed_when_database_is_unconfigured():
    response = client.get("/api/v1/cars")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database is not configured"

def test_admin_routes_fail_closed_until_private_key_is_configured():
    response = client.get("/api/v1/admin/cars")
    assert response.status_code == 503
    assert response.json()["detail"] == "Administrative access is not configured"


def test_admin_routes_reject_invalid_key_before_database_access(monkeypatch):
    from app.core import admin_auth
    from app.core.config import Settings

    monkeypatch.setattr(admin_auth, "settings", Settings(database_url=None, cors_origins=[], admin_api_key="x" * 40))
    response = client.get("/api/v1/admin/cars", headers={"X-Admin-Token": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid administrative credentials"

def test_cors_allows_admin_header_from_local_frontend():
    response = client.options(
        "/api/v1/admin/cars",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-admin-token,content-type",
        },
    )
    assert response.status_code == 200
    assert "x-admin-token" in response.headers["access-control-allow-headers"].lower()


def test_catalog_returns_selected_vehicle_translation(monkeypatch):
    car = SimpleNamespace(
        id=7, slug="test-ev", brand="Test", model="EV", trim=None, year=2026,
        price_cny=Decimal("10000"), range_km=500, battery_kwh=Decimal("70"),
        power_kw=200, drivetrain="AWD", availability="on_request",
        images=[SimpleNamespace(url="https://example.invalid/vehicle.jpg")],
        translations=[SimpleNamespace(locale="tg", title="\u041c\u043e\u0448\u0438\u043d", description="\u0422\u0430\u0432\u0441\u0438\u0444")],
    )
    fake_db = SimpleNamespace(scalars=lambda _statement: SimpleNamespace(all=lambda: [car]))
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        response = client.get("/api/v1/cars?locale=tg")
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 200
    assert response.json()[0]["localized_title"] == "\u041c\u043e\u0448\u0438\u043d"
    assert response.json()[0]["localized_description"] == "\u0422\u0430\u0432\u0441\u0438\u0444"

def test_incomplete_tariff_cannot_be_activated(monkeypatch):
    from datetime import date
    from app.core import admin_auth
    from app.core.config import Settings

    monkeypatch.setattr(admin_auth, "settings", Settings(database_url=None, cors_origins=[], admin_api_key="x" * 40))
    tariff = SimpleNamespace(name="draft", effective_on=date(2026, 1, 1), cny_to_tjs=None, shipping_tjs=None, customs_rate=None, customs_basis=None, additional_tjs=None, paperwork_tjs=None)
    fake_db = SimpleNamespace(get=lambda _model, _id: tariff)
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        response = client.post("/api/v1/admin/tariffs/3/activate", headers={"X-Admin-Token": "x" * 40})
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Cannot activate incomplete tariff")

def test_order_and_staff_crm_routes_require_login_before_database_access():
    for path in ("/api/v1/auth/me/orders", "/api/v1/auth/staff/orders", "/api/v1/crm/overview", "/api/v1/crm/managers"):
        response = client.get(path)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_quote_endpoint_reports_unavailable_without_current_tariff(monkeypatch):
    fake_db = SimpleNamespace(scalar=lambda _statement: None)
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        response = client.post("/api/v1/quotes", json={"price_cny": "10000"})
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 503
    assert response.json()["detail"] == "No current pricing tariff is configured"


def test_quote_endpoint_returns_tariff_backed_itemized_snapshot(monkeypatch):
    from datetime import date, datetime, timezone

    tariff = SimpleNamespace(
        id=9, name="Verified draft tariff", currency="TJS", effective_on=date(2026, 1, 1),
        cny_to_tjs=Decimal("1.2"), shipping_tjs=Decimal("500"), customs_rate=Decimal("0.1"),
        customs_basis="vehicle_plus_shipping", additional_tjs=Decimal("10"), paperwork_tjs=Decimal("20"),
    )
    class FakeDB:
        quote = None
        def scalar(self, _statement): return tariff
        def add(self, value): self.quote = value
        def commit(self): pass
        def refresh(self, value):
            value.id = 123
            value.created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    fake_db = FakeDB()
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        response = client.post("/api/v1/quotes", json={"price_cny": "10000"})
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 200
    result = response.json()
    assert result["tariff_name"] == tariff.name
    assert result["effective_on"] == "2026-01-01"
    assert result["customs_basis"] == "vehicle_plus_shipping"
    assert result["car_tjs"] == "12000.00"
    assert result["shipping_tjs"] == "500.00"
    assert result["customs_tjs"] == "1250.00"
    assert result["total_tjs"] == "13780.00"
    assert fake_db.quote.customer_id is None


def test_quote_endpoint_rate_limits_anonymous_persistence(monkeypatch):
    from app.core.rate_limit import SlidingWindowLimiter
    from app.api import routes

    monkeypatch.setattr(routes, "quote_limiter", SlidingWindowLimiter(max_requests=1, window_seconds=60))
    fake_db = SimpleNamespace(scalar=lambda _statement: None)
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        first = client.post("/api/v1/quotes", json={"price_cny": "10000"})
        second = client.post("/api/v1/quotes", json={"price_cny": "10000"})
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert first.status_code == 503
    assert second.status_code == 429


def test_staff_manager_directory_returns_only_minimal_manager_records(monkeypatch):
    from app.core.auth import AuthContext, require_staff

    manager = SimpleNamespace(id=4, full_name="Sales Manager", email_normalized="manager@example.test", role="manager")
    fake_db = SimpleNamespace(scalars=lambda _statement: SimpleNamespace(all=lambda: [manager]))
    staff = AuthContext(customer=SimpleNamespace(id=1, role="admin"), session=SimpleNamespace())
    monkeypatch.setitem(app.dependency_overrides, require_staff, lambda: staff)
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: fake_db)
    try:
        response = client.get("/api/v1/crm/managers")
    finally:
        app.dependency_overrides.pop(require_staff, None)
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 200
    assert response.json() == [{
        "id": 4, "full_name": "Sales Manager",
        "email_normalized": "manager@example.test", "role": "manager",
    }]
