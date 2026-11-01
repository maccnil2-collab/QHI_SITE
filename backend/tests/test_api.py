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
