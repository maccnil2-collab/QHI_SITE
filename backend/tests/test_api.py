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
