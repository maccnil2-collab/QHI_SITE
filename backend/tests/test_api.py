from fastapi.testclient import TestClient
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
